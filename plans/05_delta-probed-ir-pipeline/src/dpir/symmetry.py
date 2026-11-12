"""A molecule's point-group operations and the normal-mode pairs they make degenerate (TASKS 204, 12 Nov 2026).

Promoted from ``probes/e8_symmetry.py`` (point_group_ops, 24 Sep 2026) and the degenerate pairs of 12 Nov 2026, when a 0.5 cm⁻¹ frequency
gap had paired accidental neighbours of asymmetric tops in the GVPT2 labels and missed a pair of coronene that the quadrature split by
0.70 cm⁻¹. Degeneracy that the physics may average over is a property of the group, so it is read from the group.

Operations come from the geometry alone: candidate orthogonal maps send three non-collinear reference atoms onto same-element atoms with
the same pairwise distances (Kabsch); a candidate is kept when it maps every atom onto a same-element atom within ``tol``; for planar
molecules the reflection through the plane and its products are added; the set is closed under products. No character tables.
"""
from __future__ import annotations

import itertools
from dataclasses import dataclass

import numpy as np

PAIR_GAP_REL = 1e-9     # relative eigenvalue gap of the symmetrised mode operator below which two directions are one plane (exact by symmetry)
ORTHONORMAL_TOL = 1e-8  # largest |qᵀq − I| accepted for the mode columns
SYMMETRIZE_PASSES = 5   # symmetrising passes before a geometry that does not settle is refused
IRREDUCIBLE_TOL = 1e-6  # an operation's 2 x 2 action differs from its transpose, or two actions fail to commute, by more than this
PAIR_WEIGHT_MIN = 0.5   # a mode carries a plane when at least this much of its norm lies in it
COLLINEAR_MIN = 1e-3    # |(b - a) x (c - a)| (bohr²) above which three atoms fix an orientation
PLANAR_REL = 1e-6       # smallest second moment over largest below which the molecule is planar

Operation = tuple[np.ndarray, list[int]]


