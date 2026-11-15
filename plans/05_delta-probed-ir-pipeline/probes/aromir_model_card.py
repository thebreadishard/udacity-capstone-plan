"""What aromir's certificate states about a network version, written from this repository's records (TASKS 73).

aromir (`thebreadishard/aromir`) ships a network's weights with two JSON files, so that no number on its certificate is typed in:

    evaluation   the version's measured error per mode family and hold-out — `m08.accuracy.network_accuracy` on the evaluation records
                 of the named model files, the function the live certificate and the licence (decision 65) read;
    training     what the models were trained on — the elements, the atom-count range and the canonical SMILES of every training
                 molecule, from the checkpoints' train_ids and the corpus (`m08.pipeline.training_set`, `m08.seen`). Needs the
                 checkpoints and the corpus, so it runs on the laptop.

    python probes/aromir_model_card.py evaluation <out.json> --version 1.3 --models E7_rungC_chain35_analytic_model_n750_seed{0,1,2}.pt
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


def write_json(path: Path, record: dict) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def evaluation(version: str, models: tuple[str, ...]) -> dict:
    """The families' seed-mean errors on both hold-outs as `network_accuracy` reports them, with the records they were read from."""
    from m08 import accuracy as A
    from promotion_read import FAMILIES

    acc = A.network_accuracy(A.evaluation_records(models), A.clean_a_records(models))
    return {"network_version": version, "higher_level": acc["higher_level"], "licence_line_cm": A.LICENCE_LINE_CM,
            "holdouts": {h: {"description": v["description"], "n_molecules": v["n_molecules"]} for h, v in acc["holdouts"].items()},
            "errors_cm": {f: {h: acc["holdouts"][h]["readouts"][f]["mean"] for h in acc["holdouts"]} for f in FAMILIES},
            "seed_errors_cm": {f: {h: acc["holdouts"][h]["readouts"][f]["seeds"] for h in acc["holdouts"]} for f in FAMILIES},
            "coupled_cluster": acc["coupled_cluster"], "sources": acc["sources"]}


def training(version: str, models: tuple[str, ...], soft_mode_repair: bool) -> dict:
    """The training set's elements, atom-count range and canonical SMILES (every molecule a model fitted or stopped on), and the
    hold-outs' canonical SMILES — `m08.seen`'s index, by which the live certificate says whether the network has seen a molecule."""
    from m08 import pipeline as P
    from m08 import seen as S

    paths = tuple(P.MR.OUT / m for m in models)
    elements, sizes = P.training_set(paths)
    seen = S.load(paths)
    held_out: dict[str, list[str]] = {}
    for smiles, (holdout, _ids) in sorted(seen.holdout.items()):
        held_out.setdefault(holdout, []).append(smiles)
    return {"network_version": version, "elements": [e.capitalize() for e in elements], "min_atoms": sizes[0], "max_atoms": sizes[1],
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
    a = ap.parse_args()
    if a.what == "training":
        if a.soft_mode_repair is None:
            raise SystemExit("training needs --soft-mode-repair yes|no: whether the models saw repaired low-mode labels")
        record = training(a.version, tuple(a.models), a.soft_mode_repair == "yes")
    else:
        record = evaluation(a.version, tuple(a.models))
    write_json(a.out, record)
    print(f"[aromir model card] {a.what}: {a.out}", flush=True)


if __name__ == "__main__":
    main()
