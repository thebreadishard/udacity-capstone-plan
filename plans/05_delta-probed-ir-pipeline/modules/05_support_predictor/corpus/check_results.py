"""Mechanical check of the corpus results (23 September 2026, after E6 phase 1).

    python check_results.py [--layer A2]

Per layer: done/failed rows, every done row has result.json with two frequency lists of length 3N (six translations/rotations
included, projected to ~0), the worker's imaginary-mode count (frequencies < -10 cm^-1; such molecules are skipped by
m05/build_release.py), compute hours from the timings. Exit code 1 if a done row lacks a result or has the wrong list length.
A done row whose result.json says 'analytic_only' (merged by probes/large_pah_merge.py or probes/opt_batch_merge.py) has no such
lists and is counted only: its merge checked it with probes/large_pah_ready.state.
"""
import argparse
import csv
import json
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
# Noise principle: the two functionals' sorted frequency lists differ by tens of cm^-1, not hundreds; benzene's corpus wB97X
# finite-difference Hessian was wrong by up to 133 cm^-1 (the analytic second route restores the degeneracies).
SUSPECT_PAIR_CM = 80.0
RIGID_BELOW_CM = 50.0


@dataclass
class LayerRead:
    """What one layer's done rows show."""

    bad: int = 0
    analytic_only: int = 0
    hours: float = 0.0
    imaginary: list[str] = field(default_factory=list)
    suspect: list[str] = field(default_factory=list)


def read_row(row: dict, result: dict, read: LayerRead) -> None:
    """One done row's result.json with finite-difference lists, added to the layer's read."""
    n3 = 3 * int(row["n_atoms"])
    fb, fw = result["freq_b3lyp_cm"], result["freq_wb97x_cm"]
    if len(fb) != n3 or len(fw) != n3:
        print(f"WRONG LENGTH: {row['id']} {row['name']} {len(fb)}/{len(fw)} vs 3N={n3}")
        read.bad += 1
    if result.get("n_imaginary_b3lyp", 0) or result.get("n_imaginary_wb97x", 0):
        read.imaginary.append(f"  imaginary: {row['name']} n_imag B3LYP {result['n_imaginary_b3lyp']} wB97X {result['n_imaginary_wb97x']}, "
                              f"lowest {round(min(fb), 1)} / {round(min(fw), 1)} cm^-1")
    sorted_b, sorted_w = np.sort(np.array(fb)), np.sort(np.array(fw))
    keep = sorted_b > RIGID_BELOW_CM
    dif = sorted_w[-int(keep.sum()):] - sorted_b[keep]
    if np.abs(dif).max() > SUSPECT_PAIR_CM:
        read.suspect.append(f"  SUSPECT Hessian (max sorted-pair |dw| {round(float(np.abs(dif).max()), 1)} cm^-1, "
                            f"RMS {round(float(np.sqrt(np.mean(dif ** 2))), 1)}): {row['name']} ({row['id']}) "
                            "-> second route: corpus/analytic_hessians.py")
    read.hours += result["timings_s"]["total"] / 3600


def read_layer(done: list[dict]) -> LayerRead:
    """Every done row of a layer read; a missing result.json counts as bad, an analytic-only row is counted and not read further."""
    read = LayerRead()
    for row in done:
        path = HERE / "molecules" / row["id"] / "result.json"
        if not path.exists():
            print(f"MISSING result.json: {row['id']} {row['name']}")
            read.bad += 1
            continue
        result = json.loads(path.read_text(encoding="utf-8"))
        if result.get("labels") == "analytic_only":
            read.analytic_only += 1
            continue
        read_row(row, result, read)
    return read


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--layer", default=None)
    a = ap.parse_args()
    with open(HERE / "manifest.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    layers = [a.layer] if a.layer else sorted({r["layer"] for r in rows if r["status"] in ("done", "failed")})
    bad = 0
    for layer in layers:
        done = [r for r in rows if r["layer"] == layer and r["status"] == "done"]
        failed = [r for r in rows if r["layer"] == layer and r["status"] == "failed"]
        read = read_layer(done)
        bad += read.bad
        print(f"layer {layer}: done {len(done)}, failed {len(failed)}, with an imaginary mode {len(read.imaginary)} "
              f"(usable {len(done) - len(read.imaginary)}), compute {read.hours:.0f} h"
              + (f", analytic labels only {read.analytic_only} (not checked here)" if read.analytic_only else ""))
        for row in failed:
            print(f"  failed: {row['name']} ({row['id']}) {row['note'][:80]}")
        for line in read.imaginary + read.suspect:
            print(line)
    raise SystemExit(1 if bad else 0)


if __name__ == "__main__":
    main()
