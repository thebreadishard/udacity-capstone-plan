"""The naphthalene read of the ANO test (probes/ano_step_read_naphthalene.py): the registered lines at their edges on made-up
rows, and the read through row files as the lane writes them, built from the Hessians we hold (skipped where the git-ignored
data are absent).
"""
from __future__ import annotations

import json
import sys
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
import ano_step_read as A  # noqa: E402
import ano_step_read_naphthalene as N  # noqa: E402
import dfmp2_rows as D  # noqa: E402

INPUTS = N.Inputs()
GEOMETRY = str(INPUTS.corpus / "geometry.json")
HELD = all(p.exists() for p in (INPUTS.corpus / "geometry.json", INPUTS.cc_dz, INPUTS.mp2_dz, INPUTS.mp2_tz))
needs_held = pytest.mark.skipif(not HELD, reason="naphthalene's held Hessians (git-ignored data) are not in this checkout")


def rows(key_rise: float = 25.0, lowest: float = 0.0, key_ano: float | None = None, **changes) -> list[dict]:
    """Made-up mode rows: the key mode (from the control's −33 unless `key_ano` places it), two more judged out-of-plane modes,
    a butterfly mode far below its fundamental and an in-plane mode far below — the last two must never be judged."""
    out = [{"irrep": "B2g", "nu": 770.0, "out_of_plane": True, "judged": True, "control": -33.0,
            "ano": -33.0 + key_rise if key_ano is None else key_ano,
            "rise": key_rise, "crossing": False},
           {"irrep": "Au", "nu": 970.0, "out_of_plane": True, "judged": True, "control": -15.6, "ano": lowest, "rise": lowest + 15.6,
            "crossing": False},
           {"irrep": "B2g", "nu": 980.0, "out_of_plane": True, "judged": True, "control": -17.1, "ano": 9.0, "rise": 26.1,
            "crossing": False},
           {"irrep": "B3u", "nu": 176.0, "out_of_plane": True, "judged": False, "control": -9.0, "ano": -40.0, "rise": -31.0,
            "crossing": False},
           {"irrep": "Ag", "nu": 758.0, "out_of_plane": False, "judged": False, "control": 7.0, "ano": -40.0, "rise": -47.0,
            "crossing": False}]
    for row in out:
        row.update(changes.get(f"{row['irrep']}_{row['nu']:.0f}", {}))
    return out


@pytest.mark.parametrize(("key_rise", "lowest", "word"), [
    (20.0, -5.0, "TRANSFERS"),            # both lines at their edges
    (19.999, 0.0, "BETWEEN"),
    (40.0, -5.001, "BETWEEN"),
    (10.0, 0.0, "BETWEEN"),
    (9.999, 0.0, "NO TRANSFER"),
    (9.999, -30.0, "NO TRANSFER"),
])
def test_outcome_at_the_registered_lines(key_rise, lowest, word):
    assert N.outcome(rows(key_rise, lowest, key_ano=0.0))[0] == word


def test_the_key_mode_is_itself_judged_against_its_fundamental():
    assert N.outcome(rows(key_rise=25.0))[0] == "BETWEEN"          # −33 + 25 = −8: still more than 5 below
    assert N.outcome(rows(key_rise=28.0))[0] == "TRANSFERS"


def test_unjudged_modes_never_decide():
    assert N.outcome(rows(key_rise=30.0))[0] == "TRANSFERS"         # the butterfly and the in-plane mode sit 40 below


def test_outcome_refuses_rows_without_an_ano_reading():
    with pytest.raises(ValueError, match="nothing to judge"):
        N.outcome(rows(Au_970={"ano": None, "rise": None}))


def test_control_line_at_its_edge():
    held = rows()
    assert N.control_misses(held) == {}
    assert N.control_misses(rows(B2g_770={"control": -33.5})) == {}
    assert N.control_misses(rows(B2g_770={"control": -33.51})) == {"B2g 770": -33.51}
    assert N.control_misses(rows(Au_970={"control": -15.0})) == {"Au 970": -15.0}


def test_verdict_puts_the_control_first_then_missing_files_then_an_unread_hessian():
    off = rows(B2g_980={"control": -10.0})
    assert N.verdict(off, None, None, None)[0] == "CONTROL FAILED"
    assert N.verdict(off, "no row file", None, None)[0] == "CONTROL FAILED"
    assert N.verdict(rows(), "no row file", None, None)[0] == "PARTIAL"
    word, said = N.verdict(rows(), None, "an imaginary mode (-80.0 cm⁻¹)", None)
    assert word == "NO OUTCOME" and "imaginary" in said


