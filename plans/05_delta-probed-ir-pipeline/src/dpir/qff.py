"""Quartic force field from displaced Hessians, with the two-route noise diagnostic, and VPT2 fundamentals.

Promoted from ``probes/qff_from_hessians.py`` (21 September 2026) under the plan-05 quality policy
(``QUALITY_POLICY.md``): same conventions, same numbers, split into pure functions so that every step can be
tested on a model potential with known constants.

Conventions
-----------
* Atomic units throughout the assembly; ``HARTREE_CM`` converts to cm⁻¹ at the end.
* ``F = M^-1/2 H M^-1/2`` (masses in m_e); ``q_i`` orthonormal eigenvectors of ``F`` after projecting out translations and
  rotations; ``ω_i²`` the eigenvalues.
* Reduced dimensionless normal coordinate ``Q_i`` with Cartesian displacement ``A[:, i] = M^-1/2 q_i / sqrt(ω_i)`` per unit
  ``Q_i``, so that ``H_QQ = Aᵀ H A`` has diagonal ``ω_i`` at the reference geometry.
* ``φ_ijk = ∂³V/∂Q_i∂Q_j∂Q_k`` and ``φ_iijj = ∂⁴V/∂Q_i²∂Q_j²`` by central differences of ``H_QQ``.

Noise diagnostic
----------------
Every off-diagonal semi-diagonal quartic constant has two independent finite-difference routes: displace ``j`` and read
``H_ii`` (route a), or displace ``i`` and read ``H_jj`` (route b). Their difference is a direct estimate of the numerical
error of that constant, at no extra cost. The routes are kept separately; the assembled constant is their mean.

Degenerate subspaces
--------------------
Inside an exactly degenerate subspace any orthonormal basis is a normal-mode basis, and the program that made the
displacements may have used a different one from the one ``eigh`` returns here. The displacement directions found in each
such subspace therefore define its basis: the analysis basis is rotated onto them by the nearest orthogonal matrix before
the files are assigned (21 September 2026: without this the T2 benzene set showed a spurious route disagreement of up to
47 cm⁻¹, identical for both partners of every pair).
"""

from __future__ import annotations

import glob
import itertools
import json
import os
from dataclasses import dataclass, field

import numpy as np

HARTREE_CM = 219474.6313632
AMU_ME = 1822.888486209
BOHR_ANGSTROM = 0.529177210903
ROT_CONST_AMU_A2_CM = 16.857629206  # h/(8π²c) in amu Å² cm⁻¹
MASS = {"H": 1.00782503223, "C": 12.0, "N": 14.00307400443, "O": 15.99491461957}
DEGENERACY_CM = 0.5  # modes closer than this (cm⁻¹) are treated as exactly degenerate


@dataclass
class HessianRecord:
    """One Hessian at one geometry (bohr, E_h/bohr²)."""

    file: str
    geom: np.ndarray  # (3N,)
    H: np.ndarray  # (3N, 3N)
    symbols: list[str]


@dataclass
class Harmonic:
    omega: np.ndarray  # (n,) E_h
    q: np.ndarray  # (3N, n) mass-weighted normal modes
    A: np.ndarray  # (3N, n) Cartesian displacement per unit reduced coordinate
    Minvh: np.ndarray  # (3N,) 1/sqrt(m) per Cartesian component

    @property
    def omega_cm(self) -> np.ndarray:
        return self.omega * HARTREE_CM


@dataclass
class QFF:
    """Assembled quartic force field in cm⁻¹, with both finite-difference routes kept."""

    omega_cm: np.ndarray  # (n,)
    phi3: np.ndarray  # (n, n, n) mean of the three routes
    cubic_spread: np.ndarray  # (n, n, n) max − min of the three routes
    phi4: np.ndarray  # (n, n) φ_iijj, mean of the two routes off the diagonal
    route_a: np.ndarray  # (n, n) displace j, read H_ii
    route_b: np.ndarray  # (n, n) displace i, read H_jj
    pairs: list[tuple[int, int]] = field(default_factory=list)  # exactly degenerate pairs

    @property
    def route_disagreement(self) -> np.ndarray:
        """|route a − route b| on the strict upper triangle, as a flat array."""
        return np.abs(self.route_a - self.route_b)[np.triu_indices(len(self.omega_cm), 1)]


