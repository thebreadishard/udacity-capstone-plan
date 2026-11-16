"""What the certificate says about bands the audit named (K3, K4, K5): corpus molecules through the bundled release.

Read-only. Runs with whichever aromir is first on the path, so the same script reads main and a branch:

    python certificate_claims.py <plan folder>

Per molecule: the bands, how many are licensed, the reasons the others are not (an aromir before the per-band licence has no
reason field: 'family' is printed), every X–H stretch on a heteroatom with its licence, and what the certificate says the
measured error does not cover.
"""
from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from aromir import admission, certificate, families, release, response
from aromir import vibrations as vib
from aromir.lowlevel import LowLevel
from aromir.molecule import Geometry

LOW_HESSIAN = "hessian_b3lyp_analytic.npz"
WANT = {"Oc1ccccc1": "phenol", "Nc1ccc2ccccc2c1": "2-naphthylamine", "N#Cc1ccccc1": "benzonitrile",
        "c1ccc(-c2ccccc2)cc1": "biphenyl", "c1ccccc1": "benzene"}
LARGE = "T_c874e3c6cf"   # ovalene, 46 atoms: outside v1.3's training sizes (8-30)


def record_of(folder: Path, loaded: release.Release) -> dict:
    stored = json.loads((folder / "geometry.json").read_text(encoding="utf-8"))
    geometry = Geometry(tuple(s[0].upper() + s[1:].lower() for s in stored["symbols"]), np.array(stored["coords_bohr"], float))
    with np.load(folder / LOW_HESSIAN) as low:
        hessian = np.array(low["H_projected"], float)
    low_level = LowLevel(energy=0.0, hessian=hessian, polar_tensor=np.zeros((3, len(hessian))),
                         refinement=response.Refinement(0.0, 0.0, 0, 0), sum_rule_violation=0.0, seconds=0.0)
    admitted = admission.admit(admission.parse_smiles(stored.get("smiles") or folder.name)) if stored.get("smiles") else None
    return geometry, low_level, admitted


def main() -> None:
    plan = Path(sys.argv[1]).resolve()
    corpus = plan / "modules" / "05_support_predictor" / "corpus"
    loaded = release.load(release.bundled())
    with (corpus / "manifest.csv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    chosen = {}
    for row in rows:
        if row["smiles"] in WANT and row["smiles"] not in chosen and (corpus / "molecules" / row["id"] / LOW_HESSIAN).is_file():
            chosen[row["smiles"]] = row["id"]
    chosen.update({row["smiles"]: row["id"] for row in rows if row["id"] == LARGE})
    print(f"aromir from {Path(release.__file__).resolve().parents[2]}, release v{loaded.network_version}")
    for smiles, molecule_id in chosen.items():
        geometry, low_level, _ = record_of(corpus / "molecules" / molecule_id, loaded)
        admitted = admission.admit(admission.parse_smiles(smiles))
        corrections = loaded.corrections(geometry, low_level.hessian)
        record = certificate.build(admitted, geometry, low_level, corrections, loaded)
        bands = record["bands"]
        notes = Counter(band.get("licence_note", "family") or "licensed" for band in bands if not band["licensed"])
        print(f"{WANT.get(smiles, smiles)} ({molecule_id}, {geometry.n_atoms} atoms): {len(bands)} bands, "
              f"{sum(band['licensed'] for band in bands)} licensed; not licensed: {dict(notes)}")
        modes = vib.vibrational_modes(low_level.hessian, geometry)
        if hasattr(families, "hydrogen_carriers"):
            carriers = families.hydrogen_carriers(geometry, modes)
            n_hetero = sum(f == "CH-stretch" and c != "C" for f, c in zip(families.classify(geometry, modes), carriers, strict=True))
            print(f"    B3LYP modes the rule calls CH-stretch whose hydrogens sit on N, O or S: {n_hetero}")
        for band in bands[-3:]:
            print(f"    {band['wavenumber_cm']:>8} {band['family']:<11} licensed {band['licensed']} {band.get('licence_note', '')}")
        for line in record.get("not_in_the_error", ["(this aromir's certificate has no such section)"]):
            print(f"    not in the error: {line[:150]}")


if __name__ == "__main__":
    main()
