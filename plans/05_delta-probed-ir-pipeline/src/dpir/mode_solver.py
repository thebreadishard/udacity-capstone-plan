"""A block of modes solved rather than perturbed (TASKS 209; registered 13 November 2026).

Where a mode's correction is too large for second-order perturbation theory (`dpir.vpt2_domain` marks it), the fundamental is still a
real number — VPT2 is simply the wrong way to reach it. This module reaches it by diagonalising the Hamiltonian of a small block of
modes in a harmonic-oscillator product basis, in the dimensionless reduced normal coordinates q of the quartic force field:

    H = Σ_i (ω_i/2)(p_i² + q_i²) + (1/6) Σ_{ijk} φ_ijk q_i q_j q_k + (1/24) Σ_{ijkl} φ_ijkl q_i q_j q_k q_l

with ⟨0|q²|0⟩ = ½ per mode, so the harmonic levels are Σ ω_i(n_i + ½). The constants are given once per sorted index tuple and the
builder applies each one's multiplicity, so φ_iijj enters as φ_iijj q_i²q_j²/4 and φ_iiij as φ_iiij q_i³q_j/6. The basis holds every
product state with at most `quanta` quanta in all (a polyad truncation), grown until every fundamental settles.

**What it replaces, and what it leaves alone.** A block holds exactly the part of VPT2 that its own modes' constants produce. For one
mode that is x_ii(block) = φ_iiii/16 − 5 φ_iii²/(48 ω); for a pair it is that of each mode plus their x_ij. Everything else — the
terms running through modes outside the block — stays as VPT2 computed it, and the corrected fundamental is

    ν_i = ν_i(VPT2) + [(E(1_i) − E(0)) − (ω_i + 2 x_ii(block) + ½ Σ_{j∈block, j≠i} x_ij(block))]

so the bracket vanishes wherever the block is weakly anharmonic: the method reproduces VPT2 exactly where VPT2 is sound and departs
from it only by what it actually solved. A block may only replace what it dominates; the caller checks that (`probes/solve_marked_modes.py`).

**When it refuses.** A truncated force field almost always falls away somewhere far out; what matters is whether it does so inside the
stretch of q the basis samples, because a variational answer there is the runaway and not a fundamental. A fundamental that has not
settled by MAX_QUANTA, or a state that cannot be told apart from its harmonic parent, raises rather than returning a number.
"""
from __future__ import annotations

import itertools
import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

import numpy as np

START_QUANTA = 40          # the first basis holds every product state with at most this many quanta in all
QUANTA_STEP = 20
MAX_QUANTA = 120           # beyond this a fundamental is called unsettled rather than returned
CONVERGENCE_CM = 1e-4      # two successive bases must agree on every fundamental to this
ASSIGNMENT_MIN = 0.5       # a fundamental must carry at least this much of its harmonic parent, or it is not that fundamental
DIRECTIONS = 721           # directions sampled when asking whether the quartic form stays non-negative
RUNAWAY_SEARCH = 3.0       # the potential is followed this many basis reaches out before it is called bounded
RUNAWAY_POINTS = 2000      # samples along each direction in that search
RUNAWAY_MARGIN = 1.5       # the potential must stay up to this many basis reaches, or the block is refused
SECOND_ORDER_LAMBDAS = (0.05, 0.10)   # the two scalings the block's second-order value is extrapolated from: small enough that the
                                      # λ⁶ term left after the λ⁴ removal stays under ~0.1 cm⁻¹ even for a φ_iiii of 3,000 cm⁻¹,
                                      # large enough that dividing by λ² keeps the solver's own tolerance under 0.05 cm⁻¹


@dataclass(frozen=True)
class BlockSolution:
    """One block's fundamentals, and how far the basis was grown to reach them."""

    modes: tuple[int, ...]
    omega_cm: tuple[float, ...]
    fundamentals_cm: tuple[float, ...]
    overlaps: tuple[float, ...]
    quanta: int
    settled_to_cm: float

    def fundamental(self, mode: int) -> float:
        """The fundamental of one of the block's modes, by its own index."""
        return self.fundamentals_cm[self.modes.index(mode)]

    def shift_cm(self, mode: int) -> float:
        """That fundamental's distance from the harmonic frequency."""
        i = self.modes.index(mode)
        return self.fundamentals_cm[i] - self.omega_cm[i]


