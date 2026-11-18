"""A run's progress record for the live show (`modules/08_industry_synthesis/m08/progress.py`, pipeline 0.9): the six stations' states in
order, refusals for an unknown step, a step done before it started and a finish with steps left, and a record read back to be finished."""
from __future__ import annotations

import json
import sys

import pytest

from pin_tools import PLAN

sys.path.insert(0, str(PLAN / "modules" / "08_industry_synthesis"))
from m08.progress import FILE, STEPS, Progress


def read(folder):
    return json.loads((folder / FILE).read_text(encoding="utf-8"))


def test_a_new_record_has_every_station_pending(tmp_path):
    Progress(tmp_path, "benzene", "0.9", {"formula": "C6H6"})
    rec = read(tmp_path)
    assert [rec["steps"][s]["state"] for s in STEPS] == ["pending"] * 6 and not rec["finished"] and rec["molecule"]["formula"] == "C6H6"


def test_the_states_follow_the_run(tmp_path):
    p = Progress(tmp_path, "x", "0.9", {})
    for s in ("molecule", "geometry"):
        p.start(s)
        p.done(s)
    p.reused("optimise", 30.5)
    p.reused("hessian", 3212)
    p.start("network")
    assert read(tmp_path)["steps"]["network"]["state"] == "active"
    p.done("network")
    p.start("spectrum")
    p.done("spectrum")
    rec = read(tmp_path)
    assert rec["steps"]["optimise"] == {"state": "reused", "seconds_then": 30.5}
    assert rec["steps"]["geometry"]["state"] == "done" and rec["steps"]["geometry"]["seconds"] >= 0
    Progress.load(tmp_path).finish()
    assert read(tmp_path)["finished"] and not list(tmp_path.glob("*.tmp"))


@pytest.mark.parametrize("act, message", [
    (lambda p: p.start("lunch"), "unknown step"),
    (lambda p: p.done("network"), "never started"),
    (lambda p: p.finish(), "steps not done"),
])
def test_what_cannot_happen_is_refused(tmp_path, act, message):
    with pytest.raises(ValueError, match=message):
        act(Progress(tmp_path, "x", "0.9", {}))


def test_a_run_that_stops_marks_its_step_and_says_why(tmp_path):
    p = Progress(tmp_path, "x", "0.12", {})
    p.start("molecule")
    p.done("molecule")
    p.start("geometry")
    p.fail("failed: RuntimeError: boom")
    rec = read(tmp_path)
    assert rec["steps"]["geometry"]["state"] == "failed" and rec["failed"] == {"reason": "failed: RuntimeError: boom"} and not rec["finished"]


def test_a_delivered_run_keeps_its_delivery_when_something_stops_after_it(tmp_path):
    p = Progress(tmp_path, "x", "0.12", {})
    for s in STEPS:
        p.start(s)
        p.done(s)
    p.delivered(1, "first", final=False)
    p.fail("interrupted (Ctrl-C)")
    rec = read(tmp_path)
    assert rec["finished"] and "failed" not in rec


def test_a_refused_run_s_record_can_be_taken_over_and_nothing_else_can(tmp_path):
    folder = tmp_path / "mol"
    Progress.refused(folder, "mol", "0.12", {"given": "CCO"}, "refused: no aromatic ring")
    assert Progress.refused_only(folder) and read(folder)["failed"]["before_start"]
    (folder / "pipeline.json").write_text("{}", encoding="utf-8")
    assert not Progress.refused_only(folder)
    other = tmp_path / "other"
    other.mkdir()
    Progress(other, "other", "0.12", {})
    assert not Progress.refused_only(other)
