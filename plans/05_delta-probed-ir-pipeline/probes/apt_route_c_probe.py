"""TASKS 44 route C probe (11 Oct 2026): is the APT a by-product of the analytic Hessian? `corpus/analytic_hessians.py` (the labels route) solves
the CPHF response ∂C_occ/∂R inside `mf.Hessian().kernel()`; `dipole_derivs_cphf.py` (route B) solves the same response again. This probe runs the
labels route's B3LYP Hessian at its own settings with the response captured (`capture_mo1`), contracts it to the APT (`apt_from_mo1`, the one
implementation route B uses too), and measures, per molecule:
  - cost: SCF, Hessian, and the extra contraction, in seconds;
  - two routes: the APT against route B's saved file (dipole_b3lyp_cphf.npz) and the finite-difference APT (dipole_b3lyp_fd.npz) where present,
    the translation sum rule, and the Hessian against the saved hessian_b3lyp_analytic.npz;
  - the band heights (km/mol) from the captured APT against route B's.
Nothing is written into the molecule folders; one JSON per run goes to --out.

    python probes/apt_route_c_probe.py <dir with geometry.json> [more dirs] --out <file.json> [--threads 4] [--grid 99,590]
"""
import argparse
import json
import os
import sys
import time

import numpy as np
from pyscf import dft, gto, lib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "modules", "05_support_predictor", "corpus"))
from analytic_hessians import project_tr  # noqa: E402  (the labels route's own projector)
from apt import apt_from_mo1, capture_mo1, intensities, sum_rule  # noqa: E402

LIMITS = {"vs_route_b": 1e-4, "sum_rule": 5e-4, "vs_fd": 1e-3, "hessian": 1e-5}   # e, e, e, hartree/bohr² (route B's own limits; the
# Hessian limit: the same call at the same settings, so only the SCF's convergence separates the two)


def maxdiff(a, b):
    return float(np.abs(np.asarray(a) - np.asarray(b)).max())


def probe(d, grid, log=print):
    """One molecule at the labels route's settings (analytic_hessians.py: RKS, 6-31G* Cartesian, grid unpruned, conv_tol 1e-11)."""
    g = json.load(open(os.path.join(d, "geometry.json")))
    x = np.asarray(g["coords_bohr"], float)
    masses = np.asarray(g["masses_amu"], float)
    n = len(x)
    mol = gto.M(atom=[(s.capitalize(), tuple(c)) for s, c in zip(g["symbols"], x, strict=True)], unit="Bohr", basis="6-31g*", cart=True,
                symmetry=False, verbose=0, max_memory=20000)
    t0 = time.time()
    mf = dft.RKS(mol)
    mf.xc = "b3lyp"
    mf.grids.atom_grid = grid
    mf.grids.prune = None
    mf.conv_tol = 1e-11
    mf.kernel()
    if not mf.converged:
        raise RuntimeError(f"{d}: SCF not converged")
    t1 = time.time()
    hobj = mf.Hessian()
    captured = capture_mo1(hobj)
    H = hobj.kernel()
    t2 = time.time()
    P = apt_from_mo1(mf, captured["mo1"])
    t3 = time.time()
    Hc = H.transpose(0, 2, 1, 3).reshape(3 * n, 3 * n)
    Hc = 0.5 * (Hc + Hc.T)
    Hp = project_tr(Hc, masses, x)
    freq, km = intensities(P, Hp, masses)
    r = {"dir": d, "atoms": n, "seconds": {"scf": round(t1 - t0, 1), "hessian": round(t2 - t1, 1), "apt_contraction": round(t3 - t2, 2)},
         "sum_rule": sum_rule(P, mol.charge)}
    r["apt_share_of_hessian"] = round(r["seconds"]["apt_contraction"] / r["seconds"]["hessian"], 4)
    files = {k: os.path.join(d, f) for k, f in (("b", "dipole_b3lyp_cphf.npz"), ("fd", "dipole_b3lyp_fd.npz"), ("h", "hessian_b3lyp_analytic.npz"))}
    if os.path.exists(files["b"]):
        zb = np.load(files["b"])
        r["vs_route_b"] = maxdiff(P, zb["apt"])
        _, km_b = intensities(zb["apt"], Hp, masses)                        # route B's APT with this Hessian: the heights differ only by the APT
        r["km_vs_route_b"] = maxdiff(km, km_b)
        r["route_b_seconds"] = int(zb["seconds"]) if "seconds" in zb.files else None
    if os.path.exists(files["fd"]):
        r["vs_fd"] = maxdiff(P, np.load(files["fd"])["apt"])
    if os.path.exists(files["h"]):
        r["hessian_vs_saved"] = maxdiff(Hc, np.load(files["h"])["H_raw"])
    measured = {"vs_route_b": "vs_route_b", "sum_rule": "sum_rule", "vs_fd": "vs_fd", "hessian": "hessian_vs_saved"}
    r["checks"] = {k: r[m] <= LIMITS[k] for k, m in measured.items() if m in r}
    r["passed"] = all(r["checks"].values())
    strongest = np.argsort(km)[::-1][:3]
    r["strongest_bands"] = [[round(float(freq[i]), 1), round(float(km[i]), 2)] for i in strongest]
    log(f"{d}: {n} atoms; SCF {r['seconds']['scf']} s, Hessian {r['seconds']['hessian']} s, APT contraction {r['seconds']['apt_contraction']} s "
        f"({100 * r['apt_share_of_hessian']:.2f} % of the Hessian); sum rule {r['sum_rule']:.1e}"
        + (f"; vs route B {r['vs_route_b']:.1e} e, heights {r['km_vs_route_b']:.1e} km/mol" if "vs_route_b" in r else "")
        + (f"; vs FD {r['vs_fd']:.1e} e" if "vs_fd" in r else "")
        + (f"; Hessian vs saved {r['hessian_vs_saved']:.1e}" if "hessian_vs_saved" in r else "")
        + f" → {'PASS' if r['passed'] else 'FAIL'}", flush=True)
    return r


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("dirs", nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--grid", default="99,590")
    a = ap.parse_args()
    lib.num_threads(a.threads)
    grid = tuple(int(v) for v in a.grid.split(","))
    rows = [probe(d, grid) for d in a.dirs]
    with open(a.out, "w") as f:
        json.dump({"probe": "TASKS 44 route C", "limits": LIMITS, "threads": a.threads, "grid": list(grid), "molecules": rows}, f, indent=1)
    return 0 if all(r["passed"] for r in rows) else 3


if __name__ == "__main__":
    sys.exit(main())
