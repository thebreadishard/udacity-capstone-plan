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


SOUND_FREQ = [0.01, -0.02, 0.03, 0.0, -0.01, 0.02, 150.0, 410.0, 900.0, 3100.0]   # six near-zero entries, then the vibrations


def _folder(tmp_path, b3lyp_freq=SOUND_FREQ, wb97x_freq=SOUND_FREQ, apt_passed=True, result=None):
    d = tmp_path / "T_x"
    d.mkdir()
    (d / "geometry.json").write_text("{}")
    np.savez(d / "hessian_b3lyp_analytic.npz", freq_cm=np.array(b3lyp_freq))
    np.savez(d / "hessian_wb97x_analytic.npz", freq_cm=np.array(wb97x_freq))
    np.savez(d / "dipole_b3lyp_cphf.npz", passed=apt_passed)
    (d / "result.json").write_text(json.dumps(result or {"labels": "analytic_only", "n_imaginary_b3lyp": 0, "n_imaginary_wb97x": 0}))
    return d


def test_ready_needs_every_file_and_a_minimum(tmp_path):
    assert LR.state(tmp_path) == "no geometry.json"
    d = _folder(tmp_path, b3lyp_freq=[*SOUND_FREQ, -120.0])
    assert LR.state(d).startswith("IMAGINARY (1, 0)")
    (d / "result.json").write_text(json.dumps({"labels": "fd"}))
    assert LR.state(d) == "result.json not analytic_only"


def test_a_sound_folder_is_ready_without_counts_in_result_json(tmp_path):
    d = _folder(tmp_path, result={"labels": "analytic_only"})
    assert LR.state(d) == "ready" and LR.apt_passed(d)


def test_a_mode_above_the_old_minus_ten_threshold_is_refused(tmp_path):
    """TASKS 198: result.json written at the -10 cm-1 threshold says zero for a -7 cm-1 mode; the trainer's count, and so this check, says one."""
    d = _folder(tmp_path, wb97x_freq=[*SOUND_FREQ[:6], -7.0, *SOUND_FREQ[7:]])
    result = json.loads((d / "result.json").read_text())
    assert result["n_imaginary_b3lyp"] == 0 and result["n_imaginary_wb97x"] == 0    # what the old check read: it passed
    assert LR.state(d) == "IMAGINARY (0, 1): re-optimise at the label settings"


def test_a_failed_apt_does_not_hold_the_run_and_is_named(tmp_path):
    d = _folder(tmp_path, apt_passed=False)
    assert LR.state(d) == "ready" and not LR.apt_passed(d)


def test_the_frozen_lists_hold_the_four_and_the_six():
    ids = LR.ids()
    assert len(ids) == 10 and sum(i.startswith("T_") for i in ids) == 4 and sum(i.startswith("D_") for i in ids) == 6
