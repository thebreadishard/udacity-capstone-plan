"""Prices of the remaining computations per route (TASKS 92, 86, 96; the user, 23 Oct 2026: 'kosten ... op verschillende manieren: laptop,
Helsinki, PC en Snellius').

Every price is a power law fitted to measured runs and names its source; what is scaled rather than measured says so in the report.

  fill     the corpus fill list (`anchor_plan.py fill`): the corpus deck per machine class, fitted to the finished neutral rows of the
           corpus ledgers (main and shards) in the 6-31G* basis functions; and the analytic labels as the labels server makes them, fitted
           to its lane logs in the atom count
  mp2      the composite's DF-MP2 step for the anchor cover (`anchor_plan.py select`), per gradient from the five anchors of 20 Oct (`time -v`
           wall time and peak, NBF and the gradient count from each psi4 log), 6 N gradients per molecule
  cations  radical cations of computed neutrals for the cation cells short of the target: a neutral's cation covers its cells with charge
           +1; candidates are computed in-domain neutrals whose cation twin (same SMILES hash) is not in the manifest; priced on the
           laptop's analytic UKS runs ('(CA) <id> max RSS .. kB, wall .. s'), selected by anchor_plan's greedy cover

    python probes/compute_prices.py fill|mp2|cations      → out/anchor_plan/price_<action>.md and .json
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import anchor_plan as ap
from m08.prices import MACHINES, host_class  # anchor_plan puts modules/08_industry_synthesis on the path

RESULTS = ap.PLAN / "probes" / "results_m1"
CC_PVTZ = {"H": 14, "C": 30, "N": 30, "O": 30, "F": 30, "S": 34, "Cl": 34}   # spherical
CATION_LAYER = "P3c"
LANE_OK = re.compile(r"^\[[^]]+\] lane \d+ (\S+) ok (\d+) s")
CATION_RUN = re.compile(r"\(CA\) (P3c_[0-9a-f]+) max RSS (\d+) kB, wall ([\d.]+) s")
THREADS = re.compile(r"threads=(\d+)")


@dataclass(frozen=True)
class Sources:
    """Where the measured runs are; the defaults are the records the 23 Oct prices came from."""
    manifest: Path = ap.MANIFEST
    corpus: Path = ap.CORPUS
    lane_logs: Path = RESULTS / "labels_lane_logs_2026-10-23"
    dfmp2: Path = RESULTS / "dfmp2_anchors_2026-10-20"
    cation_log: Path = RESULTS / "cation_analytic_2026-10-09.analytic.log"
    fill: Path = ap.OUT / "fill_t30.json"
    cover: Path = ap.OUT / "selection_m2_max26.json"


def read_manifest(path: Path) -> dict[str, dict]:
    with path.open(encoding="utf-8") as f:
        return {r["id"]: r for r in csv.DictReader(f)}


def machine_class(row: dict) -> str | None:
    """'laptop' or '<server class>, <n> threads'; None when the row does not say how many threads it ran (no fair comparison)."""
    host = host_class(row["machine"])
    if host == "laptop":
        return "laptop"
    m = THREADS.search(row.get("note") or "")
    return f"{host}, {m[1]} threads" if m and host != "unknown" else None


def deck_points(corpus: Path, functions_of: dict[str, int]) -> dict[str, list[tuple[float, float]]]:
    """(6-31G* functions, seconds) per machine class from every finished neutral row of the corpus ledgers, each run counted once."""
    points: dict[str, list[tuple[float, float]]] = {}
    seen = set()
    for ledger in [corpus / "ledger.csv", *sorted(corpus.glob("shards_*/**/ledger.csv"))]:
        with ledger.open(encoding="utf-8") as f:
            for r in csv.DictReader(f):
                cls = machine_class(r)
                key = (r["id"], r["machine"], r["start"])
                if (cls is None or r["status"] != "done" or not r["seconds_total"] or r["layer"] in ap.CATION_LAYERS
                        or r["id"] not in functions_of or key in seen):
                    continue
                seen.add(key)
                points.setdefault(cls, []).append((functions_of[r["id"]], float(r["seconds_total"])))
    return points


def lane_points(lane_logs: Path, atoms_of: dict[str, int]) -> list[tuple[float, float]]:
    """(atoms, seconds) of every molecule a labels lane finished ('ok' lines of lane_<n>.log)."""
    pts = []
    for log in sorted(lane_logs.glob("lane_*.log")):
        for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
            m = LANE_OK.match(line)
            if m:
                pts.append((atoms_of[m[1]], float(m[2])))
    return pts


def wall_seconds(text: str) -> float:
    """`time -v`'s 'Elapsed (wall clock) time (h:mm:ss or m:ss)' in seconds."""
    m = re.search(r"Elapsed \(wall clock\) time \(h:mm:ss or m:ss\): ([\d:.]+)", text)
    if m is None:
        raise ValueError("no wall clock line")
    return sum(float(x) * 60 ** k for k, x in enumerate(reversed(m[1].split(":"))))