def states(n_modes: int, quanta: int) -> list[tuple[int, ...]]:
    """Every product state with at most `quanta` quanta in all, the ground state first."""
    if n_modes < 1 or quanta < 1:
        raise ValueError(f"{n_modes} modes and {quanta} quanta: both at least one")
    out = [s for total in range(quanta + 1) for s in itertools.product(range(total + 1), repeat=n_modes) if sum(s) == total]
    return out


def position_operators(basis: list[tuple[int, ...]]) -> list[np.ndarray]:
    """q_i in that basis, dimensionless reduced normal coordinates (⟨0|q²|0⟩ = ½ per mode)."""
    index = {s: k for k, s in enumerate(basis)}
    n_modes = len(basis[0])
    out = []
    for i in range(n_modes):
        q = np.zeros((len(basis), len(basis)))
        for s, row in index.items():
            raised = (*s[:i], s[i] + 1, *s[i + 1:])
            if raised in index:
                value = math.sqrt((s[i] + 1) / 2.0)
                q[index[raised], row] = q[row, index[raised]] = value
        out.append(q)
    return out


def _multiplicity(key: tuple[int, ...]) -> int:
    """How many index orders this sorted tuple stands for in the fully symmetric sum."""
    counts: dict[int, int] = {}
    for i in key:
        counts[i] = counts.get(i, 0) + 1
    return math.factorial(len(key)) // math.prod(math.factorial(c) for c in counts.values())


def block_hamiltonian(omega_cm: Sequence[float], constants: Mapping[tuple[int, ...], float], basis: list[tuple[int, ...]]) -> np.ndarray:
    """H in cm⁻¹ in that basis: the harmonic diagonal plus every constant with its multiplicity, indices local to the block."""
    if any(w <= 0 for w in omega_cm):
        raise ValueError(f"omega {list(omega_cm)} cm-1: positive")
    n_modes = len(omega_cm)
    q = position_operators(basis)
    h = np.diag([sum(w * (n + 0.5) for w, n in zip(omega_cm, s, strict=True)) for s in basis])
    for key, phi in constants.items():
        if len(key) not in (3, 4):
            raise ValueError(f"constant {key}: order 3 or 4; the harmonic part is omega")
        if any(not 0 <= i < n_modes for i in key):
            raise ValueError(f"constant {key}: every index inside a block of {n_modes} modes")
        if not phi:
            continue
        term = np.eye(len(basis))
        for i in key:
            term = term @ q[i]
        # the q of different modes commute in the full product basis but not at the edge of a polyad truncation, so a product of
        # them is not symmetric there; the observable is, and the difference vanishes as the basis grows
        h = h + phi * _multiplicity(key) / math.factorial(len(key)) * (term + term.T) / 2.0
    return h


def _form(order: int, n_modes: int, constants: Mapping[tuple[int, ...], float], axes: np.ndarray) -> np.ndarray:
    """The homogeneous part of that order, on unit directions: Σ φ · multiplicity / order! · Π q."""
    value = np.zeros(axes.shape[1])
    for key, phi in constants.items():
        if len(key) != order or not phi:
            continue
        term = np.ones(axes.shape[1])
        for i in key:
            term = term * axes[i]
        value += phi * _multiplicity(key) / math.factorial(order) * term
    return value


def basis_reach(quanta: int) -> float:
    """How far in q a basis of that many quanta reaches: the classical turning point of its highest state, √(2n+1)."""
    return float(np.sqrt(2 * quanta + 1))


