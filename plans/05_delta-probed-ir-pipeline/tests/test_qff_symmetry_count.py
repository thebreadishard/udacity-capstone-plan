"""probes/qff_symmetry_count.py (13 Oct 2026): the mode classification against textbook counts, and HBC's slightly non-planar geometry that
made e8_symmetry.point_group_ops return no operation at all before _kabsch_both."""
import json
import os
import sys

import numpy as np

PROBES = os.path.join(os.path.dirname(__file__), "..", "probes")
sys.path.insert(0, PROBES)
import qff_symmetry_count as Q  # noqa: E402
from e8_symmetry import BOHR, point_group_ops  # noqa: E402


def _benzene():
    r, h = 1.39 / BOHR, 1.09 / BOHR
    ang = np.arange(6) * np.pi / 3
    c = np.c_[r * np.cos(ang), r * np.sin(ang), np.zeros(6)]
    return ["C"] * 6 + ["H"] * 6, np.vstack([c, c * (r + h) / r])


def test_benzene_modes_by_symmetry():
    """D6h benzene: 2 a1g, 8 other non-degenerate modes (a2g, 2 b1u, 2 b2g, 2 b2u, a2u), 10 degenerate pairs; 33 Hessians with the ±
    saving, 23 with the pair saving."""
    r = Q.count(*_benzene())
    assert (r["order"], r["M"], r["n_ts"], r["n_other_nondeg"], r["n_pairs"]) == (24, 30, 2, 8, 10)
    assert (r["full"], r["pm"], r["pair"]) == (61, 33, 23) and r["pair_problems"] == []


def test_tetracene_has_fifteen_totally_symmetric_modes():
    r = Q.count(*Q.tetracene_ideal())
    assert (r["order"], r["M"], r["n_ts"], r["n_pairs"]) == (8, 84, 15, 0)


def test_a_slightly_nonplanar_molecule_keeps_its_operations():
    """PAHdb's HBC (z within ±0.37 bohr, D3d): before 13 Oct the three reference atoms' Kabsch fit returned the plane's reflection for the
    identity, and a non-planar molecule has no reflection partner to recover it — point_group_ops found no operation at all."""
    s = json.load(open(Q.SELECTION, encoding="utf-8"))["test"]["hexa-peri-hexabenzocoronene"]
    assert len(point_group_ops(s["symbols"], np.array(s["xyz"]) / BOHR)) == 12


def test_selection_file_is_readable():
    sel = json.load(open(Q.SELECTION, encoding="utf-8"))
    assert {"coronene", "ovalene"} <= set(sel["test"])
