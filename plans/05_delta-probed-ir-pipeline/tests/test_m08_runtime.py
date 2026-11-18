"""The pipeline's laptop-time estimate (`modules/08_industry_synthesis/m08/runtime.py`, TASKS 151) on synthetic result folders: the fit, the
half-hour line and its warning, which runs count — the laptop's, at the thread count, on one pyscf version — and the refusals; and on the
recorded runs, against what they took."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from pin_tools import PLAN

sys.path.insert(0, str(PLAN / "modules" / "08_industry_synthesis"))
from m08 import pipeline as P
from m08 import runtime as RT

LAPTOP = "Asus18"
OLD, NEW = "2.14.0", "2.15.0"
BENZENE, NAPHTHALENE, ANTHRACENE = "c1ccccc1", "c1ccc2ccccc2c1", "c1ccc2cc3ccccc3cc2c1"     # 102, 166, 230 basis functions


def run(root: Path, name: str, smiles: str, seconds: float, **where: object) -> None:
    """A finished computed run's record; `where` overrides the host, the thread count and step 3's pyscf version."""
    w = {"host": LAPTOP, "threads": 6, "pyscf": OLD} | where
    d = root / "pipeline_x" / name
    d.mkdir(parents=True)
    rec = {"input": {"smiles": smiles}, "settings": {"threads": w["threads"]}, "provenance": {"host": w["host"]},
           "seconds": {"optimise": 0.0, "low_level": seconds}, "low_level": {"b3lyp": {"software": {"pyscf": w["pyscf"]}}}}
    (d / "pipeline.json").write_text(json.dumps(rec), encoding="utf-8")


def cubic(n: int) -> float:
    return 360.0 * (n / 102) ** 3


def test_a_cubic_law_is_recovered_with_its_half_hour_line(tmp_path):
    for name, smi, n in (("b", BENZENE, 102), ("n", NAPHTHALENE, 166), ("a", ANTHRACENE, 230)):
        run(tmp_path, name, smi, cubic(n))
    e = RT.estimate("Cc1ccc2ccccc2c1", 6, OLD, tmp_path)                      # 185 functions
    assert e["exponent"] == pytest.approx(3.0, abs=1e-6) and e["seconds"] == round(cubic(185))
    assert e["half_hour_functions"] == int(102 * (1800 / 360) ** (1 / 3)) and not e["within_half_hour"]
    assert RT.estimate(BENZENE, 6, OLD, tmp_path)["within_half_hour"]


def test_past_the_half_hour_the_line_warns_and_within_it_does_not(tmp_path):
    for name, smi, n in (("b", BENZENE, 102), ("n", NAPHTHALENE, 166), ("a", ANTHRACENE, 230)):
        run(tmp_path, name, smi, cubic(n))
    beyond = RT.announce(ANTHRACENE, 6, OLD, tmp_path)
    assert beyond.startswith("WARNING: the estimate passes the demo's half hour (30 min)") and "on pyscf 2.14.0" in beyond
    assert RT.announce(BENZENE, 6, OLD, tmp_path).startswith("estimated laptop time")


def test_the_fit_never_mixes_pyscf_versions(tmp_path):
    """Step 3 moved to pyscf 2.15.0 in pipeline 0.10; the timed runs were 2.14.0's. A version without three sizes has no estimate,
    and the line gives the fitted version's time under that version's name."""
    for name, smi, n in (("b", BENZENE, 102), ("n", NAPHTHALENE, 166), ("a", ANTHRACENE, 230)):
        run(tmp_path, name, smi, cubic(n))
    run(tmp_path, "new", BENZENE, 2 * cubic(102), pyscf=NEW)
    run(tmp_path, "unnamed", NAPHTHALENE, 1.0, pyscf=None)
    assert sorted(r[3] or "" for r in RT.timed_runs(6, tmp_path)) == ["", OLD, OLD, OLD, NEW]
    with pytest.raises(ValueError, match=r"on pyscf 2\.15\.0 cover fewer than three sizes"):
        RT.estimate(BENZENE, 6, NEW, tmp_path)
    assert RT.estimate(BENZENE, 6, OLD, tmp_path)["seconds"] == round(cubic(102))       # the 2.15.0 run and the unnamed one stay out
    line = RT.announce(BENZENE, 6, NEW, tmp_path)
    assert line.startswith("no time estimate: 1 timed laptop runs at 6 threads on pyscf 2.15.0")
    assert "another version's time, not this run's: estimated laptop time ≈ 6 min for 102 basis functions on pyscf 2.14.0" in line
    assert RT.fitted_versions(6, tmp_path) == [OLD]
    assert RT.announce(BENZENE, 6, None, tmp_path).startswith("no time estimate: step 3 runs an interpreter given with --pyscf-python")


def test_the_pipeline_asks_for_the_version_step_3_will_run_at_six_threads(tmp_path):
    assert P.PipelineConfig.model_fields["threads"].default == 6 and P.parse_args(["--name", "x", "--out", "o", "--smiles", "C"]).threads == 6
    cfg = P.PipelineConfig(name="x", out_root=tmp_path, smiles="c1ccccc1", models=(Path("m.pt"),), psi4_python=Path(sys.executable))
    assert P.step3_pyscf(cfg) == P.WSL_PYSCF_VERSION == "2.15.0"
    assert P.step3_pyscf(cfg.model_copy(update={"pyscf_python": "~/other/bin/python"})) is None


def test_only_laptop_runs_at_the_same_threads_count(tmp_path):
    run(tmp_path, "b", BENZENE, cubic(102))
    run(tmp_path, "n", NAPHTHALENE, cubic(166))
    run(tmp_path, "server", ANTHRACENE, 10.0, host="ubuntu-32gb-hel1-2")
    run(tmp_path, "eight", ANTHRACENE, 10.0, threads=8)
    assert [r[0] for r in RT.timed_runs(6, tmp_path)] == [102, 166]
    with pytest.raises(ValueError, match="fewer than three sizes"):
        RT.estimate(BENZENE, 6, OLD, tmp_path)
    assert RT.announce(BENZENE, 6, NEW).startswith(("estimated", "WARNING", "no time estimate"))   # the real results folder: any of them
    assert RT.announce(None, 6, NEW).startswith("no time estimate for an xyz input")


def test_two_runs_of_one_size_are_not_three_sizes(tmp_path):
    run(tmp_path, "b1", BENZENE, 350.0)
    run(tmp_path, "b2", "C1=CC=CC=C1", 360.0)
    run(tmp_path, "n", NAPHTHALENE, cubic(166))
    with pytest.raises(ValueError, match="fewer than three sizes"):
        RT.estimate(BENZENE, 6, OLD, tmp_path)


def test_the_recorded_runs_are_met_within_a_quarter():
    # a broken fit misses by factors; the scatter of real runs is up to 18 % (cinnoline, 30 Oct 2026: 1,262 s against 1,485 estimated)
    versions = RT.fitted_versions(6)
    if not versions:
        pytest.skip("fewer than three timed sizes of one pyscf version in probes/results_m1 on this machine")
    for _, seconds, folder, pyscf in RT.timed_runs(6):
        if pyscf in versions:
            smiles = json.loads((RT.RESULTS / folder / "pipeline.json").read_text(encoding="utf-8"))["input"]["smiles"]
            assert RT.estimate(smiles, 6, pyscf)["seconds"] == pytest.approx(seconds, rel=0.25), folder


def test_without_a_fit_on_the_asked_version_the_other_version_answers_labelled(tmp_path):
    for name, smi, n in (("b", BENZENE, 102), ("n", NAPHTHALENE, 166), ("a", ANTHRACENE, 230)):
        run(tmp_path, name, smi, cubic(n))
    assert RT.estimate_or_other(BENZENE, 6, OLD, tmp_path)["other_version"] is False
    e = RT.estimate_or_other(BENZENE, 6, NEW, tmp_path)
    assert e["other_version"] and e["pyscf"] == OLD and e["seconds"] == round(cubic(102))
    assert RT.estimate_or_other(BENZENE, 8, NEW, tmp_path) is None


def test_the_pipeline_says_when_step_3_recorded_another_pyscf(tmp_path):
    cfg = P.PipelineConfig(name="x", out_root=tmp_path, smiles="c1ccccc1", models=(Path("m.pt"),), psi4_python=Path(sys.executable))

    def rec(version, reused=False):
        return {"reuse": {"reused": reused}, "low_level": {"b3lyp": {"software": {"pyscf": version}}}}

    assert P.pyscf_as_recorded(cfg, rec("2.15.0")) is None and P.pyscf_as_recorded(cfg, rec("2.14.0", reused=True)) is None
    assert P.pyscf_as_recorded(cfg, rec("2.16.0")) == "step 3 recorded pyscf 2.16.0; the time estimate assumed 2.15.0"
    other = cfg.model_copy(update={"pyscf_python": "~/other/bin/python"})
    assert P.pyscf_as_recorded(other, rec("2.15.0")) == "step 3 recorded pyscf 2.15.0; the time estimate assumed an unknown version"
