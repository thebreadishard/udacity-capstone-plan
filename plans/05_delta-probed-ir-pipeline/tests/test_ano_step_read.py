"""The ANO test's read (`probes/ano_step_read.py`, TASKS 300) on synthetic records, before the run: the registered lines at their edges,
the basis-set-limit formula, and — through row files written here from Hessians we hold, with the method text dfmp2_rows.py writes for
the lane's options — a step that repeats the conventional one (NO GAIN), a limit recipe whose n⁻³ part must cancel, a core-valence
term of the right sign, a composite that is the full CCSD(T)/cc-pVTZ Hessian (its 25 November numbers), and the cases the read must
refuse or leave without an outcome: a target with imaginary modes, a Newton step too long, a missing, unfinished or mislabelled row
file, a control that does not repeat, a fitting check over its line."""
from __future__ import annotations

import copy
import json
import re
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
GEOMETRY = str(INPUTS.corpus / "geometry.json")
HELD = all(p.exists() for p in (INPUTS.force_field / "qff_report.npz", INPUTS.corpus / "geometry.json", INPUTS.cc_dz, INPUTS.cc_tz,
                                INPUTS.mp2_dz_conventional, INPUTS.mp2_tz_conventional))
needs_held = pytest.mark.skipif(not HELD, reason="benzene's held Hessians and force field (git-ignored data) are not in this checkout")
CH, OOP, IP = "C-H stretch", "out of plane", "other in plane"
QZ_FIT = ("cc-pvqz-jkfit", "cc-pvqz-ri")
# probes/ano_step_benzene.sh, label → (basis, --theory, --df-basis-scf, --df-basis-mp2, --frozen-core); None is the option not given
LANE = {"mp2_ccpvdz": ("cc-pvdz", "mp2", None, None, None), "mp2_anopvqz": ("ano-pvqz", "mp2", *QZ_FIT, None),
        "mp2_roosanotz": ("roos-ano-tz", "mp2", *QZ_FIT, None), "mp2_ccpvtz": ("cc-pvtz", "mp2", None, None, None),
        "scf_ccpvtz": ("cc-pvtz", "scf", None, None, None), "mp2_ccpwcvtz_fc": ("cc-pwcvtz", "mp2", "cc-pvtz-jkfit", None, None),
        "mp2_ccpwcvtz_ae": ("cc-pwcvtz", "mp2", "cc-pvtz-jkfit", None, 0), "mp2_ccpvqz": ("cc-pvqz", "mp2", None, None, None),
        "scf_ccpvqz": ("cc-pvqz", "scf", None, None, None)}


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
    assert set(A.EXPECTED) == set(LANE)
    for recipe in A.RECIPES.values():
        assert set(recipe.labels) <= set(LANE)
    assert set(A.FITTING_CHECKED) <= set(LANE)
    assert sorted((m for group in A.GROUPS.values() for m in group), key=A.MODES.index) == A.MODES
    assert [len(v) for v in A.GROUPS.values()] == [4, 6, 10]


def test_the_lane_table_here_is_the_lane_script():
    script = (PLAN / "probes" / "ano_step_benzene.sh").read_text(encoding="utf-8")
    arrays = {name: options.split() for name, options in re.findall(r"^(\w+_FIT)=\((.*)\)$", script, re.MULTILINE)}
    lane = {}
    for line in script.splitlines():
        words = line.split("#")[0].split()
        if len(words) < 3 or words[0] not in ("rows", "with_fit_check") or words[1].startswith('"'):
            continue
        options = arrays["QZ_FIT"] if words[0] == "with_fit_check" else words[3:]
        given = dict(zip(options[::2], options[1::2], strict=True))
        frozen = given.get("--frozen-core")
        lane[words[1]] = (words[2], given.get("--theory", "mp2"), given.get("--df-basis-scf"), given.get("--df-basis-mp2"),
                          None if frozen is None else int(frozen))
    assert lane == LANE
    assert arrays["FIVEZ_FIT"] == ["--df-basis-scf", "cc-pv5z-jkfit", "--df-basis-mp2", "cc-pv5z-ri"]
    assert 'rows "$1" "$2" "${QZ_FIT[@]}"' in script and 'rows "$1_fit5z" "$2" "${FIVEZ_FIT[@]}" --only-row "$k"' in script


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


