"""Write a release's evaluation record of format 2 from its record of format 1 and aromir's own measurement (TASKS 243).

    python make_evaluation_record.py <evaluation.json of format 1> <output of `aromir evaluate`> <aromir commit> <out.json>

Format 1 held one unnamed table (`errors_cm`, `seed_errors_cm`): each seed's first-order error and their mean. Format 2 keeps
those numbers under their name and adds the band error of the seeds' mean — the error of what the release delivers, on which the
licence is read since the user's decision of 16 November 2026 (decision 65, amended). The weights are not touched.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

BASIS = ("the band error of the seeds' mean, the error of what the release delivers; chosen on 16 November 2026, after it and the "
         "first-order error per seed had both been measured on both hold-outs")


def main() -> None:
    old = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    measured = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    commit, out = sys.argv[3], Path(sys.argv[4])
    if set(measured) != set(old["holdouts"]):
        raise SystemExit(f"measured on {sorted(measured)}, the record has {sorted(old['holdouts'])}")
    for name, holdout in old["holdouts"].items():
        if measured[name]["n_molecules"] != holdout["n_molecules"]:
            raise SystemExit(f"hold-out ({name}): measured on {measured[name]['n_molecules']} molecules, the record counts "
                             f"{holdout['n_molecules']}")
    families = list(old["errors_cm"])
    new = {
        "record_version": 2,
        "network_version": old["network_version"],
        "higher_level": old["higher_level"],
        "licence_line_cm": old["licence_line_cm"],
        "licence_basis": BASIS,
        "holdouts": old["holdouts"],
        "band_error_seed_mean_cm": {family: {name: measured[name]["band_error_seed_mean"][family] for name in old["holdouts"]}
                                    for family in families},
        "first_order_error_per_seed_cm": old["seed_errors_cm"],
        "first_order_error_per_seed_mean_cm": old["errors_cm"],
        "coupled_cluster": old["coupled_cluster"],
        "sources": [*old["sources"],
                    f"band errors: `aromir evaluate` at aromir {commit} on the two hold-outs as "
                    "probes/results_m1/aromir_audit_fixes_2026-11-16/holdouts_for_aromir.py of thebreadishard/udacity-capstone-plan "
                    "(plan 05) writes them; counterpart probes/results_m1/aromir_product_error_2026-11-16/product_error.json"],
        "atom_order_spread": old["atom_order_spread"],
    }
    tmp = out.with_name(out.name + ".tmp")
    tmp.write_text(json.dumps(new, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, out)
    for family in families:
        print(family, {name: (new["band_error_seed_mean_cm"][family][name]["rms_cm"], new["first_order_error_per_seed_mean_cm"][family][name])
                       for name in old["holdouts"]})


if __name__ == "__main__":
    main()
