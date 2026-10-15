"""Rung 4's read, prepared before any label (TASKS 61, 15 Oct 2026): the curve files are nested and leave the test family to the structural
hold-out; the settled check refuses an unknown layer; the registered read applies line 1 and the still-learning rule per family, and refuses a
tetracene set that lost molecules."""
import csv
import sys
from pathlib import Path

import pytest

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
import manifest_settled as MS  # noqa: E402
import rung4_curve_files as CF  # noqa: E402
import rung4_read as RR  # noqa: E402

# ---------------------------------------------------------------- the curve files

@pytest.mark.skipif(not CF.FROZEN.exists() or not CF.HELD_OUT.exists(), reason="the frozen rung-4 list is not present")
def test_curve_files_are_nested_and_leave_the_test_family_to_the_hold_out():
    files = CF.curve_files(CF.frozen_rows(), CF.bare_ids(CF.HELD_OUT))
    ex = {k: set(files[f"rung4_k{k}_exclude.txt"]) for k in CF.CURVE}
    assert [len(ex[k]) for k in CF.CURVE] == [120, 80, 40] and ex[0] > ex[10] > ex[20]
    test = set(files["rung4_tetracene.txt"])
    assert len(test) == 30 and not test & ex[0]
    ranks = {r["id"]: int(r["curve_rank"]) for r in CF.frozen_rows()}
    assert all(ranks[i] > 10 for i in ex[10]) and all(ranks[i] <= 20 for i in ex[0] - ex[20])


def test_curve_files_refuse_a_disagreeing_hold_out():
    rows = [dict(id=f"T{i}", test_family="1", family="tetracene", curve_rank="0") for i in range(2)]
    with pytest.raises(SystemExit, match="disagree"):
        CF.curve_files(rows, ["T0"])


# ---------------------------------------------------------------- the settled check

def test_settled_needs_every_row_finished_and_at_least_one_row(tmp_path):
    m = tmp_path / "manifest.csv"
    with open(m, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "layer", "status"])
        w.writerows([["a", "P3", "done"], ["b", "P3", "failed"], ["c", "R4", "pending"], ["d", "G", "moved"]])
    assert MS.unsettled(["P3", "G"], m) == {}
    assert set(MS.unsettled(["P3", "R4", "XX"], m)) == {"R4", "XX"}


# ---------------------------------------------------------------- the registered read

def records(e: dict[int, dict[str, list[float]]], coupling=None, dropped=()) -> dict[int, list[dict]]:
    """Per k, one record per seed with tetracene's per-family read-outs."""
    out = {}
    for k, fam in e.items():
        n = len(next(iter(fam.values())))
        out[k] = [{"tetracene": {"diag_rms": {F: fam[F][s] for F in RR.FAMILIES}, "coupling_ratio": (coupling or {}).get(k, 1.0),
                                 "corrected_freq_rms": 3.0, "dropped": list(dropped)}} for s in range(n)]
    return out


def curve(ch_oop: dict[int, list[float]]) -> dict[int, dict[str, list[float]]]:
    """Every family well inside the line except CH-oop, which follows the given seed values."""
    return {k: {"CH-stretch": [1.0, 1.1, 0.9], "CH-oop": ch_oop[k], "ring-ip": [2.0, 2.1, 1.9], "other": [2.2, 2.3, 2.1]} for k in RR.CURVE}


def test_rung_4_holds_when_every_family_meets_the_line():
    res = RR.read(records(curve({0: [4.0] * 3, 10: [3.0, 3.1, 2.9], 20: [2.6, 2.7, 2.5], 30: [2.3, 2.4, 2.2]}), coupling={0: 0.6, 30: 0.4}))
    assert res["verdict"].startswith("rung 4 holds") and res["q4"] == pytest.approx(1.5)


def test_a_miss_that_is_still_learning_is_data_limited():
    res = RR.read(records(curve({0: [5.0] * 3, 10: [4.0, 4.1, 3.9], 20: [3.5, 3.6, 3.4], 30: [3.0, 3.1, 2.9]})))
    assert res["families"]["CH-oop"]["status"] == "data-limited" and res["verdict"].startswith("data-limited")


def test_a_flat_miss_sends_the_read_to_the_search():
    res = RR.read(records(curve({0: [3.2] * 3, 10: [3.1, 3.3, 3.0], 20: [3.0, 3.2, 3.1], 30: [3.0, 3.2, 3.0]})))
    assert res["families"]["CH-oop"]["status"] == "flat miss" and res["verdict"].startswith("no verdict at 30")


def test_a_fall_inside_the_noise_is_not_learning():
    """e(30) below e(10) by less than two combined standard errors is flat (the registered rule, not 'any decrease')."""
    res = RR.read(records(curve({0: [3.5] * 3, 10: [3.0, 3.6, 2.4], 20: [3.1, 3.2, 3.0], 30: [2.7, 3.3, 2.1]})))
    assert res["families"]["CH-oop"]["still_learning"] is False


def test_the_read_refuses_a_set_that_lost_molecules_or_a_missing_k():
    with pytest.raises(SystemExit, match="lost 1 registered"):
        RR.read(records(curve({k: [2.0] * 3 for k in RR.CURVE}), dropped=["R4_x"]))
    recs = records(curve({k: [2.0] * 3 for k in RR.CURVE}))
    del recs[20]
    with pytest.raises(SystemExit, match="need records"):
        RR.read(recs)
    assert RR.report(RR.read(records(curve({k: [2.0] * 3 for k in RR.CURVE}))))[2].startswith("**rung 4 holds")


def test_the_read_is_written_as_json():
    """15 Oct 2026: still_learning returned a numpy bool, which json.dumps refuses; found by the test above before any read."""
    import json
    res = RR.read(records(curve({0: [5.0] * 3, 10: [4.0, 4.1, 3.9], 20: [3.5, 3.6, 3.4], 30: [3.0, 3.1, 2.9]})))
    assert json.loads(json.dumps(res))["families"]["CH-oop"]["still_learning"] is True