def test_an_unread_recipe_forbids_no_gain_but_not_useful_and_is_said():
    assert A.outcome({"1": CONTROL, "2": rms(7.5, 29.0, 9.0)}, {"5": "imaginary"})[0] == "NO OUTCOME"
    word, sentence = A.outcome({"1": CONTROL, "2": rms(7.5, 9.0, 9.0)}, {"5": "imaginary"})
    assert word == "USEFUL" and sentence.endswith("; recipe(s) 5 not read")
    word, sentence = A.outcome({"1": CONTROL, "2": rms(1.0, 1.0, 1.0)}, {"5": "imaginary"})
    assert word == "PASS" and sentence.endswith("; recipe(s) 5 not read")


def test_control_line_at_its_edge():
    assert A.control_holds(rms(8.0, 29.5, 9.5), CONTROL)
    assert not A.control_holds(rms(8.0625, 30.0, 9.0), CONTROL)
    assert not A.control_holds(rms(7.5, 30.0, 8.4375), CONTROL)


def test_verdict_without_a_control_that_repeats_and_with_rows_missing():
    conventional, good = rms(7.5, 30.0, 9.0), rms(1.0, 1.0, 1.0)
    word, sentence = A.verdict({"2": good}, conventional, {"1": "no row file for mp2_ccpvtz"}, {})
    assert word == "PARTIAL" and "no row file for mp2_ccpvtz" in sentence
    assert A.verdict({"2": good}, conventional, {}, {"1": "imaginary"})[0] == "NO OUTCOME"
    with pytest.raises(ValueError, match="nothing to judge"):
        A.outcome({"1": CONTROL}, {})
    assert A.verdict({"1": rms(7.5, 30.75, 9.0), "2": good}, conventional, {}, {})[0] == "CONTROL FAILED"
    assert A.verdict({"1": rms(8.0, 30.5, 9.25), "2": good}, conventional, {}, {})[0] == "PASS"
    assert A.verdict({"1": CONTROL, "2": good}, conventional, {"5": "no row file"}, {})[0] == "PARTIAL"
    assert A.verdict({"1": CONTROL, "2": good}, conventional, {}, {"5": "imaginary"})[0] == "PASS"      # unread for its Hessian: not PARTIAL
    word, sentence = A.verdict({"1": CONTROL}, conventional, {}, {"2": "imaginary"})
    assert word == "NO OUTCOME" and "2: imaginary" in sentence


def test_caveats_name_the_fitting_check_and_the_diagnostic():
    quiet = {m: {"dz": -10.0, "tz": -6.0, "change": 4.0} for m in A.DIAGNOSTIC_MODES}
    under = {"largest_change": 5e-7, "change_of_largest_element": 1e-7, "under_line": True}
    assert A.caveats({"mp2_anopvqz": under}, quiet) == []
    over = {"largest_change": 2e-6, "change_of_largest_element": 1e-7, "under_line": False}
    loud = quiet | {"ω17": {"dz": -10.0, "tz": -4.5, "change": 5.5}}
    said = A.caveats({"mp2_anopvqz": over, "mp2_roosanotz": under}, loud)
    assert len(said) == 2 and "mp2_anopvqz (recipe 5) is over its line" in said[0] and "on ω17:" in said[1]


def test_named_averages_a_degenerate_pair_and_refuses_a_wrong_count():
    freq, keys = [], []
    for sp, ref in A.REF.values():
        twice = abs(A.KEY[sp][2]) == 1
        freq += [ref - 1.0, ref + 3.0] if twice else [ref]
        keys += [A.KEY[sp]] * (2 if twice else 1)
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


def lane_file(label: str) -> tuple[D.RowsPlan, str]:
    """The plan and the method text dfmp2_rows.py writes for a label of the lane; '<label>_fit5z' with cc-pV5Z's fitting sets."""
    basis, theory, scf, mp2, frozen = LANE[label.removesuffix(A.FIT_SUFFIX)]
    if label.endswith(A.FIT_SUFFIX):
        scf, mp2 = "cc-pv5z-jkfit", "cc-pv5z-ri"
    plan = D.plan_from_geometry(GEOMETRY, basis)
    plan = plan if frozen is None else replace(plan, frozen=frozen)
    return plan, D.method_text("1.11", plan, D.Fitting.named_after(basis, scf, mp2), theory)


