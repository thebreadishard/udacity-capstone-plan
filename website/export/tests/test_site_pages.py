"""TASKS 44–45 (10 Oct 2026): every built molecule page leads with the best spectrum it has — the anchor's (with heights from the anchor's own CC
dipole derivatives on benzene, the B3LYP ones said on benzonitrile, positions only on naphthalene), else the cheap level's with heights, else the
cheap positions with the 'not computed' line. Design §10 (10 Oct 2026): under an anchor the cheap input is the lead card's lower panel, the
reading notes sit behind a tap, and the long flag story behind a short chip. Runs against website/site/dist after `npm run build`; skipped when
there is no build."""
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


def lead_card(h: str) -> str:
    start = h.index('class="card first')
    return h[start:h.index("</section>", start)]


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


def test_anchor_card_draws_the_cheap_input_as_its_lower_panel_and_the_cheap_card_no_second_chart():
    for mid in ("A_8448043181", "A_3100da3761"):                                         # benzene, benzonitrile
        h = page(mid)
        card = lead_card(h)
        assert ">anchor</text>" in card and ">cheap input (B3LYP)</text>" in card
        assert h.count('class="irspec"') == 1 and "Drawn as the lower panel of the anchor spectrum above." in h


def test_key_line_shows_and_the_reading_notes_sit_behind_a_tap():
    card = lead_card(page("A_8448043181"))
    key, notes = card.index("Spectrum overlap with the anchor (1 = the same shape): network, held-out test 0.37"), card.index('class="howto"')
    assert key < notes < card.index("Compared with the cheap Hessian") and notes < card.index("The network's prediction, shown as a test.")


def test_the_long_flag_story_sits_behind_a_short_chip():
    h = page("A_8448043181")
    chip = h[h.index('class="chip flag"'):]
    chip = chip[:chip.index("</details>")]
    assert ">analytic Hessian</summary>" in chip and "finite-difference Hessian was noisy" in chip


def test_a_cheap_lead_page_keeps_one_panel_and_the_notes_behind_a_tap():
    h = page("A_07cadc7923")
    card = lead_card(h)
    assert "Infrared spectrum at the cheap level" in card and "cheap input (B3LYP)</text>" not in card
    assert card.index('class="howto"') < card.index("Band heights from the molecule")


def test_every_series_is_drawn_once():
    """The user, 10 Oct 19:3x (pyridine): the B3LYP row stood in the anchor chart and again in the frequencies chart."""
    for mid in ("A_6e858b26e5", "A_01f3186607"):                                         # pyridine, naphthalene: positions-only anchors
        h = page(mid)
        assert h.count('class="spectrum"') == 1 and "ωB97X</text>" in lead_card(h)
        assert "Both functionals are drawn in the anchor chart above" in h
    h = page("A_8448043181")                                                             # benzene: heights; the table carries ωB97X
    assert 'class="spectrum"' not in h and h.count('class="irspec"') == 1
    assert page("A_d9139359ab").count('class="spectrum"') == 1                          # azulene: the frequencies card leads with its chart


def test_a_long_flag_label_gets_a_short_chip():
    assert ">finite-difference Hessian noisy</summary>" in page("A_6e858b26e5")
