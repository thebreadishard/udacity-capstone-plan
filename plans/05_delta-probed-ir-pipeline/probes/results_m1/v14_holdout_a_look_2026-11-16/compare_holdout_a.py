"""Hold-out (a) per family and per molecule: the carried chain 35 against the v1.4 search's finished trainings (read-only).

Usage: compare_holdout_a.py <label=record.json>...   (every seed of every record becomes a column)
"""
import json
import sys

FAMILIES = ("CH-stretch", "CH-oop", "ring-ip", "other")
columns: list[tuple[str, dict]] = []
for arg in sys.argv[1:]:
    label, path = arg.split("=", 1)
    with open(path, encoding="utf-8") as handle:
        record = json.load(handle)
    for entry in record["curve"].values():
        for seed in entry["per_seed"]:
            columns.append((f"{label}/s{seed['seed']}", seed["a"]))

first = columns[0][1]["per_molecule"]
example = next(iter(first.values()))
print("per-molecule keys:", {k: (round(v, 3) if isinstance(v, float) else str(v)[:60]) for k, v in example.items()})
print()
header = f"{'':<26}" + "".join(f"{name:>11}" for name, _ in columns)
print(header)
for family in FAMILIES:
    print(f"{'diag ' + family:<26}" + "".join(f"{read['diag_rms'][family]:>11.2f}" for _, read in columns))
for key in ("corrected_freq_rms", "coupling_rms", "dH_residual_ratio"):
    print(f"{key:<26}" + "".join(f"{read[key]:>11.3f}" for _, read in columns))
print()
numeric = [k for k, v in example.items() if isinstance(v, (int, float))]
for key in numeric:
    print(f"--- per molecule: {key}")
    for mol in first:
        cells = "".join(f"{read['per_molecule'].get(mol, {}).get(key, float('nan')):>11.3f}" for _, read in columns)
        print(f"{mol:<26}{cells}")
