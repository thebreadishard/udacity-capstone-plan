"""Module 06 — the PAHdb comparison the report promised (PRE_REGISTRATION.md, addition of 18 Oct 2026): how far the generated samples sit
from the astrochemical distribution, measured on the molecular formula.

    python m06/pahdb_compare.py table <module02 species csv> data/pahdb_theoretical_4.00_neutral_chno.csv
    python m06/pahdb_compare.py samples notebook/out/seed0 notebook/out/samples_seed0_T1.0.txt     (needs the saved weights; checks them)
    python m06/pahdb_compare.py compare notebook/out/samples_seed0_T1.0.txt data/pahdb_theoretical_4.00_neutral_chno.csv \
        data/pubchem_aromatics_2026-09-24.csv notebook/pahdb_comparison.json notebook/figures/pahdb_comparison.png

Sets: G — seed 0's 10,000 samples at temperature 1.0 (regenerated with the notebook's own call; valid and unique), P — the PubChem dataset,
A — PAHdb v4.00's neutral C/H/N/O species. Measures: carbon count, H/C, shares with N, with O and with another element; Wasserstein-1 of
n_C and of H/C between each pair.
"""
import argparse
import csv
import json
import os
import re
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from evaluate import canonical, wasserstein1

from data import read_dataset

REGISTERED = {"validity": 0.9239, "uniqueness": 0.9916657646931486}   # results.json, seed0_T1.0 (26 Sep 2026)
N_SAMPLES, TEMPERATURE, SEED = 10000, 1.0, 0
FORMULA_RE = re.compile(r"([A-Z][a-z]?)(\d*)")


def formula_counts(formula):
    """Element counts of a molecular formula such as 'C10H7Cl'."""
    counts = {}
    for el, n in FORMULA_RE.findall(formula):
        counts[el] = counts.get(el, 0) + (int(n) if n else 1)
    return counts


def smiles_counts(smiles):
    """Element counts of a SMILES, hydrogens included."""
    from rdkit import Chem
    m = Chem.MolFromSmiles(smiles)
    counts = {}
    for a in m.GetAtoms():
        counts[a.GetSymbol()] = counts.get(a.GetSymbol(), 0) + 1
        counts["H"] = counts.get("H", 0) + a.GetTotalNumHs()
    return counts


def measures(counts_list):
    """Per set: n_C, H/C (molecules with carbon), and the shares with N, with O and with another element."""
    n_c = np.array([c.get("C", 0) for c in counts_list], float)
    h_c = np.array([c.get("H", 0) / c["C"] for c in counts_list if c.get("C")], float)
    other = [any(el not in ("C", "H", "N", "O") for el in c) for c in counts_list]
    return {"n": len(counts_list), "n_C": n_c, "H_C": h_c, "share_N": float(np.mean([c.get("N", 0) > 0 for c in counts_list])),
            "share_O": float(np.mean([c.get("O", 0) > 0 for c in counts_list])), "share_other": float(np.mean(other))}


def write_table(species_csv, out_csv):
    """PAHdb's neutral species made of C, H, N and O only, as a formula table."""
    with open(species_csv, encoding="utf-8", newline="") as fh:
        rows = [r for r in csv.DictReader(fh) if r["charge"] == "0"]
    keep = [r for r in rows if int(r["n_c"]) + int(r["n_h"]) + int(r["n_n"]) + int(r["n_o"]) == int(r["n_atoms"])]
    Path(out_csv).parent.mkdir(parents=True, exist_ok=True)
    tmp = out_csv + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["uid", "formula", "n_c", "n_h", "n_n", "n_o"])
        w.writerows([r["uid"], r["formula"], r["n_c"], r["n_h"], r["n_n"], r["n_o"]] for r in keep)
    os.replace(tmp, out_csv)
    print(f"{len(keep)} of {len(rows)} neutral species are C/H/N/O only -> {out_csv}")


