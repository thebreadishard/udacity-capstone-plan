"""probes/s3_read.py on synthetic records, before any route A label exists (the S3 registration): degenerate pairs collapse to one mode,
a triple or a pair across families is refused, and each family's reading follows the registered lines — holds, fails on the line, fails
on (c), no verdict below MIN_MODES, reported only without an S2b verdict."""
import os
import sys

import numpy as np
import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(ROOT, "probes"))
sys.path.insert(0, os.path.join(ROOT, "src"))
import s3_read as S  # noqa: E402


def _rec(omega, family, delta, xtb=None, mol_id="t"):
    omega = np.asarray(omega, float)
    return {"id": mol_id, "omega": omega, "delta": np.asarray(delta, float), "family": np.asarray(family), "h": np.zeros(len(omega)),
            "o": np.zeros(len(omega)), "xtb": np.asarray(delta if xtb is None else xtb, float)}


def test_pairs_collapse_and_triples_are_refused():
    groups = S.pair_groups(np.array([1000.0, 1000.3, 1200.0, 1500.0, 1500.4]))
    assert sorted(len(g) for g in groups) == [1, 2, 2]
    with pytest.raises(ValueError, match="more than two"):
        S.pair_groups(np.array([900.0, 900.2, 900.4]))


def test_target_rows_average_a_pair_and_refuse_one_across_families():
    test = _rec([800.0, 800.2, 1300.0], ["CH-oop", "CH-oop", "ring-ip"], [-4.0, -6.0, -10.0])
    models = {"c": lambda tr, te: np.array([1.0, 3.0, 5.0])}
    r = S.target_rows({}, test, models)
    assert r["pairs"] == 1 and np.allclose(r["truth"], [-5.0, -10.0]) and np.allclose(r["pred"]["c"], [2.0, 5.0])
    with pytest.raises(ValueError, match="spans families"):
        S.target_rows({}, _rec([800.0, 800.2], ["CH-oop", "ring-ip"], [0.0, 0.0]), models)


def _rows(n, err_b, err_c, family="ring-ip", mol="t"):
    truth = np.linspace(-20, -5, n)
    return {mol: {"omega": np.linspace(600, 1900, n), "family": np.array([family] * n), "truth": truth,
                  "pred": {"c": truth + err_c, "b": truth + err_b, "x1": truth + err_b, "x0": truth + err_c, "x2*": np.full(n, np.nan)}}}


@pytest.mark.parametrize(("n", "err_b", "err_c", "expect"), [
    (8, 1.0, 4.0, "transfer holds"),
    (8, 3.5, 6.0, "transfer fails"),          # above the line
    (8, 2.0, 1.5, "transfer fails"),          # under the line but not below (c)
    (5, 1.0, 4.0, "no verdict"),              # fewer than MIN_MODES
])
def test_family_reading_follows_the_lines(n, err_b, err_c, expect):
    verdicts = {"ring-ip": {"best_curve_model": "b", "rms_at_all": 2.0}}
    e = S.family_read(_rows(n, err_b, err_c), verdicts)["ring-ip"]
    assert e["reading"].startswith(expect) and e["size_penalty"] == pytest.approx(err_b / 2.0)


def test_a_family_without_an_s2b_verdict_is_reported_only():
    e = S.family_read(_rows(8, 1.0, 4.0, family="other"), {})["other"]
    assert e["reading"].startswith("no S2b verdict") and "verdict_model" not in e


def test_read_targets_end_to_end_with_x2_chosen_for_one_family(monkeypatch):
    rng = np.random.default_rng(1)

    def stub(cfg=None):
        return lambda tr, te: (te["xtb"] + 0.5, None, 0)
    monkeypatch.setattr(S, "predict_x1", stub())
    monkeypatch.setattr(S, "config_predictor", stub)
    fams = ["CH-oop"] * 6 + ["ring-ip"] * 8
    train = {f"s{k}": [_rec(np.linspace(600, 1900, 14) + k, fams, -0.01 * np.linspace(600, 1900, 14) + rng.normal(0, 0.3, 14), mol_id=f"m{k}")]
             for k in range(6)}
    om = np.r_[np.linspace(650, 950, 6), np.linspace(1000, 1800, 7), 1800.3]
    targets = {"tetracene": [_rec(om, fams, -0.01 * om, mol_id="tetracene")]}
    s2b = {"verdicts": {"CH-oop": {"best_curve_model": "x2*", "rms_at_all": 1.0}, "ring-ip": {"best_curve_model": "b", "rms_at_all": 1.0}},
           "x2_choice": {"CH-oop": S.X2_GRID[0].name}}
    res = S.read_targets(train, targets, s2b)
    row = res["rows"]["tetracene"]
    assert row["pairs"] == 1 and len(row["truth"]) == 13
    assert np.all(np.isfinite(row["pred"]["x2*"][row["family"] == "CH-oop"])) and np.all(np.isnan(row["pred"]["x2*"][row["family"] == "ring-ip"]))
    ch = res["families"]["CH-oop"]
    assert ch["verdict_model"] == "x2*" and ch["rms"]["x2*"] == pytest.approx(0.5)
    assert res["families"]["ring-ip"]["n"] == 7 and res["families"]["ring-ip"]["reading"].startswith("transfer")
