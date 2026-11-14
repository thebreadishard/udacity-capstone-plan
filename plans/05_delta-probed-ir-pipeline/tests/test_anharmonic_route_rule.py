"""probes/anharmonic_route_rule.py on synthetic S2b and S3 reads, before either read exists (PreRegistration_2026-11-04_Anharmonic_Route_Rule.md):
the learned route when S3's line holds, the family mean when only it meets the line, no step otherwise, and the families S3 cannot judge."""
from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes"))
R = pytest.importorskip("anharmonic_route_rule")


def s3(n: int, **rms: float) -> dict:
    return {"n": n, "rms": rms}


def v(model: str) -> dict:
    return {"best_curve_model": model}


@pytest.mark.parametrize("verdict,entry,route", [
    (v("x1"), s3(10, c=4.0, x1=2.5), "x1"),                # the learned model carries
    (v("x1"), s3(10, c=4.0, x1=3.0), "x1"),                # exactly on the line
    (v("x1"), s3(10, c=2.8, x1=2.9), "c"),                 # under the line but not below (c): the mean carries
    (v("x1"), s3(10, c=2.9, x1=2.9), "c"),                 # equal to (c) is not below it
    (v("x1"), s3(10, c=2.5, x1=3.4), "c"),                 # the learned model misses, the mean meets the line
    (v("c"), s3(10, c=2.0), "c"),                          # S2b chose the mean itself
    (v("x2*"), s3(10, c=2.0, **{"x2*": math.nan}), "c"),   # the verdict model gave no prediction
    (v("x1"), s3(10, c=3.2, x1=3.1), None),                # neither carries
    (v("x1"), s3(5, c=1.0, x1=0.5), None),                 # too few target modes: not checked at size
    (None, s3(10, c=1.0), None),                           # no S2b verdict
])
def test_the_route_per_family(verdict, entry, route):
    got = R.route_for_family(verdict, entry)
    assert got["route"] == route
    if route is None:
        assert got["error_bar_cm"] is None
    else:
        assert got["error_bar_cm"] == entry["rms"][route]


def test_a_family_without_target_modes_gets_no_step():
    s2b = {"scopes": {R.MAIN_SCOPE: {"read": {"verdicts": {"CH-stretch": v("c"), "ring-ip": v("x1")}}}}}
    got = R.route_rule(s2b, {"read": {"families": {"ring-ip": s3(12, c=4.0, x1=2.0)}}})
    assert got["CH-stretch"]["route"] is None and "0 target mode" in got["CH-stretch"]["reason"]
    assert got["ring-ip"]["route"] == "x1"


def test_the_reading_names_the_targets_and_the_licence():
    res = {"ring-ip": {"route": "x1", "error_bar_cm": 2.0, "reason": "carries"},
           "CH-oop": {"route": None, "error_bar_cm": None, "reason": "neither carries"}}
    s3_read = {"registration": "PreRegistration_2026-11-02_S3_Route_A_Transfer.md", "marked_policy": "exclude",
               "targets": ["tetracene", "coronene"],
               "read": {"families": {
                   "ring-ip": {"n": 12, "verdict_model": "x1",
                               "per_molecule": {"tetracene": {"x1": 1.5}, "coronene": {"x1": 2.4}}},
                   "CH-oop": {"n": 8, "verdict_model": "x2*",
                              "per_molecule": {"tetracene": {"x2*": 4.5}, "coronene": {"x2*": 11.9}}}},
                        "rows": {"tetracene": {"family": ["ring-ip", "CH-oop"], "truth": [-6.0, -3.0]},
                                 "coronene": {"family": ["ring-ip"], "truth": [-8.0]}}}}
    text = "\n".join(R.report(res, {}, s3_read))
    assert "| tetracene | coronene | harmonic position |" in text
    assert "| ring-ip | 12 | x1 | 2.00 | x1 | 1.50 | 2.40 | 7.07 | carries |" in text
    assert "| CH-oop | 8 | no step | — | x2* | 4.50 | 11.90 | 3.00 | neither carries |" in text
    assert "Licensed, an anharmonic step in the pipeline: ring-ip" in text


