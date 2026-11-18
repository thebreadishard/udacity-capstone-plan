"""Write v1.4's evaluation record for aromir, from the capstone's product-error read or from `aromir evaluate` (decision 66).

    python make_evaluation_record.py capstone <plan folder> <v1.3 evaluation.json> <out.json>
    python make_evaluation_record.py aromir <measured.json> <capstone record written above> <product_error.json> <out.json>

`capstone`: the tables from `modules/05_support_predictor/out/v14/E7_rungC_v14s3clean_c00_control_product_error.json` (the
measurement networks' product error, m08's licence numbers). It is what `aromir evaluate` needs to load the measurement folder
(the licence line), and the counterpart of the second form.
`aromir`: the tables from what `aromir evaluate` measured with the measurement networks on the same hold-outs, in the atom
order aromir gives each molecule. Every cell must agree to TOL with product_error.py's read in that order (aromir's code on the
corpus's stored Hessians, a second route), or nothing is written; the capstone's read, in the corpus's atom order, is printed
beside it, and the difference is the network's dependence on the atom order (v1.4 is not order-free). This is the record aromir
ships.
The level, the line, the licence basis and the coupled-cluster sentence are v1.3's (the same proxy and rule); no atom-order spread
is given — it was not measured for v1.4.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from aromir import evaluation, families

TOL = 0.01                       # cm⁻¹: two decimals as recorded, against product_error.py in aromir's atom order
STEM = "E7_rungC_v14s3clean_c00_control"
HERE = Path(__file__).resolve().parent
SOURCES_CAPSTONE = ("every error in this record: the measurement networks' product-error read, "
                    f"modules/05_support_predictor/out/v14/{STEM}_product_error.json of thebreadishard/udacity-capstone-plan "
                    "(plan 05)")
SOURCES_AROMIR = ("every error in this record: `aromir evaluate` with the measurement networks "
                  f"({', '.join(f'{STEM}_model_n1082_seed{s}.pt' for s in range(3))}) on the two hold-outs as "
                  "probes/results_m1/aromir_audit_fixes_2026-11-16/holdouts_for_aromir.py of thebreadishard/udacity-capstone-plan "
                  "(plan 05) writes them; counterpart, within 0.01 cm⁻¹ in every cell: "
                  "probes/results_m1/aromir_v14_release_2026-11-18/product_error.json (aromir's code on the stored Hessians, in "
                  "aromir's atom order); the capstone's read in the corpus's atom order is "
                  f"modules/05_support_predictor/out/v14/{STEM}_product_error.json")


def write_json(path: Path, record: dict) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def rounded(value: float) -> float:
    return round(float(value), 2)


def capstone_tables(product: dict, names: dict[str, str]) -> dict:
    """The tables of format 2 from the capstone's product-error record, by hold-out name ('a' is its set 'a8')."""
    band, seeds, means = {}, {}, {}
    for family in families.FAMILIES:
        band[family], seeds[family], means[family] = {}, {}, {}
        for name, key in names.items():
            entry = product["holdouts"][name]
            if entry["set"] != key:
                raise SystemExit(f"hold-out ({name}) of the product record is its set {entry['set']}, not {key}")
            read = entry["families"][family]
            band[family][name] = {"rms_cm": rounded(read["product"]["rms"]), "n_modes": read["product"]["n_modes"],
                                  "interval_cm": [rounded(v) for v in read["product"]["interval"]],
                                  "share_of_resamples_within_line": round(read["product"]["share_below_line"], 2)}
            per_seed = read["first_order_certificate_families"]["seeds"]
            seeds[family][name] = [rounded(v) for v in per_seed]
            means[family][name] = rounded(sum(per_seed) / len(per_seed))
    return {"band_error_seed_mean_cm": band, "first_order_error_per_seed_cm": seeds, "first_order_error_per_seed_mean_cm": means}


def capstone(plan: Path, v13: Path, out: Path) -> None:
    product = json.loads((plan / "modules" / "05_support_predictor" / "out" / "v14" / f"{STEM}_product_error.json")
                         .read_text(encoding="utf-8"))
    old = json.loads(v13.read_text(encoding="utf-8"))
    holdouts = json.loads((HERE / "holdouts.json").read_text(encoding="utf-8"))
    record = {
        "record_version": 2,
        "network_version": "1.4",
        "higher_level": old["higher_level"],
        "licence_line_cm": old["licence_line_cm"],
        "licence_basis": old["licence_basis"],
        "holdouts": {name: {"description": holdouts["descriptions"][name], "n_molecules": len(ids)}
                     for name, ids in holdouts["ids"].items()},
        **capstone_tables(product, holdouts["sets"]),
        "coupled_cluster": old["coupled_cluster"],
        "sources": [SOURCES_CAPSTONE],
    }
    write_json(out, record)
    print(f"wrote {out} from the capstone's read", flush=True)


