"""Write the anharmonic step's artefact (TASKS 211): x2* per family, on all training molecules, as the table the registered read fitted on.

    python anharmonic_step_fit.py [--data-root <plan folder holding the force fields>] [--out <artefact.json>]

Per reading window (mid: 550–2000 cm⁻¹; ch: 2800 cm⁻¹ and up) the route rule's record names the S2b read (each family's
configuration) and the S3 read (the policy for marked modes). The training molecules and the two targets are loaded through
`s3_read.load_scope`, the targets are read by `s3_read.read_targets`, and the table saved is `s2_read.concat` of the training
molecules, the object `read_targets` fits on.

Each window is read twice (TASKS 255). Under the match rule 'single' — one xtb mode per mode, the registered read's — every
family's rms must equal the registered bar of the route rule to TOLERANCE_CM, otherwise nothing is written: that shows this code
path is the registered one. Under the rule 'sets' (`s2_xtb_read.match_sets`, the match the step uses) the table gains the modes
that were refused for their basis; that table is the one saved, and its rms on the same target rows is recorded beside the
registered bar, which stays what it was: a registered number. The two may differ by CHANGE_LIMIT_CM at most, otherwise nothing
is written either — a table change that moves a bar further is a new model and needs its own registration.

Beside the table the artefact keeps what a certificate must be able to say of the model without the force fields: the training
molecules and the targets by RDKit's canonical SMILES, the table's elements and how many molecules each composition has, each
target's rms per family, and PROBES_PER_FAMILY probe rows per family (training rows with the shift this fit gives them), which
`anharmonic_step.load_artefact` reproduces on every machine before it lets the artefact be used.

The force fields (165 MB of ref.json and qff_report.npz) are not in git, so the script reads them under --data-root; the artefact
needs none of them afterwards. Relative paths in the reads' records are taken from that folder.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from collections import Counter
from typing import Any

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PLAN = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(PLAN, "src"))
from anharmonic_step import (  # noqa: E402
    ARTEFACT,
    FORMAT,
    MODEL,
    NOT_MEASURED_FAMILY,
    NOT_MEASURED_O,
    PROBE_TOLERANCE_CM,
    TABLE_KEYS,
    load_artefact,
)
from s2_read import WINDOWS, concat, window_record, window_size, write_atomic  # noqa: E402
from s2_xtb_read import DEFAULT_RULE, MARK_SHARE, MATCH_RULES, MIN_OVERLAP  # noqa: E402
from s2b_read import read_sets  # noqa: E402
from s3_read import MAIN_SCOPE, label_notes, load_scope, predictors, read_targets  # noqa: E402

from dpir.provenance import git_state  # noqa: E402

LABELS = "probes/results_m1/labels_domain_2026-11-13"
ROUTE_RULES = {"mid": f"{LABELS}/route_rule/route_rule.json", "ch": f"{LABELS}/route_rule/route_rule_ch.json"}
SETS, TARGETS = f"{LABELS}/sets.json", f"{LABELS}/S3_targets/targets.json"
TOLERANCE_CM = 0.01        # the registration's acceptance line (PreRegistration_2026-11-14_Printed_Band_Position.md, section 4)
REGISTERED_RULE = "single"  # the match of the registered reads
CHANGE_LIMIT_CM = 0.05     # a position is printed to 0.1 cm⁻¹: a bar moved by less than half of that states the same error
REGISTRATION = "GoalGathering/notes/PreRegistration_2026-11-14_Printed_Band_Position.md"
DECISIONS = "probes/results_m1/anharmonic_design_questions_2026-11-16/REPORT.md"
PROBES_PER_FAMILY = 3      # the family's training rows of lowest, middle and highest ω


def sha16(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()[:16]


def read_json(path: str) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def read_window(name: str, match_rule: str, policy: str, main: dict[str, Any]) -> dict[str, Any]:
    """One window under one match rule: the training molecules, the targets read by S2b's models, and the sizes."""
    window = WINDOWS[name]
    train, _, excluded_train, _ = load_scope(SETS, policy, window, match_rule)
    targets, _, excluded_targets, _ = load_scope(TARGETS, policy, window, match_rule)
    return {"train": train, "targets": targets, "excluded": {**excluded_train, **excluded_targets},
            "read": read_targets(train, targets, main, label_notes(TARGETS), window), "size": window_size(train, window)}


