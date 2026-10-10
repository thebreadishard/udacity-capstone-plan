"""TASKS 44 (10 Oct 2026): the built molecule pages carry the intensity chart where the export has heights and say 'positions only' where it has
none; one card leads the page. Runs against website/site/dist after `npm run build`; skipped when there is no build."""
import os

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.abspath(os.path.join(HERE, "..", "..", "site", "dist", "molecule"))
pytestmark = pytest.mark.skipif(not os.path.isdir(DIST), reason="no site build (run npm run build in website/site)")


def page(mid: str) -> str:
    with open(os.path.join(DIST, mid, "index.html"), encoding="utf-8") as f:
        return f.read()


def test_benzene_has_heights_and_the_accuracy_block():
    h = page("A_8448043181")
    assert "Infrared spectrum at the cheap level" in h and "4 infrared-active bands" in h
    assert "How well is this shape known?" in h and "not licensed yet" in h
    assert h.count('class="irspec"') == 1 and h.count("<svg class=\"wide\"") >= 2       # IR chart and positions chart, each with its renders
    assert h.index("Infrared spectrum at the cheap level") < h.index(">Structure<")       # the spectrum card leads


def test_naphthalene_says_positions_only():
    h = page("A_01f3186607")
    assert "Band heights are not computed for this molecule yet" in h and 'class="irspec"' not in h
    assert h.index("Harmonic frequencies at the cheap level") < h.index(">Structure<")
