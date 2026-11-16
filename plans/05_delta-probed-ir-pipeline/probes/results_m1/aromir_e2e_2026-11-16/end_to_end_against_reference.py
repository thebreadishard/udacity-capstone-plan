"""A molecule run end to end through aromir against its stored higher-level Hessian (TASKS 245: the audit's K6).

    python end_to_end_against_reference.py <plan folder> <aromir result folder> <corpus id>

The release's errors were measured on stored Hessians at the corpus geometries (psi4 minima). A user's run goes through aromir's
own chain: RDKit start, pyscf optimisation, pyscf Hessian, the network, diagonalisation. This reads the certificate of such a run
and compares its corrected positions with the bands of the corpus's ωB97X analytic Hessian at the corpus geometry, band by band
in order of position, per family (the family aromir's certificate gives the band). Beside it: the same comparison for the
uncorrected B3LYP positions the certificate prints, so that the correction's gain is on the same footing.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from aromir import families, vibrations
from aromir.molecule import Geometry


def main() -> None:
    plan, result, molecule_id = Path(sys.argv[1]).resolve(), Path(sys.argv[2]), sys.argv[3]
    folder = plan / "modules" / "05_support_predictor" / "corpus" / "molecules" / molecule_id
    stored = json.loads((folder / "geometry.json").read_text(encoding="utf-8"))
    geometry = Geometry(tuple(s[0].upper() + s[1:].lower() for s in stored["symbols"]), np.array(stored["coords_bohr"], float))
    with np.load(folder / "hessian_wb97x_analytic.npz") as z:
        reference = np.sort(vibrations.vibrational_modes(np.array(z["H_projected"], float), geometry).wavenumbers)
    record = json.loads((result / "certificate.json").read_text(encoding="utf-8"))
    bands = sorted(record["bands"], key=lambda band: band["wavenumber_cm"])
    corrected = np.array([band["wavenumber_cm"] for band in bands])
    plain = np.sort([band["b3lyp_cm"] for band in record["bands"]])
    family = np.array([band["family"] for band in bands])
    if len(corrected) != len(reference):
        raise SystemExit(f"{len(corrected)} bands in the certificate, {len(reference)} in the reference")
    print(f"{record['molecule']['smiles']} ({molecule_id}): aromir end to end against the corpus's ωB97X bands, {len(reference)} bands")
    print(f"  {'family':<11}{'bands':>6}{'corrected rms':>15}{'largest':>9}{'B3LYP rms':>11}")
    for name in families.FAMILIES:
        chosen = family == name
        if not chosen.any():
            continue
        error = corrected[chosen] - reference[chosen]
        plain_error = plain[chosen] - reference[chosen]
        print(f"  {name:<11}{int(chosen.sum()):>6}{np.sqrt(np.mean(error**2)):>15.2f}{np.abs(error).max():>9.2f}"
              f"{np.sqrt(np.mean(plain_error**2)):>11.2f}")
    error = corrected - reference
    print(f"  {'all':<11}{len(error):>6}{np.sqrt(np.mean(error**2)):>15.2f}{np.abs(error).max():>9.2f}"
          f"{np.sqrt(np.mean((plain - reference)**2)):>11.2f}")


if __name__ == "__main__":
    main()
