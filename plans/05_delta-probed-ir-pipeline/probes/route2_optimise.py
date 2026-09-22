"""Route 2, step 1 (22 September 2026): optimise a molecule at Mackie's level — B97-1 with the Dunning TZ2P basis (BSE 'CADPAC-TZ2P') —
with geomeTRIC in pyscf, and write the reference stub `<out_dir>/reference.json` in the form the QFF chain reads
({driver: hessian, molecule: {symbols, geometry in bohr}}); `pyscf_hessians_for_qff.py --xc B97-1 --basis CADPAC-TZ2P` then adds the
analytic Hessian, `make_qff_displacements.py --disp 0.10` the 2n stubs, and the same runner the 2n Hessians.

Usage: python route2_optimise.py <stageA.json with symbols + coords_bohr> <out_dir> [--threads 16] [--xc B97-1] [--basis CADPAC-TZ2P]
"""
import argparse
import json
import os
import time

import numpy as np
from pyscf import dft, gto, lib
from pyscf.geomopt.geometric_solver import optimize


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stagea")
    ap.add_argument("out_dir")
    ap.add_argument("--threads", type=int, default=16)
    ap.add_argument("--xc", default="B97-1")
    ap.add_argument("--basis", default="CADPAC-TZ2P")
    ap.add_argument("--grid", default="99,590")
    a = ap.parse_args()
    lib.num_threads(a.threads)
    s = json.load(open(a.stagea))
    symbols, coords = s["symbols"], np.array(s["coords_bohr"])
    rad, ang = (int(x) for x in a.grid.split(","))
    mol = gto.M(atom=[(sy, tuple(c)) for sy, c in zip(symbols, coords)], unit="Bohr", basis=a.basis, symmetry=False, verbose=0, max_memory=24000)
    mf = dft.RKS(mol)
    mf.xc = a.xc
    mf.grids.atom_grid = (rad, ang)
    mf.grids.prune = None
    mf.conv_tol = 1e-11
    mf.conv_tol_grad = 1e-8
    t0 = time.time()
    # tight convergence: the quartic force field is built by finite differences around this point
    mol_eq = optimize(mf, maxsteps=100, convergence_energy=1e-7, convergence_grms=1e-5, convergence_gmax=2e-5, convergence_drms=1e-4, convergence_dmax=2e-4)
    x = mol_eq.atom_coords()  # bohr
    mf2 = dft.RKS(mol_eq)
    mf2.xc = a.xc
    mf2.grids.atom_grid = (rad, ang)
    mf2.grids.prune = None
    mf2.conv_tol = 1e-11
    mf2.conv_tol_grad = 1e-8
    e = mf2.kernel()
    g = mf2.nuc_grad_method().kernel()
    os.makedirs(a.out_dir, exist_ok=True)
    rec = {"driver": "hessian", "molecule": {"symbols": list(symbols), "geometry": x.tolist()},
           "model": {"method": a.xc, "basis": a.basis}, "keywords": {"grid": [rad, ang], "optimiser": "geomeTRIC via pyscf.geomopt", "e_opt": float(e), "max_force_au": float(np.abs(g).max())},
           "note": "reference stub for route 2; return_result (the analytic Hessian) is added by pyscf_hessians_for_qff.py"}
    json.dump(rec, open(os.path.join(a.out_dir, "reference.json"), "w"))
    shift = np.linalg.norm(x - coords, axis=1)
    print(f"optimised in {time.time() - t0:.0f} s: E = {e:.9f}, max |force| {np.abs(g).max():.2e} E_h/bohr, atoms moved by at most {shift.max() * 0.529177:.4f} Å from the start; wrote {a.out_dir}/reference.json")


if __name__ == "__main__":
    main()
