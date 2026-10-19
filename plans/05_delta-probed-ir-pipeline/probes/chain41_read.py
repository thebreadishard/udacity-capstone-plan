"""Chain 41's registered read (rung C pre-registration, chain 41, registered 11 Oct 2026, before any pool 3 neutral was fetched or read).

The size arm reads all thirty s5 molecules; each control fold reads its own fifteen. Seed means of the ring-coupling ratio r:
- r_S: the size arm on s5.
- r_K: the control on s5, both folds pooled.

**Pooling, fixed 13 Oct 2026 before any number:** the records carry each set's ratio, not its count of coupling entries. r_K is therefore the
mean of the two folds' ratios. Each fold tests fifteen five-ring neutrals of 32–40 atoms, so the entry counts are close.

Lines on q5 = r_S / r_K, as registered:
- ≤ 1.3: carries;
- ≥ 1.8: steep;
- between: noted, and the five-ring families enter the corpus before the next pool is designed.

Reported beside, without lines:
- corrected ω on s5 against the zero rule, both arms;
- the size arm on s4N;
- r_S per scaffold, as the mean of per-molecule ratios (scaffold = the candidate list's parent).

Writes out/read_chain41.{json,md} under module 05; exit 0 (a read, not a gate).

    python probes/chain41_read.py --size <3 eval json> --fold1 <3> --fold2 <3>
"""
import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np

M05 = Path(__file__).resolve().parents[1] / "modules" / "05_support_predictor"
OUT = M05 / "out" / "read_chain41"
CANDIDATES = M05 / "out" / "pool3_candidates_2026-10-03.csv"


def mean_of(records: list, hold: str, key: str = "coupling_ratio") -> float:
    return float(np.mean([r[hold][key] for r in records]))


# The amendment of 19 Oct 2026 (rung C pre-registration, chain 41): these two leave the read by the loader's imaginary-mode rule (B3LYP
# finite-difference labels; their ωB97X Hessians have none); TASKS 74's analytic re-read brings them back
AMENDED_OUT = {"P3_086e85b2d7": "imaginary mode −53.7 cm⁻¹ in the B3LYP FD label", "P3_2aa4adcc95": "imaginary mode −28.4 cm⁻¹ in the B3LYP FD label",
               "P3_2a090cd77b": "imaginary mode −39.8 cm⁻¹ in the ωB97X FD label (s4N; methyl torsion)"}


def require_complete(records: list, hold: str) -> None:
    """A registered test set is read whole or not at all (13 Oct 2026: the loader had silently skipped every molecule above 32 atoms); only
    the molecules the 19 Oct amendment names may be missing."""
    for r in records:
        dropped = [i for i in (r[hold].get("dropped") or []) if i not in AMENDED_OUT]
        if dropped:
            raise SystemExit(f"hold-out ({hold}) lost {len(dropped)} registered molecules at evaluation ({', '.join(dropped[:5])}) — not read")


def verdict(q5: float, curve: dict | None = None) -> str:
    if q5 <= 1.3:
        return "carries (≤ 1.3)"
    if q5 < 1.8:
        return "between: noted; the five-ring families enter the corpus first"
    if curve is None:
        return "steep (≥ 1.8) — no control curve read"
    return ("steep (≥ 1.8) and the control still learning: data-limited — the five-ring and larger families enter the corpus; chain 42's arm D next"
            if curve["still_learning"] else "steep (≥ 1.8) with a flat control curve: the search (recipe, loss, ring-coupling input) before any statement")


def scaffold_of(ids) -> dict:
    """id → its scaffold: the parent's name for a derivative with a parent_id, else the name before '+' (14 Oct 2026: the five-ring
    neutrals carry no parent_id, so every derivative had counted as its own scaffold)."""
    rows = {r["id"]: r for r in csv.DictReader(open(CANDIDATES, encoding="utf-8"))}
    return {i: rows[rows[i]["parent_id"]]["name"] if rows[i]["parent_id"] in rows else rows[i]["name"].split("+")[0] for i in ids if i in rows}


def seed_r_k(fold1: list, fold2: list) -> np.ndarray:
    """r_K per seed: the mean of the two folds' ratios of that seed (records in seed order)."""
    return np.array([0.5 * (a["s5"]["coupling_ratio"] + b["s5"]["coupling_ratio"]) for a, b in zip(fold1, fold2, strict=True)])


