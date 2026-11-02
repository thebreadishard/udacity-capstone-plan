"""S3's registered read (GoalGathering/notes/PreRegistration_2026-11-02_S3_Route_A_Transfer.md, 'Read'): does the learned anharmonic
shift carry from S2's and S2b's small molecules to tetracene and coronene?

    python s3_read.py --sets <sets.json> --s2b-read <s2b_read.json> --targets <targets.json> --out <dir>

<sets.json> and <targets.json> are lists of computed sets as probes/s2b_read.py reads them; the training molecules and the targets go
through the same loader in S2b's main scope. Every model is fitted once on all training molecules and predicts the targets' window modes;
a degenerate pair (ω within PAIR_TOL) counts once, as the mean of its two members' truth and prediction. Per family, pooled over the
targets: the verdict model is S2b's best curve model for the family; transfer holds when its rms is ≤ LINE_LICENSE and below (c)'s; a
family with fewer than MIN_MODES target modes gets no verdict. The size penalty divides the target rms by that model's rms at 'all' in S2b.
"""
from __future__ import annotations

import argparse
import itertools
import json
import os
import sys
from collections.abc import Callable
from typing import Any

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from s2_read import FAMILIES, LINE_LICENSE, XTB_KEY, concat, fit_predict, rms, write_atomic  # noqa: E402
from s2_xtb_read import X2_GRID, build, config_predictor, load_modes, predict_x1  # noqa: E402
from s2b_read import READ_SCOPES, load_set, merge, read_sets  # noqa: E402

MAIN_SCOPE = READ_SCOPES[0]
PAIR_TOL = 0.5          # cm⁻¹: two window modes this close are one degenerate pair
MIN_MODES = 6           # target modes of a family below which no verdict is read
MODELS = ("c", "b", "x1", "x2*", "x0")

Predictor = Callable[[dict, dict], np.ndarray]


def predictors(x2_config_name: str | None) -> dict[str, Predictor]:
    """The models of the read, each (train, test) → the test's predicted Δ_anh; x2* only when S2b chose a configuration for the family."""
    out: dict[str, Predictor] = {"c": lambda tr, te: fit_predict(tr, te)[1], "b": lambda tr, te: fit_predict(tr, te)[0],
                                 "x1": lambda tr, te: predict_x1(tr, te)[0], "x0": lambda tr, te: te[XTB_KEY]}
    if x2_config_name is not None:
        configs = {c.name: c for c in X2_GRID}
        if x2_config_name not in configs:
            raise ValueError(f"S2b's x2 choice {x2_config_name!r} is not in X2_GRID")
        x2 = config_predictor(configs[x2_config_name])
        out["x2*"] = lambda tr, te: x2(tr, te)[0]
    return out


def pair_groups(omega: np.ndarray, tol: float = PAIR_TOL) -> list[np.ndarray]:
    """Indices of the modes, grouped so that a mode within tol of its neighbour in ω shares its group; a group of more than two is refused."""
    order = np.argsort(omega)
    groups, current = [], [order[0]] if len(order) else []
    for i, j in itertools.pairwise(order):
        if omega[j] - omega[i] <= tol:
            current.append(j)
        else:
            groups.append(np.array(current))
            current = [j]
    if current:
        groups.append(np.array(current))
    big = [g for g in groups if len(g) > 2]
    if big:
        raise ValueError(f"{len(big)} group(s) of more than two modes within {tol} cm⁻¹: ω {[omega[g].round(2).tolist() for g in big]}")
    return groups


