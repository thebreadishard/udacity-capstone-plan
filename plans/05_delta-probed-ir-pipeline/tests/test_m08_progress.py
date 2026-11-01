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
