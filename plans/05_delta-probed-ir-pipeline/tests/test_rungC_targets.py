"""rungC_targets (1 Oct 2026, lever 4): the ridge-anchored pattern target from the normal equations equals the same problem solved as an augmented
dense least squares; on corpus benzene it reconstructs far better than the projected target while staying at its scale; the plain least squares
(λ = 0) is the explosive case the ridge removes; the cache round-trips and invalidates on a changed λ; the trainer carries the switch."""
import re
import sys
from pathlib import Path

import numpy as np
import pytest
import scipy.linalg

PLAN = Path(__file__).resolve().parents[1]
M05 = PLAN / "modules" / "05_support_predictor" / "m05"
CORPUS = PLAN / "modules" / "05_support_predictor" / "corpus" / "molecules"
sys.path.insert(0, str(M05))
import rungC_targets as RT  # noqa: E402


def _augmented_fit(dH, B, masses, mask, lam_rel):
    """The same objective as a dense least squares: rows = upper triangle of the weighted Cartesian residual (√2 off-diagonal), plus √λ (x − x_proj)."""
    d = 1.0 / np.sqrt(np.repeat(masses * RT.AMU2AU, 3))
    n = B.shape[1]
    rows = np.triu_indices(n)
    W = np.outer(d, d) * np.where(np.eye(n, dtype=bool), 1.0, np.sqrt(2.0))
    I, J = np.where(np.triu(mask))
    cols = []
    for i, j in zip(I, J, strict=True):
        E = np.outer(B[i], B[j])
        if i != j:
            E = E + E.T
        cols.append((E * W)[rows])
    A = np.stack(cols, 1)
    h = (dH * W)[rows]
    x0 = RT.projected_target(dH, B)[I, J]
    # the module's λ is relative to the mean diagonal of the normal matrix AᵀA, which equals the mean squared column norm of A
    lam = lam_rel * float((A * A).sum()) / A.shape[1]
    Aa = np.vstack([A, np.sqrt(lam) * np.eye(len(I))])
    ha = np.concatenate([h, np.sqrt(lam) * x0])
    x = scipy.linalg.lstsq(Aa, ha, lapack_driver="gelsd")[0]
    X = np.zeros((B.shape[0], B.shape[0]))
    X[I, J] = x
    X[J, I] = x
    return X


def _random_system(seed=0, n_atoms=6, K=14):
    rng = np.random.default_rng(seed)
    B = rng.normal(size=(K, 3 * n_atoms))
    B[-1] = B[0] + 0.3 * B[1]                                       # one redundant internal, as real internal sets have
    masses = rng.uniform(1.0, 16.0, size=n_atoms)
    S = rng.normal(size=(3 * n_atoms, 3 * n_atoms))
    mask = np.zeros((K, K), bool)
    for i in range(K):
        mask[i, i] = True
        for j in range(i + 1, K):
            mask[i, j] = mask[j, i] = rng.random() < 0.5
    return B, masses, S + S.T, mask


def test_normal_equations_equal_the_augmented_least_squares():
    B, masses, dH, mask = _random_system()
    for lam in (1e-2, 1e-4):
        X = RT.pattern_ls_target(dH, B, masses, mask, lam_rel=lam)
        X_ref = _augmented_fit(dH, B, masses, mask, lam)
        assert np.allclose(X, X_ref, rtol=1e-6, atol=1e-9 * np.abs(X_ref).max())
        assert np.all(X[~mask] == 0.0)
    with pytest.raises(ValueError, match="symmetric"):
        RT.pattern_ls_target(dH, B, masses, np.triu(mask))
    with pytest.raises(ValueError, match="lam_rel"):
        RT.pattern_ls_target(dH, B, masses, mask, lam_rel=-1.0)


@pytest.mark.skipif(not (CORPUS / "A_8448043181" / "geometry.json").exists(), reason="corpus benzene not on this machine")
def test_benzene_ridge_target_reconstructs_well_at_the_projected_scale_and_plain_ls_explodes():
    pytest.importorskip("geometric")
    import json

    import e7_rungB_pairs as RB
    import e7_t2_sqm as T2
    d = CORPUS / "A_8448043181"
    g = json.load(open(d / "geometry.json"))
    masses, coords = np.asarray(g["masses_amu"]), np.asarray(g["coords_bohr"], float)
    lo = np.load(d / "hessian_b3lyp.npz")["H_projected"]
    dH = np.load(d / "hessian_wb97x.npz")["H_projected"] - lo
    B0, _types = T2.internals(g["symbols"], coords)
    F_low, _rec = T2.to_internal(lo, B0)
    pairs, _f, _c, B, _atoms = RB.molecule_pairs(g["symbols"], coords, F_low, return_atoms=True, pattern="d")
    K = B.shape[0]
    mask = np.zeros((K, K), bool)
    mask[pairs[:, 0], pairs[:, 1]] = True
    mask |= mask.T
    proj = np.where(mask, RT.projected_target(dH, B), 0.0)
    X = RT.pattern_ls_target(dH, B, masses, mask)
    res_x, res_proj = RT.weighted_residual(dH, B, masses, X), RT.weighted_residual(dH, B, masses, proj)
    assert res_x < 0.7 * res_proj                                                   # clearly closer to ΔH than the projected target
    assert np.abs(X).max() < 20 * np.abs(proj).max()                               # and at its physical scale
    assert np.allclose(X, _augmented_fit(dH, B, masses, mask, RT.LAM_REL), rtol=1e-5, atol=1e-8 * np.abs(X).max())


def test_cache_round_trip_and_invalidation_on_lambda(tmp_path):
    B, masses, dH, mask = _random_system(seed=1, n_atoms=4, K=8)
    X1, cached1 = RT.cached_pattern_ls_target(tmp_path, "mol", "d", dH, B, masses, mask)
    X2, cached2 = RT.cached_pattern_ls_target(tmp_path, "mol", "d", dH, B, masses, mask)
    assert (cached1, cached2) == (False, True) and np.array_equal(X1, X2)
    X3, cached3 = RT.cached_pattern_ls_target(tmp_path, "mol", "d", dH, B, masses, mask, lam_rel=1e-2)
    assert cached3 is False and not np.allclose(X3, X1)
    assert (tmp_path / f"d_lam{RT.LAM_REL:g}" / "mol.npz").exists() and (tmp_path / "d_lam0.01" / "mol.npz").exists()


def test_trainer_switch_present_with_the_registered_default():
    text = (M05 / "rungC_train.py").read_text(encoding="utf-8")
    assert re.search(r'add_argument\("--aux-target", default="projected", choices=\["projected", "ls"\]', text)
    assert re.search(r'add_argument\("--ls-lam", type=float, default=LAM_REL', text)
