"""Diagnosis (12 Oct 2026): the analytic CPHF APT (route C, `corpus/apt.py`) differs from the field route and FD on benzene by 4e-4 e while the
field route and FD agree to 4e-5. Bisect by functional at the same grid: HF (no exchange-correlation term), PBE (a GGA without exact exchange),
B3LYP (the labels route's functional). If HF agrees and the DFT functionals do not, the error sits in the XC part of pyscf's response; if HF
disagrees too, in the part every functional shares.

    python probes/results_m1/uks_apt_margin_2026-10-11/diagnose_xc.py   (WSL, qc05; ≈ 30 min at 4 threads)
"""
import json
import os
import sys
import time

import numpy as np
from pyscf import gto, lib

HERE = os.path.dirname(os.path.abspath(__file__))
PLAN = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(PLAN, "probes"))
sys.path.insert(0, os.path.join(PLAN, "modules", "05_support_predictor", "corpus"))
from apt import apt_from_mo1, hessian_with_response, sum_rule  # noqa: E402
from apt_field_route import apt_field, scf_in_field  # noqa: E402

lib.num_threads(4)
D = os.path.join(PLAN, "modules", "05_support_predictor", "corpus", "molecules", "A_8448043181")
g = json.load(open(os.path.join(D, "geometry.json")))
mol = gto.M(atom=[(s.capitalize(), tuple(c)) for s, c in zip(g["symbols"], g["coords_bohr"], strict=True)], unit="Bohr", basis="6-31g*",
            cart=True, symmetry=False, verbose=0, max_memory=4000)
out = {}
for xc in ("hf", "pbe", "b3lyp"):
    settings = {"xc": xc, "grid": (99, 590)}
    t0 = time.time()
    mf = scf_in_field(mol, settings, np.zeros(3))          # the same SCF settings as the field route, no field
    _, mo1 = hessian_with_response(mf.Hessian())
    P_c = apt_from_mo1(mf, mo1)
    P_f, _ = apt_field(mol, settings, 1e-3, log=lambda *a, **k: None)
    out[xc] = {"routeC_vs_field": float(np.abs(P_c - P_f).max()), "sum_rule_routeC": sum_rule(P_c), "sum_rule_field": sum_rule(P_f),
               "seconds": round(time.time() - t0)}
    print(xc, json.dumps(out[xc]), flush=True)
json.dump(out, open(os.path.join(HERE, "diagnose_xc.json"), "w"), indent=1)
