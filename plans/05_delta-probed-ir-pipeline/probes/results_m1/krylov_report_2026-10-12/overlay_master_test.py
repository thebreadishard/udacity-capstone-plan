"""Does pyscf master's CPHF fix (#3334, after 2.14.0) solve our case? (12 Oct 2026.) Benzene, PBE/6-31G* Cartesian, grid (99, 590): the
Hessian's CPHF solution (all 3N right-hand sides at once, as `hessian.rhf.solve_mo1` does) with pyscf 2.14.0 as installed, then with master's
pure-Python `lib/linalg_helper.py` and `scf/cphf.py` laid over it (commit in master/COMMIT). For each: the solution's true residual in the
solver's own system (max over all 36 directions) and the APT against the field route (`probes/apt_field_route.py`, agreed with FD to 4e-5).
Also 2.14.0 solving one direction at a time (nroots = 1), to show whether the joint multi-root solve is the cause (pyscf issue #2702).

    python probes/results_m1/krylov_report_2026-10-12/overlay_master_test.py   (WSL, qc05; ≈ 25 min)
"""
import importlib.util
import json
import os
import sys
import time

import numpy as np
import pyscf.lib
import pyscf.scf.cphf
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
nmo, nocc = C.shape[1], int(o.sum())
hobj = mf.Hessian()
h1ao = hobj.make_h1(C, occ, None, hobj.atmlst)
fx = rhf_hess.gen_vind(mf, C, occ)
e_ai = 1.0 / (e[v][:, None] - e[o][None, :])
S = mf.get_ovlp()
s1a = -mol.intor("int1e_ipovlp", comp=3)
aos = mol.aoslice_by_atom()


def rhs(A):
    p0, p1 = aos[A, 2:]
    s1ao = np.zeros((3,) + S.shape)
    s1ao[:, p0:p1] += s1a[:, p0:p1]
    s1ao[:, :, p0:p1] += s1a[:, p0:p1].transpose(0, 2, 1)
    s1 = np.array([C.T @ x @ C[:, o] for x in s1ao])
    hs = np.array([C.T @ x @ C[:, o] for x in h1ao[A]]) - s1 * e[o]
    b = hs.copy()
    b[:, v] *= -e_ai
    b[:, o] = -0.5 * s1[:, o]
    return b


def residual(mo1s):
    """max |x + e_ai·fx(x)|_vo − b| over all atoms and directions, x in the MO basis (the solver's own system)."""
    worst = 0.0
    for A in range(mol.natm):
        x = np.array([C.T @ S @ m for m in mo1s[A]])
        w = fx(x).reshape(-1, nmo, nocc)
        y = x.copy()
        y[:, v] += w[:, v] * e_ai
        worst = max(worst, float(np.abs(y - rhs(A))[:, v].max()))
    return worst


def run(label):
    t0 = time.time()
    mo1, _ = hobj.solve_mo1(e, C, occ, h1ao, None, hobj.atmlst)
    sec = time.time() - t0
    P = apt_from_mo1(mf, mo1)
    return {"label": label, "seconds": round(sec, 1), "residual": residual(mo1), "apt_vs_field": float(np.abs(P - P_f).max())}


def run_one_root():
    """2.14.0's solver, one right-hand side at a time (as before pyscf's multi-root change)."""
    t0 = time.time()
    mo1s = []
    for A in range(mol.natm):
        cols = []
        for d in range(3):
            single = [None] * mol.natm
            single[A] = h1ao[A][d:d + 1]
            m, _ = hobj.solve_mo1(e, C, occ, single, None, [A])
            cols.append(m[A][0])
        mo1s.append(np.array(cols))
    sec = time.time() - t0
    P = apt_from_mo1(mf, mo1s)
    return {"label": "2.14.0, one right-hand side at a time", "seconds": round(sec, 1), "residual": residual(mo1s),
            "apt_vs_field": float(np.abs(P - P_f).max())}


P_f, _ = apt_field(mol, {"xc": "pbe", "grid": (99, 590)}, 1e-3, log=lambda *a, **k: None)
rows = [run("2.14.0 as installed")]
print(json.dumps(rows[-1]), flush=True)
rows.append(run_one_root())
print(json.dumps(rows[-1]), flush=True)
for name, target in (("linalg_helper", pyscf.lib), ("cphf", pyscf.scf.cphf)):     # master's pure-Python files over 2.14.0
    spec = importlib.util.spec_from_file_location(f"master_{name}", os.path.join(HERE, "master", f"{name}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if name == "linalg_helper":
        target.krylov = mod.krylov
    else:
        for attr in ("solve", "solve_nos1", "solve_withs1"):
            setattr(target, attr, getattr(mod, attr))
rows.append(run(f"master {open(os.path.join(HERE, 'master', 'COMMIT')).read().strip()[:8]} overlay"))
print(json.dumps(rows[-1]), flush=True)
json.dump(rows, open(os.path.join(HERE, "overlay_master_test.json"), "w"), indent=1)
