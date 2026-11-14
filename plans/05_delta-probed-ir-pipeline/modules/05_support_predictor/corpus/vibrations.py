"""The vibrational arithmetic the label route and the low-mode repair share, defined once (TASKS 216, 14 November 2026).

Until today the same formulas stood in three places: `probes/qc_common.py` (the rigid motions, a curvature as a signed frequency),
`probes/low_mode_patch.py` (the modes, the merged low directions, the patched Hessian) and `analytic_hessians.py` (its own copy of the
rigid motions inside `project_tr`). The repair is moving into the label route, so the arithmetic moves into the production folder with
it, and the probes import it from here.

**The repair.** For mass-weighted directions U (orthonormal columns, inside the vibrational space) the true Hessian's columns C = H U
come from central differences of grid-response gradients along each direction. The repaired mass-weighted Hessian keeps the label
outside span(U) and takes the measured columns inside it:

    H' = Q H Q + C Uᵀ + U Cᵀ − U S Uᵀ,   Q = 1 − U Uᵀ,   S = (UᵀC + CᵀU) / 2,

which is exact when the label's error lies in the rows and columns along U. On D_ac28161d06 the patched lowest mode agreed with the
gradient and energy routes to 0.04 cm⁻¹ (TASKS 49, option 3), and on B_0f06474656 the patched Hessians reproduced a full
finite-difference reference to 0.13 cm⁻¹ (12 November).

This module is numpy only, so importing it costs no pyscf; the measurement that produces C lives beside the SCF in
`analytic_hessians.py`.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from constants import AMU2AU, HARTREE2CM

LABEL_TAGS = ("b3lyp", "wb97x")   # the corpus's two label functionals, in file-name order; analytic_hessians maps each to its xc
LOW_MODE_CM = 20.0          # TASKS 201 step 2: above ≈ 20 cm⁻¹ the measured change stays under 0.5 cm⁻¹; below it reaches 6 cm⁻¹
SUBSPACE_KEEP = 0.3         # a merged direction is kept when its singular value in the union of both functionals' low modes exceeds this
STEP_BOHR = 0.01            # the largest atomic displacement of a step (0.01 and 0.02 agreed within 0.15 cm⁻¹ at the fine grid)
ORTHONORMAL_TOL = 1e-10     # how far UᵀU may stand from the identity before the repair refuses the directions


@dataclass(frozen=True)
class Modes:
    """A Hessian's vibrational modes: signed frequencies (cm⁻¹, ascending) and mass-weighted vectors (3N, 3N−6) orthogonal to the rigid
    motions."""

    omega_cm: np.ndarray
    vectors: np.ndarray


def signed_cm(k_au: np.ndarray | float) -> np.ndarray | float:
    """A mass-weighted curvature (hartree / (bohr² mₑ)) as a signed frequency in cm⁻¹; an imaginary mode comes back negative."""
    return np.sign(k_au) * np.sqrt(np.abs(k_au)) * HARTREE2CM


def mass_weights(masses_amu: np.ndarray) -> np.ndarray:
    """√m per Cartesian coordinate in electron masses (3N,)."""
    return np.sqrt(np.repeat(np.asarray(masses_amu, float) * AMU2AU, 3))


def rigid_basis(masses_amu: np.ndarray, coords_bohr: np.ndarray) -> np.ndarray:
    """An orthonormal basis (3N, 6) of the mass-weighted translations and rotations about the centre of mass."""
    masses = np.asarray(masses_amu, float)
    x = np.asarray(coords_bohr, float)
    n = len(masses)
    r = x - (x * masses[:, None]).sum(0) / masses.sum()
    motions = []
    for k in range(3):
        v = np.zeros((n, 3))
        v[:, k] = 1.0
        motions.append((v * np.sqrt(masses)[:, None]).ravel())
    for k in range(3):
        e = np.zeros(3)
        e[k] = 1.0
        motions.append((np.cross(np.tile(e, (n, 1)), r) * np.sqrt(masses)[:, None]).ravel())
    q, _ = np.linalg.qr(np.array(motions).T)
    return q


def vibrational_modes(H: np.ndarray, masses_amu: np.ndarray, coords_bohr: np.ndarray) -> Modes:
    """The vibrational modes of a Cartesian Hessian (hartree/bohr²) in the space orthogonal to the mass-weighted rigid motions."""
    sm = mass_weights(masses_amu)
    rigid = rigid_basis(masses_amu, coords_bohr)
    full, _ = np.linalg.qr(np.hstack([rigid, np.eye(len(sm))]))
    basis = full[:, rigid.shape[1]:]
    Hmw = 0.5 * (H + H.T) / np.outer(sm, sm)
    w, Y = np.linalg.eigh(basis.T @ Hmw @ basis)
    return Modes(np.asarray(signed_cm(w), float), basis @ Y)


def low_mode_directions(mode_sets: list[Modes], below_cm: float = LOW_MODE_CM) -> np.ndarray:
    """One orthonormal set (3N, k) spanning every mode below below_cm in any of the given Hessians; (3N, 0) when there is none."""
    stacked = np.hstack([m.vectors[:, np.abs(m.omega_cm) < below_cm] for m in mode_sets])
    if stacked.shape[1] == 0:
        return stacked
    U, s, _ = np.linalg.svd(stacked, full_matrices=False)
    return U[:, s > SUBSPACE_KEEP]


def displacement(direction: np.ndarray, masses_amu: np.ndarray, step_bohr: float = STEP_BOHR) -> tuple[np.ndarray, float]:
    """The Cartesian step (N, 3) bohr whose largest atomic displacement is step_bohr along a mass-weighted direction, and its length q
    in the mass-weighted coordinate (bohr mₑ^½)."""
    d = (direction / mass_weights(masses_amu)).reshape(-1, 3)
    q = step_bohr / float(np.linalg.norm(d, axis=1).max())
    return q * d, q


def column(gradient_plus: np.ndarray, gradient_minus: np.ndarray, q: float, masses_amu: np.ndarray) -> np.ndarray:
    """The mass-weighted Hessian column H u from central differences of Cartesian gradients (hartree/bohr) at ± q along u."""
    return (np.ravel(gradient_plus) - np.ravel(gradient_minus)) / mass_weights(masses_amu) / (2 * q)


def patched_hessian(H: np.ndarray, masses_amu: np.ndarray, U: np.ndarray, C: np.ndarray) -> np.ndarray:
    """The Cartesian Hessian with its mass-weighted rows and columns along U replaced by the measured columns C (both (3N, k)); raises
    when U is not orthonormal or the shapes differ."""
    if U.shape != C.shape:
        raise ValueError(f"directions {U.shape} and columns {C.shape} differ in shape")
    if U.shape[1] and np.abs(U.T @ U - np.eye(U.shape[1])).max() > ORTHONORMAL_TOL:
        raise ValueError("the directions are not orthonormal")
    sm = mass_weights(masses_amu)
    Hmw = 0.5 * (H + H.T) / np.outer(sm, sm)
    Q = np.eye(len(sm)) - U @ U.T
    S = 0.5 * (U.T @ C + C.T @ U)
    patched = Q @ Hmw @ Q + C @ U.T + U @ C.T - U @ S @ U.T
    return 0.5 * (patched + patched.T) * np.outer(sm, sm)
