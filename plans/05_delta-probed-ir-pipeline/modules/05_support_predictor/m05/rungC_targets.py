"""Pattern-consistent ΔF targets for the hybrid head (1 Oct 2026, Sherlock day, lever 4).

Finding behind it: the pattern term's target was the projected truth B⁺ᵀ ΔH B⁺ read on the pattern. Reconstructed with zeros off the pattern that
target leaves 0.38–0.42 of the ring couplings on naphthalene and 2-methylnaphthalene — exactly where the single-molecule overfits (0.41, 0.40)
and the pool read-outs of every head (0.37–0.43) stopped. The pattern-supported ΔF that reconstructs best is a least-squares fit, but the plain
least-squares minimiser is useless as a regression target: the redundant internals give the design matrix near-null directions along which the
entries run to 1e7–1e10 a.u. while the reconstruction barely changes (the first lever-4 run exploded on them, 11:4x). The target used is therefore the
ridge solution anchored on the projected truth,

    min over symmetric X supported on the pattern of  ‖ D (Bᵀ X B − ΔH) D ‖_F²  +  λ ‖ X − X_proj ‖²_pattern ,   D = diag(m^-1/2),

the ΔF nearest to the physically scaled projected values among those that reconstruct ΔH well. λ is relative to the mean diagonal of the normal
matrix (`lam_rel`); the choice is registered in the pre-registration with the numbers of the λ scan. With the ridge the normal equations are well
conditioned, so they are solved directly: with E_p = e_i e_jᵀ + e_j e_iᵀ (i < j) or e_i e_iᵀ (i = j) and c_p = 1 or 1/√2, N_pq = 2 c_p² c_q² (G_jk G_il +
G_jl G_ik) with the Wilson matrix G = B M⁻¹ Bᵀ, r_p = 2 c_p² R_ij with R = B M⁻¹ ΔH M⁻¹ Bᵀ, and (N + λI) x = r + λ x_proj by Cholesky — seconds per
molecule. Counterpart: the same problem as an augmented dense least squares (`tests/test_rungC_targets.py`), equal to 1e-6.
`cached_pattern_ls_target` keeps the result on disk keyed by a hash of (ΔH, B, mask, λ); `probes/rungC_ls_targets_build.py` fills the cache ahead.
"""
import hashlib
from pathlib import Path

import numpy as np
import scipy.linalg

AMU2AU = 1822.888486209
LAM_REL = 1e-3          # default ridge, relative to the mean diagonal of the normal matrix (λ scan of 1 Oct 2026, registered)
ROW_CHUNK = 1500
PINV_RCOND = 1e-10      # singular values of B below this × the largest are null directions (redundant internals); numpy's default cutoff let a 2.7e-16
                        # value through on one machine and not on another (12:2x) — an explicit cutoff makes the prior the same everywhere
SCALE_LIMIT = 20.0      # a target whose entries exceed this multiple of the prior's is refused (the blow-ups of 11:4x and 12:2x)


def projected_target(dH: np.ndarray, B: np.ndarray) -> np.ndarray:
    """B⁺ᵀ ΔH B⁺ — the pair model's projected truth (full K × K), with the explicit pseudo-inverse cutoff PINV_RCOND."""
    Bp = np.linalg.pinv(B, rcond=PINV_RCOND)
    return Bp.T @ dH @ Bp


def scale_ratio(X: np.ndarray, prior: np.ndarray) -> float:
    """max|X| / max|prior| — the guard's number."""
    return float(np.abs(X).max() / max(np.abs(prior).max(), 1e-30))


