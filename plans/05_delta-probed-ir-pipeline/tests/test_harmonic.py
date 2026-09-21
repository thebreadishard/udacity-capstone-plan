"""Harmonic analysis on a constructed Hessian with known frequencies (no electronic-structure code)."""

import numpy as np
import pytest

from dpir.qff import HARTREE_CM, degenerate_groups, harmonic, translation_rotation_projector


def external_vectors(geom, m):
    """The six mass-weighted translation and rotation vectors, written out independently of the package:
    translation t_a = sqrt(m_k) e_a; infinitesimal rotation r_a = sqrt(m_k) (e_a × (x_k − x_com))."""
    x = geom.reshape(-1, 3)
    xc = x - (m[:, None] * x).sum(0) / m.sum()
    vecs = []
    for a in range(3):
        v = np.zeros_like(x)
        v[:, a] = np.sqrt(m)
        vecs.append(v.ravel())
    e = np.eye(3)
    for a in range(3):
        v = np.array([np.sqrt(mk) * np.cross(e[a], xk) for mk, xk in zip(m, xc, strict=True)])
        vecs.append(v.ravel())
    return np.array(vecs).T  # (3N, 6)


def vibrational_basis(geom, m, rng):
    """A random orthonormal basis of the vibrational subspace: the orthogonal complement of the six external vectors."""
    T = external_vectors(geom, m)
    Qt, _ = np.linalg.qr(T)
    R = rng.normal(size=(len(geom), len(geom)))
    R -= Qt @ (Qt.T @ R)  # project the external directions out
    U, s, _ = np.linalg.svd(R)
    return U[:, : len(geom) - 6]


def test_projector_annihilates_the_external_vectors(model_molecule):
    symbols, geom, m, rng = model_molecule
    P = translation_rotation_projector(geom, m)
    T = external_vectors(geom, m)
    np.testing.assert_allclose(P @ T, 0.0, atol=1e-12)
    np.testing.assert_allclose(P @ P, P, atol=1e-12)
    assert round(np.trace(P)) == 3 * len(symbols) - 6


def test_linear_molecule_is_refused():
    m = np.array([12.0, 15.99, 15.99]) * 1822.888
    geom = np.array([0, 0, 0, 0, 0, 2.2, 0, 0, -2.2], float)  # CO₂-like, collinear
    with pytest.raises(NotImplementedError):
        translation_rotation_projector(geom, m)


def hessian_from_modes(q, omega, m):
    """Cartesian Hessian whose mass-weighted form has modes q and eigenvalues ω² (translation/rotation-clean)."""
    Msqrt = np.repeat(np.sqrt(m), 3)
    F = q @ np.diag(omega**2) @ q.T
    return Msqrt[:, None] * F * Msqrt[None, :]


def test_recovers_frequencies_and_modes(model_molecule):
    symbols, geom, m, rng = model_molecule
    omega = np.array([0.004, 0.006, 0.006, 0.009, 0.012, 0.015])  # E_h, one exactly degenerate pair
    q = vibrational_basis(geom, m, rng)
    H = hessian_from_modes(q, omega, m)
    h = harmonic(H, symbols, geom)
    assert h.omega.shape == (6,)
    np.testing.assert_allclose(h.omega, omega, rtol=1e-9)
    np.testing.assert_allclose(h.q.T @ h.q, np.eye(6), atol=1e-12)
    # A is the reduced-coordinate displacement: Aᵀ H A = diag(ω)
    np.testing.assert_allclose(h.A.T @ H @ h.A, np.diag(omega), atol=1e-12)
    assert np.isclose(h.omega_cm[0], 0.004 * HARTREE_CM)


def test_translations_and_rotations_are_projected_out(model_molecule):
    symbols, geom, m, rng = model_molecule
    omega = np.array([0.004, 0.006, 0.006, 0.009, 0.012, 0.015])
    q = vibrational_basis(geom, m, rng)
    H = hessian_from_modes(q, omega, m)
    # contaminate the Hessian with a translation/rotation component; the analysis must not see it
    P = translation_rotation_projector(geom, m)
    lam, V = np.linalg.eigh(P)
    Vtr = V[:, lam < 0.5]
    Msqrt = np.repeat(np.sqrt(m), 3)
    H_dirty = H + Msqrt[:, None] * (Vtr @ (0.01 * np.eye(6)) @ Vtr.T) * Msqrt[None, :]
    np.testing.assert_allclose(harmonic(H_dirty, symbols, geom).omega, omega, rtol=1e-9)


def test_degenerate_groups():
    w = np.array([400.0, 612.0, 612.2, 990.0, 1011.0, 1011.3, 1011.6])
    assert degenerate_groups(w) == [[0], [1, 2], [3], [4, 5, 6]]
    assert degenerate_groups(w, tol_cm=0.1) == [[i] for i in range(7)]
