"""The new anchors' read rule (`probes/new_anchor_read.py`) on synthetic curves with the regime's edge cases, before any anchor is read."""
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes"))
import new_anchor_read as R

PROXY = {f: 30.0 for f in R.FAMILIES}


def curves(**per_family):
    """Every family the same curve unless named: base is a k → value dict."""
    base = per_family.pop("base")
    return {f: dict(per_family.get(f.replace("-", "_").lower(), base)) for f in R.FAMILIES}


def test_split_is_fixed_by_the_id_and_keeps_carried_anchors_out_of_training():
    ids = [f"B_{i:010x}" for i in range(500)]
    train, test = R.split(ids, carried_before={"A_carried1", ids[3]})
    assert "A_carried1" in test and ids[3] in test and ids[3] not in train
    assert set(train).isdisjoint(test)
    share = sum(R.is_test(i) for i in ids) / len(ids)
    assert 0.15 < share < 0.25
    assert R.split(ids, {"A_carried1", ids[3]}) == (train, test)        # the same call gives the same lists
    assert train == [i for i in ids if i in set(train)]                  # training keeps the given (cheapest-first) order


@pytest.mark.parametrize(("n", "expected"), [(0, []), (19, []), (20, [20]), (45, [20, 40, 45]), (60, [20, 40, 60])])
def test_milestones(n, expected):
    assert R.milestones(n) == expected


def test_reached_needs_two_consecutive_milestones_at_the_line():
    out = R.decide(curves(base={20: 4.0, 40: 2.9, 60: 2.8, 80: 2.7}), PROXY)
    assert (out.verdict, out.k) == ("REACHED", 40)


def test_one_milestone_at_the_line_then_above_is_not_reached():
    out = R.decide(curves(base={20: 4.0, 40: 2.9, 60: 3.1}), PROXY)
    assert out.verdict != "REACHED"


def test_reached_already_at_the_first_milestone():
    out = R.decide(curves(base={20: 2.0, 40: 1.9}), PROXY)
    assert (out.verdict, out.k) == ("REACHED", 20)


def test_other_falling_keeps_the_waves_going():
    out = R.decide(curves(base={20: 2.5, 40: 2.4, 60: 2.3}, other={20: 4.6, 40: 4.2, 60: 3.8}), PROXY)
    assert out.verdict == "FALLING" and out.families["other"] == "falling" and out.families["CH-oop"] == "at the line"


def test_other_flat_above_the_line_stops_the_waves():
    out = R.decide(curves(base={20: 2.5, 40: 2.4, 60: 2.3}, other={20: 3.30, 40: 3.27, 60: 3.24}), PROXY)
    assert out.verdict == "FLAT" and out.families["other"] == "flat above"


def test_flat_needs_three_milestones():
    out = R.decide(curves(base={20: 2.5, 40: 2.4}, other={20: 3.30, 40: 3.29}), PROXY)
    assert out.verdict == "FALLING"


def test_no_learning_when_a_family_is_not_below_the_proxy_model_as_it_is():
    out = R.decide(curves(base={20: 2.5, 40: 2.4}, ch_oop={20: 31.0, 40: 30.5}), PROXY)
    assert out.verdict == "NO LEARNING" and out.families["CH-oop"] == "no learning"


@pytest.mark.parametrize(("bad", "reason"), [
    ({"drop": "other"}, "missing"), ({"grid": True}, "different milestones"), ({"single": True}, "two are needed"),
    ({"nan": True}, "not finite")])
def test_no_reading(bad, reason):
    c = curves(base={20: 2.5, 40: 2.4})
    if "drop" in bad:
        del c[bad["drop"]]
    if "grid" in bad:
        c["other"] = {20: 2.5, 60: 2.4}
    if "single" in bad:
        c = curves(base={20: 2.5})
    if "nan" in bad:
        c["ring-ip"][40] = math.nan
    out = R.decide(c, PROXY)
    assert out.verdict == "NO READING" and reason in out.reason


def test_frozen_lists_are_written_once(tmp_path):
    plan = tmp_path / "plan.json"
    plan.write_text('{"chosen": {"single": ["B_1", "B_2", "A_c"]}}')
    registry = tmp_path / "reg.json"
    registry.write_text('{"anchors": [{"mol_id": "A_c", "status": "carried"}, {"mol_id": "B_9", "status": "superseded"}]}')
    out = tmp_path / "lists"
    assert R.main(["frozen", "--plan", str(plan), "--registry", str(registry), "--out", str(out)]) == 0
    test = (out / "test_ids.txt").read_text().split()
    train = (out / "train_ids.txt").read_text().split()
    assert "A_c" in test and "A_c" not in train and "B_9" not in test
    assert sorted(train + [t for t in test if t != "A_c"]) == ["B_1", "B_2"]
    with pytest.raises(SystemExit, match="written once"):
        R.main(["frozen", "--plan", str(plan), "--registry", str(registry), "--out", str(out)])
