"""Repro for pyscf/pyscf#2702 / #3384: the Hessian CPHF (solve_mo1) of C12H9Cl, RKS B3LYP/6-31G* (Cartesian d), unpruned (99, 590) grid.

Prints, per case, the max |residual| of the equations solve_withs1 solves (scaled by e_ai, as in the comments on #2702), the wall time of
solve_mo1, and the cost in operator applications: calls of the Krylov operator and the number of vectors it was applied to (load-independent).
While solve_mo1 runs, a progress line (operator calls and vectors so far, minutes since its start) at most every PROGRESS_SECONDS: the
per-root fallback of the 3384 branches applies the operator root by root and can run for days (15 Oct 2026: 37 h without a line).

    python repro_2702.py              # all cases (C12H9Cl last: ~1.5 h of solve_mo1 on 4 threads)
    python repro_2702.py --small      # water B3LYP and benzene PBE only (minutes)
    python repro_2702.py --large      # C12H9Cl only
"""
import json
import sys
import time

import numpy
import pyscf
from pyscf import gto, lib
from pyscf.hessian import rhf as rhf_hess

lib.num_threads(int(sys.argv[sys.argv.index("--threads") + 1]) if "--threads" in sys.argv else 4)
C12H9CL = """
C   7.0561946558  1.9675933237  0.4137084126
C   5.8250122269  0.0372316896 -0.6559189720
Cl  7.7040681494 -2.1743229680 -2.3480015352
C   3.0676467199 -0.4643682858 -0.5881441974
C   1.9837532816 -2.6039491638 -1.8128285871
C  -0.5746803982 -3.0472881231 -1.7356694194
C  -2.2388275222 -1.3973336410 -0.4367877779
C  -4.8898247181 -1.7984476513 -0.3193338216
C  -6.4280837778 -0.1411653645  0.9663878541
C  -5.3833478880  1.9983619494  2.1965847783
C  -2.8229252505  2.4386833670  2.1172047623
C  -1.1799349562  0.7622714729  0.8043001378
C   1.4599297663  1.1686571561  0.6918049727
H   6.0601373645  3.4045989301  1.4812928887
H   9.0868336963  2.1615372256  0.2506454353
H   3.2003006089 -3.9032163736 -2.8223035205
H  -1.3523211427 -4.6944883524 -2.6865567111
H  -5.6847244528 -3.4408207315 -1.2646657739
H  -8.4540523624 -0.4657607011  1.0445282384
H  -6.6192719496  3.2913641594  3.2047863035
H  -2.0174979954  4.0781077862  3.0591347557
H   2.2016159441  2.8227543148  1.6521808833
"""  # bohr
WATER = "O 0 0 0; H 0 -0.757 0.587; H 0 0.757 0.587"
BENZENE = """C 0.000 1.396 0.000; C 1.209 0.698 0.000; C 1.209 -0.698 0.000; C 0.000 -1.396 0.000; C -1.209 -0.698 0.000;
C -1.209 0.698 0.000; H 0.000 2.479 0.000; H 2.147 1.240 0.000; H 2.147 -1.240 0.000; H 0.000 -2.479 0.000;
H -2.147 -1.240 0.000; H -2.147 1.240 0.000"""

COUNT = {"calls": 0, "vectors": 0}
PROGRESS_SECONDS = 600
PROGRESS = {"start": time.time(), "last": time.time()}
_krylov = lib.krylov


def counting_krylov(aop, b, *args, **kwargs):
    """lib.krylov with its operator counted (calls and vectors); nested calls get the counted operator already."""
    if getattr(aop, "_counted", False):
        return _krylov(aop, b, *args, **kwargs)

    def counted(x):
        COUNT["calls"] += 1
        COUNT["vectors"] += 1 if numpy.ndim(x) == 1 else len(x)
        now = time.time()
        if now - PROGRESS["last"] >= PROGRESS_SECONDS:
            PROGRESS["last"] = now
            print(f"  progress {time.strftime('%F %T')}: {COUNT['calls']} operator calls, {COUNT['vectors']} vectors, "
                  f"{(now - PROGRESS['start']) / 60:.0f} min into solve_mo1", flush=True)
        return aop(x)
    counted._counted = True
    return _krylov(counted, b, *args, **kwargs)


lib.krylov = counting_krylov


def residual(mf, mo1):
    """max over atoms, directions and elements of the e_ai-scaled residual of the equations solve_withs1 solves."""
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


CASES = [("water B3LYP/6-31G, default grid", dict(atom=WATER, basis="6-31g"), "b3lyp", None),
         ("benzene PBE/6-31G* cart, grid (99, 590)", dict(atom=BENZENE, basis="6-31g*", cart=True), "pbe", (99, 590)),
         ("C12H9Cl B3LYP/6-31G* cart, grid (99, 590)", dict(atom=C12H9CL, basis="6-31g*", cart=True, unit="Bohr", max_memory=20000), "b3lyp", (99, 590))]
if "--small" in sys.argv:
    CASES = CASES[:2]
if "--large" in sys.argv:
    CASES = CASES[2:]
for name, molargs, xc, grid in CASES:
    mol = gto.M(verbose=0, **molargs)
    mf = mol.RKS(xc=xc)
    if grid is not None:
        mf.grids.atom_grid, mf.grids.prune = grid, None
    mf.run(conv_tol=1e-11)
    hobj = mf.Hessian()
    h1ao = hobj.make_h1(mf.mo_coeff, mf.mo_occ)
    COUNT.update(calls=0, vectors=0)
    t0 = time.time()
    PROGRESS.update(start=t0, last=t0)
    mo1, _ = hobj.solve_mo1(mf.mo_energy, mf.mo_coeff, mf.mo_occ, h1ao)
    t = time.time() - t0
    print(json.dumps({"case": name, "residual": residual(mf, mo1), "solve_mo1_seconds": round(t, 1), "operator_calls": COUNT["calls"],
                      "operator_vectors": COUNT["vectors"], "pyscf": pyscf.__file__}), flush=True)
