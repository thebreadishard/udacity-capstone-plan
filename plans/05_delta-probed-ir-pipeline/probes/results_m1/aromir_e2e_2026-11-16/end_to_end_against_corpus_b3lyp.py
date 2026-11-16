"""The B3LYP positions of an aromir end-to-end run against the corpus's B3LYP Hessians of the same molecule (TASKS 245).

    python end_to_end_against_corpus_b3lyp.py <plan folder> <aromir result folder> <corpus id>

aromir optimises with pyscf from an RDKit start and measures every soft mode; the corpus row was optimised by psi4 and holds two
B3LYP Hessians: the analytic one (`hessian_b3lyp_analytic.npz`) and the label with its soft modes measured
(`hessian_b3lyp.npz`). The uncorrected positions the certificate prints (`b3lyp_cm`) are compared with both, band by band in
order of position, and the lowest five are printed, since the soft-mode repair acts there. The run record says whether the run
left a saddle point.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from aromir import vibrations
from aromir.molecule import Geometry

LOWEST = 5


def corpus_positions(folder: Path, name: str, geometry: Geometry) -> np.ndarray:
    with np.load(folder / name) as stored:
        return np.sort(vibrations.vibrational_modes(np.array(stored["H_projected"], float), geometry).wavenumbers)


def main() -> None:
    plan, result, molecule_id = Path(sys.argv[1]).resolve(), Path(sys.argv[2]), sys.argv[3]
    folder = plan / "modules" / "05_support_predictor" / "corpus" / "molecules" / molecule_id
    stored = json.loads((folder / "geometry.json").read_text(encoding="utf-8"))
    geometry = Geometry(tuple(s[0].upper() + s[1:].lower() for s in stored["symbols"]), np.array(stored["coords_bohr"], float))
    record = json.loads((result / "certificate.json").read_text(encoding="utf-8"))
    run = json.loads((result / "run.json").read_text(encoding="utf-8"))
    ours = np.sort([band["b3lyp_cm"] for band in record["bands"]])
    print(f"{record['molecule']['smiles']} ({molecule_id}): aromir's B3LYP positions against the corpus's, {len(ours)} bands")
    print(f"  left a saddle point: {run.get('left_saddle_point')}; files: {', '.join(sorted(p.name for p in result.iterdir()))}")
    for label, name in (("analytic", "hessian_b3lyp_analytic.npz"), ("soft modes measured (the label)", "hessian_b3lyp.npz")):
        theirs = corpus_positions(folder, name, geometry)
        if len(theirs) != len(ours):
            raise SystemExit(f"{len(ours)} bands in the certificate, {len(theirs)} in {name}")
        difference = ours - theirs
        print(f"  corpus {label}: rms {np.sqrt(np.mean(difference**2)):.2f}, largest {np.abs(difference).max():.2f} cm-1 "
              f"(band at {theirs[np.abs(difference).argmax()]:.1f}); above 200 cm-1: "
              f"rms {np.sqrt(np.mean(difference[theirs > 200]**2)):.2f}")
        print(f"    lowest {LOWEST}: aromir {np.round(ours[:LOWEST], 2).tolist()}  corpus {np.round(theirs[:LOWEST], 2).tolist()}")
    corrected = np.sort([band["wavenumber_cm"] for band in record["bands"]])
    print(f"  aromir corrected, lowest {LOWEST}: {np.round(corrected[:LOWEST], 2).tolist()}")


if __name__ == "__main__":
    main()