def write_rows(run: Path, label: str, H: np.ndarray, *, ks: tuple[int, ...] | None = None, method: str | None = None, **plan_fields) -> None:
    """A row file as the lane leaves it, its rows cut from H; '<label>_fit5z' holds the plan's first row only."""
    plan, text = lane_file(label)
    plan = replace(plan, **plan_fields)
    if ks is None:
        ks = plan.ks[:1] if label.endswith(A.FIT_SUFFIX) else plan.ks
    D.save_rows(run / f"rows_{label}.npz", plan, {k: H[k] for k in ks}, method or text)


def write_run(run: Path, mp2: dict[str, np.ndarray], **other: np.ndarray) -> Path:
    """Every row file of the lane: each MP2 target the conventional cc-pVTZ Hessian, the SCF rows equal in both basis sets, no
    core-valence term — so every recipe is the conventional composite — except the labels given in `other`."""
    run.mkdir()
    M = {label: mp2["dz"] if label == A.STEP_FROM else 0.8 * mp2["tz"] if label.startswith("scf") else mp2["tz"] for label in LANE}
    M |= other
    for label, H in M.items():
        write_rows(run, label, H)
    for label in A.FITTING_CHECKED:
        write_rows(run, label + A.FIT_SUFFIX, M[label])
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
    assert all(c["largest_change"] == 0.0 and c["under_line"] for c in record["fitting"].values()) and len(record["fitting"]) == 2
    text = A.report(record)
    assert "**Outcome: NO GAIN**" in text and "| ω4 | b2g | 712.4 | 708.8 |" in text and "(under the line 1e-06" in text
    assert re.search(r"corrected rms per group: [+-]0\.00 / [+-]0\.00 / [+-]0\.00", text) and "compared on unrounded values" in text
    # ω5 and ω17: +7.1 and +8.1 between the two basis sets, from what we hold — said with the outcome (amendment 1)
    assert record["diagnostic_fired"] and "on ω5, ω17: the artefact sits in the coupled-cluster part" in record["sentence"]
    assert "line 5.0 cm⁻¹, crossed." in text and "- Recipe 4 not in the run: ano-pVTZ" in text
    assert "- psi4 that made the rows: 1.11 (every file read)." in text and record["sentence"].count("recipe 4 of the registration") == 1
    quiet = copy.deepcopy(record) | {"diagnostic_fired": False}
    assert "line 5.0 cm⁻¹, not crossed." in A.report(quiet)


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
def test_core_valence_term_enters_with_its_sign_through_the_files(held, tmp_path):
    _, _, mp2 = held
    term = 0.5 * (mp2["tz"] - mp2["dz"])
    lowered = mp2["tz"] - term                                      # every valence target misses the term; all-electron − frozen-core is it
    record = A.read(write_run(tmp_path / "rows", mp2, mp2_ccpvtz=lowered, mp2_ccpvqz=lowered, mp2_ccpwcvtz_ae=mp2["tz"] + term), INPUTS, False)
    assert record["recipes"]["7"]["rms"] == pytest.approx(record["conventional"]["rms"], abs=1e-3)
    assert record["recipes"]["6"]["rms"][CH] != pytest.approx(record["conventional"]["rms"][CH], abs=0.05)


@needs_held
def test_a_step_that_makes_the_full_cc_tz_hessian_reads_as_it_did(held, tmp_path):
    frame, cc, mp2 = held
    record = A.read(write_run(tmp_path / "rows", mp2, mp2_ccpvqz=mp2["dz"] + cc["tz"] - cc["dz"]), INPUTS, False)
    assert record["recipes"]["2"]["rms"] == pytest.approx(rms(3.7, 27.0, 6.1), abs=0.06)      # benzene_geometry_term.txt, 25 Nov
    assert record["recipes"]["2"]["rms"] == pytest.approx(A.group_rms(A.reading(frame, cc["tz"]).corrected), abs=0.05)
    assert record["recipes"]["2"]["overlap"] == pytest.approx(0.586, abs=0.01)                # the same file's smallest overlap²
    assert record["outcome"] == "NO GAIN"


