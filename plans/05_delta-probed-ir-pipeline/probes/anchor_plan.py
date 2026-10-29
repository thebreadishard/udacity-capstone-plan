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
    python probes/anchor_plan.py fill --target 30      # the corpus side: DFT molecules missing per cell to 30, the cheapest pending ones
    python probes/anchor_plan.py count --n 167         # N anchors with the anchor count's ring-context mix → out/anchor_plan/count_n167.*

The count (TASKS 82; the anchor count of 29 Oct 2026, `PreRegistration_2026-10-29_Anchor_Count.md`): its N was read on random draws from
the proxy check's reservoir, and a cell cover did not beat random draws (arm (c)'s C1), so N anchors are priced with the reservoir's mix
of ring contexts (single, fused, five; `fusion_context`): per context its share of N, the cheapest neutral molecules of that context in
the domain. Beside it, the price of N drawn as the count drew them: N times the reservoir's mean price. The cheapest selection is
smaller than the reservoir's molecules, which the count did not measure; the two prices bracket the plan. Cations are left out (their
route is TASKS 98), and molecules above 250 cc-pVDZ functions are counted because a CPX62's 32 GB does not hold them (TASKS 93).

The fill list (decision 52: ~30 mixed children cover a scaffold family): 'computed' is a manifest row marked done or a molecule with a
ωB97X Hessian in a fetched, not yet merged shard folder (corpus/shards_*); its price is the cheap deck on the laptop, a power law in the
6-31G* basis functions fitted to the corpus ledger's laptop rows.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from rdkit import Chem

PLAN = Path(__file__).resolve().parents[1]
M05 = PLAN / "modules" / "05_support_predictor"
M08 = PLAN / "modules" / "08_industry_synthesis"
sys.path.insert(0, str(M08))
from m08.prices import MACHINES  # noqa: E402  (after the sys.path insert)

MANIFEST = M05 / "corpus" / "manifest.csv"
LEDGER = M05 / "corpus" / "ledger.csv"
CORPUS = M05 / "corpus"
OUT = M05 / "out" / "anchor_plan"
ADJACENCY = {1: "solo", 2: "duo", 3: "trio", 4: "quartet", 5: "quintet", 6: "sextet"}
BASIS_FUNCTIONS = {"H": 5, "C": 14, "N": 14, "O": 14, "F": 14, "S": 18, "Cl": 18}   # cc-pVDZ, spherical d
BASIS_FUNCTIONS_631GS = {"H": 2, "C": 15, "N": 15, "O": 15, "F": 15, "S": 19, "Cl": 19}   # 6-31G*, Cartesian d (the corpus deck)
LAPTOP = "Asus18"
GRADIENTS_PER_HOUR = 4.6        # two partial runs of 8 threads on a CPX62, quinoline (anchor set three's measured timing, 12 Oct 2026)
REFERENCE_FUNCTIONS = 175       # quinoline's cc-pVDZ basis
SIZE_EXPONENT = 5               # the registered size rule of anchor set three
EXTRA_GRADIENTS = 7             # the reference gradient and the CC APT's six
EUR_PER_HOUR_CPX62 = MACHINES["CPX62"]["eur_per_hour"]
CATION_LAYERS = {"P3c"}
RESERVOIR = M05 / "out" / "proxy_check_2026-10-21" / "a_reservoir.txt"   # the anchor count's draws (PreRegistration_2026-10-29_Anchor_Count.md)
CPX62_FUNCTION_LIMIT = 250                       # above it a CC/DZ anchor needs more than a CPX62's 32 GB (TASKS 93)
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


def fusion_context(mol: Chem.Mol) -> str:
    """The context the CC correction's CH-oop mean shift follows on the anchors (TASKS 82, 27 Oct 2026: ≈ 0 on single rings, about half
    the proxy's with the opposite sign on fused ones, about the proxy's with a five-membered ring): 'five' when any ring has five members,
    else 'fused' when a ring atom belongs to two rings, else 'single' (one ring, or rings joined by a bond as in biphenyl)."""
    rings = mol.GetRingInfo().AtomRings()
    if any(len(r) == 5 for r in rings):
        return "five"
    shared = Counter(a for r in rings for a in r)
    return "fused" if any(n > 1 for n in shared.values()) else "single"


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
                out[r["id"]] = {"name": r["name"], "smiles": r["smiles"], "layer": r["layer"], "status": r["status"], "n_atoms": n_atoms,
                                "basis_functions": n_functions,
                                "hours": round(hours, 1), "eur": round(hours * EUR_PER_HOUR_CPX62, 2), "cells": sorted(cells(r["smiles"], r["layer"]))}
    return out


