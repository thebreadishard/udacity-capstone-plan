"""The response kernel itself (12 Oct 2026): pyscf's response function v1 = mf.gen_response(hermi=1)(dD) against the finite difference
[Veff(D0 + ε dD) − Veff(D0 − ε dD)] / 2ε on the same grid, for the CPHF density response dD of benzene's carbon 0 (x). If they differ, the CPHF
equations are solved with a kernel that is not the derivative of the potential the SCF uses — the cause found in `diagnose_riddle.py` (h1 right,
dD off). LDA (no density gradient), PBE (GGA), B3LYP; seconds each.

    python probes/results_m1/uks_apt_margin_2026-10-11/diagnose_kernel.py   (WSL, qc05)
"""
import json
import os
import sys

import numpy as np
from pyscf import gto, lib

HERE = os.path.dirname(os.path.abspath(__file__))
PLAN = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(PLAN, "probes"))
sys.path.insert(0, os.path.join(PLAN, "modules", "05_support_predictor", "corpus"))
from apt import hessian_with_response  # noqa: E402
from hessian_fixed_grid_fd import make_mf  # noqa: E402

lib.num_threads(4)
D = os.path.join(PLAN, "modules", "05_support_predictor", "corpus", "molecules", "A_8448043181")
g = json.load(open(os.path.join(D, "geometry.json")))
mol = gto.M(atom=[(s.capitalize(), tuple(c)) for s, c in zip(g["symbols"], g["coords_bohr"], strict=True)], unit="Bohr", basis="6-31g*",
            cart=True, symmetry=False, verbose=0, max_memory=4000)
out = {}
for xc in ("lda,vwn", "pbe", "b3lyp"):
    mf = make_mf(mol, xc, grid=(99, 590))
    mf.kernel()
    D0 = mf.make_rdm1()
    mocc = mf.mo_coeff[:, mf.mo_occ > 0]
    _, mo1 = hessian_with_response(mf.Hessian())
    dD = 2.0 * (mo1[0][0] @ mocc.T)
    dD = dD + dD.T
    v1 = mf.gen_response(hermi=1)(dD)
    row = {"v1_max_abs": float(np.abs(v1).max())}
    for eps in (1e-2, 1e-3):
        fd = (mf.get_veff(mol, D0 + eps * dD) - mf.get_veff(mol, D0 - eps * dD)) / (2 * eps)
        row[f"v1_vs_fd_eps{eps:g}"] = float(np.abs(v1 - fd).max())
    out[xc] = row
    print(xc, json.dumps(row), flush=True)
json.dump(out, open(os.path.join(HERE, "diagnose_kernel.json"), "w"), indent=1)
