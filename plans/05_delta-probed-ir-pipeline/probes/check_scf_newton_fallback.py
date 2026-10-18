"""Check of s1_anharmonic_level's second-order SCF fallback (18 Oct 2026) — runs in WSL's qc05 env (pyscf): on water at B3LYP/6-31G*
(grid 75,302), the energy and gradient with DIIS cut to 3 cycles (so that the fallback runs) equal those of a normal DIIS run: energy
to 1e-10 E_h, gradient to 1e-7 E_h/bohr — ten times below the optimiser's final GTOL (1e-6); the SCF's own orbital-gradient threshold
(1e-8) moves the nuclear gradient by about that much.

    python check_scf_newton_fallback.py      → prints the differences and PASS or FAIL
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from s1_anharmonic_level import pyscf_energy_and_gradient  # noqa: E402

SYM = ["O", "H", "H"]
X = np.array([[0.0, 0.0, 0.2217], [0.0, 1.4309, -0.8867], [0.0, -1.4309, -0.8867]])
TOL_E, TOL_G = 1e-10, 1e-7


def main() -> int:
    e_ref, g_ref = pyscf_energy_and_gradient(SYM, "6-31g*", "75,302", 2)(X)
    e_fb, g_fb = pyscf_energy_and_gradient(SYM, "6-31g*", "75,302", 2, diis_cycles=3)(X)
    de, dg = abs(e_fb - e_ref), float(np.abs(g_fb - g_ref).max())
    ok = de <= TOL_E and dg <= TOL_G
    print(f"|ΔE| {de:.1e} E_h, max |Δg| {dg:.1e} E_h/bohr -> {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
