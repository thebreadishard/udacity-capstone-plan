"""probes/promotion_read.py: arms from per-seed read-outs on any hold-out (the selection set too), the refusals, the user's rule of 26 Oct
(none worse at the reported precision, one better), and decision 57 as amended on 17 Nov (the composite beyond the Student-t line with
Welch's degrees of freedom; no read-out worse beyond two SE)."""
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


def on_the_lines(holds: dict[str, tuple[float, ...]]) -> P.Arm:
    """An arm whose five read-outs on each hold-out sit at k times their lines, k per seed."""
    return P.Arm(values={h: {q: tuple(k * P.LINES[q] for k in ks) for q in P.QUANTITIES} for h, ks in holds.items()}, substituted=frozenset())


def test_the_composite_and_welchs_degrees_of_freedom_by_hand():
    new = P.composite(on_the_lines({"a": (0.8, 0.9, 1.0), "b": (1.0, 1.1, 1.2)}))     # per seed the mean of the two: 0.9, 1.0, 1.1
    carried = P.composite(on_the_lines({"a": (1.1, 1.3, 1.5), "b": (1.1, 1.3, 1.5)}))
    assert new.per_seed == pytest.approx((0.9, 1.0, 1.1)) and new.mean == pytest.approx(1.0) and carried.mean == pytest.approx(1.3)
    assert new.standard_error ** 2 == pytest.approx(0.01 / 3) and carried.standard_error ** 2 == pytest.approx(0.04 / 3)
    assert P.welch_df(new, carried) == pytest.approx((0.05 / 3) ** 2 / ((0.01 / 3) ** 2 / 2 + (0.04 / 3) ** 2 / 2))   # 2.941
    assert P.welch_df(new, new) == pytest.approx(4.0)                               # equal spreads, three seeds each: n1 + n2 - 2
    with pytest.raises(ValueError, match="no standard error"):
        P.welch_df(P.Composite((1.0, 1.0)), P.Composite((1.2, 1.2)))


@pytest.mark.parametrize(("df", "tabulated"), [(2, 4.303), (4, 2.776), (10, 2.228)])
def test_the_t_critical_values_are_the_tables(df, tabulated):
    assert P.t_critical(df) == pytest.approx(tabulated, abs=5e-4)


def test_the_score_on_the_lines_is_one():
    assert P.on_lines(P.LINES) == pytest.approx(1.0) and P.on_lines({**P.LINES, "other": 4.5}) == pytest.approx(1.1)


def amended(fam: dict, ratio: float) -> P.AmendedPromotion:
    return P.amended_promotion(P.arm_from_seeds(seeds("sel", fam, ratio), ("sel",)), P.arm_from_seeds(seeds("sel", BASE, 0.18), ("sel",)))


def test_one_cell_worse_inside_two_se_refused_by_the_old_rule_promoted_by_the_amended():
    better = {f: v - 0.3 for f, v in BASE.items()} | {"CH-oop": BASE["CH-oop"] + 0.02}  # CH-oop worse by 0.02, two SE are 0.08
    p = amended(better, 0.15)
    assert p.promoted and p.worse_beyond_two_se == () and p.df == pytest.approx(4.0)
    assert p.composite_difference < -p.threshold and p.threshold == pytest.approx(P.t_critical(4.0) * p.combined_se)
    assert not p.old_rule.promoted and p.old_rule.worse == ("(sel) CH-oop",)
    lines = P.amended_lines(p)
    assert "below it." in lines[0] and lines[1].endswith("none.") and "the rule of 26 Oct" in lines[2] and "not promoted" in lines[2]


def test_one_cell_worse_beyond_two_se_is_refused_by_the_guard_though_the_composite_is_better():
    p = amended({f: v - 0.3 for f, v in BASE.items()} | {"CH-oop": BASE["CH-oop"] + 0.2}, 0.15)
    assert p.composite_difference < -p.threshold and not p.promoted and p.worse_beyond_two_se == ("(sel) CH-oop",)
    assert "**worse beyond two SE on (sel) CH-oop**" in P.amended_lines(p)[1]


def test_identical_arms_are_not_promoted():
    p = amended(BASE, 0.18)
    assert not p.promoted and p.composite_difference == pytest.approx(0.0) and p.worse_beyond_two_se == () and not p.old_rule.promoted
    assert "**not below it**" in P.amended_lines(p)[0]


def test_a_better_composite_inside_the_t_line_is_not_promoted():
    p = amended({**BASE, "other": BASE["other"] - 0.05}, 0.18)                       # better on one cell by 0.05: the old rule promotes
    assert p.old_rule.promoted and not p.promoted and -p.threshold < p.composite_difference < 0


def test_an_arm_with_uneven_seed_counts_is_refused():
    arm = P.Arm(values={"sel": {q: (1.0, 2.0) for q in P.QUANTITIES} | {P.RATIO: (0.1, 0.2, 0.3)}}, substituted=frozenset())
    with pytest.raises(ValueError, match="different numbers of seeds"):
        P.composite(arm)
