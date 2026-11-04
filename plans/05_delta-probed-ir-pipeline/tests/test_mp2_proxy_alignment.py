"""probes/mp2_proxy_alignment.py's read on synthetic records, before any anchor's number is read (TASKS 11 (c)): the pooled statistics, the
leave-one-anchor-out factor, the thresholds of the verdict and the regime's edges (a candidate that carries nothing, too few modes, a perfect
baseline)."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes"))
M = pytest.importorskip("mp2_proxy_alignment")


def _records(truth: list[list[float]], **cands: list[list[float]]) -> list[dict]:
    """One record per anchor, every mode in CH-oop."""
    return [{"mol_id": f"A{k}", "families": ["CH-oop"] * len(t), "truth": t, **{c: v[k] for c, v in cands.items()}}
            for k, t in enumerate(truth)]


TRUTH = [[1.0, -2.0, 3.0, 0.5], [2.0, 1.0, -1.0, 0.0], [-3.0, 0.5, 2.0, 1.5]]


def test_a_candidate_equal_to_cc_leaves_nothing():
    s = M.family_stats(_records(TRUTH, wb97x=TRUTH), "CH-oop", "wb97x")
    assert not s["too_few"] and s["n_anchors"] == 3 and s["n_modes"] == 12
    assert s["corr"] == pytest.approx(1.0) and s["slope"] == pytest.approx(1.0)
    assert s["rms_direct"] == pytest.approx(0.0) and s["rms_scaled_loo"] == pytest.approx(0.0)


def test_a_candidate_twice_cc_is_wrong_as_it_is_and_right_after_its_factor():
    double = [[2 * x for x in t] for t in TRUTH]
    s = M.family_stats(_records(TRUTH, wb97x=double), "CH-oop", "wb97x")
    t = np.concatenate(TRUTH)
    assert s["slope"] == pytest.approx(0.5) and s["rms_direct"] == pytest.approx(np.sqrt(np.mean(t ** 2)))
    assert s["rms_scaled_loo"] == pytest.approx(0.0, abs=1e-12)


def test_the_factor_is_fitted_on_the_other_anchors_only():
    cand = [[x for x in TRUTH[0]], [2 * x for x in TRUTH[1]], [x for x in TRUTH[2]]]   # anchor 1 is off by a factor two
    s = M.family_stats(_records(TRUTH, wb97x=cand), "CH-oop", "wb97x")
    assert s["rms_scaled_loo"] > 0.3                    # a fit that saw anchor 1 itself would hide part of its miss


def test_a_candidate_that_carries_nothing_reads_as_the_cc_rms():
    zero = [[0.0] * len(t) for t in TRUTH]
    s = M.family_stats(_records(TRUTH, wb97x=zero), "CH-oop", "wb97x")
    assert s["slope"] == 0.0 and np.isnan(s["corr"])
    assert s["rms_scaled_loo"] == pytest.approx(s["rms_cc"]) and s["rms_direct"] == pytest.approx(s["rms_cc"])


def test_too_few_anchors_or_modes_is_not_read():
    assert M.family_stats(_records(TRUTH[:2], wb97x=TRUTH[:2]), "CH-oop", "wb97x")["too_few"]           # 2 anchors
    short = [t[:3] for t in TRUTH]
    assert M.family_stats(_records(short, wb97x=short), "CH-oop", "wb97x")["too_few"]                  # 9 modes
    assert M.family_stats(_records(TRUTH, wb97x=TRUTH), "other", "wb97x")["n_modes"] == 0


def test_the_verdict_thresholds():
    def st(v):
        return {"too_few": False, "rms_scaled_loo": v}
    assert M.family_verdict(st(0.8), st(1.0)) == ("better", pytest.approx(0.8))
    assert M.family_verdict(st(0.81), st(1.0))[0] == "no clear difference"
    assert M.family_verdict(st(1.25), st(1.0)) == ("worse", pytest.approx(1.25))
    assert M.family_verdict(st(0.0), st(0.0)) == ("no clear difference", None)
    assert M.family_verdict(st(0.1), st(0.0)) == ("worse", None)
    assert M.family_verdict({"too_few": True}, st(1.0)) == ("too few modes", None)


def test_the_read_covers_every_family_and_reports():
    rng = np.random.default_rng(0)
    recs = []
    for k in range(4):
        fams = ["CH-oop", "other", "ring-ip", "CH-stretch"] * 3
        t = rng.normal(size=12)
        recs.append({"mol_id": f"A{k}", "families": fams, "truth": t.tolist(), "wb97x": (t + rng.normal(size=12)).tolist(),
                     "mp2_dz": (t + 0.1 * rng.normal(size=12)).tolist(), "mp2_tz": t.tolist()})
    res = M.read(recs)
    assert set(res) == set(M.FAMS) and all(r["verdict"] == "better" for r in res.values())
    assert "| CH-oop | better |" in M.report(res, recs)


def test_amendment_1_adds_the_631gs_verdict_only_when_every_record_carries_it():
    rng = np.random.default_rng(1)
    recs = []
    for k in range(4):
        t = rng.normal(size=12)
        recs.append({"mol_id": f"A{k}", "families": ["CH-oop", "other", "ring-ip", "CH-stretch"] * 3, "truth": t.tolist(),
                     "wb97x": (t + 0.2 * rng.normal(size=12)).tolist(), "mp2_dz": t.tolist(), "mp2_tz": t.tolist(),
                     "mp2_631gs": [0.0] * 12})                      # a stone that carries nothing reads as the CC rms: worse
    res = M.read(recs)
    assert all(r["verdict_631gs"] == "worse" for r in res.values()) and all(r["verdict"] == "better" for r in res.values())
    assert "MP2/6-31G* against ωB97X" in M.report(res, recs)
    del recs[0]["mp2_631gs"]
    res = M.read(recs)
    assert not any("verdict_631gs" in r for r in res.values()) and "MP2/6-31G*" not in M.report(res, recs)


def test_a_missing_631gs_row_file_stops_the_read(tmp_path):
    with pytest.raises(SystemExit, match=r"no MP2/6-31G\* rows for A_x"):
        M.rows_631gs(tmp_path, "A_x", ["H", "H"], np.zeros((2, 3)), np.ones(2))
