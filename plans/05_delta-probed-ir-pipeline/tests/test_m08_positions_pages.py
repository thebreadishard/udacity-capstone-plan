"""What the live certificate and the pages print of a band's position (`m08/live_certificate.py`, `m08/demo_page.py`,
`m08/positions.py`; TASKS 211): ν beside ω with the licence kept on ω, the bar headed as the step's, the certificate-level
sentences said once, the three kinds of band line, the first delivery and a result without the step, and the demo page's and the
show's sentences. On the frozen corpus's benzene, with the stand-in force field of tests/test_m08_anharmonic.py."""
from __future__ import annotations

import inspect
import json
import sys
from pathlib import Path

import pytest

from pin_tools import PLAN
from test_m08_anharmonic import APPLIED, artefact, request, spectra_of, stepped  # noqa: F401  artefact is a fixture
from test_m08_live_certificate import ZERO, accuracy, record, result  # noqa: F401  accuracy and result are fixtures

sys.path.insert(0, str(PLAN / "modules" / "08_industry_synthesis"))
from m08 import anharmonic as AN
from m08 import demo_page as D
from m08 import live_certificate as LC
from m08 import pipeline as P
from m08 import positions as POS
from m08 import show as S
from m08 import show_live as L
from m08.progress import STEPS, Progress

# isort: split
import anharmonic_step as AS  # probes/, on the path through m08.pipeline

LICENCE = {"quantity_name": "error", "caveats": []}


def certificate_of(rows: list[dict], summary: dict, note: str = "a note") -> dict:
    """What `_band_lines` and `to_markdown`'s position paragraphs read of a certificate."""
    return {"bands": rows, "licence": LICENCE, "positions": {"note": note, "cautions": POS.cautions(summary), "anharmonic": summary}}


def test_the_certificate_prints_nu_beside_omega_and_keeps_the_licence_on_omega(result, accuracy, artefact, monkeypatch):  # noqa: F811
    out = stepped(result, artefact, monkeypatch)
    rows = LC.bands(LC.load_result(result), accuracy, {}, ["ring-ip", "CH-stretch"])
    sticks = out["network"]["sticks"]
    assert [b["network_cm"] for b in rows] == [s["omega_cm"] for s in sticks] and [b["nu_cm"] for b in rows] == [s["nu_cm"] for s in sticks]
    assert all(b["printed_cm"] == (b["nu_cm"] if b["nu_cm"] is not None else b["network_cm"]) for b in rows)
    assert all((b["printed"] == POS.ANHARMONIC) == (b["nu_cm"] is not None) for b in rows)
    assert all(b["licensed"] == (b["family"] in ("ring-ip", "CH-stretch")) for b in rows)          # the licence did not move with ν
    assert all(b["step_family"] == b["family"] for b in rows if b["nu_cm"] is not None)            # one family per band, by both rules
    stretches = [b for b in rows if b["family"] == "CH-stretch"]
    assert all(b["network_cm"] > 3150 and b["lab_region"] == LC.lab_region(b["nu_cm"]) for b in stretches)   # the region of the printed position
    lines = LC._band_lines(certificate_of(rows, out["anharmonic"]))
    text = "\n".join(lines)
    assert lines[0].startswith(f"| best estimate (cm⁻¹) | printed | harmonic ω, network | Δ_anh | {POS.BAR_HEADER} |")
    assert "± of Δ_anh, against its VPT2 label" in lines[0] and "± of ν" not in text               # the bar is the step's, not ν's
    assert "| ω licensed | error of ω on (a) / (b), cm⁻¹ |" in lines[0]
    first = next(b for b in rows if b["nu_cm"] is not None and b["step_bar_cm"] is not None)
    assert f"| {first['nu_cm']} | anharmonic ν | {first['network_cm']} | {first['delta_anh_cm']:+} | {first['step_bar_cm']} |" in text
    assert f"Which position each band is printed at ({POS.LICENCE_SCOPE}):" in text
    assert f"- harmonic position, no anharmonic step: {AS.REASON_TEXT[AS.UNMEASURED]} — " in text
    assert "- anharmonic estimate ν = ω + Δ_anh; the step's error is ± 3.37 cm⁻¹ (rms of Δ_anh against its VPT2 label, family ring-ip); " in text
    flagged = [b for b in rows if b["step_error_measured"] is False]
    assert flagged and f"printed without an error bar: {AS.NOT_MEASURED_TEXT}; no licence is claimed for ν — {len(flagged)} band(s): " in text
    assert all(f"| {b['nu_cm']} | anharmonic ν | {b['network_cm']} | {b['delta_anh_cm']:+} | not measured |" in text for b in flagged)
    assert sum(line.startswith("- ") for line in lines) == len({b["position_note"] for b in rows})


