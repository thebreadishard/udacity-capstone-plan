"""The pipeline's demo page (`modules/08_industry_synthesis/m08/demo_page.py`, TASKS 146): the drawn scale, the family rows, the refusals,
and the page from the committed demo results, whose numbers must be the records'."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np
import pytest

from pin_tools import PLAN

sys.path.insert(0, str(PLAN / "modules" / "08_industry_synthesis"))
from m08 import demo_page as D
from m08 import pipeline as P

GRID = np.arange(500.0, 3500.0, 2.0)


def _points(svg: str, key: str) -> np.ndarray:
    pts = re.search(rf'class="c-{key}" points="([^"]+)"', svg).group(1)
    return np.array([[float(v) for v in p.split(",")] for p in pts.split()])


def test_the_highest_point_sits_at_its_wavenumber_and_the_top_of_the_plot():
    peak = np.exp(-(((GRID - 1000.0) / 5.0) ** 2))
    xy = _points(D.svg_spectrum(GRID, {"network": peak, "b3lyp": 0.5 * peak}, "t"), "network")
    top = xy[np.argmin(xy[:, 1])]
    assert top[0] == pytest.approx(D._x(1000.0), abs=0.1)
    assert top[1] == pytest.approx(D.PAD_T, abs=0.1)
    assert D._x(3500.0) < D._x(500.0)                     # wavenumber decreases to the right


def test_curves_share_one_scale():
    peak = np.exp(-(((GRID - 1600.0) / 5.0) ** 2))
    svg = D.svg_spectrum(GRID, {"network": peak, "b3lyp": 0.5 * peak}, "t")
    half = _points(svg, "b3lyp")[:, 1].min()
    assert half == pytest.approx(D._y(0.5), abs=0.1)


def test_an_all_zero_panel_is_refused():
    with pytest.raises(ValueError, match="every curve is zero"):
        D.svg_spectrum(GRID, {"network": np.zeros_like(GRID)}, "empty")


READ = {f: {"mean": 1.0} for f in D.FAMILY_ORDER}


def test_family_rows_count_bands_and_keep_the_order():
    bands = [{"family": "other", "licensed": False}, {"family": "ring-ip", "licensed": True}, {"family": "ring-ip", "licensed": True}]
    rows = D.family_rows(bands, READ, READ)
    assert [(r["family"], r["bands"], r["licensed"]) for r in rows] == [("ring-ip", 2, True), ("other", 1, False)]


def test_family_rows_refuse_a_split_licence_and_an_unknown_family():
    with pytest.raises(ValueError, match="disagree"):
        D.family_rows([{"family": "CH-oop", "licensed": True}, {"family": "CH-oop", "licensed": False}], READ, READ)
    with pytest.raises(ValueError, match="outside"):
        D.family_rows([{"family": "CO-stretch", "licensed": True}], READ, READ)


def test_the_page_refuses_two_network_versions():
    def panel(version: str) -> D.Panel:
        return D.Panel(D.DEMO[0], {}, {"network": {"name": P.NETWORK, "version": version}}, None, GRID, {})
    with pytest.raises(ValueError, match="mixes network versions"):
        D.page([panel("1.3"), panel("1.4")])


@pytest.mark.parametrize(("seconds", "text"), [(2.3, "2 s"), (480.4, "8 min"), (13353.7, "3.7 h")])
def test_times_read_in_their_unit(seconds, text):
    assert D._minutes(seconds) == text


def test_the_page_from_the_demo_results_carries_the_records_numbers():
    for d in D.DEMO:
        vs = d.folder / "vs_corpus.json"
        if not (d.folder / "certificate.json").exists() or (vs.exists() and not (Path(json.loads(vs.read_text("utf-8"))["corpus"])
                                                                                   / P.TRUTH_HESSIAN).exists()):
            pytest.skip(f"{d.folder.name}: the demo result or its corpus truth is not on this machine")
    panels = [D.load_panel(d) for d in D.DEMO]
    text = D.page(panels)
    for p in panels:
        assert f'id="{p.certificate["molecule"]["name"]}"' in text
        if p.vs_corpus is not None:
            assert f'{p.vs_corpus["against_truth"]["all_modes"]["network"]:.2f} cm⁻¹' in text
            assert set(p.curves) == {"network", "b3lyp", "truth"}
        else:
            assert set(p.curves) == {"network", "b3lyp"}
