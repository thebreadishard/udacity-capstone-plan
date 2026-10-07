"""Seed means of T3 leave-one-anchor-out records (`m05/rungC_cc_transfer.py` json files), per held-out anchor and column — the mechanical read for
lever 1 (chain 33's lines of 3 Oct: naphthalene's ring-ip ω, α-tuned, with four training anchors; the all-mode ω and the ring-coupling ratio beside it).

    python probes/t3_seed_means.py "<glob of seed jsons>" [--label NAME] [--columns network_alpha,network_head_l2] [--json out.json]

Several globs may be given; each prints its own table so two anchor sets or two model chains sit side by side."""
from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path

import numpy as np

NAMES = {"A_8448043181": "benzene", "A_01f3186607": "naphthalene", "A_6e858b26e5": "pyridine", "B_8b12a55d3a": "fluorobenzene",
         "A_a1e6ec1862": "anthracene", "A_fdc27f1bd1": "benzonitrile"}
FAMILIES = ("ring-ip", "CH-stretch", "CH-oop", "other")


def read_set(pattern: str):
    files = sorted(glob.glob(pattern))
    if not files:
        raise SystemExit(f"no files match {pattern}")
    recs = [json.loads(Path(f).read_text(encoding="utf-8")) for f in files]
    anchors = sorted(recs[0]["folds"])
    return files, recs, anchors


def table(recs, anchors, columns):
    rows = {}
    for a in anchors:
        for col in columns:
            vals = [r["folds"][a][col] for r in recs if a in r["folds"] and col in r["folds"][a]]
            if not vals:
                continue
            fam = {f: float(np.mean([v["freq_rms_by_family"].get(f, np.nan) for v in vals])) for f in FAMILIES}
            rows[(a, col)] = dict(n_seeds=len(vals), all=float(np.mean([v["corrected_freq_rms"] for v in vals])),
                                  ratio=float(np.mean([v["coupling_ratio"] for v in vals])), **fam,
                                  spread_ring=float(np.ptp([v["freq_rms_by_family"].get("ring-ip", np.nan) for v in vals])) if len(vals) > 1 else 0.0)
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("patterns", nargs="+")
    ap.add_argument("--columns", default="network_alpha,network_head_l2")
    ap.add_argument("--json", default=None)
    a = ap.parse_args()
    columns = a.columns.split(",")
    out = {}
    for pat in a.patterns:
        files, recs, anchors = read_set(pat)
        rows = table(recs, anchors, columns)
        n_train = len(recs[0]["folds"][anchors[0]]["train"])
        print(f"\n## {pat}  ({len(files)} seeds; {n_train} training anchors per fold; model {Path(recs[0]['model']).name})")
        print("| held-out | column | ring-ip | CH-stretch | CH-oop | other | all | ratio | ring-ip seed range |")
        print("|---|---|---|---|---|---|---|---|---|")
        for (anc, col), r in rows.items():
            print(f"| {NAMES.get(anc, anc)} | {col} | {r['ring-ip']:.2f} | {r['CH-stretch']:.2f} | {r['CH-oop']:.2f} | {r['other']:.2f} | {r['all']:.2f} | "
                  f"{r['ratio']:.3f} | {r['spread_ring']:.2f} |")
        out[pat] = {f"{anc}|{col}": r for (anc, col), r in rows.items()}
    if a.json:
        Path(a.json).write_text(json.dumps(out, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