def test_the_certificate_says_once_what_nus_error_is_and_what_the_bars_rest_on(result, artefact, monkeypatch):  # noqa: F811
    """Review findings 1 and 5: under the statement, each once — the bar is the step's and ν carries ω's error too, neither against
    experiment; the two hydrocarbon targets with the registered row counts; and x2*'s own word on having seen the molecule."""
    out = stepped(result, artefact, monkeypatch)
    said = POS.cautions(out["anharmonic"])
    paragraphs = LC._position_paragraphs(certificate_of([], out["anharmonic"], out["note"]))
    text = "\n".join(paragraphs)
    assert paragraphs[0].startswith("**Positions.** Each band is printed at its best estimate")
    assert "**What the bar is, and what ν's error is.** The bar beside a step is the step's error alone" in text
    assert "the rms of Δ_anh against its B3LYP VPT2 label — and not the error of ν" in text
    assert "ν carries ω's error too" in text and "neither of the two is an error against experiment." in text
    assert "**What the bars rest on.** The bars rest on 2 target molecules, coronene and tetracene, both hydrocarbons" in text
    assert "target modes: CH-oop 22, other 23, ring-ip 56, CH-stretch 20" in text
    assert "ring-ip 4.25 / 2.35" in text and "coronene carries the larger error in every family" in text and "they are thin" in text
    assert text.count("What the bar is") == 1 and text.count("What the bars rest on") == 1
    assert "This molecule's elements" not in text                       # a hydrocarbon: the table holds 14 of them
    assert said["seen"] == ("the anharmonic model x2* has this molecule in its training table (A_8448043181, one of 37): for this "
                            "molecule the step's bar is not an out-of-sample error")
    few = out["anharmonic"] | {"composition": out["anharmonic"]["composition"] | {"elements": "C,H,O", "training_molecules": 3, "few": True}}
    assert "**This molecule's elements in the anharmonic model's table.** The training table of x2* holds 3 of 37" in "\n".join(
        LC._position_paragraphs(certificate_of([], few)))


def test_each_model_states_for_itself_whether_it_has_seen_the_molecule():
    """The statement's 'held out… never trained on' is the ΔH network's; the anharmonic model's line stands beside it."""
    lic = {"quantity_name": "error", "licensed_families": ["ring-ip"], "caveats": []}
    s = LC.statement("x", "1.3", 3, lic, "held out: never trained on")
    assert s.endswith("This molecule and the ΔH network: held out: never trained on.")
    assert "the harmonic positions ω are licensed for ring-ip (decision 65)" in s and "harmonic infrared spectrum" not in s


def test_the_first_delivery_is_a_complete_harmonic_certificate_that_says_what_will_come(result, accuracy, artefact):  # noqa: F811
    """Review finding 2: the record as the pipeline writes it before step 6 starts — every band harmonic, the certificate's
    positions paragraph saying that the step runs, under which budget, and what the second delivery adds."""
    record(result, ZERO, [ZERO])
    rec = json.loads((result / "pipeline.json").read_text(encoding="utf-8"))
    out = AN.first_delivery(request(result, artefact), spectra_of(result))
    P.write_json(result / "pipeline.json", rec | {"spectra": out})
    rows = LC.bands(LC.load_result(result), accuracy, {}, [])
    assert len(rows) == 30 and all(b["printed"] == POS.HARMONIC and b["no_step_reason"] == POS.RUNNING and b["nu_cm"] is None for b in rows)
    cert = certificate_of(rows, out["anharmonic"], out["note"])
    assert cert["positions"]["cautions"] == {} and LC._band_lines(cert)[-1].startswith("| ")
    first = LC._position_paragraphs(cert)[0]
    assert "in this first delivery: the anharmonic step is running, with a time budget of 120 minutes" in first
    assert "this certificate is written again and adds per band the anharmonic estimate ν = ω + Δ_anh beside ω" in first
    lines = LC._delivery_lines({"deliveries": [{"number": 1, "delivery": P.FIRST_DELIVERY, "at": "2026-11-16 20:00:00",
                                               "seconds_since_start": 324.0, "final_by": "2026-11-16 22:02"},
                                              {"number": 2, "delivery": P.SECOND_DELIVERY, "at": "2026-11-16 20:40:00",
                                               "seconds_since_start": 2724.0, "final_by": None}]})
    assert lines == [f"- delivery 1 — {P.FIRST_DELIVERY}: 2026-11-16 20:00:00, 324.0 s after the start; final by 2026-11-16 22:02, and if "
                     "no later delivery stands here by then, this one is final",
                     f"- delivery 2 — {P.SECOND_DELIVERY}: 2026-11-16 20:40:00, 2724.0 s after the start"]
    assert LC._delivery_lines({}) == []


