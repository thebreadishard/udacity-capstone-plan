"""Write the anharmonic step's artefact (TASKS 211): x2* per family, on all training molecules, as the table the registered read fitted on.

    python anharmonic_step_fit.py [--data-root <plan folder holding the force fields>] [--out <artefact.json>]

Per reading window (mid: 550–2000 cm⁻¹; ch: 2800 cm⁻¹ and up) the route rule's record names the S2b read (each family's
configuration) and the S3 read (the policy for marked modes). The training molecules and the two targets are loaded through
`s3_read.load_scope`, the targets are read by `s3_read.read_targets`, and every family's rms must equal the registered bar of the
route rule to TOLERANCE_CM — otherwise nothing is written. The table saved is `s2_read.concat` of the training molecules, the
object `read_targets` fits on.

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
from s2_xtb_read import MIN_OVERLAP  # noqa: E402
from s2b_read import read_sets  # noqa: E402
from s3_read import MAIN_SCOPE, label_notes, load_scope, predictors, read_targets  # noqa: E402

from dpir.provenance import git_state  # noqa: E402

LABELS = "probes/results_m1/labels_domain_2026-11-13"
ROUTE_RULES = {"mid": f"{LABELS}/route_rule/route_rule.json", "ch": f"{LABELS}/route_rule/route_rule_ch.json"}
SETS, TARGETS = f"{LABELS}/sets.json", f"{LABELS}/S3_targets/targets.json"
TOLERANCE_CM = 0.01        # the registration's acceptance line (PreRegistration_2026-11-14_Printed_Band_Position.md, section 4)
REGISTRATION = "GoalGathering/notes/PreRegistration_2026-11-14_Printed_Band_Position.md"
DECISIONS = "probes/results_m1/anharmonic_design_questions_2026-11-16/REPORT.md"
PROBES_PER_FAMILY = 3      # the family's training rows of lowest, middle and highest ω


def sha16(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()[:16]


def read_json(path: str) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def fit_window(name: str) -> dict[str, Any]:
    """One window's record: the training table, and per printed family its configuration, the registered bar and the refit's."""
    rule = read_json(ROUTE_RULES[name])
    s2b, s3 = read_json(rule["s2b_read"]), read_json(rule["s3_read"])
    for record, path in ((s2b, rule["s2b_read"]), (s3, rule["s3_read"])):
        if record.get("window_name", "mid") != name:
            raise SystemExit(f"{path} is a read of window {record.get('window_name')!r}, not {name!r}")
    window, policy, main = WINDOWS[name], s3["marked_policy"], s2b["scopes"][MAIN_SCOPE]["read"]
    train, _, excluded_train, _ = load_scope(SETS, policy, window)
    targets, _, excluded_targets, _ = load_scope(TARGETS, policy, window)
    read = read_targets(train, targets, main, label_notes(TARGETS), window)
    table = concat([m for mols in train.values() for m in mols], window)
    size = window_size(train, window)
    families = {}
    for fa, printed in rule["printed"].items():
        if printed["model"] != MODEL:
            raise SystemExit(f"{ROUTE_RULES[name]}: {fa} is printed with {printed['model']!r}; this artefact holds {MODEL} only")
        refit = read["families"][fa]["rms"][MODEL]
        if abs(refit - printed["bar_cm"]) > TOLERANCE_CM:
            raise SystemExit(f"{name}/{fa}: the refit gives {refit:.4f} cm-1 against the registered {printed['bar_cm']:.4f}: "
                             f"more than {TOLERANCE_CM} apart, so no artefact is written")
        families[fa] = {"config": main["x2_choice"][fa], "bar_cm": round(printed["bar_cm"], 2), "bar_refit_cm": refit,
                        "n_training_modes": size["per_family"][fa], "n_target_rows": read["families"][fa]["n"],
                        "per_target_rms_cm": {t: v[MODEL] for t, v in read["families"][fa]["per_molecule"].items()}}
    return {"window": window_record(window), "marked_policy": policy, "route_rule": ROUTE_RULES[name],
            "folders": {m["id"]: m["dir"] for mols in (*train.values(), *targets.values()) for m in mols},
            "s2b_read": rule["s2b_read"], "s3_read": rule["s3_read"],
            "sha16": {p: sha16(p) for p in (ROUTE_RULES[name], rule["s2b_read"], rule["s3_read"])},
            "molecules": sorted(size["per_molecule"]), "targets": sorted(read["rows"]),
            "excluded": {**excluded_train, **excluded_targets}, "families": families,
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
            print(f"(FIT) {w.name} {fa}: {m.config}, {m.n_training_modes} training modes, {m.n_target_rows} target rows, "
                  f"refit {m.bar_refit_cm:.4f} against the registered {m.bar_cm}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
