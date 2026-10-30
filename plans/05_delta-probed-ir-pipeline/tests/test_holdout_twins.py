"""Hold-out twins in the trainer's pool (`m05/holdout_twins.py`, `rungC_train.drop_twins`; TASKS 157, the user's decision of 30 Oct 2026):
a pool molecule that is a hold-out molecule under another id leaves the pool under --holdout-twins drop and stays under keep; a cation is
not its neutral parent; an id without a manifest row is refused."""
from __future__ import annotations

import csv
import sys
from types import SimpleNamespace

import pytest

from pin_tools import PLAN

sys.path.insert(0, str(PLAN / "modules" / "05_support_predictor" / "m05"))
import holdout_twins as HT
import rungC_train as RT

ROWS = [("A_cn", "A", "c1ccc(C#N)cc1"), ("B_twin", "B", "N#Cc1ccccc1"), ("B_tol", "B", "Cc1ccccc1"), ("P3c_cn", "P3c", "N#Cc1ccccc1"),
        ("A_naph", "A", "c1ccc2ccccc2c1")]


@pytest.fixture
def molecules(tmp_path):
    with (tmp_path / "manifest.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id", "layer", "smiles"])
        w.writeheader()
        w.writerows({"id": i, "layer": layer, "smiles": s} for i, layer, s in ROWS)
    (tmp_path / "molecules").mkdir()
    return tmp_path / "molecules"


def test_a_twin_leaves_the_pool_and_a_cation_does_not(molecules):
    cfg = SimpleNamespace(holdout_twins="drop", molecules=str(molecules))
    logged = []
    pool, dropped = RT.drop_twins(cfg, ["B_twin", "B_tol", "P3c_cn", "A_naph"], ["A_cn"], logged.append)
    assert dropped == ["B_twin"] and pool == ["B_tol", "P3c_cn", "A_naph"]
    assert "B_twin" in logged[0]


def test_keep_reproduces_the_old_pool(molecules):
    cfg = SimpleNamespace(holdout_twins="keep", molecules=str(molecules))
    assert RT.drop_twins(cfg, ["B_twin", "B_tol"], ["A_cn"], print) == (["B_twin", "B_tol"], [])


def test_no_twin_changes_nothing_and_an_unknown_id_is_refused(molecules):
    keys = HT.manifest_keys(molecules)
    assert HT.twins(["B_tol", "A_naph"], ["A_cn"], keys) == []
    with pytest.raises(KeyError, match="A_gone"):
        HT.twins(["B_tol"], ["A_gone"], keys)


def test_the_config_default_is_drop():
    assert RT.TrainConfig.model_fields["holdout_twins"].default == "drop"
