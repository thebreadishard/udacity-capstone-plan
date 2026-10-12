"""The CPHF equations' residual (12 Oct 2026). h1 is exact (diagnose_h1), the kernel exact (diagnose_kernel), the solver converged
(diagnose_rks_cphf), yet route C's density response is off. Insert two solutions into pyscf's closed-shell CPHF equation for benzene carbon 0 (x),
PBE, grid (99, 590):
    r_ai = (ε_a − ε_i) U_ai + h1_ai − ε_i S1_ai + v1[dD(U)]_ai,   U_ij = −S1_ij / 2
(the form `scf/cphf.py solve_withs1` solves): (1) pyscf's U → r ≈ 0 shows the solver; (2) the true U from the frozen-grid FD of the density,
U_ai = (Cᵀ S dD S C)_ai / 2 → r ≠ 0 shows a term the equation lacks for DFT, and r's size and pattern name it. Also r for HF as the control.

    python probes/results_m1/uks_apt_margin_2026-10-11/diagnose_residual.py   (WSL, qc05)
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
A, d, H = 0, 0, 0.0025
out = {}
for xc in ("hf", "pbe"):
    mf = make_mf(mol, xc, grid=(99, 590))
    mf.kernel()
    C, e, occ = mf.mo_coeff, mf.mo_energy, mf.mo_occ
    o, v = occ > 0, occ == 0
    Co = C[:, o]
    S = mf.get_ovlp()
    hobj = mf.Hessian()
    h1 = hobj.make_h1(C, occ, None, [A])[0][d]
    h1all = hobj.make_h1(C, occ, None, hobj.atmlst)
    mo1all, _ = hobj.solve_mo1(e, C, occ, h1all, None, hobj.atmlst)
    U_py = C.T @ S @ mo1all[A][d]                                   # (nmo, nocc) in the MO basis
    p0, p1 = mol.aoslice_by_atom()[A, 2:]
    s1a = -mol.intor("int1e_ipovlp", comp=3)[d]
    s1 = np.zeros_like(S)
    s1[p0:p1] += s1a[p0:p1]
    s1[:, p0:p1] += s1a[p0:p1].T
    S1 = C.T @ s1 @ Co                                               # (nmo, nocc)
    vresp = mf.gen_response(C, occ, hermi=1)

    def residual(U, C=C, Co=Co, vresp=vresp, e=e, o=o, v=v, h1=h1, S1=S1):   # bound now: the loop rebinds these names
        dm = 2.0 * (C @ U @ Co.T)
        dm = dm + dm.T
        v1 = C.T @ vresp(dm) @ Co
        r = (e[:, None] - e[o][None, :]) * U + C.T @ h1 @ Co - S1 * e[o][None, :] + v1
        return r[v], dm

    r_py, dm_py = residual(U_py)
    x0 = mol.atom_coords(unit="Bohr")
    Dm = []
    for s in (+1, -1):
        x = x0.copy()
        x[A, d] += s * H
        m = mol.set_geom_(x, unit="Bohr", inplace=False)
        mfd = make_mf(m, xc, grids=frozen_grids(mf.grids, m))
        mfd.kernel(mf.make_rdm1())
        Dm.append(mfd.make_rdm1())
    dD_fd = (Dm[0] - Dm[1]) / (2 * H)
    U_fd = np.array(U_py)
    U_fd[v] = (C.T @ S @ dD_fd @ S @ Co)[v] / 2.0                    # the true virtual-occupied block; the occupied block stays −S1/2
    r_fd, dm_fd = residual(U_fd)
    out[xc] = {"residual_pyscf": float(np.abs(r_py).max()), "residual_fd_solution": float(np.abs(r_fd).max()),
               "U_vo_pyscf_vs_fd": float(np.abs(U_py[v] - U_fd[v]).max()), "U_vo_max": float(np.abs(U_fd[v]).max()),
               "dD_rebuilt_vs_fd": float(np.abs(dm_fd - dD_fd).max()),
               "U_oo_check_vs_fd": float(np.abs((C.T @ S @ dD_fd @ S @ Co)[o] / 2.0 - U_py[o]).max())}
    print(xc, json.dumps(out[xc]), flush=True)
json.dump(out, open(os.path.join(HERE, "diagnose_residual.json"), "w"), indent=1)
