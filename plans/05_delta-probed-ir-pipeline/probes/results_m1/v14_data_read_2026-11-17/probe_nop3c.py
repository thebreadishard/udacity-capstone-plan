"""TASKS 253's first test read: seed 0 of the whole-pool recipe without the layer P3c, beside seed 0 with it and the carried version.

Usage: probe_nop3c.py <module 05 folder>. Read-only. Per molecule of hold-out (a8) the corrected-frequency rms; benzene per family
(the evaluator's per-family diagonal error is per set, so benzene's families come from the licence read's own function, which loads
the three checkpoints and the molecule's two label Hessians); the ten promotion cells for the single seed.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np

M05 = Path(sys.argv[1]).resolve()
PLAN = M05.parents[1]
sys.path.insert(0, str(PLAN / "probes"))
import product_error_read as R  # noqa: E402  the probes folder is not a package

OUT = M05 / "out" / "v14"
FAMILIES = ("ring-ip", "CH-stretch", "CH-oop", "other")
BENZENE = "A_8448043181"
with (M05 / "corpus" / "manifest.csv").open(encoding="utf-8", newline="") as handle:
    name = {row["id"]: row["name"] for row in csv.DictReader(handle)}
arms = {"without P3c, seed 0": json.loads((OUT / "eval_nop3c_seed0.json").read_text(encoding="utf-8")),
        "with P3c, seed 0": json.loads((OUT / "eval_data_seed0.json").read_text(encoding="utf-8")),
        "carried, seed 0": json.loads((OUT / "eval_carried_data_seed0.json").read_text(encoding="utf-8"))}
print("=== hold-out (a8), corrected-frequency rms per molecule (cm-1)")
print(f"{'':<16}" + "".join(f"{a:>22}" for a in arms))
for molecule in arms["with P3c, seed 0"]["a8"]["per_molecule"]:
    print(f"{name[molecule]:<16}" + "".join(f"{r['a8']['per_molecule'][molecule]['corrected_freq_rms']:>22.2f}" for r in arms.values()))
print("\n=== the promotion's cells, single seed")
for hold in ("a8", "b"):
    for family in FAMILIES:
        print(f"({hold}) {family:<12}" + "".join(f"{r[hold]['diag_rms'][family]:>22.2f}" for r in arms.values()))
    print(f"({hold}) {'coupling':<12}" + "".join(f"{r[hold]['coupling_ratio']:>22.3f}" for r in arms.values()))


def rms(values: np.ndarray) -> float:
    return float(np.sqrt(np.mean(values**2)))


folder = M05 / "corpus" / "molecules" / BENZENE
models = {"without P3c, seed 0": OUT / "E7_rungC_v14s3nop3c_c00_control_model_n1032_seed0.pt",
          "with P3c, seed 0": OUT / "E7_rungC_v14s3full_c00_control_model_n1082_seed0.pt",
          "carried, seed 0": M05 / "out" / "E7_rungC_chain35_analytic_model_n750_seed0.pt"}
print("\n=== benzene, first-order error per family (cm-1)")
for label, model in models.items():
    read = R.molecule_read(folder, (model,))
    print(f"{label:<22}" + "".join(f"  {f} {rms(read.first_order[0][read.family == f]):.2f}" for f in FAMILIES))
