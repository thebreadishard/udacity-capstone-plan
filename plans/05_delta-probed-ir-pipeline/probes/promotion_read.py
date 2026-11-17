"""The comparison of a new ΔH-network version with the carried one, in one place: decision 57 as amended on 17 Nov 2026 (the user).

A new version is promoted (`amended_promotion`) when its composite — per seed, the mean over the arm's hold-outs and the five read-outs
(the diagonal rms of the four families and the coupling ratio) of each read-out over its line (LINES) — has a seed mean below the carried
arm's by more than the two-sided 95 % Student-t critical value times the combined standard error (degrees of freedom by Welch and
Satterthwaite), and no single read-out is worse beyond two combined standard errors. The rule of 26 Oct until 17 Nov (`promotion`: none
of the read-outs worse at the reported precision, one better) promoted about 12 % of real improvements of v1.3's and v1.4's size
(TASKS 263, probes/results_m1/promotion_rule_test_2026-11-17); it is kept for the historical reads and printed beside the new one.

Used by chain 35's read (`chain35_read.py`, on the hold-outs) and by v1.4's search (`v14_search.py`, on the selection set). An arm is the
seed values of one model version per hold-out and read-out; it is built from `rungC_eval_saved.py` JSONs (`load_eval_arm`) or from the
trainer's per-seed records (`arm_from_seeds`). Every comparison is made on the numbers as reported (two decimals in cm⁻¹, three for the
ratio), so a float's last bits cannot decide it.
"""
from __future__ import annotations

import json
import math
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "modules" / "05_support_predictor" / "m05"))
import network_kind as NK  # module 05's code is not a package

FAMILIES = ("ring-ip", "CH-stretch", "CH-oop", "other")
RATIO = "coupling_ratio"
QUANTITIES = (*FAMILIES, RATIO)
FROZEN_B = "holdout_b_frozen_2026-10-08.txt"
LINES = {**dict.fromkeys(FAMILIES, 3.0), RATIO: 0.25}   # cm⁻¹ for a family's diagonal rms; the coupling ratio's line
CONFIDENCE = 0.95                                       # the composite's two-sided level (decision 57 as amended on 17 Nov)


def digits(quantity: str) -> int:
    """The reported precision: three decimals for the coupling ratio, two for a family's rms in cm⁻¹."""
    return 3 if quantity == RATIO else 2


def reported(value: float, quantity: str) -> float:
    return round(value, digits(quantity))


@dataclass(frozen=True)
class Arm:
    """Seed values per hold-out and read-out, and the molecules read on analytic targets."""
    values: dict[str, dict[str, tuple[float, ...]]]
    substituted: frozenset[str]

    @property
    def holdouts(self) -> tuple[str, ...]:
        return tuple(self.values)

    @property
    def n_seeds(self) -> int:
        counts = {len(v) for per_q in self.values.values() for v in per_q.values()}
        if len(counts) != 1:
            raise ValueError(f"the arm's read-outs hold different numbers of seeds ({sorted(counts)})")
        return counts.pop()

    def mean(self, hold: str, q: str) -> float:
        return _mean(self.values[hold][q])

    def standard_error(self, hold: str, q: str) -> float:
        return _standard_error(self.values[hold][q])


def _mean(values: tuple[float, ...]) -> float:
    return sum(values) / len(values)


def _standard_error(values: tuple[float, ...]) -> float:
    """The standard error of the seed mean (sample standard deviation over the square root of the seed count)."""
    m = _mean(values)
    return math.sqrt(sum((x - m) ** 2 for x in values) / (len(values) - 1)) / math.sqrt(len(values))


@dataclass(frozen=True)
class Comparison:
    hold: str
    quantity: str
    new: float
    carried: float
    difference: float
    beyond_two_se: bool


@dataclass(frozen=True)
class Promotion:
    """The verdict of the rule of 26 Oct (until 17 Nov 2026)."""
    promoted: bool
    worse: tuple[str, ...]
    better: tuple[str, ...]


@dataclass(frozen=True)
class Composite:
    """One arm's composite: per seed, the mean over its hold-outs of `on_lines`."""
    per_seed: tuple[float, ...]

    @property
    def mean(self) -> float:
        return _mean(self.per_seed)

    @property
    def standard_error(self) -> float:
        return _standard_error(self.per_seed)


