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


def _side(delta, marked=(), checked=True, omega=None):
    """A molecule as s2_read.load_molecule leaves it, so far as attach_xtb reads it; its modes 100 cm⁻¹ apart unless given."""
    mask = np.zeros(len(delta), bool)
    mask[list(marked)] = True
    omega = 500.0 + 100.0 * np.arange(len(delta)) if omega is None else np.asarray(omega, float)
    return {"omega": omega, "delta": np.asarray(delta, float), "vpt2_marked": mask, "vpt2_checked": checked}


def test_attach_xtb_follows_the_partner_and_leaves_nan_without_one():
    q = orthonormal(6, 4, 2)
    qx = q[:, [1, 0, 2, 3]].copy()
    qx[:, 3] = q[:, 3] * 0.5 + q[:, 2] * np.sqrt(0.75)  # overlap 0.25 with its own mode
    rec = X.attach_xtb(_side(np.zeros(4)), _side([10.0, 20.0, 30.0, 40.0]), q, qx)
    assert rec["xtb"][0] == 20.0 and rec["xtb"][1] == 10.0 and np.isnan(rec["xtb"][3]) and rec["no_xtb"].tolist() == [False, False, False, True]
    assert not rec["vpt2_marked"].any() and rec["vpt2_checked"]


def test_a_mode_inherits_the_mark_of_its_xtb_partner():
    q = orthonormal(6, 4, 2)
    qx = q[:, [1, 0, 2, 3]].copy()
    qx[:, 3] = q[:, 3] * 0.5 + q[:, 2] * np.sqrt(0.75)      # mode 3 has no partner, so it can inherit nothing
    rec = X.attach_xtb(_side(np.zeros(4), marked=[2]), _side([10.0, 20.0, 30.0, 40.0], marked=[1, 3]), q, qx)
    # xtb mode 1 is G mode 0's partner, so mode 0 is marked; mode 2 was marked on the G side already
    assert rec["vpt2_marked"].tolist() == [True, False, True, False]


def test_an_unchecked_side_makes_the_pair_unchecked():
    q = orthonormal(6, 4, 2)
    rec = X.attach_xtb(_side(np.zeros(4)), _side(np.zeros(4), checked=False), q, q.copy())
    assert not rec["vpt2_checked"]


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


# ---- the set-wise match (TASKS 255) ----

PAIR = (2, 3)
OMEGA_PAIR = np.array([600.0, 700.0, 1000.0, 1000.3, 1200.0, 1300.0])        # modes 2 and 3: a degenerate pair, split by noise


def _pair(share=0.985, seed=5):
    """Six G modes in nine dimensions and the xtb modes that match them one to one, except that the plane of the xtb pair leans
    out of the plane of the G pair: every vector of one plane has `share` of its square in the other."""
    basis = orthonormal(9, 9, seed)
    q, qx = basis[:, :6], basis[:, :6].copy()
    for k, spare in zip(PAIR, (6, 7), strict=True):
        qx[:, k] = np.sqrt(share) * q[:, k] + np.sqrt(1.0 - share) * basis[:, spare]
    return q, qx


def _turned(q, angle, pair=PAIR):
    """The modes with the two vectors of a pair turned by `angle` in their plane."""
    out, (a, b) = q.copy(), pair
    out[:, a], out[:, b] = np.cos(angle) * q[:, a] + np.sin(angle) * q[:, b], -np.sin(angle) * q[:, a] + np.cos(angle) * q[:, b]
    return out


def test_modes_alone_in_their_sets_are_matched_as_match_modes_matches_them_to_the_bit():
    rng = np.random.default_rng(8)
    for seed in range(20):
        q = orthonormal(12, 8, seed)
        mix, _ = np.linalg.qr(np.eye(8) + 0.6 * rng.normal(size=(8, 8)))       # some modes keep a partner, some lose it
        qx, values = q @ mix, rng.normal(size=8)
        partner, overlap = X.match_modes(q, qx)
        m = X.match_sets(500.0 + 100.0 * np.arange(8), q, qx)
        assert np.array_equal(m.partner, partner) and np.array_equal(m.overlap, overlap) and not m.set_wise.any()
        assert np.array_equal(m.carry(values), np.where(partner >= 0, values[np.maximum(partner, 0)], np.nan), equal_nan=True)
        assert np.array_equal(m.flagged(values > 0), (partner >= 0) & (values > 0)[np.maximum(partner, 0)])
    assert (partner < 0).any() and (partner >= 0).any()


