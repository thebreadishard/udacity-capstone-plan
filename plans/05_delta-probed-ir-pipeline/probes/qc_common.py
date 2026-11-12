"""Constants, the translation/rotation projection, the translation residual and an atomic text writer — numpy only, so the CC Hessian probe (pyscf), the
composite tools (any python, psi4's in WSL) and the deck rehearsal (module 05's python) import one implementation instead of keeping copies."""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

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


def signed_cm(k_au: float) -> float:
    """A mass-weighted curvature (hartree / (bohr^2 me)) as a signed frequency in cm-1."""
    return float(np.sign(k_au) * np.sqrt(abs(k_au)) * HARTREE2CM)


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
