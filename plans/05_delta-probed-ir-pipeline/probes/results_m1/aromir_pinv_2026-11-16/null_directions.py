"""What the small singular directions of a molecule's Wilson B are: rigid motions, or something else (TASKS 236; read-only).

For diphenylacetylene the scan finds three values of 1e-7 past the rank 3N-6. This prints, for the six directions past the
rank, the singular value and how much of the right singular vector lies in the span of the six rigid motions (1 = a pure
translation/rotation), and which primitive kinds carry the left singular vector.

    python null_directions.py <plan folder> <corpus id>
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from aromir import release as aromir_release
from aromir.molecule import Geometry
from aromir.network import primitives
from aromir.vibrations import rigid_basis


def main() -> None:
    plan, molecule_id = Path(sys.argv[1]).resolve(), sys.argv[2]
    folder = plan / "modules" / "05_support_predictor" / "corpus" / "molecules" / molecule_id
    stored = json.loads((folder / "geometry.json").read_text(encoding="utf-8"))
    geometry = Geometry(tuple(s[0].upper() + s[1:].lower() for s in stored["symbols"]), np.array(stored["coords_bohr"], float))
    settings = aromir_release.load(aromir_release.bundled()).recipes[0].inputs.primitives
    built = primitives.build(geometry, settings)
    kinds = [primitives.PRIMITIVE_KINDS[primitives.kind(p)] for p in built.internals]
    print(f"{molecule_id}: {geometry.n_atoms} atoms, primitives {dict(Counter(kinds))}")
    u, s, vt = np.linalg.svd(built.wilson_b, full_matrices=False)
    rank = 3 * geometry.n_atoms - 6
    # the rigid motions of unit masses span the same space as the mass-weighted ones' Cartesian images
    weights = np.repeat(np.sqrt(geometry.masses_amu), 3)
    rigid, _ = np.linalg.qr(rigid_basis(geometry) / weights[:, None])
    for index in range(rank - 1, rank + 6):
        in_rigid = float(np.linalg.norm(rigid.T @ vt[index]))
        weight = Counter()
        for kind_name, value in zip(kinds, u[:, index] ** 2, strict=True):
            weight[kind_name] += float(value)
        top = ", ".join(f"{k} {v:.2f}" for k, v in weight.most_common(2))
        print(f"  s[{index + 1}] = {s[index]:.3e}{' (last real)' if index == rank - 1 else ''}: share of the right vector in the "
              f"rigid motions {in_rigid:.6f}; left vector on {top}")


if __name__ == "__main__":
    main()
