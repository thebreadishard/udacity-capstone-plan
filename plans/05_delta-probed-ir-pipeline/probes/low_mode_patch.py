"""Label Hessians repaired along their low modes with grid-response curvature (TASKS 201 step 3; the user, 12 Nov 2026: problems are solved
at the source, not swept under the rug).

pyscf's CPU DFT Hessian leaves out the derivative of the quadrature weights (software ledger 56). TASKS 201 step 2 measured what that does
to vibrations: B_0f06474656's lowest B3LYP mode moves from 9.5 to 15.7 cm⁻¹ against a finite-difference Hessian of grid-response gradients,
while every other mode of it and of benzene moves less than 0.43 cm⁻¹. The error lives in the low modes, so only those are repaired.

For a set of mass-weighted directions U (orthonormal columns, inside the vibrational space) the true Hessian's columns C = H U come from
central differences of grid-response gradients along each direction. The repaired mass-weighted Hessian keeps the label outside span(U)
and takes the measured columns inside it:

    H' = Q H Q + C Uᵀ + U Cᵀ − U S Uᵀ,   Q = 1 − U Uᵀ,   S = (UᵀC + CᵀU) / 2,

which is exact when the label's error lies in the rows and columns along U (TASKS 49's option 3: the patched lowest mode of
D_ac28161d06 agreed with the gradient and energy routes to 0.04 cm⁻¹). The directions are the label modes below LOW_MODE_CM in either
functional, merged into one orthonormal set, so both functionals are repaired along the same directions.

This module is numpy only (the arithmetic, and `select` with its command line); probes/low_mode_patch_run.py computes the gradients.

    python probes/low_mode_patch.py <corpus molecules dir> <ids out> [--below 20]
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from qc_common import AMU2AU, rigid_basis, signed_cm, write_atomic

LOW_MODE_CM = 20.0          # TASKS 201 step 2: above ≈ 20 cm⁻¹ the measured change stays under 0.5 cm⁻¹; below it reaches 6 cm⁻¹
SUBSPACE_KEEP = 0.3         # a merged direction is kept when its singular value in the union of both functionals' low modes exceeds this
LABEL_TAGS = ("b3lyp", "wb97x")   # the two label functionals, the corpus files' tags
STEP_BOHR = 0.01            # the largest atomic displacement of a step, as option 3 (0.01 and 0.02 agreed within 0.15 cm⁻¹ at the fine grid)


@dataclass(frozen=True)
class Modes:
    """A Hessian's vibrational modes: signed frequencies (cm⁻¹, ascending) and mass-weighted vectors (3N, 3N−6) orthogonal to the rigid
    motions."""

    omega_cm: np.ndarray
    vectors: np.ndarray


def mass_weights(masses_amu: np.ndarray) -> np.ndarray:
    """√m per Cartesian coordinate in electron masses (3N,)."""
    return np.sqrt(np.repeat(np.asarray(masses_amu, float) * AMU2AU, 3))


def vibrational_modes(H: np.ndarray, masses_amu: np.ndarray, coords_bohr: np.ndarray) -> Modes:
    """The vibrational modes of a Cartesian Hessian (hartree/bohr²) in the space orthogonal to the mass-weighted rigid motions."""
    sm = mass_weights(masses_amu)
    rigid = rigid_basis(np.asarray(masses_amu, float), np.asarray(coords_bohr, float))
    full, _ = np.linalg.qr(np.hstack([rigid, np.eye(len(sm))]))
    basis = full[:, rigid.shape[1]:]
    Hmw = 0.5 * (H + H.T) / np.outer(sm, sm)
    w, Y = np.linalg.eigh(basis.T @ Hmw @ basis)
    return Modes(np.array([signed_cm(k) for k in w]), basis @ Y)


def low_mode_directions(mode_sets: list[Modes], below_cm: float = LOW_MODE_CM) -> np.ndarray:
    """One orthonormal set (3N, k) spanning every mode below below_cm in any of the given Hessians; (3N, 0) when there is none."""
    low = [m.vectors[:, np.abs(m.omega_cm) < below_cm] for m in mode_sets]
    stacked = np.hstack(low)
    if stacked.shape[1] == 0:
        return stacked
    U, s, _ = np.linalg.svd(stacked, full_matrices=False)
    return U[:, s > SUBSPACE_KEEP]


def displacement(direction: np.ndarray, masses_amu: np.ndarray, step_bohr: float = STEP_BOHR) -> tuple[np.ndarray, float]:
    """The Cartesian step (N, 3) bohr whose largest atomic displacement is step_bohr along a mass-weighted direction, and its length q
    in the mass-weighted coordinate (bohr me^1/2)."""
    d = (direction / mass_weights(masses_amu)).reshape(-1, 3)
    q = step_bohr / float(np.linalg.norm(d, axis=1).max())
    return q * d, q


def column(gradient_plus: np.ndarray, gradient_minus: np.ndarray, q: float, masses_amu: np.ndarray) -> np.ndarray:
    """The mass-weighted Hessian column H u from central differences of Cartesian gradients (hartree/bohr) at ± q along u."""
    return (np.ravel(gradient_plus) - np.ravel(gradient_minus)) / mass_weights(masses_amu) / (2 * q)


def patched_hessian(H: np.ndarray, masses_amu: np.ndarray, U: np.ndarray, C: np.ndarray) -> np.ndarray:
    """The Cartesian Hessian with its mass-weighted rows and columns along U replaced by the measured columns C (both (3N, k)); raises when
    U is not orthonormal or the shapes differ."""
    if U.shape != C.shape:
        raise ValueError(f"directions {U.shape} and columns {C.shape} differ in shape")
    if U.shape[1] and np.abs(U.T @ U - np.eye(U.shape[1])).max() > 1e-10:
        raise ValueError("the directions are not orthonormal")
    sm = mass_weights(masses_amu)
    Hmw = 0.5 * (H + H.T) / np.outer(sm, sm)
    Q = np.eye(len(sm)) - U @ U.T
    S = 0.5 * (U.T @ C + C.T @ U)
    patched = Q @ Hmw @ Q + C @ U.T + U @ C.T - U @ S @ U.T
    return 0.5 * (patched + patched.T) * np.outer(sm, sm)
def read_label(molecule_dir: Path) -> tuple[dict, dict[str, np.ndarray]]:
    """A corpus folder's geometry.json and its two analytic label Hessians (H_raw, hartree/bohr²) by functional tag."""
    geometry = json.loads((molecule_dir / "geometry.json").read_text(encoding="utf-8"))
    hessians = {}
    for tag in LABEL_TAGS:
        with np.load(molecule_dir / f"hessian_{tag}_analytic.npz") as z:
            hessians[tag] = np.asarray(z["H_raw"], float)
    return geometry, hessians


