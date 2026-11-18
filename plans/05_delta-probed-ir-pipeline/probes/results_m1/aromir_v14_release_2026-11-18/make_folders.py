"""Write aromir's two v1.4 network folders from the training checkpoints (decision 66; the parent's task of 18 Nov 2026).

    python make_folders.py <plan folder> <out folder> [--release-record]

`--release-record` rewrites only `<out>/release/release.json` from the folders already written (the conversion is deterministic;
release.json gained the seeds' tensor hashes after the review of aromir 6954a77).

`<out>/measurement/`: the measurement networks (`..._model_n1082_seed*.pt`) as an aromir release folder of the v1.3 kind — the
seeds' weights and recipes and their `training.json` (what they fitted or stopped on, and the two hold-outs they never saw). It
is not shipped: `aromir evaluate` and `product_error.py` read the errors on it, so the errors come from aromir's own code.

`<out>/release/`: the release networks (`..._release_model_n1132_seed*.pt`) — the shipped seeds, their `training.json` (every
molecule they fitted or stopped on, nothing held out, and the neutral parents of the radical cations among them),
`measurement.json` (the measurement networks' training record, which the errors belong to) and `release.json` (which networks
the folder ships, the checks that let them ship, and the checkpoints by hash). `evaluation.json` is written later, from what
`aromir evaluate` measures on the measurement folder (make_evaluation_record.py).

Read-only on the plan; no network is run.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

import torch
from aromir import admission
from aromir.network import convert
from rdkit import Chem

PLAN = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]).resolve()
M05 = PLAN / "modules" / "05_support_predictor"
V14 = M05 / "out" / "v14"
STEM = "E7_rungC_v14s3clean_c00_control"
MEASUREMENT = [V14 / f"{STEM}_model_n1082_seed{s}.pt" for s in range(3)]
RELEASE = [V14 / f"{STEM}_release_model_n1132_seed{s}.pt" for s in range(3)]
EVAL_RECORDS = [V14 / f"{STEM}_eval_clean_seed{s}.json" for s in range(3)]
CHECKS = V14 / f"{STEM}_release_release_checks.json"
CATION_LAYER = "P3c"            # a cation row carries its neutral parent's SMILES (m08/seen.py)
VERSION = "1.4"
# m08/seen.py's cation clause, with its source: seed 0 of v1.4's recipe, benzene's corrected-frequency rms without and with the
# P3c layer (probes/results_m1/v14_data_read_2026-11-17/probe_nop3c.txt)
CATION_TEST = {"molecule": "benzene", "without_cm": 1.47, "with_cm": 5.37, "n_networks": 1,
               "source": "probes/results_m1/v14_data_read_2026-11-17/probe_nop3c.txt of thebreadishard/udacity-capstone-plan (plan 05)"}
HOLDOUT_SETS = {"a": "a8", "b": "b"}   # hold-out name -> the evaluation records' set the licence is read on (m08.accuracy)
HOLDOUT_TEXT = {
    "a": ("eight of the ten molecules set aside on 19 September 2026, before any network was trained; the other two have a twin "
          "in another layer of the training pool and are left out of the read (30 October 2026)"),
    "b": ("every substituted molecule of two ring scaffolds, set aside on 8 October 2026; no measurement network trained on a "
          "molecule of either scaffold"),
}


def sha(path: Path, n: int = 16) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()[:n]


def canonical(smiles: str) -> str:
    """The SMILES aromir's admission gives a molecule (admission.admit: RDKit's canonical form without hydrogens)."""
    molecule = admission.parse_smiles(smiles)
    return str(Chem.MolToSmiles(admission.without_hydrogens(molecule)))


def manifest() -> dict[str, dict[str, str]]:
    with (M05 / "corpus" / "manifest.csv").open(newline="", encoding="utf-8") as handle:
        return {row["id"]: row for row in csv.DictReader(handle)}


def train_ids(checkpoints: list[Path]) -> tuple[set[str], set[float], set[str]]:
    """Every id a seed fitted or stopped on, the seeds' inner-validation shares, and their network kinds."""
    ids: set[str] = set()
    shares: set[float] = set()
    kinds: set[str] = set()
    for path in checkpoints:
        record = torch.load(path, map_location="cpu", weights_only=False)
        ids |= set(record["train_ids"])
        args = record["args"] if isinstance(record["args"], dict) else vars(record["args"])
        shares.add(float(args["inner_val"]))
        kinds.add(str(args.get("network_kind", "measurement")))
    return ids, shares, kinds