def test_a_degenerate_pair_is_matched_the_same_in_every_basis_of_either_side():
    """100 draws: both pairs turned by random angles, the two planes sharing 0.7. The best one-to-one overlap runs from 0.35 to
    0.7 with the angle, under the line in about a quarter of the bases; the shift, the refusal and the mark each mode gets do
    not move."""
    q, qx = _pair(share=0.7)
    g, x = _side(np.zeros(6), omega=OMEGA_PAIR), _side([10.0, 20.0, -40.0, -40.0, 50.0, 60.0], marked=[1])
    reference = X.attach_xtb(g, x, q, qx)
    assert reference["xtb"].tolist() == [10.0, 20.0, -40.0, -40.0, 50.0, 60.0] and not reference["xtb_set_wise"].any()
    rng, as_a_set, lost_one_to_one = np.random.default_rng(11), 0, 0
    for _ in range(100):
        a, b = rng.uniform(0.0, 2.0 * np.pi, 2)
        rec = X.attach_xtb(g, x, _turned(q, a), _turned(qx, b))
        assert np.abs(rec["xtb"] - reference["xtb"]).max() <= 1e-9
        assert np.array_equal(rec["no_xtb"], reference["no_xtb"]) and np.array_equal(rec["vpt2_marked"], reference["vpt2_marked"])
        assert (rec["xtb_overlap"][list(PAIR)] >= 0.5).all()
        assert np.allclose(rec["xtb_overlap"][rec["xtb_set_wise"]], 0.7, atol=1e-12)
        as_a_set += int(rec["xtb_set_wise"][list(PAIR)].all())
        lost_one_to_one += int(X.attach_xtb(g, x, _turned(q, a), _turned(qx, b), rule="single")["no_xtb"][list(PAIR)].all())
    assert 10 < as_a_set < 50 and lost_one_to_one == as_a_set          # the one-to-one rule lost the pair in exactly those bases


def test_the_basis_a_pair_was_refused_for_is_45_degrees():
    q, qx = _pair()
    g, x = _side(np.zeros(6), omega=OMEGA_PAIR), _side([10.0, 20.0, -40.0, -40.0, 50.0, 60.0])
    turned = _turned(qx, np.pi / 4)
    _, one_to_one = X.match_modes(q, turned)
    assert np.allclose(one_to_one[list(PAIR)], 0.4925)
    rec = X.attach_xtb(g, x, q, turned)
    assert rec["xtb"][list(PAIR)].tolist() == pytest.approx([-40.0, -40.0], abs=1e-12) and rec["xtb_set_wise"].tolist() == [0, 0, 1, 1, 0, 0]
    assert np.allclose(rec["xtb_overlap"][list(PAIR)], 0.985) and not rec["no_xtb"].any()
    assert X.attach_xtb(g, x, q, turned, rule="single")["no_xtb"].tolist() == [0, 0, 1, 1, 0, 0]


def test_a_pair_whose_two_labels_differ_gets_a_shift_between_them():
    """Stored labels of a symmetry pair differ by numerical noise; the carried shift then depends on the basis, within the two."""
    q, qx = _pair()
    g, x = _side(np.zeros(6), omega=OMEGA_PAIR), _side([10.0, 20.0, -40.0, -40.02, 50.0, 60.0])
    rng = np.random.default_rng(12)
    for _ in range(50):
        rec = X.attach_xtb(g, x, q, _turned(qx, rng.uniform(0.0, 2.0 * np.pi)))
        assert ((rec["xtb"][list(PAIR)] <= -40.0) & (rec["xtb"][list(PAIR)] >= -40.02)).all()


def test_planes_that_do_not_coincide_are_refused_as_a_set_too():
    q, qx = _pair(share=0.4)
    rec = X.attach_xtb(_side(np.zeros(6), omega=OMEGA_PAIR), _side(np.arange(6.0)), q, _turned(qx, 0.3))
    assert rec["no_xtb"].tolist() == [0, 0, 1, 1, 0, 0] and np.isnan(rec["xtb"][list(PAIR)]).all() and not rec["xtb_set_wise"].any()
    assert np.allclose(rec["xtb_overlap"][list(PAIR)], 0.4)             # the overlap of the plane, in any basis


