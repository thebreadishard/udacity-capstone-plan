"""TASKS 38 (9 Oct 2026): the five-membered-ring pool selects pending A2 rows of the four families only, refuses the frozen hold-out (b), and prices
by interpolated measured hours over two runners per box."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "modules" / "05_support_predictor" / "corpus"))
import five_ring_pool as FP  # noqa: E402


def _row(i, name, layer="A2", status="pending", n=22):
    return {"id": i, "name": name, "layer": layer, "status": status, "n_atoms": str(n)}


def test_select_keeps_only_pending_a2_rows_of_the_four_families():
    m = [_row("x1", "carbazole+CH3"), _row("x2", "fluorene+CH3"), _row("x3", "acenaphthylene+OH", status="done"),
         _row("x4", "dibenzofuran+CN", layer="B"), _row("x5", "acenaphthylene+F")]
    assert [r["id"] for r in FP.select(m, set())] == ["x5", "x1"]          # sorted by family, then id


def test_select_refuses_the_frozen_holdout_b():
    with pytest.raises(ValueError, match="hold-out"):
        FP.select([_row("x1", "carbazole+CH3")], {"x1"})


def test_run_order_is_round_robin_smallest_first():
    rows = [_row("c2", "carbazole+X", n=24), _row("c1", "carbazole+Y", n=21), _row("a1", "acenaphthylene+Z", n=22),
            _row("d1", "dibenzofuran", n=20)]
    assert [r["id"] for r in FP.run_order(rows)] == ["a1", "c1", "d1", "c2"]


def test_price_interpolates_and_splits_over_two_runners():
    p = FP.price([_row("a", "carbazole", n=21), _row("b", "carbazole", n=23)], {20: 1.0, 22: 2.0, 24: 4.0}, 0.2)
    assert p["runner_hours"] == pytest.approx(1.5 + 3.0) and p["box_hours"] == pytest.approx(2.25) and p["eur"] == pytest.approx(0.45)
    assert p["n_outside_range"] == 0


def test_price_outside_the_measured_range_follows_the_power_law_or_refuses():
    """10 Oct 2026: no silent clamping at the ends of the measured range."""
    table = {20: 1.0, 40: 8.0}                                            # h ∝ N³ exactly
    p = FP.price([_row("big", "carbazole", n=80)], table, 0.2)
    assert p["n_outside_range"] == 1 and p["power_law_exponent"] == pytest.approx(3.0) and p["runner_hours"] == pytest.approx(64.0)
    small = FP.price([_row("small", "carbazole", n=10)], table, 0.2)
    assert small["runner_hours"] == pytest.approx(0.125)                 # not clamped up to the 20-atom value
    with pytest.raises(ValueError, match="outside the measured range"):
        FP.price([_row("big", "carbazole", n=80)], table, 0.2, outside="refuse")
    with pytest.raises(ValueError, match="at least two"):
        FP.price([_row("x", "carbazole")], {}, 0.2)
