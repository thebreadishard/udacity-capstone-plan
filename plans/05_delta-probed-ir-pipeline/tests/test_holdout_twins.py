"""Hold-out twins in the trainer's pool (`m05/holdout_twins.py`, `rungC_train.drop_twins`; TASKS 157, the user's decision of 30 Oct 2026):
a pool molecule that is a hold-out molecule under another id leaves the pool under --holdout-twins drop and stays under keep; a cation is
not its neutral parent under drop and is its twin under drop-any-charge (TASKS 253); an id without a manifest row is refused."""
from __future__ import annotations

import argparse
import csv
import sys
from types import SimpleNamespace
from typing import get_args

import pytest

from pin_tools import PLAN

sys.path.insert(0, str(PLAN / "modules" / "05_support_predictor" / "m05"))
import holdout_twins as HT
import rungC_config as RC
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
    cfg = SimpleNamespace(holdout_twins="drop", network_kind="measurement", molecules=str(molecules))
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
    assert get_args(RT.TrainConfig.model_fields["holdout_twins"].annotation) == ("drop", "drop-any-charge", "keep")
    ap = argparse.ArgumentParser()
    RC._holdout_arguments(ap)
    assert ap.parse_args([]).holdout_twins == "drop"
    assert ap.parse_args(["--holdout-twins", "drop-any-charge"]).holdout_twins == "drop-any-charge"


def test_drop_any_charge_also_drops_the_cation_of_a_held_molecule(molecules):
    """TASKS 253: benzene's radical cation stayed in the pool under drop and carried its correction onto benzene's read."""
    cfg = SimpleNamespace(holdout_twins="drop-any-charge", network_kind="measurement", molecules=str(molecules))
    logged = []
    pool, dropped = RT.drop_twins(cfg, ["B_twin", "B_tol", "P3c_cn", "A_naph"], ["A_cn"], logged.append)
    assert dropped == ["B_twin", "P3c_cn"] and pool == ["B_tol", "A_naph"]
    assert "B_twin, P3c_cn" in logged[0]


def test_any_charge_keys_by_the_skeleton_alone(molecules):
    keys = HT.manifest_keys(molecules)
    assert HT.twins(["P3c_cn", "B_tol"], ["A_cn"], keys) == []
    assert HT.twins(["P3c_cn", "B_tol"], ["A_cn"], keys, any_charge=True) == ["P3c_cn"]
    assert HT.twins(["A_cn", "B_tol"], ["P3c_cn"], keys, any_charge=True) == ["A_cn"]           # the neutral of a held cation too