# ----------------------------------------------------------------------------------------------------------------------
# input
# ----------------------------------------------------------------------------------------------------------------------


def load_results(cache_dir: str) -> list[HessianRecord]:
    """Read every qcschema AtomicResult with ``driver == "hessian"`` in ``cache_dir`` (other json files are skipped)."""
    recs = []
    for f in sorted(glob.glob(os.path.join(cache_dir, "*.json"))):
        with open(f, encoding="utf-8") as fh:
            d = json.load(fh)
        if not isinstance(d, dict) or d.get("driver") != "hessian" or "molecule" not in d:
            continue
        geom = np.array(d["molecule"]["geometry"], float).ravel()
        n = len(geom)
        recs.append(HessianRecord(os.path.basename(f), geom, np.array(d["return_result"], float).reshape(n, n), list(d["molecule"]["symbols"])))
    return recs


def reference_index(recs: list[HessianRecord]) -> int:
    """The record whose geometry is closest to the mean of all geometries (the displacements are symmetric ±δ)."""
    G = np.array([r.geom for r in recs])
    return int(np.argmin(np.linalg.norm(G - G.mean(0), axis=1)))


# ----------------------------------------------------------------------------------------------------------------------
# harmonic analysis
# ----------------------------------------------------------------------------------------------------------------------


def atomic_masses_me(symbols: list[str]) -> np.ndarray:
    return np.array([MASS[s] for s in symbols]) * AMU_ME


def translation_rotation_projector(geom: np.ndarray, m: np.ndarray) -> np.ndarray:
    """Projector (3N × 3N) onto the complement of the six mass-weighted translation/rotation vectors."""
    x = geom.reshape(-1, 3)
    com = (m[:, None] * x).sum(0) / m.sum()
    xc = x - com
    n = len(m)
    vecs = []
    for a in range(3):
        v = np.zeros((n, 3))
        v[:, a] = np.sqrt(m)
        vecs.append(v.ravel())
    for a in range(3):
        e = np.zeros(3)
        e[a] = 1.0
        v = np.cross(np.tile(e, (n, 1)), xc) * np.sqrt(m)[:, None]
        vecs.append(v.ravel())
    T = np.array(vecs).T
    if np.linalg.matrix_rank(T, tol=1e-8) < 6:
        raise NotImplementedError("linear molecule (five external degrees of freedom): not supported by this projector")
    Q, _ = np.linalg.qr(T)
    return np.eye(3 * n) - Q @ Q.T


def harmonic(H: np.ndarray, symbols: list[str], geom: np.ndarray) -> Harmonic:
    """Harmonic frequencies, mass-weighted modes and the reduced-coordinate displacement matrix ``A``."""
    m = atomic_masses_me(symbols)
    Minvh = np.repeat(1.0 / np.sqrt(m), 3)
    F = Minvh[:, None] * H * Minvh[None, :]
    P = translation_rotation_projector(geom, m)
    lam, q = np.linalg.eigh(P @ F @ P)
    order = np.argsort(lam)
    lam, q = lam[order], q[:, order]
    if (lam < -1e-8).any():
        raise ValueError(f"imaginary mode(s): eigenvalue(s) {lam[lam < -1e-8]} of the projected mass-weighted Hessian; not a minimum")
    vib = lam > 1e-8
    if vib.sum() != 3 * len(symbols) - 6:
        raise ValueError(f"{vib.sum()} vibrational modes found, expected {3 * len(symbols) - 6}: a mode below ≈ 22 cm⁻¹ would be dropped silently")
    omega = np.sqrt(lam[vib])
    q = fix_mode_signs(q[:, vib])
    A = (Minvh[:, None] * q) / np.sqrt(omega)[None, :]
    return Harmonic(omega, q, A, Minvh)