def mp2_records(dfmp2: Path) -> list[dict]:
    """Per molecule and basis: NBF, gradients, wall seconds and peak GB, from time_<name>_<basis>.txt and dfmp2_rows_<name>_<basis>.psi4.log."""
    records = []
    for timing in sorted(dfmp2.glob("time_*_ccpv?z.txt")):
        name, basis = timing.stem[len("time_"):].rsplit("_", 1)
        text = timing.read_text(encoding="utf-8")
        log = (dfmp2 / f"dfmp2_rows_{name}_{basis}.psi4.log").read_text(encoding="utf-8", errors="replace")
        nbf = re.search(r"NBF = +(\d+)", log)
        if nbf is None:
            raise ValueError(f"no NBF in the {name} {basis} psi4 log")
        peak = re.search(r"Maximum resident set size \(kbytes\): (\d+)", text)
        records.append({"name": name, "basis": basis, "nbf": int(nbf[1]), "gradients": log.count("Total Gradient"),
                        "seconds": wall_seconds(text), "peak_gb": int(peak[1]) / 1024 ** 2})
    return records


def cation_runs(log: Path) -> dict[str, tuple[float, float]]:
    """id → (peak GB, wall seconds) of the laptop's finished analytic cation runs."""
    text = log.read_text(encoding="utf-8", errors="replace")
    return {m[1]: (int(m[2]) / 1024 ** 2, float(m[3])) for m in CATION_RUN.finditer(text)}


def power(model: tuple[float, float], n: float) -> float:
    return math.exp(model[0]) * n ** model[1]


def fill_price(src: Sources) -> tuple[dict, list[str]]:
    manifest = read_manifest(src.manifest)
    chosen = json.loads(src.fill.read_text(encoding="utf-8"))["chosen"]
    functions_of = {i: ap.basis_functions(r["smiles"], ap.BASIS_FUNCTIONS_631GS) for i, r in manifest.items() if r["smiles"]}
    sizes = [functions_of[i] for i in chosen]
    deck = deck_points(src.corpus, functions_of)
    lane = lane_points(src.lane_logs, {i: int(r["n_atoms"]) for i, r in manifest.items() if r["n_atoms"]})
    lane_model = ap.fit_power_law(lane)
    lane_hours = sum(power(lane_model, int(manifest[i]["n_atoms"])) for i in chosen) / 3600
    out = {"molecules": len(chosen), "deck": {}, "analytic_lane": {"rows": len(lane), "model": lane_model, "lane_hours": lane_hours}}
    lines = [f"# Price of the corpus fill list ({len(chosen)} molecules, {src.fill.name})", "",
             f"6-31G* functions {min(sizes)}–{max(sizes)}, median {sorted(sizes)[len(sizes) // 2]}.", "",
             "| route | timed rows (functions) | seconds | fill hours |", "|---|---|---|---|"]
    for cls, pts in sorted(deck.items()):
        model = ap.fit_power_law(pts)
        hours = sum(power(model, n) for n in sizes) / 3600
        out["deck"][cls] = {"rows": len(pts), "model": model, "hours": hours, "largest_timed": max(n for n, _ in pts)}
        lines.append(f"| deck, {cls} | {len(pts)} ({min(n for n, _ in pts):.0f}–{max(n for n, _ in pts):.0f}) | "
                     f"e^{model[0]:.2f} n^{model[1]:.2f} | {hours:,.0f} |")
    beyond = max(v["largest_timed"] for v in out["deck"].values())
    eur = lane_hours / 4 * MACHINES["CCX53"]["eur_per_hour"]
    lines += [f"| analytic labels, CCX53 8-thread lane (n = atoms) | {len(lane)} ({min(n for n, _ in lane):.0f}–{max(n for n, _ in lane):.0f} "
              f"atoms) | e^{lane_model[0]:.2f} n^{lane_model[1]:.2f} | {lane_hours:,.0f} lane-hours = {lane_hours / 4:,.0f} server-hours ≈ €{eur:,.0f} |",
              "", f"Extrapolated: {sum(n > beyond for n in sizes)} fill molecules above the largest timed deck row ({beyond:.0f} functions), "
              f"{sum(int(manifest[i]['n_atoms']) > max(n for n, _ in lane) for i in chosen)} above the lanes' largest molecule."]
    return out, lines


