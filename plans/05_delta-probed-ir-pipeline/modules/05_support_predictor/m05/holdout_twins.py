"""Hold-out twins: a training-pool molecule that is the same molecule as a hold-out one under another id (TASKS 157, the user's decision of
30 Oct 2026). v1.3 trained on 2-naphthoic acid and benzonitrile of hold-out (a) as their layer-B twins (B_07cadc7923, B_3100da3761): the ids
differ by their layer prefix, the molecule is one. A molecule is keyed by its canonical SMILES and its charge — a P3c row carries its
neutral parent's SMILES, and a cation is not its parent — read from the corpus manifest beside the molecules directory."""
from __future__ import annotations

import csv
from pathlib import Path

CATION_LAYER = "P3c"                   # the manifest's cation rows (charge +1), written with the neutral parent's SMILES


def canonical(smiles: str) -> str:
    from rdkit import Chem, RDLogger

    RDLogger.DisableLog("rdApp.*")
    m = Chem.MolFromSmiles(smiles)
    if m is None:
        raise ValueError(f"{smiles!r} does not parse")
    return Chem.MolToSmiles(m)


def manifest_keys(molecules: str | Path) -> dict[str, tuple[str, int]]:
    """Every manifest id → (canonical SMILES, charge), from `<molecules>/../manifest.csv`."""
    path = Path(molecules).parent / "manifest.csv"
    with path.open(newline="", encoding="utf-8") as f:
        return {r["id"]: (canonical(r["smiles"]), 1 if r["layer"] == CATION_LAYER else 0) for r in csv.DictReader(f) if r["smiles"]}


def twins(pool: list[str], held: list[str], keys: dict[str, tuple[str, int]]) -> list[str]:
    """The pool ids that are a held-out molecule under another id; an id without a manifest row is refused (it could hide a twin)."""
    missing = sorted(i for i in [*pool, *held] if i not in keys)
    if missing:
        raise KeyError(f"no manifest row for {len(missing)} ids ({', '.join(missing[:3])}): their twins cannot be checked")
    held_keys = {keys[i] for i in held}
    return [i for i in pool if keys[i] in held_keys and i not in held]
