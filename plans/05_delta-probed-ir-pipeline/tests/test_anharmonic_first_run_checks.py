"""The first real run's four checks (probes/results_m1/anharmonic_step_2026-11-16/first_run_checks.py, TASKS 211) on the
stored-field certificate as a stand-in for the run: against itself checks 1–3 pass and check 4 fails (a stored field was never
timed); a copy with a time and a peak passes all four; and each check fails on a copy spoiled for it. Also the guard that goes
with the default: no committed launcher of the pipeline asks for the anharmonic step except the one run spec of that first run."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

PLAN = Path(__file__).resolve().parents[1]
FOLDER = PLAN / "probes" / "results_m1" / "anharmonic_step_2026-11-16"
spec = importlib.util.spec_from_file_location("first_run_checks", FOLDER / "first_run_checks.py")
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)


def copy(tmp_path: Path, spoil=None, timed: bool = True) -> Path:
    d = tmp_path / "benzene"
    d.mkdir()
    rec = json.loads((C.REFERENCE / "pipeline.json").read_text(encoding="utf-8"))
    if timed:
        rec["spectra"]["anharmonic"]["field"] = {"seconds": 1130.0, "peak_memory_mb": 612, "unit": "m08-anharmonic-benzene-0123456789"}
    if spoil:
        spoil(sorted(rec["spectra"]["network"]["sticks"], key=lambda s: s["omega_cm"]))
    (d / "pipeline.json").write_text(json.dumps(rec), encoding="utf-8")
    return d


def test_the_stored_certificate_against_itself_fails_only_the_check_it_cannot_meet():
    res = C.checks(C.REFERENCE)
    assert [res[k]["passed"] for k in sorted(k for k in res if k[0].isdigit())] == [True, True, True, False] and res["passed"] is False
    assert res["2_no_band_lost"]["stepped"] == {"run": 28, "reference": 28, "of": 30} and res["3_degenerate_pairs_equal"]["pairs"] >= 8
    assert res["4_time_and_memory_recorded"]["peak_memory_mb"] is None


def test_a_run_like_the_reference_with_its_time_and_memory_passes_all_four(tmp_path, capsys):
    assert C.main([str(copy(tmp_path))]) == 0
    assert "ALL FOUR PASSED: the default may become 120" in capsys.readouterr().out
    assert json.loads((tmp_path / "benzene" / "first_run_checks.json").read_text(encoding="utf-8"))["passed"] is True


def _shift(sticks: list[dict]) -> None:
    sticks[18]["anharmonic"]["delta_anh_cm"] += 1.5          # bands 18 and 12 are no pair's members


def _lose(sticks: list[dict]) -> None:
    sticks[12]["anharmonic"].update(delta_anh_cm=None, reason="no-xtb-partner")


def _split_pair(sticks: list[dict]) -> None:
    pair = next(i for i in range(5, 29) if abs(sticks[i]["omega_cm"] - sticks[i + 1]["omega_cm"]) < 0.05)
    sticks[pair]["anharmonic"]["delta_anh_cm"] += 0.4


@pytest.mark.parametrize(("spoil", "timed", "failed"), [(_shift, True, "1_steps_within_tolerance"), (_lose, True, "2_no_band_lost"),
                                                        (_split_pair, True, "3_degenerate_pairs_equal"),
                                                        (None, False, "4_time_and_memory_recorded")])
def test_each_check_fails_on_a_run_spoiled_for_it(tmp_path, spoil, timed, failed):
    d = copy(tmp_path, spoil, timed)
    res = C.checks(d)
    assert res[failed]["passed"] is False and res["passed"] is False and C.main([str(d)]) == 1
    assert all(res[k]["passed"] for k in res if k[0].isdigit() and k != failed)


def test_another_molecule_is_not_compared(tmp_path):
    d = copy(tmp_path, lambda sticks: sticks[3].update(omega_cm=sticks[3]["omega_cm"] + 5.0))
    with pytest.raises(SystemExit, match="not the same molecule"):
        C.checks(d)


def test_no_committed_launcher_starts_the_force_field_unasked():
    """The pipeline's default is off (TASKS 211) until the first real run has passed these checks; with it, a launcher starts a
    GFN2-xTB force field only by naming a budget. One run spec does — the first real run's — and nothing else that starts the
    pipeline: not the demo rerun, not the show batch, not another spec."""
    asking = []
    for path in [*sorted((PLAN / "probes").glob("*.sh")), *sorted((PLAN / "probes").glob("*.py")), *sorted((PLAN / "tools").glob("*")),
                 *sorted((PLAN / "probes" / "runspecs").glob("*.json"))]:
        if path.is_file() and path.suffix in (".sh", ".py", ".json", ".ps1"):
            text = path.read_text(encoding="utf-8", errors="replace")
            if "m08.pipeline" in text and "--anharmonic-minutes" in text:
                asking.append(path.name)
    assert asking == ["pipeline_benzene_anharmonic.json"]
