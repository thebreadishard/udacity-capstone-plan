"""Paired per-molecule read-out between two orderings of the pattern-proposer simulation (pre-registration of 26 September 2026, lines S1–S2).

The merged summaries report each ordering's median ratio against P0; S2 ("P2 vs P1, ratio ≤ 0.90") is a ratio *between* two learned orderings, so
it is computed here per molecule (same molecule, same seed) and summarised by the median and the fraction of molecules on which A needs fewer energies
than B. Two runs may be compared molecule by molecule as well (e.g. the stage-1 recipe against stage 0 on the same pool), which also gives the control
"P1 against P1" = 1.00 exactly when the scorer did not change.

    python paired_readout.py A.json A_ordering B.json B_ordering [--readout K_off_0p3] [--seeds 0,1,2]

Ordering names take `{s}` for the seed (P2_seed{s}); the same file may be given twice. Output: one markdown table on stdout, per split and seed:
n paired (both orderings reached the level), median ratio A/B, fraction A < B, fraction equal."""
from __future__ import annotations

import argparse
import json

import numpy as np


def load(path):
    return json.load(open(path, encoding="utf-8"))["per_molecule"]


def paired(pa, oa, pb, ob, readout):
    rows = {}
    for mol, va in pa.items():
        vb = pb.get(mol)
        if vb is None or oa not in va or ob not in vb:
            continue
        a, b = va[oa].get(readout), vb[ob].get(readout)
        if a is None or b is None:
            continue
        rows.setdefault(va["split"], []).append((a, b))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("a_json"); ap.add_argument("a_ordering"); ap.add_argument("b_json"); ap.add_argument("b_ordering")
    ap.add_argument("--readout", default="K_off_0p3")
    ap.add_argument("--seeds", default="0,1,2")
    args = ap.parse_args()
    pa, pb = load(args.a_json), load(args.b_json)
    seeds = [s for s in args.seeds.split(",") if s]
    print(f"| readout | split | seed | A | B | n paired | median A/B | A better | equal |")
    print("|---|---|---|---|---|---|---|---|---|")
    for s in seeds:
        oa, ob = args.a_ordering.format(s=s), args.b_ordering.format(s=s)
        for split, pairs in sorted(paired(pa, oa, pb, ob, args.readout).items()):
            arr = np.array(pairs, dtype=float)
            ratio = arr[:, 0] / arr[:, 1]
            better = float(np.mean(arr[:, 0] < arr[:, 1])); equal = float(np.mean(arr[:, 0] == arr[:, 1]))
            print(f"| {args.readout} | {split} | {s} | {oa} | {ob} | {len(arr)} | {np.median(ratio):.2f} | {100*better:.0f} % | {100*equal:.0f} % |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
