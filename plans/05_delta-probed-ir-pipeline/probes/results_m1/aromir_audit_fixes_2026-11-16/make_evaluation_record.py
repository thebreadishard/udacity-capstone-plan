"""Write a release's evaluation record of format 2 from its record of format 1 and aromir's own measurement (TASKS 243).

    python make_evaluation_record.py <evaluation.json of format 1> <output of `aromir evaluate`> <out.json>

Format 1 held one unnamed table (`errors_cm`, `seed_errors_cm`): each seed's first-order error and their mean, as the training
runs recorded them. Format 2 names both quantities and takes every number from `aromir evaluate` — the band error of the seeds'
mean, on which the licence is read since the user's decision of 16 November 2026 (decision 65, amended), and the first-order
error per seed. The old record gives the descriptions, the level, the line and the atom-order spread; its first-order numbers are
printed beside aromir's so that the difference is on record. The weights are not touched.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from aromir import evaluation

BASIS = ("the band error of the seeds' mean, the error of what the release delivers, as recorded to two decimals; chosen on 16 "
         "November 2026, after it and the first-order error per seed had both been measured on both hold-outs")
MEASURED_BY = ("every error in this record: `aromir evaluate` on the two hold-outs as "
               "probes/results_m1/aromir_audit_fixes_2026-11-16/holdouts_for_aromir.py of thebreadishard/udacity-capstone-plan "
               "(plan 05) writes them; counterpart for the band errors: "
               "probes/results_m1/aromir_product_error_2026-11-16/product_error.json")
HOLDOUTS_FROM = "the hold-outs' molecules, and the first-order errors the training runs recorded themselves (within 0.08 cm⁻¹): "


def main() -> None:
    old = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    measured = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    out = Path(sys.argv[3])
    if set(measured) != set(old["holdouts"]):
        raise SystemExit(f"measured on {sorted(measured)}, the record has {sorted(old['holdouts'])}")
    for name, holdout in old["holdouts"].items():
        if measured[name]["n_molecules"] != holdout["n_molecules"]:
            raise SystemExit(f"hold-out ({name}): measured on {measured[name]['n_molecules']} molecules, the record counts "
                             f"{holdout['n_molecules']}")
    tables = evaluation.record_tables({name: measured[name] for name in old["holdouts"]})
    new = {
        "record_version": 2,
        "network_version": old["network_version"],
        "higher_level": old["higher_level"],
        "licence_line_cm": old["licence_line_cm"],
        "licence_basis": BASIS,
        "holdouts": old["holdouts"],
        **tables,
        "coupled_cluster": old["coupled_cluster"],
        "sources": [MEASURED_BY, HOLDOUTS_FROM + ", ".join(old["sources"])],
        "atom_order_spread": old["atom_order_spread"],
    }
    tmp = out.with_name(out.name + ".tmp")
    tmp.write_text(json.dumps(new, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, out)
    largest = 0.0
    for family, per_holdout in new["first_order_error_per_seed_cm"].items():
        for name, seeds in per_holdout.items():
            before = old["seed_errors_cm"][family][name]
            largest = max(largest, *(abs(a - b) for a, b in zip(seeds, before, strict=True)))
            print(f"{family:<11}({name}) band {new['band_error_seed_mean_cm'][family][name]['rms_cm']:.2f} | first order per seed "
                  f"{seeds}, mean {new['first_order_error_per_seed_mean_cm'][family][name]:.2f} | the training runs' {before}, "
                  f"mean {old['errors_cm'][family][name]:.2f}")
    print(f"largest difference between aromir's and the training runs' first-order error of a seed: {largest:.2f} cm-1")


if __name__ == "__main__":
    main()
