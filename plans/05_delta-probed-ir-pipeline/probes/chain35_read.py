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
put the read in different branches the report says so. Promotion follows decision 57 with the user's rule of 26 Oct (a new version may
worsen none of the five — the four families and the coupling ratio — on either hold-out): chain 35 is carried as version 1.3 when no seed
mean is above chain 34's and at least one is below; otherwise the per-quantity table goes to the user. Every line and comparison is read on
the number as reported (two decimals in cm⁻¹, three for the ratio). Writes <out>.md and .json.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from promotion_read import (  # noqa: E402, RUF100  (pre-commit's pinned ruff flags the import after the path insert; the newer one calls it unused)
    QUANTITIES,
    RATIO,
    Arm,
    Comparison,
    compare,
    comparison_table,
    load_eval_arm,
    promotion,
    reported,
    write_atomic,
)

T1_FAMILY_LINE = 3.0                      # cm⁻¹, decision 53, for 'other', ring-ip and CH-oop
T1_RATIO_LINE = 0.25
OTHER_FALL_LINE = 0.3                     # cm⁻¹
# Chain 34 on analytic evaluation targets, hold-out (a), the registered table of 5 Oct 2026 06:5x (design note of 5 Oct, 'Chain 35 (the read)')
REGISTERED_BASELINE_A = {"ring-ip": 1.82, "CH-stretch": 1.25, "CH-oop": 2.36, "other": 3.35, RATIO: 0.192}
NEW_VERSION = "1.3"                       # 1.2 went to chain 36 (correction of 26 Oct 07:5x)


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
    worse: tuple[str, ...]


def branch_of(t1_met: bool, other_fall: float) -> str:
    if t1_met:
        return "T1 met"
    return "labels part of it" if other_fall >= OTHER_FALL_LINE else "labels not it"


def decide(new: Arm, carried: Arm, comparisons: list[Comparison]) -> Verdict:
    """The registered branches against both baselines, and decision 57's promotion, all on the reported numbers."""
    a = {q: reported(new.mean("a", q), q) for q in QUANTITIES}
    t1 = all(a[f] <= T1_FAMILY_LINE for f in ("other", "ring-ip", "CH-oop")) and a[RATIO] <= T1_RATIO_LINE
    fall = reported(reported(carried.mean("a", "other"), "other") - a["other"], "other")
    fall_registered = reported(REGISTERED_BASELINE_A["other"] - a["other"], "other")
    branch, branch_registered = branch_of(t1, fall), branch_of(t1, fall_registered)
    p = promotion(comparisons)
    if p.worse:
        text = f"worse on {', '.join(p.worse)}: not promoted; the per-quantity table goes to the user (decision 57, the user's rule of 26 Oct)"
    elif not p.better:
        text = "equal everywhere: nothing to promote"
    else:
        text = (f"worse on none of the five on either hold-out, lower on {len(p.better)} of {len(comparisons)}: carried as version {NEW_VERSION} "
                "(decision 57, the user's rule of 26 Oct)")
    return Verdict(t1, branch, branch_registered, branch == branch_registered, fall, fall_registered, p.promoted, text, p.worse)


def report(new: Arm, carried: Arm, comparisons: list[Comparison], v: Verdict, sources: list[str]) -> str:
    lines = [f"# Chain 35 read — {datetime.now():%Y-%m-%d %H:%M}", "",
             "Registered: design note of 5 Oct 2026, registration 1 (lines), amendments of 8 Oct (half read) and 26 Oct (full read, version 1.3).",
             f"Both arms read on the same {len(new.substituted)} analytic targets and the frozen hold-out (b). Sources: {', '.join(sources)}.", "",
             *comparison_table(new, carried, comparisons, "chain 35", "chain 34 read again")]
    reg = ", ".join(f"{q} {x}" for q, x in REGISTERED_BASELINE_A.items())
    lines += ["", f"- T1 line on (a) ('other', ring-ip, CH-oop ≤ {T1_FAMILY_LINE:g}; ratio ≤ {T1_RATIO_LINE:g}): **{'met' if v.t1_met else 'not met'}**.",
              f"- 'other' on (a) falls by {v.other_fall:+.2f} cm⁻¹ against chain 34 read again (line ≥ {OTHER_FALL_LINE:g}) → **{v.branch}**.",
              f"- Against the registered table of 5 Oct ({reg}): fall {v.other_fall_registered:+.2f} → {v.branch_against_registered}"
              + ("." if v.baselines_agree else " — **the two baselines put the read in different branches; the like-for-like one is the read, "
                                                "the difference is reported**."),
              f"- **Promotion: {v.promotion}.**",
              "- One pool size: the still-learning clause cannot be read from this chain (no curve)."]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--new", nargs="+", type=Path, required=True, help="chain 35's eval JSONs, one per seed")
    ap.add_argument("--carried", nargs="+", type=Path, required=True, help="chain 34's eval JSONs on the same targets, one per seed")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)
    new, carried = load_eval_arm(args.new), load_eval_arm(args.carried)
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
