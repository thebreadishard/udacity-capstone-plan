"""src/dpir/mode_solver.py (TASKS 209): a block of one or two modes reproduces perturbation theory where VPT2 is sound, matches an
independent grid solution of the same Hamiltonian where it is not (the noise principle's second route), reduces to the one-mode answer
when the coupling is switched off, and refuses a potential that falls away in any direction."""
import math
import sys
from pathlib import Path

import numpy as np
import pytest
from scipy.linalg import eigh_tridiagonal

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from dpir.mode_solver import (
    BlockSolution,
    basis_reach,
    block_hamiltonian,
    block_second_order,
    block_x_cm,
    by_order,
    corrected_fundamental,
    corrected_fundamentals,
    position_operators,
    runaway_distance,
    solve_block,
    solve_mode,
    states,
)

CORONENE_36 = (807.0896514159117, 711.0647894175921)   # ω and φ_iiii of the mode that drove S3's 'other' family
CORONENE_24 = (642.9393964152789, 129.96424368988372)
CORONENE_X = 4 * 69.8                                   # φ_iijj of the pair, from x(24,36) = φ_iijj/4


def grid_fundamental(omega_cm, constants, points=6001, half_width=14.0):
    """One mode on a uniform grid in q, kinetic term by the three-point second derivative: a route that shares no code with the
    harmonic-oscillator basis. `constants` is keyed by order, as solve_mode takes them."""
    q = np.linspace(-half_width, half_width, points)
    dq = q[1] - q[0]
    v = 0.5 * omega_cm * q**2 + sum(phi / math.factorial(m) * q**m for m, phi in constants.items())
    main = omega_cm / dq**2 + v
    off = np.full(points - 1, -0.5 * omega_cm / dq**2)
    e = eigh_tridiagonal(main, off, select="i", select_range=(0, 1))[0]
    return float(e[1] - e[0])


def test_a_harmonic_mode_keeps_its_frequency():
    s = solve_mode(500.0, {})
    assert isinstance(s, BlockSolution) and s.modes == (0,)
    assert s.fundamental(0) == pytest.approx(500.0, abs=1e-9) and s.shift_cm(0) == pytest.approx(0.0, abs=1e-9)
    assert s.overlaps == pytest.approx((1.0,), abs=1e-12)


def test_a_harmonic_pair_keeps_both_frequencies():
    s = solve_block([500.0, 900.0], {}, modes=[24, 36])
    assert s.modes == (24, 36)
    assert s.fundamental(24) == pytest.approx(500.0, abs=1e-9) and s.fundamental(36) == pytest.approx(900.0, abs=1e-9)


def test_the_basis_and_its_operators_are_the_dimensionless_ones():
    basis = states(2, 3)
    assert basis[0] == (0, 0) and len(basis) == 10 and max(sum(s) for s in basis) == 3
    q0, q1 = position_operators(basis)
    assert (q0 @ q0)[0, 0] == pytest.approx(0.5) and (q1 @ q1)[0, 0] == pytest.approx(0.5)   # ⟨0|q²|0⟩ = ½ per mode
    assert np.allclose(q0, q0.T) and np.allclose(q1, q1.T)
    # the two coordinates commute in the full product basis but not at the edge of a polyad truncation, so the Hamiltonian
    # symmetrises every term it builds from them
    assert not np.allclose(q0 @ q1, q1 @ q0)
    mixed = block_hamiltonian([500.0, 900.0], {(0, 0, 0, 1): 24.0}, basis)
    np.testing.assert_allclose(mixed, mixed.T, atol=1e-12)
    assert np.allclose(np.diag(block_hamiltonian([500.0, 900.0], {}, basis))[:3], [700.0, 1600.0, 1200.0])
    with pytest.raises(ValueError, match="order 3 or 4"):
        block_hamiltonian([500.0], {(0, 0): 1.0}, states(1, 4))
    with pytest.raises(ValueError, match="inside a block"):
        block_hamiltonian([500.0], {(0, 0, 1): 1.0}, states(1, 4))


