"""The digest of each pinned molecule's internal coordinates, atom numbers included (aromir tests/test_order_pins.py).

    python pin_primitive_digests.py

A count of primitive kinds does not see another choice of primitives, and a string of symbols does not see carbons that
changed places (review of aromir c19e268, finding 7). The pin is therefore the sha256 of geomeTRIC's own description of every
primitive in order, which names its atoms by number. Printed with the first three descriptions, to show what is hashed.
"""
from __future__ import annotations

import hashlib

from aromir import admission, geometry, release
from aromir.network import primitives

SMILES = ("c1ccccc1", "Oc1ccccc1", "N#Cc1ccccc1", "c1ccc(-c2ccccc2)cc1", "Cc1ccc2ccccc2c1", "FC(F)(F)c1ccncc1", "Clc1ccsc1")


def main() -> None:
    settings = release.load(release.bundled()).recipes[0].inputs.primitives
    for smiles in SMILES:
        start = geometry.start_from_smiles(admission.admit(admission.parse_smiles(smiles)).smiles)
        described = [repr(primitive) for primitive in primitives.build(start, settings).internals]
        digest = hashlib.sha256("\n".join(described).encode()).hexdigest()[:16]
        print(f"{smiles:<22}{len(described):>4} primitives  {digest}  {described[:3]} … {described[-1]}")


if __name__ == "__main__":
    main()
