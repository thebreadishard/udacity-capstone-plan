"""Write the hold-outs of a release's source record in the layout `aromir evaluate` reads (TASKS 243).

The adapter between this repository's corpus and aromir's neutral hold-out format: per set a folder, per molecule one .npz with
`symbols`, `coords_bohr`, `hessian` (the B3LYP analytic Hessian, projected) and `reference_hessian` (the ωB97X analytic one), the
atoms in the order aromir gives the molecule when it reads it as an xyz file. The files are numbered in the source record's order,
because the resampling interval depends on the order of the molecules.

    python holdouts_for_aromir.py <plan folder> <source record, relative to module 05's out/> <out folder> a8=a b=b

Each `<set in the record>=<hold-out name>` names one set. Read-only on the corpus; no quantum chemistry.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import numpy as np
from aromir import admission, evaluation
from aromir import geometry as aromir_geometry
from aromir.constants import ANGSTROM_PER_BOHR
from aromir.molecule import Geometry


def load(folder: Path) -> tuple[Geometry, np.ndarray, np.ndarray]:
    """The stored geometry and the two analytic Hessians of one corpus molecule."""
    stored = json.loads((folder / "geometry.json").read_text(encoding="utf-8"))
    symbols = tuple(s[0].upper() + s[1:].lower() for s in stored["symbols"])
    hessians = []
    for level in ("b3lyp", "wb97x"):
        with np.load(folder / f"hessian_{level}_analytic.npz") as z:
            hessians.append(np.array(z["H_projected"], float))
    return Geometry(symbols, np.array(stored["coords_bohr"], float)), hessians[0], hessians[1]


def aromir_order(geometry: Geometry, scratch: Path) -> list[int]:
    """The atom order aromir gives a molecule read from an xyz file in the corpus order."""
    lines = [str(geometry.n_atoms), "holdouts_for_aromir"]
    for symbol, row in zip(geometry.symbols, geometry.coords_bohr * ANGSTROM_PER_BOHR, strict=True):
        lines.append(f"{symbol} {row[0]:.10f} {row[1]:.10f} {row[2]:.10f}")
    path = scratch / "molecule.xyz"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return list(aromir_geometry.canonical_order(admission.parse_xyz(path)))


def main() -> None:
    plan, source_name, out = Path(sys.argv[1]).resolve(), sys.argv[2], Path(sys.argv[3])
    module = plan / "modules" / "05_support_predictor"
    source = json.loads((module / "out" / source_name).read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory() as scratch:
        for pair in sys.argv[4:]:
            key, _, name = pair.partition("=")
            folder = out / name
            folder.mkdir(parents=True, exist_ok=False)
            ids = list(source[key]["per_molecule"])
            for number, molecule_id in enumerate(ids):
                geometry, low, reference = load(module / "corpus" / "molecules" / molecule_id)
                order = aromir_order(geometry, Path(scratch))
                index = (3 * np.array(order)[:, None] + np.arange(3)).ravel()
                moved = evaluation.Reference(molecule_id, geometry.reordered(order), low[np.ix_(index, index)],
                                             reference[np.ix_(index, index)])
                evaluation.write(folder / f"{number:03d}_{molecule_id}.npz", moved)
            print(f"{key} -> {folder}: {len(ids)} molecules", flush=True)


if __name__ == "__main__":
    main()
