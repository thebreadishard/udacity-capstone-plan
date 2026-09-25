"""Reduced (dimensionless) normal-coordinate displacements, with a harmonic self-check — own software, 25 September 2026.

Convention (the anchor's, `m1_frozen_spaces.py`; `dpir.qff`): for mode k with mass-weighted orthonormal eigenvector L_k (3N), frequency ω_k in
atomic units (E_h, ħ = 1) and Minv = 1/sqrt(mass in m_e) per Cartesian component,

    x(q) = x0 + Minv ⊙ L_k · q / sqrt(ω_k),          E_harm(q) = ½ ω_k q²   (so q = 1 costs ω/2 ≈ 0.002 E_h for a 1000 cm⁻¹ mode).

Why this module exists: on 25 September 2026 the cation price probe (`l3_ulno_price.py`) and its neutral twin (`l2_lno_price.py`) divided by ω (the
square root of the mass-weighted Hessian's eigenvalue ω²) instead of by sqrt(ω): a displacement 15× too large, +0.27 E_h, a spurious UHF state
with ⟨S²⟩ 1.14, and 56 minutes of ULNO-CCSD(T) on a point that meant nothing. `harmonic_check` makes that class of mistake impossible: the
displacement is rejected unless ½ dᵀ H d equals ½ ω q² to within a per cent, which is exact for a harmonic surface along an eigenvector."""
from __future__ import annotations

import numpy as np

HARTREE2CM = 219474.6313632


def omega_from_eigenvalue(w: float) -> float:
    """ω (au) from an eigenvalue of the mass-weighted Hessian (au); negative eigenvalues give the magnitude."""
    return float(np.sqrt(abs(w)))


def reduced_displacement(coords0: np.ndarray, L_k: np.ndarray, omega_au: float, Minv: np.ndarray, q: float) -> np.ndarray:
    """Cartesian geometry (N × 3, bohr) displaced by q dimensionless units along mode k."""
    return np.asarray(coords0) + ((np.asarray(L_k) * q / np.sqrt(omega_au)) * np.asarray(Minv)).reshape(-1, 3)


def harmonic_check(H_cart: np.ndarray, coords0: np.ndarray, x: np.ndarray, omega_au: float, q: float, rtol: float = 0.01) -> float:
    """½ dᵀ H d (d = x − x0, Cartesian, H in E_h/bohr²) must equal ½ ω q² to within rtol; returns the ratio and raises otherwise."""
    d = (np.asarray(x) - np.asarray(coords0)).reshape(-1)
    e_harm = 0.5 * float(d @ np.asarray(H_cart) @ d); e_expected = 0.5 * omega_au * q * q
    ratio = e_harm / e_expected if e_expected else float("inf")
    if not (1 - rtol <= ratio <= 1 + rtol):
        raise ValueError(f"reduced displacement is not in the convention: ½dᵀHd = {e_harm:.3e} E_h against ½ωq² = {e_expected:.3e} (ratio {ratio:.3g}); "
                         f"a ratio near 1/ω ({1 / omega_au:.0f}) means the displacement was divided by ω instead of sqrt(ω)")
    return ratio