@dataclass(frozen=True)
class AmendedPromotion:
    """The verdict of decision 57 as amended on 17 Nov 2026, with the rule of 26 Oct's verdict beside it (`old_rule`, deciding nothing)."""
    promoted: bool
    composite_new: float
    composite_carried: float
    composite_difference: float          # new minus carried: below zero is better
    combined_se: float
    df: float                            # Welch–Satterthwaite
    t_critical: float
    threshold: float                     # t_critical × combined_se: the difference must lie below minus this
    worse_beyond_two_se: tuple[str, ...]
    old_rule: Promotion


def arm_from_seeds(seeds: list[dict], holdouts: tuple[str, ...], substituted: frozenset[str] = frozenset()) -> Arm:
    """An arm from per-seed read-out dicts ({hold: {"diag_rms": {...}, "coupling_ratio": x}}), at least two seeds."""
    if len(seeds) < 2:
        raise ValueError(f"an arm needs at least two seeds for a standard error, got {len(seeds)}")
    missing = [h for h in holdouts if any(h not in s for s in seeds)]
    if missing:
        raise ValueError(f"hold-out(s) {missing} absent from a seed's read-outs")
    values = {h: {q: tuple(float(s[h][RATIO] if q == RATIO else s[h]["diag_rms"][q]) for s in seeds) for q in QUANTITIES} for h in holdouts}
    return Arm(values=values, substituted=substituted)


def load_eval_arm(paths: list[Path], holdouts: tuple[str, ...] = ("a", "b")) -> Arm:
    """One `rungC_eval_saved.py` JSON per seed; every one read on the frozen hold-out (b) and on the same analytic targets. A record
    of a release network (decision 66) is refused: it trained on the hold-outs, and an arm is a hold-out error."""
    recs = []
    for p in paths:
        with open(p, encoding="utf-8") as f:
            rec = json.load(f)
        NK.refuse_release(NK.stated_kind(rec, Path(p).name), Path(p).name, "an arm of its read-outs")
        if not str(rec.get("holdout_b_file", "")).endswith(FROZEN_B):
            raise ValueError(f"{p} is not read on the frozen hold-out (b) of 8 Oct")
        recs.append(rec)
    subs = {frozenset(r.get("substituted_analytic", [])) for r in recs}
    if len(subs) != 1:
        raise ValueError(f"the seeds of {paths[0].parent / paths[0].stem}… were read on different analytic targets")
    return arm_from_seeds(recs, holdouts, subs.pop())


def compare(new: Arm, carried: Arm) -> list[Comparison]:
    """Seed means of every read-out on the new arm's hold-outs; 'beyond two SE' when the difference exceeds twice the combined standard error."""
    if new.holdouts != carried.holdouts:
        raise ValueError(f"the arms are read on different hold-outs ({new.holdouts} against {carried.holdouts})")
    if new.substituted != carried.substituted:
        raise ValueError(f"the arms were read on different analytic targets ({len(new.substituted)} against {len(carried.substituted)} molecules)")
    out = []
    for h in new.holdouts:
        for q in QUANTITIES:
            d = new.mean(h, q) - carried.mean(h, q)
            se = math.sqrt(new.standard_error(h, q) ** 2 + carried.standard_error(h, q) ** 2)
            out.append(Comparison(h, q, new.mean(h, q), carried.mean(h, q), d, abs(d) > 2 * se))
    return out


def _label(c: Comparison) -> str:
    return f"({c.hold}) {c.quantity}"


def promotion(comparisons: list[Comparison]) -> Promotion:
    """The user's rule of 26 Oct, decision 57 until 17 Nov 2026: none of the read-outs worse at the reported precision, at least one
    better. Chain 35's read (v1.3) was decided by it; since 17 Nov it is printed beside `amended_promotion` and decides nothing."""
    worse = tuple(_label(c) for c in comparisons if reported(c.new, c.quantity) > reported(c.carried, c.quantity))
    better = tuple(_label(c) for c in comparisons if reported(c.new, c.quantity) < reported(c.carried, c.quantity))
    return Promotion(promoted=not worse and bool(better), worse=worse, better=better)


def on_lines(read: Mapping[str, float]) -> float:
    """The mean of the five read-outs ({quantity: value}), each over its line: 1.0 = on the lines on average."""
    return sum(read[q] / LINES[q] for q in QUANTITIES) / len(QUANTITIES)


