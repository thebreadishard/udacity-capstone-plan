"""probes/s2_xtb_read.py (S2 amendment 4, 19 Oct 2026), tested on synthetic records before any real number (CLAUDE.md, 'Evidence'): the
mode matching finds a permutation and refuses a partner below the overlap line; on molecules whose G label is exactly a per-family slope
times Δ_xtb plus an offset, x1 recovers it to round-off, x0 shows the scale error with Pearson r = 1, and x2 runs; a family absent from a
scaffold and modes without a partner do not break the read."""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes"))
pytest.importorskip("sklearn")
X = pytest.importorskip("s2_xtb_read")

SLOPE = {"CH-stretch": 0.9, "CH-oop": 0.6, "ring-ip": 0.8, "other": 0.7}
OFFSET = {"CH-stretch": -2.0, "CH-oop": 1.5, "ring-ip": -0.5, "other": 0.0}


def orthonormal(n, m, seed):
    q, _ = np.linalg.qr(np.random.default_rng(seed).normal(size=(n, n)))
    return q[:, :m]


def test_a_permutation_is_found_with_full_overlap():
    q = orthonormal(9, 6, 0)
    perm = np.array([3, 0, 5, 1, 4, 2])
    partner, overlap = X.match_modes(q, q[:, perm])
    assert (perm[partner] == np.arange(6)).all() and np.allclose(overlap, 1.0)


def test_modes_mixed_beyond_recognition_have_no_partner():
    q = orthonormal(9, 6, 1)
    v = np.ones(3) / np.sqrt(3)
    h = np.eye(3) - 2 * np.outer(v, v)                  # squared entries 1/9 and 4/9: no mode keeps half of itself or of another
    qx = q.copy()
    qx[:, :3] = q[:, :3] @ h
    partner, overlap = X.match_modes(q, qx)
    assert (partner[:3] == -1).all() and (partner[3:] == np.arange(3, 6)).all() and np.allclose(overlap[:3], 4 / 9)


def test_attach_xtb_follows_the_partner_and_leaves_nan_without_one():
    q = orthonormal(6, 4, 2)
    qx = q[:, [1, 0, 2, 3]].copy()
    qx[:, 3] = q[:, 3] * 0.5 + q[:, 2] * np.sqrt(0.75)  # overlap 0.25 with its own mode
    rec = X.attach_xtb({"delta": np.zeros(4)}, {"delta": np.array([10.0, 20.0, 30.0, 40.0])}, q, qx)
    assert rec["xtb"][0] == 20.0 and rec["xtb"][1] == 10.0 and np.isnan(rec["xtb"][3]) and rec["no_xtb"].tolist() == [False, False, False, True]


def synthetic(n_scaf=10, per=24, seed=3):
    """One molecule per scaffold, window modes only; G = slope(family) × xtb + offset(family); scaffold 0 has no 'other' mode."""
    rng = np.random.default_rng(seed)
    by_scaf = {}
    for s in range(n_scaf):
        fam = rng.choice(X.FAMILIES[:3] if s == 0 else X.FAMILIES, size=per)
        xtb = rng.normal(-15, 8, size=per)
        delta = np.array([SLOPE[f] * x + OFFSET[f] for f, x in zip(fam, xtb, strict=True)])
        by_scaf[f"s{s}"] = [{"omega": rng.uniform(600, 1900, size=per), "family": fam, "h": rng.uniform(0, 1, size=per),
                             "o": rng.uniform(0, 1, size=per), "delta": delta, "xtb": xtb}]
    return by_scaf


def test_x1_recovers_an_exact_per_family_slope_and_x0_shows_the_scale_error():
    data = synthetic()
    r = X.read_scope(data)
    mols = [m for ms in data.values() for m in ms]
    fam, xtb, delta = (np.concatenate([m[k] for m in mols]) for k in ("family", "xtb", "delta"))
    for fa in X.FAMILIES:
        assert r["x1"]["per_family"][fa]["b"] < 0.05, fa          # the ridge's 1e-3 penalty leaves a trace, no more
        implied = np.sqrt(np.mean((xtb - delta)[fam == fa] ** 2))
        assert r["x0"][fa]["pearson_r"] > 0.999 and abs(r["x0"][fa]["rms"] - implied) < 1e-9 and implied > 10 * r["x1"]["per_family"][fa]["b"]
    assert r["x1"]["verdict"]["licensed"] == ["b", "c"] or "b" in r["x1"]["verdict"]["licensed"]
    assert set(r["x2"]) == set(X.FAMILIES) and all(np.isfinite(v["rms"]) for v in r["x2"].values())
