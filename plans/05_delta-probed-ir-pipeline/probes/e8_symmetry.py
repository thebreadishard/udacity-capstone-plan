"""Symmetry-reduced finite-difference Hessians (24 September 2026).

A Hessian obeys H[P(i), P(k)] = R H[i, k] Rᵀ for every point-group operation (R, P) — R the 3 × 3 orthogonal matrix, P the atom permutation
it induces. So the block rows of one atom per orbit determine the whole Hessian: displace only the symmetry-unique atoms (3 directions, ±),
build their block rows by central differences, and copy them onto the equivalent atoms with R · Rᵀ. Rows reached by more than one operation
give a consistency check (their spread is a noise measure of the gradients).

Point-group detection works from the geometry alone: candidate operations are the orthogonal maps that send three non-collinear reference
atoms onto same-element atoms with the same pairwise distances (Kabsch), kept when they map every atom onto a same-element atom within a
tolerance; for planar molecules the reflection through the plane and its products are added. No character tables, no labels — only what the
reconstruction needs.

Functions: point_group_ops, orbits, unique_displacements, reconstruct, self_check. Validation: python e8_symmetry.py --validate (benzene's 72
CCSD(T) gradients → 12; naphthalene's analytic B3LYP Hessian from the corpus → 30 rows; both must reproduce the full matrix).
"""
import argparse
import itertools
import json
import os

import numpy as np

BOHR = 0.529177210903


def _kabsch(A, B):
    """Orthogonal R (proper or improper) minimising |R A − B| for 3 × m point sets A, B (columns), both already centred."""
    U, _, Vt = np.linalg.svd(B @ A.T)
    return U @ Vt


def point_group_ops(symbols, coords_bohr, tol=0.02):
    """All orthogonal operations (R, perm) with R x_i ≈ x_perm[i] and same elements. tol in bohr. Includes the identity."""
    x = np.asarray(coords_bohr, float); masses_like = np.ones(len(x)); com = x.mean(0); x = x - com; n = len(x)
    sym = list(symbols)
    ops = []

    # planar? normal vector
    ev, R0 = np.linalg.eigh(x.T @ x); normal = R0[:, 0] if ev[0] < 1e-6 * max(ev[-1], 1.0) else None
    keys = set()

    def accept(R):
        """Return (R_refit, perm) for a new operation, else None. Identity of an operation = (perm, proper/improper); R is refit over all atoms."""
        y = x @ R.T; perm = []
        for i in range(n):
            d = np.linalg.norm(x - y[i], axis=1); j = int(np.argmin(d))
            if d[j] > tol or sym[j] != sym[i]:
                return None
            perm.append(j)
        if len(set(perm)) != n:
            return None
        improper = np.linalg.det(R) < 0
        key = (tuple(perm), bool(improper))
        if key in keys:
            return None
        Rf = _kabsch(x.T, x[perm].T)                        # best proper or improper map over all atoms
        if (np.linalg.det(Rf) < 0) != improper:
            if normal is None:
                return None
            Rf = (np.eye(3) - 2 * np.outer(normal, normal)) @ Rf
        if np.abs(x @ Rf.T - x[perm]).max() > tol:
            return None
        keys.add(key)
        return Rf, perm

    # reference triple: three non-collinear atoms (prefer heavy)
    order = sorted(range(n), key=lambda i: (sym[i] == "H", -np.linalg.norm(x[i])))
    ref = None
    for a, b, c in itertools.combinations(order, 3):
        if np.linalg.norm(np.cross(x[b] - x[a], x[c] - x[a])) > 1e-3:
            ref = (a, b, c); break
    a, b, c = ref; dab, dac, dbc = (np.linalg.norm(x[a] - x[b]), np.linalg.norm(x[a] - x[c]), np.linalg.norm(x[b] - x[c]))
    cands = []
    for a2 in range(n):
        if sym[a2] != sym[a]:
            continue
        for b2 in range(n):
            if b2 == a2 or sym[b2] != sym[b] or abs(np.linalg.norm(x[a2] - x[b2]) - dab) > tol:
                continue
            for c2 in range(n):
                if c2 in (a2, b2) or sym[c2] != sym[c] or abs(np.linalg.norm(x[a2] - x[c2]) - dac) > tol or abs(np.linalg.norm(x[b2] - x[c2]) - dbc) > tol:
                    continue
                A = np.array([x[a], x[b], x[c]]).T; B = np.array([x[a2], x[b2], x[c2]]).T
                R = _kabsch(A, B); cands.append(R)
                if normal is not None:                      # the improper partner through the molecular plane
                    S = np.eye(3) - 2 * np.outer(normal, normal); cands.append(S @ R); cands.append(R @ S)
    for R in cands:
        if np.allclose(R @ R.T, np.eye(3), atol=1e-6):
            r = accept(R)
            if r is not None:
                ops.append(r)
    # close under products (groups here are small; identity of an operation = its key)
    changed = True
    while changed:
        changed = False
        for (R1, p1), (R2, p2) in list(itertools.product(ops, ops)):
            r = accept(R1 @ R2)
            if r is not None:
                ops.append(r); changed = True
    return ops


def orbits(ops, n):
    """Atom orbits under the group; returns a list of sorted atom lists and the representative (smallest index) of each."""
    seen = set(); out = []
    for i in range(n):
        if i in seen:
            continue
        orb = sorted({p[i] for _, p in ops}); out.append(orb); seen |= set(orb)
    return out


def unique_displacements(ops, n):
    """Cartesian indices k = 3 * atom + xyz to displace: the three directions of one representative atom per orbit."""
    reps = [orb[0] for orb in orbits(ops, n)]
    return [3 * i + d for i in reps for d in range(3)], reps


