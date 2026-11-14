"""The shared vibrational arithmetic (TASKS 216, 14 November 2026): `modules/05_support_predictor/corpus/vibrations.py`.

The formulas moved here out of `probes/qc_common.py` and `probes/low_mode_patch.py` when the low-mode repair moved into the label
route. These tests pin the properties the repair rests on, above all the one its docstring claims: when the label's error lies in the
rows and columns along the measured directions, the repair returns the true Hessian exactly.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "modules" / "05_support_predictor" / "corpus"))
import vibrations as V

RNG = np.random.default_rng(20261114)
ATOMS = 4
MASSES = np.array([12.0, 12.0, 1.00782503207, 1.00782503207])


def random_symmetric(n: int) -> np.ndarray:
    a = RNG.normal(size=(n, n))
    return 0.5 * (a + a.T)


def orthonormal_columns(n: int, k: int) -> np.ndarray:
    q, _ = np.linalg.qr(RNG.normal(size=(n, k)))
    return q[:, :k]


def cartesian(Hmw: np.ndarray, masses: np.ndarray) -> np.ndarray:
    """A mass-weighted Hessian back in Cartesian units, the inverse of what the repair does on the way in."""
    sm = V.mass_weights(masses)
    return Hmw * np.outer(sm, sm)


def test_a_signed_frequency_keeps_the_sign_of_the_curvature() -> None:
    assert V.signed_cm(0.0) == 0.0
    assert V.signed_cm(1e-6) > 0 and V.signed_cm(-1e-6) < 0
    assert V.signed_cm(-4e-6) == pytest.approx(-V.signed_cm(4e-6))
    both = V.signed_cm(np.array([9e-6, -9e-6]))
    assert both[0] == pytest.approx(-both[1]) and both[0] > 0


def test_the_rigid_basis_spans_six_motions_and_is_orthonormal() -> None:
    coords = RNG.normal(size=(ATOMS, 3))
    q = V.rigid_basis(MASSES, coords)
    assert q.shape == (3 * ATOMS, 6)
    assert np.abs(q.T @ q - np.eye(6)).max() < 1e-12


def test_the_modes_leave_the_rigid_motions_out() -> None:
    coords = RNG.normal(size=(ATOMS, 3))
    H = cartesian(random_symmetric(3 * ATOMS), MASSES)
    modes = V.vibrational_modes(H, MASSES, coords)
    assert modes.omega_cm.shape == (3 * ATOMS - 6,) and modes.vectors.shape == (3 * ATOMS, 3 * ATOMS - 6)
    rigid = V.rigid_basis(MASSES, coords)
    assert np.abs(rigid.T @ modes.vectors).max() < 1e-10          # every mode is orthogonal to every rigid motion
    assert np.all(np.diff(modes.omega_cm) >= 0)                   # ascending, as the dataclass promises


def test_the_repair_returns_the_true_hessian_when_the_error_lies_along_the_directions() -> None:
    n = 3 * ATOMS
    true_mw = random_symmetric(n)
    U = orthonormal_columns(n, 2)
    X = RNG.normal(size=(n, 2))
    error = U @ X.T + X @ U.T                                     # an error in the rows and columns along U, and nowhere else
    label = cartesian(true_mw + error, MASSES)
    columns = true_mw @ U                                         # what the displaced gradients measure
    repaired = V.patched_hessian(label, MASSES, U, columns)
    assert np.abs(repaired - cartesian(true_mw, MASSES)).max() < 1e-10


def test_the_repair_leaves_a_hessian_alone_when_the_columns_are_its_own() -> None:
    n = 3 * ATOMS
    true_mw = random_symmetric(n)
    U = orthonormal_columns(n, 1)
    repaired = V.patched_hessian(cartesian(true_mw, MASSES), MASSES, U, true_mw @ U)
    assert np.abs(repaired - cartesian(true_mw, MASSES)).max() < 1e-10


def test_the_repair_refuses_directions_that_are_not_orthonormal_or_do_not_match() -> None:
    n = 3 * ATOMS
    H = cartesian(random_symmetric(n), MASSES)
    U = orthonormal_columns(n, 2)
    with pytest.raises(ValueError, match="differ in shape"):
        V.patched_hessian(H, MASSES, U, U[:, :1])
    with pytest.raises(ValueError, match="orthonormal"):
        V.patched_hessian(H, MASSES, 2 * U, 2 * U)


def test_a_step_moves_one_atom_by_the_asked_distance() -> None:
    n = 3 * ATOMS
    U = orthonormal_columns(n, 1)
    step, q = V.displacement(U[:, 0], MASSES, step_bohr=0.01)
    assert step.shape == (ATOMS, 3)
    assert np.linalg.norm(step, axis=1).max() == pytest.approx(0.01)
    assert q > 0


def test_the_column_is_the_central_difference_of_the_gradients() -> None:
    n = 3 * ATOMS
    true_mw = random_symmetric(n)
    U = orthonormal_columns(n, 1)
    u, q = U[:, 0], 0.37
    sm = V.mass_weights(MASSES)
    # a quadratic energy's Cartesian gradient at ± q along the mass-weighted direction u
    gradients = [(true_mw @ (sign * q * u)) * sm for sign in (1, -1)]
    measured = V.column(gradients[0], gradients[1], q, MASSES)
    assert np.abs(measured - true_mw @ u).max() < 1e-12


def test_merged_directions_count_the_subspace_once() -> None:
    n = 3 * ATOMS
    shared = orthonormal_columns(n, 3)
    low = V.Modes(np.array([5.0, 9.0, 40.0]), shared)
    other = V.Modes(np.array([7.0, 300.0, 400.0]), shared[:, [0, 1, 2]])
    merged = V.low_mode_directions([low, other], below_cm=20.0)
    assert merged.shape == (n, 2)                                 # modes at 5 and 9 from the first set, 7 is the same vector as 5's
    assert np.abs(merged.T @ merged - np.eye(2)).max() < 1e-12
    assert V.low_mode_directions([V.Modes(np.array([40.0]), shared[:, :1])], below_cm=20.0).shape == (n, 0)


def test_the_label_tags_are_the_label_routes_own() -> None:
    pytest.importorskip("pyscf")
    import analytic_hessians as AH
    assert tuple(tag for tag, _xc in AH.FUNCTIONALS) == V.LABEL_TAGS
