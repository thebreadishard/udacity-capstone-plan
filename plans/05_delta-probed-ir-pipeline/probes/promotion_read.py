"""The comparison of a new ΔH-network version with the carried one, in one place (decision 57 with the user's rule of 26 Oct 2026: a new
version may worsen none of the five read-outs — the diagonal rms of the four families and the coupling ratio — and must improve one).

Used by chain 35's read (`chain35_read.py`, on the hold-outs) and by v1.4's search (`v14_search.py`, on the selection set). An arm is the
seed values of one model version per hold-out and read-out; it is built from `rungC_eval_saved.py` JSONs (`load_eval_arm`) or from the
trainer's per-seed records (`arm_from_seeds`). Every comparison is made on the numbers as reported (two decimals in cm⁻¹, three for the
ratio), so a float's last bits cannot decide it.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

FAMILIES = ("ring-ip", "CH-stretch", "CH-oop", "other")
RATIO = "coupling_ratio"
QUANTITIES = (*FAMILIES, RATIO)
FROZEN_B = "holdout_b_frozen_2026-10-08.txt"


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

    def mean(self, hold: str, q: str) -> float:
        v = self.values[hold][q]
        return sum(v) / len(v)

    def standard_error(self, hold: str, q: str) -> float:
        v = self.values[hold][q]
        m = self.mean(hold, q)
        return math.sqrt(sum((x - m) ** 2 for x in v) / (len(v) - 1)) / math.sqrt(len(v))


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
    promoted: bool
    worse: tuple[str, ...]
    better: tuple[str, ...]


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
    """One `rungC_eval_saved.py` JSON per seed; every one read on the frozen hold-out (b) and on the same analytic targets."""
    recs = []
    for p in paths:
        with open(p, encoding="utf-8") as f:
            rec = json.load(f)
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


def promotion(comparisons: list[Comparison]) -> Promotion:
    """The user's rule of 26 Oct: none of the read-outs worse at the reported precision, at least one better."""
    worse = tuple(f"({c.hold}) {c.quantity}" for c in comparisons if reported(c.new, c.quantity) > reported(c.carried, c.quantity))
    better = tuple(f"({c.hold}) {c.quantity}" for c in comparisons if reported(c.new, c.quantity) < reported(c.carried, c.quantity))
    return Promotion(promoted=not worse and bool(better), worse=worse, better=better)


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
