"""TASKS 127's first check (26 Oct 2026): does the coupled-cluster anchor want shorter C–H bonds than the B3LYP/6-31G* geometry it was taken at?
The carried benzene anchor stores the CCSD(T)/cc-pVTZ gradient at that geometry. Per C–H bond: the force on the hydrogen along the bond (negative =
pulling it towards its carbon, i.e. CC prefers a shorter bond) and, from the anchor's own Hessian, the bond length change that force implies to
first order, Δr = F / k with k the curvature of the energy along that bond (hydrogen displaced, rest fixed).

    python probes/cc_ch_bond_force.py      → one line per C–H bond on stdout
"""
from __future__ import annotations

import sys

import numpy as np
from e8_symmetry import BOHR

ANCHOR = "probes/results_m1/e8_benzene_ccpvtz_oop_2026-10-03/hessian_ccsd_t.npz"
SYMBOLS = ["C"] * 6 + ["H"] * 6           # the corpus geometry's atom order (A_8448043181), which the anchor shares
CH_MAX_BOHR = 2.3                          # a C–H bond is shorter than this (≈ 1.2 Å)


def bonds(coords: np.ndarray) -> list[tuple[int, int]]:
    return [(c, h) for h, sh in enumerate(SYMBOLS) if sh == "H" for c, sc in enumerate(SYMBOLS)
            if sc == "C" and np.linalg.norm(coords[h] - coords[c]) < CH_MAX_BOHR]


def main() -> int:
    from pathlib import Path
    z = np.load(Path(__file__).resolve().parents[1] / ANCHOR)
    coords, grad, H = z["coords_bohr"], z["gradient"], z["H_raw"]
    out = []
    for c, h in bonds(coords):
        u = (coords[h] - coords[c]) / np.linalg.norm(coords[h] - coords[c])
        force = float(-grad[h] @ u)                                       # E_h/bohr along C→H
        k = float(u @ H[3 * h:3 * h + 3, 3 * h:3 * h + 3] @ u)            # E_h/bohr²
        out.append((c, h, np.linalg.norm(coords[h] - coords[c]) * BOHR, force, force / k * BOHR))
        print(f"C{c}–H{h}: r = {out[-1][2]:.4f} Å, force along C→H {force:+.5f} E_h/bohr, implied Δr {out[-1][4]:+.4f} Å")
    mean_dr = float(np.mean([o[4] for o in out]))
    print(f"mean implied Δr {mean_dr:+.4f} Å ({'shorter' if mean_dr < 0 else 'longer'} C–H bonds at the CC level, to first order)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
