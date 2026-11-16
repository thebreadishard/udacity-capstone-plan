"""Print what aromir's pinned tests are to hold: atom order and primitives of a few molecules (TASKS 245: P1).

    python pin_values.py

For each SMILES: the symbols of the start geometry in aromir's order, and the count of each kind of primitive under the bundled
release's settings; for one benzene xyz with its atoms listed backwards, the order `geometry.canonical_order` gives.
"""
from __future__ import annotations

import tempfile
from collections import Counter
from pathlib import Path

import rdkit
from aromir import admission, geometry, release
from aromir.network import primitives

SMILES = ("c1ccccc1", "Oc1ccccc1", "N#Cc1ccccc1", "c1ccc(-c2ccccc2)cc1", "Cc1ccc2ccccc2c1", "FC(F)(F)c1ccncc1", "Clc1ccsc1")
BENZENE_BACKWARDS = """12
benzene, hydrogens first
H   1.2405  -2.1486  0.0
H  -1.2405  -2.1486  0.0
H  -2.4810   0.0000  0.0
H  -1.2405   2.1486  0.0
H   1.2405   2.1486  0.0
H   2.4810   0.0000  0.0
C   0.6985  -1.2098  0.0
C  -0.6985  -1.2098  0.0
C  -1.3970   0.0000  0.0
C  -0.6985   1.2098  0.0
C   0.6985   1.2098  0.0
C   1.3970   0.0000  0.0
"""


def main() -> None:
    settings = release.load(release.bundled()).recipes[0].inputs.primitives
    print(f"rdkit {rdkit.__version__}")
    for smiles in SMILES:
        start = geometry.start_from_smiles(admission.admit(admission.parse_smiles(smiles)).smiles)
        built = primitives.build(start, settings)
        kinds = Counter(primitives.PRIMITIVE_KINDS[primitives.kind(p)] for p in built.internals)
        print(f'    ("{smiles}", "{"".join(start.symbols)}", {dict(sorted(kinds.items()))}),')
    with tempfile.TemporaryDirectory() as scratch:
        path = Path(scratch) / "benzene.xyz"
        path.write_text(BENZENE_BACKWARDS, encoding="utf-8")
        print("benzene backwards ->", geometry.canonical_order(admission.parse_xyz(path)))


if __name__ == "__main__":
    main()
