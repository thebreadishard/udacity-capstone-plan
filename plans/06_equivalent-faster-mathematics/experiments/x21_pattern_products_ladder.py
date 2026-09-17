#!/usr/bin/env python3
"""X21 - X14's pattern-product count across the whole molecule ladder (17 September 2026).

X14 counted 9 products = 18 gradients for naphthalene's symmetry pattern. Whether the gradient route
scales - whether its advantage over the energy deck grows or shrinks with molecule size - has never been
counted for anything else. This does it for the eight planar PAHs of deck_counts_planar.py, using the
same colouring code X14 used (x1c) and the same deck sizes the plan quotes.

Pure counting: the pattern is block-diagonal by irrep, so the colouring depends only on the irrep block
sizes. No energies, no molecules, milliseconds.

Also reported: what the deck becomes if Delta_2 comes from gradients and only the diagonal anharmonic
terms (c0, phi_iii, Delta_4) still come from energies - the 2M single-mode pattern block, which the deck
contains already.
"""
import json
import sys
from datetime import datetime
from math import comb
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent.parent / "05_delta-probed-ir-pipeline" / "probes"))
from x1c_triangular_substitution import (smallest_last_order, lower_pattern, intersection_graph,  # noqa: E402
                                         sequential_colouring, is_proper, recover_by_substitution)
import deck_counts_planar as dc  # noqa: E402

G_MEASURED = 4.07   # LNO-CCSD(T) AD ratio, benzene 6-31g, M2a cell 3, 17 September (1 repeat)


def pattern_from_irreps(modes):
    """Block-diagonal boolean pattern: two modes may couple only within the same irrep."""
    labels = []
    for ir, n in modes.items():
        labels += [ir] * n
    M = len(labels)
    P = np.zeros((M, M), dtype=bool)
    for i in range(M):
        for j in range(M):
            if i == j or labels[i] == labels[j]:
                P[i, j] = True
    return P, labels


def products(P, seed=0):
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
    rng = np.random.default_rng(seed)
    R = rng.standard_normal((M, M))
    R = (R + R.T) / 2
    R[~P] = 0.0
    probes = [R @ (colour == q).astype(float) for q in range(k)]
    err = float(np.abs(recover_by_substitution(P, pos, colour, probes) - R).max())
    return k, nm, err


def main():
    rows = []
    print("%-22s %4s %6s %7s %7s %9s %9s %11s %9s"
          % ("molecule", "M", "pairs", "H deck", "k", "gradients", "break-even", "at g=4.07", "vs deck"))
    for name, grp, n_at, a, b in dc.MOLECULES:
        modes = dc.modes_d2h(n_at, a, b) if grp == "D2h" else dc.modes_c2v(n_at, a)
        M, n, E, full, hdeck, hdiag, hp25 = dc.decks(modes, "Ag" if grp == "D2h" else "A1")
        P, labels = pattern_from_irreps(modes)
        assert P.shape[0] == M
        assert int(np.triu(P, 1).sum()) == E, (name, int(np.triu(P, 1).sum()), E)
        k, nm, err = products(P)
        grads = 2 * k
        breakeven = hdeck / grads
        cost = grads * G_MEASURED
        rows.append(dict(molecule=name.split(" (")[0], group=grp, M=M, pairs=E, h_deck=hdeck,
                         diagonal_block=hdiag, k=k, gradients=grads, colouring=nm, recovery_err=err,
                         breakeven_g=breakeven, energy_equivalents_at_g=cost, saving_vs_deck=hdeck / cost))
        print("%-22s %4d %6d %7d %7d %9d %9.1f %11.0f %9.1fx"
              % (name.split(" (")[0], M, E, hdeck, k, grads, breakeven, cost, hdeck / cost))

    print("\nRecovery error (exactness check, should be ~1e-16): max %.1e over the ladder"
          % max(r["recovery_err"] for r in rows))

    print("\nIf Delta_2 comes from gradients and only the diagonal anharmonic terms stay on energies")
    print("(the 2M single-mode block the deck already contains):")
    print("%-22s %10s %14s %12s %10s" % ("molecule", "old deck", "new: 2M + grads", "at g=4.07", "saving"))
    for r in rows:
        new_e = 2 * r["M"]
        new_cost = new_e + r["gradients"] * G_MEASURED
        r["new_deck_energies"] = new_e
        r["new_total_energy_equivalents"] = new_cost
        r["saving_total"] = r["h_deck"] / new_cost
        print("%-22s %10d %14s %12.0f %9.1fx"
              % (r["molecule"], r["h_deck"], "%d + %d" % (new_e, r["gradients"]), new_cost, r["saving_total"]))

    out = dict(date=datetime.now().strftime("%Y-%m-%d %H:%M"), g_measured=G_MEASURED,
               g_source="M2a cell 3, LNO-CCSD(T), benzene 6-31g, 17 Sep 2026, ONE repeat - provisional",
               note="counting only; pattern is block-diagonal by irrep so colouring depends on block sizes alone",
               rows=rows)
    json.dump(out, open(HERE / "x21_pattern_products_ladder.json", "w"), indent=1)
    print("\nwritten: x21_pattern_products_ladder.json")


if __name__ == "__main__":
    main()