def cells(record: dict) -> dict[tuple, float]:
    """Every number of the tables, keyed by where it sits."""
    out = {}
    for family, per in record["band_error_seed_mean_cm"].items():
        for name, b in per.items():
            out[("band", family, name)] = b["rms_cm"]
            out[("low", family, name)], out[("high", family, name)] = b["interval_cm"]
            out[("modes", family, name)] = b["n_modes"]
    for family, per in record["first_order_error_per_seed_cm"].items():
        for name, values in per.items():
            for seed, v in enumerate(values):
                out[("seed", family, name, seed)] = v
    return out


def second_route(product: dict, names: dict[str, str]) -> dict[tuple, float]:
    """product_error.py's read in aromir's atom order, keyed as `cells` keys the tables."""
    out = {}
    for name, key in names.items():
        table = product["sets"][key]["aromir"]
        for family in families.FAMILIES:
            boot = table["mean_band_bootstrap"][family]
            out[("band", family, name)] = table["mean"][family]["band"]
            out[("low", family, name)], out[("high", family, name)] = boot["p2.5"], boot["p97.5"]
            for seed in range(3):
                out[("seed", family, name, seed)] = table[f"seed{seed}"][family]["first_order"]
    return out


def from_aromir(measured_path: Path, capstone_path: Path, product_path: Path, out: Path) -> None:
    measured = json.loads(measured_path.read_text(encoding="utf-8"))
    base = json.loads(capstone_path.read_text(encoding="utf-8"))
    names = json.loads((HERE / "holdouts.json").read_text(encoding="utf-8"))["sets"]
    product = json.loads(product_path.read_text(encoding="utf-8"))
    if set(measured) != set(base["holdouts"]):
        raise SystemExit(f"measured on {sorted(measured)}, the record has {sorted(base['holdouts'])}")
    for name, holdout in base["holdouts"].items():
        if measured[name]["n_molecules"] != holdout["n_molecules"]:
            raise SystemExit(f"hold-out ({name}): measured on {measured[name]['n_molecules']}, the record counts {holdout['n_molecules']}")
    record = base | evaluation.record_tables(measured) | {"sources": [SOURCES_AROMIR]}
    here, corpus, route = cells(record), cells(base), second_route(product, names)
    worst = max(abs(here[k] - route[k]) for k in route)
    order_effect = max(abs(here[k] - corpus[k]) for k in here if k[0] != "modes")
    modes = {k: (here[k], corpus[k]) for k in here if k[0] == "modes" and here[k] != corpus[k]}
    for family in families.FAMILIES:
        for name in base["holdouts"]:
            print(f"{family:<11}({name}) band: aromir evaluate {here[('band', family, name)]:.2f}, product_error.py in aromir's "
                  f"order {route[('band', family, name)]:.3f}, the capstone in the corpus order {corpus[('band', family, name)]:.2f}"
                  f" | modes {here[('modes', family, name)]} / {corpus[('modes', family, name)]}", flush=True)
    print(f"largest difference to product_error.py in aromir's order, any cell: {worst:.4f} cm-1 (tolerance {TOL}); to the "
          f"capstone's corpus-order read: {order_effect:.3f} cm-1 (the atom order); mode counts that differ: {modes}", flush=True)
    if worst > TOL or modes:
        raise SystemExit(f"STOP: aromir's measurement differs from product_error.py by {worst:.4f} cm-1 (> {TOL}) or in mode counts")
    write_json(out, record)
    print(f"wrote {out} from aromir's measurement", flush=True)


def main() -> None:
    form = sys.argv[1]
    if form == "capstone":
        capstone(Path(sys.argv[2]).resolve(), Path(sys.argv[3]), Path(sys.argv[4]))
    elif form == "aromir":
        from_aromir(Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4]), Path(sys.argv[5]))
    else:
        raise SystemExit(f"{form}: the form is 'capstone' or 'aromir'")


if __name__ == "__main__":
    main()
