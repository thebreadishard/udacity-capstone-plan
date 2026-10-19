"""Lever 2 (2 Oct 2026): where does the carried model fail, and which molecules should the next pool contain?

T2 was restated on 2 Oct as coverage, not count (a fixed A+A2 composition gave 0.29 / 0.25 / 0.24 at 45 / 100 / 175 and the carried recipe 0.235 at
449): the per-molecule hold-out errors of the pattern-f hybrid records are joined with the manifest (SMILES → ring count, fusion, ring heteroatoms,
substituent elements → a *kind*; a computed molecule's charge from its job.json, since a pool 3 cation carries its neutral parent's SMILES), averaged
per molecule over seeds and records, and summarised per kind beside the kind's count in the training pool. The weak and uncovered kinds pick the
next-pool candidates from the manifest's pending rows (layers B and C, the wide deck), stratified and capped.

    python probes/rungC_error_map.py [--records 'modules/05_support_predictor/out/E7_rungC_*_2026-10-0*.json'] [--n-next 200] [--max-heavy 14]

Writes <out>/rungC_error_map_<date>.{json,md} and <out>/next_pool_candidates_<date>.csv. Every number comes from the record files named in the json.
"""
from __future__ import annotations

import argparse
import collections
import csv
import glob
import json
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
from corpus_state import recorded_state

PLAN = Path(__file__).resolve().parents[1]
M05 = PLAN / "modules" / "05_support_predictor"
KEYS = ("coupling_ratio", "corrected_freq_rms", "dH_residual_ratio")
REASONS = ("weak+uncovered", "weak", "uncovered", "new-kind")
SHARE = {"weak+uncovered": 0.4, "weak": 0.3, "uncovered": 0.2, "new-kind": 0.1}
UNKNOWN_HEAVY = 99          # a pending row without a heavy-atom count is treated as too large


@dataclass(frozen=True)
class MapSettings:
    """The candidate rule's settings."""
    n_next: int = 200
    max_heavy: int = 19
    layers: tuple[str, ...] = ("A2", "B", "C")
    min_pool: int = 8

    def __post_init__(self) -> None:
        if self.n_next < 1 or self.max_heavy < 1 or self.min_pool < 0 or not self.layers:
            raise ValueError(f"settings out of range: {self}")


def kind_of(smiles: str, charge: int | None = None):
    """A coarse molecular kind from the SMILES: aromatic ring count, fused or not, ring heteroatoms, substituent elements. None when rdkit cannot parse.
    `charge` is the molecule's recorded charge where it was computed (corpus_state.recorded_state); without it, the SMILES's formal charge."""
    from rdkit import Chem
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    ri = mol.GetRingInfo()
    rings = [set(r) for r in ri.AtomRings()]
    arom = sum(1 for r in rings if all(mol.GetAtomWithIdx(i).GetIsAromatic() for i in r))
    in_ring = set().union(*rings) if rings else set()
    fused = any(len(a & b) >= 2 for i, a in enumerate(rings) for b in rings[i + 1:])
    het_ring = sorted({mol.GetAtomWithIdx(i).GetSymbol() for i in in_ring if mol.GetAtomWithIdx(i).GetSymbol() != "C"})
    subst = sorted({a.GetSymbol() for a in mol.GetAtoms() if a.GetIdx() not in in_ring})
    n_sub = sum(1 for a in mol.GetAtoms() if a.GetIdx() not in in_ring)
    charge = Chem.GetFormalCharge(mol) if charge is None else charge
    return dict(n_rings=len(rings), n_arom=arom, fused=fused, het_ring=het_ring, subst=subst, n_sub=n_sub, charge=charge,
                kind=f"{arom}ar{'-fused' if fused else ''}|{'ring-' + ''.join(het_ring) if het_ring else 'carbo'}|sub:{''.join(subst) or 'none'}"
                     + ("|cation" if charge else ""))


def record_errors(path: Path) -> tuple[dict, dict]:
    """Per-molecule errors of the largest size of one record, averaged over seeds, keyed by (set, id); and the record's pool ids."""
    with open(path, encoding="utf-8") as fh:
        r = json.load(fh)
    if r.get("head") != "hybrid" or r.get("pattern") != "f" or r.get("smoke"):
        return {}, {}
    n = max(r["curve"], key=int)
    acc = collections.defaultdict(list)
    for seed in r["curve"][n]["per_seed"]:
        for hold in ("a", "b"):
            for i, v in (seed[hold].get("per_molecule") or {}).items():
                acc[(hold, i)].append([v[k] for k in KEYS])
    return {k: np.mean(v, axis=0) for k, v in acc.items()}, {"pool_ids": r.get("pool_ids", []), "n": int(n), "file": path.name}


