"""Diagnosis (12 Oct 2026, after M3 read 'an analytic error'): is the analytic UKS APT's gap to the field route and to FD a CPHF that stopped
early? pyscf's Hessian solves the response with max_cycle = 50 and tol = mf.conv_tol_cpscf × (atoms in the block) and goes on unconverged
without an error. Here the same upstream UKS APT on P3c_00e041576d with max_cycle = 200 and conv_tol_cpscf = 1e-12, against the field route
(apt_field_route.py, which needs no response) and the FD Richardson value; the Hessian's asymmetry is recorded too.

    python probes/results_m1/uks_apt_margin_2026-10-11/diagnose_cphf.py   (WSL, qc05; ≈ 25 min at 4 threads)
"""
import json
import os
import sys
import time

import numpy as np
from pyscf import dft, gto, lib

HERE = os.path.dirname(os.path.abspath(__file__))
PLAN = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(PLAN, "probes"))
sys.path.insert(0, os.path.join(PLAN, "modules", "05_support_predictor", "corpus"))
from apt import sum_rule  # noqa: E402
from apt_route_props_probe import apt_from_upstream  # noqa: E402
from upstream_infrared import load  # noqa: E402

MID = "P3c_00e041576d"
D = os.path.join(PLAN, "modules", "05_support_predictor", "corpus", "shards_pool3", "a", "molecules", MID)
lib.num_threads(4)
infrared, _ = load()
g = json.load(open(os.path.join(D, "geometry.json")))
mol = gto.M(atom=[(s.capitalize(), tuple(c)) for s, c in zip(g["symbols"], g["coords_bohr"], strict=True)], unit="Bohr", basis="6-31g*",
            cart=True, symmetry=False, verbose=0, max_memory=4000, charge=1, spin=1)
mf = dft.UKS(mol)
mf.xc = "b3lyp"
mf.grids.atom_grid = (99, 590)
mf.grids.prune = None
mf.conv_tol = 1e-11
mf.kernel()
assert mf.converged
mf.conv_tol_cpscf = 1e-12
ir = infrared.uks.Infrared(mf)
ir.mf_hess = mf.Hessian()
ir.mf_hess.max_cycle = 200
t0 = time.time()
ir.kernel_dipderiv()
P = apt_from_upstream(ir.de)
H = ir.mf_hess.de.transpose(0, 2, 1, 3).reshape(3 * mol.natm, 3 * mol.natm)
field = np.load(os.path.join(HERE, f"{MID}_field.npz"))
fd = np.load(os.path.join(HERE, f"{MID}_fd.npz"))
star = (4 * fd["apt"] - fd["apt_h"]) / 3
default = np.load(os.path.join(HERE, f"{MID}_upstream_apt.npz"))["apt"]
out = {
    "seconds": round(time.time() - t0), "max_cycle": 200, "conv_tol_cpscf": 1e-12,
    "tight_vs_field_noGR": float(np.abs(P - field["apt_no_grid_response"]).max()),
    "tight_vs_fd_richardson": float(np.abs(P - star).max()),
    "default_vs_field_noGR": float(np.abs(default - field["apt_no_grid_response"]).max()),
    "tight_vs_default": float(np.abs(P - default).max()),
    "sum_rule_tight": sum_rule(P, 1),
    "hessian_asymmetry_tight": float(np.abs(H - H.T).max()),
}
json.dump(out, open(os.path.join(HERE, "diagnose_cphf.json"), "w"), indent=1)
print(json.dumps(out), flush=True)
