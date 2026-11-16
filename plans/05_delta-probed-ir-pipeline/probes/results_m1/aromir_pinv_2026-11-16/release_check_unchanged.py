"""The release check of 15 Nov against its re-run with the rank-based B⁺: every seed's max|ΔH| side by side (TASKS 236).

    python release_check_unchanged.py <delta_h_compare.json of 15 Nov> <delta_h_compare_fixed.json>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> None:
    before = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    after = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    if before["tensor_sha256"] != after["tensor_sha256"]:
        raise SystemExit("the two records are not of the same weights")
    largest = 0.0
    for old, new in zip(before["molecules"], after["molecules"], strict=True):
        for seed_old, seed_new in zip(old["seeds"], new["seeds"], strict=True):
            change = abs(seed_old["max_abs_delta_h"] - seed_new["max_abs_delta_h"])
            largest = max(largest, change, seed_new["max_abs_difference"])
            print(f"{old['id']} {seed_old['model'][-8:]}: max|dH| 15 Nov {seed_old['max_abs_delta_h']:.10f}, now "
                  f"{seed_new['max_abs_delta_h']:.10f}, change {change:.1e}; aromir - trainer now {seed_new['max_abs_difference']:.1e}, "
                  f"bands {seed_new['max_band_difference_cm']:.1e} cm-1")
    print(f"largest change or difference: {largest:.1e} hartree/bohr2 (tolerance of the release check: 1e-6)")


if __name__ == "__main__":
    main()
