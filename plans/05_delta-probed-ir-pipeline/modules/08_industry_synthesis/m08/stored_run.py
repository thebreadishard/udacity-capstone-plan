"""A stored pipeline run, read back without computing anything (20 November 2026).

The notebook of a submitted module cannot run the pipeline: its steps need psi4, pyscf and the networks' weights. What it can
show is a result the pipeline stored - one run's certificate, as JSON - so that a reader sees what the product prints for a
molecule and how a band's licence reads. The run is named here once. `m08/make_snapshot.py` opens it through this module too, so
the snapshot of a submitted repository holds the file.

The record says which pipeline version wrote it, and the notebook prints that: a stored run is evidence of that version, not of
the newest one.
"""
from __future__ import annotations

import json

from . import paths

STORED_RUN = "probes/results_m1/pipeline_benzene_anharmonic_v3_2026-11-19/benzene"   # carried network v1.4, release networks
CERTIFICATE = "certificate.json"
KIND = "live certificate"              # m08/live_certificate.py's records; the catalogue's certificates are another kind


def certificate(folder: str = STORED_RUN) -> dict:
    """The certificate record of the stored run in `folder` (plan-relative).

    A file that is not a pipeline certificate is refused: the notebook's table reads fields only that kind has.
    """
    path = paths.resolve(f"{folder}/{CERTIFICATE}")
    record = json.loads(path.read_text(encoding="utf-8"))
    if record.get("kind") != KIND:
        raise ValueError(f"{path}: kind {record.get('kind')!r}, not a pipeline certificate ({KIND!r})")
    return record


def band_rows(record: dict, strongest: int = 8) -> list[dict]:
    """The `strongest` bands of a pipeline certificate as the reader's table, in order of position.

    Each row holds what the certificate prints for the band: the printed position and which kind it is (the anharmonic estimate
    or the harmonic one), the network's harmonic position with the range of its seeds, the uncorrected B3LYP position and the
    scaled baseline, the height, the family, and two different error statements that must not be mixed. The licence and the
    family error are about the network's harmonic ω against the DFT proxy. The step's bar is the anharmonic step's own error
    against its label, for a band printed as ν; no licence is claimed for ν.
    """
    if strongest < 1:
        raise ValueError(f"strongest = {strongest}: at least one band")
    top = sorted(record["bands"], key=lambda b: -b["km_mol"])[:strongest]
    return [{"printed (cm⁻¹)": b["printed_cm"], "printed as": b["printed"], "network ω": b["network_cm"],
             "seeds' range": f"{b['seed_range_cm'][0]}–{b['seed_range_cm'][1]}", "B3LYP ω": b["b3lyp_cm"],
             "scaled B3LYP": b["baseline_cm"], "height (km/mol)": b["km_mol"], "family": b["family"],
             "ω: family error (a) / (b)": f"{b['error_cm']['a']} / {b['error_cm']['b']}", "ω licensed": b["licensed"],
             "ν: the step's error bar": b["step_bar_cm"] if b["step_bar_cm"] is not None else "—"}
            for b in sorted(top, key=lambda b: b["printed_cm"])]