def regenerate(model_dir, out_txt):
    """Seed 0's samples from its saved weights with the notebook's call; refuses unless validity and uniqueness reproduce results.json."""
    import torch
    from model import SmilesTransformer
    from train import generate

    from data import Vocab
    with open(Path(model_dir) / f"train_log_seed{SEED}.json", encoding="utf-8") as fh:
        log = json.load(fh)
    vocab = Vocab(log["vocab"])
    model = SmilesTransformer(len(vocab.itos), max_len=log["max_len"])
    model.load_state_dict(torch.load(Path(model_dir) / f"model_seed{SEED}.pt"))
    model.eval()
    samples = generate(model, vocab, n=N_SAMPLES, temperature=TEMPERATURE, seed=SEED)
    valid = [c for c in (canonical(s) for s in samples) if c]
    got = {"validity": len(valid) / len(samples), "uniqueness": len(set(valid)) / len(valid)}
    if any(abs(got[k] - REGISTERED[k]) > 1e-12 for k in REGISTERED):
        raise SystemExit(f"regenerated samples do not reproduce results.json: {got} against {REGISTERED}")
    tmp = out_txt + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(samples) + "\n")
    os.replace(tmp, out_txt)
    print(f"{len(samples)} samples reproduce results.json ({got}) -> {out_txt}")


def compare(samples_txt, table_csv, dataset_csv, out_json, out_png):
    """The three sets' measures, the pairwise W1 distances, a JSON record and the figure."""
    with open(samples_txt, encoding="utf-8") as fh:
        samples = [s for s in fh.read().splitlines() if s]
    generated = sorted({c for c in (canonical(s) for s in samples) if c})
    with open(table_csv, encoding="utf-8", newline="") as fh:
        pahdb = [{"C": int(r["n_c"]), "H": int(r["n_h"]), "N": int(r["n_n"]), "O": int(r["n_o"])} for r in csv.DictReader(fh)]
    sets = {"generated": measures([smiles_counts(s) for s in generated]),
            "pubchem": measures([formula_counts(r["formula"]) for r in read_dataset(dataset_csv)]),
            "pahdb": measures([{k: v for k, v in c.items() if v} for c in pahdb])}
    pairs = [("generated", "pubchem"), ("generated", "pahdb"), ("pubchem", "pahdb")]
    record = {"sets": {k: {"n": v["n"], "n_C_median": float(np.median(v["n_C"])), "n_C_range": [float(v["n_C"].min()), float(v["n_C"].max())],
                           "H_C_median": float(np.median(v["H_C"])), "share_N": v["share_N"], "share_O": v["share_O"], "share_other": v["share_other"]}
                       for k, v in sets.items()},
              "w1": {f"{a}|{b}": {"n_C": wasserstein1(sets[a]["n_C"], sets[b]["n_C"]), "H_C": wasserstein1(sets[a]["H_C"], sets[b]["H_C"])}
                     for a, b in pairs},
              "samples": {"file": os.path.basename(samples_txt), "n_raw": len(samples), "n_valid_unique": len(generated)}}
    tmp = out_json + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=1)
    os.replace(tmp, out_json)
    figure(sets, out_png)
    print(json.dumps(record["w1"], indent=1))
    return record


def figure(sets, out_png):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.2))
    labels = {"generated": "generated (seed 0)", "pubchem": "PubChem training data", "pahdb": "PAHdb v4.00, neutral C/H/N/O"}
    for key, v in sets.items():
        axes[0].hist(v["n_C"], bins=np.arange(0, 140, 2), density=True, histtype="step", label=labels[key])
        axes[1].hist(v["H_C"], bins=np.linspace(0, 2, 41), density=True, histtype="step", label=labels[key])
    axes[0].set(xlabel="carbon atoms per molecule", ylabel="share of molecules (density)", title="Molecule size")
    axes[1].set(xlabel="H/C ratio", ylabel="share of molecules (density)", title="Hydrogen per carbon")
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out_png, dpi=150)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("table")
    t.add_argument("species_csv")
    t.add_argument("out_csv")
    s = sub.add_parser("samples")
    s.add_argument("model_dir")
    s.add_argument("out_txt")
    c = sub.add_parser("compare")
    for name in ("samples_txt", "table_csv", "dataset_csv", "out_json", "out_png"):
        c.add_argument(name)
    a = ap.parse_args()
    if a.cmd == "table":
        write_table(a.species_csv, a.out_csv)
    elif a.cmd == "samples":
        regenerate(a.model_dir, a.out_txt)
    else:
        compare(a.samples_txt, a.table_csv, a.dataset_csv, a.out_json, a.out_png)
    return 0


if __name__ == "__main__":
    sys.exit(main())
