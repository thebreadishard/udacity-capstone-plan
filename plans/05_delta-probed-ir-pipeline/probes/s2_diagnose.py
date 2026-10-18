"""S2 diagnostics, step 0 of the search (18 Oct 2026, after verdict 3; exploratory, no line): is route (b)'s error a model that is too simple
(bias) or too little data (variance)?

    python s2_diagnose.py <s2_root> --selection <selection.json> [--extra ID=DIR ...] --out <dir>

Per family, the rms of (b) and (c) in-sample (fitted on every molecule, scored on the same modes) beside the leave-one-scaffold-out rms of the
registered read. In-sample close to held-out: the model cannot represent the shifts even on the modes it was fitted to, and more molecules of
the same kind will not lower the error — the features or the model class must change. In-sample far below held-out: the model fits what it
sees and generalises poorly, which more data does lower. Also per molecule, the held-out rms of the 'other' family, to see whether the error
is spread or sits in a few molecules.
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from s2_read import FAMILIES, SCOPES, concat, design, fit_predict, load_selection, loso, rms, write_atomic  # noqa: E402


def in_sample(mols):
    """Both routes fitted on all window modes and scored on the same modes: (truth, pred_b, pred_c, family)."""
    data = concat(mols)
    pb, pc, _unseen = fit_predict(data, data)
    return data["delta"], pb, pc, data["family"]


def per_family(truth, pb, pc, fam):
    return {fa: {"n": int((fam == fa).sum()), "b": rms((pb - truth)[fam == fa]), "c": rms((pc - truth)[fam == fa])} for fa in FAMILIES}


def held_out_by_molecule(by_scaf, family):
    """Per molecule, the held-out rms of one family's window modes (the molecule's scaffold left out)."""
    out = {}
    for s, mols in by_scaf.items():
        train = concat([m for t, ms in by_scaf.items() if t != s for m in ms])
        for m in mols:
            test = concat([m])
            sel = test["family"] == family
            if sel.any():
                pb, _pc, _u = fit_predict(train, test)
                out[m["id"]] = {"scaffold": s, "n": int(sel.sum()), "b": rms((pb - test["delta"])[sel])}
    return out


def largest_errors(by_scaf, n=15):
    """The n largest held-out errors of route (b) over all window modes, each with its molecule, ω, family, truth, prediction and h."""
    rows = []
    for s, mols in by_scaf.items():
        train = concat([m for t, ms in by_scaf.items() if t != s for m in ms])
        for m in mols:
            test = concat([m])
            pb, _pc, _u = fit_predict(train, test)
            rows += [{"id": m["id"], "omega": float(w), "family": str(f), "delta": float(d), "pred_b": float(p), "h": float(h)}
                     for w, f, d, p, h in zip(test["omega"], test["family"], test["delta"], pb, test["h"], strict=True)]
    return sorted(rows, key=lambda r: -abs(r["pred_b"] - r["delta"]))[:n]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("root")
    ap.add_argument("--selection", required=True)
    ap.add_argument("--extra", nargs="*", default=[])
    ap.add_argument("--out", required=True)
    ap.add_argument("--gvpt2-dir", help="S2 amendment 2: GVPT2 labels from probes/gvpt2_labels.py")
    ap.add_argument("--scope", choices=SCOPES, default="all")
    a = ap.parse_args()
    by_scaf, used, _excluded = load_selection(a.root, a.selection, "G", dict(e.split("=", 1) for e in a.extra), a.gvpt2_dir, a.scope)
    mols = [m for ms in by_scaf.values() for m in ms]
    n_params = design(np.zeros(1), np.array(["other"]), np.zeros(1), np.zeros(1)).shape[1]
    res = {"labels": "GVPT2" if a.gvpt2_dir else "DVPT2 (stored)", "scope": a.scope,
           "molecules": len(used), "scaffolds": len(by_scaf), "route_b_parameters": n_params,
           "in_sample": per_family(*in_sample(mols)), "held_out": per_family(*loso(by_scaf)[:4]),
           "other_by_molecule": held_out_by_molecule(by_scaf, "other"), "largest_errors": largest_errors(by_scaf)}
    ins, ho = res["in_sample"], res["held_out"]
    lines = [f"# S2 diagnostics — bias or variance? ({len(used)} molecules, {len(by_scaf)} scaffolds, route (b) has {n_params} coefficients; "
             f"labels {res['labels']}, scope {a.scope})", "",
             "| family | modes | (b) in-sample | (b) held out | (c) in-sample | (c) held out |", "|---|---|---|---|---|---|"]
    lines += [f"| {fa} | {ho[fa]['n']} | {ins[fa]['b']:.2f} | {ho[fa]['b']:.2f} | {ins[fa]['c']:.2f} | {ho[fa]['c']:.2f} |" for fa in FAMILIES]
    lines += ["", "| molecule | scaffold | 'other' modes | (b) held-out rms |", "|---|---|---|---|"]
    lines += [f"| {i} | {v['scaffold']} | {v['n']} | {v['b']:.2f} |"
              for i, v in sorted(res["other_by_molecule"].items(), key=lambda kv: -kv[1]["b"])]
    lines += ["", "| molecule | ω (cm⁻¹) | family | Δ_anh | (b) predicts | h |", "|---|---|---|---|---|---|"]
    lines += [f"| {r['id']} | {r['omega']:.0f} | {r['family']} | {r['delta']:.1f} | {r['pred_b']:.1f} | {r['h']:.2f} |" for r in res["largest_errors"]]
    os.makedirs(a.out, exist_ok=True)
    write_atomic(os.path.join(a.out, "s2_diagnose.json"), json.dumps(res, indent=1))
    write_atomic(os.path.join(a.out, "s2_diagnose.md"), "\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
