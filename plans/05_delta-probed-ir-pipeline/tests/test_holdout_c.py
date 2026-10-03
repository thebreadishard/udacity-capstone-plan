"""P3-4 (decision 54, 3 Oct 2026): hold-out (c) in E6.splits — ids in the frozen file leave the pool and are never in (a) or (b); an absent file
changes nothing; comments and blank lines in the file are ignored; the psi4 worker's geometry.json carries charge and multiplicity."""
import re
import sys
from pathlib import Path

import pytest

PLAN = Path(__file__).resolve().parents[1]
M05 = PLAN / "modules" / "05_support_predictor"
sys.path.insert(0, str(M05 / "m05"))
E6 = pytest.importorskip("e6_learning_curve")


def _mols():
    mols = {}
    for k in range(12):
        mols[f"A_{k:010d}"] = {"layer": "A", "core": f"A_{k:010d}"}
    for core in ("x", "y", "z"):
        for k in range(3):
            mols[f"A2_{core}{k:09d}"] = {"layer": "A2", "core": core}
    for k in range(6):
        mols[f"P3_{k:010d}"] = {"layer": "P3", "core": f"P3_{k:010d}"}
    return mols


def test_absent_file_keeps_everything_in_pool_or_ab(tmp_path, monkeypatch):
    monkeypatch.setattr(E6, "HOLDOUT_C_FILE", tmp_path / "none.txt")
    mols = _mols()
    a, b, cores, pool = E6.splits(mols)
    assert set(a) | set(b) | set(pool) == set(mols)
    assert E6.holdout_c(mols) == []


def test_listed_ids_leave_the_pool(tmp_path, monkeypatch):
    f = tmp_path / "holdout_c.txt"
    f.write_text("# parents of pool 3\nP3_0000000001\n\nP3_0000000004\nnot_in_corpus\n", encoding="utf-8")
    monkeypatch.setattr(E6, "HOLDOUT_C_FILE", f)
    mols = _mols()
    a, b, cores, pool = E6.splits(mols)
    c = E6.holdout_c(mols)
    assert set(c) == {"P3_0000000001", "P3_0000000004"}
    assert not set(c) & set(pool) and not set(c) & set(a) and not set(c) & set(b)
    assert set(a) | set(b) | set(pool) | set(c) == set(mols)


def test_worker_geometry_carries_charge_and_multiplicity():
    src = (M05 / "corpus" / "psi4_worker.py").read_text(encoding="utf-8")
    assert re.search(r'"charge": int\(d\["charge"\]\), "multiplicity": int\(d\["multiplicity"\]\)', src)
