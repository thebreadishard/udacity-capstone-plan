"""Export every complete corpus molecule for the pattern-proposer simulation (pre-registration 26 September 2026): Δ₂, the deterministic deck (hash),
the exact responses. Seconds per molecule, desk work.

    python run_export.py <corpus/molecules> <out/exports> [--use-analytic] [--limit N] [--dry-run]

Writes one npz per molecule and `<out>/index.json` (id, layer, split, M, deck hash, in-band share of off-diagonal power)."""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pp import core as C  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("molecules")
    ap.add_argument("out")
    ap.add_argument("--use-analytic", action="store_true")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--dry-run", action="store_true", help="list what would be exported; write nothing")
    a = ap.parse_args()
    root, out = Path(a.molecules), Path(a.out)
    dirs = sorted(d for d in root.iterdir() if (d / "hessian_b3lyp.npz").exists() and (d / "hessian_wb97x.npz").exists())
    if a.limit:
        dirs = dirs[: a.limit]
    print(f"{len(dirs)} complete molecule folders under {root}" + (" (dry run)" if a.dry_run else ""))
    if a.dry_run:
        return 0
    out.mkdir(parents=True, exist_ok=True)
    index, t0 = [], time.time()
    for k, d in enumerate(dirs):
        try:
            e = C.export_molecule(d, a.use_analytic)
        except Exception as ex:  # noqa: BLE001 — a broken folder is reported and skipped, as the E-series does
            print("skip", d.name, repr(ex)[:120])
            continue
        if bool((np.asarray(e["freq_cm"]) < 0).any()):
            print("skip", d.name, "imaginary mode")
            continue
        layer = "A" if d.name.startswith("A_") else ("A2" if d.name.startswith("A2_") else "B")
        f = np.asarray(e["freq_cm"])
        off = np.triu(e["D2"], 1)
        band = np.triu(np.abs(f[:, None] - f[None, :]) <= C.W_BAND_CM, 1)
        tot = np.linalg.norm(off)
        C.save_export(e, out / f"{d.name}.npz")
        index.append(dict(id=d.name, layer=layer, split=C.split_of(d.name, layer), M=e["M"], n_patterns=int(len(e["kinds"])),
                          n_holdout=int(e["holdout"].sum()), deck_hash=e["deck_hash"], inband_share=float((np.linalg.norm(off * band) / tot) ** 2) if tot else 1.0))
        if (k + 1) % 50 == 0:
            print(f"  {k + 1}/{len(dirs)} in {time.time() - t0:.0f} s", flush=True)
    json.dump(dict(built=time.strftime("%Y-%m-%d %H:%M"), source=str(root), use_analytic=a.use_analytic, molecules=index), open(out / "index.json", "w"), indent=1)
    splits = {}
    for r in index:
        splits[r["split"]] = splits.get(r["split"], 0) + 1
    print(f"exported {len(index)} molecules in {time.time() - t0:.0f} s; splits {splits}; -> {out / 'index.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