def runaway_distance(omega_cm: Sequence[float], constants: Mapping[tuple[int, ...], float]) -> float:
    """The smallest q at which the block's potential falls back to the value it has at the origin, over all directions — ∞ when it
    never does.

    A truncated force field almost always runs away somewhere: a quartic form that dips a tenth of a percent below zero makes the
    potential fall again at some distance. What matters is whether that distance lies inside the stretch of q the basis samples, not
    whether it exists, so this returns the distance and `solve_block` compares it with `basis_reach`.
    """
    n_modes = len(omega_cm)
    if n_modes == 2:
        angles = np.linspace(0.0, 2.0 * np.pi, DIRECTIONS)
        axes = np.stack([np.cos(angles), np.sin(angles)])
    else:
        angles = np.array([0.0, np.pi])          # one mode has two directions, not a circle of them
        axes = np.stack([np.cos(angles)])
    harmonic = 0.5 * np.einsum("i,ij->j", np.asarray(omega_cm, float), axes**2)
    cubic, quartic = _form(3, n_modes, constants, axes), _form(4, n_modes, constants, axes)
    q = np.linspace(0.0, RUNAWAY_SEARCH * basis_reach(MAX_QUANTA), RUNAWAY_POINTS)[1:]
    value = harmonic[:, None] * q**2 + cubic[:, None] * q**3 + quartic[:, None] * q**4
    fallen = value <= 0.0
    if not fallen.any():
        return float("inf")
    return float(q[np.argmax(fallen.any(axis=0))])


def _fundamentals(energies: np.ndarray, vectors: np.ndarray, basis: list[tuple[int, ...]],
                  n_modes: int) -> tuple[list[float], list[float]]:
    """Each mode's fundamental above the ground state, taken as the eigenstate carrying most of that harmonic first excited state."""
    ground = basis.index((0,) * n_modes)
    zero = int(np.argmax(np.abs(vectors[ground]) ** 2))
    out, overlaps = [], []
    for i in range(n_modes):
        parent = basis.index(tuple(1 if k == i else 0 for k in range(n_modes)))
        weights = np.abs(vectors[parent]) ** 2
        weights[zero] = -1.0
        which = int(np.argmax(weights))
        out.append(float(energies[which] - energies[zero]))
        overlaps.append(float(weights[which]))
    return out, overlaps


def solve_block(omega_cm: Sequence[float], constants: Mapping[tuple[int, ...], float],
                modes: Sequence[int] | None = None) -> BlockSolution:
    """Every mode's fundamental in the block, the basis grown until each settles to CONVERGENCE_CM."""
    omega_cm = tuple(float(w) for w in omega_cm)
    modes = tuple(range(len(omega_cm))) if modes is None else tuple(int(m) for m in modes)
    if len(modes) != len(omega_cm):
        raise ValueError(f"modes {modes} and omega {omega_cm}: one frequency per mode")
    if len(omega_cm) > 2:
        raise ValueError(f"a block of {len(omega_cm)} modes: this solver takes one or two, the sizes a semi-diagonal force field holds")
    runaway = runaway_distance(omega_cm, constants)
    if runaway <= RUNAWAY_MARGIN * basis_reach(MAX_QUANTA):
        raise ValueError(f"the potential of the block {modes} falls back to its origin at q = {runaway:.1f}, inside "
                         f"{RUNAWAY_MARGIN:g} times the reach {basis_reach(MAX_QUANTA):.1f} of the largest basis: a variational "
                         f"answer there is the runaway, not a fundamental; this block needs a measured potential")
    previous: list[float] | None = None
    for quanta in range(START_QUANTA, MAX_QUANTA + 1, QUANTA_STEP):
        basis = states(len(omega_cm), quanta)
        energies, vectors = np.linalg.eigh(block_hamiltonian(omega_cm, constants, basis))
        found, overlaps = _fundamentals(energies, vectors, basis, len(omega_cm))
        if min(overlaps) < ASSIGNMENT_MIN:
            raise ValueError(f"a fundamental of the block {modes} carries only {min(overlaps):.2f} of its harmonic parent, so which "
                             f"state it is cannot be told; this block is mixed beyond a fundamental's meaning")
        if previous is not None:
            settled = max(abs(a - b) for a, b in zip(found, previous, strict=True))
            if settled <= CONVERGENCE_CM:
                return BlockSolution(modes, omega_cm, tuple(found), tuple(overlaps), quanta, settled)
        previous = found
    raise ValueError(f"the fundamentals of the block {modes} had not settled to {CONVERGENCE_CM} cm-1 at {MAX_QUANTA} quanta: "
                     f"last {previous}")