@needs_held
@pytest.mark.parametrize("partial", [False, True])
def test_a_target_with_imaginary_modes_is_left_unread(held, tmp_path, partial):
    _, cc, mp2 = held
    upside_down = mp2["tz"] - 1.5 * (cc["dz"] + mp2["tz"] - mp2["dz"])
    record = A.read(write_run(tmp_path / "rows", mp2, mp2_anopvqz=upside_down), INPUTS, partial)
    assert "imaginary" in record["unread"]["5"] and "5" not in record["recipes"]
    assert record["outcome"] == "NO OUTCOME" and "Recipe 5 not read" in A.report(record)     # not PARTIAL: every row file is there


@needs_held
def test_hessians_the_geometry_term_cannot_be_read_for_are_refused(held):
    frame, cc, _ = held
    with pytest.raises(A.Unreadable, match="Newton step"):
        A.reading(frame, 0.01 * cc["tz"])
    with pytest.raises(A.Unreadable, match="do not pair"):
        A.own_modes(replace(frame, keys=frame.keys[::-1]), cc["tz"])


@needs_held
def test_the_read_refuses_itself_when_it_does_not_repeat_25_november(held, monkeypatch):
    frame, cc, mp2 = held
    monkeypatch.setattr(A, "CONVENTIONAL_PINS", rms(7.6, 30.4, 8.9))
    with pytest.raises(SystemExit, match="the read itself is off"):
        A.conventional_reading(frame, cc, mp2)
    monkeypatch.setattr(A, "MAP_LINE_BOHR", 1e-5)
    with pytest.raises(SystemExit, match="largest atom distance"):
        A.load_frame(INPUTS)


@needs_held
def test_missing_or_unfinished_rows_stop_the_read_unless_partial(held, tmp_path):
    _, _, mp2 = held
    run = write_run(tmp_path / "rows", mp2)
    (run / "rows_mp2_ccpvqz.npz").unlink()
    with pytest.raises(SystemExit, match="no row file for mp2_ccpvqz"):
        A.read(run, INPUTS, partial=False)
    record = A.read(run, INPUTS, partial=True)
    assert record["outcome"] == "PARTIAL" and sorted(record["unread"]) == ["2", "6", "7"] and sorted(record["recipes"]) == ["1", "3", "5"]
    write_rows(run, "mp2_ccpvqz", mp2["tz"], ks=(0, 1))             # the file while its rows are being made
    with pytest.raises(SystemExit, match=r"rows_mp2_ccpvqz.npz holds rows \[0, 1\]"):
        A.read(run, INPUTS, partial=False)
    record = A.read(run, INPUTS, partial=True)
    assert record["outcome"] == "PARTIAL" and "holds rows [0, 1]" in record["unread"]["2"] and sorted(record["recipes"]) == ["1", "3", "5"]
    write_rows(run, "mp2_ccpvdz", mp2["dz"], ks=(0,))
    with pytest.raises(SystemExit, match=r"rows_mp2_ccpvdz.npz holds rows \[0\]"):
        A.read(run, INPUTS, partial=True)


@needs_held
@pytest.mark.parametrize(("label", "change", "said"), [
    ("mp2_ccpvqz", {"basis": "cc-pvtz"}, r"at cc-pvtz, .* expected DF-MP2 \(cc-pvqz-jkfit / cc-pvqz-ri, frozen 6\) at cc-pvqz"),
    ("scf_ccpvqz", {"method": "DF-MP2 psi4 1.11 (cc-pvqz-jkfit / cc-pvqz-ri, frozen 6)"}, r"expected DF-SCF \(cc-pvqz-jkfit\)"),
    ("mp2_anopvqz", {"method": "DF-MP2 psi4 1.11 (def2-universal-jkfit / def2-qzvpp-ri, frozen 6)"}, "holds DF-MP2 psi4 1.11 .def2"),
    ("mp2_ccpwcvtz_ae", {"frozen": 6}, r"expected DF-MP2 \(cc-pvtz-jkfit / cc-pwcvtz-ri, frozen 0\)"),
    ("mp2_ccpwcvtz_fc", {"method": "DF-MP2 psi4 1.11 (cc-pwcvtz-jkfit / cc-pwcvtz-ri, frozen 6)"}, r"expected DF-MP2 \(cc-pvtz-jkfit / cc-pwcvtz"),
    ("mp2_ccpvtz", {"step": 0.02}, "step 0.02"),
    ("mp2_ccpvtz", {"cart": True}, "cartesian True"),
])
def test_a_row_file_of_another_level_is_refused(held, tmp_path, label, change, said):
    _, _, mp2 = held
    run = write_run(tmp_path / "rows", mp2)
    if "frozen" in change:                                           # the frozen count is part of the method text dfmp2_rows.py writes
        plan, _ = lane_file(label)
        change = {"method": D.method_text("1.11", replace(plan, frozen=change["frozen"]), D.Fitting.named_after("cc-pwcvtz", "cc-pvtz-jkfit"),
                                          "mp2")}
    write_rows(run, label, mp2["tz"], **change)
    with pytest.raises(SystemExit, match=said):
        A.read(run, INPUTS, partial=False)


