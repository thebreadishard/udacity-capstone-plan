"""The anchor plan's cells (`probes/anchor_plan.py`): adjacency runs on textbook molecules, the ring context, aza and charge."""
import sys
from pathlib import Path

import pytest

pytest.importorskip("rdkit")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes"))
import anchor_plan as A  # noqa: E402  (after the sys.path insert)


@pytest.mark.parametrize(("smiles", "expected"), [
    ("c1ccccc1", {("sextet", "one", False, 0)}),                                     # benzene
    ("c1ccc2ccccc2c1", {("quartet", "two", False, 0)}),                               # naphthalene: two quartets
    ("c1ccc2cc3ccccc3cc2c1", {("quartet", "three+", False, 0), ("solo", "three+", False, 0)}),   # anthracene
    ("c1ccc2c(c1)ccc1ccccc12", {("quartet", "three+", False, 0), ("duo", "three+", False, 0)}),  # phenanthrene
    ("c1ccncc1", {("quintet", "one", True, 0)}),                                     # pyridine: the N breaks the ring once
    ("c1cc2cccc3c2c(c1)C=C3", {("trio", "three+-five", False, 0), ("duo5", "three+-five", False, 0)}),   # acenaphthylene
])
def test_cells_of_textbook_molecules(smiles, expected):
    assert A.cells(smiles, "A") == expected


def test_runs_are_counted_per_ring():
    from rdkit import Chem
    assert sorted(A.ch_runs(Chem.MolFromSmiles("c1ccc2ccccc2c1"))) == [(6, 4), (6, 4)]
    assert sorted(A.ch_runs(Chem.MolFromSmiles("Cc1ccccc1"))) == [(6, 5)]                # toluene: a quintet


def test_a_cation_layer_sets_the_charge():
    assert A.cells("c1ccc2ccccc2c1", "P3c") == {("quartet", "two", False, 1)}


def test_an_unreadable_smiles_is_refused():
    with pytest.raises(ValueError, match="unreadable"):
        A.cells("c1cc", "A")
