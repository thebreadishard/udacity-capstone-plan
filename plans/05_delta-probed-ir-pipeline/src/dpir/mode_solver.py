"""One mode's fundamental solved rather than perturbed (TASKS 209, stage 1; registered 13 November 2026).

Where a mode's correction is too large for second-order perturbation theory (`dpir.vpt2_domain` marks it), the fundamental is still a
real number — VPT2 is simply the wrong way to reach it. This module reaches it by diagonalising the mode's own one-dimensional
Hamiltonian in a harmonic-oscillator basis, in the dimensionless reduced normal coordinate q of the quartic force field:

    H = (ω/2)(p² + q²) + Σ_m φ_m q^m / m!      (m = 3, 4, and 6 where a measured potential supplies it)

with ⟨0|q²|0⟩ = ½, so q = (a + a†)/√2 and the harmonic levels are ω(n + ½). The basis grows until the fundamental settles.

**What it replaces, and what it leaves alone.** A one-mode block holds exactly the part of VPT2's x_ii that comes from the mode's own
constants, x_ii(block) = φ_iiii/16 − 5 φ_iii²/(48 ω). Everything else — the terms of x_ii that run through other modes, and every
x_ij — stays as VPT2 computed it. So the corrected fundamental is

    ν = ν(VPT2) + [(E₁ − E₀) − (ω + 2 x_ii(block))]

and the bracket vanishes wherever the block is weakly anharmonic: the method reproduces VPT2 exactly where VPT2 is sound, and departs
from it only by what it actually solved. `corrected_fundamental` is the one implementation of that rule.

**When it refuses.** A quartic constant below zero makes the one-mode potential unbounded, and a variational answer in any finite basis
is then meaningless, however convergent it looks; such a mode needs a measured potential with a positive sextic term, not this solver.
A fundamental that has not settled by MAX_BASIS raises rather than returning its last value.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

START_BASIS = 40           # harmonic-oscillator states in the first attempt
BASIS_STEP = 40            # added at each attempt
MAX_BASIS = 400            # beyond this the fundamental is called unsettled rather than returned
CONVERGENCE_CM = 1e-4      # two successive bases must agree on the fundamental to this
LEVELS = 3                 # levels above the zero point kept in the solution


@dataclass(frozen=True)
class ModeSolution:
    """One mode's own levels, and how far the basis was grown to reach them."""

    omega_cm: float
    fundamental_cm: float
    levels_cm: tuple[float, ...]
    basis: int
    settled_to_cm: float

    @property
    def shift_cm(self) -> float:
        """The fundamental's distance from the harmonic frequency."""
        return self.fundamental_cm - self.omega_cm


def position(basis: int) -> np.ndarray:
    """q in a harmonic-oscillator basis of that size, in dimensionless reduced normal coordinates (⟨0|q²|0⟩ = ½)."""
    if basis < 2:
        raise ValueError(f"basis {basis}: at least two states")
    off = np.sqrt(np.arange(1, basis) / 2.0)
    return np.diag(off, 1) + np.diag(off, -1)


def hamiltonian(omega_cm: float, constants: dict[int, float], basis: int) -> np.ndarray:
    """H in cm⁻¹ in that basis: the harmonic diagonal plus every given φ_m q^m / m!."""
    if omega_cm <= 0:
        raise ValueError(f"omega {omega_cm} cm-1: positive")
    if any(order < 3 for order in constants):
        raise ValueError(f"constants {sorted(constants)}: orders 3 and above; the harmonic part is omega")
    q = position(basis)
    h = np.diag(omega_cm * (np.arange(basis) + 0.5))
    power = np.eye(basis)
    for order in range(1, max(constants, default=0) + 1):
        power = power @ q
        if constants.get(order):
            h = h + constants[order] / math.factorial(order) * power
    return h


def _refuse_unbounded(constants: dict[int, float]) -> None:
    """A one-mode potential that falls away at large |q| has no variational answer, whatever a finite basis reports."""
    highest = max((order for order, phi in constants.items() if phi), default=0)
    if highest == 0:
        return
    if highest % 2 or constants[highest] < 0:
        raise ValueError(f"the potential is unbounded below: its highest term is order {highest} with "
                         f"phi {constants[highest]:.1f} cm-1; this mode needs a measured potential, not this solver")


def solve_mode(omega_cm: float, constants: dict[int, float], levels: int = LEVELS) -> ModeSolution:
    """The mode's lowest levels above its zero point, the basis grown until the fundamental settles to CONVERGENCE_CM."""
    _refuse_unbounded(constants)
    previous = None
    for basis in range(START_BASIS, MAX_BASIS + 1, BASIS_STEP):
        if basis <= levels:
            continue
        energies = np.linalg.eigvalsh(hamiltonian(omega_cm, constants, basis))
        fundamental = float(energies[1] - energies[0])
        if previous is not None and abs(fundamental - previous) <= CONVERGENCE_CM:
            return ModeSolution(omega_cm, fundamental, tuple(float(e) for e in energies[1:levels + 1] - energies[0]),
                                basis, abs(fundamental - previous))
        previous = fundamental
    raise ValueError(f"the fundamental of a mode at {omega_cm:.1f} cm-1 had not settled to {CONVERGENCE_CM} cm-1 at a basis of "
                     f"{MAX_BASIS}: last two {previous:.4f} and {fundamental:.4f} cm-1")


def block_x_cm(omega_cm: float, constants: dict[int, float]) -> float:
    """The part of VPT2's x_ii a one-mode block already holds: φ_iiii/16 − 5 φ_iii²/(48 ω)."""
    if omega_cm <= 0:
        raise ValueError(f"omega {omega_cm} cm-1: positive")
    return constants.get(4, 0.0) / 16.0 - 5.0 * constants.get(3, 0.0) ** 2 / (48.0 * omega_cm)


def corrected_fundamental(omega_cm: float, constants: dict[int, float], nu_vpt2_cm: float) -> tuple[float, ModeSolution]:
    """VPT2's fundamental with the one-mode block replaced by its solution, and that solution. The correction is the block's exact
    level spacing minus the block's own second-order value, so it vanishes wherever VPT2 was sound."""
    solution = solve_mode(omega_cm, constants)
    second_order = omega_cm + 2.0 * block_x_cm(omega_cm, constants)
    return nu_vpt2_cm + (solution.fundamental_cm - second_order), solution
