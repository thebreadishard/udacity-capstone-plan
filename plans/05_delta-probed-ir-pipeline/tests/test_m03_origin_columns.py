"""Module 03, band-origin column (item 105 added 29 Sep 2026): the printed-value parser reads value, 1 σ fit uncertainty and reading precision;
every item-105 value occurs verbatim in the text extract of the paper; the abstract-grade items keep their lower-bound form."""
import sys
from pathlib import Path

import pytest

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "modules" / "03_lab_scoreboard"))
import origin_columns_naphthalene as O  # noqa: E402


def test_parse_printed_with_and_without_uncertainty():
    assert O.parse_printed("1603.28695(5)") == (1603.28695, 5e-05, 5e-06)
    assert O.parse_printed("473.73950(1)") == (473.7395, 1e-05, 5e-06)
    v, fit, reading = O.parse_printed("782.330949")
    assert (v, fit) == (782.330949, None) and abs(reading - 5e-07) < 1e-15
    assert O.parse_printed("782") == (782.0, None, 0.5)


def test_item_105_bands_and_grades():
    s = O.SOURCES["105"]
    modes = [m for m, _, _ in s["bands"]]
    assert modes == ["nu48", "nu24", "nu47", "nu46", "nu35", "nu19"] and "text" in s
    assert all("(" in p for _, _, p in s["bands"])                       # PDF grade: every value carries its fit uncertainty
    assert all("text" not in O.SOURCES[k] for k in ("72", "73"))          # abstract grade unchanged


@pytest.mark.skipif(not O.TXT105.exists(), reason="the Chawananon 2022 text extract is not on this machine")
def test_item_105_values_are_verbatim_in_the_text_extract():
    text = O.TXT105.read_text(encoding="utf-8", errors="replace")
    for _, _, printed in O.SOURCES["105"]["bands"]:
        assert printed in text, printed
