#!/usr/bin/env python3
"""X20 - how gradient noise propagates through X14's 18-gradient construction (17 September 2026).

X14 recovers naphthalene's whole Delta_2 from 9 pattern products (18 gradients) with a recovery error
of 0.0e+00 - but that is with EXACT products. Real gradients carry noise, and the substitution
(Curtis-Powell-Reid) recovery back-substitutes previously recovered elements, so error can accumulate
along the elimination order. This measures that, on the real Delta_2 of the naphthalene dry run, and
compares three things at once:

  substitution, symmetry pattern   9 products  = 18 gradients   (X14 row a)
  least squares, symmetry pattern  9 products  = 18 gradients   (same data, stabler solve)
  substitution, dense              48 products = 96 gradients   (X14 row d, stage C's mode G)

Noise model: a product is (g(+q) - g(-q)) / 2q from two gradients each carrying sigma_g per projected
component, so the product component carries sigma_g * sqrt(2) / (2q), with q = 1 as in the deck.
sigma_g runs over the plan's own grid, 0.5 to 5 uE_h per unit q, extended downward to locate the
threshold at which the worst family clears 0.5 cm-1.

Deliverable: the gradient accuracy the 18-gradient route needs, in the same units the plan measures.
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from x1c_triangular_substitution import (smallest_last_order, lower_pattern, intersection_graph,  # noqa: E402
                                         sequential_colouring, is_proper, recover_by_substitution)

DRY = HERE.parent.parent / "05_delta-probed-ir-pipeline" / "probes" / "results_dryrun" / "naphthalene_sym"
SIGMAS = [0.0, 0.01, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0]   # uE_h per unit q; 0.5-5 is the plan's grid
NREP = 200
Q_AMP = 1.0
HARTREE_TO_CM = 219474.63
TARGET_CM = 0.5


def colouring(P):
    M = P.shape[0]
    H = P.copy()
    np.fill_diagonal(H, False)
    pos = smallest_last_order(H)
    Lp = lower_pattern(P, pos)
    Gu = intersection_graph(Lp)
    pos_gu = smallest_last_order(Gu)
    cands = []
    for c, nm in ((sequential_colouring(Gu, list(np.argsort(-Gu.sum(1)))), "largest-first"),
                  (sequential_colouring(Gu, sorted(range(M), key=lambda v: pos_gu[v])), "smallest-last")):
        if is_proper(Gu, c):
            cands.append((int(c.max() + 1), nm, c))
    k, nm, colour = min(cands, key=lambda t: t[0])
    return pos, colour, k


def ls_design(P, colour, k):
    """Rows: one per (probe q, component i). Columns: the upper-triangle elements allowed by P."""
    M = P.shape[0]
    idx = [(i, j) for i in range(M) for j in range(i, M) if P[i, j]]
    col_of = {p: c for c, p in enumerate(idx)}
    rows, n = [], len(idx)
    for q in range(k):
        seed = (colour == q)
        for i in range(M):
            r = np.zeros(n)
            for j in range(M):
                if seed[j] and P[i, j]:
                    r[col_of[(min(i, j), max(i, j))]] += 1.0
            rows.append(r)
    return np.array(rows), idx


def freq_err(D_rec, D_true, omega, families):
    s = np.sqrt(omega)
    W2 = np.diag(omega ** 2)
    f_r = np.sqrt(np.abs(np.linalg.eigvalsh(W2 + D_rec * np.outer(s, s)))) * HARTREE_TO_CM
    f_t = np.sqrt(np.abs(np.linalg.eigvalsh(W2 + D_true * np.outer(s, s)))) * HARTREE_TO_CM
    f_r.sort(); f_t.sort()
    d = f_r - f_t
    return {fam: float(np.sqrt(np.mean(d[[k for k, f in enumerate(families) if f == fam]] ** 2)))
            for fam in sorted(set(families))}


def main():
    a = json.load(open(DRY / "stageA.json"))
    z = np.load(DRY / "stageA_hessians.npz")
    omega, D2 = z["omega_au"], z["D2_direct"]
    M = a["M"]
    irreps = a["irreps"]
    families = a["families"]

    P_sym = np.zeros((M, M), dtype=bool)
    for i in range(M):
        for j in range(M):
            if i == j or irreps[i] == irreps[j]:
                P_sym[i, j] = True
    eligible = int((np.triu(P_sym, 1)).sum())
    P_dense = np.ones((M, M), dtype=bool)

    outside = float(np.abs(D2[~P_sym]).max())
    inside = float(np.abs(D2[P_sym]).max())
    print("naphthalene, M = %d, same-irrep pairs = %d (X14 row (a) says 141)" % (M, eligible))
    print("largest |Delta_2| element OUTSIDE the symmetry pattern: %.3e uE_h (inside: %.3e) -- the prior itself"
          % (outside * 1e6, inside * 1e6))

    setups = []
    for name, P in (("symmetry", P_sym), ("dense", P_dense)):
        pos, colour, k = colouring(P)
        A, idx = ls_design(P, colour, k)
        setups.append(dict(name=name, P=P, pos=pos, colour=colour, k=k, A=A, idx=idx))
        print("  %-9s pattern: %d products = %d gradients, %d unknown elements, %d equations"
              % (name, k, 2 * k, len(idx), A.shape[0]))

    Dtrue = {s["name"]: np.where(s["P"], D2, 0.0) for s in setups}
    rng = np.random.default_rng(20260917)
    rows = []
    print("\n%-28s %9s %12s %12s %12s" % ("method (gradients)", "sigma_g", "elem RMS", "worst family", "amplif."))
    for sg in SIGMAS:
        sp = sg * 1e-6 * np.sqrt(2) / (2 * Q_AMP)          # noise per product component, E_h
        for s in setups:
            R = Dtrue[s["name"]]
            probes_exact = [R @ (s["colour"] == q).astype(float) for q in range(s["k"])]
            for method in ("substitution", "least-squares"):
                if s["name"] == "dense" and method == "least-squares":
                    continue
                e_el, e_fam = [], []
                for _ in range(NREP if sg > 0 else 1):
                    probes = [p + rng.normal(0, sp, size=M) for p in probes_exact]
                    if method == "substitution":
                        D_rec = recover_by_substitution(s["P"], s["pos"], s["colour"], probes)
                    else:
                        y = np.concatenate(probes)
                        sol, *_ = np.linalg.lstsq(s["A"], y, rcond=None)
                        D_rec = np.zeros((M, M))
                        for (i, j), v in zip(s["idx"], sol):
                            D_rec[i, j] = D_rec[j, i] = v
                    e_el.append(np.sqrt(np.mean((D_rec - R) ** 2)))
                    e_fam.append(max(freq_err(D_rec, R, omega, families).values()))
                el = float(np.mean(e_el)) * 1e6
                fam = float(np.mean(e_fam))
                amp = el / (sg if sg > 0 else np.nan)
                label = "%s, %s (%d)" % (s["name"], method, 2 * s["k"])
                print("%-28s %9.2f %12.4f %12.4f %12.2f" % (label, sg, el, fam, amp))
                rows.append(dict(pattern=s["name"], method=method, gradients=2 * s["k"], sigma_g_uEh=sg,
                                 elem_rms_uEh=el, worst_family_cm=fam, amplification=None if sg == 0 else amp))

    print("\nsigma_g the plan must hold to keep the worst family under %.1f cm-1:" % TARGET_CM)
    for key in [("symmetry", "substitution"), ("symmetry", "least-squares"), ("dense", "substitution")]:
        pts = [(r["sigma_g_uEh"], r["worst_family_cm"]) for r in rows
               if (r["pattern"], r["method"]) == key and r["sigma_g_uEh"] > 0]
        pts.sort()
        ok = [s for s, f in pts if f <= TARGET_CM]
        lab = "%s, %s" % key
        if not ok:
            print("  %-28s never: even sigma_g = %.2f gives %.2f cm-1" % (lab, pts[0][0], pts[0][1]))
        elif len(ok) == len(pts):
            print("  %-28s always on this grid (up to sigma_g = %.1f)" % (lab, pts[-1][0]))
        else:
            print("  %-28s sigma_g <= %.2f uE_h per unit q" % (lab, max(ok)))
    out = dict(date=datetime.now().strftime("%Y-%m-%d %H:%M"), molecule="naphthalene", M=M,
               eligible_pairs=eligible, nrep=NREP, q_amp=Q_AMP, target_cm=TARGET_CM,
               max_outside_pattern_uEh=outside * 1e6, rows=rows,
               note="noise model: product component carries sigma_g*sqrt(2)/(2q); Delta_2 is the dry run's direct one")
    json.dump(out, open(HERE / "x20_gradient_noise_propagation.json", "w"), indent=1)
    print("\nwritten: x20_gradient_noise_propagation.json")


if __name__ == "__main__":
    main()