def read_kinds(rows: dict[str, dict]) -> dict[str, dict]:
    """Per manifest row with a parsable SMILES, its kind; a computed row's charge is its recorded one (a pool 3 cation's SMILES is neutral)."""
    kinds = {}
    for i, r in rows.items():
        recorded = recorded_state(i)[0] if r["status"] == "done" else None
        k = kind_of(r["smiles"], recorded) if r.get("smiles") else None
        if k:
            kinds[i] = k
    return kinds


def load_records(pattern: str) -> list[tuple[dict, dict]]:
    per_rec = [record_errors(Path(p)) for p in sorted(glob.glob(pattern))]
    per_rec = [(e, meta) for e, meta in per_rec if e]
    if not per_rec:
        raise SystemExit(f"no pattern-f hybrid records match {pattern}")
    return per_rec


def mean_per_molecule(per_rec: list[tuple[dict, dict]]) -> dict:
    acc = collections.defaultdict(list)
    for e, _ in per_rec:
        for key, v in e.items():
            acc[key].append(v)
    return {key: np.mean(v, axis=0) for key, v in acc.items()}


def kind_table(per_mol: dict, kinds: dict, rows: dict, pool_kind: collections.Counter) -> list[dict]:
    """Per kind of the held-out molecules: count, sets, pool count, mean errors and the three worst; sorted by ring-coupling ratio, worst first."""
    by_kind = collections.defaultdict(list)
    for (hold, i), v in per_mol.items():
        by_kind[kinds[i]["kind"] if i in kinds else "unparsed"].append((hold, i, v))
    table = []
    for kind, items in by_kind.items():
        V = np.array([v for _, _, v in items])
        table.append(dict(kind=kind, n_holdout=len(items), sets="".join(sorted({h for h, _, _ in items})), pool_count=pool_kind.get(kind, 0),
                          coupling_ratio=float(V[:, 0].mean()), omega=float(V[:, 1].mean()), dH_ratio=float(V[:, 2].mean()),
                          worst=sorted(((float(v[0]), i, rows[i]["name"]) for _, i, v in items), reverse=True)[:3]))
    table.sort(key=lambda t: -t["coupling_ratio"])
    return table


def reason_for(kind: str, weak: set, uncovered: set, pool_kind: collections.Counter) -> str | None:
    if kind in weak and kind in uncovered:
        return "weak+uncovered"
    if kind in weak:
        return "weak"
    if kind in uncovered:
        return "uncovered"
    return "new-kind" if kind not in pool_kind else None


