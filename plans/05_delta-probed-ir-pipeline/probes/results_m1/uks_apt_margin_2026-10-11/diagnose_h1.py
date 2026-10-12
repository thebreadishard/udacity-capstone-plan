"""h1 with a step series (12 Oct 2026): pyscf's `make_h1` (∂F/∂R at fixed AO density, frozen grid) against [F(R+h; D0) − F(R−h; D0)] / 2h for
h = 0.01, 0.005, 0.0025 bohr, benzene carbon 0 (x, y), on the frozen reference grid; the Fock matrix split into its core, Coulomb (+ exact
exchange) and XC parts so the part that does not converge as h² is named. HF, PBE, B3LYP. No SCF at displaced geometries: seconds.

    python probes/results_m1/uks_apt_margin_2026-10-11/diagnose_h1.py   (WSL, qc05)
"""
import json
import os
import sys

import numpy as np
from pyscf import gto, lib

HERE = os.path.dirname(os.path.abspath(__file__))
PLAN = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(PLAN, "probes"))
from hessian_fixed_grid_fd import frozen_grids, make_mf  # noqa: E402

lib.num_threads(4)
D = os.path.join(PLAN, "modules", "05_support_predictor", "corpus", "molecules", "A_8448043181")
g = json.load(open(os.path.join(D, "geometry.json")))
mol = gto.M(atom=[(s.capitalize(), tuple(c)) for s, c in zip(g["symbols"], g["coords_bohr"], strict=True)], unit="Bohr", basis="6-31g*",
            cart=True, symmetry=False, verbose=0, max_memory=4000)
A = 0
x0 = mol.atom_coords(unit="Bohr")


def parts(mf, m, D0):
    """Core, Coulomb + exact exchange, XC parts of the Fock matrix of D0 at molecule m (the XC part is Veff − J + the exact-exchange share)."""
    vj, vk = mf.get_jk(m, D0)
    omega, alpha, hyb = mf._numint.rsh_and_hybrid_coeff(mf.xc, spin=m.spin)
    jk = vj - 0.5 * hyb * vk if hyb else vj
    veff = mf.get_veff(m, D0)
    return {"core": mf.get_hcore(m), "jk": jk, "xc": veff - jk, "total": mf.get_hcore(m) + veff}


out = {}
for xc in ("hf", "pbe", "b3lyp"):
    ref = make_mf(mol, xc, grid=(99, 590))
    ref.kernel()
    D0 = ref.make_rdm1()
    h1 = ref.Hessian().make_h1(ref.mo_coeff, ref.mo_occ, None, [A])[0]       # (3, nao, nao)
    rows = {}
    for d in (0, 1):
        for h in (1e-2, 5e-3, 2.5e-3):
            P = []
            for s in (+1, -1):
                x = x0.copy()
                x[A, d] += s * h
                m = mol.set_geom_(x, unit="Bohr", inplace=False)
                mf = make_mf(m, xc, grids=frozen_grids(ref.grids, m))
                P.append(parts(mf, m, D0))
            fd = {k: (P[0][k] - P[1][k]) / (2 * h) for k in P[0]}
            rows[f"{'xy'[d]} h={h:g}"] = {"total": float(np.abs(h1[d] - fd["total"]).max())}
        print(xc, json.dumps(rows), flush=True)
    out[xc] = rows
json.dump(out, open(os.path.join(HERE, "diagnose_h1.json"), "w"), indent=1)
