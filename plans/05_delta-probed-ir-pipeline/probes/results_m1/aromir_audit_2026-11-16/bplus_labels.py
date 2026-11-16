"""The b+ set: which labels its 30 molecules have now, and what chain 35 and the v1.4 control read on it (read-only).

Usage: bplus_labels.py <module 05 folder>
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

m05 = Path(sys.argv[1])
with (m05 / "corpus" / "manifest.csv").open(encoding="utf-8", newline="") as handle:
    name = {row["id"]: row["name"] for row in csv.DictReader(handle)}
control = json.loads((m05 / "out" / "v14" / "E7_rungC_v14s1a_c00_control_seleval_seed0.json").read_text(encoding="utf-8"))
ids = list(control["b+"]["per_molecule"])
analytic = [i for i in ids if (m05 / "corpus" / "molecules" / i / "hessian_wb97x_analytic.npz").is_file()]
substituted = set(control.get("substituted_analytic", []))
print(f"b+ molecules: {len(ids)}; with hessian_wb97x_analytic.npz now: {len(analytic)}; read on analytic labels by the control's eval: "
      f"{len([i for i in ids if i in substituted])}")
print("cores:", sorted({name[i].split('+')[0] for i in ids}))
print(f"control (v1.4 c00, seed 0) on b+: diag_rms {control['b+']['diag_rms']}")
v13 = json.loads((m05 / "out" / "E7_rungC_chain35_analytic.json").read_text(encoding="utf-8"))
print("chain 35 record: hold-out keys per seed:", [k for k in v13["curve"]["750"]["per_seed"][0] if isinstance(v13["curve"]["750"]["per_seed"][0][k], dict)])
print("chain 35 substituted_analytic holds b+ ids:", len([i for i in ids if i in set(v13.get("substituted_analytic", []))]), "of", len(ids))
for seed in v13["curve"]["750"]["per_seed"]:
    for key in ("b", "b+"):
        if key in seed:
            print(f"  chain 35 seed {seed['seed']} {key}: diag_rms {seed[key]['diag_rms']} n {len(seed[key].get('per_molecule', {}))}")
