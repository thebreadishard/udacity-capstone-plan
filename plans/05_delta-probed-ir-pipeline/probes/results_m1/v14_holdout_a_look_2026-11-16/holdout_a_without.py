"""Hold-out (a) with and without one molecule, and hold-out (b), per seed of each record (read-only).

Usage: holdout_a_without.py <excluded id> <label=record.json>...
Per-molecule corrected-frequency RMS pooled over molecules with equal weight; the record's own pooled numbers beside it.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

excluded = sys.argv[1]
print(f"{'':<10}{'(a) record':>11}{'(a) by mol':>11}{'(a) without':>12}{'(b) record':>11}{'(b) coupling':>13}{'n pool':>8}")
for arg in sys.argv[2:]:
    label, path = arg.split("=", 1)
    record = json.loads(Path(path).read_text(encoding="utf-8"))
    for entry in record["curve"].values():
        for seed in entry["per_seed"]:
            per_molecule = seed["a"]["per_molecule"]
            sq = {i: read["corrected_freq_rms"] ** 2 for i, read in per_molecule.items()}
            rest = [v for i, v in sq.items() if i != excluded]
            print(f"{label + '/s' + str(seed['seed']):<10}{seed['a']['corrected_freq_rms']:>11.2f}{np.sqrt(np.mean(list(sq.values()))):>11.2f}"
                  f"{np.sqrt(np.mean(rest)):>12.2f}{seed['b']['corrected_freq_rms']:>11.2f}{seed['b']['coupling_rms']:>13.2f}"
                  f"{len(record['pool_ids']) if entry['n'] > len(record['pool_ids']) else entry['n']:>8}")
