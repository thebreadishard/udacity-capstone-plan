"""The cheap fix to price (12 Oct 2026, for the design note): defect correction in batch. After pyscf's Hessian response, the residual of all 3N
directions in the solver's own system is formed at once; the correction equation (I + A) δ = r is solved by the same multi-root `lib.krylov`
pyscf uses (all 3N together, one batched operator call per cycle), x ← x + δ, until the residual is below 1e-8. Benzene B3LYP/6-31G* Cartesian,
grid (99, 590) unpruned; seconds, rounds, residuals, and the APT against last night's field route (agrees with FD to 3.9e-5). Compare
refine_timing.py: one-vector GMRES to the same end took 1,171 s against a 780 s Hessian.

    python probes/results_m1/krylov_report_2026-10-12/refine_batched.py   (WSL, qc05; ≈ 20 min)
"""
import json
import os
import sys
import time

import numpy as np
from pyscf import gto, lib
from pyscf.hessian import rhf as rhf_hess

HERE = os.path.dirname(os.path.abspath(__file__))
PLAN = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(PLAN, "probes"))
sys.path.insert(0, os.path.join(PLAN, "modules", "05_support_predictor", "corpus"))
from apt import apt_from_mo1, hessian_with_response  # noqa: E402
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
nmo, nocc = C.shape[1], int(o.sum())
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

b = []
for A in range(mol.natm):
    p0, p1 = aos[A, 2:]
    s1ao = np.zeros((3,) + S.shape)
    s1ao[:, p0:p1] += s1a[:, p0:p1]
    s1ao[:, :, p0:p1] += s1a[:, p0:p1].transpose(0, 2, 1)
    s1 = np.array([C.T @ x @ C[:, o] for x in s1ao])
    hs = np.array([C.T @ x @ C[:, o] for x in h1ao[A]]) - s1 * e[o]
    bb = hs.copy()
    bb[:, v] *= -e_ai
    bb[:, o] = -0.5 * s1[:, o]
    b.append(bb)
b = np.concatenate(b)                                                      # (3N, nmo, nocc), the solver's right-hand side
x = np.concatenate([np.array([C.T @ S @ m for m in mo1[A]]) for A in range(mol.natm)])
n_calls = [0]


def apply(xx):
    """The solver's operator on a batch: x + e_ai·fx(x) on the virtual rows, identity on the occupied rows."""
    n_calls[0] += 1
    xx = xx.reshape(-1, nmo, nocc)
    w = fx(xx).reshape(-1, nmo, nocc)
    y = xx.copy()
    y[:, v] += w[:, v] * e_ai
    return y


def vind_vo(xx):
    """(I + A) − I on the virtual rows only, in lib.krylov's convention ((1 + a) x = b)."""
    n_calls[0] += 1
    xx = xx.reshape(-1, nmo, nocc)
    w = fx(xx).reshape(-1, nmo, nocc)
    w[:, v] *= e_ai
    w[:, o] = 0.0
    return w.reshape(len(xx), -1)


rows = []
t1 = time.time()
for rnd in range(4):
    r = b - apply(x)
    r[:, o] = 0.0
    res = float(np.abs(r).max())
    P = apt_from_mo1(mf, [np.einsum("pq,xqi->xpi", C, x[3 * A:3 * A + 3]) for A in range(mol.natm)])
    rows.append({"round": rnd, "residual": res, "apt_vs_field": float(np.abs(P - P_field).max()), "seconds": round(time.time() - t1, 1),
                 "operator_calls": n_calls[0]})
    print(json.dumps(rows[-1]), flush=True)
    if res < 1e-8:
        break
    delta = lib.krylov(vind_vo, r.reshape(len(r), -1), tol=1e-9, max_cycle=50).reshape(r.shape)
    x = x + delta
json.dump({"hessian_seconds": round(t_hess, 1), "rounds": rows}, open(os.path.join(HERE, "refine_batched.json"), "w"), indent=1)
