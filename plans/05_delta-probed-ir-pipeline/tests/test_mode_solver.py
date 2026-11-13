"""src/dpir/mode_solver.py (TASKS 209 stage 1): the one-mode block reproduces perturbation theory where VPT2 is sound, matches an
independent grid solution of the same Hamiltonian where it is not (the noise principle's second route), and refuses a potential that
falls away at large |q|."""
import math
import sys
from pathlib import Path

import numpy as np
import pytest
from scipy.linalg import eigh_tridiagonal

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from dpir.mode_solver import (
    ModeSolution,
    block_x_cm,
    corrected_fundamental,
    hamiltonian,
    position,
    solve_mode,
)

CORONENE_36 = (807.0896514159117, 711.0647894175921)   # ω and φ_iiii of the mode that drove S3's 'other' family


def grid_fundamental(omega_cm, constants, points=6001, half_width=14.0):
    """The same Hamiltonian on a uniform grid in q, kinetic term by the three-point second derivative: a route that shares no code
    with the harmonic-oscillator basis."""
    q = np.linspace(-half_width, half_width, points)
    dq = q[1] - q[0]
    v = 0.5 * omega_cm * q**2 + sum(phi / math.factorial(m) * q**m for m, phi in constants.items())
    main = omega_cm / dq**2 + v
    off = np.full(points - 1, -0.5 * omega_cm / dq**2)
    e = eigh_tridiagonal(main, off, select="i", select_range=(0, 1))[0]
    return float(e[1] - e[0])


def test_a_harmonic_mode_keeps_its_frequency():
    s = solve_mode(500.0, {})
    assert isinstance(s, ModeSolution)
    assert s.fundamental_cm == pytest.approx(500.0, abs=1e-9) and s.shift_cm == pytest.approx(0.0, abs=1e-9)
    assert s.levels_cm == pytest.approx((500.0, 1000.0, 1500.0), abs=1e-8)


def test_position_is_the_dimensionless_coordinate():
    q = position(6)
    assert (q @ q)[0, 0] == pytest.approx(0.5)              # ⟨0|q²|0⟩ = ½
    assert q[0, 1] == pytest.approx(np.sqrt(0.5)) and np.allclose(q, q.T)
    assert np.allclose(np.diag(hamiltonian(500.0, {}, 4)), [250.0, 750.0, 1250.0, 1750.0])
    with pytest.raises(ValueError, match="at least two states"):
        position(1)
    with pytest.raises(ValueError, match="orders 3 and above"):
        hamiltonian(500.0, {2: 1.0}, 4)


@pytest.mark.parametrize("quartic", [0.5, 2.0, 8.0])
def test_a_weak_quartic_reproduces_perturbation_theory(quartic):
    omega = 1000.0
    s = solve_mode(omega, {4: quartic})
    # first order is ω + φ/8; what is left over is the next order, which goes as φ²/ω
    assert s.fundamental_cm == pytest.approx(omega + quartic / 8.0, abs=0.05 * quartic**2 / omega + 1e-9)
    corrected, _ = corrected_fundamental(omega, {4: quartic}, nu_vpt2_cm=omega + quartic / 8.0)
    assert corrected == pytest.approx(omega + quartic / 8.0, abs=0.05)   # VPT2 is reproduced where VPT2 is sound


def test_what_perturbation_theory_misses_grows_as_the_square_of_the_constant():
    omega = 1000.0
    missed = [abs(solve_mode(omega, {4: phi}).fundamental_cm - (omega + phi / 8.0)) for phi in (2.0, 8.0)]
    assert missed[1] / missed[0] == pytest.approx(16.0, rel=0.02)   # four times the constant, sixteen times the miss


def test_a_weak_cubic_and_quartic_reproduce_their_x_ii():
    omega, constants = 1000.0, {3: 30.0, 4: 5.0}
    expected = omega + 2.0 * block_x_cm(omega, constants)
    assert block_x_cm(omega, constants) == pytest.approx(5.0 / 16.0 - 5.0 * 900.0 / (48.0 * 1000.0))
    assert solve_mode(omega, constants).fundamental_cm == pytest.approx(expected, abs=0.05)


def test_the_strong_quartic_matches_an_independent_grid_solution():
    omega, quartic = CORONENE_36
    basis = solve_mode(omega, {4: quartic})
    grid = grid_fundamental(omega, {4: quartic})
    assert basis.fundamental_cm == pytest.approx(grid, abs=0.05)
    # perturbation theory puts this fundamental at ω + φ/8; the solved one is well below it
    assert basis.fundamental_cm < omega + quartic / 8.0 - 5.0
    assert basis.basis <= 400 and basis.settled_to_cm <= 1e-4


def test_a_cubic_term_too_is_matched_by_the_grid():
    omega, constants = 600.0, {3: -120.0, 4: 300.0}
    assert solve_mode(omega, constants).fundamental_cm == pytest.approx(grid_fundamental(omega, constants), abs=0.05)


def test_the_correction_is_only_what_the_block_solved():
    omega, quartic = CORONENE_36
    nu_vpt2 = 986.29
    corrected, solution = corrected_fundamental(omega, {4: quartic}, nu_vpt2)
    assert corrected == pytest.approx(nu_vpt2 + solution.fundamental_cm - (omega + quartic / 8.0))
    assert corrected < nu_vpt2            # the block's exact spacing is below its second-order value


def test_an_unbounded_potential_is_refused():
    for constants in ({4: -50.0}, {3: 40.0}, {4: 10.0, 6: -3.0}, {3: 1.0, 4: 0.0}):
        with pytest.raises(ValueError, match="unbounded below"):
            solve_mode(800.0, constants)
    solve_mode(800.0, {3: 40.0, 4: 200.0})          # the quartic holds the cubic
    solve_mode(800.0, {4: -50.0, 6: 400.0})         # the sextic holds a negative quartic


def test_a_fundamental_that_will_not_settle_raises(monkeypatch):
    monkeypatch.setattr("dpir.mode_solver.CONVERGENCE_CM", 1e-18)
    with pytest.raises(ValueError, match="had not settled"):
        solve_mode(*[CORONENE_36[0], {4: CORONENE_36[1]}])
