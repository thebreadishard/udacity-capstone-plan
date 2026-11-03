"""Read TASKS 156 (c): is imidazole+CH3's NOISY flag grid noise, like styrene's vinyl, or the methyl torsion's large amplitude?

The reading rule, written before the fine Hessians (3 Nov 2026), on probes/qff_grid_recheck.py's record of the seven modes:
  control  the coarse grid's largest route disagreement reproduces S2's 5.63 cm⁻¹ within CONTROL_CM (the same Hessians, the same formulas);
  GRID NOISE        the fine grid's largest disagreement is at most NOISE_SHARE of the coarse one;
  LARGE AMPLITUDE   it stays at TORSION_SHARE of the coarse one or more: the torsion itself, and the rotor policy then matters;
  MIXED             in between: neither reading.
Styrene's read of 17 Oct by the same measure: 10.65 → 2.05 cm⁻¹ (share 0.19), grid noise.

    python probes/s2_gridcheck_methyl_read.py <grid_recheck.json>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

S2_COARSE_MAX_CM = 5.63
CONTROL_CM = 0.05
NOISE_SHARE = 0.5
TORSION_SHARE = 0.75


def verdict(rec: dict) -> tuple[str, float]:
    """The reading and the fine-to-coarse share of the largest route disagreement."""
    coarse, fine = rec["max_disagreement"]["coarse"], rec["max_disagreement"]["fine"]
    if abs(coarse - S2_COARSE_MAX_CM) > CONTROL_CM:
        return f"CONTROL FAILED: coarse max {coarse:.2f} against S2's {S2_COARSE_MAX_CM}", fine / coarse
    share = fine / coarse
    if share <= NOISE_SHARE:
        return "GRID NOISE", share
    if share >= TORSION_SHARE:
        return "LARGE AMPLITUDE", share
    return "MIXED", share


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    with Path(sys.argv[1]).open(encoding="utf-8") as handle:
        rec = json.load(handle)
    reading, share = verdict(rec)
    md = rec["max_disagreement"]
    print(f"imidazole+CH3, modes {rec['modes']}: largest route disagreement {md['coarse']:.2f} cm⁻¹ at 75/302, {md['fine']:.2f} at 99/590 "
          f"(share {share:.2f})")
    for r in sorted(rec["pairs"], key=lambda r: -r["coarse"]["disagreement"])[:8]:
        print(f"  pair {r.get('pair', (r.get('i'), r.get('j')))}: {r['coarse']['disagreement']:.2f} → {r['fine']['disagreement']:.2f}")
    print("VERDICT:", reading)


if __name__ == "__main__":
    main()