@pytest.mark.parametrize("quartic", [0.5, 2.0, 8.0])
def test_a_weak_quartic_reproduces_perturbation_theory(quartic):
    omega = 1000.0
    s = solve_mode(omega, {4: quartic})
    # first order is ω + φ/8; what is left over is the next order, which goes as φ²/ω
    assert s.fundamental(0) == pytest.approx(omega + quartic / 8.0, abs=0.05 * quartic**2 / omega + 1e-9)
    corrected, _ = corrected_fundamental(omega, {4: quartic}, nu_vpt2_cm=omega + quartic / 8.0)
    assert corrected == pytest.approx(omega + quartic / 8.0, abs=0.05)   # VPT2 is reproduced where VPT2 is sound


def test_what_perturbation_theory_misses_grows_as_the_square_of_the_constant():
    omega = 1000.0
    missed = [abs(solve_mode(omega, {4: phi}).fundamental(0) - (omega + phi / 8.0)) for phi in (2.0, 8.0)]
    assert missed[1] / missed[0] == pytest.approx(16.0, rel=0.02)   # four times the constant, sixteen times the miss


def test_a_weak_cubic_and_quartic_reproduce_their_x_ii():
    omega, constants = 1000.0, {3: 30.0, 4: 5.0}
    expected = omega + 2.0 * block_x_cm(omega, constants)
    assert block_x_cm(omega, constants) == pytest.approx(5.0 / 16.0 - 5.0 * 900.0 / (48.0 * 1000.0))
    assert solve_mode(omega, constants).fundamental(0) == pytest.approx(expected, abs=0.05)


def test_the_strong_quartic_matches_an_independent_grid_solution():
    omega, quartic = CORONENE_36
    block = solve_mode(omega, {4: quartic})
    assert block.fundamental(0) == pytest.approx(grid_fundamental(omega, {4: quartic}), abs=0.05)
    # perturbation theory puts this fundamental at ω + φ/8; the solved one is well below it
    assert block.fundamental(0) < omega + quartic / 8.0 - 5.0


def test_a_cubic_term_too_is_matched_by_the_grid():
    omega, constants = 600.0, {3: -120.0, 4: 300.0}
    assert solve_mode(omega, constants).fundamental(0) == pytest.approx(grid_fundamental(omega, constants), abs=0.05)


def test_a_pair_without_coupling_is_the_two_single_modes():
    (w24, p24), (w36, p36) = CORONENE_24, CORONENE_36
    pair = solve_block([w24, w36], {(0, 0, 0, 0): p24, (1, 1, 1, 1): p36}, modes=[24, 36])
    assert pair.fundamental(24) == pytest.approx(solve_mode(w24, {4: p24}).fundamental(0), abs=1e-3)
    assert pair.fundamental(36) == pytest.approx(solve_mode(w36, {4: p36}).fundamental(0), abs=1e-3)


def test_a_weak_pair_coupling_reproduces_its_x_ij():
    w0, w1, coupling = 700.0, 1100.0, 8.0            # φ_iijj enters x_ij as φ/4, and the fundamental as ½ x_ij
    pair = solve_block([w0, w1], {(0, 0, 1, 1): coupling})
    assert pair.fundamental(0) == pytest.approx(w0 + 0.5 * coupling / 4.0, abs=0.02)
    assert pair.fundamental(1) == pytest.approx(w1 + 0.5 * coupling / 4.0, abs=0.02)


def test_the_multiplicity_of_each_constant_is_the_force_fields_own():
    # φ_iiij enters the potential as φ q_i³q_j/6: at four quanta the matrix element is that of q_i³q_j times φ/6
    basis = states(2, 6)
    q0, q1 = position_operators(basis)
    h = block_hamiltonian([500.0, 900.0], {(0, 0, 0, 1): 24.0}, basis)
    raw = 4.0 * (q0 @ q0 @ q0 @ q1)
    expected = np.diag([sum(w * (n + 0.5) for w, n in zip((500.0, 900.0), s, strict=True)) for s in basis]) + (raw + raw.T) / 2
    np.testing.assert_allclose(h, expected, atol=1e-10)


