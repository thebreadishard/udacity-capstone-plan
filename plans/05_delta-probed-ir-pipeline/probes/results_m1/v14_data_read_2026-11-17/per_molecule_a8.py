"""Hold-out (a8) per molecule for both arms of the v1.4-on-the-data read: where the two worse cells come from (read-only).

Usage: per_molecule_a8.py <module 05 folder>
Per molecule and seed: the trainer's corrected-frequency rms, and with this repository's own code the first-order diagonal error of
the CH-oop and CH-stretch modes (the read's quantity for the two cells the promotion is worse on).
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

m05 = Path(sys.argv[1])
out = m05 / "out" / "v14"
with (m05 / "corpus" / "manifest.csv").open(encoding="utf-8", newline="") as handle:
    name = {row["id"]: row["name"] for row in csv.DictReader(handle)}
arms = {"new": [out / f"eval_data_seed{s}.json" for s in range(3)], "carried": [out / f"eval_carried_data_seed{s}.json" for s in range(3)]}
records = {arm: [json.loads(p.read_text(encoding="utf-8")) for p in paths] for arm, paths in arms.items()}
ids = list(records["new"][0]["a8"]["per_molecule"])
print("per-molecule keys:", list(records["new"][0]["a8"]["per_molecule"][ids[0]]))
print(f"{'molecule':<16}{'name':<16}" + "".join(f"{arm + ' s' + str(s):>12}" for arm in arms for s in range(3)))
for key in ("corrected_freq_rms", "coupling_rms", "dH_residual_ratio"):
    print(f"--- {key}")
    for molecule in ids:
        cells = "".join(f"{records[arm][s]['a8']['per_molecule'][molecule][key]:>12.3f}" for arm in arms for s in range(3))
        print(f"{molecule:<16}{name[molecule]:<16}{cells}")
print("--- diag_rms per family, a8")
for family in ("ring-ip", "CH-stretch", "CH-oop", "other"):
    print(f"{family:<32}" + "".join(f"{records[arm][s]['a8']['diag_rms'][family]:>12.3f}" for arm in arms for s in range(3)))
