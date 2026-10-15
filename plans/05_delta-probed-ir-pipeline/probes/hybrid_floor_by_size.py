"""Beside the registered read of the carried head's floor (TASKS 65, 15 Oct 2026; exploratory, no line): the pooled form floor and target bound
per size bin, the share of molecules whose form floor is numerically zero (the pattern has at least as many free entries as K has conditions,
so the fit is exact), and the per-molecule counts that decide that regime. Written after the read showed a line-2 forecast of 10¹⁰ cm⁻¹, to see
the trend the power law was fitted through.

    python probes/hybrid_floor_by_size.py probes/results_m1/hybrid_floor_2026-10-15/floor.json [--out <prefix>]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import floor_lines as FL  # noqa: E402

BINS = ((0, 14), (15, 19), (20, 23), (24, 27), (28, 99))
EXACT = 1e-6                     # cm⁻¹: a per-molecule form floor below this is the exact-fit regime, not a floor
KEYS = ("ring-ip", "other", "CH-stretch", "ring_coupling")


def by_size(records: list[dict]) -> list[dict]:
    rows = []
    for lo, hi in BINS:
        recs = [r for r in records if lo <= r["n_atoms"] <= hi]
        if not recs:
            continue
        exact = sum(1 for r in recs if (v := FL.per_molecule(r["form"], "ring-ip")) is None or v < EXACT)
        conditions = [r["n_modes"] * (r["n_modes"] + 1) // 2 for r in recs]
        rows.append({"atoms": f"{lo}-{hi}", "molecules": len(recs), "form_exact_fit": exact,
                     "median_conditions": sorted(conditions)[len(conditions) // 2],
                     "median_pattern_pairs": sorted(r["n_pattern_pairs"] for r in recs)[len(recs) // 2],
                     **{f"form {k}": FL.pooled([r["form"] for r in recs], k) for k in KEYS},
                     **{f"target {k}": FL.pooled([r["target"] for r in recs], k) for k in KEYS}})
    return rows


def table(rows: list[dict]) -> list[str]:
    cols = list(rows[0])
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for r in rows:
        lines.append("| " + " | ".join(f"{v:.3f}" if isinstance(v, float) else str(v) for v in r.values()) + " |")
    return lines


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("record", type=Path)
    ap.add_argument("--out", type=Path, default=None)
    a = ap.parse_args()
    rows = by_size(json.loads(a.record.read_text(encoding="utf-8"))["records"])
    lines = ["# Carried head's floor by size (beside the registered read; exploratory)", "", *table(rows)]
    if a.out:
        Path(f"{a.out}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        Path(f"{a.out}.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
