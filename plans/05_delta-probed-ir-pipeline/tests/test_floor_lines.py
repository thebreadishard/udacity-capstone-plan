"""probes/floor_lines.py (TASKS 65, 15 Oct 2026): the registered lines both floor tests share — exact pooling over molecules of different sizes,
the ring-coupling ratio as E6.readout defines it, line 1's size bound, line 2's power law and its refusal to fit fewer than three points."""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes"))
import floor_lines as FL  # noqa: E402


def test_error_sums_split_per_family_and_ring_couplings():
    K = np.diag([1.0, 2.0, 3.0, 4.0])
    K[1, 2] = K[2, 1] = 0.5                                               # a coupling inside the ring family (modes 1 and 2)
    Kf = K + np.diag([0.0, 1.0, 2.0, 0.0])
    Kf[1, 2] = Kf[2, 1] = 0.75
    s = FL.error_sums(K, Kf, ["CH-stretch", "ring-ip", "ring-ip", "other"])
    assert s["ring-ip"] == [5.0, 2] and s["CH-stretch"] == [0.0, 1] and s["CH-oop"] == [0.0, 0]
    assert s["ring_coupling"] == [0.0625, 0.25]


def test_pooling_is_exact_and_the_ratio_matches_e6():
    a = {"ring-ip": [4.0, 1], "ring_coupling": [1.0, 4.0]}
    b = {"ring-ip": [0.0, 3], "ring_coupling": [0.0, 12.0]}
    assert FL.pooled([a, b], "ring-ip") == pytest.approx(1.0)              # √(4/4), not the mean of 2 and 0
    assert FL.pooled([a, b], "ring_coupling") == pytest.approx(0.25)
    assert np.isnan(FL.pooled([{"CH-oop": [0.0, 0]}], "CH-oop"))
    assert FL.per_molecule(a, "ring-ip") == 2.0 and FL.per_molecule(b, "ring-ip") is None


def test_line_1_bound_is_lowered_until_thirty_molecules_are_in():
    assert FL.line_1_bound([30] * 10 + [24] * 15 + [23] * 10 + [10] * 50) == 23
    assert FL.line_1_bound([26] * 30) == 25


def test_the_forecast_recovers_a_known_power_law_and_needs_three_points():
    pts = [(n, 0.02 * n ** 1.3) for n in (8, 10, 15, 20, 30)]              # the 8-atom point is below the fit's bound and left out
    at60, interval, n_fit = FL.forecast(pts, np.random.default_rng(0))
    assert at60 == pytest.approx(0.02 * 60 ** 1.3) and n_fit == 4 and interval[0] == pytest.approx(interval[1])
    assert FL.forecast(pts[:3], np.random.default_rng(0))[1:] == (None, 2)


def test_the_families_are_the_read_outs():
    la = pytest.importorskip("learning_curve_layerA", reason="module 05 on the path needs torch")
    assert tuple(la.FAMILIES) == FL.FAMILIES



def test_the_binned_forecast_recovers_a_power_law_and_needs_three_bins():
    items = [(n, [(0.02 * n ** 1.3) ** 2 * 10, 10]) for n in [16, 18, 21, 22, 25, 26, 30, 31] * 6]
    assert FL.binned_forecast(items) == pytest.approx(0.02 * 60 ** 1.3, rel=0.02)
    assert np.isnan(FL.binned_forecast(items[:2]))                          # one bin only
    exact = [(n, [1e-24, 10]) for n in (8, 10, 12, 14) * 6]                # an exact-fit regime below 15 atoms
    assert FL.binned_forecast(exact + items, FL.AMENDED) == pytest.approx(0.02 * 60 ** 1.3, rel=0.02)
    assert FL.binned_forecast(exact + items, FL.ORIGINAL) > 10 * 0.02 * 60 ** 1.3     # what the rule prevents
