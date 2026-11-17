"""The second version of the real run's four checks (probes/results_m1/anharmonic_step_2026-11-17/first_run_checks.py, TASKS 255):
a step's tolerance is a fraction of its family's bar, differences are compared as the record rounds them. On the stored-field
certificate as a stand-in for a run, and on the first real run's own record, which git holds."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

PLAN = Path(__file__).resolve().parents[1]
FOLDER = PLAN / "probes" / "results_m1" / "anharmonic_step_2026-11-17"
FIRST_RUN = PLAN / "probes" / "results_m1" / "pipeline_benzene_anharmonic_first_run" / "benzene"
spec = importlib.util.spec_from_file_location("first_run_checks_v2", FOLDER / "first_run_checks.py")
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)
#           family: (a band of it in the reference, its tolerance = min(0.3 × bar, 2.0) + 0.1)
BANDS = {"ring-ip": (1388.5, 1.11), "other": (625.1, 1.25), "CH-oop": (701.7, 2.1), "CH-stretch": (3215.7, 1.96)}


def copy(tmp_path: Path, spoil=None, timed: bool = True) -> Path:
    d = tmp_path / "benzene"
    d.mkdir(parents=True)
    rec = json.loads((C.REFERENCE / "pipeline.json").read_text(encoding="utf-8"))
    if timed:
        rec["spectra"]["anharmonic"]["field"] = {"seconds": 1130.0, "peak_memory_mb": 612, "unit": "m08-anharmonic-benzene-0123456789"}
    if spoil:
        spoil(sorted(rec["spectra"]["network"]["sticks"], key=lambda s: s["omega_cm"]))
    (d / "pipeline.json").write_text(json.dumps(rec), encoding="utf-8")
    return d


def moved(position: float, by: float):
    def spoil(sticks: list[dict]) -> None:
        stick = next(s for s in sticks if s["omega_cm"] == position)
        stick["anharmonic"]["delta_anh_cm"] = round(stick["anharmonic"]["delta_anh_cm"] + by, 1)
    return spoil


def test_the_stored_certificate_against_itself_fails_only_the_check_it_cannot_meet():
    res = C.checks(C.REFERENCE)
    assert [res[k]["passed"] for k in sorted(k for k in res if k[0].isdigit())] == [True, True, True, False] and res["passed"] is False
    assert res["2_no_band_lost"]["stepped"] == {"run": 28, "reference": 28, "of": 30}
    assert res["1_steps_within_tolerance"]["tolerance"]["bars_cm"] == {"CH-oop": 8.38, "other": 3.84, "ring-ip": 3.37, "CH-stretch": 6.21}


def test_a_run_like_the_reference_with_its_time_and_memory_passes_all_four(tmp_path, capsys):
    assert C.main([str(copy(tmp_path))]) == 0
    assert "ALL FOUR PASSED" in capsys.readouterr().out


@pytest.mark.parametrize("family", sorted(BANDS))
def test_a_step_may_move_by_three_tenths_of_its_familys_bar_and_two_wavenumbers_at_most(tmp_path, family):
    """At the line (as the record rounds: a difference of 1.9 against 1.96) the check passes; 0.2 further it fails, naming the band."""
    position, line = BANDS[family]
    at = int(line * 10) / 10
    inside = C.checks(copy(tmp_path / "in", moved(position, at)))["1_steps_within_tolerance"]
    assert inside["passed"] and inside["closest_to_its_line"]["difference_cm"] == at and inside["closest_to_its_line"]["tolerance_cm"] == line
    outside = C.checks(copy(tmp_path / "out", moved(position, -(at + 0.2))))["1_steps_within_tolerance"]
    assert not outside["passed"] and [(b["omega_cm"], b["family"], b["tolerance_cm"]) for b in outside["bands_beyond"]] == [(position, family, line)]


def test_a_band_whose_error_was_not_measured_is_held_to_its_familys_bar(tmp_path):
    """733.7 is stepped in family 'other' without a bar of its own (o ≥ 0.8); its tolerance is the family's all the same."""
    ref = next(s for s in C.sticks_of(C.REFERENCE)[0] if s["omega_cm"] == 733.7)
    assert ref["anharmonic"]["bar_cm"] is None and ref["anharmonic"]["family"] == "other"
    assert C.checks(copy(tmp_path / "in", moved(733.7, 1.2)))["1_steps_within_tolerance"]["passed"]
    assert not C.checks(copy(tmp_path / "out", moved(733.7, 1.4)))["1_steps_within_tolerance"]["passed"]


def test_differences_are_compared_as_the_record_rounds_them():
    """−130.9 − (−132.6) is 1.6999999999999886 in binary; the check reads 1.7."""
    stick = {"omega_cm": 3241.6, "anharmonic": {"delta_anh_cm": -132.6, "family": "CH-stretch"}}
    run = [{**stick, "anharmonic": {"delta_anh_cm": -130.9, "family": "CH-stretch"}}]
    near, _ = C.check_steps(run, [stick], {"CH-stretch": 6.21})
    assert near["closest_to_its_line"]["difference_cm"] == 1.7 and near["passed"]
    with pytest.raises(SystemExit, match="no bar for"):
        C.check_steps(run, [stick], {"ring-ip": 3.37})


def test_a_lost_band_a_split_pair_and_an_untimed_field_still_fail(tmp_path):
    def lose(sticks: list[dict]) -> None:
        sticks[12]["anharmonic"].update(delta_anh_cm=None, reason="no-xtb-partner")

    def split(sticks: list[dict]) -> None:
        pair = next(i for i in range(5, 29) if abs(sticks[i]["omega_cm"] - sticks[i + 1]["omega_cm"]) < 0.05)
        sticks[pair]["anharmonic"]["delta_anh_cm"] += 0.4

    assert not C.checks(copy(tmp_path / "a", lose))["2_no_band_lost"]["passed"]
    assert not C.checks(copy(tmp_path / "b", split))["3_degenerate_pairs_equal"]["passed"]
    assert not C.checks(copy(tmp_path / "c", timed=False))["4_time_and_memory_recorded"]["passed"]


def test_the_first_real_runs_record_passes_the_step_check_and_fails_on_its_lost_pair():
    """The run of 17 Nov 2026 as recorded (one-to-one match): its CH stretches at 3241.6 are 1.7 from the reference's, 0.87 of
    their line; the pair at 1691.0 is lost, which is what the set-wise match repairs (replay_runs.txt beside the script)."""
    res = C.checks(FIRST_RUN)
    near = res["1_steps_within_tolerance"]
    assert near["passed"] and near["closest_to_its_line"] == {"difference_cm": 1.7, "of_tolerance": 0.87, "omega_cm": 3241.6,
                                                               "family": "CH-stretch", "tolerance_cm": 1.96}
    assert [b["omega_cm"] for b in res["2_no_band_lost"]["bands_lost"]] == [1691.0, 1691.0] and res["passed"] is False
    assert res["3_degenerate_pairs_equal"]["passed"] and res["4_time_and_memory_recorded"]["passed"]
