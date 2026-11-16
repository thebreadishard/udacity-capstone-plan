"""Where each hold-out (a) molecule's derivatives sit: v1.3's pool, the v1.4 search's pool, and its selection set (read-only).

Usage: relatives.py <module 05 folder>
A derivative is a manifest row whose name starts with the parent's name followed by '+' (the corpus naming: core+substituent).
"""
from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from pathlib import Path

M05 = Path(sys.argv[1])
with (M05 / "corpus" / "manifest.csv").open(encoding="utf-8", newline="") as handle:
    rows = list(csv.DictReader(handle))
print("manifest columns:", list(rows[0])[:12])
name = {row["id"]: row["name"] for row in rows}

v13 = json.loads((M05 / "out" / "E7_rungC_chain35_analytic.json").read_text(encoding="utf-8"))
v14 = json.loads((M05 / "out" / "v14" / "E7_rungC_v14s1a_c00_control.json").read_text(encoding="utf-8"))
sets = {"v1.3 pool": v13["pool_ids"], "v1.4 pool": v14["pool_ids"], "v1.4 sel": v14["holdout_sel"],
        "v1.4 twins dropped": v14["holdout_twins_dropped"]}


def core_of(molecule_id: str) -> str:
    return name.get(molecule_id, "?").split("+")[0]


print(f"{'hold-out (a)':<16}{'name':<22}" + "".join(f"{label:>20}" for label in sets))
for parent in v14["holdout_a"]:
    parent_name = name.get(parent, "?")
    counts = [sum(1 for i in ids if core_of(i) == parent_name and i != parent) for ids in sets.values()]
    print(f"{parent:<16}{parent_name:<22}" + "".join(f"{c:>20}" for c in counts))
print()
print("selection set by core:", dict(Counter(core_of(i) for i in v14["holdout_sel"]).most_common()))
print()
print("v1.4 pool by layer prefix:", dict(Counter(i.split("_")[0] for i in v14["pool_ids"])))
print("v1.3 pool by layer prefix:", dict(Counter(i.split("_")[0] for i in v13["pool_ids"])))
