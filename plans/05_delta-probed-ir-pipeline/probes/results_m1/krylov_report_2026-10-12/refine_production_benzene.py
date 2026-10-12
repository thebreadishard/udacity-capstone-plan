"""The production code on a real molecule before the install (12 Oct 2026, TASKS 44 (a)): benzene (A_8448043181) at the labels settings through
`analytic_hessians.labels_mol/labels_scf`, `apt.solve_response` and `apt.refine_response` — the code the labels server will run — against the
field route of 11–12 Oct (`../uks_apt_margin_2026-10-11/benzene_field.npz`, which agrees with FD of the dipole to 3.9e-5). Reference numbers
from `refine_batched.py` (the measurement the design note priced): residual 1.3e-4 → 7.8e-8 in one round, APT against the field 4.3e-4 → 3.75e-5.
No Hessian (≈ 5 min at 4 threads).

    python probes/results_m1/krylov_report_2026-10-12/refine_production_benzene.py   (WSL, qc05)
"""
import json
import os
import sys
import time

import numpy as np
from pyscf import lib

HERE = os.path.dirname(os.path.abspath(__file__))
PLAN = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(PLAN, "modules", "05_support_predictor", "corpus"))
import analytic_hessians as AH  # noqa: E402
from apt import apt_from_mo1, refine_response, solve_response, sum_rule  # noqa: E402

lib.num_threads(4)
D = os.path.join(PLAN, "modules", "05_support_predictor", "corpus", "molecules", "A_8448043181")
P_field = np.load(os.path.join(HERE, "..", "uks_apt_margin_2026-10-11", "benzene_field.npz"))["apt_grid_response"]
t0 = time.time()
mf, _ = AH.labels_scf(AH.labels_mol(json.load(open(os.path.join(D, "geometry.json")))), "b3lyp", (99, 590))
t_scf = time.time() - t0
hobj = mf.Hessian()
response = solve_response(hobj)
t_resp = time.time() - t0 - t_scf
mo1, info = refine_response(hobj, response.mo1, response.h1ao)
P_c, P_r = apt_from_mo1(mf, response.mo1), apt_from_mo1(mf, mo1)
row = {"scf_seconds": round(t_scf, 1), "response_seconds": round(t_resp, 1), "refine": info,
       "apt_vs_field_unrefined": float(np.abs(P_c - P_field).max()), "apt_vs_field_refined": float(np.abs(P_r - P_field).max()),
       "sum_rule_refined": sum_rule(P_r), "software": AH.software()}
print(json.dumps(row, indent=1), flush=True)
json.dump(row, open(os.path.join(HERE, "refine_production_benzene.json"), "w"), indent=1)