def test_the_certificates_two_files_are_a_pair_and_a_cut_pair_is_refused(tmp_path, monkeypatch):
    """Round two, finding 5: both files are written whole before either replaces the old one, each names its delivery, and a
    folder whose record and page are of different deliveries is refused by the reader the pages use."""
    monkeypatch.setattr(LC, "to_markdown", lambda c: f"# page\n\n{LC.DELIVERY_MARK.format(c['delivery'])}\n")
    LC.write({"delivery": 1, "x": "first"}, tmp_path)
    assert LC.read_certificate(tmp_path)["x"] == "first" and not list(tmp_path.glob("*.tmp"))
    moved = []
    real = LC.os.replace

    def cut_after_the_record(src: Path, dst: Path) -> None:
        if moved:
            raise OSError("killed between the two files")
        moved.append(Path(dst).name)
        real(src, dst)

    monkeypatch.setattr(LC.os, "replace", cut_after_the_record)
    with pytest.raises(OSError, match="killed between"):
        LC.write({"delivery": 2, "x": "second"}, tmp_path)
    assert moved == ["certificate.json"]                                      # the fixed order: the record, then the page
    assert json.loads((tmp_path / "certificate.json").read_text(encoding="utf-8"))["x"] == "second"
    with pytest.raises(LC.MismatchedPair, match="is delivery 2 and"):
        LC.read_certificate(tmp_path)
    monkeypatch.setattr(LC, "load_result", lambda folder: None)              # the show reads the pair through the same reader
    with pytest.raises(LC.MismatchedPair):
        S.molecule(tmp_path)
    assert "LC.read_certificate(demo.folder)" in inspect.getsource(D.load_panel)       # and so does the demo page
    monkeypatch.setattr(LC.os, "replace", real)
    LC.write({"delivery": 2, "x": "second"}, tmp_path)
    assert LC.read_certificate(tmp_path)["x"] == "second"
    (tmp_path / "certificate.json").write_text(json.dumps({"x": "old"}), encoding="utf-8")       # a record from before the numbering
    assert LC.read_certificate(tmp_path) == {"x": "old"}


def test_the_live_show_has_the_result_at_the_first_delivery_and_asks_again_at_the_second(tmp_path):
    """Round two, finding 1: the progress record the show polls is finished at delivery 1 and carries the delivery's number and
    state; the page fetches the result whenever that number is one it has not shown."""
    p = Progress(tmp_path, "benzene", "0.11", {"smiles": "c1ccccc1", "formula": "C6H6", "n_atoms": 12})
    for step in STEPS:
        p.start(step)
        p.done(step)
    assert L.progress_view(tmp_path)["finished"] is False and L.progress_view(tmp_path)["delivery"] is None
    p.delivered(1, "harmonic delivered, anharmonic step running, final by 2026-11-16 22:02", final=False)
    view = L.progress_view(tmp_path)
    assert view["finished"] is True and view["delivery"] == {"number": 1, "final": False,
                                                             "state": "harmonic delivered, anharmonic step running, final by 2026-11-16 22:02"}
    p.delivered(2, "final: with the anharmonic positions", final=True)
    assert L.progress_view(tmp_path)["delivery"] == {"number": 2, "state": "final: with the anharmonic positions", "final": True}
    template = (PLAN / "modules" / "08_industry_synthesis" / "m08" / "show_template.html").read_text(encoding="utf-8")
    assert "const delivery = p.delivery ? p.delivery.number : (p.finished ? 1 : 0);" in template
    assert "if (p.finished && live.shown !== delivery && !live.asking) {" in template and "live.shown = delivery;" in template
    assert "p.delivery ? p.delivery.state" in template


def test_a_result_without_the_step_is_one_sentence_not_a_line_per_band(result, accuracy):  # noqa: F811
    record(result, ZERO, [ZERO])                                   # a record as a pipeline before 0.11 wrote it: no anharmonic block
    rows = LC.bands(LC.load_result(result), accuracy, {}, [])
    assert all(b["printed"] == POS.HARMONIC and b["printed_cm"] == b["network_cm"] and b["no_step_reason"] == POS.NOT_APPLIED for b in rows)
    lines = LC._band_lines(certificate_of(rows, POS.summary_of({})))
    assert lines[-1].startswith("| ") and all("| harmonic ω |" in line and "| — | — |" in line for line in lines[2:])


def test_the_demo_page_and_the_show_say_which_position_they_print():
    old = {"licence": {"licensed_families": []}}
    assert D.limits(old)[0] == f"Positions are harmonic (ω): the anharmonic step was not applied — {POS.BEFORE_THE_STEP}."
    new = old | {"positions": {"note": POS.note(APPLIED)}}
    assert D.limits(new)[0].startswith("Each band is printed at its best estimate — the anharmonic position ν") and POS.LICENCE_SCOPE in D.limits(new)[0]
    assert D._step_time({"anharmonic": 30.0}, "anharmonic") == "30 s" and D._step_time({}, "anharmonic") == "—" and D._step_time({}, None) == ""
    assert any(key == "anharmonic" and "no licence is claimed" in what for _, what, key in D.STEPS)
    assert "harmonic positions ω" in POS.DRAWN and "harmonic (ω)" in POS.CATALOGUE and "says which" in POS.PIPELINE