def sizes_and_elements(ids: set[str]) -> tuple[list[str], int, int]:
    elements: set[str] = set()
    counts = []
    for molecule_id in ids:
        stored = json.loads((M05 / "corpus" / "molecules" / molecule_id / "geometry.json").read_text(encoding="utf-8"))
        elements |= {s[0].upper() + s[1:].lower() for s in stored["symbols"]}
        counts.append(len(stored["symbols"]))
    return sorted(elements), min(counts), max(counts)


def training_record(ids: set[str], rows: dict[str, dict[str, str]], held_out: dict[str, list[str]]) -> dict:
    missing = sorted(ids - set(rows))
    if missing:
        raise SystemExit(f"{len(missing)} trained ids are not in the manifest: {missing[:5]}")
    neutral = {i for i in ids if rows[i]["layer"] != CATION_LAYER}
    cations = ids - neutral
    elements, smallest, largest = sizes_and_elements(ids)
    record = {
        "network_version": VERSION,
        "elements": elements,
        "min_atoms": smallest,
        "max_atoms": largest,
        "trained_smiles": sorted({canonical(rows[i]["smiles"]) for i in neutral}),
        "held_out_smiles": held_out,
        "soft_mode_repair": False,
    }
    if cations:
        record["cation_parent_smiles"] = sorted({canonical(rows[i]["smiles"]) for i in cations})
        record["cation_test"] = CATION_TEST
    print(f"  {len(ids)} ids ({len(neutral)} neutral, {len(cations)} cation rows) -> {len(record['trained_smiles'])} neutral "
          f"SMILES, {len(record.get('cation_parent_smiles', []))} cation parents; {smallest}-{largest} atoms, {elements}", flush=True)
    return record


def write_json(path: Path, record: dict) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def held_out_sets(rows: dict[str, dict[str, str]]) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    """The hold-outs' ids and canonical SMILES, from the measurement networks' evaluation records (the same in all three)."""
    ids = None
    for path in EVAL_RECORDS:
        record = json.loads(path.read_text(encoding="utf-8"))
        these = {h: list(record[key]["per_molecule"]) for h, key in HOLDOUT_SETS.items()}
        if ids is not None and these != ids:
            raise SystemExit(f"{path.name} lists other hold-out molecules than {EVAL_RECORDS[0].name}")
        ids = these
    return ids, {h: sorted({canonical(rows[i]["smiles"]) for i in v}) for h, v in ids.items()}


def convert_seeds(checkpoints: list[Path], folder: Path) -> None:
    folder.mkdir(parents=True, exist_ok=False)
    for seed, path in enumerate(checkpoints):
        recipe = convert.convert(path, folder, f"seed-{seed}", VERSION)
        if recipe.seed != seed:
            raise SystemExit(f"{path.name} holds seed {recipe.seed}")


def seeds_from_checkpoints() -> dict[str, str]:
    """Each release seed's tensor sha256 as a fresh conversion of its checkpoint gives it, checked against the seed in
    <out>/release: release.json is then bound to the checkpoints it names, not only to the folder."""
    written = {f"seed-{s}": json.loads((OUT / "release" / f"seed-{s}.json").read_text(encoding="utf-8"))["sha256"]
               for s in range(len(RELEASE))}
    with tempfile.TemporaryDirectory() as scratch:
        convert_seeds(RELEASE, Path(scratch) / "release")
        fresh = {name: json.loads((Path(scratch) / "release" / f"{name}.json").read_text(encoding="utf-8"))["sha256"]
                 for name in written}
    if fresh != written:
        raise SystemExit(f"STOP: the seeds in {OUT / 'release'} are not the conversion of the release checkpoints")
    return fresh