def fix_mode_signs(q: np.ndarray) -> np.ndarray:
    """Sign convention: the largest-magnitude component of every mode is positive. ``eigh`` leaves the sign to the
    linear-algebra backend (Windows and Linux numpy differed on the T2 set, 21 Sep 2026); cubic constants carry one sign
    per index, so without a convention the same input gives different φ_ijk on different machines."""
    q = q.copy()
    for j in range(q.shape[1]):
        if q[np.argmax(np.abs(q[:, j])), j] < 0:
            q[:, j] *= -1
    return q


def degenerate_groups(omega_cm: np.ndarray, tol_cm: float = DEGENERACY_CM) -> list[list[int]]:
    """Consecutive modes within ``tol_cm`` of each other, as index groups (singletons included)."""
    groups: list[list[int]] = []
    for i in range(len(omega_cm)):
        if groups and abs(omega_cm[i] - omega_cm[groups[-1][-1]]) < tol_cm:
            groups[-1].append(i)
        else:
            groups.append([i])
    return groups


# ----------------------------------------------------------------------------------------------------------------------
# assignment of displaced Hessians to (mode, sign)
# ----------------------------------------------------------------------------------------------------------------------


def assign_displacements(recs: list[HessianRecord], i0: int, A: np.ndarray, disp: float) -> dict[int, tuple[int, float, np.ndarray, float]]:
    """For every record but the reference: (mode, sign, dQ, residual) with dQ the displacement in reduced coordinates
    and residual = |dQ − sign·disp·e_mode|."""
    n = A.shape[1]
    pinvA = np.linalg.pinv(A)
    ref = recs[i0].geom
    out = {}
    for k, r in enumerate(recs):
        if k == i0:
            continue
        dQ = pinvA @ (r.geom - ref)
        i = int(np.argmax(np.abs(dQ)))
        s = float(np.sign(dQ[i]))
        out[k] = (i, s, dQ, float(np.linalg.norm(dQ - s * disp * np.eye(n)[i])))
    return out


def align_degenerate_subspaces(harm: Harmonic, recs: list[HessianRecord], i0: int, disp: float) -> tuple[Harmonic, dict, int]:
    """Rotate the analysis basis inside each exactly degenerate subspace onto the measured displacement directions.

    Returns the (possibly rotated) harmonic object, the final assignment and the number of subspaces aligned.
    A subspace is aligned only when exactly one '+' file is found per direction; otherwise it is left as is.
    """
    A, q = harm.A.copy(), harm.q.copy()
    asg = assign_displacements(recs, i0, A, disp)
    n_aligned = 0
    for S in [g for g in degenerate_groups(harm.omega_cm) if len(g) > 1]:
        cand = [v[2][S] for v in asg.values() if v[0] in S and v[1] > 0]
        if len(cand) != len(S):
            continue
        V = np.array([c / np.linalg.norm(c) for c in cand]).T  # columns: measured directions in the current basis of S
        U, _, Vt = np.linalg.svd(V)
        R = U @ Vt  # nearest orthogonal matrix
        A[:, S] = A[:, S] @ R
        q[:, S] = q[:, S] @ R
        # conventions inside the subspace, so that the result does not depend on the backend's starting basis:
        # sign as everywhere (largest component positive), order by the name of the file displaced along +direction
        sgn = np.array([1.0 if q[np.argmax(np.abs(q[:, i])), i] > 0 else -1.0 for i in S])
        q[:, S] *= sgn  # exact column operations on q and A alike: A keeps the probe's construction A_S·R
        A[:, S] *= sgn
        sub = assign_displacements(recs, i0, A, disp)
        plus_file = {}
        for k, (i, s, _dQ, _resid) in sub.items():
            if i in S and s > 0:
                plus_file[i] = min(recs[k].file, plus_file.get(i, recs[k].file))
        order = sorted(S, key=lambda i: plus_file.get(i, ""))
        A[:, S] = A[:, order]
        q[:, S] = q[:, order]
        n_aligned += 1
    out = Harmonic(harm.omega, q, A, harm.Minvh)
    if n_aligned:
        asg = assign_displacements(recs, i0, A, disp)
    return out, asg, n_aligned


# ----------------------------------------------------------------------------------------------------------------------
# force-field assembly
# ----------------------------------------------------------------------------------------------------------------------