def basis_functions(smiles: str, table: dict[str, int] = BASIS_FUNCTIONS) -> int:
    """Basis functions of the molecule with its hydrogens: cc-pVDZ (spherical) by default, or another per-element table."""
    mol = Chem.AddHs(Chem.MolFromSmiles(smiles))
    missing = sorted({a.GetSymbol() for a in mol.GetAtoms()} - set(table))
    if missing:
        raise ValueError(f"no basis count for {missing}")
    return sum(table[a.GetSymbol()] for a in mol.GetAtoms())


def fit_power_law(points: list[tuple[float, float]]) -> tuple[float, float]:
    """(log prefactor, exponent) of seconds = e^a · n^b, least squares in log-log; refuses fewer than three points."""
    if len(points) < 3:
        raise SystemExit(f"a power law needs at least three timed rows, got {len(points)}")
    x, y = np.log([p[0] for p in points]), np.log([p[1] for p in points])
    b, a = np.polyfit(x, y, 1)
    return float(a), float(b)


def dft_cost_model(smiles_of: dict[str, str], ledger: Path = LEDGER) -> tuple[float, float]:
    """The cheap deck's laptop seconds as a power law in the 6-31G* basis functions, from the ledger's finished laptop rows."""
    with ledger.open(encoding="utf-8") as f:
        pts = [(basis_functions(smiles_of[r["id"]], BASIS_FUNCTIONS_631GS), float(r["seconds_total"])) for r in csv.DictReader(f)
               if r["status"] == "done" and r["machine"] == LAPTOP and r["seconds_total"] and r["id"] in smiles_of]
    return fit_power_law(pts)


def computed_ids(manifest_rows: list[dict], corpus: Path = CORPUS) -> set[str]:
    """Manifest rows marked done, and molecules with a ωB97X Hessian in a fetched shard folder not yet merged."""
    done = {r["id"] for r in manifest_rows if r["status"] == "done"}
    shards = {p.parent.name for p in corpus.glob("shards_*/**/hessian_wb97x.npz")}
    return done | shards


def anchor_hours(n_atoms: int, n_functions: int) -> float:
    """CPX62 hours of one anchor with only its plane as symmetry (the rule of step 2)."""
    return (6 * n_atoms + EXTRA_GRADIENTS) / GRADIENTS_PER_HOUR * (n_functions / REFERENCE_FUNCTIONS) ** SIZE_EXPONENT


def cell_members(rows: dict[str, dict]) -> dict[tuple, list[str]]:
    members: dict[tuple, list[str]] = {}
    for i, r in rows.items():
        for c in r["cells"]:
            members.setdefault(tuple(c), []).append(i)
    return members


def select(rows: dict[str, dict], demand: dict[tuple, int], cost: str = "eur") -> list[str]:
    """The greedy cheapest multi-cover: each step takes the molecule with the most still-open cell places per unit of `cost`, until every
    cell has min(its demand, its candidates) molecules. Ties go to the smaller molecule, then the id, so the selection is reproducible.
    Greedy, so an approximation of the cheapest cover (within a logarithmic factor of it), not the exact optimum an integer program gives."""
    members = cell_members(rows)
    need = {c: min(demand.get(c, 0), len(members.get(c, []))) for c in set(demand) | set(members)}
    chosen: list[str] = []
    left = set(rows)
    while any(need.values()):
        def gain(i: str) -> int:
            return sum(1 for c in rows[i]["cells"] if need[tuple(c)] > 0)
        best = max((i for i in left if gain(i)), key=lambda i: (gain(i) / rows[i][cost], -rows[i]["n_atoms"], i))
        chosen.append(best)
        left.discard(best)
        for c in rows[best]["cells"]:
            need[tuple(c)] = max(0, need[tuple(c)] - 1)
    return chosen


def reservoir_rows(reservoir: Path = RESERVOIR, manifest: Path = MANIFEST) -> dict[str, dict]:
    """The reservoir's molecules with their ring context and anchor price (in the domain or not: the count drew from all of them)."""
    ids = reservoir.read_text(encoding="utf-8").split()
    with manifest.open(encoding="utf-8") as f:
        smiles = {r["id"]: r["smiles"] for r in csv.DictReader(f)}
    missing = [i for i in ids if not smiles.get(i)]
    if missing:
        raise ValueError(f"{len(missing)} reservoir ids without a SMILES in the manifest: {missing[:5]}")
    out = {}
    for i in ids:
        mol = Chem.MolFromSmiles(smiles[i])
        hours = anchor_hours(Chem.AddHs(mol).GetNumAtoms(), basis_functions(smiles[i]))
        out[i] = {"context": fusion_context(mol), "hours": hours, "eur": hours * EUR_PER_HOUR_CPX62}
    return out


