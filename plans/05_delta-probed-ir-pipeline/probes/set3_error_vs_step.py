"""Set-three diagnosis, A8 (21 Oct 2026): does the network's out-of-plane error per anchor follow the size of that anchor's composite basis
step (TZ − DZ) or of its method part (CC/DZ − B3LYP)? A large step means the anchor's truth there rests on the MP2 step's accuracy (test 2 on
benzene: the composite 7.3 cm⁻¹ from full CC/TZ in CH-oop). Reads E01's record (λ = 1, every anchor a fold) and A7's decompose.json; numpy.

    python probes/set3_error_vs_step.py <out_dir>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
import set3_diagnosis as D  # noqa: E402


def main(out_dir: Path) -> int:
    rec = json.loads((out_dir / "E01_ref_lambda1_seed0.json").read_text(encoding="utf-8"))["folds"]
    dec = json.loads((out_dir / "decompose.json").read_text(encoding="utf-8"))
    names = {**D.S3.ORIGINALS, **D.S3.NEW}
    for fam in ("CH-oop", "other"):
        rows = [(names[i], f[D.column("E01_ref_lambda1")]["freq_rms_by_family"][fam], f["zero_rule"]["freq_rms_by_family"][fam],
                 dec[names[i]][fam]["basis step (TZ - DZ)"]["rms"], dec[names[i]][fam]["total"]["rms"])
                for i, f in rec.items() if names[i] in dec and fam in dec[names[i]]]
        err, zero, step, total = (np.array([r[k] for r in rows]) for k in (1, 2, 3, 4))
        print(f"== {fam}: n {len(rows)}; corr(network error, basis step rms) {np.corrcoef(err, step)[0, 1]:+.2f}; "
              f"corr(network error, correction rms) {np.corrcoef(err, total)[0, 1]:+.2f}; corr(zero-rule error, correction rms) "
              f"{np.corrcoef(zero, total)[0, 1]:+.2f}")
        for r in sorted(rows, key=lambda r: -r[1]):
            print(f"  {r[0]:15s} network {r[1]:5.1f}  zero rule {r[2]:5.1f}  step rms {r[3]:5.1f}  correction rms {r[4]:5.1f}")
    return 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1]).resolve()))
