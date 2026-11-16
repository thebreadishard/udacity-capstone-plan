"""What the live certificate and the pages print of a band's position (`m08/live_certificate.py`, `m08/demo_page.py`,
`m08/positions.py`; TASKS 211): ν beside ω with the licence kept on ω, the three kinds of band line, a result without the step,
and the demo page's and the show's sentences. On the frozen corpus's benzene, with the stand-in force field of
tests/test_m08_anharmonic.py."""
from __future__ import annotations

import sys

from pin_tools import PLAN
from test_m08_anharmonic import APPLIED, artefact, stepped  # noqa: F401  artefact is a fixture
from test_m08_live_certificate import ZERO, accuracy, record, result  # noqa: F401  accuracy and result are fixtures

sys.path.insert(0, str(PLAN / "modules" / "08_industry_synthesis"))
from m08 import demo_page as D
from m08 import live_certificate as LC
from m08 import positions as POS

# isort: split
import anharmonic_step as AS  # probes/, on the path through m08.pipeline


def test_the_certificate_prints_nu_beside_omega_and_keeps_the_licence_on_omega(result, accuracy, artefact, monkeypatch):  # noqa: F811
    out = stepped(result, artefact, monkeypatch)
    rows = LC.bands(LC.load_result(result), accuracy, {}, ["ring-ip", "CH-stretch"])
    sticks = out["network"]["sticks"]
    assert [b["network_cm"] for b in rows] == [s["omega_cm"] for s in sticks] and [b["nu_cm"] for b in rows] == [s["nu_cm"] for s in sticks]
    assert all(b["printed_cm"] == (b["nu_cm"] if b["nu_cm"] is not None else b["network_cm"]) for b in rows)
    assert all((b["printed"] == POS.ANHARMONIC) == (b["nu_cm"] is not None) for b in rows)
    assert all(b["licensed"] == (b["family"] in ("ring-ip", "CH-stretch")) for b in rows)          # the licence did not move with ν
    stretches = [b for b in rows if b["family"] == "CH-stretch"]
    assert all(b["network_cm"] > 3150 and b["lab_region"] == LC.lab_region(b["nu_cm"]) for b in stretches)   # the region of the printed position
    cert = {"bands": rows, "licence": {"quantity_name": "error", "caveats": []},
            "positions": {"note": out["note"], "anharmonic": out["anharmonic"]}}
    lines = LC._band_lines(cert)
    assert lines[0].startswith("| best estimate (cm⁻¹) | printed | harmonic ω, network | Δ_anh | ± of ν (measured, not licensed) |")
    assert "| ω licensed | error of ω on (a) / (b), cm⁻¹ |" in lines[0]
    first = next(b for b in rows if b["nu_cm"] is not None and b["anharmonic_bar_cm"] is not None)
    assert f"| {first['nu_cm']} | anharmonic ν | {first['network_cm']} | {first['delta_anh_cm']:+} | {first['anharmonic_bar_cm']} |" in "\n".join(lines)
    text = "\n".join(lines)
    assert f"Which position each band is printed at ({POS.LICENCE_SCOPE}):" in text
    assert f"- harmonic position, no anharmonic step: {AS.REASON_TEXT[AS.UNMEASURED]} — " in text
    flagged = [b for b in rows if b["anharmonic_error_measured"] is False]
    assert flagged and f"printed without an error bar: {AS.NOT_MEASURED_TEXT}; no licence is claimed for ν — {len(flagged)} band(s): " in text
    assert all(f"| {b['nu_cm']} | anharmonic ν | {b['network_cm']} | {b['delta_anh_cm']:+} | not measured |" in text for b in flagged)
    assert sum(line.startswith("- ") for line in lines) == len({b["position_note"] for b in rows})


def test_a_result_without_the_step_is_one_sentence_not_a_line_per_band(result, accuracy):  # noqa: F811
    record(result, ZERO, [ZERO])                                   # a record as a pipeline before 0.11 wrote it: no anharmonic block
    rows = LC.bands(LC.load_result(result), accuracy, {}, [])
    assert all(b["printed"] == POS.HARMONIC and b["printed_cm"] == b["network_cm"] and b["no_step_reason"] == POS.NOT_APPLIED for b in rows)
    summary = POS.summary_of({})
    lines = LC._band_lines({"bands": rows, "licence": {"quantity_name": "error", "caveats": []}, "positions": {"anharmonic": summary}})
    assert lines[-1].startswith("| ") and all("| harmonic ω |" in line and "| — | — |" in line for line in lines[2:])


def test_the_statement_licenses_omega_by_name():
    lic = {"quantity_name": "error", "licensed_families": ["ring-ip"], "caveats": []}
    s = LC.statement("x", "1.3", 3, lic, "never seen")
    assert "the harmonic positions ω are licensed for ring-ip (decision 65)" in s and "harmonic infrared spectrum" not in s


def test_the_demo_page_and_the_show_say_which_position_they_print():
    old = {"licence": {"licensed_families": []}}
    assert D.limits(old)[0] == f"Positions are harmonic (ω): the anharmonic step was not applied — {POS.BEFORE_THE_STEP}."
    new = old | {"positions": {"note": POS.note(APPLIED)}}
    assert D.limits(new)[0].startswith("Each band is printed at its best estimate — the anharmonic position ν") and POS.LICENCE_SCOPE in D.limits(new)[0]
    assert D._step_time({"anharmonic": 30.0}, "anharmonic") == "30 s" and D._step_time({}, "anharmonic") == "—" and D._step_time({}, None) == ""
    assert any(key == "anharmonic" and "no licence is claimed" in what for _, what, key in D.STEPS)
    assert "harmonic positions ω" in POS.DRAWN and "harmonic (ω)" in POS.CATALOGUE and "says which" in POS.PIPELINE
