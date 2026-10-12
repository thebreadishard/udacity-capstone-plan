"""The pyscf pull request for issue #2702 (12 Oct 2026, on the user's word), measured: the Hessian CPHF's true residual and the solve time with
pyscf master as it is and with the patched `scf/cphf.py` (worktree ~/pyscf-wt-cphf, branch cphf-krylov-residual; compiled libraries copied
from the ~/pyscf-master build). Cases: water as in pyscf's own hessian/test/test_rks.py (6-31G, default grid) at HF and B3LYP, and the
reproduction posted on #2702 (benzene PBE/6-31G*, default grid). Run once per state of the worktree (`--labels-case`: only benzene PBE
at the labels route's setting, Cartesian 6-31G* and the unpruned (99, 590) grid, where the overlay of master's two files gave 5.6e-5):

    PYTHONPATH=~/pyscf-wt-cphf python pr_residual_check.py <label>      (WSL, qc05; appends to pr_residual_check.jsonl)
"""
import json
import os
import sys
import time

import numpy
import pyscf
from pyscf import gto, lib
from pyscf.hessian import rhf as rhf_hess

HERE = os.path.dirname(os.path.abspath(__file__))
lib.num_threads(4)
WATER = "O 0 0 0; H 0 -0.757 0.587; H 0 0.757 0.587"
BENZENE = """C 0.000 1.396 0.000; C 1.209 0.698 0.000; C 1.209 -0.698 0.000; C 0.000 -1.396 0.000; C -1.209 -0.698 0.000;
C -1.209 0.698 0.000; H 0.000 2.479 0.000; H 2.147 1.240 0.000; H 2.147 -1.240 0.000; H 0.000 -2.479 0.000;
H -2.147 -1.240 0.000; H -2.147 1.240 0.000"""


def residual(mf, mo1):
    """max over directions and elements of e_ai-scaled residual of the equations solve_withs1 solves (as in the #2702 comment)."""
    mol = mf.mol
    C, e, occ = mf.mo_coeff, mf.mo_energy, mf.mo_occ
    o, v = occ > 0, occ == 0
    mocc = C[:, o]
    fx = rhf_hess.gen_vind(mf, C, occ)
    e_ai = 1 / (e[v][:, None] - e[o])
    s1a = -mol.intor("int1e_ipovlp", comp=3)
    S = mf.get_ovlp()
    h1ao = mf.Hessian().make_h1(C, occ)
    worst = 0.0
    for ia, (_, _, p0, p1) in enumerate(mol.aoslice_by_atom()):
        s1ao = numpy.zeros((3,) + S.shape)
        s1ao[:, p0:p1] += s1a[:, p0:p1]
        s1ao[:, :, p0:p1] += s1a[:, p0:p1].transpose(0, 2, 1)
        s1 = lib.einsum("pq,xqr,ri->xpi", C.T, s1ao, mocc)
        h1 = lib.einsum("pq,xqr,ri->xpi", C.T, h1ao[ia], mocc)
        x = lib.einsum("pq,qr,xri->xpi", C.T, S, mo1[ia])
        r = (e[v][:, None] - e[o]) * x[:, v] + h1[:, v] - s1[:, v] * e[o] + fx(x)[:, v]
        worst = max(worst, float(abs(r * e_ai).max()))
    return worst


CASES = [("water HF", WATER, "6-31g", "RHF", None), ("water B3LYP", WATER, "6-31g", "b3lyp", None), ("benzene PBE", BENZENE, "6-31g*", "pbe", None)]
if "--labels-case" in sys.argv:      # our labels route's setting: Cartesian d, unpruned (99, 590) grid (the overlay test's case)
    CASES = [("benzene PBE cart (99,590)", BENZENE, "6-31g*", "pbe", (99, 590))]
rows = []
for name, atom, basis, method, grid in CASES:
    mol = gto.M(atom=atom, basis=basis, verbose=0, cart=grid is not None)
    mf = mol.RHF() if method == "RHF" else mol.RKS(xc=method)
    if grid is not None:
        mf.grids.atom_grid, mf.grids.prune = grid, None
    mf.run(conv_tol=1e-11)
    hobj = mf.Hessian()
    h1ao = hobj.make_h1(mf.mo_coeff, mf.mo_occ)
    t0 = time.time()
    mo1, _ = hobj.solve_mo1(mf.mo_energy, mf.mo_coeff, mf.mo_occ, h1ao)
    t = time.time() - t0
    rows.append({"label": sys.argv[1], "case": name, "residual": residual(mf, mo1), "solve_mo1_seconds": round(t, 1),
                 "tol": mf.conv_tol_cpscf * mol.natm, "pyscf_file": pyscf.__file__})
    print(json.dumps(rows[-1]), flush=True)
with open(os.path.join(HERE, "pr_residual_check.jsonl"), "a") as fh:
    for r in rows:
        fh.write(json.dumps(r) + "\n")
