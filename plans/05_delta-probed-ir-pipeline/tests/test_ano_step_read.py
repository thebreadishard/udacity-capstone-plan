"""The ANO test's read (`probes/ano_step_read.py`, TASKS 300) on synthetic records, before the run: the registered lines at their edges,
the basis-set-limit formula, and — through row files written here from Hessians we hold — a step that repeats the conventional one
(NO GAIN), a limit recipe whose n⁻³ part must cancel, a composite that is the full CCSD(T)/cc-pVTZ Hessian (its 25 November numbers),
and the cases the read must refuse or leave without an outcome: a target with imaginary modes, a Newton step too long, a missing or
mislabelled row file, a control that does not repeat, a fitting check over its line."""
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
import dfmp2_rows as D  # noqa: E402

INPUTS = A.Inputs()
HELD = all(p.exists() for p in (INPUTS.force_field / "qff_report.npz", INPUTS.corpus / "geometry.json", INPUTS.cc_dz, INPUTS.cc_tz,
                                INPUTS.mp2_dz_conventional, INPUTS.mp2_tz_conventional))
needs_held = pytest.mark.skipif(not HELD, reason="benzene's held Hessians and force field (git-ignored data) are not in this checkout")
CH, OOP, IP = "C-H stretch", "out of plane", "other in plane"


def rms(ch: float, oop: float, ip: float) -> dict[str, float]:
    return {CH: ch, OOP: oop, IP: ip}


CONTROL = rms(7.5, 30.0, 9.0)


# ---------------------------------------------------------------- the formulas and the lines, no data

def test_basis_limit_removes_an_inverse_cube_error():
    rng = np.random.default_rng(0)
    scf, limit, slope = rng.normal(size=(3, 4, 4))
    M = {"scf_ccpvtz": scf + 0.3, "scf_ccpvqz": scf, "mp2_ccpvtz": scf + 0.3 + limit + slope / 27, "mp2_ccpvqz": scf + limit + slope / 64}
    np.testing.assert_allclose(A.basis_limit(M), scf + limit, atol=1e-12)
    M |= {"mp2_ccpwcvtz_fc": slope, "mp2_ccpwcvtz_ae": slope + 0.25}
    np.testing.assert_allclose(A.with_core_valence(M), scf + limit + 0.25, atol=1e-12)


def test_every_recipe_names_row_files_the_lane_writes():
    for recipe in A.RECIPES.values():
        assert set(recipe.labels) <= set(A.EXPECTED)
    assert set(A.FITTING_CHECKED) <= set(A.EXPECTED)
    assert sorted((m for group in A.GROUPS.values() for m in group), key=A.MODES.index) == A.MODES
    assert [len(v) for v in A.GROUPS.values()] == [4, 6, 10]


@pytest.mark.parametrize(("recipe", "word"), [
    (rms(2.0, 2.0, 2.0), "PASS"),                 # at the line is under it
    (rms(2.0, 2.5, 2.0), "USEFUL"),
    (rms(8.5, 10.0, 10.0), "USEFUL"),             # out of plane at 10.0, both others exactly 1.0 above the control
    (rms(8.75, 10.0, 9.0), "BETWEEN"),            # a C–H group 1.25 above the control
    (rms(7.5, 10.5, 9.0), "BETWEEN"),
    (rms(7.5, 25.0, 9.0), "BETWEEN"),             # lowered by exactly 5.0
    (rms(7.5, 25.5, 9.0), "NO GAIN"),
    (rms(7.5, 35.0, 9.0), "NO GAIN"),             # worse than the control
])
def test_outcome_at_the_registered_lines(recipe, word):
    assert A.outcome({"1": CONTROL, "2": recipe}, {})[0] == word


def test_outcome_takes_the_best_recipe_and_never_the_control():
    assert A.outcome({"1": rms(1.0, 1.0, 1.0), "2": rms(1.0, 1.5, 1.0), "3": rms(1.0, 0.5, 3.0)}, {})[0] == "PASS"
    word, sentence = A.outcome({"1": CONTROL, "2": rms(7.5, 29.0, 9.0), "5": rms(7.5, 9.0, 9.0), "6": rms(1.0, 40.0, 1.0)}, {})
    assert word == "USEFUL" and "recipe(s) 5:" in sentence


def test_an_unread_recipe_forbids_no_gain_but_not_useful():
    assert A.outcome({"1": CONTROL, "2": rms(7.5, 29.0, 9.0)}, {"5": "imaginary"})[0] == "NO OUTCOME"
    assert A.outcome({"1": CONTROL, "2": rms(7.5, 9.0, 9.0)}, {"5": "imaginary"})[0] == "USEFUL"


