"""Chain 42 (12 Oct 2026): the registered read (q_T and g with their lines) and the wait condition on the ten large-PAH folders."""
import json
import sys
from pathlib import Path

import numpy as np

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
import chain42_read as R  # noqa: E402
import large_pah_ready as LR  # noqa: E402


def _rec(rT, ra, rb=0.3):
    pm = {"T_x": {"corrected_freq_rms": 5.0}, "T_y": {"corrected_freq_rms": 7.0}}
    return {"T": {"coupling_ratio": rT, "corrected_freq_rms": 6.0, "per_molecule": pm}, "a": {"coupling_ratio": ra, "corrected_freq_rms": 3.0},
            "b": {"coupling_ratio": rb, "corrected_freq_rms": 4.0}}


def test_the_read_takes_seed_means_and_applies_the_registered_lines():
    arm0 = [_rec(0.60, 0.30), _rec(0.62, 0.32), _rec(0.58, 0.28)]           # q_T = 0.60 / 0.30 = 2.0 → steep
    arm_d = [_rec(0.48, 0.30)] * 3                                           # g = 0.48 / 0.60 = 0.80 → the lever works
    res = R.read(arm0, arm_d)
    assert np.isclose(res["q_T"], 2.0) and np.isclose(res["g"], 0.8)
    assert res["line_1"].startswith("steep") and res["line_2"].startswith("the lever works")
    assert R.verdicts(1.2, 0.97) == {"line_1": "carries (≤ 1.3)", "line_2": R.verdicts(1.0, 0.99)["line_2"]}
    assert "too few to judge" in R.verdicts(1.5, 0.96)["line_2"] and R.verdicts(1.5, 0.9) == {"line_1": "between: noted", "line_2": "between: noted"}


def test_ready_needs_every_file_and_a_minimum(tmp_path):
    d = tmp_path / "T_x"
    d.mkdir()
    assert LR.state(d) == "no geometry.json"
    for f in ("geometry.json", "hessian_b3lyp_analytic.npz", "hessian_wb97x_analytic.npz"):
        (d / f).write_text("{}")
    np.savez(d / "dipole_b3lyp_cphf.npz", passed=True)
    (d / "result.json").write_text(json.dumps({"labels": "analytic_only"}))
    assert LR.state(d) == "no n_imaginary in result.json"
    (d / "result.json").write_text(json.dumps({"labels": "analytic_only", "n_imaginary_b3lyp": 1, "n_imaginary_wb97x": 0}))
    assert LR.state(d).startswith("IMAGINARY")
    (d / "result.json").write_text(json.dumps({"labels": "analytic_only", "n_imaginary_b3lyp": 0, "n_imaginary_wb97x": 0}))
    assert LR.state(d) == "ready" and LR.apt_passed(d)


def test_a_failed_apt_does_not_hold_the_run_and_is_named(tmp_path):
    d = tmp_path / "T_x"
    d.mkdir()
    for f in ("geometry.json", "hessian_b3lyp_analytic.npz", "hessian_wb97x_analytic.npz"):
        (d / f).write_text("{}")
    np.savez(d / "dipole_b3lyp_cphf.npz", passed=False, sum_rule_max=7.9e-4)
    (d / "result.json").write_text(json.dumps({"labels": "analytic_only", "n_imaginary_b3lyp": 0, "n_imaginary_wb97x": 0}))
    assert LR.state(d) == "ready" and not LR.apt_passed(d)


def test_the_frozen_lists_hold_the_four_and_the_six():
    ids = LR.ids()
    assert len(ids) == 10 and sum(i.startswith("T_") for i in ids) == 4 and sum(i.startswith("D_") for i in ids) == 6