def family_record(where: str, printed: dict[str, Any], config: str, registered: dict[str, Any], carried: dict[str, Any]) -> dict[str, Any]:
    """One printed family's record from its two reads (the registered match and the carried one), or the refusal: the
    registered read not reproduced, the carried table moving the bar past CHANGE_LIMIT_CM, or scoring other target rows."""
    fa = where.split("/")[1]
    if printed["model"] != MODEL:
        raise SystemExit(f"{where} is printed with {printed['model']!r}; this artefact holds {MODEL} only")
    old, new = registered["read"]["families"][fa], carried["read"]["families"][fa]
    if abs(old["rms"][MODEL] - printed["bar_cm"]) > TOLERANCE_CM:
        raise SystemExit(f"{where}: the registered read's match gives {old['rms'][MODEL]:.4f} cm-1 against the registered "
                         f"{printed['bar_cm']:.4f}: more than {TOLERANCE_CM} apart, so no artefact is written")
    if abs(new["rms"][MODEL] - printed["bar_cm"]) > CHANGE_LIMIT_CM or new["n"] != old["n"]:
        raise SystemExit(f"{where}: the set-wise table gives {new['rms'][MODEL]:.4f} cm-1 on {new['n']} target rows against the "
                         f"registered {printed['bar_cm']:.4f} on {old['n']}: other rows or more than {CHANGE_LIMIT_CM} apart — a "
                         "new model, which needs its own registration; no artefact is written")
    return {"config": config, "bar_cm": round(printed["bar_cm"], 2), "bar_one_to_one_cm": old["rms"][MODEL],
            "bar_refit_cm": new["rms"][MODEL], "n_training_modes": carried["size"]["per_family"][fa],
            "n_training_modes_one_to_one": registered["size"]["per_family"][fa], "n_target_rows": new["n"],
            "per_target_rms_cm": {t: v[MODEL] for t, v in new["per_molecule"].items()}}


def fit_window(name: str) -> dict[str, Any]:
    """One window's record: the training table under the carried match, and per printed family its configuration, the
    registered bar, its reproduction under the registered match and the bar of the table saved."""
    rule = read_json(ROUTE_RULES[name])
    s2b, s3 = read_json(rule["s2b_read"]), read_json(rule["s3_read"])
    for record, path in ((s2b, rule["s2b_read"]), (s3, rule["s3_read"])):
        if record.get("window_name", "mid") != name:
            raise SystemExit(f"{path} is a read of window {record.get('window_name')!r}, not {name!r}")
    window, policy, main = WINDOWS[name], s3["marked_policy"], s2b["scopes"][MAIN_SCOPE]["read"]
    registered, carried = (read_window(name, r, policy, main) for r in (REGISTERED_RULE, DEFAULT_RULE))
    train, size = carried["train"], carried["size"]
    table = concat([m for mols in train.values() for m in mols], window)
    families = {fa: family_record(f"{name}/{fa}", printed, main["x2_choice"][fa], registered, carried)
                for fa, printed in rule["printed"].items()}
    return {"window": window_record(window), "marked_policy": policy, "route_rule": ROUTE_RULES[name],
            "folders": {m["id"]: m["dir"] for mols in (*train.values(), *carried["targets"].values()) for m in mols},
            "s2b_read": rule["s2b_read"], "s3_read": rule["s3_read"],
            "sha16": {p: sha16(p) for p in (ROUTE_RULES[name], rule["s2b_read"], rule["s3_read"])},
            "molecules": sorted(size["per_molecule"]), "targets": sorted(carried["read"]["rows"]),
            "excluded": carried["excluded"], "families": families,
            "table": {k: table[k].tolist() for k in TABLE_KEYS}}


def probe_rows(name: str, window: dict[str, Any]) -> list[dict[str, Any]]:
    """PROBES_PER_FAMILY training rows of every modelled family of a window, each with the shift the fit gives it."""
    table = {k: np.asarray(window["table"][k], str if k == "family" else float) for k in TABLE_KEYS}
    rows = []
    for fa, model in window["families"].items():
        mine = np.flatnonzero(table["family"] == fa)
        mine = mine[np.argsort(table["omega"][mine], kind="stable")]
        picked = mine[np.unique(np.linspace(0, len(mine) - 1, PROBES_PER_FAMILY).round().astype(int))]
        test = {k: table[k][picked] for k in TABLE_KEYS}
        shift = predictors(model["config"])[MODEL](table, test)
        rows += [{"window": name, **{k: test[k][j].item() for k in TABLE_KEYS}, "shift_cm": float(shift[j])} for j in range(len(picked))]
    return rows


