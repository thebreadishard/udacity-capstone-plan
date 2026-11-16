"""Read the scan's table: the distribution of the gap and the molecules at its edges (TASKS 236; read-only).

    python scan_table.py <b_gap_scan.tsv> <corpus manifest.csv> [<ids to mark, one per line>]
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

EDGE = 8


def main() -> None:
    with Path(sys.argv[1]).open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    with Path(sys.argv[2]).open(encoding="utf-8", newline="") as handle:
        names = {row["id"]: row["name"] for row in csv.DictReader(handle)}
    marked = set(Path(sys.argv[3]).read_text(encoding="utf-8").split()) if len(sys.argv) > 3 else set()
    null = np.array([float(r["null_over_max"]) for r in rows])
    real = np.array([float(r["real_over_max"]) for r in rows])
    print(f"{len(rows)} molecules; atoms {min(int(r['n_atoms']) for r in rows)}..{max(int(r['n_atoms']) for r in rows)}")
    print(f"real/max: min {real.min():.3e}, median {np.median(real):.3e}")
    print(f"null/max: median {np.median(null):.3e}, 99th percentile {np.percentile(null, 99):.3e}, max {null.max():.3e}")
    for low, high in ((0, 1e-15), (1e-15, 1e-14), (1e-14, 1e-12), (1e-12, 1e-10), (1e-10, 1e-6), (1e-6, 1.0)):
        print(f"  null/max in [{low:g}, {high:g}): {int(((null >= low) & (null < high)).sum())}")
    wrong = [r for r in rows if r["kept_by_default"] != r["rank"]]
    wrong_values = [r for r in rows if r["kept_by_default_values_only"] != r["rank"]]
    print(f"default cutoff keeps a wrong count: {len(wrong)} by the SVD with vectors, {len(wrong_values)} by values only")
    if marked:
        hit = {r["id"] for r in wrong} & marked
        present = {r["id"] for r in rows} & marked
        print(f"of the {len(marked)} marked ids, {len(present)} are in the scan and {len(hit)} are among those {len(wrong)}")
    print("largest null/max:")
    for r in sorted(rows, key=lambda r: -float(r["null_over_max"]))[:EDGE]:
        print(f"  {r['id']:<16}{names.get(r['id'], '?')[:38]:<40}{r['n_atoms']:>4} atoms  real {float(r['s_last_real']):.3e}  "
              f"null {float(r['s_first_null']):.3e}  null/max {float(r['null_over_max']):.3e}  kept {r['kept_by_default']} of {r['rank']}")
    print("smallest real/max:")
    for r in sorted(rows, key=lambda r: float(r["real_over_max"]))[:EDGE]:
        print(f"  {r['id']:<16}{names.get(r['id'], '?')[:38]:<40}{r['n_atoms']:>4} atoms  real {float(r['s_last_real']):.3e}  "
              f"real/max {float(r['real_over_max']):.3e}")


if __name__ == "__main__":
    main()