def still_learning(full: np.ndarray, half: np.ndarray) -> dict:
    """The learning-curve clause (14 Oct 2026): r_K(full) below r_K(half) by more than twice the combined standard error of the seed means."""
    se = float(np.sqrt(full.var(ddof=1) / len(full) + half.var(ddof=1) / len(half)))
    drop = float(half.mean() - full.mean())
    return {"r_K_half": float(half.mean()), "r_K_full": float(full.mean()), "drop": drop, "two_se": 2 * se, "still_learning": drop > 2 * se}


def read(size: list, fold1: list, fold2: list, scaffolds: dict | None = None, half1: list | None = None, half2: list | None = None) -> dict:
    for recs, holds in ((size, ("s5", "s4N")), (fold1, ("s5",)), (fold2, ("s5",)), (half1 or [], ("s5",)), (half2 or [], ("s5",))):
        for h in holds:
            require_complete(recs, h)
    r_s = mean_of(size, "s5")
    r_k = float(np.mean([mean_of(fold1, "s5"), mean_of(fold2, "s5")]))
    curve = still_learning(seed_r_k(fold1, fold2), seed_r_k(half1, half2)) if half1 and half2 else None
    res = {"r_S": r_s, "r_K": r_k, "q5": r_s / r_k, "verdict": verdict(r_s / r_k, curve), "control_curve": curve,
           "beside": {"size_arm_s4N": mean_of(size, "s4N"),
                      "omega_rms_s5": {"size": mean_of(size, "s5", "corrected_freq_rms"),
                                       "control": float(np.mean([mean_of(fold1, "s5", "corrected_freq_rms"), mean_of(fold2, "s5", "corrected_freq_rms")])),
                                       "zero_rule": mean_of(size, "s5", "corrected_freq_rms_zero_rule")}}}
    if scaffolds:
        per = {}
        for i, sc in scaffolds.items():
            vals = [r["s5"]["per_molecule"][i]["coupling_ratio"] for r in size if i in r["s5"]["per_molecule"]]
            vals = [v for v in vals if v is not None]
            if vals:
                per.setdefault(sc, []).append(float(np.mean(vals)))
        res["beside"]["r_S_per_scaffold"] = {sc: float(np.mean(v)) for sc, v in sorted(per.items())}
    return res


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--size", nargs="+", required=True)
    ap.add_argument("--fold1", nargs="+", required=True)
    ap.add_argument("--fold2", nargs="+", required=True)
    ap.add_argument("--fold1-half", nargs="+", default=None, help="the half-control arm of fold 1 (14 Oct 2026, learning-curve amendment)")
    ap.add_argument("--fold2-half", nargs="+", default=None)
    a = ap.parse_args()
    load = lambda paths: [json.loads(Path(p).read_text(encoding="utf-8")) for p in paths]  # noqa: E731
    size = load(a.size)
    res = read(size, load(a.fold1), load(a.fold2), scaffold_of(size[0]["s5"]["per_molecule"]),
               load(a.fold1_half) if a.fold1_half else None, load(a.fold2_half) if a.fold2_half else None)
    res["files"] = {"size": a.size, "fold1": a.fold1, "fold2": a.fold2, "fold1_half": a.fold1_half, "fold2_half": a.fold2_half}
    lines = ["# Chain 41 — five fused rings from a corpus of at most four (registered read)", "",
             f"q5 = r_S / r_K = {res['r_S']:.3f} / {res['r_K']:.3f} = **{res['q5']:.2f}** → {res['verdict']}", "",
             f"Beside: size arm on s4N {res['beside']['size_arm_s4N']:.3f}; corrected ω on s5 — size {res['beside']['omega_rms_s5']['size']:.2f}, "
             f"control {res['beside']['omega_rms_s5']['control']:.2f}, zero rule {res['beside']['omega_rms_s5']['zero_rule']:.2f} cm⁻¹."]
    if res["control_curve"]:
        c = res["control_curve"]
        lines.append(f"Control curve: r_K half {c['r_K_half']:.3f} → full {c['r_K_full']:.3f} (drop {c['drop']:.3f} against 2 SE {c['two_se']:.3f}): "
                     f"{'still learning' if c['still_learning'] else 'flat'}.")
    for sc, v in res["beside"].get("r_S_per_scaffold", {}).items():
        lines.append(f"- r_S {sc}: {v:.3f}")
    Path(f"{OUT}.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    Path(f"{OUT}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
