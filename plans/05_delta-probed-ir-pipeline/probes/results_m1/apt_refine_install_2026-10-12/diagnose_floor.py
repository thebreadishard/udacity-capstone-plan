"""Why do two labels APTs miss the CPHF bound of 1e-6 after three refinement rounds? (13 Oct 2026, ≈ 02:0x; exploratory, decided alone on the
user's standing word of 12 Oct night.)

B_1194d7a42a ended at 1.1e-6 and B_127dd8c4ed at 2.1e-6. Of the 20 refined labels APTs, the residuals after refinement lie between 4e-7 and
2e-6 at 22 atoms, and the lanes are moving to larger molecules. There are two explanations, and each has its own remedy:

1. **Solver.** The refinement's correction is solved by the same multi-root `lib.krylov` that stalls (pyscf #2702). Per-column solves would
   reach the bound. That is #3384's own remedy upstream.
2. **Floor.** The operator itself is only accurate to ~1e-6 at this size (grid and integral screening). No solver goes below that, and these
   molecules need the field route as their second route.

**Rule, fixed before the run.** On B_127dd8c4ed, at the labels settings:
- reproduce the three batched rounds of `apt.refine_response`;
- solve every column still above 1e-7 with scipy GMRES on that column alone, from the refined solution, with rtol 1e-10 and at most
  300 iterations;
- read the largest residual left.

Ways it can come out:
- ≤ 1e-7 on every column → **solver** (1).
- Columns stalling ≥ 5e-7 → **floor** (2). A floor would also show as the batched rounds' residual flattening.
- Between → noted.

As a check on the floor reading, the operator is applied twice to the same vector and the difference is reported, but only if fx is not
deterministic. It is deterministic, so only (1)/(2) apply.

    python diagnose_floor.py   (WSL, qc05, 4 threads; ≈ 2 h)
"""
import json
import os
import sys
import time

import numpy as np
from pyscf import lib
from pyscf.hessian import rhf as rhf_hess
from scipy.sparse.linalg import LinearOperator, gmres

HERE = os.path.dirname(os.path.abspath(__file__))
PLAN = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(PLAN, "modules", "05_support_predictor", "corpus"))
import analytic_hessians as AH  # noqa: E402
from apt import refine_response, solve_response  # noqa: E402

lib.num_threads(4)
D = os.path.join(HERE, "floor_B_127dd8c4ed")
t0 = time.time()
mf, _ = AH.labels_scf(AH.labels_mol(json.load(open(os.path.join(D, "geometry.json")))), "b3lyp", (99, 590))
hobj = mf.Hessian()
resp = solve_response(hobj)
print(json.dumps({"step": "response", "seconds": round(time.time() - t0)}), flush=True)
rounds = []
for nr in (1, 2, 3, 5):
    _, info = refine_response(hobj, resp.mo1, resp.h1ao, bound=0.0, max_rounds=nr)
    rounds.append({"rounds": nr, "residual_after": info["residual_after"], "seconds": info["seconds"]})
    print(json.dumps(rounds[-1]), flush=True)
mo1, info = refine_response(hobj, resp.mo1, resp.h1ao, bound=0.0, max_rounds=3)

# the refined solution's columns, in the solver's own system (the same construction as apt.refine_response)
mol = mf.mol
C, e, occ = mf.mo_coeff, mf.mo_energy, mf.mo_occ
o, v = occ > 0, occ == 0
nmo, nocc = C.shape[1], int(o.sum())
mocc = C[:, o]
e_ai = 1.0 / (e[v][:, None] - e[o][None, :])
S = mf.get_ovlp()
s1a = -mol.intor("int1e_ipovlp", comp=3)
b = []
for A, (_, _, p0, p1) in enumerate(mol.aoslice_by_atom()):
    s1ao = np.zeros((3,) + S.shape)
    s1ao[:, p0:p1] += s1a[:, p0:p1]
    s1ao[:, :, p0:p1] += s1a[:, p0:p1].transpose(0, 2, 1)
    s1 = np.einsum("pq,xqr,ri->xpi", C.T, s1ao, mocc)
    bb = np.einsum("pq,xqr,ri->xpi", C.T, np.asarray(resp.h1ao[A]), mocc) - s1 * e[o]
    bb[:, v] *= -e_ai
    bb[:, o] = -0.5 * s1[:, o]
    b.append(bb)
b = np.concatenate(b)
x = np.concatenate([np.einsum("pq,qr,xri->xpi", C.T, S, mo1[A]) for A in range(mol.natm)])
fx = rhf_hess.gen_vind(mf, C, occ)


def a_vo(xx):
    w = fx(xx.reshape(-1, nmo, nocc)).reshape(-1, nmo, nocc)
    w[:, v] *= e_ai
    w[:, o] = 0.0
    return w


r = b - x - a_vo(x)
col = np.abs(r.reshape(len(r), -1)).max(axis=1)
w1, w2 = a_vo(x[:2]), a_vo(x[:2])
out = {"atoms": mol.natm, "nmo": nmo, "nocc": nocc, "rounds": rounds, "residual_after_3": float(col.max()),
       "columns_above_1e-7": int((col > 1e-7).sum()), "fx_repeat_max_diff": float(np.abs(w1 - w2).max())}
print(json.dumps({k: out[k] for k in ("residual_after_3", "columns_above_1e-7", "fx_repeat_max_diff")}), flush=True)

vshape = (nmo, nocc)
gm = []
t1 = time.time()
for j in np.argsort(-col)[: int((col > 1e-7).sum())][:12]:               # the worst twelve columns at most
    rhs = b[j].copy()

    def mv(y):
        y = y.reshape(1, *vshape)
        return (y + a_vo(y)).ravel()
    op = LinearOperator((nmo * nocc, nmo * nocc), matvec=mv, dtype=float)
    sol, info_g = gmres(op, rhs.ravel(), x0=x[j].ravel(), rtol=1e-10, atol=0.0, maxiter=300, restart=60)
    res_j = float(np.abs(rhs.ravel() - mv(sol)).max())
    gm.append({"column": int(j), "before": float(col[j]), "after": res_j, "gmres_info": int(info_g)})
    print(json.dumps(gm[-1]), flush=True)
out.update(gmres_columns=gm, gmres_seconds=round(time.time() - t1), max_after_gmres=max(g["after"] for g in gm) if gm else None)
worst = out["max_after_gmres"]
out["reading"] = ("solver (1)" if worst is not None and worst <= 1e-7 else "floor (2)" if worst is not None and worst >= 5e-7 else "between: noted")
json.dump(out, open(os.path.join(D, "diagnose_floor.json"), "w"), indent=1)
print(json.dumps({"reading": out["reading"], "max_after_gmres": worst, "seconds_total": round(time.time() - t0)}), flush=True)
