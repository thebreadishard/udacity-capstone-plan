"""Benzene and the eight per molecule: the clean arm (v14_clean) against the data arm and the carried version, three seeds each.

Usage: clean_benzene.py <module 05 folder>. Read-only; corrected-frequency rms per molecule of hold-out (a8), per seed and mean.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

M05 = Path(sys.argv[1]).resolve()
OUT = M05 / "out" / "v14"
with (M05 / "corpus" / "manifest.csv").open(encoding="utf-8", newline="") as handle:
    name = {row["id"]: row["name"] for row in csv.DictReader(handle)}
arms = {who: [json.loads((OUT / f"eval_{who}_seed{s}.json").read_text(encoding="utf-8")) for s in (0, 1, 2)]
        for who in ("clean", "data", "carried_data")}
molecules = list(arms["clean"][0]["a8"]["per_molecule"])
print(f"{'a8 molecule':<18}" + "".join(f"{who:>30}" for who in arms))
for m in molecules:
    cells = []
    for recs in arms.values():
        vals = [r["a8"]["per_molecule"][m]["corrected_freq_rms"] for r in recs]
        cells.append(" ".join(f"{v:5.2f}" for v in vals) + f" | {sum(vals) / 3:5.2f}")
    print(f"{name[m]:<18}" + "".join(f"{c:>30}" for c in cells))