def target_rows(train: dict, test: dict, models: dict[str, Predictor]) -> dict[str, Any]:
    """One target's window modes with truth and every model's prediction, its degenerate pairs collapsed to their means."""
    preds = {name: np.asarray(p(train, test), float) for name, p in models.items()}
    groups = pair_groups(test["omega"])
    fam = []
    for g in groups:
        kinds = set(test["family"][g])
        if len(kinds) != 1:
            raise ValueError(f"a degenerate pair at {test['omega'][g].round(2).tolist()} cm⁻¹ spans families {sorted(kinds)}")
        fam.append(kinds.pop())
    return {"omega": np.array([test["omega"][g].mean() for g in groups]), "family": np.array(fam),
            "truth": np.array([test["delta"][g].mean() for g in groups]),
            "pred": {name: np.array([p[g].mean() for g in groups]) for name, p in preds.items()},
            "pairs": sum(len(g) == 2 for g in groups)}


def family_read(rows: dict[str, dict[str, Any]], verdicts: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Per family pooled over the targets: n, every model's rms, the verdict model's reading and size penalty; per molecule the rms."""
    out = {}
    for fa in FAMILIES:
        sel = {t: r["family"] == fa for t, r in rows.items()}
        n = int(sum(s.sum() for s in sel.values()))
        if n == 0:
            continue
        pooled = {}
        for m in MODELS:
            if all(m in r["pred"] for r in rows.values()):
                pooled[m] = rms(np.concatenate([r["pred"][m][sel[t]] - r["truth"][sel[t]] for t, r in rows.items()]))
        per_molecule = {t: {m: rms(r["pred"][m][sel[t]] - r["truth"][sel[t]]) for m in r["pred"]} for t, r in rows.items() if sel[t].any()}
        entry: dict[str, Any] = {"n": n, "rms": pooled, "per_molecule": per_molecule}
        v = verdicts.get(fa)
        if v is None:
            entry["reading"] = "no S2b verdict for this family: reported only"
        else:
            model = v["best_curve_model"]
            entry["verdict_model"] = model
            r_model = pooled.get(model, float("nan"))
            entry["size_penalty"] = r_model / v["rms_at_all"] if v["rms_at_all"] > 0 else float("nan")
            if n < MIN_MODES:
                entry["reading"] = f"no verdict: {n} target mode(s) < {MIN_MODES}"
            elif not np.isfinite(r_model):
                entry["reading"] = f"no verdict: the verdict model {model} gave no prediction"
            elif r_model <= LINE_LICENSE and r_model < pooled["c"]:
                entry["reading"] = f"transfer holds: {model} {r_model:.2f} ≤ {LINE_LICENSE} and below (c) {pooled['c']:.2f}"
            else:
                entry["reading"] = f"transfer fails: {model} {r_model:.2f} against line {LINE_LICENSE} and (c) {pooled['c']:.2f}"
        out[fa] = entry
    return out


def read_targets(train_by_scaf: dict, targets_by_scaf: dict, s2b_main: dict[str, Any]) -> dict[str, Any]:
    """Every target's rows with each family's models (x2* at S2b's choice for the family), then the per-family read."""
    train = concat([m for ms in train_by_scaf.values() for m in ms])
    verdicts, choice = s2b_main["verdicts"], s2b_main.get("x2_choice", {})
    rows = {}
    for mols in targets_by_scaf.values():
        for m in mols:
            test = concat([m])
            per_family = {fa: target_rows(train, test, predictors(choice.get(fa))) for fa in FAMILIES}
            base = per_family[FAMILIES[0]]
            pred = {name: base["pred"][name].copy() for name in MODELS if name != "x2*" and name in base["pred"]}
            pred["x2*"] = np.full(len(base["truth"]), np.nan)
            for fa, r in per_family.items():
                if "x2*" in r["pred"]:
                    sel = base["family"] == fa
                    pred["x2*"][sel] = r["pred"]["x2*"][sel]
            rows[m["id"]] = {**base, "pred": pred}
    return {"rows": rows, "families": family_read(rows, verdicts)}


def report(res: dict[str, Any]) -> list[str]:
    lines = [f"# S3 read — {', '.join(res['targets'])} against S2/S2b's models, line {LINE_LICENSE} cm⁻¹ per family", "",
             "| family | n | " + " | ".join(MODELS) + " | verdict model | size penalty | reading |", "|---|---|" + "---|" * (len(MODELS) + 3)]
    for fa, e in res["read"]["families"].items():
        cells = " | ".join(f"{e['rms'][m]:.2f}" if np.isfinite(e["rms"].get(m, np.nan)) else "—" for m in MODELS)
        sp = e.get("size_penalty", float("nan"))
        lines.append(f"| {fa} | {e['n']} | {cells} | {e.get('verdict_model', '—')} | {sp:.2f} | {e['reading']} |")
    lines += ["", f"Degenerate pairs collapsed: {res['pairs']}. Excluded: {res['excluded'] or 'none'}."]
    lines += [f"- {t}: {len(n['moved'])} mode(s) moved by a polyad, {len(n['skipped_degenerate'])} resonance(s) skipped beside a "
              f"degenerate mode, {n['polyad_bridges']} polyad bridge(s)" for t, n in res["label_notes"].items()]
    return lines


def label_notes(sets_path: str) -> dict[str, dict[str, Any]]:
    """Per target, from its gvpt2_labels.py file: the modes a polyad moved and the resonances skipped beside a degenerate mode."""
    notes = {}
    for s in read_sets(sets_path):
        for name in sorted(os.listdir(s.gvpt2_dir)):
            if name.endswith(".json"):
                with open(os.path.join(s.gvpt2_dir, name), encoding="utf-8") as fh:
                    g = json.load(fh)
                notes[g["id"]] = {"moved": g["moved"], "skipped_degenerate": g["skipped_degenerate"],
                                  "polyad_bridges": g["polyad_bridges"]}
    return notes


def load_scope(sets_path: str) -> tuple[dict, dict, dict]:
    """A sets file's molecules in the main scope with their xtb partners, the build counts and the exclusions."""
    parts = {s.name: load_set(s) for s in read_sets(sets_path)}
    g_by_scaf, x_by_id = merge(parts)
    dirs = {m["id"]: (m["dir"], x_by_id[m["id"]]["dir"]) for ms in g_by_scaf.values() for m in ms if m["id"] in x_by_id}
    by_scaf, counts = build(g_by_scaf, x_by_id, load_modes(dirs), MAIN_SCOPE)
    excluded = {i: f"{name}: {w}" for name, p in parts.items() for i, w in {**p["excluded_g"], **p["excluded_x"]}.items()}
    return by_scaf, counts, excluded


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--sets", required=True)
    ap.add_argument("--s2b-read", required=True)
    ap.add_argument("--targets", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    with open(a.s2b_read, encoding="utf-8") as fh:
        s2b_main = json.load(fh)["scopes"][MAIN_SCOPE]["read"]
    train_by_scaf, train_counts, excl_train = load_scope(a.sets)
    targets_by_scaf, target_counts, excl_targets = load_scope(a.targets)
    if not targets_by_scaf:
        raise SystemExit("no target with a G label and an xtb force field: nothing to read")
    read = read_targets(train_by_scaf, targets_by_scaf, s2b_main)
    res = {"registration": "PreRegistration_2026-11-02_S3_Route_A_Transfer.md", "scope": MAIN_SCOPE,
           "targets": sorted(read["rows"]), "training_scaffolds": len(train_by_scaf), "counts": {"train": train_counts, "targets": target_counts},
           "excluded": {**excl_train, **excl_targets}, "pairs": {t: r["pairs"] for t, r in read["rows"].items()},
           "label_notes": label_notes(a.targets),
           "read": {"families": read["families"],
                    "rows": {t: {"omega": r["omega"], "family": r["family"], "truth": r["truth"], "pred": r["pred"]} for t, r in read["rows"].items()}}}
    os.makedirs(a.out, exist_ok=True)
    write_atomic(os.path.join(a.out, "s3_read.json"), json.dumps(res, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else float(o)))
    lines = report(res)
    write_atomic(os.path.join(a.out, "s3_read.md"), "\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
