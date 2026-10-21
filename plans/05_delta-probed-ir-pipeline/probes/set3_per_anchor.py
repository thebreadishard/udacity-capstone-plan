"""Set-three diagnosis: per anchor, the CH-oop and 'other' ω rms and the matched intensity error of chosen runs against the zero rule
(exploratory; R-B's anchors are pyridine, fluorobenzene, benzonitrile). JSON only.

    python probes/set3_per_anchor.py <out_dir> <run stem> [<run stem> ...]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import set3_diagnosis as D


def main(out_dir: Path, stems: list[str]) -> int:
    names = {**D.S3.ORIGINALS, **D.S3.NEW}
    for stem in stems:
        exp = stem.rsplit("_seed", 1)[0]
        folds = json.loads((out_dir / f"{stem}.json").read_text(encoding="utf-8"))["folds"]
        col = D.column(exp)
        below = [i for i in D.S3.LOW_SYMMETRY if i in folds and "intensity" in folds[i][col]
                 and folds[i][col]["intensity"][D.S3.MATCHED] < folds[i]["zero_rule"]["intensity"][D.S3.MATCHED]]
        print(f"== {stem}: R-B's three below the zero rule on {len(below)} of 3")
        for i, f in folds.items():
            fam, z = f[col]["freq_rms_by_family"], f["zero_rule"]["freq_rms_by_family"]
            inten = f"{f[col]['intensity'][D.S3.MATCHED]:.3f} / {f['zero_rule']['intensity'][D.S3.MATCHED]:.3f}" if "intensity" in f[col] else "—"
            print(f"  {names[i]:15s} CH-oop {fam.get('CH-oop', float('nan')):5.1f} (zero {z.get('CH-oop', float('nan')):5.1f})  other "
                  f"{fam.get('other', float('nan')):5.1f} (zero {z.get('other', float('nan')):5.1f})  intensity {inten}")
    return 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1]).resolve(), sys.argv[2:]))
