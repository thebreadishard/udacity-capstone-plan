"""Is it the Krylov solver? (12 Oct 2026.) diagnose_residual.py found pyscf's CPHF solution for benzene PBE off its own equation by 1.1e-5 while
the true (frozen-grid FD) solution satisfies it to 4e-7, and tightening tol / max_cycle changed nothing (diagnose_rks_cphf.py). Here, with
pyscf's own operator (`hessian.rhf.gen_vind`) and right-hand side (as `scf/cphf.py solve_withs1` builds them) for every atom of benzene:
  (1) the residual of pyscf's returned solution in the solver's own system x + A x = b;
  (2) iterative refinement x ← x + (b − x − A x), each step's residual and route C's APT against the field route.
If the residual falls and the APT moves to the field route, the solver stopped early — not the physics.

    python probes/results_m1/uks_apt_margin_2026-10-11/diagnose_krylov.py   (WSL, qc05)
"""
import json
import os
import sys

import numpy as np
from pyscf import gto, lib
from pyscf.hessian import rhf as rhf_hess

HERE = os.path.dirname(os.path.abspath(__file__))
PLAN = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(PLAN, "probes"))
sys.path.insert(0, os.path.join(PLAN, "modules", "05_support_predictor", "corpus"))
from apt import apt_from_mo1  # noqa: E402
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
nao, nmo, nocc = C.shape[0], C.shape[1], int(o.sum())
hobj = mf.Hessian()
h1ao = hobj.make_h1(C, occ, None, hobj.atmlst)
mo1_py, _ = hobj.solve_mo1(e, C, occ, h1ao, None, hobj.atmlst)
fx = rhf_hess.gen_vind(mf, C, occ)
s1a = -mol.intor("int1e_ipovlp", comp=3)
e_ai = 1.0 / (e[v][:, None] - e[o][None, :])
aos = mol.aoslice_by_atom()


def system(A):
    """b and the occupied block of solve_withs1 for atom A (three directions)."""
    p0, p1 = aos[A, 2:]
    s1ao = np.zeros((3, nao, nao))
    s1ao[:, p0:p1] += s1a[:, p0:p1]
    s1ao[:, :, p0:p1] += s1a[:, p0:p1].transpose(0, 2, 1)
    s1 = np.array([C.T @ x @ C[:, o] for x in s1ao])
    hs = np.array([C.T @ x @ C[:, o] for x in h1ao[A]]) - s1 * e[o]
    b = hs.copy()
    b[:, v] *= -e_ai
    b[:, o] = -0.5 * s1[:, o]
    return b


def apply(x):
    """The solver's operator: x + e_ai * fx(x) on the virtual rows, identity on the occupied rows."""
    w = fx(x).reshape(-1, nmo, nocc)
    y = x.copy()
    y[:, v] += w[:, v] * e_ai
    return y


bs = [system(A) for A in range(mol.natm)]
xs = [C.T @ mf.get_ovlp() @ mo1_py[A] for A in range(mol.natm)]          # pyscf's solution in the MO basis, (3, nmo, nocc) per atom
P_f, _ = apt_field(mol, {"xc": "pbe", "grid": (99, 590)}, 1e-3, log=lambda *a, **k: None)
rows = []
for it in range(6):
    res = max(float(np.abs(bs[A] - apply(xs[A])).max()) for A in range(mol.natm))
    P = apt_from_mo1(mf, [np.einsum("pq,xqi->xpi", C, xs[A]) for A in range(mol.natm)])
    rows.append({"refinement_step": it, "residual_max": res, "apt_vs_field": float(np.abs(P - P_f).max())})
    print(json.dumps(rows[-1]), flush=True)
    xs = [xs[A] + (bs[A] - apply(xs[A])) for A in range(mol.natm)]
json.dump(rows, open(os.path.join(HERE, "diagnose_krylov.json"), "w"), indent=1)