def label_directions(molecule_dir: Path, below_cm: float = LOW_MODE_CM) -> np.ndarray:
    """The merged low-mode directions (3N, k) of one corpus folder's two analytic labels."""
    geometry, hessians = read_label(molecule_dir)
    masses, coords = np.asarray(geometry["masses_amu"], float), np.asarray(geometry["coords_bohr"], float)
    return low_mode_directions([vibrational_modes(H, masses, coords) for H in hessians.values()], below_cm)


def select(molecules: Path, below_cm: float = LOW_MODE_CM) -> dict[str, int]:
    """Every corpus folder with both analytic labels and at least one low-mode direction, with its count."""
    dirs = sorted(d for d in molecules.iterdir() if all((d / f"hessian_{t}_analytic.npz").is_file() for t in LABEL_TAGS))
    counts = {d.name: int(label_directions(d, below_cm).shape[1]) for d in dirs}
    return {i: n for i, n in counts.items() if n}


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description="Write the ids of the corpus folders whose labels have modes below the threshold.")
    ap.add_argument("molecules", type=Path)
    ap.add_argument("ids_out", type=Path)
    ap.add_argument("--below", type=float, default=LOW_MODE_CM)
    a = ap.parse_args(argv)
    chosen = select(a.molecules, a.below)
    lines = [f"# low_mode_patch.py select: folders with label modes below {a.below} cm⁻¹ (id, directions)"]
    write_atomic(a.ids_out, "\n".join([*lines, *(f"{i} {n}" for i, n in chosen.items())]) + "\n")
    print(f"{len(chosen)} molecules, {sum(chosen.values())} directions below {a.below} cm⁻¹ → {a.ids_out}")


if __name__ == "__main__":
    main()