def release_record(n_release_ids: int, shares: set[float]) -> dict:
    """aromir's release.json: the checks by name, the checkpoints by hash (checked against the checks' record)."""
    checks = json.loads(CHECKS.read_text(encoding="utf-8"))
    if not checks["passed"] or checks["refusals"]:
        raise SystemExit(f"{CHECKS.name}: the release checks did not pass: {checks['refusals']}")
    if len(shares) != 1:
        raise SystemExit(f"the release seeds stopped on different shares: {shares}")
    hashes = {p.name: sha(p) for p in MEASUREMENT + RELEASE}
    if any(checks["model_sha16"].get(name) != h for name, h in hashes.items()):
        raise SystemExit(f"{CHECKS.name} was read on other checkpoints: {checks['model_sha16']} against {hashes}")
    return {
        "network_version": VERSION,
        "n_entries": n_release_ids,
        "fitted_share": round(1 - shares.pop(), 6),
        "checks": {name: bool(check["passed"]) for name, check in checks["checks"].items()},
        "seed_sha256": seeds_from_checkpoints(),
        "release_checkpoints": {p.name: hashes[p.name] for p in RELEASE},
        "measurement_checkpoints": {p.name: hashes[p.name] for p in MEASUREMENT},
        "source": (f"modules/05_support_predictor/out/v14/{CHECKS.name} of thebreadishard/udacity-capstone-plan (plan 05), "
                   f"{checks['date']}"),
    }


def release_record_only() -> None:
    """Rewrite release.json alone, from the checkpoints and the seeds already converted."""
    r_ids, r_shares, _ = train_ids(RELEASE)
    write_json(OUT / "release" / "release.json", release_record(len(r_ids), r_shares))
    print("release.json rewritten", flush=True)


def main() -> None:
    if sys.argv[3:] == ["--release-record"]:
        release_record_only()
        return
    if sys.argv[3:]:
        raise SystemExit(f"unknown arguments {sys.argv[3:]}")
    rows = manifest()
    holdout_ids, holdout_smiles = held_out_sets(rows)
    print({h: len(v) for h, v in holdout_ids.items()}, "hold-out molecules", flush=True)

    m_ids, m_shares, m_kinds = train_ids(MEASUREMENT)
    r_ids, r_shares, r_kinds = train_ids(RELEASE)
    print("kinds", m_kinds, r_kinds, "inner-validation shares", m_shares, r_shares, flush=True)
    leaked = {h: sorted(set(v) & m_ids) for h, v in holdout_ids.items()}
    if any(leaked.values()):
        raise SystemExit(f"measurement networks trained on hold-out molecules: {leaked}")
    if not m_ids <= r_ids:
        raise SystemExit(f"the release networks lack {len(m_ids - r_ids)} molecules the measurement networks trained on")
    print(f"release adds {len(r_ids - m_ids)} ids to the measurement networks' {len(m_ids)}", flush=True)

    print("measurement:", flush=True)
    measurement = training_record(m_ids, rows, holdout_smiles)
    print("release:", flush=True)
    release = training_record(r_ids, rows, {})

    convert_seeds(MEASUREMENT, OUT / "measurement")
    write_json(OUT / "measurement" / "training.json", measurement)
    convert_seeds(RELEASE, OUT / "release")
    write_json(OUT / "release" / "training.json", release)
    write_json(OUT / "release" / "measurement.json", measurement)
    write_json(OUT / "release" / "release.json", release_record(len(r_ids), r_shares))
    write_json(OUT / "holdouts.json", {"ids": holdout_ids, "descriptions": HOLDOUT_TEXT, "sets": HOLDOUT_SETS})
    print("done", flush=True)


if __name__ == "__main__":
    main()
