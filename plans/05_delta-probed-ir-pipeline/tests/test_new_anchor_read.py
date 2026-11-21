"""The new anchors' read rule (`probes/new_anchor_read.py`) on synthetic tables with the regime's edge cases, before any anchor is read."""
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes"))
import new_anchor_read as R

PROXY = {f: 30.0 for f in R.FAMILIES}
N = 40


def pts(values, half=0.05):
    """k = 20, 40, … → Point(mean, mean − half, mean + half)."""
    return {R.STEP * (j + 1): R.Point(v, v - half, v + half) for j, v in enumerate(values)}


def table(base, half=0.05, **per_family):
    """Every family the same curve unless named (ring_ip, ch_stretch, ch_oop, other)."""
    return {f: pts(per_family.get(f.replace("-", "_").lower(), base), half) for f in R.FAMILIES}


def decide(curves, proxy=PROXY, n_test=N, n_train=122):
    return R.decide(curves, proxy, n_test, n_train)


# split and milestones

def test_split_is_fixed_by_the_id_cheapest_first_and_keeps_carried_out_of_training():
    ids = [f"B_{i:010x}" for i in range(500)]
    hours = {i: float(500 - n) for n, i in enumerate(ids)}
    train, test = R.split(ids, {"A_carried1", ids[3]}, hours)
    assert "A_carried1" in test and ids[3] in test and ids[3] not in train
    assert set(train).isdisjoint(test)
    assert [hours[i] for i in train] == sorted(hours[i] for i in train)
    assert 0.15 < sum(R.is_test(i) for i in ids) / len(ids) < 0.25
    assert R.split(ids, {"A_carried1", ids[3]}, hours) == (train, test)


def test_milestones_need_the_first_k_of_the_order_finished():
    order = [f"m{i}" for i in range(70)]
    assert R.milestones(order, set(order[:45])) == [20, 40]
    assert R.milestones(order, set(order[:19])) == []
    assert R.milestones(order, set(order[1:70])) == []          # the cheapest one missing: nothing is read
    assert R.milestones(order, set(order)) == [20, 40, 60]


# outcomes

def test_reached_needs_the_line_held_through_the_last_milestone_over_two_milestones():
    out = decide(table([4.0, 2.9, 2.8, 2.7]))
    assert (out.verdict, out.k) == ("REACHED", 40)


def test_a_later_rise_undoes_reached():
    out = decide(table([2.5, 2.5, 2.5], other=[2.9, 2.9, 5.0]))
    assert out.verdict != "REACHED"


def test_at_the_line_only_at_the_last_milestone_is_unconfirmed():
    out = decide(table([3.5, 3.2, 2.9]))
    assert out.verdict == "AT THE LINE UNCONFIRMED" and "next milestone" in out.reason
    out = decide(table([3.5, 3.2, 3.1, 3.1, 3.05, 2.9]), n_train=122)                # k = 120 of 122: no 140
    assert out.verdict == "AT THE LINE UNCONFIRMED" and "no next milestone exists" in out.reason


def test_a_milestone_beyond_the_training_order_is_no_reading():
    out = decide(table([2.5, 2.4, 2.3]), n_train=50)
    assert out.verdict == "NO READING" and "beyond the 50 training anchors" in out.reason


def test_other_falling_keeps_the_waves_going():
    out = decide(table([2.5, 2.4, 2.3], other=[4.6, 4.2, 3.8]))
    assert out.verdict == "FALLING" and out.families["other"] == "falling" and out.families["CH-oop"] == "at the line"


def test_other_flat_above_the_line_stops_the_waves():
    out = decide(table([2.5, 2.4, 2.3], other=[3.30, 3.27, 3.24]))
    assert out.verdict == "FLAT" and out.families["other"] == "flat above"


def test_a_gain_inside_the_noise_is_flat():
    curves = table([2.5, 2.4, 2.3], other=[4.0, 3.5, 3.6])
    curves["other"][60] = R.Point(3.6, 3.0, 4.2)                  # gain 0.4, half-width 0.6
    assert decide(curves).families["other"] == "flat above"


def test_flat_is_not_declared_while_another_family_still_falls():
    out = decide(table([2.5, 2.4, 2.3], other=[3.30, 3.27, 3.24], ch_oop=[4.6, 4.2, 3.8]))
    assert out.verdict == "FALLING"


def test_flat_needs_three_milestones():
    assert decide(table([2.5, 2.4], other=[3.30, 3.29])).verdict == "FALLING"


def test_no_learning_only_for_a_family_above_the_line():
    out = decide(table([2.5, 2.4], ch_oop=[31.0, 30.5]))
    assert out.verdict == "NO LEARNING" and out.families["CH-oop"] == "no learning"
    proxy = dict(PROXY, **{"CH-stretch": 2.5})                     # the proxy already at the line; the fine-tune a little worse
    out = decide(table([2.5, 2.4], ch_stretch=[2.8, 2.8], other=[4.6, 4.2]), proxy=proxy)
    assert out.verdict == "FALLING" and out.families["CH-stretch"] == "at the line"


@pytest.mark.parametrize(("make", "reason"), [
    (lambda: (table([2.5, 2.4]), 29), "at least 30"),
    (lambda: ({f: v for f, v in table([2.5, 2.4]).items() if f != "other"}, N), "missing"),
    (lambda: ({**table([2.5, 2.4]), "other": {20: R.Point(2, 1.9, 2.1), 60: R.Point(2, 1.9, 2.1)}}, N), "different milestones"),
    (lambda: ({f: {40: R.Point(2, 1.9, 2.1), 80: R.Point(2, 1.9, 2.1)} for f in R.FAMILIES}, N), "are not 20"),
    (lambda: (table([2.5]), N), "two are needed"),
    (lambda: ({**table([2.5, 2.4]), "ring-ip": {20: R.Point(2, 1.9, 2.1), 40: R.Point(math.nan, 1, 2)}}, N), "not finite"),
    (lambda: ({**table([2.5, 2.4]), "ring-ip": {20: R.Point(-1, -2, 0), 40: R.Point(2, 1.9, 2.1)}}, N), "negative"),
    (lambda: ({**table([2.5, 2.4]), "ring-ip": {20: R.Point(2, 2.2, 2.1), 40: R.Point(2, 1.9, 2.1)}}, N), "lower end lies above"),
])
def test_no_reading(make, reason):
    curves, n_test = make()
    out = decide(curves, n_test=n_test)
    assert out.verdict == "NO READING" and reason in out.reason


def test_frozen_lists_are_written_once(tmp_path, monkeypatch):
    import anchor_plan
    monkeypatch.setattr(anchor_plan, "corpus_cells", lambda: {"B_1": {"hours": 9.0}, "B_2": {"hours": 1.0}, "A_c": {"hours": 5.0}})
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
