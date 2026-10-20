"""Constants and the translation/rotation projection shared by the anchor pipeline — numpy only, so the CC Hessian probe (pyscf), the
composite tools (any python, psi4's in WSL) and the deck rehearsal (module 05's python) import one implementation instead of keeping copies."""
from __future__ import annotations

import numpy as np

AMU2AU = 1822.888486209          # electron masses per atomic mass unit
HARTREE2CM = 219474.6313705      # cm⁻¹ per hartree
CORE_ORBITALS = {"H": 0, "He": 0, "Li": 1, "Be": 1, "B": 1, "C": 1, "N": 1, "O": 1, "F": 1, "Ne": 1,     # frozen core per element
                 "Na": 5, "Mg": 5, "Al": 5, "Si": 5, "P": 5, "S": 5, "Cl": 5, "Ar": 5}


def project_tr(H: np.ndarray, masses: np.ndarray, x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(H with the six translations and rotations projected out by the mass-weighted projector, back in Cartesian units; the mass-weighted
    H before the projection). x in bohr, masses in amu."""
    n = len(masses)
    sm = np.sqrt(np.repeat(masses * AMU2AU, 3))
    r = x - (x * masses[:, None]).sum(0) / masses.sum()
    D = []
    for k in range(3):
        v = np.zeros((n, 3))
        v[:, k] = 1.0
        D.append((v * np.sqrt(masses)[:, None]).ravel())
    for k in range(3):
        e = np.zeros(3)
        e[k] = 1.0
        v = np.cross(np.tile(e, (n, 1)), r)
        D.append((v * np.sqrt(masses)[:, None]).ravel())
    q, _ = np.linalg.qr(np.array(D).T)
    P = np.eye(3 * n) - q @ q.T
    Hmw = H / np.outer(sm, sm)
    return (P @ Hmw @ P) * np.outer(sm, sm), Hmw
