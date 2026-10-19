"""The charge and multiplicity a corpus molecule was computed with: the deck in its molecules/<id>/job.json. A pool 3 cation's manifest SMILES
is its neutral parent's (P3c_541c53d1a5, phenanthrene⁺, carries phenanthrene's), so the SMILES cannot say it (19 Oct 2026: S2b's selector
took two cations for neutral molecules)."""
from __future__ import annotations

import json
import os

CORPUS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "modules", "05_support_predictor", "corpus")
NEUTRAL_SINGLET = (0, 1)


def recorded_state(mol_id: str, corpus: str = CORPUS) -> tuple[int, int]:
    """(charge, multiplicity) from the deck in the molecule's job.json; a missing file or key fails loudly."""
    path = os.path.join(corpus, "molecules", mol_id, "job.json")
    if not os.path.isfile(path):
        raise SystemExit(f"{mol_id}: no job.json, so its charge is unknown")
    with open(path, encoding="utf-8") as fh:
        deck = json.load(fh).get("deck", {})
    if "charge" not in deck or "multiplicity" not in deck:
        raise SystemExit(f"{mol_id}: job.json's deck names no charge or multiplicity")
    return int(deck["charge"]), int(deck["multiplicity"])
