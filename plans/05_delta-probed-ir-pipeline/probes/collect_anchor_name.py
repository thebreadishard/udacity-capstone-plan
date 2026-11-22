"""The registry name of a new anchor: the corpus manifest's name for its id (probes/collect_anchor.sh, stage 4).

    python probes/collect_anchor_name.py <molecule id>     → the name on stdout; exit 1 when the manifest has no such row or no name
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

MANIFEST = Path(__file__).resolve().parents[1] / "modules" / "05_support_predictor" / "corpus" / "manifest.csv"


def name_of(mol_id: str, manifest: Path = MANIFEST) -> str:
    """The manifest's name for the id; refused when the row or its name is missing."""
    with manifest.open(encoding="utf-8", newline="") as handle:
        names = [row["name"].strip() for row in csv.DictReader(handle) if row["id"] == mol_id]
    if len(names) != 1 or not names[0]:
        raise SystemExit(f"{mol_id}: {len(names)} manifest rows with a name in {manifest}")
    return names[0]


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    print(name_of(sys.argv[1]))