def test_verdict_without_a_control_that_repeats():
    conventional = rms(7.6, 30.2, 8.9)
    assert A.verdict({"2": CONTROL}, conventional, {"1": "no row file"}, False)[0] == "NO OUTCOME"
    assert A.verdict({"1": rms(7.6, 30.75, 8.9), "2": rms(1.0, 1.0, 1.0)}, conventional, {}, False)[0] == "CONTROL FAILED"
    assert A.verdict({"1": rms(8.0, 30.5, 9.25), "2": rms(1.0, 1.0, 1.0)}, conventional, {}, False)[0] == "PASS"
    assert A.verdict({"1": rms(7.6, 30.2, 8.9), "2": rms(1.0, 1.0, 1.0)}, conventional, {"5": "no row file"}, True)[0] == "PARTIAL"
    assert A.verdict({"1": rms(7.6, 30.2, 8.9)}, conventional, {}, False)[0] == "NO OUTCOME"


def test_named_averages_a_degenerate_pair_and_refuses_a_wrong_count():
    freq, keys = [], []
    for name, (sp, ref) in A.REF.items():
        twice = abs(A.KEY[sp][2]) == 1
        freq += [ref - 1.0, ref + 3.0] if twice else [ref]
        keys += [A.KEY[sp]] * (2 if twice else 1)
        assert name in A.MODES
    out = A.named(np.array(freq), keys)
    assert out["ω1"] == pytest.approx(1006.6) and out["ω16"] == pytest.approx(407.3) and out["ω20"] == pytest.approx(3196.1)
    assert A.group_rms({m: A.REF[m][1] + 2.0 for m in A.MODES}) == pytest.approx(rms(2.0, 2.0, 2.0))
    with pytest.raises(A.Unreadable, match="modes of ours"):
        A.named(np.array([*freq[:-1], 50.0]), [*keys[:-1], A.KEY["a2u"]])


# ---------------------------------------------------------------- through row files, on the Hessians we hold

@pytest.fixture(scope="module")
def held():
    frame, sym, x0 = A.load_frame(INPUTS)
    cc, mp2 = A.conventional_parts(INPUTS, sym, x0)
    return frame, cc, mp2


def write_rows(run: Path, label: str, H: np.ndarray, *, basis: str | None = None, fitting: str = "cc-pvqz-jkfit / cc-pvqz-ri") -> None:
    """A row file as dfmp2_rows.py writes it, its rows cut from H; '<label>_fit5z' holds the plan's first row only."""
    base = label.removesuffix("_fit5z")
    expected_basis, kind, frozen = A.EXPECTED[base]
    plan = D.plan_from_geometry(str(INPUTS.corpus / "geometry.json"), basis or expected_basis)
    plan = replace(plan, frozen=plan.frozen if frozen is None else frozen)
    ks = plan.ks[:1] if label.endswith("_fit5z") else plan.ks
    D.save_rows(run / f"rows_{label}.npz", plan, {k: H[k] for k in ks}, f"{kind} psi4 fake ({fitting}, frozen {plan.frozen})")


def write_run(run: Path, mp2: dict[str, np.ndarray], **other: np.ndarray) -> Path:
    """Every row file of the lane: each MP2 target the conventional cc-pVTZ Hessian, the SCF rows equal in both basis sets, no
    core-valence term — so every recipe is the conventional composite — except the labels given in `other`."""
    run.mkdir()
    M = {label: mp2["dz"] if label == A.STEP_FROM else 0.8 * mp2["tz"] if label.startswith("scf") else mp2["tz"] for label in A.EXPECTED}
    M |= other
    for label, H in M.items():
        write_rows(run, label, H)
    for label in A.FITTING_CHECKED:
        write_rows(run, f"{label}_fit5z", M[label], fitting=A.FIVE_ZETA_FITTING)
    return run


@needs_held
def test_rows_of_the_conventional_step_repeat_it(held, tmp_path):
    _, _, mp2 = held
    record = A.read(write_run(tmp_path / "rows", mp2), INPUTS, partial=False)
    assert record["outcome"] == "NO GAIN" and record["unread"] == {}
    assert sorted(record["recipes"]) == sorted(A.RECIPES)
    for recipe in record["recipes"].values():
        assert recipe["rms"] == pytest.approx(record["conventional"]["rms"], abs=1e-3)
    assert record["conventional"]["rms"] == pytest.approx(A.CONVENTIONAL_PINS, abs=A.PIN_TOLERANCE)
    assert record["fitting_change"] == {"mp2_anopvqz": 0.0, "mp2_roosanotz": 0.0}
    text = A.report(record)
    assert "**Outcome: NO GAIN**" in text and "| ω4 | b2g | 712.4 | 708.8 |" in text and "under the line 1e-06" in text
    assert "artefact sits in the coupled-cluster part" in text      # ω5 and ω17: +7.1 and +8.1 between the two basis sets, from what we hold


@needs_held
def test_limit_recipe_cancels_an_inverse_cube_part_through_the_files(held, tmp_path):
    _, _, mp2 = held
    slope = 20.0 * (mp2["tz"] - mp2["dz"])
    record = A.read(write_run(tmp_path / "rows", mp2, mp2_ccpvtz=mp2["tz"] + slope / 27, mp2_ccpvqz=mp2["tz"] + slope / 64), INPUTS, False)
    assert record["outcome"] == "CONTROL FAILED"                    # the control's target carries slope/27; the limit must not
    for key in ("6", "7"):
        assert record["recipes"][key]["rms"] == pytest.approx(record["conventional"]["rms"], abs=1e-3)
    assert record["recipes"]["2"]["rms"][CH] != pytest.approx(record["conventional"]["rms"][CH], abs=0.05)


