"""Deck sizes per molecule under the symmetry prior, from the point group alone (2026-09-15, for P27).

A planar molecule of D2h or C2v symmetry: the number of vibrational modes per irrep follows from the
character of the 3N Cartesian representation, which needs only the atom count and the number of atoms
lying on each in-plane symmetry axis. The symmetry prior of the proposal (§3.2) keeps couplings between
modes of the same irrep only, so the deck costs

    full deck            4M + 2E              (M modes, E same-irrep pairs; duration_table.py convention)
    H deck (I14/dec. 37) 4n + 2(M-n) + 2C(n,2) + (E - C(n,2))   (n totally symmetric modes; ± pairs
                                                                 only for totally symmetric patterns)
    diagonal H deck      4n + 2(M-n)
    H + P25              diagonal H deck + 0.4 x (couplings of the H deck)   (19/47 at benzene, X10)

Check printed first: naphthalene must give 9 ag, 4 b1g, 3 b2g, 8 b3g, 4 au, 8 b1u, 8 b2u, 4 b3u and E = 141
(proposal §3.2 / X13). Coronene (D6h, degenerate irreps) is not counted here; the duration table's 842 stands.
"""
from math import comb

# D2h, molecule in the yz plane, z = long in-plane axis, y = short in-plane axis, x = out of plane.
# Operation order: E, C2z, C2y, C2x, i, s_xy, s_xz, s_yz.  Characters per unmoved atom: 3, -1, -1, -1, -3, 1, 1, 1.
D2H = {"Ag": (1, 1, 1, 1, 1, 1, 1, 1), "B1g": (1, 1, -1, -1, 1, 1, -1, -1), "B2g": (1, -1, 1, -1, 1, -1, 1, -1),
       "B3g": (1, -1, -1, 1, 1, -1, -1, 1), "Au": (1, 1, 1, 1, -1, -1, -1, -1), "B1u": (1, 1, -1, -1, -1, -1, 1, 1),
       "B2u": (1, -1, 1, -1, -1, 1, -1, 1), "B3u": (1, -1, -1, 1, -1, 1, 1, -1)}
D2H_TRANS_ROT = {"B1u": 1, "B2u": 1, "B3u": 1, "B1g": 1, "B2g": 1, "B3g": 1}
# C2v, molecule in the yz plane, z = the C2 axis.  Order: E, C2, s_xz, s_yz.
C2V = {"A1": (1, 1, 1, 1), "A2": (1, 1, -1, -1), "B1": (1, -1, 1, -1), "B2": (1, -1, -1, 1)}
C2V_TRANS_ROT = {"A1": 1, "B1": 2, "B2": 2, "A2": 1}


def modes_d2h(n_atoms, on_long, on_short):
    chi = (3 * n_atoms, -on_long, -on_short, 0, 0, on_short, on_long, n_atoms)
    return {ir: sum(a * b for a, b in zip(chi, row)) // 8 - D2H_TRANS_ROT.get(ir, 0) for ir, row in D2H.items()}


def modes_c2v(n_atoms, on_axis):
    chi = (3 * n_atoms, -on_axis, on_axis, n_atoms)
    return {ir: sum(a * b for a, b in zip(chi, row)) // 4 - C2V_TRANS_ROT.get(ir, 0) for ir, row in C2V.items()}


def decks(modes, ts):
    M = sum(modes.values()); E = sum(comb(k, 2) for k in modes.values()); n = modes[ts]
    full = 4 * M + 2 * E
    h_diag = 4 * n + 2 * (M - n)
    h_coup = 2 * comb(n, 2) + (E - comb(n, 2))
    return M, n, E, full, h_diag + h_coup, h_diag, h_diag + round(0.4 * h_coup)


MOLECULES = [  # name, group, atoms, atoms on the long axis, atoms on the short axis (C2v: on the C2 axis)
    ("benzene (D2h frame, for benzene+)", "D2h", 12, 4, 0),
    ("naphthalene (also naphthalene+)", "D2h", 18, 0, 2),
    ("anthracene", "D2h", 24, 0, 4),
    ("phenanthrene", "C2v", 24, 0, None),
    ("pyrene", "D2h", 26, 4, 2),
    ("tetracene", "D2h", 30, 0, 2),
    ("perylene", "D2h", 32, 0, 0),
    ("pentacene", "D2h", 36, 0, 4),
]

if __name__ == "__main__":
    nap = modes_d2h(18, 0, 2)
    assert nap == {"Ag": 9, "B1g": 4, "B2g": 3, "B3g": 8, "Au": 4, "B1u": 8, "B2u": 8, "B3u": 4}, nap
    assert sum(comb(k, 2) for k in nap.values()) == 141
    print("check: naphthalene 9/4/3/8/4/8/8/4, E = 141 -- passed\n")
    print("| molecule | group | M | n_ts | E (same-irrep pairs) | full deck | H deck | diagonal H deck | H + P25 |")
    print("|---|---|---|---|---|---|---|---|---|")
    for name, grp, n_at, a, b in MOLECULES:
        modes = modes_d2h(n_at, a, b) if grp == "D2h" else modes_c2v(n_at, a)
        assert sum(modes.values()) == 3 * n_at - 6
        M, n, E, full, hdeck, hdiag, hp25 = decks(modes, "Ag" if grp == "D2h" else "A1")
        print(f"| {name} | {grp} | {M} | {n} | {E} | {full} | {hdeck} | {hdiag} | {hp25} |")
    print("\nirreps:")
    for name, grp, n_at, a, b in MOLECULES:
        modes = modes_d2h(n_at, a, b) if grp == "D2h" else modes_c2v(n_at, a)
        print(f"  {name}: " + ", ".join(f"{k} {v}" for k, v in modes.items()))
