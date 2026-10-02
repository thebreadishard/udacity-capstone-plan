"""Lever 2 (2 Oct 2026): where does the carried model fail, and which molecules should the next pool contain?

T2 was restated on 2 Oct as coverage, not count (a fixed A+A2 composition gave 0.29 / 0.25 / 0.24 at 45 / 100 / 175 and the carried recipe 0.235 at
449): the per-molecule hold-out errors of the pattern-f hybrid records are joined with the manifest (SMILES → ring count, fusion, ring heteroatoms,
substituent elements → a *kind*), averaged per molecule over seeds and records, and summarised per kind beside the kind's count in the training pool.
The weak and uncovered kinds pick the next-pool candidates from the manifest's pending rows (layers B and C, the wide deck), stratified and capped.

    python probes/rungC_error_map.py [--records 'modules/05_support_predictor/out/E7_rungC_*_2026-10-0*.json'] [--n-next 200] [--max-heavy 14]

Writes <out>/rungC_error_map_<date>.{json,md} and <out>/next_pool_candidates_<date>.csv. Every number comes from the record files named in the json.
"""
import argparse
import collections
import csv
import glob
import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np

PLAN = Path(__file__).resolve().parents[1]
M05 = PLAN / "modules" / "05_support_predictor"
KEYS = ("coupling_ratio", "corrected_freq_rms", "dH_residual_ratio")


def kind_of(smiles: str):
    """A coarse molecular kind from the SMILES: aromatic ring count, fused or not, ring heteroatoms, substituent elements. None when rdkit cannot parse."""
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
    charge = Chem.GetFormalCharge(mol)
    return dict(n_rings=len(rings), n_arom=arom, fused=fused, het_ring=het_ring, subst=subst, n_sub=n_sub, charge=charge,
                kind=f"{arom}ar{'-fused' if fused else ''}|{'ring-' + ''.join(het_ring) if het_ring else 'carbo'}|sub:{''.join(subst) or 'none'}"
                     + ("|cation" if charge else ""))


