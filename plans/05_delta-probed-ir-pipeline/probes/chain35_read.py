"""Chain 35's registered read: do analytic training labels close the 'other' family? (registration 1 of
GoalGathering/notes/Design_2026-10-05_Analytic_Labels_and_Stepping_Stone.md, amendments of 8 and 26 Oct; the read is a script, not a model pass).

    python probes/chain35_read.py --new out/E7_rungC_chain35_analytic_eval_frozenb_seed{0,1,2}.json
                                  --carried out/E7_rungC_chain34_eval_c35labels_seed{0,1,2}.json --out out/E7_rungC_chain35_read

Both arms are `rungC_eval_saved.py` reads on the same analytic targets and the frozen hold-out (b) of 8 Oct: chain 35's three seeds and the
carried chain 34's three seeds read again on the corpus as it stands (like for like — chain 34's table of 5 Oct read 36 analytic molecules,
Wednesday's corpus about 809). Registered lines on hold-out (a), seed means:
- 'other' ≤ 3 with ring-ip ≤ 3, CH-oop ≤ 3 and coupling ratio ≤ 0.25 → T1 met in every family at the proxy level;
- otherwise 'other' falls by ≥ 0.3 against chain 34 → the labels were part of it, the low-mode input is designed on analytic labels;
- otherwise → the labels were not it; the input design is the next lever.
The fall is read against chain 34 read again (the like-for-like baseline) and, beside it, against the registered table of 5 Oct; when the two
put the read in different branches the report says so. Promotion follows decision 57 (the registered recipe best on both hold-outs is
carried; an open line does not block): chain 35 is carried as version 1.3 when its seed mean is lower than chain 34's on every family and
the coupling ratio of both hold-outs (the precedent of 4 Oct); otherwise the per-quantity table goes to the user. Every line is read on the
number as reported (two decimals in cm⁻¹, three for the ratio). Writes <out>.md and .json.
"""
from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

FAMILIES = ("ring-ip", "CH-stretch", "CH-oop", "other")
HOLDOUTS = ("a", "b")
RATIO = "coupling_ratio"
QUANTITIES = (*FAMILIES, RATIO)
FROZEN_B = "holdout_b_frozen_2026-10-08.txt"

T1_FAMILY_LINE = 3.0                      # cm⁻¹, decision 53, for 'other', ring-ip and CH-oop
T1_RATIO_LINE = 0.25
OTHER_FALL_LINE = 0.3                     # cm⁻¹
# Chain 34 on analytic evaluation targets, hold-out (a), the registered table of 5 Oct 2026 06:5x (design note of 5 Oct, 'Chain 35 (the read)')
REGISTERED_BASELINE_A = {"ring-ip": 1.82, "CH-stretch": 1.25, "CH-oop": 2.36, "other": 3.35, RATIO: 0.192}
NEW_VERSION = "1.3"                       # 1.2 went to chain 36 (correction of 26 Oct 07:5x)


@dataclass(frozen=True)
class Arm:
    """Seed values per hold-out and quantity, and the molecules read on analytic targets."""
    values: dict[str, dict[str, tuple[float, ...]]]
    substituted: frozenset[str]

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
class Verdict:
    t1_met: bool
    branch: str
    branch_against_registered: str
    baselines_agree: bool
    other_fall: float
    other_fall_registered: float
    promoted: bool
    promotion: str
    worse_or_equal: tuple[str, ...]


def load_arm(paths: list[Path]) -> Arm:
    """One eval JSON per seed (at least two); every one read on the frozen hold-out (b) and on the same analytic targets."""
    if len(paths) < 2:
        raise ValueError(f"an arm needs at least two seeds for a standard error, got {len(paths)}")
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
    values = {h: {q: tuple(float(r[h][RATIO] if q == RATIO else r[h]["diag_rms"][q]) for r in recs) for q in QUANTITIES} for h in HOLDOUTS}
    return Arm(values=values, substituted=subs.pop())


def compare(new: Arm, carried: Arm) -> list[Comparison]:
    """Seed means of every quantity on both hold-outs; 'beyond two SE' when the difference exceeds twice the combined standard error."""
    out = []
    for h in HOLDOUTS:
        for q in QUANTITIES:
            d = new.mean(h, q) - carried.mean(h, q)
            se = math.sqrt(new.standard_error(h, q) ** 2 + carried.standard_error(h, q) ** 2)
            out.append(Comparison(h, q, new.mean(h, q), carried.mean(h, q), d, abs(d) > 2 * se))
    return out


def digits(quantity: str) -> int:
    """The reported precision: three decimals for the coupling ratio, two for a family's rms in cm⁻¹."""
    return 3 if quantity == RATIO else 2


def reported(value: float, quantity: str) -> float:
    """A number as the report prints it; the lines are read on it, so a float's last bits cannot move a read across a line."""
    return round(value, digits(quantity))