def reconstruct(block_rows, ops, n):
    """block_rows: {atom i: (3, 3n) array of Hessian rows of atom i} for the representatives. Returns H (3n × 3n), and the spread of rows reached
    by several operations (max abs difference), as the consistency measure."""
    H = np.full((3 * n, 3 * n), np.nan); spread = 0.0; counts = {}
    for i, rows in block_rows.items():
        Bi = rows.reshape(3, n, 3)                       # rows: direction of atom i; columns: atom k, xyz
        for R, p in ops:
            j = p[i]; new = np.zeros((3, n, 3))
            for k in range(n):
                new[:, p[k], :] = R @ Bi[:, k, :] @ R.T
            new = new.reshape(3, 3 * n)
            if np.isnan(H[3 * j:3 * j + 3]).any():
                H[3 * j:3 * j + 3] = new; counts[j] = 1
            else:
                spread = max(spread, float(np.abs(H[3 * j:3 * j + 3] - new).max()))
                H[3 * j:3 * j + 3] = (H[3 * j:3 * j + 3] * counts[j] + new) / (counts[j] + 1); counts[j] += 1
    if np.isnan(H).any():
        missing = sorted({k // 3 for k in np.where(np.isnan(H).any(1))[0]})
        raise ValueError(f"atoms not reached by the group from the representatives: {missing}")
    return 0.5 * (H + H.T), spread


def self_check(H, ops, n):
    """Max |H − (P⊗R) H (P⊗R)ᵀ| over the group: how symmetric the reconstructed matrix is (should be ~0 by construction)."""
    worst = 0.0
    for R, p in ops:
        M = np.zeros((3 * n, 3 * n))
        for k in range(n):
            M[3 * p[k]:3 * p[k] + 3, 3 * k:3 * k + 3] = R
        worst = max(worst, float(np.abs(H - M @ H @ M.T).max()))
    return worst


# ------------------------------------------------------------------------------------------------------------- validation
def _freqs(H, masses):
    sm = np.sqrt(np.repeat(masses, 3)); w = np.linalg.eigvalsh(H / np.outer(sm, sm))
    au2cm = 219474.6313705; amu2au = 1822.888486209
    f = np.sqrt(np.abs(w) / amu2au) * au2cm
    return np.sort(np.where(w < 0, -f, f))


def validate():
    here = os.path.dirname(os.path.abspath(__file__))
    # 1. benzene: 72 CCSD(T)/cc-pVDZ FD gradients (E8) → reconstruct from the representatives' 12
    d = os.path.join(here, "results_m1", "e8_benzene_ccpvdz")
    g = json.load(open(os.path.join(here, "..", "modules", "05_support_predictor", "corpus", "molecules", "A_8448043181", "geometry.json")))
    sym, x, m = g["symbols"], np.array(g["coords_bohr"]), np.array(g["masses_amu"]); n = len(sym)
    ops = point_group_ops(sym, x); orb = orbits(ops, n); ks, reps = unique_displacements(ops, n)
    print(f"benzene: {len(ops)} operations, orbits {orb}, {len(ks)} displacements ({2 * len(ks)} gradients) instead of {6 * n}")
    step = float(np.load(os.path.join(d, "hessian_ccsd_t.npz"))["step"])
    def row(k):
        gp = np.load(os.path.join(d, "grads", f"grad_{k:02d}_p.npy")).ravel(); gm = np.load(os.path.join(d, "grads", f"grad_{k:02d}_m.npy")).ravel()
        return (gp - gm) / (2 * step)
    block_rows = {i: np.array([row(3 * i + dd) for dd in range(3)]) for i in reps}
    Hs, spread = reconstruct(block_rows, ops, n)
    Hfull = np.load(os.path.join(d, "hessian_ccsd_t.npz"))["H_raw"]
    print(f"  spread of multiply-reached rows {spread:.2e} a.u.; max|H_sym − H_full| {np.abs(Hs - Hfull).max():.2e} a.u. (FD asymmetry of the full one 2.7e-4); "
          f"self-check {self_check(Hs, ops, n):.1e}")
    fs, ff = _freqs(Hs, m)[6:], _freqs(Hfull, m)[6:]
    print(f"  frequencies: max |Δ| {np.abs(fs - ff).max():.2f} cm-1; degenerate-pair splits sym {max(abs(fs[i] - fs[i + 1]) for i in (0, 2, 4)):.2f} vs full {max(abs(ff[i] - ff[i + 1]) for i in (0, 2, 4)):.2f}")
    # 2. naphthalene: corpus analytic B3LYP Hessian → block rows of the representatives → reconstruct → must equal the analytic matrix
    d2 = os.path.join(here, "..", "modules", "05_support_predictor", "corpus", "molecules", "A_01f3186607")
    g = json.load(open(os.path.join(d2, "geometry.json"))); sym, x, m = g["symbols"], np.array(g["coords_bohr"]), np.array(g["masses_amu"]); n = len(sym)
    ops = point_group_ops(sym, x); orb = orbits(ops, n); ks, reps = unique_displacements(ops, n)
    print(f"naphthalene: {len(ops)} operations, orbits {orb}, {len(ks)} displacements ({2 * len(ks)} gradients) instead of {6 * n}")
    H = np.load(os.path.join(d2, "hessian_b3lyp.npz"))["H_raw"]
    Hs, spread = reconstruct({i: H[3 * i:3 * i + 3] for i in reps}, ops, n)
    print(f"  spread {spread:.2e}; max|H_sym − H_analytic| {np.abs(Hs - H).max():.2e} a.u.; freq max |Δ| {np.abs(_freqs(Hs, m) - _freqs(H, m)).max():.3f} cm-1")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--validate", action="store_true"); a = ap.parse_args()
    if a.validate:
        validate()