def quotas(n: int, counts: dict[str, int]) -> dict[str, int]:
    """n split over the contexts in proportion to `counts` (largest remainder, ties by name), summing to n."""
    total = sum(counts.values())
    exact = {c: n * k / total for c, k in counts.items()}
    q = {c: int(x) for c, x in exact.items()}
    for c in sorted(exact, key=lambda c: (-(exact[c] - q[c]), c))[: n - sum(q.values())]:
        q[c] += 1
    return q


def count_selection(rows: dict[str, dict], quota: dict[str, int]) -> dict[str, list[str]]:
    """Per context, its quota of the cheapest neutral domain molecules (ties: fewer atoms, then the id); too few candidates is refused."""
    out = {}
    for ctx, k in quota.items():
        pool = sorted((i for i, r in rows.items() if r["layer"] not in CATION_LAYERS and fusion_context(Chem.MolFromSmiles(r["smiles"])) == ctx),
                      key=lambda i: (rows[i]["eur"], rows[i]["n_atoms"], i))
        if len(pool) < k:
            raise ValueError(f"context {ctx}: {k} anchors asked, {len(pool)} neutral candidates in the domain")
        out[ctx] = pool[:k]
    return out


def count_report(rows: dict[str, dict], chosen: dict[str, list[str]], reservoir: dict[str, dict], n: int) -> list[str]:
    ids = [i for v in chosen.values() for i in v]
    eur, hours = sum(rows[i]["eur"] for i in ids), sum(rows[i]["hours"] for i in ids)
    mean_eur = sum(r["eur"] for r in reservoir.values()) / len(reservoir)
    big = [i for i in ids if rows[i]["basis_functions"] > CPX62_FUNCTION_LIMIT]
    counts = Counter(r["context"] for r in reservoir.values())
    lines = [f"# Anchor plan — {n} anchors with the anchor count's ring-context mix", "",
             f"**The cheapest {n}: ≈ {hours:,.0f} CPX62 hours, ≈ €{eur:,.0f}** (the CC/DZ Hessian and the CC APT; the MP2 step not counted). "
             f"**Drawn as the count drew them: ≈ €{n * mean_eur:,.0f}** ({n} × the reservoir's mean €{mean_eur:,.0f} over {len(reservoir)} molecules). "
             "The cheapest selection is made of smaller molecules than the reservoir's, which the count did not measure; the two bracket the plan.", "",
             f"Mix (the reservoir's {len(reservoir)}): " + ", ".join(f"{c} {counts[c]}" for c in sorted(counts)) + ". "
             f"Neutral only (cations: TASKS 98). Already computed in the corpus (proxy labels exist): {sum(rows[i]['status'] == 'done' for i in ids)}. "
             f"Above {CPX62_FUNCTION_LIMIT} cc-pVDZ functions (more than a CPX62's 32 GB, TASKS 93): {len(big)}.", "",
             "| context | anchors | atoms | basis functions | h | € |", "|---|---|---|---|---|---|"]
    for ctx, v in sorted(chosen.items()):
        lines.append(f"| {ctx} | {len(v)} | {min(rows[i]['n_atoms'] for i in v)}–{max(rows[i]['n_atoms'] for i in v)} | "
                     f"{min(rows[i]['basis_functions'] for i in v)}–{max(rows[i]['basis_functions'] for i in v)} | "
                     f"{sum(rows[i]['hours'] for i in v):,.0f} | {sum(rows[i]['eur'] for i in v):,.0f} |")
    return lines


def count_action(rows: dict[str, dict], n: int) -> list[str]:
    if n < 1:
        raise SystemExit("--n must be at least 1")
    reservoir = reservoir_rows()
    quota = quotas(n, dict(Counter(r["context"] for r in reservoir.values())))
    chosen = count_selection(rows, quota)
    write_text(OUT / f"count_n{n}.json", json.dumps({"n": n, "quota": quota, "chosen": chosen, "reservoir": str(RESERVOIR.relative_to(PLAN))}, indent=1))
    lines = count_report(rows, chosen, reservoir, n)
    write_text(OUT / f"count_n{n}.md", "\n".join(lines) + "\n")
    return lines


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


