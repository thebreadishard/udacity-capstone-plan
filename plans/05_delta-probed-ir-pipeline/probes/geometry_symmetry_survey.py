"""How symmetric are the corpus geometries, and does it matter? (14 Oct 2026, TASKS 51: azulene's corpus geometry is C2v only to 2.6e-3 bohr.)

The corpus optimises with psi4 in C1 from an RDKit start (layers A/B, `corpus/psi4_worker.py`), to psi4's default criteria (max force 3e-4,
max displacement 1.2e-3 bohr): a molecule ends wherever those are met, so its point group holds only to a residual that differs per molecule.
The CC anchors are computed at these geometries, and the FD CC route builds its Hessian and APT from symmetry-unique displacements —
symmetric by construction — while the analytic B3LYP Hessian at the same geometry is not. Per molecule this script reports:
- the point group's operation count and the geometry residual (largest atom displacement under the operations `e8_symmetry.point_group_ops`
  finds);
- the effect of forcing the symmetry on the B3LYP analytic Hessian (`hessian_b3lyp_analytic.npz`, H_projected): max |Δω| between its harmonic
  frequencies and those of its group average — the size of the inconsistency a symmetric CC Hessian meets at that geometry.

    python probes/geometry_symmetry_survey.py --ids A_d9139359ab,A_7aa232d4e9 [--layers A,A2] [--out survey.json]
"""
import argparse
import csv
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "src"))
from apt_symmetry_diagnosis import geometry_residual  # noqa: E402
from e8_cc_locality import normal_modes  # noqa: E402
from e8_symmetry import point_group_ops  # noqa: E402
from qff_symmetry_rebuild import rep  # noqa: E402

CORPUS = os.path.join(HERE, "..", "modules", "05_support_predictor", "corpus")


def survey_one(mol_dir: str) -> dict:
    g = json.load(open(os.path.join(mol_dir, "geometry.json"), encoding="utf-8"))
    sym = [s.capitalize() for s in g["symbols"]]
    x = np.asarray(g["coords_bohr"], float)
    n = len(sym)
    ops = point_group_ops(sym, x)
    out = {"n_ops": len(ops), "geometry_residual_bohr": geometry_residual(x, ops)}
    hp = os.path.join(mol_dir, "hessian_b3lyp_analytic.npz")
    if os.path.exists(hp) and len(ops) > 1:
        H = np.asarray(np.load(hp)["H_projected"], float)
        Hs = sum(rep(R, p, n) @ H @ rep(R, p, n).T for R, p in ops) / len(ops)
        m = np.asarray(g["masses_amu"], float)                          # the corpus's own masses
        f0, f1 = normal_modes(H, m)[1], normal_modes(Hs, m)[1]
        out["max_abs_dfreq_symmetrised_cm"] = float(np.abs(f1 - f0).max())
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ids", default="")
    ap.add_argument("--layers", default="")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    rows = list(csv.DictReader(open(os.path.join(CORPUS, "manifest.csv"), encoding="utf-8")))
    names = {r["id"]: r["name"] for r in rows}
    ids = [i for i in a.ids.split(",") if i]
    if a.layers:
        layers = set(a.layers.split(","))
        ids += [r["id"] for r in rows if r["layer"] in layers and r["status"] == "done" and r["id"] not in ids]
    res = {}
    for i in ids:
        d = os.path.join(CORPUS, "molecules", i)
        if os.path.exists(os.path.join(d, "geometry.json")):
            res[i] = {"name": names.get(i, ""), **survey_one(d)}
    sym = {k: v for k, v in res.items() if v["n_ops"] > 1}
    r = np.array([v["geometry_residual_bohr"] for v in sym.values()])
    df = np.array([v["max_abs_dfreq_symmetrised_cm"] for v in sym.values() if "max_abs_dfreq_symmetrised_cm" in v])
    summary = {"molecules": len(res), "with_symmetry": len(sym),
               "residual_bohr_quantiles": {q: float(np.quantile(r, q / 100)) for q in (50, 90, 99, 100)} if len(r) else {},
               "max_abs_dfreq_quantiles_cm": {q: float(np.quantile(df, q / 100)) for q in (50, 90, 99, 100)} if len(df) else {}}
    for i in a.ids.split(","):
        if i in res:
            print(f"{i} {res[i]['name']}: ops {res[i]['n_ops']}, residual {res[i]['geometry_residual_bohr']:.1e} bohr, "
                  f"max |Δω| on symmetrising {res[i].get('max_abs_dfreq_symmetrised_cm', float('nan')):.3f} cm⁻¹")
    print(json.dumps(summary, indent=1))
    if a.out:
        json.dump({"summary": summary, "molecules": res}, open(a.out, "w", encoding="utf-8"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
