"""Pattern-consistent ΔF targets for the hybrid head (1 Oct 2026, Sherlock day, lever 4).

Finding behind it: the pattern term's target was the projected truth B⁺ᵀ ΔH B⁺ read on the pattern. Reconstructed with zeros off the pattern that
target leaves 0.38–0.42 of the ring couplings on naphthalene and 2-methylnaphthalene — exactly where the single-molecule overfits (0.41, 0.40)
and the pool read-outs of every head (0.37–0.43) stopped. The best pattern-supported ΔF is the least-squares fit

    min over symmetric X supported on the pattern of ‖ D (Bᵀ X B − ΔH) D ‖_F ,   D = diag(m^-1/2)  (the registered mass weighting),

whose ring-coupling ratio on the same molecules is 0.02–0.09 (`probes/rungC_pattern_ceiling.py`). It is solved as the dense linear least-squares
problem it is: one column per pattern pair p = (i ≤ j), the column being vec(D (b_i b_jᵀ + b_j b_iᵀ) D) (b_i = row i of B), by LAPACK's SVD route
(`scipy.linalg.lstsq`, driver gelsd, its default rank cutoff; the minimum-norm solution where the redundant internals leave freedom). Three routes that
looked cheaper were tried first and rejected with numbers: conjugate gradients on the normal equations did not converge in 2,000 iterations; a
Cholesky of the normal matrix with a 1e-10 ridge lost the small-eigenvalue directions (naphthalene residual 0.088 against 0.036) — the normal
equations square the condition number of the Wilson matrix; and the pivoted-QR driver with a 1e-10 cutoff left 0.022 on benzene against 0.011 — the
near-redundant directions carry signal. Seconds to a few minutes per molecule; `cached_pattern_ls_target` keeps the result on disk keyed by a hash of
(ΔH, B, mask), so a training run pays it once (`probes/rungC_ls_targets_build.py` fills the cache ahead). Counterpart: an independent dense fit in
`tests/test_rungC_targets.py` (same objective to 1e-6 on benzene, same reconstruction to 1e-7 on a full-rank system).
"""
import hashlib
from pathlib import Path

import numpy as np
import scipy.linalg

AMU2AU = 1822.888486209


def _design_matrix(B: np.ndarray, W: np.ndarray, I: np.ndarray, J: np.ndarray, rows: tuple) -> np.ndarray:
    """(rows, P): column p = the upper triangle of W ⊙ (b_i b_jᵀ + b_j b_iᵀ) — for i = j the single outer product (X_ii enters Bᵀ X B once)."""
    A = np.empty((len(rows[0]), len(I)))
    for p, (i, j) in enumerate(zip(I, J, strict=True)):
        E = np.outer(B[i], B[j])
        if i != j:
            E = E + E.T
        A[:, p] = (E * W)[rows]
    return A


def pattern_ls_target(dH: np.ndarray, B: np.ndarray, masses_amu: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """The mass-weighted least-squares ΔF supported on `mask` (K × K boolean, symmetric) such that Bᵀ ΔF B ≈ ΔH. Returns ΔF (K × K).
    Both sides are symmetric, so the Frobenius objective is taken over the upper triangle with weight √2 off the diagonal — half the rows, the same
    minimiser."""
    mask = np.asarray(mask, bool)
    if not np.array_equal(mask, mask.T):
        raise ValueError("the pattern mask must be symmetric")
    d = 1.0 / np.sqrt(np.repeat(np.asarray(masses_amu, float) * AMU2AU, 3))
    n = B.shape[1]
    rows = np.triu_indices(n)
    W = np.outer(d, d) * np.where(np.eye(n, dtype=bool), 1.0, np.sqrt(2.0))
    I, J = np.where(np.triu(mask))
    A = _design_matrix(B, W, I, J, rows)
    x = scipy.linalg.lstsq(A, (dH * W)[rows], lapack_driver="gelsd", check_finite=False, overwrite_a=True)[0]
    X = np.zeros((B.shape[0], B.shape[0]))
    X[I, J] = x
    X[J, I] = x
    return X


def weighted_residual(dH: np.ndarray, B: np.ndarray, masses_amu: np.ndarray, X: np.ndarray) -> float:
    """‖D (Bᵀ X B − ΔH) D‖_F / ‖D ΔH D‖_F — the fraction of the mass-weighted Cartesian power a ΔF leaves."""
    d = 1.0 / np.sqrt(np.repeat(np.asarray(masses_amu, float) * AMU2AU, 3))
    W = np.outer(d, d)
    return float(np.linalg.norm((B.T @ X @ B - dH) * W) / np.linalg.norm(dH * W))


def target_key(dH: np.ndarray, B: np.ndarray, mask: np.ndarray) -> str:
    h = hashlib.sha256()
    for arr in (np.ascontiguousarray(dH, dtype=np.float64), np.ascontiguousarray(B, dtype=np.float64), np.ascontiguousarray(mask, dtype=np.uint8)):
        h.update(arr.tobytes())
    return h.hexdigest()[:24]


def cached_pattern_ls_target(cache_dir: Path, mol_id: str, pattern: str, dH: np.ndarray, B: np.ndarray, masses_amu: np.ndarray,
                             mask: np.ndarray) -> tuple[np.ndarray, bool]:
    """(ΔF, from_cache): the target from `<cache_dir>/<pattern>/<id>.npz` when its key matches (ΔH, B, mask), else computed and stored."""
    path = Path(cache_dir) / pattern / f"{mol_id}.npz"
    key = target_key(dH, B, mask)
    if path.exists():
        with np.load(path) as z:
            if str(z["key"]) == key:
                return np.array(z["X"]), True
    X = pattern_ls_target(dH, B, masses_amu, mask)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp.npz")
    np.savez(tmp, X=X, key=key)
    tmp.replace(path)
    return X, False