def test_every_outcome_carries_the_geometry_note_and_what_else_stands_under_it():
    fitting = {"largest_change": 3e-5, "under_line": False}
    word, said = N.verdict(rows(key_rise=30.0, Au_970={"crossing": True}), None, None, fitting)
    assert word == "TRANSFERS"
    assert "without the geometry term" in said and "fitting check is over its line" in said and "Au 970" in said
    quiet = N.verdict(rows(key_rise=30.0, B3u_176={"crossing": True}), None, None, {"largest_change": 1e-7, "under_line": True})[1]
    assert "fitting" not in quiet and "crossings" not in quiet and "without the geometry term" in quiet


def test_mode_rows_judge_out_of_plane_modes_above_the_butterfly_pair_only():
    control = {("B3u", 176.0): (167.0, False), ("B2g", 770.0): (737.0, False), ("Ag", 758.0): (765.0, True)}
    ano = {("B3u", 176.0): (170.0, False), ("B2g", 770.0): (772.5, True), ("Ag", 758.0): (760.0, False)}
    made = {(r["irrep"], r["nu"]): r for r in N.mode_rows(control, ano)}
    assert [r["judged"] for r in N.mode_rows(control, ano)] == [False, False, True]          # by measured wavenumber: 176, 758, 770
    assert made[("B2g", 770.0)]["rise"] == pytest.approx(35.5) and made[("B2g", 770.0)]["ano"] == pytest.approx(2.5)
    assert made[("B2g", 770.0)]["crossing"] and made[("Ag", 758.0)]["crossing"] and not made[("B3u", 176.0)]["crossing"]
    alone = N.mode_rows(control, None)
    assert all(r["ano"] is None and r["rise"] is None for r in alone)


def test_the_measured_list_names_every_mode_once_and_holds_the_pinned_ones():
    measured = N.experiment()
    assert len(measured) == 48 and set(N.CONTROL_PINS) | {N.KEY_MODE} <= set(measured)
    assert sum(irrep in N.OUT_OF_PLANE for irrep, _ in measured) == 15


# ---------------------------------------------------------------- through the files


@pytest.fixture(scope="module")
def held():
    return N.load_held(INPUTS)


def write_rows(run: Path, label: str, H: np.ndarray, *, ks: tuple[int, ...] | None = None, fit: tuple[str, str] = ("cc-pvqz-jkfit", "cc-pvqz-ri"),
               **plan_fields) -> None:
    """A row file as the lane leaves it, its rows cut from H; '<label>_fit5z' holds the plan's first row, with cc-pV5Z's fitting sets."""
    plan = replace(D.plan_from_geometry(GEOMETRY, "ano-pvqz"), **plan_fields)
    if label.endswith(A.FIT_SUFFIX):
        fit, ks = ("cc-pv5z-jkfit", "cc-pv5z-ri"), ks or plan.ks[:1]
    method = D.method_text("1.10.2", plan, D.Fitting.named_after(plan.basis, *fit), "mp2")
    D.save_rows(run / f"rows_{label}.npz", plan, {k: H[k] for k in ks or plan.ks}, method)


def write_run(run: Path, H: np.ndarray, fit_row: np.ndarray | None = None) -> Path:
    run.mkdir()
    write_rows(run, N.ANO, H)
    write_rows(run, N.ANO + A.FIT_SUFFIX, H if fit_row is None else fit_row)
    return run


@needs_held
def test_the_control_repeats_the_read_of_19_november(tmp_path):
    record = N.read(tmp_path, INPUTS, partial=True)
    assert record["outcome"] == "PARTIAL"
    by_key = {(r["irrep"], r["nu"]): r["control"] for r in record["modes"]}
    for key, pin in N.CONTROL_PINS.items():
        assert by_key[key] == pytest.approx(pin, abs=N.CONTROL_LINE)
    assert sum(r["judged"] for r in record["modes"]) == 13


@needs_held
def test_rows_of_the_cc_pvtz_step_read_as_no_transfer(held, tmp_path):
    record = N.read(write_run(tmp_path / "run", held.mp2_tz), INPUTS, partial=False)
    assert record["outcome"] == "NO TRANSFER"
    assert max(abs(r["rise"]) for r in record["modes"]) < 0.05           # the rows are the control's own Hessian, symmetrised
    assert record["fitting"]["under_line"]


