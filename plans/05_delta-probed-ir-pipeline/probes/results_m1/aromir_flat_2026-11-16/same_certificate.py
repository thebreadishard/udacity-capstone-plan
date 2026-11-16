"""Did a change of aromir move a molecule's certificate? Two certificate.json files, band by band (TASKS 248).

    python same_certificate.py <certificate.json before> <certificate.json after>

Prints the largest difference of every number a band carries, the count of licensed bands in each, and the optimisation's
record of each, so that 'nothing moved' is a number and not a reading of two tables.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

NUMBERS = ("wavenumber_cm", "intensity_km_mol", "b3lyp_cm", "scaled_b3lyp_cm")


def main() -> None:
    before, after = (json.loads(Path(name).read_text(encoding="utf-8")) for name in sys.argv[1:3])
    if len(before["bands"]) != len(after["bands"]):
        raise SystemExit(f"{len(before['bands'])} bands before, {len(after['bands'])} after")
    print(f"{after['molecule']['smiles']}: {len(after['bands'])} bands")
    for name in NUMBERS:
        largest = max(abs(a[name] - b[name]) for a, b in zip(after["bands"], before["bands"], strict=True))
        print(f"  largest difference in {name}: {largest:.2f}")
    ranges = max(abs(x - y) for a, b in zip(after["bands"], before["bands"], strict=True)
                 for x, y in zip(a["seed_range_cm"], b["seed_range_cm"], strict=True))
    print(f"  largest difference in the seeds' range: {ranges:.2f}")
    for label, record in (("before", before), ("after", after)):
        licensed = sum(band["licensed"] for band in record["bands"])
        families = sum(a["family"] == b["family"] for a, b in zip(after["bands"], before["bands"], strict=True))
        print(f"  {label}: {licensed} licensed; optimisation {record['computation']['optimisation']}")
    print(f"  bands with the same family: {families} of {len(after['bands'])}")


if __name__ == "__main__":
    main()
