"""What aromir's certificate states about a network version, written from this repository's records (TASKS 73).

aromir (`thebreadishard/aromir`) ships a network's weights with two JSON files, so that no number on its certificate is typed in:

    evaluation   the version's measured error per mode family and hold-out — `m08.accuracy.network_accuracy` on the evaluation records
                 of the named model files, the function the live certificate and the licence (decision 65) read — with the hold-outs
                 described for a reader outside this plan (`reader_wording`) and, when its record is given, the largest change of a
                 band between atom orders;
    training     what the models were trained on — the elements, the atom-count range and the canonical SMILES of every training
                 molecule, from the checkpoints' train_ids and the corpus (`m08.pipeline.training_set`, `m08.seen`). Needs the
                 checkpoints and the corpus, so it runs on the laptop.

    python probes/network_invariance_check.py <corpus ids> --what smiles --seeds 5 --out <spread.json>      (laptop: needs the models)
    python probes/aromir_model_card.py evaluation <out.json> --version 1.3 --models E7_rungC_chain35_analytic_model_n750_seed{0,1,2}.pt \\
        [--order-spread <spread.json>]
    python probes/aromir_model_card.py training <out.json> --version 1.3 --models <the same names> --soft-mode-repair no
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "modules" / "08_industry_synthesis"))
from aromir_common import aromir_symbol  # noqa: E402  (beside this script)


def write_json(path: Path, record: dict) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def registered_version(models: tuple[str, ...]) -> str:
    """The one network version the model registry gives the named files; refused when a file is unknown or they are of several."""
    from m08 import pipeline as P

    status = P.MR.read_status(P.MR.STATUS_FILE)
    unknown = [m for m in models if m not in status]
    if unknown:
        raise SystemExit(f"not in the model registry: {unknown}")
    versions = {status[m]["version"] for m in models}
    if len(versions) != 1:
        raise SystemExit(f"the named models are of {len(versions)} versions: {sorted(versions)}")
    return versions.pop()


def reader_wording() -> dict[str, tuple[str, int | None]]:
    """This repository's descriptions → the wording a reader of the public model card gets.

    `m08.accuracy`'s texts name tasks, chains and layers that mean nothing outside this plan. Each is mapped here by its full text, so a
    description that changes there, or a new hold-out, is refused instead of reaching the card in the plan's own words. A wording that
    names a count carries it, and `for_a_reader` refuses the record when its own count is another.
    """
    from m08 import accuracy as A

    return {
        A.CLEAN_A: ("eight molecules set aside on 19 September 2026, before any network was trained, and never trained on in any form "
                    "(two more molecules of that set, 2-naphthoic acid and benzonitrile, are left out of this read because the network "
                    "had trained on them under another identifier)", 8),
        A.HOLDOUTS["a"]: ("the molecules set aside on 19 September 2026, before any network was trained; two of them, 2-naphthoic "
                          "acid and benzonitrile, were trained on under another identifier, so this read is not clean", None),
        A.HOLDOUTS["b"]: ("every substituted molecule of two ring scaffolds, set aside on 8 October 2026; the network trained on no "
                          "molecule of either scaffold", None),
        A.CC_NOTE: ("not measured for this network version", None),
    }


def for_a_reader(text: str, n_molecules: int | None = None) -> str:
    wording = reader_wording()
    if text not in wording:
        raise SystemExit(f"no reader's wording for this text of m08.accuracy (add it to reader_wording): {text!r}")
    worded, count = wording[text]
    if count is not None and n_molecules != count:
        raise SystemExit(f"the reader's wording names {count} molecules, the record has {n_molecules}: {worded!r}")
    return worded


def order_spread(record_path: Path, models: tuple[str, ...]) -> dict:
    """The largest change of a band between atom orders, from a `probes/network_invariance_check.py --what smiles --out` record.

    Refused unless the record is the 'smiles' kind (the orders another SMILES writing gives: the case a user meets) and every check in
    it ran the named models.
    """
    record = json.loads(record_path.read_text(encoding="utf-8"))
    if record["what"] != "smiles":
        raise SystemExit(f"{record_path}: a '{record['what']}' record; the card states the spread over SMILES-like orders (--what smiles)")
    ran = {tuple(sorted(c["models"])) for c in record["checks"]}
    if ran != {tuple(sorted(models))}:
        raise SystemExit(f"{record_path}: its checks ran {sorted(ran)}, not the named models")
    return {"max_cm": max(v["max_cm"] for v in record["summary"].values()), "n_molecules": len(record["summary"]),
            "n_orders": record["seeds"], "source": record_path.name}


def evaluation(version: str, models: tuple[str, ...], spread_record: Path | None) -> dict:
    """The families' seed-mean errors on both hold-outs as `network_accuracy` reports them, with the records they were read from, the
    descriptions in a reader's wording, and the atom-order spread when its record is given."""
    from m08 import accuracy as A
    from promotion_read import FAMILIES

    acc = A.network_accuracy(A.evaluation_records(models), A.clean_a_records(models))
    out = {"network_version": version, "higher_level": acc["higher_level"], "licence_line_cm": A.LICENCE_LINE_CM,
           "holdouts": {h: {"description": for_a_reader(v["description"], v["n_molecules"]), "n_molecules": v["n_molecules"]}
                        for h, v in acc["holdouts"].items()},
           "errors_cm": {f: {h: acc["holdouts"][h]["readouts"][f]["mean"] for h in acc["holdouts"]} for f in FAMILIES},
           "seed_errors_cm": {f: {h: acc["holdouts"][h]["readouts"][f]["seeds"] for h in acc["holdouts"]} for f in FAMILIES},
           "coupled_cluster": for_a_reader(acc["coupled_cluster"]), "sources": acc["sources"]}
    if spread_record is not None:
        out["atom_order_spread"] = order_spread(spread_record, models)
    return out


