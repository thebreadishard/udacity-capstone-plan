"""Pins rung 4's psi4 job (`probes/rung4_jobs.job`) before its body moves into `probes/corpus_opt_jobs.py` (21 Nov 2026): the job a row
gives must not change, key for key, coordinate for coordinate."""
import hashlib
import json
import sys
from pathlib import Path

import pytest

pytest.importorskip("rdkit")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes"))
import rung4_jobs as R

ROW = {"id": "R4_37539913ef", "layer": "R4", "name": "benzo[c]phenanthrene", "smiles": "c1ccc2c(c1)ccc1ccc3ccccc3c12", "n_atoms": "30",
       "family": "benzo[c]phenanthrene", "test_family": "0", "curve_rank": "1"}
DECK = {"low_functional": "B3LYP", "threads": 8, "memory_gb": 24}
PINNED_SHA = "d83265b195bbe277e2bab90d764627726f561c83fe544c2d891e08ae6f951130"


def digest(job: dict) -> str:
    rounded = dict(job, xyz_angstrom=[[s, round(x, 8), round(y, 8), round(z, 8)] for s, x, y, z in job["xyz_angstrom"]])
    return hashlib.sha256(json.dumps(rounded, sort_keys=True).encode()).hexdigest()


def test_rung4_job_is_unchanged():
    job = R.job(ROW, DECK, "/root/labels/rung4/molecules")
    assert len(job["xyz_angstrom"]) == 30
    assert job["out_dir"] == "/root/labels/rung4/molecules/R4_37539913ef"
    assert (job["optimise"], job["hessians"], job["grid_check"]) == (True, False, False)
    assert job["source"] == {"list": "rung4_candidates_2026-10-14.csv", "family": "benzo[c]phenanthrene", "name": "benzo[c]phenanthrene",
                             "smiles": ROW["smiles"], "test_family": 0, "curve_rank": 1}
    assert digest(job) == PINNED_SHA