def choose_candidates(rows: dict, kinds: dict, weak: set, uncovered: set, pool_kind: collections.Counter,
                      s: MapSettings) -> tuple[list[dict], list[dict]]:
    """Pending rows of the layers within the heavy-atom cap whose kind is weak, uncovered or new, by reason quotas; (chosen, pending)."""
    pending = [r for i, r in rows.items()
               if r["status"] == "pending" and r["layer"] in s.layers and int(r["n_heavy"] or UNKNOWN_HEAVY) <= s.max_heavy and i in kinds]
    buckets = collections.defaultdict(list)
    for r in pending:
        k = kinds[r["id"]]["kind"]
        reason = reason_for(k, weak, uncovered, pool_kind)
        if reason:
            buckets[(reason, k)].append(r)
    chosen = []
    for reason in REASONS:
        ks = [k for (rs, k) in buckets if rs == reason]
        if not ks:
            continue
        per_kind = max(1, round(s.n_next * SHARE[reason]) // len(ks))
        for k in ks:
            cands = sorted(buckets[(reason, k)], key=lambda r: (int(r["n_heavy"]), r["id"]))
            chosen += [dict(id=r["id"], name=r["name"], smiles=r["smiles"], layer=r["layer"], n_heavy=r["n_heavy"], kind=k, reason=reason)
                       for r in cands[:per_kind]]
    return chosen[:s.n_next], pending


def report_lines(res: dict[str, Any], n_records: int, stamp: str, s: MapSettings) -> list[str]:
    lines = [f"# Error map of the pattern-f hybrid records ({res['date']})", "",
             f"{n_records} records (largest size each: {sorted(set(res['sizes']))}), per-molecule errors averaged over seeds and records; pool of "
             f"{res['n_pool']} molecules. Kind = aromatic rings, fusion, ring heteroatoms, substituent elements (rdkit on the manifest SMILES).", "",
             "| kind | hold-out n (sets) | pool count | ring-coupling ratio | ω rms (cm⁻¹) | ΔH residual | worst molecules (ratio) |",
             "|---|---|---|---|---|---|---|"]
    for t in res["table"]:
        lines.append(f"| {t['kind']} | {t['n_holdout']} ({t['sets']}) | {t['pool_count']} | {t['coupling_ratio']:.2f} | {t['omega']:.1f} | "
                     f"{t['dH_ratio']:.2f} | " + ", ".join(f"{n} {r:.2f}" for r, _, n in t["worst"]) + " |")
    chosen = res["chosen"]
    lines += ["", f"Median kind ratio {res['median_kind_ratio']:.2f}; weak kinds (≥ median): {len(res['weak'])}; uncovered kinds (pool < {s.min_pool}): "
              f"{len(res['uncovered'])}.",
              f"Next-pool candidates: {len(chosen)} of {res['n_pending_considered']} pending rows of layers {','.join(s.layers)} with ≤ {s.max_heavy} heavy "
              "atoms, by reason: " + ", ".join(f"{r} {sum(1 for c in chosen if c['reason'] == r)}" for r in REASONS)
              + f" → `next_pool_candidates_{stamp}.csv`."]
    return lines


def write_outputs(out: Path, stamp: str, res: dict[str, Any], lines: list[str]) -> None:
    with open(out / f"rungC_error_map_{stamp}.json", "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1, ensure_ascii=False)
    with open(out / f"next_pool_candidates_{stamp}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id", "name", "smiles", "layer", "n_heavy", "kind", "reason"])
        w.writeheader()
        w.writerows(res["chosen"])
    (out / f"rungC_error_map_{stamp}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--records", default=str(M05 / "out" / "E7_rungC_*_2026-10-0*.json"))
    ap.add_argument("--manifest", default=str(M05 / "corpus" / "manifest.csv"))
    ap.add_argument("--out", default=str(M05 / "out"))
    ap.add_argument("--n-next", type=int, default=200)
    ap.add_argument("--max-heavy", type=int, default=19, help="cost cap on the next pool (heavy atoms); 19 admits the four-ring A2 rows (pyrene+X, 17–19)")
    ap.add_argument("--layers", default="A2,B,C",
                    help="manifest layers whose pending rows are candidates (A2 holds the 441 three-ring and 93 four-ring pending rows)")
    ap.add_argument("--min-pool", type=int, default=8, help="a kind with fewer training molecules than this counts as uncovered")
    a = ap.parse_args()
    s = MapSettings(n_next=a.n_next, max_heavy=a.max_heavy, layers=tuple(a.layers.split(",")), min_pool=a.min_pool)
    stamp = datetime.now().strftime("%Y-%m-%d")
    with open(a.manifest, encoding="utf-8") as fh:
        rows = {r["id"]: r for r in csv.DictReader(fh)}
    kinds = read_kinds(rows)
    per_rec = load_records(a.records)
    pool_ids = sorted({i for _, meta in per_rec for i in meta["pool_ids"]})
    pool_kind = collections.Counter(kinds[i]["kind"] for i in pool_ids if i in kinds)
    per_mol = mean_per_molecule(per_rec)
    table = kind_table(per_mol, kinds, rows, pool_kind)
    med = float(np.median([t["coupling_ratio"] for t in table]))
    weak = {t["kind"] for t in table if t["coupling_ratio"] >= med}
    uncovered = {t["kind"] for t in table if t["pool_count"] < s.min_pool}
    chosen, pending = choose_candidates(rows, kinds, weak, uncovered, pool_kind, s)
    res = dict(date=datetime.now().strftime("%Y-%m-%d %H:%M"), records=[m["file"] for _, m in per_rec], sizes=[m["n"] for _, m in per_rec],
               n_pool=len(pool_ids), median_kind_ratio=med, min_pool=s.min_pool, max_heavy=s.max_heavy, layers=sorted(set(s.layers)), table=table,
               weak=sorted(weak), uncovered=sorted(uncovered), n_pending_considered=len(pending), chosen=chosen,
               per_molecule={f"{h}:{i}": dict(zip(KEYS, map(float, v), strict=True), kind=kinds.get(i, {}).get("kind"), name=rows[i]["name"])
                             for (h, i), v in per_mol.items()})
    lines = report_lines(res, len(per_rec), stamp, s)
    write_outputs(Path(a.out), stamp, res, lines)
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
