"""How much of the selection set's frequency error two unsupported cores carry, per finished training (read-only).

Usage: sel_sensitivity.py <module 05 folder> <label=record.json>...
Per-molecule corrected-frequency RMS, pooled over molecules with equal weight (an approximation of the trainer's pooling over modes).
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np

M05 = Path(sys.argv[1])
with (M05 / "corpus" / "manifest.csv").open(encoding="utf-8", newline="") as handle:
    name = {row["id"]: row["name"] for row in csv.DictReader(handle)}
print(f"{'':<8}{'registered':>11}{'by molecule':>12}{'no biphenylene':>16}{'no biph, fluor':>16}{'per-core mean':>15}{'biph share':>12}")
for arg in sys.argv[2:]:
    label, path = arg.split("=", 1)
    record = json.loads(Path(path).read_text(encoding="utf-8"))
    seed = next(iter(record["curve"].values()))["per_seed"][0]
    per_molecule = seed["sel"]["per_molecule"]
    cores = np.array([name[i].split("+")[0] for i in per_molecule])
    sq = np.array([read["corrected_freq_rms"] ** 2 for read in per_molecule.values()])
    without_one = cores != "biphenylene"
    without_two = without_one & (cores != "fluoranthene")
    per_core = np.mean([np.sqrt(sq[cores == c].mean()) for c in sorted(set(cores))])
    print(f"{label:<8}{seed['sel']['corrected_freq_rms']:>11.2f}{np.sqrt(sq.mean()):>12.2f}{np.sqrt(sq[without_one].mean()):>16.2f}"
          f"{np.sqrt(sq[without_two].mean()):>16.2f}{per_core:>15.2f}{sq[~without_one].sum() / sq.sum():>12.0%}")