def solve_mode(omega_cm: float, constants: Mapping[int, float]) -> BlockSolution:
    """One mode's own block, its constants given by order (3 and 4) as a quartic force field names them."""
    return solve_block([omega_cm], by_order(constants))


def block_second_order(omega_cm: Sequence[float], constants: Mapping[tuple[int, ...], float],
                       modes: Sequence[int] | None = None) -> tuple[float, ...]:
    """What second-order perturbation theory makes of this block, taken from the same diagonalisation rather than from a second set
    of formulas that could drift from it.

    Scale the cubic constants by λ and the quartic ones by λ², the ordering in which both first enter at second order. The exact
    fundamentals are then ν(λ) = ω + a₂λ² + a₄λ⁴ + …, with no odd power, so a₂ — the whole of second-order perturbation theory for
    this block — is the λ → 0 limit of (ν(λ) − ω)/λ², reached from two small λ whose λ⁴ term is removed.

    Dividing by λ² divides the solver's own settling tolerance by λ² too, so this value carries about CONVERGENCE_CM / λ_small², which
    is 0.01 cm⁻¹ at the λ used here — far below the corrections it is subtracted from, which run to tens of cm⁻¹, but a reason not to
    quote it on its own.
    """
    scaled = []
    for lam in SECOND_ORDER_LAMBDAS:
        constants_lambda = {key: phi * lam ** (len(key) - 2) for key, phi in constants.items()}
        solution = solve_block(omega_cm, constants_lambda, modes)
        scaled.append([(nu - w) / lam**2 for nu, w in zip(solution.fundamentals_cm, omega_cm, strict=True)])
    small, large = SECOND_ORDER_LAMBDAS
    weight = large**2 / (large**2 - small**2)
    return tuple(w + weight * a - (weight - 1.0) * b for w, a, b in zip(omega_cm, scaled[0], scaled[1], strict=True))


def block_x_cm(omega_cm: float, constants: Mapping[int, float]) -> float:
    """The part of VPT2's x_ii a one-mode block holds, in closed form: φ_iiii/16 − 5 φ_iii²/(48 ω).

    This is the counterpart `block_second_order` is checked against for one mode (the only size with a closed form in reach); the
    correction itself never uses it, so there is one implementation in the path a label depends on.
    """
    if omega_cm <= 0:
        raise ValueError(f"omega {omega_cm} cm-1: positive")
    return constants.get(4, 0.0) / 16.0 - 5.0 * constants.get(3, 0.0) ** 2 / (48.0 * omega_cm)


def by_order(constants: Mapping[int, float]) -> dict[tuple[int, ...], float]:
    """One mode's constants, given by order as a force field names them, keyed as a block's are."""
    if any(order not in (3, 4) for order in constants):
        raise ValueError(f"constants {sorted(constants)}: orders 3 and 4")
    return {(0,) * order: float(phi) for order, phi in constants.items()}


def corrected_fundamentals(omega_cm: Sequence[float], constants: Mapping[tuple[int, ...], float], nu_vpt2_cm: Sequence[float],
                           modes: Sequence[int] | None = None) -> tuple[tuple[float, ...], BlockSolution]:
    """Each mode's VPT2 fundamental with the block replaced by its solution, and that solution. The correction is the block's exact
    level spacing minus the block's own second-order value, so it vanishes wherever VPT2 was sound."""
    solution = solve_block(omega_cm, constants, modes)
    second_order = block_second_order(omega_cm, constants, modes)
    return tuple(nu + (exact - order) for nu, exact, order
                 in zip(nu_vpt2_cm, solution.fundamentals_cm, second_order, strict=True)), solution


def corrected_fundamental(omega_cm: float, constants: Mapping[int, float], nu_vpt2_cm: float) -> tuple[float, BlockSolution]:
    """One mode's block: `corrected_fundamentals` with its constants given by order."""
    corrected, solution = corrected_fundamentals([omega_cm], by_order(constants), [nu_vpt2_cm])
    return corrected[0], solution
