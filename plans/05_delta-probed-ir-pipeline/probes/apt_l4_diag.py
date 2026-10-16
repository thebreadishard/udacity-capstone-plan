"""Diagnosis D1 of L4's miss (TASKS 44; REGISTRATION.md, 16 Oct 2026): is the field route or the refined APT off on B_1f3de8463a?

The field route is a central difference in the field F, so its error grows as F²: on a strongly polarisable molecule (1-cyano-3-nitro-
naphthalene, a push-pull system) it can exceed the 1e-4 e line at F = 1e-3 while the refined APT is right. Run the field route again at
2F and compare, with P the refined APT and A(F) the field-route APT without grid response:

    slope s   least-squares slope of A(2F) − P on A(F) − P over the entries where |A(F) − P| > 1e-4 e (the ones that miss).
              Field-route error, P right: s ≈ 4. P off, field route converged in F: s ≈ 1.
    Richardson R = (4 A(F) − A(2F)) / 3 removes the F² term; d_R = max |P − R|.

Verdict, fixed before the run:
    'field-route truncation'  3 ≤ s ≤ 5 and d_R ≤ 1e-4 e — the refined APT stands; the miss is the field route's at F = 1e-3.
    'refined APT in doubt'    0.5 ≤ s ≤ 1.5 — diagnosis D2 next: the refined APT re-solved to a residual of 1e-9.
    'unexplained'             anything else — no conclusion; examined further.

    python probes/apt_l4_diag.py --refined <recompute>/<id> --field <l4>/<id>_field.npz --field2 <l4>/<id>_field_F2e-3.npz --out <prefix>
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

LINE_E = 1e-4
TRUNCATION_SLOPE = (3.0, 5.0)
SOLVER_SLOPE = (0.5, 1.5)
APT_FILE = "dipole_b3lyp_cphf.npz"


def diagnose(P: np.ndarray, A1: np.ndarray, A2: np.ndarray) -> dict:
    """The slope, the Richardson distance and the verdict for refined APT P and field-route APTs at F (A1) and 2F (A2)."""
    e1, e2 = (A1 - P).ravel(), (A2 - P).ravel()
    missing = np.abs(e1) > LINE_E
    slope = float(e1[missing] @ e2[missing] / (e1[missing] @ e1[missing])) if missing.any() else float("nan")
    d_rich = float(np.abs(P - (4 * A1 - A2) / 3).max())
    if TRUNCATION_SLOPE[0] <= slope <= TRUNCATION_SLOPE[1] and d_rich <= LINE_E:
        verdict = "field-route truncation"
    elif SOLVER_SLOPE[0] <= slope <= SOLVER_SLOPE[1]:
        verdict = "refined APT in doubt"
    else:
        verdict = "unexplained"
    return {"verdict": verdict, "slope": slope, "entries_over_line": int(missing.sum()), "max_diff_F_e": float(np.abs(e1).max()),
            "max_diff_2F_e": float(np.abs(e2).max()), "max_diff_richardson_e": d_rich, "line_e": LINE_E}


def field_apt(path: Path) -> np.ndarray:
    with np.load(path) as z:
        return np.array(z["apt_no_grid_response"], dtype=float)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--refined", type=Path, required=True, help="the molecule's recompute folder")
    ap.add_argument("--field", type=Path, required=True, help="field route at F")
    ap.add_argument("--field2", type=Path, required=True, help="field route at 2F")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    with np.load(a.refined / APT_FILE) as z:
        P = np.array(z["apt"], dtype=float)
    res = diagnose(P, field_apt(a.field), field_apt(a.field2))
    Path(f"{a.out}.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    text = (f"# L4 diagnosis D1 — {a.refined.name}: {res['verdict']}\n\nslope {res['slope']:.2f} over {res['entries_over_line']} entries; "
            f"max diff at F {res['max_diff_F_e']:.2e} e, at 2F {res['max_diff_2F_e']:.2e} e, Richardson {res['max_diff_richardson_e']:.2e} e "
            f"(line {LINE_E:g} e)\n")
    Path(f"{a.out}.md").write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
