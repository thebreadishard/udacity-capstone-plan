"""A chain runner's wait condition (15 Oct 2026, TASKS 61): exit 0 when no manifest row of the given layers is still to be computed — every row
is done, failed or moved, i.e. the batch has been fetched and merged. Else exit 1 with one status line (counts per layer and status).

    python probes/manifest_settled.py P3 R4 [--manifest modules/05_support_predictor/corpus/manifest.csv]

A layer with no row at all is not settled: a typo must not pass as an empty, finished batch.
"""
from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from pathlib import Path

MANIFEST = Path(__file__).resolve().parents[1] / "modules" / "05_support_predictor" / "corpus" / "manifest.csv"
SETTLED = {"done", "failed", "moved"}


def unsettled(layers: list[str], manifest: Path = MANIFEST) -> dict[str, Counter]:
    """{layer: Counter of statuses} for every layer that is empty or has a row still to compute."""
    counts = {layer: Counter() for layer in layers}
    for row in csv.DictReader(open(manifest, encoding="utf-8", newline="")):
        if row["layer"] in counts:
            counts[row["layer"]][row["status"]] += 1
    return {layer: c for layer, c in counts.items() if not c or set(c) - SETTLED}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("layers", nargs="+")
    ap.add_argument("--manifest", type=Path, default=MANIFEST)
    a = ap.parse_args()
    open_layers = unsettled(a.layers, a.manifest)
    if open_layers:
        print("not settled: " + "; ".join(f"{layer} {dict(c) or 'no rows'}" for layer, c in open_layers.items()))
        return 1
    print(f"settled: {', '.join(a.layers)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
