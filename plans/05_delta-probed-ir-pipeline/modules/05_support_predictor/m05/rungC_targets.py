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

The read-out target (`kfit_target`, 15 Oct 2026, TASKS 68): the same ridge problem in the metric the read-outs use, the mode-basis matrix
K = scale ∘ (C ΔF Cᵀ) of `e7_t2_posthoc.k_of`. The scale 1/(2√(ω_i ω_j)) is separable, so with U = diag(a) Vᵀ M^-1/2 Bᵀ, a_i = √(c/2)/√ω_i,
K(ΔF) = U ΔF Uᵀ and the normal equations are those above with G = UᵀU and R = Uᵀ K U — one solver, `_ridge_on_pattern`, for both targets.
Why: TASKS 65 found pattern f able to hold the correction (least-squares floor ring-ip 0.107 cm⁻¹ at ≥ 24 atoms) while the projected target
loses 1.13 cm⁻¹ there, growing with size; this target is the floor's fit, kept near the projected truth by the ridge.
"""
import hashlib
from pathlib import Path

import numpy as np
import scipy.linalg

AMU2AU = 1822.888486209
HARTREE2CM = 219474.6313705   # learning_curve_layerA.HARTREE2CM; tests/test_rungC_targets.py keeps the two equal
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
    minv = 1.0 / np.repeat(np.asarray(masses_amu, float) * AMU2AU, 3)
    BM = B * minv[None, :]                                  # B M⁻¹
    G = BM @ B.T                                            # Wilson G = B M⁻¹ Bᵀ
    R = BM @ dH @ BM.T                                      # B M⁻¹ ΔH M⁻¹ Bᵀ
    return _ridge_on_pattern(G, R, mask, projected_target(dH, B), lam_rel)


def _ridge_on_pattern(G: np.ndarray, R: np.ndarray, mask: np.ndarray, prior: np.ndarray, lam_rel: float) -> np.ndarray:
    """min over symmetric X supported on `mask` of ‖U X Uᵀ − Y‖_F² + λ ‖X − prior‖²_pattern, from G = UᵀU and R = UᵀYU; λ relative to the mean
    diagonal of the normal matrix. Both targets are this problem: the LS target (U = (B M^-1/2)ᵀ, Y = M^-1/2 ΔH M^-1/2) and the read-out target
    (U = diag(a) Vᵀ M^-1/2 Bᵀ, Y = K)."""
    mask = np.asarray(mask, bool)
    if not np.array_equal(mask, mask.T):
        raise ValueError("the pattern mask must be symmetric")
    if lam_rel < 0:
        raise ValueError("lam_rel must be >= 0")
    I, J = np.where(np.triu(mask))
    P = len(I)
    c2 = np.where(I == J, 0.5, 1.0)                         # c_p²
    N = np.empty((P, P))
    for s in range(0, P, ROW_CHUNK):
        e = min(s + ROW_CHUNK, P)
        N[s:e] = (G[np.ix_(J[s:e], I)] * G[np.ix_(I[s:e], J)] + G[np.ix_(J[s:e], J)] * G[np.ix_(I[s:e], I)])
        N[s:e] *= 2.0 * c2[s:e, None] * c2[None, :]
    r = 2.0 * c2 * R[I, J]
    x0 = prior[I, J]
    lam = lam_rel * float(np.trace(N)) / P
    N[np.diag_indices(P)] += lam
    x = scipy.linalg.cho_solve(scipy.linalg.cho_factor(N, lower=True, check_finite=False), r + lam * x0, check_finite=False)
    X = np.zeros((G.shape[0], G.shape[0]))
    X[I, J] = x
    X[J, I] = x
    return X


def readout_basis(dH: np.ndarray, B: np.ndarray, masses_amu: np.ndarray, w: np.ndarray, V: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(U, K): U = diag(a) Vᵀ M^-1/2 Bᵀ with a_i = √(HARTREE2CM/2)/√ω_i, so that U ΔF Uᵀ is e7_t2_posthoc.k_of's K of a ΔF; and the true K of
    ΔH in the same basis (cm⁻¹). w, V: the low level's vibrational eigenvalues and mass-weighted eigenvectors (learning_curve_layerA.normal_modes)."""
    d = 1.0 / np.sqrt(np.repeat(np.asarray(masses_amu, float) * AMU2AU, 3))
    a = np.sqrt(HARTREE2CM / 2.0) / np.sqrt(np.sqrt(np.abs(np.asarray(w, float))))
    U = a[:, None] * ((V.T * d[None, :]) @ B.T)
    K = np.outer(a, a) * (V.T @ (dH * np.outer(d, d)) @ V)
    return U, K


