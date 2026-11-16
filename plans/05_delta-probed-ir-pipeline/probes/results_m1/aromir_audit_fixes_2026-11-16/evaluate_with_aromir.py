"""Run aromir's own evaluation of its bundled release on a folder of hold-outs and write what it measures (TASKS 243).

    python evaluate_with_aromir.py <hold-out folder written by holdouts_for_aromir.py> <out.json>

The counterpart is `../aromir_product_error_2026-11-16/product_error.txt` (the capstone's measurement of 16 Nov): the band error of
the seed mean per family and hold-out must agree to the second decimal, and so must the first-order error per seed with the
release record's printed numbers.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import torch
from aromir import evaluation, families, release


def main() -> None:
    folder, out = Path(sys.argv[1]), Path(sys.argv[2])
    torch.set_num_threads(2)
    loaded = release.load(release.bundled())
    measured = evaluation.evaluate(loaded, folder)
    tmp = out.with_name(out.name + ".tmp")
    tmp.write_text(json.dumps(measured, indent=1) + "\n", encoding="utf-8")
    os.replace(tmp, out)
    for name, holdout in measured.items():
        print(f"hold-out ({name}), {holdout['n_molecules']} molecules")
        for family in families.FAMILIES:
            band = holdout["band_error_seed_mean"][family]
            seeds = holdout["first_order_error_per_seed"][family]
            print(f"  {family:<11} band error of the seed mean {band['rms_cm']:.2f} ({band['n_modes']} modes; "
                  f"{band['interval_cm'][0]:.2f}-{band['interval_cm'][1]:.2f}, {band['share_of_resamples_within_line']:.2f} "
                  f"of resamples below the line) | first order per seed {seeds}, mean {sum(seeds) / len(seeds):.2f}")


if __name__ == "__main__":
    main()
