"""Write aromir's certificate text for corpus molecules from their stored Hessians, no quantum chemistry (TASKS 243).

    python certificates_on_stored_hessians.py <plan folder> <out folder> <SMILES> [<SMILES> ...]

For each SMILES the first corpus molecule with an analytic B3LYP Hessian is taken, in the atom order aromir gives it; the polar
tensor is not stored with the analytic Hessian, so the heights are printed as zero and are no part of this record.
"""
from __future__ import annotations

import csv
import json
import sys
import tempfile
from pathlib import Path

import numpy as np
from aromir import admission, certificate, release, response
from aromir import geometry as aromir_geometry
from aromir.constants import ANGSTROM_PER_BOHR
from aromir.lowlevel import LowLevel
from aromir.molecule import Geometry

LOW_HESSIAN = "hessian_b3lyp_analytic.npz"


def aromir_order(geometry: Geometry, scratch: Path) -> list[int]:
    lines = [str(geometry.n_atoms), "certificate"]
    for symbol, row in zip(geometry.symbols, geometry.coords_bohr * ANGSTROM_PER_BOHR, strict=True):
        lines.append(f"{symbol} {row[0]:.10f} {row[1]:.10f} {row[2]:.10f}")
    path = scratch / "molecule.xyz"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return list(aromir_geometry.canonical_order(admission.parse_xyz(path)))


def main() -> None:
    plan, out = Path(sys.argv[1]).resolve(), Path(sys.argv[2])
    corpus = plan / "modules" / "05_support_predictor" / "corpus"
    loaded = release.load(release.bundled())
    with (corpus / "manifest.csv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as scratch:
        for smiles in sys.argv[3:]:
            molecule_id = next(row["id"] for row in rows
                               if row["smiles"] == smiles and (corpus / "molecules" / row["id"] / LOW_HESSIAN).is_file())
            folder = corpus / "molecules" / molecule_id
            stored = json.loads((folder / "geometry.json").read_text(encoding="utf-8"))
            geometry = Geometry(tuple(s[0].upper() + s[1:].lower() for s in stored["symbols"]), np.array(stored["coords_bohr"], float))
            with np.load(folder / LOW_HESSIAN) as low:
                hessian = np.array(low["H_projected"], float)
            order = aromir_order(geometry, Path(scratch))
            index = (3 * np.array(order)[:, None] + np.arange(3)).ravel()
            geometry, hessian = geometry.reordered(order), hessian[np.ix_(index, index)]
            low_level = LowLevel(energy=0.0, hessian=hessian, polar_tensor=np.zeros((3, len(hessian))),
                                 refinement=response.Refinement(0.0, 0.0, 0, 0), sum_rule_violation=0.0, seconds=0.0)
            admitted = admission.admit(admission.parse_smiles(smiles))
            record = certificate.build(admitted, geometry, low_level, loaded.corrections(geometry, hessian), loaded)
            name = f"certificate_{molecule_id}.md"
            (out / name).write_text(certificate.to_markdown(record), encoding="utf-8", newline="\n")
            n_licensed = sum(band["licensed"] for band in record["bands"])
            print(f"{smiles} ({molecule_id}): {len(record['bands'])} bands, {n_licensed} licensed -> {name}")


if __name__ == "__main__":
    main()
