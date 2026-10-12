"""The proof (12 Oct 2026): solve pyscf's own CPHF system for benzene carbon 0 (x, y, z; PBE) with GMRES to a tight residual instead of
`lib.krylov`, and compare route C's APT column with the field route's. diagnose_krylov.py found pyscf's returned solution off its own system by
6.8e-5 (the Krylov solver stopped early whatever tol and max_cycle say). If the GMRES solution's column equals the field route's, the solver is
the cause of the APT error, not the equations.

    python probes/results_m1/uks_apt_margin_2026-10-11/diagnose_gmres.py   (WSL, qc05)
"""
import json
import os
import sys

import numpy as np
from pyscf import gto, lib
from pyscf.hessian import rhf as rhf_hess
from scipy.sparse.linalg import LinearOperator, gmres

HERE = os.path.dirname(os.path.abspath(__file__))
PLAN = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(PLAN, "probes"))
sys.path.insert(0, os.path.join(PLAN, "modules", "05_support_predictor", "corpus"))
from apt import apt_from_mo1, hessian_with_response  # noqa: E402
from apt_field_route import apt_field  # noqa: E402
from hessian_fixed_grid_fd import make_mf  # noqa: E402

lib.num_threads(4)
D = os.path.join(PLAN, "modules", "05_support_predictor", "corpus", "molecules", "A_8448043181")
g = json.load(open(os.path.join(D, "geometry.json")))
mol = gto.M(atom=[(s.capitalize(), tuple(c)) for s, c in zip(g["symbols"], g["coords_bohr"], strict=True)], unit="Bohr", basis="6-31g*",
            cart=True, symmetry=False, verbose=0, max_memory=4000)
mf = make_mf(mol, "pbe", grid=(99, 590))
mf.kernel()
C, e, occ = mf.mo_coeff, mf.mo_energy, mf.mo_occ
o, v = occ > 0, occ == 0
nao, nmo, nocc, nvir = C.shape[0], C.shape[1], int(o.sum()), int(v.sum())
A = 0
hobj = mf.Hessian()
h1ao = hobj.make_h1(C, occ, None, [A])[A]
mo1_py, _ = hobj.solve_mo1(e, C, occ, hobj.make_h1(C, occ, None, hobj.atmlst), None, hobj.atmlst)
fx = rhf_hess.gen_vind(mf, C, occ)
e_ai = 1.0 / (e[v][:, None] - e[o][None, :])
p0, p1 = mol.aoslice_by_atom()[A, 2:]
s1a = -mol.intor("int1e_ipovlp", comp=3)
r_int = mol.intor("int1e_r", comp=3)
Co = C[:, o]
S = mf.get_ovlp()
P_f, _ = apt_field(mol, {"xc": "pbe", "grid": (99, 590)}, 1e-3, log=lambda *a, **k: None)
rows = []
for d in range(3):
    s1ao = np.zeros((nao, nao))
    s1ao[p0:p1] += s1a[d, p0:p1]
    s1ao[:, p0:p1] += s1a[d, p0:p1].T
    s1 = C.T @ s1ao @ Co
    hs = C.T @ h1ao[d] @ Co - s1 * e[o]
    x_oo = -0.5 * s1[o]

    def full(xvo, x_oo=x_oo):
        x = np.zeros((nmo, nocc))
        x[v] = xvo.reshape(nvir, nocc)
        x[o] = x_oo
        return x

    def matvec(xvo, x_oo=x_oo):
        x = full(xvo, x_oo)
        x[o] = 0.0                                        # the operator acts on the virtual part; the occupied part goes to the right-hand side
        w = fx(x[None])[0]
        return (xvo.reshape(nvir, nocc) + w[v] * e_ai).ravel()

    w_oo = fx(full(np.zeros(nvir * nocc))[None])[0]       # response to the fixed occupied block
    b = (-(hs[v] + w_oo[v]) * e_ai).ravel()
    op = LinearOperator((nvir * nocc, nvir * nocc), matvec=matvec, dtype=float)
    xvo, info = gmres(op, b, rtol=1e-12, atol=0.0, restart=300, maxiter=20)
    resid = float(np.abs(op.matvec(xvo) - b).max())
    U = full(xvo)
    dD = 2.0 * (C @ U @ Co.T)
    dD = dD + dD.T
    U_py = C.T @ S @ mo1_py[A][d]
    dD_py = 2.0 * (C @ U_py @ Co.T)
    dD_py = dD_py + dD_py.T
    # the APT column differs between the two solutions only by −Tr(ΔdD r): compare that to the route C − field gap
    delta = -np.einsum("pq,tpq->t", dD - dD_py, r_int)
    rows.append({"direction": "xyz"[d], "gmres_info": int(info), "gmres_residual": resid,
                 "U_vo_gmres_vs_pyscf": float(np.abs(U[v] - U_py[v]).max()),
                 "apt_shift_gmres_minus_pyscf": delta.tolist()})
    print(json.dumps(rows[-1]), flush=True)

_, mo1 = hessian_with_response(mf.Hessian())
P_c = apt_from_mo1(mf, mo1)
for d, row in enumerate(rows):
    col = 3 * A + d
    gap = P_c[:, col] - P_f[:, col]
    row["routeC_minus_field"] = gap.tolist()
    row["after_gmres_minus_field"] = (gap + np.asarray(row["apt_shift_gmres_minus_pyscf"])).tolist()
    print(json.dumps({"direction": row["direction"], "routeC_minus_field": np.abs(gap).max(),
                      "gmres_minus_field": float(np.abs(np.asarray(row["after_gmres_minus_field"])).max())}), flush=True)
json.dump(rows, open(os.path.join(HERE, "diagnose_gmres.json"), "w"), indent=1)
