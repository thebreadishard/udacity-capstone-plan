"""Benzene's error in every rung-C training record on disk, against what the training's pool was (read-only; TASKS 253).

Usage: benzene_across_records.py <module 05 folder>
One line per record and size: the pool's layers and size, whether hold-out twins were kept, the recipe's head, and benzene's
corrected-frequency rms on hold-out (a) per seed, with the median of the other hold-out (a) molecules beside it.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

m05 = Path(sys.argv[1])
BENZENE = "A_8448043181"
rows = []
for path in sorted((m05 / "out").glob("E7_rungC_*.json")) + sorted((m05 / "out" / "v14").glob("E7_rungC_*.json")):
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        continue
    if not isinstance(record, dict) or "curve" not in record:
        continue
    for size, entry in record["curve"].items():
        seeds = [s for s in entry.get("per_seed", []) if BENZENE in s.get("a", {}).get("per_molecule", {})]
        if not seeds:
            continue
        benzene = [s["a"]["per_molecule"][BENZENE]["corrected_freq_rms"] for s in seeds]
        others = [float(np.median([v["corrected_freq_rms"] for k, v in s["a"]["per_molecule"].items() if k != BENZENE])) for s in seeds]
        rows.append((record.get("date", "?"), path.stem.replace("E7_rungC_", "")[:44], size, record.get("pool_layers", "?"),
                     record.get("holdout_twins", "keep?"), "sel" if record.get("selection_split") else "-",
                     record.get("use_analytic", record.get("substituted_analytic") is not None), benzene, others))
rows.sort()
print(f"{'date':<17}{'record':<46}{'n':>6} {'layers':<15}{'twins':<7}{'sel':<4} benzene per seed | median of the others per seed")
for date, stem, size, layers, twins, sel, _, benzene, others in rows:
    print(f"{date:<17}{stem:<46}{size:>6} {layers:<15}{twins:<7}{sel:<4} " + " ".join(f"{v:5.2f}" for v in benzene)
          + "  | " + " ".join(f"{v:4.2f}" for v in others))
