"""Amendment (B) of 7 Oct 2026: the pure parts of probes/t3_coupling_shape.py — the ring-pair selection matches the T3 read-out's, the shape statistics
recover a known relation, and the pooled rms is an rms."""
import sys
from pathlib import Path

import numpy as np
import pytest

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
import t3_coupling_shape as S  # noqa: E402


def test_ring_pairs_selects_upper_triangle_of_the_ring_block():
    K = np.arange(25.0).reshape(5, 5)
    fam = ["ring-ip", "other", "ring-ip", "CH-oop", "ring-ip"]
    assert S.ring_pairs(K, fam, "ring-ip").tolist() == [K[0, 2], K[0, 4], K[2, 4]]
    assert S.ring_pairs(K, ["other"] * 5, "ring-ip").size == 0


def test_shape_stats_recovers_scale_and_sign():
    rng = np.random.default_rng(0)
    x = rng.normal(size=50)
    s = S.shape_stats(x, 0.4 * x)
    assert s["cos"] == pytest.approx(1.0) and s["slope"] == pytest.approx(0.4) and s["r"] == pytest.approx(1.0)
    assert S.shape_stats(x, -x)["cos"] == pytest.approx(-1.0)
    y = rng.normal(size=50)
    assert abs(S.shape_stats(x, y)["cos"]) < 0.5


def test_pooled_rms():
    assert S.pooled_rms([3.0, 4.0]) == pytest.approx(np.sqrt(12.5))