def assemble_qff(omega_cm: np.ndarray, H0: np.ndarray, Hp: dict[int, np.ndarray], Hn: dict[int, np.ndarray], disp: float) -> QFF:
    """Central differences of the reduced-coordinate Hessians ``H0`` (reference), ``Hp[i]``/``Hn[i]`` (mode i displaced ±disp).

    All inputs in atomic units (E_h per reduced coordinate²); the result is in cm⁻¹.
    """
    n = len(omega_cm)
    d = disp
    phi3 = np.zeros((n, n, n))
    spread = np.zeros((n, n, n))
    for i, j, k in itertools.product(range(n), repeat=3):
        routes = ((Hp[i][j, k] - Hn[i][j, k]) / (2 * d), (Hp[j][k, i] - Hn[j][k, i]) / (2 * d), (Hp[k][i, j] - Hn[k][i, j]) / (2 * d))
        phi3[i, j, k] = np.mean(routes)
        spread[i, j, k] = max(routes) - min(routes)
    phi4 = np.zeros((n, n))
    route_a = np.zeros((n, n))
    route_b = np.zeros((n, n))
    for i in range(n):
        phi4[i, i] = (Hp[i][i, i] + Hn[i][i, i] - 2 * H0[i, i]) / d**2
        for j in range(n):
            if i == j:
                continue
            route_a[i, j] = (Hp[j][i, i] + Hn[j][i, i] - 2 * H0[i, i]) / d**2  # displace j, read H_ii
            route_b[i, j] = (Hp[i][j, j] + Hn[i][j, j] - 2 * H0[j, j]) / d**2  # displace i, read H_jj
            phi4[i, j] = 0.5 * (route_a[i, j] + route_b[i, j])
    # neighbouring modes within the degeneracy tolerance, pairwise (as the probe did; a triply degenerate group gives two
    # overlapping pairs — the symmetry averaging below is then order-dependent, an open item in QUALITY_POLICY.md)
    pairs = [(i, i + 1) for i in range(n - 1) if abs(omega_cm[i] - omega_cm[i + 1]) < DEGENERACY_CM]
    return QFF(np.array(omega_cm, float), phi3 * HARTREE_CM, spread * HARTREE_CM, phi4 * HARTREE_CM, route_a * HARTREE_CM, route_b * HARTREE_CM, pairs)


def qff_from_records(recs: list[HessianRecord], disp: float) -> tuple[QFF, Harmonic, HessianRecord, dict]:
    """The whole chain: reference, harmonic analysis, degenerate-subspace alignment, assignment, assembly."""
    i0 = reference_index(recs)
    ref = recs[i0]
    harm = harmonic(ref.H, ref.symbols, ref.geom)
    harm, asg, n_aligned = align_degenerate_subspaces(harm, recs, i0, disp)
    n = len(harm.omega)
    Hp: dict[int, np.ndarray] = {}
    Hn: dict[int, np.ndarray] = {}
    for k, (i, s, _dQ, _resid) in asg.items():
        if s == 0:
            raise ValueError(f"{recs[k].file}: zero displacement from the reference (duplicate reference file?)")
        slot = Hp if s > 0 else Hn
        if i in slot:
            raise ValueError(f"{recs[k].file}: mode {i} {'+' if s > 0 else '−'} is already taken; two files map to the same displacement")
        slot[i] = recs[k].H
    missing = [i for i in range(n) if i not in Hp or i not in Hn]
    if missing:
        raise ValueError(f"modes without a ± pair: {missing}")
    A = harm.A
    toQ = lambda H: A.T @ H @ A  # noqa: E731
    qff = assemble_qff(harm.omega_cm, toQ(ref.H), {i: toQ(h) for i, h in Hp.items()}, {i: toQ(h) for i, h in Hn.items()}, disp)
    info = {"reference_file": ref.file, "assignment_residual_max": max(v[3] for v in asg.values()), "subspaces_aligned": n_aligned}
    return qff, harm, ref, info