@needs_held
def test_fitting_check_over_its_line_is_said_with_the_outcome(held, tmp_path):
    _, _, mp2 = held
    run = write_run(tmp_path / "rows", mp2)
    write_rows(run, "mp2_anopvqz_fit5z", mp2["tz"] + 1e-5)
    record = A.read(run, INPUTS, partial=False)
    check = record["fitting"]["mp2_anopvqz"]
    assert check["largest_change"] == pytest.approx(1e-5) and check["change_of_largest_element"] == pytest.approx(1e-5)
    assert not check["under_line"] and record["fitting"]["mp2_roosanotz"]["under_line"]
    assert record["outcome"] == "NO GAIN" and "fitting check of mp2_anopvqz (recipe 5) is over its line" in record["sentence"]
    assert "largest change of any element is 1.0e-05 E_h/bohr² (NOT under" in A.report(record)


@needs_held
def test_fitting_check_judges_the_largest_change_of_any_element(held, tmp_path):
    _, _, mp2 = held
    run = write_run(tmp_path / "rows", mp2)
    x0 = lane_file("mp2_anopvqz")[0].coords_bohr
    small = int(np.argmin(np.abs(mp2["tz"][0])))
    moved = mp2["tz"].copy()
    moved[0, small] += 2e-6                                          # the row's smallest element moves, its largest does not
    write_rows(run, "mp2_anopvqz_fit5z", moved)
    check = A.fitting_change(run, "mp2_anopvqz", x0)
    assert check["largest_change"] == pytest.approx(2e-6) and check["change_of_largest_element"] == 0.0 and not check["under_line"]
    zeroed, at_line = mp2["tz"].copy(), mp2["tz"].copy()
    zeroed[0, small], at_line[0, small] = 0.0, A.FITTING_LINE        # a change of exactly the line is not under it
    write_rows(run, "mp2_anopvqz", zeroed)
    write_rows(run, "mp2_anopvqz_fit5z", at_line)
    check = A.fitting_change(run, "mp2_anopvqz", x0)
    assert check["largest_change"] == A.FITTING_LINE and not check["under_line"]
    write_rows(run, "mp2_anopvqz_fit5z", zeroed, coords_bohr=x0 + 0.1)
    with pytest.raises(SystemExit, match="other coordinates"):
        A.fitting_change(run, "mp2_anopvqz", x0)


@needs_held
def test_a_fit_file_of_the_wrong_sets_or_the_wrong_row_is_refused(held, tmp_path):
    _, _, mp2 = held
    run = write_run(tmp_path / "rows", mp2)
    write_rows(run, "mp2_anopvqz_fit5z", mp2["tz"], method=lane_file("mp2_anopvqz")[1])
    with pytest.raises(SystemExit, match=r"expected DF-MP2 \(cc-pv5z-jkfit / cc-pv5z-ri, frozen 6\) at ano-pvqz"):
        A.read(run, INPUTS, partial=False)
    write_rows(run, "mp2_anopvqz_fit5z", mp2["tz"], ks=(1,))
    with pytest.raises(SystemExit, match=r"rows_mp2_anopvqz_fit5z.npz holds rows \[1\], the read needs \[0\]"):
        A.read(run, INPUTS, partial=False)


@needs_held
def test_main_writes_the_report_and_the_record(held, tmp_path, monkeypatch, capsysbinary):
    _, _, mp2 = held
    run = write_run(tmp_path / "rows", mp2)
    monkeypatch.setattr(sys, "argv", ["ano_step_read.py", str(run), str(tmp_path / "read")])
    assert A.main() == 0
    assert json.loads((tmp_path / "read.json").read_text(encoding="utf-8"))["outcome"] == "NO GAIN"
    assert (tmp_path / "read.md").read_text(encoding="utf-8") == capsysbinary.readouterr().out.decode("utf-8")
