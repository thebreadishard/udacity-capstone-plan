"""TASKS 263: the registered promotion rule (decision 57) against a proposed one, on every comparison we hold and on simulated arms.

Usage: rule_test.py <plan folder>. Read-only.

Old rule (promotion_read.promotion): no read-out worse at the reported precision, at least one better.
New rule (proposed 17 Nov, after the clean arm's read): the composite — every read-out over its line (v14_search.LINES), averaged over
both hold-outs' ten cells, per seed — is lower beyond two combined standard errors, and no read-out is worse beyond two standard errors.

Real cases: v1.3's promotion (chain 35 against chain 34), v1.4's data arm and clean arm against v1.3, and two null comparisons of one
recipe against itself (the data arm's seeds 0-2 against 3-4, and back). Simulated: per-seed values drawn independently per cell
(normal, the arm's own seed spread; correlation between cells ignored), three seeds per arm, 4,000 draws: a model equal to the carried
one (the null) and a model with the clean arm's means.
"""
from __future__ import annotations

import math
import random
import sys
from pathlib import Path

from scipy.stats import t as student_t

PLAN = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(PLAN / "probes"))
import promotion_read as P  # noqa: E402  the probes folder is not a package
from v14_search import LINES  # noqa: E402

OUT = PLAN / "modules" / "05_support_predictor" / "out"
V14 = OUT / "v14"
DRAWS = 4000


def composite(arm: P.Arm) -> list[float]:
    n = len(next(iter(arm.values.values()))[P.RATIO])
    return [sum(arm.values[h][q][i] / LINES[q] for h in arm.holdouts for q in P.QUANTITIES) / (len(arm.holdouts) * len(P.QUANTITIES))
            for i in range(n)]


def mean_se(v: list[float]) -> tuple[float, float]:
    m = sum(v) / len(v)
    return m, math.sqrt(sum((x - m) ** 2 for x in v) / (len(v) - 1)) / math.sqrt(len(v))


def rules(new: P.Arm, carried: P.Arm) -> tuple[bool, bool, str, bool]:
    comps = P.compare(new, carried)
    old = P.promotion(comps)
    (mn, sn), (mc, sc) = mean_se(composite(new)), mean_se(composite(carried))
    d, se = mn - mc, math.sqrt(sn**2 + sc**2)
    worse_beyond = [f"({c.hold}) {c.quantity}" for c in comps if c.new > c.carried and c.beyond_two_se]
    new_ok = d < 0 and abs(d) > 2 * se and not worse_beyond
    nn, nc = len(composite(new)), len(composite(carried))
    df = (sn**2 + sc**2) ** 2 / (sn**4 / (nn - 1) + sc**4 / (nc - 1))
    t_ok = d < 0 and abs(d) > student_t.ppf(0.975, df) * se and not worse_beyond
    note = (f"composite {mn:.3f} against {mc:.3f} (d {d:+.3f}, 2 SE {2 * se:.3f}); old rule worse on {', '.join(old.worse) or 'none'}; "
            f"worse beyond 2 SE: {', '.join(worse_beyond) or 'none'}")
    return old.promoted, new_ok, note + f"; t line {student_t.ppf(0.975, df) * se:.3f} (df {df:.1f})", t_ok


def arm(paths: list[Path], holdouts: tuple[str, ...]) -> P.Arm:
    return P.load_eval_arm(paths, holdouts=holdouts)


def seeds(prefix: str, ids: tuple[int, ...]) -> list[Path]:
    return [Path(f"{prefix}{s}.json") for s in ids]


CASES = {
    "v1.3 promoted (chain 35 vs chain 34), (a, b)": (
        seeds(str(OUT / "E7_rungC_chain35_analytic_eval_frozenb_seed"), (0, 1, 2)),
        seeds(str(OUT / "E7_rungC_chain34_eval_c35labels_seed"), (0, 1, 2)), ("a", "b")),
    "v1.4 data arm vs v1.3, (a8, b)": (seeds(str(V14 / "eval_data_seed"), (0, 1, 2)), seeds(str(V14 / "eval_carried_data_seed"), (0, 1, 2)),
                                        ("a8", "b")),
    "v1.4 clean arm vs v1.3, (a8, b)": (seeds(str(V14 / "eval_clean_seed"), (0, 1, 2)), seeds(str(V14 / "eval_carried_data_seed"), (0, 1, 2)),
                                         ("a8", "b")),
    "null: data seeds 0-2 vs 3-4, (a8, b)": (seeds(str(V14 / "eval_data_seed"), (0, 1, 2)), seeds(str(V14 / "eval_data_seed"), (3, 4)),
                                              ("a8", "b")),
    "null: data seeds 3-4 vs 0-2, (a8, b)": (seeds(str(V14 / "eval_data_seed"), (3, 4)), seeds(str(V14 / "eval_data_seed"), (0, 1, 2)),
                                              ("a8", "b")),
}


def drawn(template: P.Arm, spread: P.Arm, rng: random.Random, n: int = 3) -> P.Arm:
    values = {}
    for h in template.holdouts:
        values[h] = {}
        for q in P.QUANTITIES:
            sd = spread.standard_error(h, q) * math.sqrt(len(spread.values[h][q]))
            values[h][q] = tuple(rng.gauss(template.mean(h, q), sd) for _ in range(n))
    return P.Arm(values=values, substituted=template.substituted)


def simulate(true_new: P.Arm, carried: P.Arm, rng: random.Random) -> tuple[float, float, float]:
    old = new = tee = 0
    for _ in range(DRAWS):
        a, b, _, c = rules(drawn(true_new, true_new, rng), drawn(carried, carried, rng))
        old += a
        new += b
        tee += c
    return old / DRAWS, new / DRAWS, tee / DRAWS


print("=== real comparisons: old rule | composite at 2 SE | composite at Student t (chosen)")
for label, (new_paths, old_paths, holdouts) in CASES.items():
    o, n, note, t_ok = rules(arm(new_paths, holdouts), arm(old_paths, holdouts))
    print(f"{label:<48} old {'PROMOTE' if o else 'refuse':<8} 2SE {'PROMOTE' if n else 'refuse':<8} t {'PROMOTE' if t_ok else 'refuse':<8} {note}")

rng = random.Random(20261117)
carried = arm(CASES["v1.4 clean arm vs v1.3, (a8, b)"][1], ("a8", "b"))
clean = arm(CASES["v1.4 clean arm vs v1.3, (a8, b)"][0], ("a8", "b"))
v13_new, v13_old = (arm(p, ("a", "b")) for p in CASES["v1.3 promoted (chain 35 vs chain 34), (a, b)"][:2])
print(f"\n=== simulated, {DRAWS} draws each, three seeds per arm: P(promote) old rule | 2 SE | Student t")
for label, true_new, base in (("null: a model equal to v1.3", carried, carried),
                              ("a model as good as the clean arm", clean, carried),
                              ("null: a model equal to chain 34", v13_old, v13_old),
                              ("a model as good as chain 35 (v1.3)", v13_new, v13_old)):
    po, pn, pt = simulate(true_new, base, rng)
    print(f"{label:<40} old {po:6.1%}   2SE {pn:6.1%}   t {pt:6.1%}")
