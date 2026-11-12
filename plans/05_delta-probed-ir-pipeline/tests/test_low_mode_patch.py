"""probes/low_mode_patch.py (TASKS 201 step 3): the patch recovers a Hessian exactly when the label's error lies along the directions, and
leaves it untouched outside them; the low-mode directions of two functionals merge into one orthonormal set; a displacement's largest
atomic step and the central-difference column are exact on a quadratic energy; bad inputs are refused."""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes"))
import low_mode_patch as L

MASSES = np.array([12.0, 12.0, 1.008, 1.008, 14.003])
RNG = np.random.default_rng(7)
COORDS = RNG.normal(scale=2.0, size=(5, 3))


def _hessian(seed=1):
    A = np.random.default_rng(seed).normal(size=(15, 15))
    return 0.02 * (A @ A.T) / 15


def test_vibrational_modes_are_orthogonal_to_the_rigid_motions():
    m = L.vibrational_modes(_hessian(), MASSES, COORDS)
    assert m.vectors.shape == (15, 9) and np.all(np.diff(m.omega_cm) >= 0)
    rigid = L.rigid_basis(MASSES, COORDS)
    np.testing.assert_allclose(rigid.T @ m.vectors, 0.0, atol=1e-10)


def test_the_patch_recovers_the_true_hessian_when_the_error_lies_along_the_directions():
    H_true = _hessian(1)
    sm = L.mass_weights(MASSES)
    U = L.vibrational_modes(H_true, MASSES, COORDS).vectors[:, :2]
    A = np.random.default_rng(3).normal(scale=1e-3, size=(15, 2))
    E_mw = U @ A.T + A @ U.T
    H_label = H_true + E_mw * np.outer(sm, sm)
    C = (H_true / np.outer(sm, sm)) @ U
    np.testing.assert_allclose(L.patched_hessian(H_label, MASSES, U, C), H_true, atol=1e-12)


def test_the_patch_leaves_the_label_alone_outside_the_directions():
    H = _hessian(2)
    sm = L.mass_weights(MASSES)
    modes = L.vibrational_modes(H, MASSES, COORDS)
    U = modes.vectors[:, :1]
    C = (H / np.outer(sm, sm)) @ U + 1e-3 * U          # a measured curvature 1e-3 above the label's along U
    P = L.patched_hessian(H, MASSES, U, C)
    rest = modes.vectors[:, 1:]
    Hmw, Pmw = H / np.outer(sm, sm), P / np.outer(sm, sm)
    np.testing.assert_allclose(rest.T @ Pmw @ rest, rest.T @ Hmw @ rest, atol=1e-12)
    assert float(U[:, 0] @ Pmw @ U[:, 0]) == pytest.approx(float(U[:, 0] @ Hmw @ U[:, 0]) + 1e-3, rel=1e-9)


def test_low_mode_directions_merge_the_functionals():
    H1 = _hessian(4)
    modes1 = L.vibrational_modes(H1, MASSES, COORDS)
    threshold = float(abs(modes1.omega_cm[1])) + 1e-6           # the two lowest modes of the first Hessian
    U = L.low_mode_directions([modes1, modes1], below_cm=threshold)
    assert U.shape == (15, 2)
    np.testing.assert_allclose(U.T @ U, np.eye(2), atol=1e-12)
    assert L.low_mode_directions([modes1], below_cm=0.0).shape == (15, 0)


def test_displacement_and_column_are_exact_on_a_quadratic_energy():
    H = _hessian(5)
    u = L.vibrational_modes(H, MASSES, COORDS).vectors[:, 0]
    step, q = L.displacement(u, MASSES, step_bohr=0.01)
    assert float(np.linalg.norm(step, axis=1).max()) == pytest.approx(0.01)
    sm = L.mass_weights(MASSES)
    np.testing.assert_allclose(step.ravel() * sm, q * u, atol=1e-14)
    g = lambda x: H @ x.ravel()  # noqa: E731  the gradient of a quadratic energy
    np.testing.assert_allclose(L.column(g(step), g(-step), q, MASSES), (H / np.outer(sm, sm)) @ u, atol=1e-12)


def test_bad_inputs_are_refused():
    H = _hessian(6)
    U = L.vibrational_modes(H, MASSES, COORDS).vectors[:, :2]
    with pytest.raises(ValueError, match="differ in shape"):
        L.patched_hessian(H, MASSES, U, U[:, :1])
    with pytest.raises(ValueError, match="orthonormal"):
        L.patched_hessian(H, MASSES, 2 * U, U)
