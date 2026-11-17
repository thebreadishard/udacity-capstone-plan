"""Hold-out (a8) per molecule and family for both arms of the v1.4-on-the-data read (read-only; inference on eight molecules).

Usage: per_family_a8.py <plan folder>
With `probes/product_error_read.molecule_read` (the licence read's own function): per molecule, family and seed the first-order
error — the promotion read's quantity — and per molecule and family the band error of the seed-mean ΔH; then each cell of the
promotion on (a8) with one molecule left out in turn.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

PLAN = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(PLAN / "probes"))
import product_error_read as R  # noqa: E402  the probes folder is not a package

M05 = PLAN / "modules" / "05_support_predictor"
FAMILIES = ("ring-ip", "CH-stretch", "CH-oop", "other")
ARMS = {"new": tuple(M05 / "out" / "v14" / f"E7_rungC_v14s3full_c00_control_model_n1082_seed{s}.pt" for s in range(3)),
        "carried": tuple(M05 / "out" / f"E7_rungC_chain35_analytic_model_n750_seed{s}.pt" for s in range(3))}
ids = [line.split()[0] for line in (M05 / "out" / "holdout_a_clean_2026-10-30.txt").read_text(encoding="utf-8").splitlines()
       if line.strip() and not line.startswith("#")]
with (M05 / "corpus" / "manifest.csv").open(encoding="utf-8", newline="") as handle:
    name = {row["id"]: row["name"] for row in csv.DictReader(handle)}


def rms(values: np.ndarray) -> float:
    return float(np.sqrt(np.mean(values**2))) if values.size else float("nan")


reads = {arm: {m: R.molecule_read(M05 / "corpus" / "molecules" / m, models) for m in ids} for arm, models in ARMS.items()}
for family in FAMILIES:
    print(f"\n=== {family}: first-order error per seed (new 0 1 2 | carried 0 1 2), then the band error of the seed mean (new | carried), modes")
    for m in ids:
        pick = reads["new"][m].family == family
        cells = "".join(f"{rms(reads[arm][m].first_order[s][reads[arm][m].family == family]):>8.2f}" for arm in ARMS for s in range(3))
        bands = "".join(f"{rms(reads[arm][m].band[reads[arm][m].band_family == family]):>8.2f}" for arm in ARMS)
        print(f"{name[m]:<16}{cells}   |{bands}   {int(pick.sum()):>4}")


def cell(arm: str, family: str, leave_out: str | None) -> float:
    """The promotion's cell: the mean over seeds of the rms over the set's modes of that family."""
    kept = [m for m in ids if m != leave_out]
    per_seed = [rms(np.concatenate([reads[arm][m].first_order[s][reads[arm][m].family == family] for m in kept])) for s in range(3)]
    return float(np.mean(per_seed))


print("\n=== the promotion's cells on (a8), new / carried, with one molecule left out in turn")
print(f"{'left out':<16}" + "".join(f"{f:>18}" for f in FAMILIES))
for leave_out in (None, *ids):
    row = "".join(f"{cell('new', f, leave_out):>9.2f} /{cell('carried', f, leave_out):>6.2f}" for f in FAMILIES)
    print(f"{name[leave_out] if leave_out else 'none':<16}{row}")