@needs_held
def test_a_stiffer_step_moves_the_key_mode_up_and_is_read(held, tmp_path):
    lifted = held.mp2_tz + 0.02 * (held.cc_dz + held.mp2_tz - held.mp2_dz)     # the whole composite 2 % stiffer: every ω × √1.02
    record = N.read(write_run(tmp_path / "run", lifted), INPUTS, partial=False)
    key = next(r for r in record["modes"] if (r["irrep"], r["nu"]) == N.KEY_MODE)
    assert key["rise"] == pytest.approx(737.4 * (np.sqrt(1.02) - 1), abs=0.3)
    assert record["outcome"] == "NO TRANSFER"                            # 7.3 cm⁻¹: under the 10 line


@needs_held
def test_an_ano_hessian_with_an_imaginary_mode_gives_no_outcome(held, tmp_path):
    soft = held.mp2_tz - 1.2 * (held.cc_dz + held.mp2_tz - held.mp2_dz)
    record = N.read(write_run(tmp_path / "run", soft), INPUTS, partial=False)
    assert record["outcome"] == "NO OUTCOME" and "imaginary" in record["sentence"]


@needs_held
def test_missing_or_unfinished_rows_stop_the_read_unless_partial(held, tmp_path):
    run = tmp_path / "run"
    run.mkdir()
    plan = D.plan_from_geometry(GEOMETRY, "ano-pvqz")
    write_rows(run, N.ANO, held.mp2_tz, ks=plan.ks[:4])
    with pytest.raises(SystemExit, match="holds rows"):
        N.read(run, INPUTS, partial=False)
    assert N.read(run, INPUTS, partial=True)["outcome"] == "PARTIAL"
    write_rows(run, N.ANO, held.mp2_tz)
    with pytest.raises(SystemExit, match="no row file for mp2_anopvqz_fit5z"):
        N.read(run, INPUTS, partial=False)


@needs_held
@pytest.mark.parametrize(("change", "said"), [
    ({"frozen": 6}, "frozen 6"),
    ({"basis": "cc-pvqz"}, "cc-pvqz"),
    ({"step": 0.01}, "step 0.01"),
])
def test_a_row_file_of_another_level_is_refused(held, tmp_path, change, said):
    run = write_run(tmp_path / "run", held.mp2_tz)
    write_rows(run, N.ANO, held.mp2_tz, **change)
    with pytest.raises(SystemExit, match=said):
        N.read(run, INPUTS, partial=False)


@needs_held
def test_a_fit_file_with_the_rows_own_fitting_sets_is_refused(held, tmp_path):
    run = write_run(tmp_path / "run", held.mp2_tz)
    plan = D.plan_from_geometry(GEOMETRY, "ano-pvqz")
    method = D.method_text("1.10.2", plan, D.Fitting.named_after("ano-pvqz", "cc-pvqz-jkfit", "cc-pvqz-ri"), "mp2")
    D.save_rows(run / f"rows_{N.ANO}{A.FIT_SUFFIX}.npz", plan, {plan.ks[0]: held.mp2_tz[plan.ks[0]]}, method)
    with pytest.raises(SystemExit, match="cc-pv5z"):
        N.read(run, INPUTS, partial=False)


@needs_held
def test_fitting_check_over_its_line_is_said_with_the_outcome(held, tmp_path):
    other = held.mp2_tz.copy()
    other[:, 5] += 3e-5
    record = N.read(write_run(tmp_path / "run", held.mp2_tz, fit_row=other), INPUTS, partial=False)
    assert not record["fitting"]["under_line"] and "fitting check is over its line" in record["sentence"]


@needs_held
def test_main_writes_the_report_and_the_record(held, tmp_path, capsysbinary):
    run = write_run(tmp_path / "run", held.mp2_tz)
    assert N.main([str(run), str(tmp_path / "read")]) == 0
    text = (tmp_path / "read.md").read_text(encoding="utf-8")
    record = json.loads((tmp_path / "read.json").read_text(encoding="utf-8"))
    assert "**Outcome: NO TRANSFER**" in text and text.count("| yes |") == 13 and record["outcome"] == "NO TRANSFER"
    assert capsysbinary.readouterr().out.decode("utf-8") == text