def pattern_ls_target(dH: np.ndarray, B: np.ndarray, masses_amu: np.ndarray, mask: np.ndarray, lam_rel: float = LAM_REL) -> np.ndarray:
    """The mass-weighted least-squares ΔF supported on `mask` (K × K boolean, symmetric), ridge-anchored on the projected truth with relative
    strength `lam_rel` (0 = the plain least squares, which explodes on redundant internals). Returns ΔF (K × K)."""
    mask = np.asarray(mask, bool)
    if not np.array_equal(mask, mask.T):
        raise ValueError("the pattern mask must be symmetric")
    if lam_rel < 0:
        raise ValueError("lam_rel must be >= 0")
    minv = 1.0 / np.repeat(np.asarray(masses_amu, float) * AMU2AU, 3)
    BM = B * minv[None, :]                                  # B M⁻¹
    G = BM @ B.T                                            # Wilson G = B M⁻¹ Bᵀ
    R = BM @ dH @ BM.T                                      # B M⁻¹ ΔH M⁻¹ Bᵀ
    I, J = np.where(np.triu(mask))
    P = len(I)
    c2 = np.where(I == J, 0.5, 1.0)                         # c_p²
    N = np.empty((P, P))
    for s in range(0, P, ROW_CHUNK):
        e = min(s + ROW_CHUNK, P)
        N[s:e] = (G[np.ix_(J[s:e], I)] * G[np.ix_(I[s:e], J)] + G[np.ix_(J[s:e], J)] * G[np.ix_(I[s:e], I)])
        N[s:e] *= 2.0 * c2[s:e, None] * c2[None, :]
    r = 2.0 * c2 * R[I, J]
    x0 = projected_target(dH, B)[I, J]
    lam = lam_rel * float(np.trace(N)) / P
    N[np.diag_indices(P)] += lam
    x = scipy.linalg.cho_solve(scipy.linalg.cho_factor(N, lower=True, check_finite=False), r + lam * x0, check_finite=False)
    X = np.zeros((B.shape[0], B.shape[0]))
    X[I, J] = x
    X[J, I] = x
    return X


def weighted_residual(dH: np.ndarray, B: np.ndarray, masses_amu: np.ndarray, X: np.ndarray) -> float:
    """‖D (Bᵀ X B − ΔH) D‖_F / ‖D ΔH D‖_F — the fraction of the mass-weighted Cartesian power a ΔF leaves."""
    d = 1.0 / np.sqrt(np.repeat(np.asarray(masses_amu, float) * AMU2AU, 3))
    W = np.outer(d, d)
    return float(np.linalg.norm((B.T @ X @ B - dH) * W) / np.linalg.norm(dH * W))


def target_key(dH: np.ndarray, B: np.ndarray, mask: np.ndarray, lam_rel: float) -> str:
    h = hashlib.sha256()
    for arr in (np.ascontiguousarray(dH, dtype=np.float64), np.ascontiguousarray(B, dtype=np.float64), np.ascontiguousarray(mask, dtype=np.uint8)):
        h.update(arr.tobytes())
    h.update(repr(float(lam_rel)).encode())
    return h.hexdigest()[:24]


def cached_pattern_ls_target(cache_dir: Path, mol_id: str, pattern: str, dH: np.ndarray, B: np.ndarray, masses_amu: np.ndarray,
                             mask: np.ndarray, lam_rel: float = LAM_REL) -> tuple[np.ndarray, bool]:
    """(ΔF, from_cache): the target from `<cache_dir>/<pattern>_lam<λ>/<id>.npz` when its key matches (ΔH, B, mask, λ), else computed and stored."""
    path = Path(cache_dir) / f"{pattern}_lam{lam_rel:g}" / f"{mol_id}.npz"
    key = target_key(dH, B, mask, lam_rel)
    if path.exists():
        with np.load(path) as z:
            if str(z["key"]) == key:
                return np.array(z["X"]), True
    X = pattern_ls_target(dH, B, masses_amu, mask, lam_rel)
    ratio = scale_ratio(X, np.where(mask, projected_target(dH, B), 0.0))
    if ratio > SCALE_LIMIT:
        raise RuntimeError(f"{mol_id}: LS target entries {ratio:.3g}× the projected prior's — not stored (SCALE_LIMIT {SCALE_LIMIT:g}); "
                           f"raise lam_rel (now {lam_rel:g}) or inspect B")
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp.npz")
    np.savez(tmp, X=X, key=key)
    tmp.replace(path)
    return X, False