def mp2_price(src: Sources) -> tuple[dict, list[str]]:
    manifest = read_manifest(src.manifest)
    recs = mp2_records(src.dfmp2)
    models = {b: ap.fit_power_law([(r["nbf"], r["seconds"] / r["gradients"]) for r in recs if r["basis"] == b]) for b in ("ccpvdz", "ccpvtz")}
    peak = ap.fit_power_law([(r["nbf"], r["peak_gb"]) for r in recs if r["basis"] == "ccpvtz"])
    cover = json.loads(src.cover.read_text(encoding="utf-8"))["chosen"]
    per = {}
    for i in cover:
        smi, n_atoms = manifest[i]["smiles"], int(manifest[i]["n_atoms"])
        dz, tz = ap.basis_functions(smi), ap.basis_functions(smi, CC_PVTZ)
        per[i] = {"hours": 6 * n_atoms * (power(models["ccpvdz"], dz) + power(models["ccpvtz"], tz)) / 3600, "tz_functions": tz,
                  "tz_peak_gb": power(peak, tz), "cation": manifest[i]["layer"] in ap.CATION_LAYERS}
    total = sum(v["hours"] for v in per.values())
    worst = max(per, key=lambda i: per[i]["hours"])
    out = {"models": models, "tz_peak_model": peak, "hours": total, "per_molecule": per}
    lines = [f"# Price of the MP2 step for the anchor cover ({len(cover)} molecules, {src.cover.name})", "",
             f"Per gradient, from {len(recs)} timed psi4 runs (laptop, WSL, 6 threads): cc-pVDZ s = e^{models['ccpvdz'][0]:.2f} n^{models['ccpvdz'][1]:.2f}, "
             f"cc-pVTZ s = e^{models['ccpvtz'][0]:.2f} n^{models['ccpvtz'][1]:.2f}; cc-pVTZ peak GB = e^{peak[0]:.2f} n^{peak[1]:.2f} "
             f"(timed {min(r['nbf'] for r in recs if r['basis'] == 'ccpvtz')}–{max(r['nbf'] for r in recs if r['basis'] == 'ccpvtz')} functions).", "",
             f"**≈ {total:,.0f} laptop hours** with 6 N gradients each (no symmetry credit). Largest: {manifest[worst]['name']} "
             f"({per[worst]['tz_functions']} cc-pVTZ functions) ≈ {per[worst]['hours']:.0f} h at ≈ {per[worst]['tz_peak_gb']:.1f} GB. "
             f"{sum(v['cation'] for v in per.values())} cations need the open-shell DF-MP2 gradient (TASKS 99)."]
    return out, lines


def cation_candidates(rows: dict[str, dict], manifest: dict[str, dict], computed: set[str], short: dict[tuple, int]) -> dict[str, dict]:
    """Cation twins of computed in-domain neutrals that touch a short cell and are not in the manifest yet."""
    twins = {i.split("_", 1)[1] for i in manifest if i.startswith(CATION_LAYER + "_")}
    out = {}
    for i, r in rows.items():
        sha = i.split("_", 1)[1]
        if i not in computed or r["layer"] in ap.CATION_LAYERS or sha in twins or not ap.in_domain(r["smiles"], CATION_LAYER):
            continue
        cc = sorted(ap.cells(r["smiles"], CATION_LAYER))
        if any(c in short for c in cc):
            out[f"{CATION_LAYER}_{sha}"] = {"name": r["name"], "smiles": r["smiles"], "n_atoms": r["n_atoms"], "cells": [list(c) for c in cc]}
    return out