def _kabsch(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """Orthogonal R (proper or improper) minimising |R A − B| for 3 × m point sets A, B (columns), both already centred."""
    U, _, Vt = np.linalg.svd(B @ A.T)
    return U @ Vt


def _kabsch_both(A: np.ndarray, B: np.ndarray) -> list[np.ndarray]:
    """Kabsch's solution and the one with the weakest singular direction flipped: for three atoms nearly coplanar with the centre the
    weakest direction is undetermined, so a proper operation can come out improper or the reverse (13 Oct 2026); both are tried."""
    U, _, Vt = np.linalg.svd(B @ A.T)
    return [U @ Vt, U @ np.diag([1.0, 1.0, -1.0]) @ Vt]


@dataclass(frozen=True)
class _Frame:
    """The centred coordinates, the elements, the plane's normal (None when not planar) and the tolerance (bohr)."""

    x: np.ndarray
    symbols: tuple[str, ...]
    normal: np.ndarray | None
    tol: float

    @classmethod
    def build(cls, symbols: list[str], coords_bohr: np.ndarray, tol: float) -> _Frame:
        x = np.asarray(coords_bohr, float)
        x = x - x.mean(0)
        moments, axes = np.linalg.eigh(x.T @ x)
        normal = axes[:, 0] if moments[0] < PLANAR_REL * max(moments[-1], 1.0) else None
        return cls(x, tuple(symbols), normal, tol)

    def reflection(self) -> np.ndarray:
        return np.eye(3) - 2 * np.outer(self.normal, self.normal)


def _permutation(frame: _Frame, R: np.ndarray) -> list[int] | None:
    """The atom permutation R induces, or None when an atom has no same-element image within tol or two atoms share an image."""
    x, sym = frame.x, frame.symbols
    y = x @ R.T
    perm = []
    for i in range(len(x)):
        d = np.linalg.norm(x - y[i], axis=1)
        j = int(np.argmin(d))
        if d[j] > frame.tol or sym[j] != sym[i]:
            return None
        perm.append(j)
    return perm if len(set(perm)) == len(perm) else None


def _refit(frame: _Frame, perm: list[int], improper: bool) -> np.ndarray | None:
    """The orthogonal map of the given handedness fitted over all atoms to the permutation, or None when it misses an atom by more than tol."""
    Rf = _kabsch(frame.x.T, frame.x[perm].T)
    if (np.linalg.det(Rf) < 0) != improper:
        if frame.normal is None:
            return None
        Rf = frame.reflection() @ Rf
    if np.abs(frame.x @ Rf.T - frame.x[perm]).max() > frame.tol:
        return None
    return Rf


def _reference_triple(frame: _Frame) -> tuple[int, int, int]:
    """Three non-collinear atoms, heavy atoms and atoms far from the centre first; raises for a linear molecule."""
    x, sym = frame.x, frame.symbols
    order = sorted(range(len(x)), key=lambda i: (sym[i] == "H", -np.linalg.norm(x[i])))
    for a, b, c in itertools.combinations(order, 3):
        if np.linalg.norm(np.cross(x[b] - x[a], x[c] - x[a])) > COLLINEAR_MIN:
            return a, b, c
    raise ValueError("no three non-collinear atoms: linear molecules are not handled")


def _image_triples(frame: _Frame, ref: tuple[int, int, int]) -> list[tuple[int, int, int]]:
    """Every ordered triple of same-element atoms with the reference triple's pairwise distances within tol."""
    x, sym, tol = frame.x, frame.symbols, frame.tol
    a, b, c = ref
    dab, dac, dbc = np.linalg.norm(x[a] - x[b]), np.linalg.norm(x[a] - x[c]), np.linalg.norm(x[b] - x[c])
    n = len(x)
    out = []
    for a2, b2, c2 in itertools.permutations(range(n), 3):
        if (sym[a2], sym[b2], sym[c2]) != (sym[a], sym[b], sym[c]):
            continue
        if (abs(np.linalg.norm(x[a2] - x[b2]) - dab) <= tol and abs(np.linalg.norm(x[a2] - x[c2]) - dac) <= tol
                and abs(np.linalg.norm(x[b2] - x[c2]) - dbc) <= tol):
            out.append((a2, b2, c2))
    return out


def _candidates(frame: _Frame) -> list[np.ndarray]:
    """Orthogonal maps sending the reference triple onto each image triple, and their partners through the molecular plane."""
    ref = _reference_triple(frame)
    A = frame.x[list(ref)].T
    out = []
    for image in _image_triples(frame, ref):
        for R in _kabsch_both(A, frame.x[list(image)].T):
            out.append(R)
            if frame.normal is not None:
                S = frame.reflection()
                out += [S @ R, R @ S]
    return out


def point_group_ops(symbols: list[str], coords_bohr: np.ndarray, tol: float = 0.02) -> list[Operation]:
    """All orthogonal operations (R, perm) with R x_i ≈ x_perm[i] for same elements, within tol (bohr), about the coordinates' mean;
    the identity included. An operation is identified by its permutation and handedness; R is refitted over all atoms."""
    frame = _Frame.build(symbols, coords_bohr, tol)
    ops: list[Operation] = []
    keys: set[tuple[tuple[int, ...], bool]] = set()

    def accept(R: np.ndarray) -> bool:
        perm = _permutation(frame, R)
        if perm is None:
            return False
        improper = bool(np.linalg.det(R) < 0)
        key = (tuple(perm), improper)
        if key in keys:
            return False
        Rf = _refit(frame, perm, improper)
        if Rf is None:
            return False
        keys.add(key)
        ops.append((Rf, perm))
        return True

    for R in _candidates(frame):
        if np.allclose(R @ R.T, np.eye(3), atol=1e-6):
            accept(R)
    changed = True
    while changed:            # close under products; the groups here are small
        changed = False
        for (R1, _p1), (R2, _p2) in list(itertools.product(ops, ops)):
            changed |= accept(R1 @ R2)
    return ops


def rep_matrices(ops: list[Operation], n: int) -> list[np.ndarray]:
    """The 3n × 3n Cartesian representation matrix of every operation (R, perm)."""
    D = []
    for R, p in ops:
        M = np.zeros((3 * n, 3 * n))
        for i in range(n):
            M[3 * p[i]:3 * p[i] + 3, 3 * i:3 * i + 3] = R
        D.append(M)
    return D


def _check_group(ops: list[Operation], n: int) -> None:
    """Raises unless the operations' permutations are closed under composition: a geometry too far from its symmetry gives a subset of the
    group, and pairs read from it would be lost without notice."""
    keys = {tuple(p) for _R, p in ops}
    for (_R1, p1), (_R2, p2) in itertools.product(ops, ops):
        if tuple(p1[k] for k in p2) not in keys:
            raise ValueError(f"the {len(ops)} operations found are not a closed group (n = {n} atoms): the geometry is too far from its "
                             "symmetry for the tolerance")


def symmetrize(symbols: list[str], coords_bohr: np.ndarray) -> np.ndarray:
    """The geometry about its mean averaged over its group (x_i <- mean_g R_g^T x_perm_g(i)): an optimised geometry is symmetric only to its
    convergence, and a classification by the group needs exact invariance (benzene's corpus geometry gave a split pair without it). Raises
    when the operations found are not a closed group."""
    x = np.asarray(coords_bohr, float) - np.asarray(coords_bohr, float).mean(0)
    ops = point_group_ops(symbols, x)
    _check_group(ops, len(x))
    return np.mean([np.array([R.T @ x[p[i]] for i in range(len(x))]) for R, p in ops], axis=0)


def _exact_operations(symbols: list[str], coords_bohr: np.ndarray) -> list[Operation]:
    """The group's operations on the geometry symmetrised to a fixed point: averaging with refitted operations leaves a small asymmetry, so
    the geometry is symmetrised again until the exact tolerance finds as many operations as the symmetrising one; raises after
    SYMMETRIZE_PASSES or when they are not a closed group."""
    x = np.asarray(coords_bohr, float)
    for _ in range(SYMMETRIZE_PASSES):
        x = symmetrize(symbols, x)
        found, exact = point_group_ops(symbols, x), point_group_ops(symbols, x, tol=1e-6)
        if len(exact) == len(found):
            _check_group(exact, len(symbols))
            return exact
    raise ValueError(f"{len(exact)} operations at the exact tolerance against {len(found)} after {SYMMETRIZE_PASSES} symmetrising passes: "
                     "the geometry does not settle on its symmetry")


def degenerate_pairs(symbols: list[str], coords_bohr: np.ndarray, q: np.ndarray, omega_cm: np.ndarray) -> list[tuple[int, int]]:
    """The mode pairs (a, b), a < b, that carry a two-dimensional irreducible representation of the molecule's point group.

    q (3n x M) holds the orthonormal mass-weighted normal modes in columns, omega_cm their frequencies. The mode operator sum_i ω_i q_i q_iᵀ,
    averaged over the group, is the symmetrised Hessian: its eigenspaces are pure representations whatever noise mixed the modes, and a
    two-dimensional one appears as an exactly equal eigenvalue pair. Each such plane is carried by the two modes with the largest weight in it.
    Degeneracy is so read from the group: an asymmetric top has no pair however close two modes lie, and a symmetric top's pair counts as one
    however far the quadrature split it. Raises when q is not orthonormal, the operations are not a closed group or change between the
    symmetrising and the exact tolerance, a multiplet exceeds two, or a plane is not carried clearly by two modes. An equal eigenvalue pair
    on which the group acts reducibly is an accidental degeneracy and no pair."""
    q = np.asarray(q, float)
    if np.abs(q.T @ q - np.eye(q.shape[1])).max() > ORTHONORMAL_TOL:
        raise ValueError("the modes are not orthonormal columns")
    ops = _exact_operations(symbols, coords_bohr)
    D = rep_matrices(ops, len(symbols))
    omega = q @ np.diag(np.asarray(omega_cm, float)) @ q.T
    w, U = np.linalg.eigh(q.T @ (sum(d @ omega @ d.T for d in D) / len(D)) @ q)
    scale = np.abs(w).max()
    pairs: list[tuple[int, int]] = []
    i = 0
    while i < len(w):
        j = i + 1
        while j < len(w) and abs(w[j] - w[i]) < PAIR_GAP_REL * scale:
            j += 1
        if j - i > 2:
            raise ValueError(f"a multiplet of {j - i} at {w[i]:.3f} cm⁻¹: irreducible representations above dimension two are not handled")
        if j - i == 2 and _irreducible(q @ U[:, i:j], D):
            pairs.append(_carriers(U[:, i:j], w[i]))
        i = j
    used = [k for p in pairs for k in p]
    if len(used) != len(set(used)):
        raise ValueError(f"a mode carries two planes: {sorted(pairs)}")
    return sorted(pairs)


def _irreducible(plane: np.ndarray, D: list[np.ndarray]) -> bool:
    """Whether the group acts irreducibly on a plane (3n x 2, orthonormal columns): a real two-dimensional representation splits into two
    one-dimensional ones exactly when every operation acts on it as a symmetric matrix and all of them commute."""
    reps = [plane.T @ d @ plane for d in D]
    asymmetric = any(np.abs(r - r.T).max() > IRREDUCIBLE_TOL for r in reps)
    noncommuting = any(np.abs(r1 @ r2 - r2 @ r1).max() > IRREDUCIBLE_TOL for r1, r2 in itertools.product(reps, reps))
    return asymmetric or noncommuting


def _carriers(plane: np.ndarray, at_cm: float) -> tuple[int, int]:
    """The two modes (columns of the mode basis) with the largest weight in a symmetry plane given in mode coordinates; raises when either
    carries less than PAIR_WEIGHT_MIN. A plane's weights sum to two, so two carriers of at least a half leave every other mode below them."""
    weight = (plane ** 2).sum(1)
    a, b = (int(k) for k in np.argsort(weight)[::-1][:2])
    if weight[b] < PAIR_WEIGHT_MIN:
        raise ValueError(f"the plane at {at_cm:.3f} cm⁻¹ is not carried clearly by two modes (weights {np.round(np.sort(weight)[::-1][:3], 2)})")
    return min(a, b), max(a, b)
