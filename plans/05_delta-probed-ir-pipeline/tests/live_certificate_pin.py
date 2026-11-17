"""The inputs of the live certificate's pin (`tests/test_m08_live_certificate_pin.py`), built with whatever `m08` the caller hands in:
the test hands in this checkout's, and the pin was written by handing in master's (17 Nov 2026, before decision 66 reached it), so
that a certificate of measurement networks is held to what it was, every byte of record and page.

The certificate is of the frozen pin corpus's benzene after a zero correction by v1.3's three networks: its accuracy, licence and
seen line come from v1.3's tracked records; no checkpoint is opened (the caller replaces `pipeline.train_ids`, and the hashes are
the product-error record's own), no catalogue is read, and the three fields that move between builds are blanked."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import numpy as np

BENZENE = "A_8448043181"
V13 = tuple(f"E7_rungC_chain35_analytic_model_n750_seed{s}.pt" for s in range(3))


class NoCatalog:
    """A catalogue that lists nothing and knows no laboratory tolerance."""

    def find(self, smiles: str) -> None:
        return None

    def u_band(self, species: str) -> dict:
        return {}


def build(m08: dict, corpus_benzene: Path, work: Path) -> dict:
    """{"record", "page"} of the certificate; `m08` holds the modules `accuracy`, `live_certificate` and `pipeline` of one checkout."""
    A, LC, P = m08["accuracy"], m08["live_certificate"], m08["pipeline"]
    with open(A.M05_OUT / f"E7_rungC_chain35_analytic{A.PRODUCT_SUFFIX}", encoding="utf-8") as f:
        hashes = json.load(f)["model_sha16"]
    entries = [{"path": f"out/{name}", "sha16": hashes[name], "network": P.NETWORK, "version": "1.3", "status": "carried"} for name in V13]
    d = work / BENZENE
    shutil.copytree(corpus_benzene, d)
    zero = np.zeros((36, 36))
    P.save_correction(d, zero, [zero] * 3, tuple(Path(n) for n in V13))
    P.write_json(d / "pipeline.json", {"pipeline_version": "pin", "name": "benzene", "spectra": P.spectra(d, zero, [zero] * 3),
                                       "admission": {"smiles": "c1ccccc1", "formula": "C6H6", "n_atoms": 12, "elements": ["C", "H"],
                                                     "training_atoms": [6, 40], "inside_training_sizes": True, "models": entries},
                                       "seconds": {"low_level": 60.0}, "provenance": {"host": "laptop", "commit": "0" * 40, "dirty": False},
                                       "deck": {"sha16": "d" * 16}, "low_level": {"b3lyp": {"software": {"pyscf": "2.15.0"}}}})
    c = LC.certificate(d, NoCatalog())
    c["date"] = c["provenance"]["certificate_commit"] = c["provenance"]["result"] = "-"
    return {"record": json.loads(json.dumps(c, ensure_ascii=False, default=str)), "page": LC.to_markdown(c)}
