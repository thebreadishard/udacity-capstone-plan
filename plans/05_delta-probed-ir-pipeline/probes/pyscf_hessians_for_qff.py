"""Analytic DFT Hessians with pyscf at a set of displaced geometries, written as qcschema-like json so that
`qff_from_hessians.py` can assemble the quartic force field from them (21 September 2026).

Why: psi4 has no analytic B3LYP Hessian, so its Hessians are finite differences of gradients; a quartic force field by a second
finite difference on top of that is noisy (benzene, 20–21 September: two-route disagreement of the semi-diagonal quartic constants
median 22, max 1,265 cm⁻¹). pyscf has analytic RKS Hessians. This script takes the geometries of an existing cache directory (the
psi4/pyVPT2 displacements, so that the two force fields are compared point by point), computes the analytic Hessian at each, and
writes `<out_dir>/<same file name>` with the fields qff_from_hessians.py reads: driver, molecule{symbols, geometry (bohr)}, return_result.

Usage: python pyscf_hessians_for_qff.py <cache_dir> <out_dir> [--xc b3lyp] [--basis 6-31g*] [--grid 99,590] [--threads 4]
Note on the functional: pyscf's 'b3lyp' is the Gaussian definition (VWN3-type correlation); psi4's 'b3lyp' is the same family. The
noise diagnostic does not depend on this; absolute frequencies do at the cm⁻¹ level, and the report says which was used.
"""
import argparse
import glob
import json
import os
import time

import numpy as np


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cache_dir"); ap.add_argument("out_dir")
    ap.add_argument("--xc", default="b3lyp"); ap.add_argument("--basis", default="6-31g*")
    ap.add_argument("--grid", default="99,590"); ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--conv", type=float, default=1e-11)
    a = ap.parse_args()
    from pyscf import gto, dft, lib
    from pyscf.hessian import rks as rks_hess
    lib.num_threads(a.threads)
    os.makedirs(a.out_dir, exist_ok=True)
    rad, ang = (int(x) for x in a.grid.split(","))
    files = sorted(glob.glob(os.path.join(a.cache_dir, "*.json")))
    done = 0; t_all = time.time()
    for f in files:
        d = json.load(open(f))
        if not isinstance(d, dict) or d.get("driver") != "hessian" or "molecule" not in d:
            continue
        out = os.path.join(a.out_dir, os.path.basename(f))
        if os.path.exists(out):
            done += 1; continue
        sym = d["molecule"]["symbols"]; geom = np.array(d["molecule"]["geometry"], float).reshape(-1, 3)
        mol = gto.M(atom=[(s, tuple(x)) for s, x in zip(sym, geom)], unit="Bohr", basis=a.basis, symmetry=False, verbose=0)
        mf = dft.RKS(mol); mf.xc = a.xc; mf.grids.atom_grid = (rad, ang); mf.grids.prune = None
        mf.conv_tol = a.conv; mf.conv_tol_grad = 1e-8; mf.max_cycle = 200
        t0 = time.time(); e = mf.kernel()
        if not mf.converged:
            raise SystemExit(f"SCF not converged at {f}")
        H = rks_hess.Hessian(mf).kernel()                      # (natm, natm, 3, 3) in E_h/bohr²
        n = mol.natm; Hc = H.transpose(0, 2, 1, 3).reshape(3 * n, 3 * n)
        rec = {"driver": "hessian", "model": {"method": f"pyscf {a.xc}", "basis": a.basis},
               "keywords": {"grid": [rad, ang], "conv_tol": a.conv, "scf_type": "exact integrals", "hessian": "analytic (pyscf.hessian.rks)"},
               "molecule": {"symbols": sym, "geometry": geom.reshape(-1).tolist()},
               "return_result": Hc.reshape(-1).tolist(), "properties": {"return_energy": float(e)},
               "provenance": {"creator": "pyscf", "routine": "pyscf_hessians_for_qff.py", "wall_s": round(time.time() - t0, 1)}}
        json.dump(rec, open(out, "w"))
        done += 1
        print(f"[{time.strftime('%H:%M:%S')}] {done}/{len(files)} {os.path.basename(f)} E = {e:.8f} in {time.time()-t0:.0f} s", flush=True)
    print(f"done: {done} Hessians in {(time.time()-t_all)/60:.1f} min")


if __name__ == "__main__":
    main()
