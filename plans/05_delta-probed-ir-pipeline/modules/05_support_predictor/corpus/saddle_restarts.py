"""Restart geometries for the corpus molecules whose optimised geometry is a saddle point (24 September 2026; corpus README dated note: 15 of the
20 imaginary-mode molecules are genuine — a torsion of the NO2 / CF3 / vinyl / Cl substituent is imaginary in the analytic Hessian too).

For each such molecule: take the analytic Hessian of the functional that shows the imaginary mode (B3LYP first, else ωB97X), find the eigenvector of
its most negative eigenvalue in mass-weighted coordinates, and write two starting geometries displaced along that mode by ±0.25 Å (largest atomic
displacement) — a twisted substituent from which the optimiser can find the true minimum. Output per molecule: `restart_geometry_plus.json`,
`restart_geometry_minus.json` (same schema as `geometry.json`, with `restart_from` and `displacement_angstrom` fields), and a list
`restart_jobs_<date>.json` for the factory. Nothing is computed here beyond a diagonalisation; the re-optimisation and the two Hessians are a
factory run after the 28th (`run_corpus.py --restart-from restart_geometry_plus.json` is the hook to add; the original directories stay as they are
and the new results go to `<id>_r+` / `<id>_r-` so that nothing is overwritten).

Usage: python saddle_restarts.py [--ids ...] [--amplitude 0.25]
"""
import argparse
import glob
import json
import os
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BOHR = 0.529177210903


def vib_only_index(f):
    f = np.asarray(f, float)
    return np.argsort(np.abs(f))[6:]


def imaginary_mode(H, masses):
    """(frequency cm-1, Cartesian displacement unit vector) of the most negative vibrational eigenvalue of a Cartesian Hessian (a.u., amu)."""
    sm = np.sqrt(np.repeat(masses, 3)); w, V = np.linalg.eigh(H / np.outer(sm, sm))
    keep = vib_only_index(w); k = keep[np.argmin(w[keep])]
    if w[k] >= 0:
        return None, None
    f = -np.sqrt(-w[k] / 1822.888486209) * 219474.6313705
    x = V[:, k] / sm; x = x / np.abs(x.reshape(-1, 3)).max()          # Cartesian displacement scaled so that the largest atomic step is 1
    return float(f), x.reshape(-1, 3)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--ids", nargs="*"); ap.add_argument("--amplitude", type=float, default=0.25); a = ap.parse_args()
    ro = json.load(open(os.path.join(HERE, "..", "data", "second_route", "imaginary_second_route_2026-09-24.json"), encoding="utf-8"))
    genuine = [r["id"] for r in ro["rows"] if r.get("molecule_verdict", "").startswith("genuine")]
    ids = a.ids or genuine; jobs = []
    for mid in ids:
        d = os.path.join(HERE, "molecules", mid); g = json.load(open(os.path.join(d, "geometry.json"), encoding="utf-8"))
        x0 = np.array(g["coords_bohr"], float); masses = np.array(g["masses_amu"], float); sym = g["symbols"]
        chosen = None
        for tag in ("b3lyp", "wb97x"):
            p = os.path.join(d, f"hessian_{tag}_analytic.npz")
            if not os.path.exists(p):
                continue
            f, disp = imaginary_mode(np.load(p)["H_raw"], masses)
            if f is not None:
                chosen = (tag, f, disp); break
        if chosen is None:
            print(f"{mid}: no imaginary mode in the analytic Hessians — skipped"); continue
        tag, f, disp = chosen
        for sign, s in (("plus", 1.0), ("minus", -1.0)):
            x = x0 + s * a.amplitude / BOHR * disp
            out = dict(g, coords_bohr=x.tolist(), restart_from=dict(molecule=mid, functional=tag, imaginary_cm=round(f, 1), displacement_angstrom=s * a.amplitude, date=time.strftime("%Y-%m-%d")))
            json.dump(out, open(os.path.join(d, f"restart_geometry_{sign}.json"), "w", encoding="utf-8"), indent=1)
        jobs.append(dict(id=mid, functional=tag, imaginary_cm=round(f, 1), files=[f"molecules/{mid}/restart_geometry_plus.json", f"molecules/{mid}/restart_geometry_minus.json"]))
        print(f"{mid}: {tag} imaginary {f:.1f} cm-1 → two restart geometries (±{a.amplitude} Å along the mode)")
    p = os.path.join(HERE, f"restart_jobs_{time.strftime('%Y-%m-%d')}.json"); json.dump(jobs, open(p, "w", encoding="utf-8"), indent=1)
    print(f"{len(jobs)} molecules with restart geometries → {p}")


if __name__ == "__main__":
    main()
