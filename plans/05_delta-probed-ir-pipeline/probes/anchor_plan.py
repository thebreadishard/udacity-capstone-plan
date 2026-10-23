"""The anchor plan (TASKS 84; the user, 22 Oct 2026: 'Die 100-200 moeten de kleinste mogelijke zijn die de families dekken. Om de kosten te
minimaliseren. Weten we welke?'): which corpus molecules would cover the out-of-plane families at the lowest price.

Step 1, the cells. A C–H out-of-plane band is set mainly by how many C–H groups sit next to each other on one ring (solo, duo, trio, quartet;
a lone benzene ring is a sextet) — the classical PAH assignment — and, as the anchors showed (TASKS 82, 22 Oct), the CC correction to it
moves with ring fusion. A cell is (adjacency class, ring context, aza, charge). A molecule covers every cell its rings provide.

The target domain (the user, 23 Oct 2026): fused aromatics of C, H and N with the corpus's substituents, neutral and cation — ring atoms C
or N only, at least one aromatic six-membered ring; QM9 (layer C) and O/S heterocycles are out.

Step 2, the cost of one anchor (CCSD(T)/cc-pVDZ finite-difference Hessian with its gradients, the composite's MP2 step not counted — it is
cheap): gradients ≈ 6 N + 7 for a molecule with only its plane as symmetry (central differences of every Cartesian, the reference, the CC
APT's six), at 4.6 gradients per hour on a CPX62 for 175 cc-pVDZ basis functions, scaled by (basis functions / 175)^5 — the registered
rule of anchor set three (PreRegistration_2026-10-12, 'Price and launch'), checked on its wave: quinoline and isoquinoline (Cs, 17 atoms,
175 functions) took 25.8 and 28.4 h against the rule's 26 h. Molecules with more symmetry cost less (quinoxaline, D2h: 9.9 h); the rule
does not take that saving, so it prices high for them.

Step 3, the selection: the cheapest set with at least m molecules in every cell that has m candidates (greedy: the molecule that fills the
most still-open cell places per euro, until every cell is full).

    python probes/anchor_plan.py cells                 # per-cell counts → out/anchor_plan/cells.json and cells.md
    python probes/anchor_plan.py select --per-cell 2   # the selection and its price → out/anchor_plan/selection_m2.json and .md
    python probes/anchor_plan.py select --per-cell 2 --max-atoms 26   # only what a full anchor can be; the cells left open are named
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
BASIS_FUNCTIONS = {"H": 5, "C": 14, "N": 14, "O": 14, "F": 14, "S": 18, "Cl": 18}   # cc-pVDZ, spherical d
GRADIENTS_PER_HOUR = 4.6        # two partial runs of 8 threads on a CPX62, quinoline (anchor set three's measured timing, 12 Oct 2026)
REFERENCE_FUNCTIONS = 175       # quinoline's cc-pVDZ basis
SIZE_EXPONENT = 5               # the registered size rule of anchor set three
EXTRA_GRADIENTS = 7             # the reference gradient and the CC APT's six
EUR_PER_HOUR_CPX62 = 0.208      # modules/08_industry_synthesis/m08/prices.py
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
                n_atoms = Chem.AddHs(Chem.MolFromSmiles(r["smiles"])).GetNumAtoms()
                n_functions = basis_functions(r["smiles"])
                hours = anchor_hours(n_atoms, n_functions)
                out[r["id"]] = {"name": r["name"], "layer": r["layer"], "status": r["status"], "n_atoms": n_atoms, "basis_functions": n_functions,
                                "hours": round(hours, 1), "eur": round(hours * EUR_PER_HOUR_CPX62, 2), "cells": sorted(cells(r["smiles"], r["layer"]))}
    return out


def basis_functions(smiles: str) -> int:
    """cc-pVDZ basis functions (spherical) of the molecule with its hydrogens."""
    mol = Chem.AddHs(Chem.MolFromSmiles(smiles))
    missing = sorted({a.GetSymbol() for a in mol.GetAtoms()} - set(BASIS_FUNCTIONS))
    if missing:
        raise ValueError(f"no cc-pVDZ count for {missing}")
    return sum(BASIS_FUNCTIONS[a.GetSymbol()] for a in mol.GetAtoms())


def anchor_hours(n_atoms: int, n_functions: int) -> float:
    """CPX62 hours of one anchor with only its plane as symmetry (the rule of step 2)."""
    return (6 * n_atoms + EXTRA_GRADIENTS) / GRADIENTS_PER_HOUR * (n_functions / REFERENCE_FUNCTIONS) ** SIZE_EXPONENT


def select(rows: dict[str, dict], per_cell: int) -> list[str]:
    """The greedy cheapest multi-cover: each step takes the molecule with the most still-open cell places per euro, until every cell has
    min(per_cell, its candidates) molecules. Ties go to the smaller molecule, then the id, so the selection is reproducible."""
    members: dict[tuple, list[str]] = {}
    for i, r in rows.items():
        for c in r["cells"]:
            members.setdefault(tuple(c), []).append(i)
    need = {c: min(per_cell, len(m)) for c, m in members.items()}
    chosen: list[str] = []
    left = set(rows)
    while any(need.values()):
        def gain(i: str) -> int:
            return sum(1 for c in rows[i]["cells"] if need[tuple(c)] > 0)
        best = max((i for i in left if gain(i)), key=lambda i: (gain(i) / rows[i]["eur"], -rows[i]["n_atoms"], i))
        chosen.append(best)
        left.discard(best)
        for c in rows[best]["cells"]:
            need[tuple(c)] = max(0, need[tuple(c)] - 1)
    return chosen


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


def selection_report(rows: dict[str, dict], chosen: list[str], per_cell: int, open_cells: list[tuple] = ()) -> list[str]:
    cells_all = {tuple(c) for r in rows.values() for c in r["cells"]}
    short = sorted(c for c in cells_all if sum(tuple(c) in {tuple(x) for x in rows[i]["cells"]} for i in rows) < per_cell)
    eur = sum(rows[i]["eur"] for i in chosen)
    hours = sum(rows[i]["hours"] for i in chosen)
    lines = [f"# Anchor plan — the cheapest cover with {per_cell} molecules per cell", "",
             f"**{len(chosen)} molecules, ≈ {hours:,.0f} CPX62 hours, ≈ €{eur:,.0f}** (the CC/DZ Hessian and the CC APT; the MP2 step not counted). "
             f"{len(cells_all)} cells; {len(short)} have fewer than {per_cell} candidates and are filled as far as they go. "
             f"Already computed in the corpus (proxy labels exist): {sum(rows[i]['status'] == 'done' for i in chosen)}.", "",
             *([f"Cells left without a candidate under the size limit ({len(open_cells)}): " + "; ".join(" / ".join(map(str, c)) for c in open_cells), ""]
               if open_cells else []),
             "| molecule | id | atoms | basis functions | h | € | cells |", "|---|---|---|---|---|---|---|"]
    lines += [f"| {rows[i]['name']} | {i} | {rows[i]['n_atoms']} | {rows[i]['basis_functions']} | {rows[i]['hours']:.0f} | {rows[i]['eur']:.0f} | "
              f"{len(rows[i]['cells'])} |" for i in sorted(chosen, key=lambda i: rows[i]['eur'])]
    return lines


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("action", choices=["cells", "select"])
    ap.add_argument("--per-cell", type=int, default=2)
    ap.add_argument("--max-atoms", type=int, default=None, help="select: only molecules up to this many atoms (a full anchor's reach)")
    a = ap.parse_args(argv)
    rows = corpus_cells()
    if a.action == "cells":
        write_text(OUT / "cells.json", json.dumps(rows, indent=1))
        lines = cell_report(rows)
        write_text(OUT / "cells.md", "\n".join(lines) + "\n")
    else:
        if a.per_cell < 1:
            raise SystemExit("--per-cell must be at least 1")
        pool = {i: r for i, r in rows.items() if a.max_atoms is None or r["n_atoms"] <= a.max_atoms}
        open_cells = sorted({tuple(c) for r in rows.values() for c in r["cells"]} - {tuple(c) for r in pool.values() for c in r["cells"]})
        chosen = select(pool, a.per_cell)
        stem = f"selection_m{a.per_cell}" + (f"_max{a.max_atoms}" if a.max_atoms else "")
        write_text(OUT / f"{stem}.json", json.dumps({"per_cell": a.per_cell, "max_atoms": a.max_atoms, "chosen": chosen,
                                                     "open_cells": [list(c) for c in open_cells]}, indent=1))
        lines = selection_report(pool, chosen, a.per_cell, open_cells)
        write_text(OUT / f"{stem}.md", "\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