def test_the_reading_says_so_when_no_family_is_licensed():
    res = {"other": {"route": None, "error_bar_cm": None, "reason": "neither carries"}}
    s3_read = {"registration": "r.md", "targets": ["tetracene"], "read": {"families": {}, "rows": {}}}
    text = "\n".join(R.report(res, {}, s3_read))
    assert "no family. Every band keeps its harmonic position" in text
    assert "| other | 0 | no step | — | — | — | — | neither carries |" in text


def test_the_harmonic_column_is_the_rms_of_the_true_shift():
    s3_read = {"read": {"rows": {
        "tetracene": {"family": ["ring-ip", "ring-ip"], "truth": [-3.0, -4.0]},
        "coronene": {"family": ["ring-ip", "CH-oop"], "truth": [-5.0, -12.0]}}}}
    got = R.no_shift_rms(s3_read)
    assert got["ring-ip"] == pytest.approx(math.sqrt((9.0 + 16.0 + 25.0) / 3))
    assert got["CH-oop"] == pytest.approx(12.0)


# ------------------------------------------------------------------ what is printed (TASKS 211, registered 14 Nov 2026)

VERDICT_X2 = {"best_curve_model": "x2*"}


def test_a_step_that_beats_the_harmonic_position_is_printed_with_its_measured_bar():
    entry = {"n": 20, "rms": {"x2*": 6.21, "c": 6.50}}
    got = R.printed_for_family(VERDICT_X2, entry, 134.24)
    assert got["model"] == "x2*" and got["bar_cm"] == 6.21
    assert got["beats_harmonic_by_cm"] == pytest.approx(128.03)
    assert "21.6 times better" in got["reason"] and "no licence" in got["reason"]


def test_a_step_that_does_not_beat_the_harmonic_position_is_not_printed():
    entry = {"n": 20, "rms": {"x2*": 9.0, "c": 8.0}}
    got = R.printed_for_family(VERDICT_X2, entry, 8.5)
    assert got["model"] is None and got["bar_cm"] is None
    assert "does not beat the harmonic position" in got["reason"]


def test_a_family_the_targets_cannot_judge_at_size_gets_no_step():
    got = R.printed_for_family(VERDICT_X2, {"n": R.MIN_MODES - 1, "rms": {"x2*": 0.1}}, 100.0)
    assert got["model"] is None and "not checked at size" in got["reason"]
    assert R.printed_for_family(VERDICT_X2, None, 100.0)["model"] is None


def test_a_family_without_a_verdict_model_gets_no_step():
    got = R.printed_for_family(None, {"n": 20, "rms": {"c": 1.0}}, 100.0)
    assert got["model"] is None and "no S2b verdict" in got["reason"]


def test_the_printed_table_names_the_model_the_bar_and_what_it_beats():
    printed = {"ring-ip": {"model": "x2*", "bar_cm": 3.37, "harmonic_cm": 26.23, "reason": "r"},
               "CH-oop": {"model": None, "bar_cm": None, "reason": "no"}}
    text = "\n".join(R.printed_lines(printed))
    assert "| ring-ip | x2* | 3.37 | 26.23 | r |" in text
    assert "| CH-oop | harmonic position | — | — | no |" in text
    assert "claims no licence" in text


def test_a_verdict_model_with_no_prediction_says_that_and_not_that_it_lost():
    """The reason may not assert a comparison that was never made (14 Nov 2026, the independent review)."""
    got = R.printed_for_family(VERDICT_X2, {"n": 20, "rms": {"c": 6.5}}, 134.24)
    assert got["model"] is None and got["bar_cm"] is None
    assert "gave no prediction on the targets" in got["reason"]
    assert "does not beat" not in got["reason"] and "nan" not in got["reason"]


def test_a_window_a_read_predates_is_read_as_the_only_one_there_was():
    window, name = R.window_of({"scopes": {}})
    assert window == [550.0, 2000.0] and name.startswith("mid (not recorded")


def test_an_open_bound_from_an_older_record_is_written_as_null():
    """A record written before window_record carries Infinity; copying it through would put it in the new record."""
    window, name = R.window_of({"window": [2800.0, float("inf")], "window_name": "ch"})
    assert window == [2800.0, None] and name == "ch"