def record_errors(path: Path) -> tuple[dict, dict]:
    """Per-molecule errors of the largest size of one record, averaged over seeds, keyed by (set, id); and the record's pool ids."""
    r = json.load(open(path, encoding="utf-8"))
    if r.get("head") != "hybrid" or r.get("pattern") != "f" or r.get("smoke"):
        return {}, {}
    n = max(r["curve"], key=int)
    acc = collections.defaultdict(list)
    for seed in r["curve"][n]["per_seed"]:
        for hold in ("a", "b"):
            for i, v in (seed[hold].get("per_molecule") or {}).items():
                acc[(hold, i)].append([v[k] for k in KEYS])
    return {k: np.mean(v, axis=0) for k, v in acc.items()}, {"pool_ids": r.get("pool_ids", []), "n": int(n), "file": path.name}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--records", default=str(M05 / "out" / "E7_rungC_*_2026-10-0*.json"))
    ap.add_argument("--manifest", default=str(M05 / "corpus" / "manifest.csv"))
    ap.add_argument("--out", default=str(M05 / "out"))
    ap.add_argument("--n-next", type=int, default=200)
    ap.add_argument("--max-heavy", type=int, default=19, help="cost cap on the next pool (heavy atoms); 19 admits the four-ring A2 rows (pyrene+X, 17–19)")
    ap.add_argument("--layers", default="A2,B,C", help="manifest layers whose pending rows are candidates (A2 holds the 441 three-ring and 93 four-ring pending rows)")
    ap.add_argument("--min-pool", type=int, default=8, help="a kind with fewer training molecules than this counts as uncovered")
    a = ap.parse_args()
    stamp = datetime.now().strftime("%Y-%m-%d")
    rows = {r["id"]: r for r in csv.DictReader(open(a.manifest, encoding="utf-8"))}
    kinds = {}
    for i, r in rows.items():
        k = kind_of(r["smiles"]) if r.get("smiles") else None
        if k:
            kinds[i] = k
    per_rec = [record_errors(Path(p)) for p in sorted(glob.glob(a.records))]
    per_rec = [(e, meta) for e, meta in per_rec if e]
    if not per_rec:
        raise SystemExit(f"no pattern-f hybrid records match {a.records}")
    pool = collections.Counter()
    for _, meta in per_rec:
        for i in meta["pool_ids"]:
            pool[i] += 1
    pool_ids = sorted(pool)
    pool_kind = collections.Counter(kinds[i]["kind"] for i in pool_ids if i in kinds)
    acc = collections.defaultdict(list)
    for e, _ in per_rec:
        for key, v in e.items():
            acc[key].append(v)
    per_mol = {key: np.mean(v, axis=0) for key, v in acc.items()}
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
    med = float(np.median([t["coupling_ratio"] for t in table]))
    weak = {t["kind"] for t in table if t["coupling_ratio"] >= med}
    uncovered = {t["kind"] for t in table if t["pool_count"] < a.min_pool}
    # next-pool candidates: pending rows (layers B, C) whose kind is weak or uncovered — and kinds absent from the pool altogether, in smaller share
    layers = set(a.layers.split(","))
    pending = [r for i, r in rows.items() if r["status"] == "pending" and r["layer"] in layers and int(r["n_heavy"] or 99) <= a.max_heavy and i in kinds]
    buckets = collections.defaultdict(list)
    for r in pending:
        k = kinds[r["id"]]["kind"]
        reason = ("weak+uncovered" if k in weak and k in uncovered else "weak" if k in weak else "uncovered" if k in uncovered else
                  "new-kind" if k not in pool_kind else None)
        if reason:
            buckets[(reason, k)].append(r)
    order = ["weak+uncovered", "weak", "uncovered", "new-kind"]
    share = {"weak+uncovered": 0.4, "weak": 0.3, "uncovered": 0.2, "new-kind": 0.1}
    chosen = []
    for reason in order:
        ks = [k for (rs, k) in buckets if rs == reason]
        if not ks:
            continue
        quota = int(round(a.n_next * share[reason]))
        per_kind = max(1, quota // len(ks))
        for k in ks:
            cands = sorted(buckets[(reason, k)], key=lambda r: (int(r["n_heavy"]), r["id"]))
            chosen += [dict(id=r["id"], name=r["name"], smiles=r["smiles"], layer=r["layer"], n_heavy=r["n_heavy"], kind=k, reason=reason) for r in cands[:per_kind]]
    chosen = chosen[:a.n_next]
    out = Path(a.out)
    res = dict(date=datetime.now().strftime("%Y-%m-%d %H:%M"), records=[m["file"] for _, m in per_rec], sizes=[m["n"] for _, m in per_rec], n_pool=len(pool_ids),
               median_kind_ratio=med, min_pool=a.min_pool, max_heavy=a.max_heavy, layers=sorted(layers), table=table, weak=sorted(weak), uncovered=sorted(uncovered),
               n_pending_considered=len(pending), chosen=chosen,
               per_molecule={f"{h}:{i}": dict(zip(KEYS, map(float, v)), kind=kinds.get(i, {}).get("kind"), name=rows[i]["name"]) for (h, i), v in per_mol.items()})
    json.dump(res, open(out / f"rungC_error_map_{stamp}.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    with open(out / f"next_pool_candidates_{stamp}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id", "name", "smiles", "layer", "n_heavy", "kind", "reason"])
        w.writeheader()
        w.writerows(chosen)
    lines = [f"# Error map of the pattern-f hybrid records ({res['date']})", "",
             f"{len(per_rec)} records (largest size each: {sorted(set(res['sizes']))}), per-molecule errors averaged over seeds and records; pool of {len(pool_ids)} molecules. "
             f"Kind = aromatic rings, fusion, ring heteroatoms, substituent elements (rdkit on the manifest SMILES).", "",
             "| kind | hold-out n (sets) | pool count | ring-coupling ratio | ω rms (cm⁻¹) | ΔH residual | worst molecules (ratio) |", "|---|---|---|---|---|---|---|"]
    for t in table:
        lines.append(f"| {t['kind']} | {t['n_holdout']} ({t['sets']}) | {t['pool_count']} | {t['coupling_ratio']:.2f} | {t['omega']:.1f} | {t['dH_ratio']:.2f} | "
                     + ", ".join(f"{n} {r:.2f}" for r, _, n in t["worst"]) + " |")
    lines += ["", f"Median kind ratio {med:.2f}; weak kinds (≥ median): {len(weak)}; uncovered kinds (pool < {a.min_pool}): {len(uncovered)}.",
              f"Next-pool candidates: {len(chosen)} of {len(pending)} pending rows of layers {a.layers} with ≤ {a.max_heavy} heavy atoms, by reason: "
              + ", ".join(f"{r} {sum(1 for c in chosen if c['reason'] == r)}" for r in order) + f" → `next_pool_candidates_{stamp}.csv`."]
    (out / f"rungC_error_map_{stamp}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