def test_neighbours_by_accident_keep_their_own_partners_and_a_set_never_reaches_past_them():
    """Modes 2 and 3 lie 0.3 cm⁻¹ apart and are unrelated. Each keeps its own partner's shift, not a mean. Mode 2 turned half
    into a spare direction is refused: the set holds its neighbour's partner, which it does not overlap, and nothing else."""
    basis = orthonormal(9, 9, 6)
    q, qx = basis[:, :6], basis[:, :6].copy()
    x = _side([10.0, 20.0, -30.0, -70.0, 50.0, 60.0], marked=[3])
    rec = X.attach_xtb(_side(np.zeros(6), omega=OMEGA_PAIR), x, q, qx)
    assert rec["xtb"].tolist() == [10.0, 20.0, -30.0, -70.0, 50.0, 60.0] and rec["vpt2_marked"].tolist() == [0, 0, 0, 1, 0, 0]
    qx[:, 2] = np.sqrt(0.45) * q[:, 2] + np.sqrt(0.55) * basis[:, 6]
    rec = X.attach_xtb(_side(np.zeros(6), omega=OMEGA_PAIR), x, q, qx)
    assert rec["no_xtb"].tolist() == [0, 0, 1, 0, 0, 0] and rec["xtb_overlap"][2] == pytest.approx(0.45) and rec["xtb"][3] == -70.0


def test_a_set_takes_its_shift_by_overlap_and_its_mark_by_share():
    """A refused mode that lies in the span of two partners: the shift is their mean weighted by squared overlap; a marked
    member marks the mode from a twentieth of the overlap on."""
    basis = orthonormal(9, 9, 7)
    q, qx = basis[:, :6], basis[:, :6].copy()
    qx[:, 2], qx[:, 3] = _turned(q, np.arcsin(np.sqrt(0.48)))[:, [2, 3]].T       # each G mode: 0.52 on one xtb mode, 0.48 on the other
    qx[:, 2] = np.sqrt(0.9) * qx[:, 2] + np.sqrt(0.1) * basis[:, 6]              # and the first xtb mode leaves the plane a little
    g = _side(np.zeros(6), omega=OMEGA_PAIR)
    rec = X.attach_xtb(g, _side([10.0, 20.0, -30.0, -70.0, 50.0, 60.0], marked=[3]), q, qx)
    m = X.match_sets(OMEGA_PAIR, q, qx)
    ov = (q.T @ qx) ** 2
    assert m.set_wise.tolist() == [0, 0, 1, 0, 0, 0] and m.partner[2] == 2 and ov[2, 2] == pytest.approx(0.468)
    assert rec["xtb"][2] == pytest.approx((ov[2, 2] * -30.0 + ov[2, 3] * -70.0) / (ov[2, 2] + ov[2, 3]), abs=1e-12)
    assert rec["xtb"][3] == -70.0 and rec["vpt2_marked"].tolist() == [0, 0, 1, 1, 0, 0]
    weights = np.zeros((1, 3))
    weights[0] = [0.96, 0.04, 0.0]
    below = X.SetMatch(np.array([0]), np.array([0.9]), np.array([True]), weights)
    assert below.flagged([False, True, False]).tolist() == [False] and below.flagged([True, False, False]).tolist() == [True]
    assert X.MARK_SHARE == 0.05


def test_the_tolerance_decides_what_a_set_is_and_none_means_no_sets():
    assert X.mode_sets(np.array([10.0, 10.9, 11.8, 13.0, 9.5]), 1.0).tolist() == [0, 0, 0, 1, 0]      # chained through neighbours
    assert X.mode_sets(np.array([10.0, 10.9, 11.8]), None).tolist() == [0, 1, 2] and len(X.mode_sets(np.array([]), 1.0)) == 0
    q, qx = _pair()
    turned = _turned(qx, np.pi / 4)
    assert X.match_sets(OMEGA_PAIR, q, turned, tolerance=0.2).partner.tolist() == [0, 1, -1, -1, 4, 5]   # the pair is 0.3 apart
    assert sorted(X.match_sets(OMEGA_PAIR, q, turned).partner.tolist()) == [0, 1, 2, 3, 4, 5]     # at 45° either partner is as good
    with pytest.raises(ValueError, match=r"\(5,\) frequencies for modes"):
        X.match_sets(OMEGA_PAIR[:5], q, turned)


def test_an_unknown_match_rule_is_refused_before_anything_is_read():
    with pytest.raises(ValueError, match="match rule 'pairs'"):
        X.build({}, {}, {}, "all", rule="pairs")
    with pytest.raises(ValueError, match="match rule 'pairs'"):
        X.attach_xtb({}, {}, np.eye(2), np.eye(2), rule="pairs")
    assert X.MATCH_RULES == {"sets": 1.0, "single": None} and X.DEFAULT_RULE == "sets"
