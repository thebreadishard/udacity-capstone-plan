"""probes/promotion_read.py: arms from per-seed read-outs on any hold-out (the selection set too), the refusals, and the user's rule of 26 Oct
(none worse at the reported precision, one better)."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "probes"))
import promotion_read as P

BASE = {"ring-ip": 1.9, "CH-stretch": 1.3, "CH-oop": 2.4, "other": 3.1}


def seeds(hold: str, fam: dict, ratio: float, spread: tuple[float, ...] = (-0.05, 0.0, 0.05)) -> list[dict]:
    return [{hold: {"diag_rms": {f: v + e for f, v in fam.items()}, P.RATIO: ratio + e / 10}} for e in spread]


def test_an_arm_on_the_selection_set_compares_and_promotes():
    new = P.arm_from_seeds(seeds("sel", {**BASE, "other": 2.9}, 0.18), ("sel",))
    old = P.arm_from_seeds(seeds("sel", BASE, 0.18), ("sel",))
    comps = P.compare(new, old)
    assert [c.quantity for c in comps] == list(P.QUANTITIES) and all(c.hold == "sel" for c in comps)
    p = P.promotion(comps)
    assert p.promoted and p.better == ("(sel) other",) and p.worse == ()


def test_worse_at_the_reported_precision_blocks_and_a_float_tail_does_not():
    old = P.arm_from_seeds(seeds("sel", BASE, 0.18), ("sel",))
    tail = P.arm_from_seeds(seeds("sel", {**BASE, "CH-oop": 2.401, "other": 3.0}, 0.18), ("sel",))   # 2.401 reports as 2.40
    assert P.promotion(P.compare(tail, old)).promoted
    worse = P.arm_from_seeds(seeds("sel", {**BASE, "CH-oop": 2.41, "other": 3.0}, 0.18), ("sel",))
    assert P.promotion(P.compare(worse, old)).worse == ("(sel) CH-oop",)


def test_beyond_two_se_needs_a_difference_larger_than_the_spread():
    old = P.arm_from_seeds(seeds("sel", BASE, 0.18), ("sel",))
    near = P.arm_from_seeds(seeds("sel", {**BASE, "other": 3.08}, 0.18), ("sel",))
    far = P.arm_from_seeds(seeds("sel", {**BASE, "other": 2.5}, 0.18), ("sel",))
    by_q = {c.quantity: c for c in P.compare(near, old)}
    assert not by_q["other"].beyond_two_se
    assert {c.quantity: c for c in P.compare(far, old)}["other"].beyond_two_se


def test_refusals():
    with pytest.raises(ValueError, match="at least two seeds"):
        P.arm_from_seeds(seeds("sel", BASE, 0.18, spread=(0.0,)), ("sel",))
    with pytest.raises(ValueError, match="absent"):
        P.arm_from_seeds(seeds("sel", BASE, 0.18), ("a",))
    with pytest.raises(ValueError, match="different hold-outs"):
        P.compare(P.arm_from_seeds(seeds("sel", BASE, 0.18), ("sel",)), P.arm_from_seeds(seeds("a", BASE, 0.18), ("a",)))


def test_the_table_has_a_row_per_hold_out_and_read_out():
    a = P.arm_from_seeds(seeds("sel", BASE, 0.18), ("sel",))
    rows = P.comparison_table(a, a, P.compare(a, a), "new", "old")
    assert len(rows) == 2 + len(P.QUANTITIES) and "| (sel) | coupling_ratio | 0.180 (0.175–0.185) |" in rows[-1]
