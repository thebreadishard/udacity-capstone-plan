"""Which selection molecules the eval does not reproduce: names, sizes, elements (read-only)."""
import csv
import json
import sys
from collections import Counter
from pathlib import Path

m05 = Path(sys.argv[1])
out = m05 / "out" / "v14"
with (m05 / "corpus" / "manifest.csv").open(encoding="utf-8", newline="") as handle:
    rows = {row["id"]: row for row in csv.DictReader(handle)}
ev = json.loads((out / "E7_rungC_v14s1a_c00_control_seleval_seed0.json").read_text(encoding="utf-8"))
tr = json.loads((out / "E7_rungC_v14s1a_c00_control.json").read_text(encoding="utf-8"))
trainer_sel = tr["curve"]["913"]["per_seed"][0]["sel"]["per_molecule"]
bad, good = [], []
for mol, read in ev["selall"]["per_molecule"].items():
    (bad if abs(read["corrected_freq_rms"] - trainer_sel[mol]["corrected_freq_rms"]) > 1e-3 else good).append(mol)
for mol in bad:
    row = rows[mol]
    blown = ev["selall"]["per_molecule"][mol]["corrected_freq_rms"]
    print(f"{mol:<16}{row['name']:<34}{row['n_atoms']:>4}  {row['smiles'][:50]}  eval {blown:.3g}")
print("bad cores:", dict(Counter(rows[m]["name"].split("+")[0] for m in bad)))
print("good cores:", dict(Counter(rows[m]["name"].split("+")[0] for m in good)))
print("bad n_atoms:", sorted(int(rows[m]["n_atoms"]) for m in bad), "| good max n_atoms:", max(int(rows[m]["n_atoms"]) for m in good))
print("train_ids_source:", ev.get("train_ids_source"), "n_train_ids:", ev.get("n_train_ids"),
      "| substituted_analytic:", len(ev.get("substituted_analytic", [])))
