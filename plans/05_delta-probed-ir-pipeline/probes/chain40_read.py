"""Chain 40's registered read: does adding five-ring children cover hold-out (b)? (rung C pre-registration, amendments of 10 Oct 13:0x
and 14 Oct 10:5x; the read is a script, not a model pass).

    python probes/chain40_read.py --full out/E7_rungC_chain40_fivering30_eval_frozenb_seed{0,1,2}.json
                                  --half out/E7_rungC_chain40_fivering15_eval_frozenb_seed{0,1,2}.json --out out/E7_rungC_chain40_read

The registered number is the seed mean of hold-out (b)'s coupling ratio from `rungC_eval_saved.py --holdout-b-file
corpus/holdout_b_frozen_2026-10-08.txt`. Lines on Δ = (b) full arm − (b) chain 37 (0.325):
- Δ ≤ −0.03: adding the families covers (b); the runner continues to ~60 per family and (b) is read again there;
- Δ > −0.015: STOP (≈ 30 per family kept), but only when the curve is not still learning; when it is, the runner continues to ~60 per family;
- otherwise 'between': the runner continues, no lever claimed.
'Still learning' (14 Oct): the full arm's (b) is below the half arm's by more than twice the combined standard error of the two seed means
(standard error = sample standard deviation over seeds / √n) and below chain 37's. Reported beside: (b+), (a) and the four families.
Writes <out>.md and <out>.json.
"""
import argparse
import json
import math
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

CHAIN37_B = 0.325
COVERS_AT = -0.03
STOP_ABOVE = -0.015
FAMILIES = ("ring-ip", "CH-stretch", "CH-oop", "other")


@dataclass(frozen=True)
class Arm:
    """Seed values of one arm's hold-out numbers."""
    b_ratio: tuple[float, ...]
    b_plus_ratio: tuple[float, ...]
    a_ratio: tuple[float, ...]
    b_families: dict[str, tuple[float, ...]]

    @property
    def mean(self) -> float:
        return sum(self.b_ratio) / len(self.b_ratio)

    @property
    def standard_error(self) -> float:
        n = len(self.b_ratio)
        if n < 2:
            raise ValueError("a standard error needs at least two seeds")
        m = self.mean
        return math.sqrt(sum((x - m) ** 2 for x in self.b_ratio) / (n - 1)) / math.sqrt(n)


@dataclass(frozen=True)
class Verdict:
    full_mean: float
    half_mean: float
    delta: float
    gap: float
    gap_needed: float
    still_learning: bool
    branch: str
    action: str


def load_arm(paths: list[Path]) -> Arm:
    """One eval JSON per seed; all must be frozen-(b) evals."""
    recs = []
    for p in paths:
        with open(p, encoding="utf-8") as f:
            rec = json.load(f)
        if not str(rec.get("holdout_b_file", "")).endswith("holdout_b_frozen_2026-10-08.txt"):
            raise ValueError(f"{p} is not read on the frozen hold-out (b) of 8 Oct")
        recs.append(rec)
    families = {fam: tuple(r["b"]["diag_rms"][fam] for r in recs) for fam in FAMILIES}
    return Arm(b_ratio=tuple(r["b"]["coupling_ratio"] for r in recs), b_plus_ratio=tuple(r["b+"]["coupling_ratio"] for r in recs),
               a_ratio=tuple(r["a"]["coupling_ratio"] for r in recs), b_families=families)


def decide(full: Arm, half: Arm, chain37: float = CHAIN37_B) -> Verdict:
    """The registered branches, with the 14 Oct still-learning clause."""
    delta = full.mean - chain37
    gap = half.mean - full.mean
    gap_needed = 2 * math.sqrt(full.standard_error ** 2 + half.standard_error ** 2)
    still_learning = gap > gap_needed and full.mean < chain37
    if delta <= COVERS_AT:
        branch, action = "covers", "the runner continues to ~60 per family; (b) is read again there"
    elif delta > STOP_ABOVE and not still_learning:
        branch, action = "stop", "STOP file after the read (~30 per family kept); the generator route for (b)-like scaffolds goes to the user"
    elif delta > STOP_ABOVE:
        branch, action = "still learning", "the STOP branch does not apply: the runner continues to ~60 per family; (b) is read again there"
    else:
        branch, action = "between", "the runner continues; noted, no lever claimed"
    return Verdict(full.mean, half.mean, delta, gap, gap_needed, still_learning, branch, action)


def _cell(values: tuple[float, ...], digits: int = 3) -> str:
    m = sum(values) / len(values)
    return f"{m:.{digits}f} ({min(values):.{digits}f}–{max(values):.{digits}f})"


def report(full: Arm, half: Arm, v: Verdict, sources: list[str]) -> str:
    lines = [f"# Chain 40 read — {datetime.now():%Y-%m-%d %H:%M}", "",
             "Registered: rung C pre-registration, amendments of 10 Oct 13:0x (lines) and 14 Oct 10:5x (half arm, still-learning rule).",
             f"Sources: {', '.join(sources)}.", "",
             "| hold-out | full arm (~30 per family) | half arm (~22 per family) | chain 37 |", "|---|---|---|---|",
             f"| (b) coupling ratio — the registered number | {_cell(full.b_ratio)} | {_cell(half.b_ratio)} | {CHAIN37_B:.3f} |",
             f"| (b+) coupling ratio | {_cell(full.b_plus_ratio)} | {_cell(half.b_plus_ratio)} | — |",
             f"| (a) coupling ratio | {_cell(full.a_ratio)} | {_cell(half.a_ratio)} | — |"]
    lines += [f"| (b) {fam} diagonal rms (cm⁻¹) | {_cell(full.b_families[fam], 2)} | {_cell(half.b_families[fam], 2)} | — |" for fam in FAMILIES]
    lines += ["", f"- Δ = (b) full − chain 37 = {v.delta:+.4f} (lines: ≤ {COVERS_AT} covers, > {STOP_ABOVE} stop unless still learning).",
              f"- Still learning: half − full = {v.gap:.4f} against 2 × combined standard error {v.gap_needed:.4f}, full below chain 37: "
              f"{v.full_mean < CHAIN37_B} → **{'yes' if v.still_learning else 'no'}**.",
              f"- **Branch: {v.branch}** — {v.action}.",
              "- Per-scaffold (b) numbers (fluorene, fluoranthene children) are not in the eval records; they need a per-molecule eval."]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--full", nargs="+", type=Path, required=True)
    ap.add_argument("--half", nargs="+", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)
    full, half = load_arm(args.full), load_arm(args.half)
    verdict = decide(full, half)
    sources = [p.name for p in [*args.full, *args.half]]
    text = report(full, half, verdict, sources)
    for suffix, content in ((".md", text), (".json", json.dumps({"verdict": asdict(verdict), "full": asdict(full), "half": asdict(half),
                                                                    "chain37_b": CHAIN37_B, "sources": sources}, indent=1))):
        target = args.out.with_suffix(suffix)
        tmp = target.with_name(target.name + ".tmp")
        tmp.write_text(content, encoding="utf-8")
        tmp.replace(target)
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
