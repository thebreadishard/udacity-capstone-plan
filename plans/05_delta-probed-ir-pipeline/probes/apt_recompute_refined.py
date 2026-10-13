"""TASKS 44 (b), 12 Oct 2026 (the user: 'Ja, doe a, b en c zoals je adviseert'): the route-C APTs written on the labels server before the
residual-checked response was installed carry pyscf's early-stopped CPHF (pyscf #2702; ~4e-4 e on benzene, heights ≤ 0.6 %). This recomputes
their APT without the Hessian: the labels SCF, `solve_response` (pyscf's own CPHF, the one the Hessian solved) and the labels route's own writer
`write_apt`, which refines the response and checks its residual — with the Hessian taken from the molecule's `hessian_b3lyp_analytic.npz`.
One implementation: the molecule, the SCF and the writer are `analytic_hessians.py`'s.

    python probes/apt_recompute_refined.py <fetched molecule dir> [...] --out <dir> [--threads 4]     (WSL, qc05)

Per molecule, `<out>/<id>/dipole_b3lyp_cphf.npz` is written (the input folder is not touched), and one JSON line is appended to
`<out>/recompute.jsonl`: the residual before/after, the largest change of the APT and of a band height against the old file, and the seconds.
A molecule that already has an output file is skipped. The exit status is 3 when a molecule's APT fails (as the labels route's).
"""
import argparse
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "modules", "05_support_predictor", "corpus"))
import analytic_hessians as AH  # noqa: E402
from apt import solve_response  # noqa: E402
from pyscf import lib  # noqa: E402


def height_change(old, new):
    """The largest change of a band height (km/mol) relative to the strongest band of the old file: the scale a spectrum is read on."""
    old, new = np.asarray(old, dtype=float), np.asarray(new, dtype=float)
    return float(np.abs(new - old).max() / old.max())


def recompute(src, out_dir, grid=(99, 590), stamp=None):
    """The refined APT of one fetched labels molecule (closed shell); returns the summary row."""
    t0 = time.time()
    g = json.load(open(os.path.join(src, "geometry.json")))
    old = np.load(os.path.join(src, AH.APT_FILE))
    failed_refined = str(old["route"]) == "hessian_response_refined" and not bool(old["passed"])   # 13 Oct 2026: the guard's failures
    if str(old["route"]) != "hessian_response" and not failed_refined:                                   # (B_1194d7a42a, B_127dd8c4ed) redo
        raise ValueError(f"{src}: the APT file's route is {old['route']!s} (passed {bool(old['passed'])}): neither unrefined route C nor a failed "
                         "refined one")
    hz = np.load(os.path.join(src, "hessian_b3lyp_analytic.npz"))
    if tuple(hz["grid"]) != tuple(grid) or int(hz["spin"]) != 0:
        raise ValueError(f"{src}: Hessian grid {tuple(hz['grid'])} / spin {int(hz['spin'])} is not the labels route's closed-shell setting")
    mol = AH.labels_mol(g, int(hz["charge"]), 0)
    mf, _ = AH.labels_scf(mol, "b3lyp", grid)
    hobj = mf.Hessian()
    response = solve_response(hobj)
    os.makedirs(out_dir, exist_ok=True)
    try:
        message, error = AH.write_apt(out_dir, hobj, response, hz["H_projected"], np.array(g["masses_amu"]), grid, stamp or AH.software()), ""
    except ValueError as exc:
        message, error = "", str(exc)
    new = np.load(os.path.join(out_dir, AH.APT_FILE))
    return {"id": os.path.basename(os.path.normpath(src)), "passed": bool(new["passed"]), "error": error, "message": message,
            "residual_before": float(new["cphf_residual_before"]), "residual_after": float(new["cphf_residual_after"]),
            "rounds": int(new["cphf_refine_rounds"]), "apt_change_max": float(np.abs(new["apt"] - old["apt"]).max()),
            "height_change_max": height_change(old["intensity_km_mol"], new["intensity_km_mol"]),
            "sum_rule_old": float(old["sum_rule_max"]), "sum_rule_new": float(new["sum_rule_max"]), "seconds": round(time.time() - t0, 1)}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("dirs", nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--threads", type=int, default=4)
    a = ap.parse_args()
    lib.num_threads(a.threads)
    stamp = AH.software()
    failed = 0
    for src in a.dirs:
        mid = os.path.basename(os.path.normpath(src))
        out_dir = os.path.join(a.out, mid)
        if os.path.exists(os.path.join(out_dir, AH.APT_FILE)):
            print(f"{mid}: done before, skipped", flush=True)
            continue
        row = recompute(src, out_dir, stamp=stamp)
        failed += not row["passed"]
        with open(os.path.join(a.out, "recompute.jsonl"), "a") as fh:
            fh.write(json.dumps(row) + "\n")
        print(json.dumps(row), flush=True)
    if failed:
        raise SystemExit(3)


if __name__ == "__main__":
    main()
