"""After the registered read of probes/mp2_proxy_alignment.py (TASKS 11 (c)): per anchor and family, the mean and rms of the CC shifts and of each
candidate's, the anchor's own slope and its leave-one-out residual rms. A diagnosis of the pooled numbers, not a verdict.

    python probes/mp2_proxy_per_anchor.py <the read's json> <family> [<family> …]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mp2_proxy_alignment as M


def rows(records: list[dict], fam: str) -> list[str]:
    """One line per anchor: n, CC mean and rms, and per candidate its mean, rms, own slope and leave-one-out residual rms."""
    names = {**M.D.S3.ORIGINALS, **M.D.S3.NEW}
    cands = (*M.CANDIDATES, M.STONE) if all(M.STONE in r for r in records) else M.CANDIDATES
    parts = []
    for r in records:
        sel = np.array([f == fam for f in r["families"]])
        parts.append((r["mol_id"], np.asarray(r["truth"], float)[sel], {c: np.asarray(r[c], float)[sel] for c in cands}))
    out = [f"== {fam}", f"{'anchor':16s} n  meanCC rmsCC | " + " | ".join(f"{c}: mean rms slope loo" for c in cands)]
    for k, (mid, t, cs) in enumerate(parts):
        line = f"{names.get(mid, mid)[:16]:16s} {len(t):2d} {t.mean():+7.1f} {np.sqrt(np.mean(t ** 2)):5.1f} |"
        for c in cands:
            s = M._slope(np.concatenate([p[1] for j, p in enumerate(parts) if j != k]),
                         np.concatenate([p[2][c] for j, p in enumerate(parts) if j != k]))
            line += (f" {cs[c].mean():+7.1f} {np.sqrt(np.mean(cs[c] ** 2)):6.1f} {M._slope(t, cs[c]):+5.2f} "
                     f"{np.sqrt(np.mean((t - s * cs[c]) ** 2)):5.1f} |")
        out.append(line)
    return out


def main(argv: list[str]) -> int:
    records = json.loads(Path(argv[0]).read_text(encoding="utf-8"))["records"]
    for fam in argv[1:]:
        print("\n".join(rows(records, fam)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
