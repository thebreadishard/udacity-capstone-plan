"""The second route of TASKS 112's reading 1 (the noise principle: every derived quantity gets a second route): S3's error per family recomputed
directly as (f − 1) ω − K_ii pooled over the record's molecules, without `E6.readout`, with the zero rule (rms of K_ii itself) and the mean and
spread of the shift per family as context. Reads the factors and molecule ids from `out/scale_factor_baseline_2026-10-25.json`.

    python probes/scale_factor_baseline_second_route.py      → one line per hold-out and family on stdout
"""
from __future__ import annotations

import json
import sys

import numpy as np
from scale_factor_baseline import FAMILIES, M05, OUT, load_corpus, pahdb_region

TOLERANCE_CM = 0.01


def family_shifts(mols: dict, ids: list[str], factors: dict[int, float]) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    """Per family, (S3's error, the true shift K_ii) over every mode of `ids`."""
    err: dict[str, list[float]] = {}
    true: dict[str, list[float]] = {}
    for i in ids:
        m = mols[i]
        w = np.asarray(m["freq"], float)
        k = np.diag(m["K"]).astype(float)
        pred = (np.array([factors[int(r)] for r in pahdb_region(m)]) - 1.0) * w
        for fam, e, kk in zip(m["family"], pred - k, k, strict=True):
            err.setdefault(fam, []).append(float(e))
            true.setdefault(fam, []).append(float(kk))
    return {f: (np.array(err[f]), np.array(true[f])) for f in err}


def main() -> int:
    res = json.loads(OUT.with_suffix(".json").read_text(encoding="utf-8"))
    factors = {int(k): v for k, v in res["factors"]["S3"].items()}
    mols, *_ = load_corpus(str(M05 / "corpus" / "molecules"), use_analytic=True, log=lambda *_: None)
    worst = 0.0
    for h, r in res["holdouts"].items():
        shifts = family_shifts(mols, r["ids"], factors)
        for fam in FAMILIES:
            e, k = shifts[fam]
            direct = float(np.sqrt(np.mean(e ** 2)))
            worst = max(worst, abs(direct - r["S3"][fam]))
            print(f"({h}) {fam:10s} S3 direct {direct:6.2f} (record {r['S3'][fam]:6.2f})  zero rule {np.sqrt(np.mean(k ** 2)):6.2f}  "
                  f"mean shift {k.mean():+6.2f}  sd {k.std():5.2f}  modes {len(k)}")
    print(f"largest difference to the record: {worst:.4f} cm⁻¹ ({'agrees' if worst <= TOLERANCE_CM else 'DISAGREES'} within {TOLERANCE_CM})")
    return 0 if worst <= TOLERANCE_CM else 1


if __name__ == "__main__":
    sys.exit(main())
