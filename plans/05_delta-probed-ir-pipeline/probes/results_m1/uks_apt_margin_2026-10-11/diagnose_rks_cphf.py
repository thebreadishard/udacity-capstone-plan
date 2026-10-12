"""Closed-shell CPHF convergence (12 Oct 2026): h1 and the response kernel are exact (diagnose_h1.py, diagnose_kernel.py), yet route C's dD is
off. The closed-shell solver (`scf/cphf.py`, a Krylov method, max_cycle 50, tol = conv_tol_cpscf × atoms in the block) was not tested tight
(the UKS test used `ucphf`). Benzene PBE: route C's APT with pyscf's defaults against max_cycle 200 / conv_tol_cpscf 1e-12, and pyscf's own
log of the solver (verbose 5) for 'CPHF not converged' lines; the field route's column for carbon 0 as the reference.

    python probes/results_m1/uks_apt_margin_2026-10-11/diagnose_rks_cphf.py   (WSL, qc05)
"""
import json
import os
import re
import sys

import numpy as np
from pyscf import gto, lib

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
LOG = os.path.join(HERE, "diagnose_rks_cphf_pyscf.log")
mf = make_mf(mol, "pbe", grid=(99, 590))
mf.kernel()


def response(max_cycle, conv_tol_cpscf):
    mf.conv_tol_cpscf = conv_tol_cpscf
    hobj = mf.Hessian()
    hobj.max_cycle = max_cycle
    hobj.verbose = 5
    hobj.stdout = open(LOG, "a")
    print(f"=== max_cycle {max_cycle}, conv_tol_cpscf {conv_tol_cpscf}", file=hobj.stdout, flush=True)
    h1 = hobj.make_h1(mf.mo_coeff, mf.mo_occ, None, hobj.atmlst)
    mo1, _ = hobj.solve_mo1(mf.mo_energy, mf.mo_coeff, mf.mo_occ, h1, None, hobj.atmlst)
    hobj.stdout.close()
    return apt_from_mo1(mf, mo1)


if os.path.exists(LOG):
    os.remove(LOG)
default_tol = mf.conv_tol_cpscf
P_def = response(50, default_tol)
P_tight = response(200, 1e-12)
P_f, _ = apt_field(mol, {"xc": "pbe", "grid": (99, 590)}, 1e-3, log=lambda *a, **k: None)
text = open(LOG).read()
out = {"conv_tol_cpscf_default": default_tol,
       "default_vs_field": float(np.abs(P_def - P_f).max()), "tight_vs_field": float(np.abs(P_tight - P_f).max()),
       "default_vs_tight": float(np.abs(P_def - P_tight).max()),
       "not_converged_lines": len(re.findall(r"not converge", text, re.I)), "log": os.path.basename(LOG)}
json.dump(out, open(os.path.join(HERE, "diagnose_rks_cphf.json"), "w"), indent=1)
print(json.dumps(out), flush=True)