def branch_of(t1_met: bool, other_fall: float) -> str:
    if t1_met:
        return "T1 met"
    return "labels part of it" if other_fall >= OTHER_FALL_LINE else "labels not it"


def decide(new: Arm, carried: Arm, comparisons: list[Comparison]) -> Verdict:
    """The registered branches against both baselines, and decision 57's promotion, all on the reported numbers."""
    if new.substituted != carried.substituted:
        raise ValueError(f"the arms were read on different analytic targets ({len(new.substituted)} against {len(carried.substituted)} molecules)")
    a = {q: reported(new.mean("a", q), q) for q in QUANTITIES}
    t1 = all(a[f] <= T1_FAMILY_LINE for f in ("other", "ring-ip", "CH-oop")) and a[RATIO] <= T1_RATIO_LINE
    fall = reported(reported(carried.mean("a", "other"), "other") - a["other"], "other")
    fall_registered = reported(REGISTERED_BASELINE_A["other"] - a["other"], "other")
    branch, branch_registered = branch_of(t1, fall), branch_of(t1, fall_registered)
    worse = tuple(f"({c.hold}) {c.quantity}" for c in comparisons if reported(c.new, c.quantity) >= reported(c.carried, c.quantity))
    if worse:
        promotion = f"not lower everywhere ({', '.join(worse)}): the per-quantity table goes to the user (decision 57)"
    else:
        promotion = f"lower on every family and the coupling ratio of both hold-outs: carried as version {NEW_VERSION} (decision 57)"
    return Verdict(t1, branch, branch_registered, branch == branch_registered, fall, fall_registered, not worse, promotion, worse)


def _cell(values: tuple[float, ...], digits: int) -> str:
    return f"{sum(values) / len(values):.{digits}f} ({min(values):.{digits}f}–{max(values):.{digits}f})"


def report(new: Arm, carried: Arm, comparisons: list[Comparison], v: Verdict, sources: list[str]) -> str:
    lines = [f"# Chain 35 read — {datetime.now():%Y-%m-%d %H:%M}", "",
             "Registered: design note of 5 Oct 2026, registration 1 (lines), amendments of 8 Oct (half read) and 26 Oct (full read, version 1.3).",
             f"Both arms read on the same {len(new.substituted)} analytic targets and the frozen hold-out (b). Sources: {', '.join(sources)}.", "",
             "| hold-out | quantity | chain 35 | chain 34 read again | difference | beyond 2 SE |", "|---|---|---|---|---|---|"]
    for c in comparisons:
        d = digits(c.quantity)
        lines.append(f"| ({c.hold}) | {c.quantity} | {_cell(new.values[c.hold][c.quantity], d)} | "
                     f"{_cell(carried.values[c.hold][c.quantity], d)} | {c.difference:+.{d}f} | {'yes' if c.beyond_two_se else 'no'} |")
    reg = ", ".join(f"{q} {x}" for q, x in REGISTERED_BASELINE_A.items())
    lines += ["", f"- T1 line on (a) ('other', ring-ip, CH-oop ≤ {T1_FAMILY_LINE:g}; ratio ≤ {T1_RATIO_LINE:g}): **{'met' if v.t1_met else 'not met'}**.",
              f"- 'other' on (a) falls by {v.other_fall:+.2f} cm⁻¹ against chain 34 read again (line ≥ {OTHER_FALL_LINE:g}) → **{v.branch}**.",
              f"- Against the registered table of 5 Oct ({reg}): fall {v.other_fall_registered:+.2f} → {v.branch_against_registered}"
              + ("." if v.baselines_agree else " — **the two baselines put the read in different branches; the like-for-like one is the read, "
                                                "the difference is reported**."),
              f"- **Promotion: {v.promotion}.**",
              "- One pool size: the still-learning clause cannot be read from this chain (no curve)."]
    return "\n".join(lines) + "\n"


def write_atomic(target: Path, content: str) -> None:
    tmp = target.with_name(target.name + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(target)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--new", nargs="+", type=Path, required=True, help="chain 35's eval JSONs, one per seed")
    ap.add_argument("--carried", nargs="+", type=Path, required=True, help="chain 34's eval JSONs on the same targets, one per seed")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)
    new, carried = load_arm(args.new), load_arm(args.carried)
    comparisons = compare(new, carried)
    verdict = decide(new, carried, comparisons)
    sources = [p.name for p in [*args.new, *args.carried]]
    text = report(new, carried, comparisons, verdict, sources)
    record = {"verdict": asdict(verdict), "comparisons": [asdict(c) for c in comparisons],
              "registered_baseline_a": REGISTERED_BASELINE_A, "analytic_targets": len(new.substituted), "sources": sources}
    write_atomic(args.out.with_suffix(".md"), text)
    write_atomic(args.out.with_suffix(".json"), json.dumps(record, indent=1))
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