def kfit_target(dH: np.ndarray, B: np.ndarray, masses_amu: np.ndarray, w: np.ndarray, V: np.ndarray, mask: np.ndarray,
                lam_rel: float = LAM_REL) -> np.ndarray:
    """The read-out target: the ΔF on `mask` whose K is nearest the true K (whole matrix, Frobenius), ridge-anchored on the projected truth with
    relative strength `lam_rel` as the LS target is."""
    U, K = readout_basis(dH, B, masses_amu, w, V)
    return _ridge_on_pattern(U.T @ U, U.T @ K @ U, mask, projected_target(dH, B), lam_rel)


def readout_residual(dH: np.ndarray, B: np.ndarray, masses_amu: np.ndarray, w: np.ndarray, V: np.ndarray, X: np.ndarray) -> float:
    """‖U X Uᵀ − K‖_F / ‖K‖_F — the fraction of the read-out's K a ΔF leaves (weighted_residual's counterpart in the read-out metric)."""
    U, K = readout_basis(dH, B, masses_amu, w, V)
    return float(np.linalg.norm(U @ X @ U.T - K) / np.linalg.norm(K))


def weighted_residual(dH: np.ndarray, B: np.ndarray, masses_amu: np.ndarray, X: np.ndarray) -> float:
    """‖D (Bᵀ X B − ΔH) D‖_F / ‖D ΔH D‖_F — the fraction of the mass-weighted Cartesian power a ΔF leaves."""
    d = 1.0 / np.sqrt(np.repeat(np.asarray(masses_amu, float) * AMU2AU, 3))
    W = np.outer(d, d)
    return float(np.linalg.norm((B.T @ X @ B - dH) * W) / np.linalg.norm(dH * W))


def target_key(dH: np.ndarray, B: np.ndarray, mask: np.ndarray, lam_rel: float, *extra: np.ndarray) -> str:
    """The cache key: a hash of ΔH, B, the mask, λ and any extra inputs (the read-out target's ω and V); without extras the LS target's key of 1 Oct."""
    h = hashlib.sha256()
    for arr in (np.ascontiguousarray(dH, dtype=np.float64), np.ascontiguousarray(B, dtype=np.float64), np.ascontiguousarray(mask, dtype=np.uint8),
                *(np.ascontiguousarray(e, dtype=np.float64) for e in extra)):
        h.update(arr.tobytes())
    h.update(repr(float(lam_rel)).encode())
    return h.hexdigest()[:24]


def cached_pattern_ls_target(cache_dir: Path, mol_id: str, pattern: str, dH: np.ndarray, B: np.ndarray, masses_amu: np.ndarray,
                             mask: np.ndarray, lam_rel: float = LAM_REL) -> tuple[np.ndarray, bool]:
    """The LS target through the cache (the call of 1 Oct, kept for its callers)."""
    return cached_pattern_target(cache_dir, mol_id, pattern, dH, B, masses_amu, mask, lam_rel)


def cached_pattern_target(cache_dir: Path, mol_id: str, pattern: str, dH: np.ndarray, B: np.ndarray, masses_amu: np.ndarray, mask: np.ndarray,
                          lam_rel: float = LAM_REL, kind: str = "ls", w: np.ndarray | None = None, V: np.ndarray | None = None) -> tuple[np.ndarray, bool]:
    """(ΔF, from_cache) of the `kind` target ('ls', or 'kfit' with the low level's w and V): from `<cache_dir>/<pattern>_lam<λ>/<id>.npz` (LS, as
    since 1 Oct) or `<pattern>_kfit_lam<λ>/` when its key matches, else computed, checked against SCALE_LIMIT and stored."""
    if kind == "ls":
        folder, key, solve = f"{pattern}_lam{lam_rel:g}", target_key(dH, B, mask, lam_rel), lambda: pattern_ls_target(dH, B, masses_amu, mask, lam_rel)
    elif kind == "kfit":
        if w is None or V is None:
            raise ValueError("the read-out target needs the low level's w and V")
        folder, key = f"{pattern}_kfit_lam{lam_rel:g}", target_key(dH, B, mask, lam_rel, w, V)
        solve = lambda: kfit_target(dH, B, masses_amu, w, V, mask, lam_rel)  # noqa: E731
    else:
        raise ValueError(f"unknown target kind {kind!r}")
    path = Path(cache_dir) / folder / f"{mol_id}.npz"
    if path.exists():
        with np.load(path) as z:
            if str(z["key"]) == key:
                return np.array(z["X"]), True
    X = solve()
    ratio = scale_ratio(X, np.where(mask, projected_target(dH, B), 0.0))
    if ratio > SCALE_LIMIT:
        raise RuntimeError(f"{mol_id}: {kind} target entries {ratio:.3g}× the projected prior's — not stored (SCALE_LIMIT {SCALE_LIMIT:g}); "
                           f"raise lam_rel (now {lam_rel:g}) or inspect B")
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp.npz")
    np.savez(tmp, X=X, key=key)
    tmp.replace(path)
    return X, False
