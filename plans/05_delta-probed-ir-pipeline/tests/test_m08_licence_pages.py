"""The pages that show the licence, on a certificate written after the amendment of 16 Nov 2026 (decision 65: the licence is read on
the product's error, and under v1.3 'other' is licensed on an interval that crosses the line on hold-out (a)). Wherever a page shows
the licence — the demo page's family table and licence section, the show page's certificate card, the live certificate's band table
and opening statement — the caveat is printed with it, and no page carries a fixed sentence about which family is licensed. The
certificate is a stored one (module 06's candidate, 30 Oct 2026) with its accuracy, licence and bands' errors rebuilt from today's
records by the certificate's own functions; a stored one as it is shows what a pre-amendment record prints."""
from __future__ import annotations

import copy
import json
import shutil
import sys

import numpy as np
import pytest

from pin_tools import PLAN
from test_m08_own_spread import OWN_SPREAD, UNMOVED

sys.path.insert(0, str(PLAN / "modules" / "08_industry_synthesis"))
from m08 import accuracy as A
from m08 import demo_page as D
from m08 import licence
from m08 import live_certificate as LC
from m08 import show as S

V13 = tuple(f"E7_rungC_chain35_analytic_model_n750_seed{s}.pt" for s in range(3))
STORED = S.RESULTS / "pipeline_demo_v04_2026-10-30" / "candidate06"
CAVEAT = ("Licence caveat: other on hold-out (a) rests on 8 molecules: the 95 % interval of a bootstrap over molecules is 1.68–3.76 cm⁻¹ "
          "and crosses the line (70 % of the resamples lie under it).")
PRODUCT_NAME = "error of the corrected band positions of the seed-mean correction"


@pytest.fixture(scope="module")
def stored() -> dict:
    return json.loads((STORED / "certificate.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def amended(stored) -> dict:
    """The stored certificate as `live_certificate.certificate` writes it today: the accuracy with the product's error, the licence
    block, and every band's licence and error in the licence's quantity."""
    acc = A.accuracy_of(V13)
    lic = licence.state(acc)
    _, errors = A.stated_errors(acc)
    cert = copy.deepcopy(stored)
    cert["accuracy"], cert["licence"], cert["own_spread"] = acc, LC.licence_block(lic, UNMOVED), dict(UNMOVED.measured.record)
    for band in cert["bands"]:
        band["licensed"], band["error_cm"] = band["family"] in lic["licensed_families"], dict(errors[band["family"]])
        band["own_spread_cm"], band["own_spread_change"] = 0.0, "rotation 1"       # as networks that move no band would leave it
    cert["statement"] = LC.statement(cert["molecule"]["name"], "1.3", 3, cert["licence"], cert["molecule"]["seen"]["text"])
    # the stored result predates the anharmonic step (pipeline 0.11, TASKS 211): its bands are harmonic and say so
    summary = LC.POS.summary_of({})
    cert["positions"] = dict(note=LC.POS.note(summary), anharmonic=summary, drawn=LC.POS.DRAWN)
    for band in cert["bands"]:
        band.update(LC.POS.band({"omega_cm": band["network_cm"]}, summary, {}, ""))
    return cert


def panel(cert: dict) -> D.Panel:
    return D.Panel(demo=None, record={}, certificate=cert, vs_corpus=None, grid=np.zeros(1), curves={})


def test_the_licence_block_of_v13_carries_its_caveat(amended):
    assert amended["licence"]["licensed_families"] == ["ring-ip", "CH-stretch", "CH-oop", "other"]
    assert licence.caveat_sentence(amended["licence"]) == CAVEAT and amended["licence"]["quantity"] == A.PRODUCT


def test_a_certificate_stored_before_the_amendment_has_no_caveat_to_print(stored):
    assert "caveats" not in stored["licence"] and licence.caveat_sentence(stored["licence"]) == ""
    assert licence.caveat_sentence({"caveats": []}) == ""


def test_the_demo_page_says_what_the_certificate_says_about_other(stored, amended):
    """30 Oct's page said 'other' is not licensed in a fixed sentence; with today's certificate the same page chips it licensed."""
    now, then = D.limits(amended), D.limits(stored)
    assert not any("not licensed" in x for x in now) and "count as 'other', which is licensed (the table above)." in now[2]
    assert "count as 'other', which is not licensed (the table above)." in then[2] and [*now[:2], *now[3:]] == [*then[:2], *then[3:]]


def test_the_demo_pages_tables_print_the_caveat_and_name_the_quantity(stored, amended):
    for html in (D.licence_section(amended), D._family_table(panel(amended))):
        assert CAVEAT in html and "not licensed" not in html
    assert f"{PRODUCT_NAME.capitalize()}, rms in cm⁻¹" in D.licence_section(amended) and f"{PRODUCT_NAME}, (a) / (b)" in D._family_table(panel(amended))
    for html in (D.licence_section(stored), D._family_table(panel(stored))):
        assert "Licence caveat" not in html and "irst-order diagonal error of each seed&#x27;s correction" in html


def test_the_show_page_prints_the_caveat_with_the_certificate_card(tmp_path, amended):
    folder = tmp_path / "run" / "candidate06"
    shutil.copytree(STORED, folder)
    (folder / "certificate.json").write_text(json.dumps(amended, ensure_ascii=False), encoding="utf-8")
    m = S.molecule(folder)
    assert m["licence_caveat"] == CAVEAT and m["error_quantity"] == PRODUCT_NAME
    assert all(row["licensed"] for row in m["families"]) and {r["family"]: (r["error_a"], r["error_b"]) for r in m["families"]}["other"] == (2.78, 2.77)
    page = S.page(S.payload((folder,)))
    assert "Licence caveat: other on hold-out (a) rests on 8 molecules: the 95 % interval of a bootstrap over molecules is 1.68" in page
    assert "${m.licence_caveat ? `<div" in page and "${esc(m.errors_text)}" in page
    assert m["errors_text"] == f"errors: the {PRODUCT_NAME}, on molecules the network never saw (cm⁻¹)"
    assert S.molecule(STORED)["licence_caveat"] == ""


def test_the_live_certificates_band_table_ends_with_the_caveat_and_the_statement_does_not_repeat_it(amended):
    """Since the demo review the caveat is printed once on the page, under the band table; the licence line keeps its own clause."""
    lines = LC._band_lines(amended)
    assert lines[-1] == f"*{CAVEAT}*" and lines[-2] == "" and lines[-3].startswith("| ")
    assert amended["statement"].endswith(f"This molecule and the ΔH network: {amended['molecule']['seen']['text']}.")
    assert CAVEAT not in amended["statement"]
    quiet = {**amended, "licence": {**amended["licence"], "caveats": []}}
    assert LC._band_lines(quiet)[-1].startswith("| ")
    lic = {"quantity_name": PRODUCT_NAME, "licensed_families": ["ring-ip"], "caveats": []} | OWN_SPREAD
    assert LC.statement("x", "1.3", 3, lic, "never seen").endswith("This molecule and the ΔH network: never seen.")
    page = LC.to_markdown(amended)
    assert page.count(CAVEAT) == 1 and page.count(amended["licence"]["caveats"][0]) == 2   # the band table; and the licence line
