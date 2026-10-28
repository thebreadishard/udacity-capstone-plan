"""Styrene's grid re-check, read (15 Oct 2026, TASKS 62): the quartic route disagreement of the constants that tripped S2's noise guard, at the
grid of the run (75/302) and at the finer grid (99/590), from Hessians at the same geometries (`probes/s2_gridcheck_styrene.sh` computes the
finer set on s1).

Both directories hold the reference Hessian (ref.json) and the ± displaced ones of the same modes, named as dpir.qff's cache names them
(modeNN_p/m.json). The reduced coordinates are those of the coarse grid's reference (the displacements were made along them), so only the grid
differs between the two reads. For every pair (i, j) of displaced modes: route a (displace j, read H_ii) and route b (displace i, read H_jj),
dpir.qff's own formulas (`assemble_qff`), in cm⁻¹, and their disagreement at each grid.

    python probes/qff_grid_recheck.py <coarse_dir> <fine_dir> [--disp 0.10] [--out recheck.json]
"""
import argparse
import itertools
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
from dpir.qff import HARTREE_CM, assign_displacements, harmonic, load_results, reference_index


def reduced_hessians(cache_dir: str, A: np.ndarray, ref_geom: np.ndarray, disp: float):
    """(H0, Hp, Hn) in the reduced coordinates A, from one directory; displacements assigned against `ref_geom`."""
    recs = load_results(cache_dir)
    i0 = reference_index(recs)
    if np.abs(recs[i0].geom - ref_geom).max() > 1e-8:
        raise SystemExit(f"{cache_dir}: its reference geometry is not the coarse run's")
    toQ = lambda H: A.T @ H @ A  # noqa: E731
    Hp, Hn = {}, {}
    for k, (i, s, _dq, resid) in assign_displacements(recs, i0, A, disp).items():
        if resid > 1e-6:
            raise SystemExit(f"{recs[k].file}: not a clean ±{disp} displacement along one mode (residual {resid:.1e})")
        (Hp if s > 0 else Hn)[i] = toQ(recs[k].H)
    return toQ(recs[i0].H), Hp, Hn


def routes(H0, Hp, Hn, i, j, disp):
    """dpir.qff.assemble_qff's two routes for φ_iijj, in cm⁻¹."""
    a = (Hp[j][i, i] + Hn[j][i, i] - 2 * H0[i, i]) / disp ** 2
    b = (Hp[i][j, j] + Hn[i][j, j] - 2 * H0[j, j]) / disp ** 2
    return a * HARTREE_CM, b * HARTREE_CM


def recheck(coarse_dir: str, fine_dir: str, disp: float = 0.10) -> dict:
    recs = load_results(coarse_dir)
    ref = recs[reference_index(recs)]
    harm = harmonic(ref.H, ref.symbols, ref.geom)
    grids = {name: reduced_hessians(d, harm.A, ref.geom, disp) for name, d in (("coarse", coarse_dir), ("fine", fine_dir))}
    modes = sorted(set(grids["coarse"][1]) & set(grids["coarse"][2]) & set(grids["fine"][1]) & set(grids["fine"][2]))
    rows = []
    for i, j in itertools.combinations(modes, 2):
        row = {"i": i, "j": j, "omega_i": float(harm.omega_cm[i]), "omega_j": float(harm.omega_cm[j])}
        for name, (H0, Hp, Hn) in grids.items():
            a, b = routes(H0, Hp, Hn, i, j, disp)
            row[name] = {"route_a": float(a), "route_b": float(b), "disagreement": float(abs(a - b))}
        rows.append(row)
    rows.sort(key=lambda r: -r["coarse"]["disagreement"])
    # φ_iiii is route a with j = i; a grid error that both routes share shows here, not in the disagreement (S1-TZ benzene, 28 Oct 2026)
    diagonal = [{"i": i, "omega": float(harm.omega_cm[i]),
                 **{name: float(routes(*grids[name], i, i, disp)[0]) for name in grids}} for i in modes]
    return {"coarse_dir": coarse_dir, "fine_dir": fine_dir, "modes": modes, "pairs": rows, "diagonal": diagonal,
            "max_disagreement": {g: max(r[g]["disagreement"] for r in rows) for g in ("coarse", "fine")}}


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("coarse_dir")
    ap.add_argument("fine_dir")
    ap.add_argument("--disp", type=float, default=0.10)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    res = recheck(a.coarse_dir, a.fine_dir, a.disp)
    print(f"modes {res['modes']}; max route disagreement coarse {res['max_disagreement']['coarse']:.2f}, fine {res['max_disagreement']['fine']:.2f} cm⁻¹")
    for r in res["pairs"][:8]:
        print(f"  ({r['i']},{r['j']}) ω {r['omega_i']:.0f}/{r['omega_j']:.0f}: coarse {r['coarse']['disagreement']:.2f}, fine {r['fine']['disagreement']:.2f}"
              f" (φ_iijj route a coarse {r['coarse']['route_a']:.1f}, fine {r['fine']['route_a']:.1f})")
    for d in res["diagonal"]:
        print(f"  φ_iiii mode {d['i']} ω {d['omega']:.0f}: coarse {d['coarse']:.1f}, fine {d['fine']:.1f} cm⁻¹")
    if a.out:
        tmp = a.out + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(res, fh, indent=1)
        os.replace(tmp, a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
