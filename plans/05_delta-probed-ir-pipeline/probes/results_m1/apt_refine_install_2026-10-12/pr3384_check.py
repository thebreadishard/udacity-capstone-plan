"""Does pyscf #3384 (per-RHS solve for hard Krylov cases) catch B_127dd8c4ed? (13 Oct 2026, on the user's word: 'meet #3384 eerst'.)

The labels route's own SCF and response (`analytic_hessians.labels_scf`, `apt.solve_response`) with pyscf from the #3384 worktree
(~/pyscf-wt-3384: e799bb1 merged onto master 52f5737). The quantity is the production one: the max |residual| of `solve_mo1`'s response,
scaled by e_ai, as `apt.refine_response` reports it before any correction (`bound=0, max_rounds=0`, so nothing is corrected). Production with
pyscf 2.14.0: 8.2e-5 (the APT file's cphf_residual_before).

    PYTHONPATH=~/pyscf-wt-3384 python pr3384_check.py      (WSL, qc05, 4 threads, nice; ≈ 1.6 h: the response alone took 5,746 s on 13 Oct)
"""
import json
import os
import sys
import time

import pyscf
from pyscf import lib

HERE = os.path.dirname(os.path.abspath(__file__))
PLAN = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(PLAN, "modules", "05_support_predictor", "corpus"))
import analytic_hessians as AH  # noqa: E402
from apt import refine_response, solve_response  # noqa: E402

lib.num_threads(4)
D = os.path.join(HERE, "floor_B_127dd8c4ed")
if "pyscf-wt-3384" not in pyscf.__file__:
    raise SystemExit(f"pyscf comes from {pyscf.__file__}, not the #3384 worktree")
t0 = time.time()
mf, _ = AH.labels_scf(AH.labels_mol(json.load(open(os.path.join(D, "geometry.json")))), "b3lyp", (99, 590))
hobj = mf.Hessian()
resp = solve_response(hobj)
t_resp = time.time() - t0
_, info = refine_response(hobj, resp.mo1, resp.h1ao, bound=0.0, max_rounds=0)
out = {"pyscf": pyscf.__file__, "version": pyscf.__version__, "residual": info["residual_before"], "seconds_response": round(t_resp)}
print(json.dumps(out), flush=True)
json.dump(out, open(os.path.join(D, "pr3384_check.json"), "w"), indent=1)