@needs_held
def test_a_step_that_makes_the_full_cc_tz_hessian_reads_as_it_did(held, tmp_path):
    frame, cc, mp2 = held
    record = A.read(write_run(tmp_path / "rows", mp2, mp2_ccpvqz=mp2["dz"] + cc["tz"] - cc["dz"]), INPUTS, False)
    assert record["recipes"]["2"]["rms"] == pytest.approx(rms(3.7, 27.0, 6.1), abs=0.06)      # benzene_geometry_term.txt, 25 Nov
    assert record["recipes"]["2"]["rms"] == pytest.approx(A.group_rms(A.reading(frame, cc["tz"]).corrected), abs=0.05)
    assert record["outcome"] == "NO GAIN"


@needs_held
def test_a_target_with_imaginary_modes_is_left_unread(held, tmp_path):
    _, cc, mp2 = held
    upside_down = mp2["tz"] - 1.5 * (cc["dz"] + mp2["tz"] - mp2["dz"])
    record = A.read(write_run(tmp_path / "rows", mp2, mp2_anopvqz=upside_down), INPUTS, False)
    assert "imaginary" in record["unread"]["5"] and "5" not in record["recipes"]
    assert record["outcome"] == "NO OUTCOME" and "Recipe 5 not read" in A.report(record)


@needs_held
def test_a_soft_hessian_is_refused_for_its_newton_step(held):
    frame, cc, _ = held
    with pytest.raises(A.Unreadable, match="Newton step"):
        A.reading(frame, 0.01 * cc["tz"])


@needs_held
def test_missing_rows_stop_the_read_unless_partial(held, tmp_path):
    _, _, mp2 = held
    run = write_run(tmp_path / "rows", mp2)
    (run / "rows_mp2_ccpvqz.npz").unlink()
    with pytest.raises(SystemExit, match="mp2_ccpvqz"):
        A.read(run, INPUTS, partial=False)
    record = A.read(run, INPUTS, partial=True)
    assert record["outcome"] == "PARTIAL" and sorted(record["unread"]) == ["2", "6", "7"] and sorted(record["recipes"]) == ["1", "3", "5"]
    (run / "rows_mp2_ccpvdz.npz").unlink()
    with pytest.raises(SystemExit, match="every recipe needs"):
        A.read(run, INPUTS, partial=True)


@needs_held
def test_a_row_file_of_another_level_is_refused(held, tmp_path):
    _, _, mp2 = held
    run = write_run(tmp_path / "rows", mp2)
    write_rows(run, "mp2_ccpvqz", mp2["tz"], basis="cc-pvtz")
    with pytest.raises(SystemExit, match=r"holds DF-MP2 psi4 fake .* at cc-pvtz"):
        A.read(run, INPUTS, partial=False)
    write_rows(run, "mp2_ccpvqz", mp2["tz"])
    D.save_rows(run / "rows_scf_ccpvqz.npz", D.plan_from_geometry(str(INPUTS.corpus / "geometry.json"), "cc-pvqz"),
                {}, "DF-MP2 psi4 fake (cc-pvqz-jkfit / cc-pvqz-ri, frozen 6)")
    with pytest.raises(SystemExit, match="'scf_ccpvqz' is DF-SCF"):
        A.read(run, INPUTS, partial=False)


@needs_held
def test_fitting_check_over_its_line_and_a_fit_file_of_the_wrong_sets(held, tmp_path):
    _, _, mp2 = held
    run = write_run(tmp_path / "rows", mp2)
    write_rows(run, "mp2_anopvqz_fit5z", mp2["tz"] + 1e-5, fitting=A.FIVE_ZETA_FITTING)
    record = A.read(run, INPUTS, partial=False)
    assert record["fitting_change"]["mp2_anopvqz"] == pytest.approx(1e-5)
    assert "mp2_anopvqz: largest change of the row with cc-pV5Z fitting sets 1.0e-05 E_h/bohr² (NOT under" in A.report(record)
    write_rows(run, "mp2_anopvqz_fit5z", mp2["tz"])
    with pytest.raises(SystemExit, match="expected one row made with cc-pv5z"):
        A.read(run, INPUTS, partial=False)


@needs_held
def test_main_writes_the_report_and_the_record(held, tmp_path, monkeypatch, capsysbinary):
    _, _, mp2 = held
    run = write_run(tmp_path / "rows", mp2)
    monkeypatch.setattr(sys, "argv", ["ano_step_read.py", str(run), str(tmp_path / "read")])
    assert A.main() == 0
    assert json.loads((tmp_path / "read.json").read_text(encoding="utf-8"))["outcome"] == "NO GAIN"
    assert (tmp_path / "read.md").read_text(encoding="utf-8") == capsysbinary.readouterr().out.decode("utf-8")
