"""Pins rung 4's psi4 job (`probes/rung4_jobs.job`) after its body moved into `probes/corpus_opt_jobs.py` (21 Nov 2026): the job a row
gives must not change. Everything but the coordinates is pinned by a digest taken before the move; the coordinates are RDKit's embedding,
which differs between platforms in the last digits (the first pin, with coordinates, held on Windows and failed on the Linux CI), so they
are compared with the corpus's own `run_corpus.start_geometry` for the same row, the call the job is defined by."""
import hashlib
import json
import sys
from pathlib import Path

import pytest

pytest.importorskip("rdkit")
PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
sys.path.insert(0, str(PLAN / "modules" / "05_support_predictor" / "corpus"))
import rung4_jobs as R  # noqa: E402  (after the sys.path inserts)
from run_corpus import start_geometry  # noqa: E402

ROW = {"id": "R4_37539913ef", "layer": "R4", "name": "benzo[c]phenanthrene", "smiles": "c1ccc2c(c1)ccc1ccc3ccccc3c12", "n_atoms": "30",
       "family": "benzo[c]phenanthrene", "test_family": "0", "curve_rank": "1"}
DECK = {"low_functional": "B3LYP", "threads": 8, "memory_gb": 24}
PINNED_SHA = "5acb03f78f45a4d0f8a59c806f8f41685c676fd0a8712c9fa0f51e268eb22330"   # rung4_jobs.py of commit 9bf1a360, before the move


def digest(job: dict) -> str:
    """Of the job with each atom's coordinates left out (its element kept, in order)."""
    return hashlib.sha256(json.dumps(dict(job, xyz_angstrom=[a[0] for a in job["xyz_angstrom"]]), sort_keys=True).encode()).hexdigest()


def test_rung4_job_is_unchanged():
    job = R.job(ROW, DECK, "/root/labels/rung4/molecules")
    assert len(job["xyz_angstrom"]) == 30
    assert job["out_dir"] == "/root/labels/rung4/molecules/R4_37539913ef"
    assert (job["optimise"], job["hessians"], job["grid_check"]) == (True, False, False)
    assert job["source"] == {"list": "rung4_candidates_2026-10-14.csv", "family": "benzo[c]phenanthrene", "name": "benzo[c]phenanthrene",
                             "smiles": ROW["smiles"], "test_family": 0, "curve_rank": 1}
    assert digest(job) == PINNED_SHA
    xyz, _ = start_geometry({**ROW, "qm9_label": ""})
    assert job["xyz_angstrom"] == [[s, float(x), float(y), float(z)] for s, x, y, z in xyz]
