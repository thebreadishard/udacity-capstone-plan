"""probes/hot_band_desk_naphthalene.py's read on synthetic values, before its numbers (the hot-band registration's amendment of 4 Nov 2026):
§2's pass lines at their edges, the D2h labels and the refusal of a mode that is not symmetric, the mapping rule."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes"))
H = pytest.importorskip("hot_band_desk_naphthalene")


def test_the_pass_lines_at_their_edges():
    noise = {"16": 0.05, "13": 0.2, "48": 0.0}
    rows = H.passes({"16": -1.3, "13": -0.5, "48": -0.55}, noise)
    assert rows["16"]["P1_sign"] and rows["16"]["P2_size"]            # exactly a factor 2 below −2.6
    assert not rows["13"]["P1_sign"] and not rows["13"]["P2_size"]    # wrong sign, 1.1 away
    assert rows["48"]["P2_size"]                                      # within the 0.3 floor (0.25 away) though beyond a factor 1.8
    assert rows["16"]["P3_ok"] and not rows["13"]["P3_ok"]
    assert not H.passes({"16": -1.29, "13": 0.6, "48": -0.3}, noise)["16"]["P2_size"]


def test_labels_from_characters_and_a_refusal():
    chars = np.array([[-1, 1, 1, -1], [-1, -1, -1, -1], [1, 1, -1, -1], [1, 1, 1, 1]], float) * 0.999
    assert H.classify(chars) == ["b3u", "au", "b1g", "ag"]
    with pytest.raises(SystemExit):
        H.classify(np.array([[0.7, 1, 1, 1]]))
    assert H.classify(np.array([[-0.95, -1, -1, -1]])) == ["au"]


def test_the_mapping_rule():
    labels = ["b3u", "au", "b1u", "b1g", "b3u", "b2g", "b3u", "b3u"]
    assert H.mapping(labels) == {"46": 6, "48": 0, "13": 1, "16": 3}
