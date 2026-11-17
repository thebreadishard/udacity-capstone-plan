"""Which cations of the layer P3c the whole-pool trainings trained on, and which of them share a skeleton with a hold-out (a) molecule.

Usage: cation_twins.py <module 05 folder>. Read-only. A cation's id is P3c_<hash>; a hold-out (a) molecule's is A_<hash>; the same hash
is the same neutral skeleton (the corpus names them so: P3c_8448043181 is 'benzene+').
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

m05 = Path(sys.argv[1])
with (m05 / "corpus" / "manifest.csv").open(encoding="utf-8", newline="") as handle:
    rows = {row["id"]: row for row in csv.DictReader(handle)}
record = json.loads((m05 / "out" / "v14" / "E7_rungC_v14s3full_c00_control.json").read_text(encoding="utf-8"))
pool = set(record["pool_ids"])
holdout_a = record["holdout_a"]
cations = sorted(i for i in pool if i.startswith("P3c_"))
print(f"cations in the whole pool: {len(cations)} of {len(pool)}; manifest P3c rows: {sum(1 for i in rows if i.startswith('P3c_'))}")
for parent in holdout_a:
    twin = "P3c_" + parent.split("_", 1)[1]
    where = "IN THE POOL" if twin in pool else ("in manifest, not trained" if twin in rows else "none")
    print(f"  {parent} {rows[parent]['name']:<18} cation twin {twin}: {where}")
core_count: dict[str, int] = {}
for i in cations:
    core = rows[i]["name"].split("+")[0]
    core_count[core] = core_count.get(core, 0) + 1
print("cations trained, by core:", dict(sorted(core_count.items(), key=lambda kv: -kv[1])))
print("the twin-drop of the trainer:", record.get("holdout_twins"), record.get("holdout_twins_dropped"))
