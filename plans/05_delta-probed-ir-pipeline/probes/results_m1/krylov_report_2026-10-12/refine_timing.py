"""The price and the gain of a residual-checked response for route C (12 Oct 2026, for the design note): benzene B3LYP/6-31G* Cartesian, grid
(99, 590) unpruned (the labels route's settings). pyscf 2.14.0's Hessian response, then GMRES on the solver's own system started from pyscf's
solution, every atom and direction, to a residual of 1e-9; seconds, operator applications, the residual before and after, and the APT against the
field route saved last night (`../uks_apt_margin_2026-10-11/benzene_field.npz`, which agrees with FD to 3.9e-5).

    python probes/results_m1/krylov_report_2026-10-12/refine_timing.py   (WSL, qc05; ≈ 15 min)
"""
import json
import os
import sys
import time

import numpy as np
from pyscf import gto, lib
from pyscf.hessian import rhf as rhf_hess
from scipy.sparse.linalg import LinearOperator, gmres

HERE = os.path.dirname(os.path.abspath(__file__))
PLAN = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(PLAN, "probes"))
sys.path.insert(0, os.path.join(PLAN, "modules", "05_support_predictor", "corpus"))
from apt import apt_from_mo1, hessian_with_response, sum_rule  # noqa: E402
from hessian_fixed_grid_fd import make_mf  # noqa: E402

lib.num_threads(4)
D = os.path.join(PLAN, "modules", "05_support_predictor", "corpus", "molecules", "A_8448043181")
g = json.load(open(os.path.join(D, "geometry.json")))
mol = gto.M(atom=[(s.capitalize(), tuple(c)) for s, c in zip(g["symbols"], g["coords_bohr"], strict=True)], unit="Bohr", basis="6-31g*",
            cart=True, symmetry=False, verbose=0, max_memory=4000)
mf = make_mf(mol, "b3lyp", grid=(99, 590))
mf.kernel()
C, e, occ = mf.mo_coeff, mf.mo_energy, mf.mo_occ
o, v = occ > 0, occ == 0
nmo, nocc, nvir = C.shape[1], int(o.sum()), int(v.sum())
S = mf.get_ovlp()
t0 = time.time()
hobj = mf.Hessian()
_, mo1 = hessian_with_response(hobj)
t_hess = time.time() - t0
h1ao = hobj.make_h1(C, occ, None, hobj.atmlst)
fx = rhf_hess.gen_vind(mf, C, occ)
e_ai = 1.0 / (e[v][:, None] - e[o][None, :])
s1a = -mol.intor("int1e_ipovlp", comp=3)
aos = mol.aoslice_by_atom()
P_field = np.load(os.path.join(HERE, "..", "uks_apt_margin_2026-10-11", "benzene_field.npz"))["apt_grid_response"]
n_apply = [0]

t1 = time.time()
before, after, refined = 0.0, 0.0, []
for A in range(mol.natm):
    p0, p1 = aos[A, 2:]
    cols = []
    for d in range(3):
        s1ao = np.zeros(S.shape)
        s1ao[p0:p1] += s1a[d, p0:p1]
        s1ao[:, p0:p1] += s1a[d, p0:p1].T
        s1 = C.T @ s1ao @ C[:, o]
        hs = C.T @ h1ao[A][d] @ C[:, o] - s1 * e[o]
        x_oo = -0.5 * s1[o]
        base = np.zeros((nmo, nocc))
        base[o] = x_oo
        w_oo = fx(base[None])[0]
        b = (-(hs[v] + w_oo[v]) * e_ai).ravel()

        def matvec(xvo):
            n_apply[0] += 1
            x = np.zeros((nmo, nocc))
            x[v] = xvo.reshape(nvir, nocc)
            return (xvo.reshape(nvir, nocc) + fx(x[None])[0][v] * e_ai).ravel()

        op = LinearOperator((nvir * nocc, nvir * nocc), matvec=matvec, dtype=float)
        x0 = (C.T @ S @ mo1[A][d])[v].ravel()
        before = max(before, float(np.abs(op.matvec(x0) - b).max()))
        xvo, info = gmres(op, b, x0=x0, rtol=1e-12, atol=1e-9, restart=200, maxiter=10)
        after = max(after, float(np.abs(op.matvec(xvo) - b).max()))
        x = np.zeros((nmo, nocc))
        x[v] = xvo.reshape(nvir, nocc)
        x[o] = x_oo
        cols.append(C @ x)
    refined.append(np.array(cols))
t_ref = time.time() - t1
P0 = apt_from_mo1(mf, mo1)
P1 = apt_from_mo1(mf, refined)
out = {"hessian_seconds": round(t_hess, 1), "refine_seconds": round(t_ref, 1), "operator_applications": n_apply[0],
       "residual_before": before, "residual_after": after,
       "apt_vs_field_before": float(np.abs(P0 - P_field).max()), "apt_vs_field_after": float(np.abs(P1 - P_field).max()),
       "sum_rule_before": sum_rule(P0), "sum_rule_after": sum_rule(P1)}
json.dump(out, open(os.path.join(HERE, "refine_timing.json"), "w"), indent=1)
print(json.dumps(out), flush=True)