def test_a_potential_that_falls_back_within_the_basis_is_refused():
    with pytest.raises(ValueError, match="falls back to its origin"):
        solve_mode(800.0, {4: -50.0})                                        # V = 400q² − 2.08q⁴ turns over at q ≈ 13.9
    with pytest.raises(ValueError, match="falls back to its origin"):
        solve_block([800.0, 900.0], {(0, 0, 0, 0): 100.0, (1, 1, 1, 1): 100.0, (0, 0, 1, 1): -600.0})
    solve_mode(800.0, {3: 40.0, 4: 200.0})                                   # the quartic holds the cubic


def test_a_runaway_beyond_the_basis_is_allowed_and_measured():
    """A truncated force field almost always falls away somewhere; only a fall inside the basis makes the answer meaningless."""
    assert runaway_distance([800.0], {}) == float("inf")
    far = runaway_distance([800.0], {(0, 0, 0, 0): -0.1})                   # V = 400q² − 0.0042q⁴, over only at q ≈ 309
    assert far == float("inf") or far > 3 * basis_reach(120)
    solve_mode(800.0, {4: -0.1})                                             # so it is solved, not refused
    assert basis_reach(120) == pytest.approx(math.sqrt(241))


def test_blocks_of_more_than_two_modes_and_bad_shapes_are_refused():
    with pytest.raises(ValueError, match="one or two"):
        solve_block([500.0, 700.0, 900.0], {})
    with pytest.raises(ValueError, match="one frequency per mode"):
        solve_block([500.0, 700.0], {}, modes=[1])
    with pytest.raises(ValueError, match="orders 3 and 4"):
        solve_mode(500.0, {2: 1.0})


def test_a_fundamental_that_will_not_settle_raises(monkeypatch):
    monkeypatch.setattr("dpir.mode_solver.CONVERGENCE_CM", 1e-18)
    with pytest.raises(ValueError, match="had not settled"):
        solve_mode(CORONENE_36[0], {4: CORONENE_36[1]})
def test_the_blocks_second_order_value_matches_the_closed_form_for_one_mode():
    # the λ² division carries the solver's settling tolerance with it: CONVERGENCE_CM / λ_small² = 0.01 cm⁻¹ here
    for omega, constants in ((1000.0, {4: 60.0}), (800.0, {3: 150.0, 4: 400.0}), (600.0, {3: -300.0, 4: 900.0})):
        got = block_second_order([omega], by_order(constants))[0]
        assert got == pytest.approx(omega + 2.0 * block_x_cm(omega, constants), abs=0.05)


def test_the_blocks_second_order_value_gives_a_pairs_x_ij():
    w0, w1, coupling = 700.0, 1100.0, 240.0            # x_ij = phi_iijj/4, and half of it enters each fundamental
    got = block_second_order([w0, w1], {(0, 0, 1, 1): coupling})
    assert got[0] == pytest.approx(w0 + 0.5 * coupling / 4.0, rel=1e-6)
    assert got[1] == pytest.approx(w1 + 0.5 * coupling / 4.0, rel=1e-6)


def test_a_correction_vanishes_where_perturbation_theory_was_sound():
    w0, w1 = 700.0, 1100.0
    constants = {(0, 0, 0, 0): 3.0, (1, 1, 1, 1): 4.0, (0, 0, 1, 1): 5.0, (0, 0, 0, 1): 2.0}
    second = block_second_order([w0, w1], constants)
    corrected, solution = corrected_fundamentals([w0, w1], constants, list(second), modes=[24, 36])
    assert solution.modes == (24, 36)
    assert corrected[0] == pytest.approx(second[0], abs=0.01) and corrected[1] == pytest.approx(second[1], abs=0.01)


def test_the_coronene_pair_is_solved_and_its_block_is_not_its_second_order():
    (w24, p24), (w36, p36) = CORONENE_24, CORONENE_36
    constants = {(0, 0, 0, 0): p24, (1, 1, 1, 1): p36, (0, 0, 1, 1): CORONENE_X}
    second = block_second_order([w24, w36], constants, modes=[24, 36])
    solution = solve_block([w24, w36], constants, modes=[24, 36])
    # second order puts mode 36 at omega + phi/8 + half of x(24,36); the solved block is well below that
    assert second[1] == pytest.approx(w36 + p36 / 8.0 + 0.5 * CORONENE_X / 4.0, rel=1e-5)
    assert solution.fundamental(36) < second[1] - 10.0
    assert min(solution.overlaps) > 0.5
