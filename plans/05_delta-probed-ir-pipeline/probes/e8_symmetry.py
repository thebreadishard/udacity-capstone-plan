"""Symmetry-reduced finite-difference Hessians (24 September 2026).

A Hessian obeys H[P(i), P(k)] = R H[i, k] Rᵀ for every point-group operation (R, P) — R the 3 × 3 orthogonal matrix, P the atom permutation
it induces. So the block rows of one atom per orbit determine the whole Hessian: displace only the symmetry-unique atoms (3 directions, ±),
build their block rows by central differences, and copy them onto the equivalent atoms with R · Rᵀ. Rows reached by more than one operation
give a consistency check (their spread is a noise measure of the gradients).

Point-group detection (since 12 Nov 2026 in src/dpir/symmetry.py, imported here) works from the geometry alone: candidate operations
are the orthogonal maps that send three non-collinear reference
atoms onto same-element atoms with the same pairwise distances (Kabsch), kept when they map every atom onto a same-element atom within a
tolerance; for planar molecules the reflection through the plane and its products are added. No character tables, no labels — only what the
reconstruction needs.

Functions: point_group_ops, rep_matrices, symmetrize, degenerate_pairs, orbits, unique_displacements, reconstruct, self_check.
Validation: python e8_symmetry.py --validate (benzene's 72 CCSD(T) gradients → 12; naphthalene's analytic B3LYP Hessian from the
corpus → 30 rows; both must reproduce the full matrix).
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
try:
    from dpir.symmetry import degenerate_pairs, point_group_ops, rep_matrices, symmetrize  # noqa: F401  (re-exported: probes import them from here)
except ImportError as exc:   # a flat server copy without the package (bootstrap_anchors_cpx62.sh and the CCX53 row scripts ship it so)
    raise ImportError("e8_symmetry takes its operations from src/dpir/symmetry.py since 12 Nov 2026 (TASKS 204): ship "
                      "src/dpir/__init__.py and src/dpir/symmetry.py as dpir/ beside it") from exc

BOHR = 0.529177210903


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


def reconstruct_apt(dip_rows, ops, n):
    """dip_rows: {atom i: (3, 3) array D_i with D_i[x, t] = ∂μ_t/∂R_{i,x}} for the representatives. Under (R, perm): D_perm(i) = R D_i Rᵀ (the displacement
    direction and the dipole both rotate). Returns P (3 × 3n) with P[t, 3k + x] = ∂μ_t/∂R_{k,x}, as probes/dipole_derivs_fd.py stores it, and the spread of
    atoms reached by several operations (3 Oct 2026, odds lever 4)."""
    D = np.full((n, 3, 3), np.nan); spread = 0.0; counts = {}
    for i, Di in dip_rows.items():
        Di = np.asarray(Di, float).reshape(3, 3)
        for R, p in ops:
            j = p[i]; new = R @ Di @ R.T
            if np.isnan(D[j]).any():
                D[j] = new; counts[j] = 1
            else:
                spread = max(spread, float(np.abs(D[j] - new).max()))
                D[j] = (D[j] * counts[j] + new) / (counts[j] + 1); counts[j] += 1
    if np.isnan(D).any():
        raise ValueError(f"atoms not reached by the group from the representatives: {sorted(int(k) for k in np.where(np.isnan(D).any((1, 2)))[0])}")
    return D.transpose(2, 0, 1).reshape(3, 3 * n), spread


def apt_self_check(P, ops, n):
    """Max |P − R P (P_perm ⊗ R)ᵀ| over the group: how symmetric the reconstructed APT is."""
    D = P.reshape(3, n, 3).transpose(1, 2, 0)            # (n, x, t)
    worst = 0.0
    for R, p in ops:
        for k in range(n):
            worst = max(worst, float(np.abs(D[p[k]] - R @ D[k] @ R.T).max()))
    return worst


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
