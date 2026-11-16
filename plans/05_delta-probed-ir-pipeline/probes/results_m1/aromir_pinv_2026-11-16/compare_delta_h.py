"""Two files of `aromir_delta_h.py` against each other: per molecule the largest ΔH difference and band difference (TASKS 236).

    python compare_delta_h.py <a.npz> <b.npz> <out.json> [--ids <file>] [--show N]

The record holds every molecule; the screen shows the N worst and the summary. Nothing is asserted here: the tolerance is stated
where the numbers are used.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import numpy as np


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("a", type=Path)
    ap.add_argument("b", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--ids", type=Path, default=None, help="compare only these molecules")
    ap.add_argument("--show", type=int, default=5)
    args = ap.parse_args()
    rows = []
    with np.load(args.a) as a, np.load(args.b) as b:
        ids = sorted({key.split("/")[0] for key in a.files} & {key.split("/")[0] for key in b.files})
        if args.ids is not None:
            wanted = args.ids.read_text(encoding="utf-8").split()
            missing = sorted(set(wanted) - set(ids))
            if missing:
                raise SystemExit(f"not in both files: {missing}")
            ids = wanted
        for molecule_id in ids:
            dh_a, dh_b = a[f"{molecule_id}/delta_h"], b[f"{molecule_id}/delta_h"]
            bands = np.abs(a[f"{molecule_id}/bands_cm"] - b[f"{molecule_id}/bands_cm"])
            rows.append({"id": molecule_id,
                         "max_abs_delta_h_a": float(np.abs(dh_a).max()), "max_abs_delta_h_b": float(np.abs(dh_b).max()),
                         "max_abs_delta_h_difference": float(np.abs(dh_a - dh_b).max()),
                         # missing bands (an exploded Hessian without eigenvalues) count as an infinite difference
                         "max_band_difference_cm": float(bands.max()) if np.isfinite(bands).all() else float("inf")})
    worst_dh = max(rows, key=lambda r: r["max_abs_delta_h_difference"])
    worst_band = max(rows, key=lambda r: r["max_band_difference_cm"])
    record = {"a": args.a.name, "b": args.b.name, "n_molecules": len(rows),
              "largest_delta_h_difference": worst_dh, "largest_band_difference_cm": worst_band,
              "n_band_difference_above_1e-3_cm": sum(r["max_band_difference_cm"] > 1e-3 for r in rows), "molecules": rows}
    tmp = args.out.with_name(args.out.name + ".tmp")
    tmp.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    os.replace(tmp, args.out)
    print(f"{args.a.name} against {args.b.name}: {len(rows)} molecules")
    for r in sorted(rows, key=lambda r: -r["max_band_difference_cm"])[:args.show]:
        print(f"  {r['id']:<16} max|dH| {r['max_abs_delta_h_a']:.4g} / {r['max_abs_delta_h_b']:.4g}  "
              f"max|dH difference| {r['max_abs_delta_h_difference']:.3e}  bands {r['max_band_difference_cm']:.3e} cm-1")
    print(f"  largest |dH difference| {worst_dh['max_abs_delta_h_difference']:.3e} ({worst_dh['id']}); largest band difference "
          f"{worst_band['max_band_difference_cm']:.3e} cm-1 ({worst_band['id']}); "
          f"{record['n_band_difference_above_1e-3_cm']} of {len(rows)} molecules differ by more than 1e-3 cm-1")


if __name__ == "__main__":
    main()
