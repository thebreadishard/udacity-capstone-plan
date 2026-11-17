"""The whole-pool recipe on five seeds beside the three-seed read (design note §14's statement of 17 Nov 04:3x; read-only).

Usage: five_seeds.py <plan folder>
(i) per molecule of hold-out (a8) and per seed the corrected-frequency rms, the carried version beside it; (ii) benzene per family and
seed with the licence read's own function; (iii) the promotion's ten cells on three-seed and on five-seed means against the carried
version's three, at the read's reported precision. It decides nothing.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np

PLAN = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(PLAN / "probes"))
import product_error_read as R  # noqa: E402  the probes folder is not a package

M05 = PLAN / "modules" / "05_support_predictor"
OUT = M05 / "out" / "v14"
FAMILIES = ("ring-ip", "CH-stretch", "CH-oop", "other")
BENZENE = "A_8448043181"
with (M05 / "corpus" / "manifest.csv").open(encoding="utf-8", newline="") as handle:
    name = {row["id"]: row["name"] for row in csv.DictReader(handle)}
new = [json.loads((OUT / f"eval_data_seed{s}.json").read_text(encoding="utf-8")) for s in range(5)]
carried = [json.loads((OUT / f"eval_carried_data_seed{s}.json").read_text(encoding="utf-8")) for s in range(3)]

print("=== (i) hold-out (a8), corrected-frequency rms per molecule: new seeds 0-4 | carried seeds 0-2")
for molecule in new[0]["a8"]["per_molecule"]:
    cells = "".join(f"{r['a8']['per_molecule'][molecule]['corrected_freq_rms']:>7.2f}" for r in new)
    old = "".join(f"{r['a8']['per_molecule'][molecule]['corrected_freq_rms']:>7.2f}" for r in carried)
    print(f"{name[molecule]:<16}{cells}  |{old}")

stems = {s: OUT / f"E7_rungC_v14s3full_c00_control_model_n1082_seed{s}.pt" for s in range(3)}
stems |= {s: OUT / f"E7_rungC_v14s3more_c00_control_model_n1082_seed{s}.pt" for s in (3, 4)}
old_models = tuple(M05 / "out" / f"E7_rungC_chain35_analytic_model_n750_seed{s}.pt" for s in range(3))
folder = M05 / "corpus" / "molecules" / BENZENE


def rms(values: np.ndarray) -> float:
    return float(np.sqrt(np.mean(values**2)))


read_new = R.molecule_read(folder, tuple(stems[s] for s in range(5)))
read_old = R.molecule_read(folder, old_models)
print("\n=== (ii) benzene, first-order error per family: new seeds 0-4 | carried seeds 0-2")
for family in FAMILIES:
    cells = "".join(f"{rms(read_new.first_order[s][read_new.family == family]):>7.2f}" for s in range(5))
    old = "".join(f"{rms(read_old.first_order[s][read_old.family == family]):>7.2f}" for s in range(3))
    print(f"{family:<16}{cells}  |{old}")
print(f"{'seed-mean bands':<16}" + "".join(f"  {f} {rms(read_new.band[read_new.band_family == f]):.2f}" for f in FAMILIES)
      + "  (five seeds)  | carried" + "".join(f"  {f} {rms(read_old.band[read_old.band_family == f]):.2f}" for f in FAMILIES))


def cell(records: list[dict], hold: str, quantity: str) -> list[float]:
    return [r[hold]["coupling_ratio"] if quantity == "coupling_ratio" else r[hold]["diag_rms"][quantity] for r in records]


print("\n=== (iii) the promotion's cells: new on three seeds, new on five seeds, carried on three; 'worse' at the reported precision")
print(f"{'cell':<22}{'new 3':>9}{'new 5':>9}{'carried':>9}   3 seeds   5 seeds   each new seed")
for hold in ("a8", "b"):
    for quantity in (*FAMILIES, "coupling_ratio"):
        digits = 3 if quantity == "coupling_ratio" else 2
        values = cell(new, hold, quantity)
        three, five, old = round(float(np.mean(values[:3])), digits), round(float(np.mean(values)), digits), \
            round(float(np.mean(cell(carried, hold, quantity))), digits)
        per_seed = " ".join(f"{v:.{digits}f}" for v in values)
        print(f"({hold}) {quantity:<16}{three:>9.{digits}f}{five:>9.{digits}f}{old:>9.{digits}f}   "
              f"{'WORSE' if three > old else 'ok':<9} {'WORSE' if five > old else 'ok':<9} {per_seed}")
