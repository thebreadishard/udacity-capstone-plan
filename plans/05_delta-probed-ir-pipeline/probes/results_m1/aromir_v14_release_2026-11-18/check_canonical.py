"""Every SMILES of v1.4's records is the one aromir's admission gives that molecule (the certificate's 'seen' line matches on it).

    python check_canonical.py <release folder>

For each SMILES in training.json and measurement.json (trained, held out, cation parents): admission.admit(parse_smiles(s)).smiles
must be s itself. A refusal by admission is printed with its reasons. Read-only.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from aromir import admission
from aromir.errors import RefusedError


def listed(record: dict) -> set[str]:
    return {*record["trained_smiles"], *(s for v in record["held_out_smiles"].values() for s in v),
            *(record.get("cation_parent_smiles") or ())}


def main() -> None:
    folder = Path(sys.argv[1])
    smiles: set[str] = set()
    for name in ("training.json", "measurement.json"):
        smiles |= listed(json.loads((folder / name).read_text(encoding="utf-8")))
    moved, refused = [], []
    for s in sorted(smiles):
        try:
            got = admission.admit(admission.parse_smiles(s)).smiles
        except RefusedError as error:
            refused.append((s, error.reasons))
            continue
        if got != s:
            moved.append((s, got))
    print(f"{len(smiles)} SMILES: {len(moved)} rewritten by admission, {len(refused)} refused", flush=True)
    for s, got in moved[:20]:
        print(f"  rewritten {s} -> {got}")
    for s, reasons in refused[:20]:
        print(f"  refused {s}: {reasons}")
    if moved:
        raise SystemExit("STOP: a record's SMILES is not the one aromir's admission gives")


if __name__ == "__main__":
    main()