def symmetry_average(phi4: np.ndarray, pairs: list[tuple[int, int]]) -> np.ndarray:
    """Average φ_aa,jj with φ_bb,jj (and φ_aaaa with φ_bbbb) for every exactly degenerate pair (a, b)."""
    out = phi4.copy()
    n = len(phi4)
    for a, b in pairs:
        for j in range(n):
            if j in (a, b):
                continue
            m = 0.5 * (phi4[a, j] + phi4[b, j])
            out[a, j] = out[j, a] = out[b, j] = out[j, b] = m
        m = 0.5 * (phi4[a, a] + phi4[b, b])
        out[a, a] = out[b, b] = m
    return out


# ----------------------------------------------------------------------------------------------------------------------
# rotational constants and Coriolis coupling
# ----------------------------------------------------------------------------------------------------------------------


def rotational_constants(geom: np.ndarray, symbols: list[str]) -> np.ndarray:
    """Equilibrium rotational constants (cm⁻¹), ascending moments of inertia → descending constants."""
    m = np.array([MASS[s] for s in symbols])
    x = geom.reshape(-1, 3) * BOHR_ANGSTROM
    x = x - (m[:, None] * x).sum(0) / m.sum()
    inertia = np.zeros((3, 3))
    for mi, r in zip(m, x, strict=True):
        inertia += mi * (np.dot(r, r) * np.eye(3) - np.outer(r, r))
    return ROT_CONST_AMU_A2_CM / np.linalg.eigvalsh(inertia)


def coriolis_zeta(q: np.ndarray, symbols: list[str]) -> np.ndarray:
    """Coriolis coupling constants ζ^a_ij from the mass-weighted normal modes, shape (3, n, n)."""
    n = q.shape[1]
    Q = q.reshape(len(symbols), 3, n)
    z = np.zeros((3, n, n))
    for a, (b, c) in enumerate(((1, 2), (2, 0), (0, 1))):
        z[a] = np.einsum("ki,kj->ij", Q[:, b, :], Q[:, c, :]) - np.einsum("ki,kj->ij", Q[:, c, :], Q[:, b, :])
    return z


# ----------------------------------------------------------------------------------------------------------------------
# VPT2
# ----------------------------------------------------------------------------------------------------------------------


def find_fermi_resonances(w: np.ndarray, p3: np.ndarray, window: float, min_k: float) -> list[tuple[int, tuple[int, int]]]:
    """Resonances (k, (i, j)) with |ω_i + ω_j − ω_k| < window and strength K above ``min_k`` (all in cm⁻¹)."""
    n = len(w)
    fermi = []
    for i in range(n):
        for k in range(n):
            dw = 2 * w[i] - w[k]
            if i != k and abs(dw) < window and dw != 0 and p3[i, i, k] ** 4 / (256 * abs(dw) ** 3) >= min_k:
                fermi.append((k, (i, i)))
        for j in range(i + 1, n):
            for k in range(n):
                dw = w[i] + w[j] - w[k]
                if k not in (i, j) and abs(dw) < window and p3[i, j, k] ** 4 / (64 * abs(dw) ** 3) >= min_k:
                    fermi.append((k, (i, j)))
    return fermi