def composite(arm: Arm) -> Composite:
    """Per seed, the mean over the arm's hold-outs of `on_lines`: every hold-out has the five read-outs, so this is the mean over all
    hold-outs × read-outs of value over line."""
    return Composite(tuple(_mean(tuple(on_lines({q: arm.values[h][q][i] for q in QUANTITIES}) for h in arm.holdouts))
                           for i in range(arm.n_seeds)))


def welch_df(new: Composite, carried: Composite) -> float:
    """The Welch–Satterthwaite degrees of freedom of the difference of two seed means."""
    a, b = new.standard_error ** 2, carried.standard_error ** 2
    if a + b == 0:
        raise ValueError("neither arm's composite varies over its seeds: there is no standard error to judge the difference by")
    return (a + b) ** 2 / (a ** 2 / (len(new.per_seed) - 1) + b ** 2 / (len(carried.per_seed) - 1))


def t_critical(df: float) -> float:
    """The two-sided Student-t critical value at CONFIDENCE for `df` degrees of freedom."""
    return float(stats.t.ppf(1 - (1 - CONFIDENCE) / 2, df))


def worse_beyond_two_se(comparisons: list[Comparison]) -> tuple[str, ...]:
    """The read-outs on which the new arm is worse than the carried one beyond two combined standard errors (the amended rule's guard)."""
    return tuple(_label(c) for c in comparisons if c.difference > 0 and c.beyond_two_se)


def amended_promotion(new: Arm, carried: Arm) -> AmendedPromotion:
    """Decision 57 as amended on 17 Nov 2026 (the user): the composite's seed mean below the carried arm's by more than t_critical ×
    the combined standard error, and no read-out worse beyond two standard errors."""
    comparisons = compare(new, carried)
    c_new, c_carried = composite(new), composite(carried)
    se = math.sqrt(c_new.standard_error ** 2 + c_carried.standard_error ** 2)
    df = welch_df(c_new, c_carried)
    t = t_critical(df)
    difference = c_new.mean - c_carried.mean
    guard = worse_beyond_two_se(comparisons)
    return AmendedPromotion(promoted=difference < -t * se and not guard, composite_new=c_new.mean, composite_carried=c_carried.mean,
                            composite_difference=difference, combined_se=se, df=df, t_critical=t, threshold=t * se,
                            worse_beyond_two_se=guard, old_rule=promotion(comparisons))


def amended_lines(p: AmendedPromotion) -> list[str]:
    """The amended rule's two conditions and the rule of 26 Oct beside them, as report lines."""
    beyond = p.composite_difference < -p.threshold
    old = p.old_rule
    return [f"- Composite (each read-out over its line, mean over hold-outs × read-outs, per seed): {p.composite_new:.3f} against "
            f"{p.composite_carried:.3f}, difference {p.composite_difference:+.3f}; the line is −{p.threshold:.3f} (t {p.t_critical:.3f} at "
            f"{p.df:.1f} degrees of freedom × combined SE {p.combined_se:.4f}): {'below it' if beyond else '**not below it**'}.",
            "- Guard (no read-out worse beyond two SE): "
            + (f"**worse beyond two SE on {', '.join(p.worse_beyond_two_se)}**." if p.worse_beyond_two_se else "none."),
            f"- Beside them, deciding nothing — the rule of 26 Oct (none worse at the reported precision, one better): "
            f"{'promoted' if old.promoted else 'not promoted'}, worse on {', '.join(old.worse) or 'none'}, better on {len(old.better)}."]


def cell(values: tuple[float, ...], quantity: str) -> str:
    """'mean (min–max)' at the reported precision."""
    d = digits(quantity)
    return f"{sum(values) / len(values):.{d}f} ({min(values):.{d}f}–{max(values):.{d}f})"


def comparison_table(new: Arm, carried: Arm, comparisons: list[Comparison], new_name: str, carried_name: str) -> list[str]:
    lines = [f"| hold-out | quantity | {new_name} | {carried_name} | difference | beyond 2 SE |", "|---|---|---|---|---|---|"]
    for c in comparisons:
        d = digits(c.quantity)
        lines.append(f"| ({c.hold}) | {c.quantity} | {cell(new.values[c.hold][c.quantity], c.quantity)} | "
                     f"{cell(carried.values[c.hold][c.quantity], c.quantity)} | {c.difference:+.{d}f} | {'yes' if c.beyond_two_se else 'no'} |")
    return lines


def write_atomic(target: Path, content: str) -> None:
    tmp = target.with_name(target.name + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(target)
