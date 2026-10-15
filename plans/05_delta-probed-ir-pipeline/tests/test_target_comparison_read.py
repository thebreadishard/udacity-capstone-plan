"""probes/target_comparison_read.py (TASKS 66, 15 Oct 2026), run on synthetic records before its registration was committed — the step agreed
after two faulty line designs the same evening. The edge cases: identical arms, a large but noisy difference, one seed missing, a record of
two pool sizes, an advantage that is still growing, a guard missed by one family only, and the record layout of a real rungC_train JSON."""
import json
import sys
from pathlib import Path

import pytest

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
import target_comparison_read as TC  # noqa: E402

FAMS = ("CH-stretch", "CH-oop", "ring-ip", "other")


def record(ring: list[float], coupling: list[float], others: float = 2.0, holds=("a", "b", "s"), seeds=(0, 1, 2)) -> dict:
    """A rungC_train-shaped record of one pool size: per seed, per hold-out, the families' diag_rms and the coupling ratio."""
    per_seed = []
    for k, s in enumerate(seeds):
        h = {"diag_rms": {F: (ring[k] if F == "ring-ip" else others) for F in FAMS}, "coupling_ratio": coupling[k]}
        per_seed.append({"seed": s, **{name: dict(h) for name in holds}})
    return {"curve": {"868": {"n": 868, "per_seed": per_seed}}}


P = record([4.0, 4.1, 3.9], [0.35, 0.36, 0.34])


def test_identical_arms_meet_nothing_and_are_flat():
    res = TC.read((P, P), (P, P), (P, P))
    assert not any(x["met"] for x in res["line_1"].values()) and res["line_1"]["ring-ip"]["d"] == 0.0
    assert res["verdict"].startswith("line 1 missed, flat")


def test_a_clear_gain_with_a_clean_guard_adopts_r():
    R = record([3.3, 3.4, 3.2], [0.33, 0.34, 0.32])
    res = TC.read((P, R), (P, R), (P, R))
    assert res["line_1"]["ring-ip"]["met"] and res["line_1"]["ring-ip"]["d"] == pytest.approx(0.7)
    assert not res["line_1"]["coupling_ratio"]["met"] and res["verdict"].startswith("R becomes the recipe candidate")


def test_a_large_but_noisy_difference_is_not_a_line():
    R = record([2.4, 4.6, 3.3], [0.35, 0.36, 0.34])                          # mean d 0.57, but the seeds disagree in sign
    res = TC.read((P, R), (P, R), (P, R))
    assert res["line_1"]["ring-ip"]["d"] == pytest.approx(0.5667, abs=1e-3) and not res["line_1"]["ring-ip"]["met"]


def test_a_missed_line_with_a_growing_advantage_is_data_limited():
    half_r = record([4.0, 4.1, 3.9], [0.35, 0.36, 0.34])                     # no advantage at half the pool
    full_r = record([3.7, 3.8, 3.6], [0.35, 0.36, 0.34])                     # 0.3 at the full pool: below 0.5, but grown
    res = TC.read((P, full_r), (P, half_r), (P, P))
    assert res["still_growing"]["ring-ip"] and res["verdict"].startswith("line 1 missed while R's advantage is still growing")


def test_a_guard_missed_by_one_family_names_it():
    R = record([3.3, 3.4, 3.2], [0.33, 0.34, 0.32])
    worse = json.loads(json.dumps(R))
    for s in worse["curve"]["868"]["per_seed"]:
        s["b"]["diag_rms"]["CH-oop"] = 2.3                                    # 15 % worse than P's 2.0 on (b)
    res = TC.read((P, R), (P, R), (P, worse))
    assert res["verdict"].startswith("R pays on large molecules but costs elsewhere (b:CH-oop)")


def test_a_missing_seed_or_two_sizes_stop_the_read():
    short = record([3.3, 3.4], [0.33, 0.34], seeds=(0, 1))
    with pytest.raises(SystemExit, match=r"seed\(s\) \[2\] missing"):
        TC.read((P, short), (P, short), (P, short))
    two = json.loads(json.dumps(P))
    two["curve"]["434"] = two["curve"]["868"]
    with pytest.raises(SystemExit, match="2 pool sizes"):
        TC.read((P, two), (P, P), (P, P))


def test_the_read_is_written_as_json():
    json.dumps(TC.read((P, P), (P, P), (P, P)))


CHAIN39 = PLAN / "modules" / "05_support_predictor" / "out" / "E7_rungC_chain39_control_2026-10-09.json"


@pytest.mark.data
@pytest.mark.skipif(not CHAIN39.exists(), reason="chain 39's record is not present")
def test_a_real_record_has_the_layout_the_read_expects():
    rec = json.loads(CHAIN39.read_text(encoding="utf-8"))
    vals = TC.per_seed(rec, "s", "ring-ip")
    assert sorted(vals) == [0, 1, 2] and all(v > 0 for v in vals.values())
    assert TC.paired(rec, rec, "s", "coupling_ratio") == (0.0, 0.0)
