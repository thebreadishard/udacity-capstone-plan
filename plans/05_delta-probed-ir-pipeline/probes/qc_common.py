"""Constants, the translation/rotation projection, the translation residual and an atomic text writer — numpy only, so the CC Hessian probe (pyscf), the
composite tools (any python, psi4's in WSL) and the deck rehearsal (module 05's python) import one implementation instead of keeping copies."""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

import numpy as np

# the constants, the rigid motions and the signed frequency live beside the label route that writes the Hessians (TASKS 216, 14 Nov 2026)
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "modules" / "05_support_predictor" / "corpus"))
from constants import AMU2AU, HARTREE2CM  # noqa: I001,F401  the path line above blocks sorting; HARTREE2CM is re-exported here
from vibrations import rigid_basis, signed_cm
CORE_ORBITALS = {"H": 0, "He": 0, "Li": 1, "Be": 1, "B": 1, "C": 1, "N": 1, "O": 1, "F": 1, "Ne": 1,     # frozen core per element
                 "Na": 5, "Mg": 5, "Al": 5, "Si": 5, "P": 5, "S": 5, "Cl": 5, "Ar": 5}


def project_tr(H: np.ndarray, masses: np.ndarray, x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(H with the six translations and rotations projected out by the mass-weighted projector, back in Cartesian units; the mass-weighted
    H before the projection). x in bohr, masses in amu."""
    n = len(masses)
    sm = np.sqrt(np.repeat(masses * AMU2AU, 3))
    q = rigid_basis(masses, x)
    P = np.eye(3 * n) - q @ q.T
    Hmw = H / np.outer(sm, sm)
    return (P @ Hmw @ P) * np.outer(sm, sm), Hmw


def translation_residual(H: np.ndarray, masses_amu: np.ndarray) -> tuple[float, list[float]]:
    """max|H t| over the three unit translations and their curvatures as signed frequencies (cm-1); both 0 for a translation-invariant
    energy's exact Hessian."""
    H = 0.5 * (H + H.T)
    worst, freqs = 0.0, []
    for ax in range(3):
        t = np.zeros(H.shape[0])
        t[ax::3] = 1.0
        worst = max(worst, float(np.abs(H @ t).max()))
        freqs.append(signed_cm(t @ H @ t / (masses_amu.sum() * AMU2AU)))
    return worst, freqs


def write_atomic(path: Path, text: str) -> None:
    """Text through a temp file in the same folder, moved over the target."""
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    os.replace(tmp, path)
