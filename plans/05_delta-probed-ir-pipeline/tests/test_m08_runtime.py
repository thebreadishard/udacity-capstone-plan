"""The pipeline's laptop-time estimate (`modules/08_industry_synthesis/m08/runtime.py`, TASKS 151) on synthetic result folders: the fit, the
half-hour line, which runs count, and the refusals; and on the recorded runs, against what they took."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from pin_tools import PLAN

sys.path.insert(0, str(PLAN / "modules" / "08_industry_synthesis"))
from m08 import runtime as RT

LAPTOP = "Asus18"
BENZENE, NAPHTHALENE, ANTHRACENE = "c1ccccc1", "c1ccc2ccccc2c1", "c1ccc2cc3ccccc3cc2c1"     # 102, 166, 230 basis functions


def run(root: Path, name: str, smiles: str, seconds: float, host: str = LAPTOP, threads: int = 6) -> None:
    d = root / "pipeline_x" / name
    d.mkdir(parents=True)
    rec = {"input": {"smiles": smiles}, "settings": {"threads": threads}, "provenance": {"host": host},
           "seconds": {"optimise": 0.0, "low_level": seconds}}
    (d / "pipeline.json").write_text(json.dumps(rec), encoding="utf-8")


def cubic(n: int) -> float:
    return 360.0 * (n / 102) ** 3


def test_a_cubic_law_is_recovered_with_its_half_hour_line(tmp_path):
    for name, smi, n in (("b", BENZENE, 102), ("n", NAPHTHALENE, 166), ("a", ANTHRACENE, 230)):
        run(tmp_path, name, smi, cubic(n))
    e = RT.estimate("Cc1ccc2ccccc2c1", 6, tmp_path)                      # 185 functions
    assert e["exponent"] == pytest.approx(3.0, abs=1e-6) and e["seconds"] == round(cubic(185))
    assert e["half_hour_functions"] == int(102 * (1800 / 360) ** (1 / 3)) and not e["within_half_hour"]
    assert RT.estimate(BENZENE, 6, tmp_path)["within_half_hour"]


def test_only_laptop_runs_at_the_same_threads_count(tmp_path):
    run(tmp_path, "b", BENZENE, cubic(102))
    run(tmp_path, "n", NAPHTHALENE, cubic(166))
    run(tmp_path, "server", ANTHRACENE, 10.0, host="ubuntu-32gb-hel1-2")
    run(tmp_path, "eight", ANTHRACENE, 10.0, threads=8)
    assert [r[0] for r in RT.timed_runs(6, tmp_path)] == [102, 166]
    with pytest.raises(ValueError, match="fewer than three sizes"):
        RT.estimate(BENZENE, 6, tmp_path)
    assert RT.announce(BENZENE, 6).startswith(("estimated", "no time estimate"))   # the real results folder: one or the other
    assert RT.announce(None, 6).startswith("no time estimate for an xyz input")


def test_two_runs_of_one_size_are_not_three_sizes(tmp_path):
    run(tmp_path, "b1", BENZENE, 350.0)
    run(tmp_path, "b2", "C1=CC=CC=C1", 360.0)
    run(tmp_path, "n", NAPHTHALENE, cubic(166))
    with pytest.raises(ValueError, match="fewer than three sizes"):
        RT.estimate(BENZENE, 6, tmp_path)


def test_the_recorded_runs_are_met_within_ten_percent():
    runs = RT.timed_runs(6)
    if len({n for n, _, _ in runs}) < 3:
        pytest.skip("fewer than three timed sizes in probes/results_m1 on this machine")
    for _, seconds, folder in runs:
        smiles = json.loads((RT.RESULTS / folder / "pipeline.json").read_text(encoding="utf-8"))["input"]["smiles"]
        assert RT.estimate(smiles, 6)["seconds"] == pytest.approx(seconds, rel=0.10), folder