def vpt2(w: np.ndarray, p3: np.ndarray, p4: np.ndarray, B: np.ndarray, zeta: np.ndarray, fermi_window: float = 200.0, fermi_min_k: float = 0.0):
    """Anharmonic constants χ_ij and fundamentals ν_i (Mills 1972; the expressions pyVPT2 implements), with the resonant
    denominators deperturbed inside ``fermi_window``. Everything in cm⁻¹; ``B`` (3,) rotational constants, ``zeta`` (3, n, n).

    Returns (nu, chi, fermi).
    """
    n = len(w)
    fermi = find_fermi_resonances(w, p3, fermi_window, fermi_min_k)
    fset = set(fermi)
    chi = np.zeros((n, n))
    for i in range(n):
        s = p4[i, i] / 16.0
        for k in range(n):
            if (k, (i, i)) in fset:
                s -= p3[i, i, k] ** 2 / 32.0 * (1.0 / (2 * w[i] + w[k]) + 4.0 / w[k])
            else:
                s -= p3[i, i, k] ** 2 * (8 * w[i] ** 2 - 3 * w[k] ** 2) / (16 * w[k] * (4 * w[i] ** 2 - w[k] ** 2))
        chi[i, i] = s
        for j in range(n):
            if j == i:
                continue
            s = p4[i, j] / 4.0 + sum(B[a] * zeta[a, i, j] ** 2 for a in range(3)) * (w[i] / w[j] + w[j] / w[i])
            for k in range(n):
                s -= p3[i, i, k] * p3[j, j, k] / (4 * w[k])
                if (k, (i, j)) in fset or (k, (j, i)) in fset:
                    dd = (1 / (w[i] + w[j] + w[k]) + 1 / (-w[i] + w[j] + w[k]) + 1 / (w[i] - w[j] + w[k])) / -2
                elif (i, (j, k)) in fset or (i, (k, j)) in fset:
                    dd = (1 / (w[i] + w[j] + w[k]) - 1 / (w[i] + w[j] - w[k]) + 1 / (w[i] - w[j] + w[k])) / -2
                elif (j, (i, k)) in fset or (j, (k, i)) in fset:
                    dd = (1 / (w[i] + w[j] + w[k]) - 1 / (w[i] + w[j] - w[k]) + 1 / (-w[i] + w[j] + w[k])) / -2
                else:
                    D = (w[i] + w[j] - w[k]) * (w[i] + w[j] + w[k]) * (w[i] - w[j] + w[k]) * (w[i] - w[j] - w[k])
                    dd = 2 * w[k] * (w[i] ** 2 + w[j] ** 2 - w[k] ** 2) / D
                s += p3[i, j, k] ** 2 * dd / 4.0
            chi[i, j] = s
    nu = np.array([w[i] + 2 * chi[i, i] + 0.5 * sum(chi[i, j] for j in range(n) if j != i) for i in range(n)])
    return nu, chi, fermi


# ----------------------------------------------------------------------------------------------------------------------
# report (the probe's markdown, unchanged in content)
# ----------------------------------------------------------------------------------------------------------------------