def training(version: str, models: tuple[str, ...], soft_mode_repair: bool) -> dict:
    """The training set's elements, atom-count range and canonical SMILES (every molecule a model fitted or stopped on), and the
    hold-outs' canonical SMILES — `m08.seen`'s index, by which the live certificate says whether the network has seen a molecule.

    The SMILES are unique: a molecule the corpus holds under two ids is one entry (v1.3: 749 for 750 train ids). A hold-out's
    list is the whole hold-out, so a molecule that was also trained on under another id is in both lists (v1.3: two of (a)'s
    ten), while the evaluation record describes the clean read without them."""
    from m08 import pipeline as P
    from m08 import seen as S

    paths = tuple(P.MR.OUT / m for m in models)
    elements, sizes = P.training_set(paths)
    seen = S.load(paths)
    held_out: dict[str, list[str]] = {}
    for smiles, (holdout, _ids) in sorted(seen.holdout.items()):
        held_out.setdefault(holdout, []).append(smiles)
    return {"network_version": version, "elements": [aromir_symbol(e) for e in elements], "min_atoms": sizes[0], "max_atoms": sizes[1],
            "trained_smiles": sorted(seen.trained), "held_out_smiles": held_out, "soft_mode_repair": soft_mode_repair}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("what", choices=("evaluation", "training"))
    ap.add_argument("out", type=Path)
    ap.add_argument("--version", required=True)
    ap.add_argument("--models", nargs="+", required=True, help="the model files' names, as the registry and the evaluation records name them")
    ap.add_argument("--soft-mode-repair", choices=("yes", "no"),
                    help="training only: were the models trained on the corpus after the low-mode label swap of 14 Nov 2026 "
                         "(TASKS 216)? v1.3 (chain 35): no. aromir then prepares a molecule's Hessian the same way")
    ap.add_argument("--order-spread", type=Path,
                    help="evaluation only: a record of probes/network_invariance_check.py --what smiles --out, run on these models")
    a = ap.parse_args()
    registered = registered_version(tuple(a.models))
    if registered != a.version:
        raise SystemExit(f"--version {a.version}, but the model registry gives these files version {registered}")
    if a.what == "training":
        if a.soft_mode_repair is None:
            raise SystemExit("training needs --soft-mode-repair yes|no: whether the models saw repaired low-mode labels")
        record = training(a.version, tuple(a.models), a.soft_mode_repair == "yes")
    else:
        record = evaluation(a.version, tuple(a.models), a.order_spread)
    write_json(a.out, record)
    print(f"[aromir model card] {a.what}: {a.out}", flush=True)


if __name__ == "__main__":
    main()
