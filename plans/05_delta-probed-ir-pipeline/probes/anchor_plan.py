"""The anchor plan (TASKS 84; the user, 22 Oct 2026: 'Die 100-200 moeten de kleinste mogelijke zijn die de families dekken. Om de kosten te
minimaliseren. Weten we welke?'): which corpus molecules would cover the out-of-plane families at the lowest price.

Step 1, the cells. A C–H out-of-plane band is set mainly by how many C–H groups sit next to each other on one ring (solo, duo, trio, quartet;
a lone benzene ring is a sextet) — the classical PAH assignment — and, as the anchors showed (TASKS 82, 22 Oct), the CC correction to it
moves with ring fusion. A cell is (adjacency class, ring context, aza, charge). A molecule covers every cell its rings provide.

The target domain (the user, 23 Oct 2026): fused aromatics of C, H and N with the corpus's substituents, neutral and cation — ring atoms C
or N only, at least one aromatic six-membered ring; QM9 (layer C) and O/S heterocycles are out.

    python probes/anchor_plan.py cells    # per-cell counts over the corpus manifest → out/anchor_plan/cells.json and cells.md
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from collections import Counter
from pathlib import Path

from rdkit import Chem

PLAN = Path(__file__).resolve().parents[1]
M05 = PLAN / "modules" / "05_support_predictor"
MANIFEST = M05 / "corpus" / "manifest.csv"
OUT = M05 / "out" / "anchor_plan"
ADJACENCY = {1: "solo", 2: "duo", 3: "trio", 4: "quartet", 5: "quintet", 6: "sextet"}
CATION_LAYERS = {"P3c"}
OUT_OF_DOMAIN_LAYERS = {"C"}                     # QM9
RING_ELEMENTS = {"C", "N"}


def ch_runs(mol: Chem.Mol) -> list[tuple[int, int]]:
    """(ring size, run length) for every run of adjacent C–H atoms around a ring — sp2 ring carbons with one hydrogen, aromatic or not (a
    five-membered ring's C=C bends out of plane too); runs are broken by ring atoms without exactly one hydrogen (fusion carbons,
    substituted carbons, nitrogens). A C–H atom has two heavy neighbours, so it lies on one ring only."""
    out = []
    for ring in mol.GetRingInfo().AtomRings():
        is_ch = [mol.GetAtomWithIdx(a).GetSymbol() == "C" and mol.GetAtomWithIdx(a).GetHybridization() == Chem.HybridizationType.SP2
                 and mol.GetAtomWithIdx(a).GetTotalNumHs() == 1 for a in ring]
        n = len(ring)
        if all(is_ch):
            out.append((n, n))
            continue
        start = is_ch.index(False)                       # rotate so the cycle starts on a break; runs then do not wrap
        run = 0
        for k in range(1, n + 1):
            if is_ch[(start + k) % n]:
                run += 1
            elif run:
                out.append((n, run))
                run = 0
    return out


def ring_context(mol: Chem.Mol) -> str:
    """'one' ring, 'two' or 'three+' rings, with '-five' when any ring has five members."""
    rings = mol.GetRingInfo().AtomRings()
    base = "one" if len(rings) == 1 else "two" if len(rings) == 2 else "three+"
    return base + ("-five" if any(len(r) == 5 for r in rings) else "")


def cells(smiles: str, layer: str) -> set[tuple[str, str, bool, int]]:
    """The cells a molecule covers: (adjacency class, ring context, aza, charge). Runs on five-membered rings carry a '5' suffix."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"unreadable SMILES {smiles!r}")
    aza = any(a.GetSymbol() == "N" and a.GetIsAromatic() for a in mol.GetAtoms())
    charge = 1 if layer in CATION_LAYERS else 0
    ctx = ring_context(mol)
    return {(ADJACENCY.get(run, f"run{run}") + ("5" if size == 5 else ""), ctx, aza, charge) for size, run in ch_runs(mol)}


def in_domain(smiles: str, layer: str) -> bool:
    """The anchor plan's target domain: not QM9, ring atoms C or N only, at least one aromatic six-membered ring."""
    if layer in OUT_OF_DOMAIN_LAYERS:
        return False
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"unreadable SMILES {smiles!r}")
    if any(a.IsInRing() and a.GetSymbol() not in RING_ELEMENTS for a in mol.GetAtoms()):
        return False
    return any(len(r) == 6 and all(mol.GetAtomWithIdx(a).GetIsAromatic() for a in r) for r in mol.GetRingInfo().AtomRings())


def corpus_cells(manifest: Path = MANIFEST) -> dict[str, dict]:
    """Every corpus row in the target domain: its cells, atom count, layer and status (computed rows carry proxy labels)."""
    out = {}
    with manifest.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["smiles"] and in_domain(r["smiles"], r["layer"]):
                out[r["id"]] = {"name": r["name"], "layer": r["layer"], "status": r["status"], "n_atoms": int(r["n_atoms"] or 0),
                                "cells": sorted(cells(r["smiles"], r["layer"]))}
    return out


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding="utf-8", newline="\n")
    os.replace(tmp, path)


def cell_report(rows: dict[str, dict]) -> list[str]:
    count = Counter(tuple(c) for r in rows.values() for c in r["cells"])
    done = sum(r["status"] == "done" for r in rows.values())
    lines = ["# Anchor plan, step 1 — cells over the corpus's target domain", "",
             f"{len(rows)} molecules in the domain ({done} computed), {len(count)} cells.", "",
             "| adjacency | ring context | aza | charge | molecules | smallest (atoms) |", "|---|---|---|---|---|---|"]
    for cell, n in sorted(count.items()):
        smallest = min((r["n_atoms"], r["name"] or i) for i, r in rows.items() if list(cell) in [list(c) for c in r["cells"]])
        lines.append(f"| {cell[0]} | {cell[1]} | {'yes' if cell[2] else 'no'} | {'+1' if cell[3] else '0'} | {n} | {smallest[1]} ({smallest[0]}) |")
    return lines


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("action", choices=["cells"])
    ap.parse_args(argv)
    rows = corpus_cells()
    write_text(OUT / "cells.json", json.dumps(rows, indent=1))
    lines = cell_report(rows)
    write_text(OUT / "cells.md", "\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
