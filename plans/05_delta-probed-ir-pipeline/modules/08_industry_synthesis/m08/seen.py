"""Has the network seen this molecule? (TASKS 155: the demo's molecule must be unseen, and a molecule the network trained on must not be read
by the hold-out error.) The carried models' training ids — every molecule a seed fitted or stopped on — come from the checkpoints
(`pipeline.train_ids`), the hold-outs from the models' evaluation records, the SMILES from the corpus manifest. A molecule is matched by its
canonical SMILES, not by its id, so the same molecule under another id is caught. Where the corpus holds the molecule's ωB97X Hessian the
truth is set beside the network's spectrum without an atom mapping: positions paired by rank and the overlap of the broadened spectra, both
independent of the atom order and the frame."""
from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from . import accuracy as A
from . import pipeline as P
from .catalog import canonical
from .spectrum import cheap_apt, overlap, series

MANIFEST = P.M05 / "corpus" / "manifest.csv"
CATION_LAYER = "P3c"                   # a cation row carries its neutral parent's SMILES; the network trained on neutral molecules only
TEXT = {
    "trained": "in the network's training set ({ids}): the hold-out error is not this molecule's measure",
    "trained_and_held_out": "in the network's training set ({ids}) and also in hold-out ({h}) as {held}: that hold-out was not clean for it, "
                            "and the hold-out error is not this molecule's measure",
    "a": "held out, hold-out (a) ({ids}): never trained on; the measured error includes it",
    "b": "held out, hold-out (b) ({ids}): never trained on; the measured error includes it",
    "catalogue": "in the catalogue ({ids}) but not among the molecules the network trained on",
    "unseen": "not in the catalogue: the network has not seen it",
}


@dataclass(frozen=True)
class Seen:
    """Canonical SMILES → the ids the network trained on under it, and → (hold-out, ids) for the hold-out molecules."""
    trained: dict[str, list[str]]
    holdout: dict[str, tuple[str, list[str]]]


def by_smiles(ids: set[str], smiles_of: dict[str, str]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for i in sorted(ids):
        if i not in smiles_of:
            raise KeyError(f"{i} is not a neutral row of the corpus manifest")
        c = canonical(smiles_of[i])
        if c is None:
            raise ValueError(f"{i}: its manifest SMILES does not parse")
        out.setdefault(c, []).append(i)
    return out


def build(trained_ids: set[str], holdout_ids: dict[str, set[str]], smiles_of: dict[str, str]) -> Seen:
    """The index. A molecule may be both trained on and held out, under two ids (a hold-out molecule's twin in another layer); `status`
    names it, and `leaks` lists them."""
    holdout = {c: (h, ids) for h, these in holdout_ids.items() for c, ids in by_smiles(these, smiles_of).items()}
    return Seen(by_smiles(trained_ids, smiles_of), holdout)


def leaks(seen: Seen) -> dict[str, tuple[str, list[str], list[str]]]:
    """Canonical SMILES → (hold-out, its ids there, its ids in the training set) for every hold-out molecule the network also trained on."""
    return {c: (seen.holdout[c][0], seen.holdout[c][1], seen.trained[c]) for c in sorted(set(seen.trained) & set(seen.holdout))}


def load(models: tuple[Path, ...]) -> Seen:
    """The index for the models that ran."""
    with MANIFEST.open(newline="", encoding="utf-8") as f:
        smiles_of = {r["id"]: r["smiles"] for r in csv.DictReader(f) if r["layer"] != CATION_LAYER}
    holdout_ids: dict[str, set[str]] = {h: set() for h in A.HOLDOUTS}
    for record in A.evaluation_records(tuple(p.name for p in models)):
        rec = json.loads(record.read_text(encoding="utf-8"))
        for h, ids in holdout_ids.items():
            ids |= set(rec[h]["per_molecule"])
    return build(P.train_ids(models), holdout_ids, smiles_of)


def status(smiles: str, seen: Seen, listed_id: str | None) -> dict:
    """Trained on, held out, in the catalogue only, or unseen; with the ids and the certificate's sentence."""
    c = canonical(smiles)
    if c in seen.trained and c in seen.holdout:
        h, held = seen.holdout[c]
        ids = seen.trained[c]
        return {"role": "trained_and_held_out", "ids": ids,
                "text": TEXT["trained_and_held_out"].format(ids=", ".join(ids), h=h, held=", ".join(held))}
    if c in seen.trained:
        role, ids = "trained", seen.trained[c]
    elif c in seen.holdout:
        role, ids = seen.holdout[c]
    elif listed_id is not None:
        role, ids = "catalogue", [listed_id]
    else:
        role, ids = "unseen", []
    return {"role": role, "ids": ids, "text": TEXT[role].format(ids=", ".join(ids))}


def truth_beside(corpus_id: str, network_sticks: list[dict]) -> dict | None:
    """The corpus's ωB97X spectrum against the network's: the overlap (with the corpus's own B3LYP APT) and the positions paired by rank;
    None where the corpus holds no ωB97X Hessian. Ranks pair only when both list the same number of bands."""
    d = P.CORPUS / corpus_id
    if not (d / P.TRUTH_HESSIAN).exists():
        return None
    masses = np.asarray(json.loads((d / "geometry.json").read_text(encoding="utf-8"))["masses_amu"], float)
    truth = series(d / P.TRUTH_HESSIAN, masses, cheap_apt(d))
    t = np.array([s["omega_cm"] for s in truth["sticks"]])
    n = np.sort([s["omega_cm"] for s in network_sticks])
    rms = round(float(np.sqrt(np.mean((n - t) ** 2))), 2) if len(t) == len(n) else None
    heights = truth["kind"] == "positions and heights"
    return {"source": f"corpus/molecules/{corpus_id}/{P.TRUTH_HESSIAN}", "n_bands": len(t), "rms_by_rank_cm": rms,
            "overlap": overlap(network_sticks, truth["sticks"]) if heights else None}