def report(cache_dir: str, recs, qff: QFF, harm: Harmonic, ref: HessianRecord, info: dict, disp: float,
           fermi_window: float, fermi_min_k: float, pyvpt2_json: str | None = None):
    """Markdown report plus the arrays to save; returns (text, arrays)."""
    n = len(qff.omega_cm)
    if n < 2:
        raise ValueError("the two-route diagnostic needs at least two modes")
    w = qff.omega_cm
    in_pair = {i for p in qff.pairs for i in p}
    diff = np.abs(qff.route_a - qff.route_b)
    iu = np.triu_indices(n, 1)
    lines = [
        f"# Quartic force field from {len(recs)} displaced Hessians — {cache_dir}",
        "",
        f"Reference file `{ref.file}`; {n} vibrational modes; displacement {disp} in reduced coordinates; "
        f"assignment residual max {info['assignment_residual_max']:.2e}.",
        "Harmonic ω (cm⁻¹): " + ", ".join(f"{x:.1f}" for x in w),
        "",
        "## Noise diagnostics",
        "",
        "Off-diagonal semi-diagonal quartic constants φ_iijj have two independent finite-difference routes (displace j and read H_ii; "
        "displace i and read H_jj). Their difference is a direct estimate of the numerical error of that constant. Exactly degenerate "
        "pairs (a, b) must give equal φ_aa,jj and φ_bb,jj for every totally symmetric j; their difference is a second estimate.",
        "",
        f"- route disagreement |φ_iijj(a) − φ_iijj(b)|: median {np.median(diff[iu]):.1f}, 90th percentile {np.percentile(diff[iu], 90):.1f}, "
        f"max {diff[iu].max():.1f} cm⁻¹ (max |φ_iijj| {np.abs(qff.phi4[iu]).max():.1f})",
        f"- cubic route spread (max − min of the three routes): median {np.median(qff.cubic_spread):.2f}, max {qff.cubic_spread.max():.1f} cm⁻¹",
    ]
    ts = [i for i in range(n) if abs(qff.phi3[i, i, i]) > 5 and i not in in_pair]
    lines += [
        f"- totally symmetric modes (|φ_iii| > 5 cm⁻¹, non-degenerate): {[(i, round(float(w[i]), 1)) for i in ts]}",
        "",
        "| degenerate pair (ω) | j (ω) | φ_aa,jj | φ_bb,jj | difference | route disagreement a / b |",
        "|---|---|---|---|---|---|",
    ]
    for a, b in qff.pairs:
        for j in ts:
            lines.append(f"| ({a},{b}) {w[a]:.0f} | {j} {w[j]:.0f} | {qff.phi4[a, j]:+.1f} | {qff.phi4[b, j]:+.1f} | "
                         f"{abs(qff.phi4[a, j] - qff.phi4[b, j]):.1f} | {diff[a, j]:.1f} / {diff[b, j]:.1f} |")
    phi4s = symmetry_average(qff.phi4, qff.pairs)
    B = rotational_constants(ref.geom, ref.symbols)
    zeta = coriolis_zeta(harm.q, ref.symbols)
    nu_raw, chi_raw, fermi = vpt2(w, qff.phi3, qff.phi4, B, zeta, fermi_window, fermi_min_k)
    nu_sym, chi_sym, _ = vpt2(w, qff.phi3, phi4s, B, zeta, fermi_window, fermi_min_k)
    lines += [
        "",
        f"## VPT2 fundamentals (deperturbation window {fermi_window} cm⁻¹, min K {fermi_min_k}; {len(fermi)} resonances deperturbed; "
        "polyad diagonalisation not applied)",
        "",
        "| mode | ω | ν raw quartics | ν − ω | ν symmetry-averaged quartics | ν − ω | pyVPT2 ν | pair |",
        "|---|---|---|---|---|---|---|---|",
    ]
    py = None
    if pyvpt2_json and os.path.exists(pyvpt2_json):
        with open(pyvpt2_json, encoding="utf-8") as fh:
            pj = json.load(fh)
        pw = np.array(pj["omega"])
        pn = np.array(pj["nu"])
        keep = pw > 1.0
        pw, pn = pw[keep], pn[keep]
        py = [pn[int(np.argmin(np.abs(pw - x)))] for x in w]
    for i in range(n):
        tag = "" if i not in in_pair else "e"
        pycol = f"{py[i]:.1f}" if py else "—"
        lines.append(f"| {i} | {w[i]:.1f} | {nu_raw[i]:.1f} | {nu_raw[i] - w[i]:+.1f} | {nu_sym[i]:.1f} | {nu_sym[i] - w[i]:+.1f} | {pycol} | {tag} |")
    arrays = dict(omega_cm=w, phi_ijk=qff.phi3, phi_iijj=qff.phi4, phi_iijj_route_a=qff.route_a, phi_iijj_route_b=qff.route_b, phi_iijj_sym=phi4s,
                  chi_raw=chi_raw, chi_sym=chi_sym, nu_raw=nu_raw, nu_sym=nu_sym)
    return "\n".join(lines) + "\n", arrays


def main(argv=None):
    import argparse

    from dpir.provenance import provenance_block

    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cache_dir")
    ap.add_argument("--disp", type=float, default=0.05)
    ap.add_argument("--pyvpt2-json", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--fermi-window", type=float, default=200.0, help="cm-1; resonances with |Δ| below it are deperturbed")
    ap.add_argument("--fermi-min-k", type=float, default=0.0, help="cm-1; strength threshold K = φ⁴/(64Δ³) (type 2) or /(256Δ³) (type 1)")
    args = ap.parse_args(argv)
    recs = load_results(args.cache_dir)
    qff, harm, ref, info = qff_from_records(recs, args.disp)
    txt, arrays = report(args.cache_dir, recs, qff, harm, ref, info, args.disp, args.fermi_window, args.fermi_min_k, args.pyvpt2_json)
    txt += "\n" + provenance_block()
    out = args.out or os.path.join(os.path.dirname(args.cache_dir.rstrip("/\\")), "qff_report.md")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(txt)
    print(txt)
    np.savez(out[:-3] + ".npz" if out.endswith(".md") else out + ".npz", **arrays)


if __name__ == "__main__":
    main()
