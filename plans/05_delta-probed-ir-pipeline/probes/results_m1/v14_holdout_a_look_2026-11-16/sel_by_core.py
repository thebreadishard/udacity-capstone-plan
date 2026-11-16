"""The control's error on the selection set, per scaffold core (read-only). Usage: sel_by_core.py <module 05 folder>"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np

M05 = Path(sys.argv[1])
with (M05 / "corpus" / "manifest.csv").open(encoding="utf-8", newline="") as handle:
    name = {row["id"]: row["name"] for row in csv.DictReader(handle)}
record = json.loads((M05 / "out" / "v14" / "E7_rungC_v14s1a_c00_control.json").read_text(encoding="utf-8"))
per_molecule = record["curve"]["913"]["per_seed"][0]["sel"]["per_molecule"]
by_core: dict[str, list[float]] = {}
for molecule_id, read in per_molecule.items():
    by_core.setdefault(name[molecule_id].split("+")[0], []).append(read["corrected_freq_rms"])
print(f"{'core':<22}{'n':>4}{'median':>9}{'rms':>9}{'max':>9}")
for core, values in sorted(by_core.items(), key=lambda kv: -float(np.median(kv[1]))):
    v = np.array(values)
    print(f"{core:<22}{len(v):>4}{np.median(v):>9.2f}{np.sqrt(np.mean(v**2)):>9.2f}{v.max():>9.2f}")
