"""spot_coordinates.draw: the registered rule for the spot-check anchors' coordinates (TASKS 36)."""
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "probes"))
import spot_coordinates as SC  # noqa: E402


def _benzene_like(tilt=0.0):
    ang = np.arange(6) * np.pi / 3
    c = np.c_[2.6 * np.cos(ang), 2.6 * np.sin(ang), np.zeros(6)]
    h = np.c_[4.7 * np.cos(ang), 4.7 * np.sin(ang), np.zeros(6)]
    x = np.vstack([h[:2], c, h[2:]])                       # H first: the rule must pick by element, not by position 0
    rot = np.array([[np.cos(tilt), 0, np.sin(tilt)], [0, 1, 0], [-np.sin(tilt), 0, np.cos(tilt)]])
    return ["H", "H"] + ["C"] * 6 + ["H"] * 4, x @ rot.T


def test_first_c_and_h_axes():
    sym, x = _benzene_like()
    rows = SC.draw(sym, x)
    assert [(r["element"], r["atom"], r["kind"]) for r in rows] == [
        ("C", 2, "out-of-plane"), ("C", 2, "in-plane"), ("H", 0, "out-of-plane"), ("H", 0, "in-plane")]
    assert rows[0]["k"] == 3 * 2 + 2 and rows[2]["k"] == 2       # z is out of plane
    assert rows[1]["axis"] in "xy" and rows[1]["oop_share"] < 1e-6


def test_small_tilt_is_accepted_and_recorded():
    sym, x = _benzene_like(tilt=0.1)
    rows = SC.draw(sym, x)
    assert rows[0]["axis"] == "z" and 0.98 < rows[0]["oop_share"] < 1.0
    assert rows[1]["axis"] == "y"                                # the tilt is about y, so y stays fully in plane


def test_large_tilt_is_refused():
    sym, x = _benzene_like(tilt=0.6)
    with pytest.raises(ValueError, match="plane normal"):
        SC.draw(sym, x)
