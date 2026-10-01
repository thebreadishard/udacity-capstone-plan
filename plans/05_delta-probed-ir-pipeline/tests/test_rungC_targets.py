"""rungC_targets (1 Oct 2026, lever 4): the conjugate-gradient pattern fit reaches the dense least-squares optimum (same reconstruction, same
weighted residual) on a redundant random system and on corpus benzene; an asymmetric mask is refused; the trainer carries the switch."""
import re
import sys
from pathlib import Path

import numpy as np
import pytest

PLAN = Path(__file__).resolve().parents[1]
M05 = PLAN / "modules" / "05_support_predictor" / "m05"
CORPUS = PLAN / "modules" / "05_support_predictor" / "corpus" / "molecules"
sys.path.insert(0, str(M05))
import rungC_targets as RT  # noqa: E402


def _dense_fit(dH, B, masses, mask):
    """The probe's dense solution: least squares over the upper-triangle pattern entries in the mass-weighted norm."""
    d = 1.0 / np.sqrt(np.repeat(masses * RT.AMU2AU, 3))
    W = np.outer(d, d)
    K = B.shape[0]
    pairs = [(i, j) for i in range(K) for j in range(i, K) if mask[i, j]]
    cols = []
    for i, j in pairs:
        E = np.outer(B[i], B[j])
        E = E + E.T if i != j else E
        cols.append((E * W).ravel())
    x, *_ = np.linalg.lstsq(np.stack(cols, 1), (dH * W).ravel(), rcond=None)
    X = np.zeros((K, K))
    for (i, j), v in zip(pairs, x, strict=True):
        X[i, j] = X[j, i] = v
    return X


def test_solver_matches_an_independent_dense_least_squares_on_a_well_posed_random_system():
    rng = np.random.default_rng(0)
    n_atoms, K = 6, 10                                              # 18 Cartesians, 10 independent internals: a full-rank design
    B = rng.normal(size=(K, 3 * n_atoms))
    masses = rng.uniform(1.0, 16.0, size=n_atoms)
    S = rng.normal(size=(3 * n_atoms, 3 * n_atoms))
    dH = S + S.T
    mask = np.zeros((K, K), bool)
    for i in range(K):
        mask[i, i] = True
        for j in range(i + 1, K):
            mask[i, j] = mask[j, i] = rng.random() < 0.4
    X_cg = RT.pattern_ls_target(dH, B, masses, mask)
    X_dense = _dense_fit(dH, B, masses, mask)
    assert np.allclose(B.T @ X_cg @ B, B.T @ X_dense @ B, atol=1e-7)
    assert abs(RT.weighted_residual(dH, B, masses, X_cg) - RT.weighted_residual(dH, B, masses, X_dense)) < 1e-8
    assert np.all(X_cg[~mask] == 0.0)
    with pytest.raises(ValueError, match="symmetric"):
        RT.pattern_ls_target(dH, B, masses, np.triu(mask))


@pytest.mark.skipif(not (CORPUS / "A_8448043181" / "geometry.json").exists(), reason="corpus benzene not on this machine")
def test_benzene_pattern_d_fit_leaves_little_and_beats_the_projected_truth():
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
    assert np.allclose(B, B0)
    K = B.shape[0]
    mask = np.zeros((K, K), bool)
    mask[pairs[:, 0], pairs[:, 1]] = True
    mask |= mask.T
    X = RT.pattern_ls_target(dH, B, masses, mask)
    Bp = np.linalg.pinv(B)
    projected = np.where(mask, Bp.T @ dH @ Bp, 0.0)
    res_ls, res_proj = RT.weighted_residual(dH, B, masses, X), RT.weighted_residual(dH, B, masses, projected)
    assert res_ls < 0.05 < res_proj                                                 # the fit leaves little; the projected target leaves a lot
    res_dense = RT.weighted_residual(dH, B, masses, _dense_fit(dH, B, masses, mask))
    assert res_ls <= res_dense + 1e-6                                               # the same minimum as the independent SVD route (redundant internals:
    assert np.abs(B.T @ X @ B - dH).max() < 0.05 * np.abs(dH).max()                 # the two drivers may truncate differently, the objective is unique)


def test_trainer_switch_present_with_the_registered_default():
    text = (M05 / "rungC_train.py").read_text(encoding="utf-8")
    assert re.search(r'add_argument\("--aux-target", default="projected", choices=\["projected", "ls"\]', text)


def test_cache_round_trip_and_invalidation(tmp_path):
    rng = np.random.default_rng(1)
    B = rng.normal(size=(6, 9))
    masses = rng.uniform(1.0, 12.0, size=3)
    S = rng.normal(size=(9, 9))
    dH = S + S.T
    mask = np.ones((6, 6), bool)
    X1, cached1 = RT.cached_pattern_ls_target(tmp_path, "mol", "d", dH, B, masses, mask)
    X2, cached2 = RT.cached_pattern_ls_target(tmp_path, "mol", "d", dH, B, masses, mask)
    assert (cached1, cached2) == (False, True) and np.array_equal(X1, X2)
    X3, cached3 = RT.cached_pattern_ls_target(tmp_path, "mol", "d", 2 * dH, B, masses, mask)
    assert cached3 is False and np.allclose(X3, 2 * X1, atol=1e-8)
    assert (tmp_path / "d" / "mol.npz").exists()