def cation_price(src: Sources, target: int) -> tuple[dict, list[str]]:
    manifest = read_manifest(src.manifest)
    runs = cation_runs(src.cation_log)
    functions = {i: ap.basis_functions(manifest[i]["smiles"], ap.BASIS_FUNCTIONS_631GS) for i in runs}
    wall = ap.fit_power_law([(functions[i], w) for i, (_, w) in runs.items()])
    peak = ap.fit_power_law([(functions[i], g) for i, (g, _) in runs.items()])
    rows = ap.corpus_cells(src.manifest)
    computed = ap.computed_ids(list(manifest.values()), src.corpus)
    have = Counter(tuple(c) for i, r in rows.items() if i in computed for c in r["cells"])
    short = {c: target - have[c] for c in ap.cell_members(rows) if c[3] == 1 and have[c] < target}
    cands = cation_candidates(rows, manifest, computed, short)
    for v in cands.values():
        n = ap.basis_functions(v["smiles"], ap.BASIS_FUNCTIONS_631GS)
        v.update(functions=n, hours=power(wall, n) / 3600, peak_gb=power(peak, n))
    chosen = ap.select(cands, short, cost="hours")
    filled = Counter(tuple(c) for i in chosen for c in cands[i]["cells"] if tuple(c) in short)
    still = {c: short[c] - filled[c] for c in short if filled[c] < short[c]}
    hours = sum(cands[i]["hours"] for i in chosen)
    sizes = (f"{min(cands[i]['functions'] for i in chosen)}–{max(cands[i]['functions'] for i in chosen)} functions, largest peak by the "
             f"fit ≈ {max(cands[i]['peak_gb'] for i in chosen):.1f} GB") if chosen else "none chosen"
    out = {"target": target, "wall_model": wall, "peak_model": peak, "short_cells": len(short), "candidates": len(cands), "chosen": chosen,
           "hours": hours, "still_short": [[list(c), k] for c, k in sorted(still.items())]}
    lines = [f"# Cation candidates for the cation cells short of {target}", "",
             f"Priced on {len(runs)} analytic UKS cation runs on the laptop (6 threads, {min(functions.values())}–{max(functions.values())} "
             f"6-31G* functions): wall s = e^{wall[0]:.2f} n^{wall[1]:.2f}, peak GB = e^{peak[0]:.2f} n^{peak[1]:.2f}.", "",
             f"{len(short)} cation cells short ({sum(short.values())} places); {len(cands)} candidates. **{len(chosen)} cations, ≈ {hours:,.0f} laptop "
             f"hours**, {sizes}. {len(still)} cells stay short ({sum(still.values())} places). A cation cell no manifest row covers is "
             "not counted as short (the fill list's cells).", "",
             "| adjacency | ring context | aza | still short | candidates |", "|---|---|---|---|---|"]
    members = ap.cell_members(cands)
    lines += [f"| {c[0]} | {c[1]} | {'yes' if c[2] else 'no'} | {k} | {len(members.get(c, []))} |" for c, k in sorted(still.items(), key=lambda x: -x[1])]
    return out, lines


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("action", choices=["fill", "mp2", "cations"])
    p.add_argument("--target", type=int, default=30, help="cations: computed molecules per cell (decision 52)")
    a = p.parse_args(argv)
    src = Sources()
    if a.action == "fill":
        out, lines = fill_price(src)
    elif a.action == "mp2":
        out, lines = mp2_price(src)
    else:
        out, lines = cation_price(src, a.target)
    ap.write_text(ap.OUT / f"price_{a.action}.json", json.dumps(out, indent=1, default=str))
    ap.write_text(ap.OUT / f"price_{a.action}.md", "\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