def smiles_by_id(sets_path: str) -> dict[str, str]:
    """Every selected molecule of a sets file by RDKit's canonical SMILES (the form m08/pipeline.py names a molecule by)."""
    from rdkit import Chem

    out = {}
    for s in read_sets(sets_path):
        for m in read_json(s.selection)["selected"]:
            out[m["id"]] = Chem.MolToSmiles(Chem.MolFromSmiles(m["smiles"]))
    return out


def element_record(folders: dict[str, str], training: list[str], targets: list[str]) -> dict[str, Any]:
    """The elements of the training molecules (from each one's reference record), how many molecules each composition has,
    and the targets' compositions."""
    def of(i: str) -> str:
        return ",".join(sorted(set(read_json(os.path.join(folders[i], "ref.json"))["molecule"]["symbols"])))

    compositions = Counter(of(i) for i in training)
    return {"elements": sorted({e for key in compositions for e in key.split(",")}), "compositions": dict(sorted(compositions.items())),
            "target_composition": {t: of(t) for t in targets}}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-root", default=PLAN, help="the plan folder whose probes/results_m1 holds the force fields")
    ap.add_argument("--out", default=ARTEFACT)
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    os.chdir(a.data_root)
    windows = {name: fit_window(name) for name in ROUTE_RULES}
    folders = {i: d for w in windows.values() for i, d in w.pop("folders").items()}
    training = sorted({i for w in windows.values() for i in w["molecules"]})
    targets = sorted({t for w in windows.values() for t in w["targets"]})
    smiles = {**smiles_by_id(SETS), **smiles_by_id(TARGETS)}
    state = git_state(HERE)
    record = {"format": FORMAT, "model": MODEL, "written": time.strftime("%Y-%m-%d %H:%M"), "commit": state.get("commit"),
              "commit_dirty": state.get("dirty"), "registration": REGISTRATION, "decisions": DECISIONS, "scope": MAIN_SCOPE,
              "features": "FX: family one-hot, ω/1000, h, o, Δ_anh of the matched GFN2-xTB mode (s2_search.inputs)",
              "min_overlap": MIN_OVERLAP, "not_measured": {"family": NOT_MEASURED_FAMILY, "o_at_least": NOT_MEASURED_O},
              "match": {"rule": DEFAULT_RULE, "set_tolerance_cm": MATCH_RULES[DEFAULT_RULE], "mark_share": MARK_SHARE,
                        "registered_rule": REGISTERED_RULE, "change_limit_cm": CHANGE_LIMIT_CM},
              "sets_file": SETS, "targets_file": TARGETS, "tolerance_cm": TOLERANCE_CM,
              "training_molecules": training, "molecules": {i: smiles[i] for i in training},
              "targets": {t: smiles[t] for t in targets}, **element_record(folders, training, targets),
              "probes": [row for name, w in windows.items() for row in probe_rows(name, w)],
              "probe_tolerance_cm": PROBE_TOLERANCE_CM, "windows": windows}
    os.makedirs(os.path.dirname(out), exist_ok=True)
    write_atomic(out, json.dumps(record, indent=1, ensure_ascii=False))
    art = load_artefact(out)
    print(f"(FIT) {out}: {os.path.getsize(out)} bytes, {len(record['training_molecules'])} training molecules", flush=True)
    for w in art.windows:
        for fa, m in w.families.items():
            print(f"(FIT) {w.name} {fa}: {m.config}, {m.n_target_rows} target rows; registered {m.bar_cm}, reproduced with the "
                  f"registered match {m.bar_one_to_one_cm:.4f} on {m.n_training_modes_one_to_one} training modes; this table "
                  f"{m.bar_refit_cm:.4f} on {m.n_training_modes} — changed by the set-wise match: "
                  f"{m.n_training_modes - m.n_training_modes_one_to_one:+d} rows", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
