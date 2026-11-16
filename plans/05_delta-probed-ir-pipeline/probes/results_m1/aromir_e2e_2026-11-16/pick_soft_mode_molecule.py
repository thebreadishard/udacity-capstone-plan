"""The smallest corpus molecules whose B3LYP label has a mode below 20 cm-1, for an end-to-end aromir run (TASKS 245).

    python pick_soft_mode_molecule.py <plan folder>

Reads `probes/results_m1/soft_mode_by_label_2026-11-16/soft_mode_by_label.txt` (one line per molecule with the three lowest modes
of each label before and after the repair) and the corpus manifest; prints the candidates by size, with the SMILES aromir takes.
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

SOFT_BELOW_CM = 20.0
SHOWN = 12


def main() -> None:
    plan = Path(sys.argv[1]).resolve()
    listing = plan / "probes" / "results_m1" / "soft_mode_by_label_2026-11-16" / "soft_mode_by_label.txt"
    with (plan / "modules" / "05_support_predictor" / "corpus" / "manifest.csv").open(encoding="utf-8", newline="") as handle:
        manifest = {row["id"]: row for row in csv.DictReader(handle)}
    pattern = re.compile(r"^(\S+)\s+(b3lyp only|both)\s+before b3lyp \[([^\]]+)\].*?\| now b3lyp \[([^\]]+)\]")
    found = {}
    for line in listing.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if match is None or match.group(1) not in manifest:
            continue
        before = [float(x) for x in match.group(3).split(",")]
        now = [float(x) for x in match.group(4).split(",")]
        if abs(before[0]) < SOFT_BELOW_CM:
            found[match.group(1)] = (before, now)
    ranked = sorted(found, key=lambda molecule_id: (int(manifest[molecule_id]["n_atoms"]), molecule_id))
    print(f"{len(found)} molecules with an analytic B3LYP lowest mode below {SOFT_BELOW_CM:g} cm-1 in absolute value")
    for molecule_id in ranked[:SHOWN]:
        row = manifest[molecule_id]
        before, now = found[molecule_id]
        print(f"{molecule_id:<16}{row['n_atoms']:>3} atoms  {row['name'][:30]:<32}{row['smiles']:<34} analytic {before} measured {now}")


if __name__ == "__main__":
    main()