def fill_plan(rows: dict[str, dict], computed: set[str], target: int) -> tuple[dict, list[str]]:
    """Per cell (computed, demand) and the cheapest pending molecules that bring every cell to `target` computed ones (laptop hours)."""
    have = Counter(tuple(c) for i, r in rows.items() if i in computed for c in r["cells"])
    cells_all = set(cell_members(rows))
    demand = {c: max(0, target - have[c]) for c in cells_all}
    pending = {i: r for i, r in rows.items() if i not in computed}
    chosen = select(pending, demand, cost="dft_hours")
    return {c: (have[c], demand[c]) for c in cells_all}, chosen


def fill_report(rows: dict[str, dict], per_cell: dict, chosen: list[str], target: int, model: tuple[float, float]) -> list[str]:
    got = Counter(tuple(c) for i in chosen for c in rows[i]["cells"])
    hours = sum(rows[i]["dft_hours"] for i in chosen)
    short = {c: d - min(d, got[c]) for c, (_, d) in per_cell.items() if got[c] < d}
    lines = [f"# Corpus fill list — every cell to {target} computed molecules (decision 52)", "",
             f"**{len(chosen)} molecules to compute, ≈ {hours:,.0f} laptop hours** (the cheap deck; seconds = e^{model[0]:.2f} · n^{model[1]:.2f} "
             "in the 6-31G* basis functions, fitted to the ledger's laptop rows). "
             f"{sum(1 for _, d in per_cell.values() if d == 0)} of {len(per_cell)} cells already have {target}; "
             f"{len(short)} cannot reach {target} from the manifest's candidates.", "",
             "| adjacency | ring context | aza | charge | computed | missing | filled | short |", "|---|---|---|---|---|---|---|---|"]
    for c, (h, d) in sorted(per_cell.items(), key=lambda x: -x[1][1]):
        if d:
            lines.append(f"| {c[0]} | {c[1]} | {'yes' if c[2] else 'no'} | {'+1' if c[3] else '0'} | {h} | {d} | {min(d, got[c])} | {short.get(c, 0)} |")
    return lines


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("action", choices=["cells", "select", "fill", "count"])
    ap.add_argument("--n", type=int, default=None, help="count: the number of anchors to price (the anchor count read 167, 29 Oct 2026)")
    ap.add_argument("--target", type=int, default=30, help="fill: computed molecules per cell (decision 52: ~30 cover a family)")
    ap.add_argument("--per-cell", type=int, default=2)
    ap.add_argument("--max-atoms", type=int, default=None, help="select: only molecules up to this many atoms (a full anchor's reach)")
    a = ap.parse_args(argv)
    rows = corpus_cells()
    if a.action == "count":
        if a.n is None:
            raise SystemExit("count needs --n")
        lines = count_action(rows, a.n)
    elif a.action == "fill":
        with MANIFEST.open(encoding="utf-8") as f:
            manifest = list(csv.DictReader(f))
        model = dft_cost_model({r["id"]: r["smiles"] for r in manifest if r["smiles"]})
        for r in rows.values():
            r["dft_hours"] = round(float(np.exp(model[0])) * basis_functions(r["smiles"], BASIS_FUNCTIONS_631GS) ** model[1] / 3600, 2)
        per_cell, chosen = fill_plan(rows, computed_ids(manifest), a.target)
        write_text(OUT / f"fill_t{a.target}.json", json.dumps({"target": a.target, "model": model, "chosen": chosen,
                                                               "per_cell": [[list(c), h, d] for c, (h, d) in per_cell.items()]}, indent=1))
        lines = fill_report(rows, per_cell, chosen, a.target, model)
        write_text(OUT / f"fill_t{a.target}.md", "\n".join(lines) + "\n")
    elif a.action == "cells":
        write_text(OUT / "cells.json", json.dumps(rows, indent=1))
        lines = cell_report(rows)
        write_text(OUT / "cells.md", "\n".join(lines) + "\n")
    else:
        if a.per_cell < 1:
            raise SystemExit("--per-cell must be at least 1")
        pool = {i: r for i, r in rows.items() if a.max_atoms is None or r["n_atoms"] <= a.max_atoms}
        open_cells = sorted({tuple(c) for r in rows.values() for c in r["cells"]} - {tuple(c) for r in pool.values() for c in r["cells"]})
        chosen = select(pool, dict.fromkeys(cell_members(pool), a.per_cell))
        stem = f"selection_m{a.per_cell}" + (f"_max{a.max_atoms}" if a.max_atoms else "")
        write_text(OUT / f"{stem}.json", json.dumps({"per_cell": a.per_cell, "max_atoms": a.max_atoms, "chosen": chosen,
                                                     "open_cells": [list(c) for c in open_cells]}, indent=1))
        lines = selection_report(pool, chosen, a.per_cell, open_cells)
        write_text(OUT / f"{stem}.md", "\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
