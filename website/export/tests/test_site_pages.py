"""TASKS 44–45 (10 Oct 2026): every built molecule page leads with the best spectrum it has — the anchor's (with heights from the anchor's own CC
dipole derivatives on benzene, the B3LYP ones said on benzonitrile, positions only on naphthalene), else the cheap level's with heights, else the
cheap positions with the 'not computed' line. Runs against website/site/dist after `npm run build`; skipped when there is no build."""
import os

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.abspath(os.path.join(HERE, "..", "..", "site", "dist", "molecule"))
pytestmark = pytest.mark.skipif(not os.path.isdir(DIST), reason="no site build (run npm run build in website/site)")


def page(mid: str) -> str:
    with open(os.path.join(DIST, mid, "index.html"), encoding="utf-8") as f:
        return f.read()


def leads_with(h: str, heading: str) -> bool:
    return h.index(heading) < h.index(">Structure<")


def test_benzene_leads_with_the_cc_anchor_and_keeps_the_cheap_card():
    h = page("A_8448043181")
    assert leads_with(h, "Infrared spectrum at the anchor level") and "own coupled-cluster dipole derivatives" in h          # the apostrophe is HTML-escaped
    assert "Compared with the cheap Hessian (B3LYP, analytic, the same dipole derivatives): spectrum overlap 0.26" in h
    assert "Infrared spectrum at the cheap level" in h and "How well is this shape known?" in h   # the cheap card follows, below the lead


def test_benzonitrile_says_its_heights_use_cheap_dipole_derivatives():
    assert "cheap-level (B3LYP) dipole derivatives" in page("A_3100da3761")


def test_naphthalene_anchor_is_positions_only():
    h = page("A_01f3186607")
    assert leads_with(h, "Infrared spectrum at the anchor level") and "not computed for this molecule yet" in h and 'class="irspec"' not in h


def test_a_molecule_without_anchor_or_heights_leads_with_positions():
    h = page("A_d9139359ab")                                                             # azulene
    assert leads_with(h, "Harmonic frequencies at the cheap level") and "Band heights are not computed for this molecule yet" in h
