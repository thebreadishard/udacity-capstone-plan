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


@pytest.mark.parametrize(("smiles", "layer", "inside"), [
    ("c1ccc2ccccc2c1", "A", True), ("c1ccc2ncccc2c1", "B", True), ("c1cc2cccc3c2c(c1)C=C3", "A", True),   # naphthalene, quinoline, acenaphthylene
    ("c1ccc2occc2c1", "A2", False), ("c1ccsc1", "B", False),                                           # benzofuran, thiophene
    ("C1CCCCC1", "B", False), ("c1ccccc1", "C", False), ("c1ccccc1", "P3c", True)])                    # no aromatic six-ring, QM9, a cation
def test_the_target_domain(smiles, layer, inside):
    assert A.in_domain(smiles, layer) is inside


def test_basis_functions_and_the_price_rule():
    assert A.basis_functions("c1ccc2ncccc2c1") == 175                       # quinoline, the rule's reference
    assert A.anchor_hours(17, 175) == pytest.approx((6 * 17 + 7) / 4.6)     # ≈ 23.7 h; measured 25.8 and 28.4 h
    assert A.anchor_hours(17, 350) == pytest.approx(A.anchor_hours(17, 175) * 32)
    with pytest.raises(ValueError, match="no basis count"):
        A.basis_functions("c1ccccc1[Br]")


def test_the_selection_covers_every_cell_at_the_lowest_price():
    rows = {"cheap_ab": {"cells": [("a",), ("b",)], "eur": 1.0, "n_atoms": 10},
            "cheap_a": {"cells": [("a",)], "eur": 1.0, "n_atoms": 10},
            "dear_b": {"cells": [("b",)], "eur": 9.0, "n_atoms": 30},
            "dear_ab": {"cells": [("a",), ("b",)], "eur": 20.0, "n_atoms": 30}}
    assert A.select(rows, {("a",): 1, ("b",): 1}) == ["cheap_ab"]
    assert sorted(A.select(rows, {("a",): 2, ("b",): 2})) == ["cheap_a", "cheap_ab", "dear_b"]   # b's second place: dear_b (9) before dear_ab
    rows["only_c"] = {"cells": [("c",)], "eur": 5.0, "n_atoms": 12}
    assert "only_c" in A.select(rows, dict.fromkeys(A.cell_members(rows), 2))  # a cell with one candidate is filled as far as it goes


def test_the_fill_plan_counts_computed_molecules_and_fills_the_rest():
    rows = {"done_a": {"cells": [("a",)], "dft_hours": 1.0, "n_atoms": 10},
            "pend_a": {"cells": [("a",)], "dft_hours": 1.0, "n_atoms": 10},
            "pend_ab": {"cells": [("a",), ("b",)], "dft_hours": 1.5, "n_atoms": 20},       # two places for 1.5 h: the best ratio
            "pend_b": {"cells": [("b",)], "dft_hours": 1.0, "n_atoms": 10}}
    per_cell, chosen = A.fill_plan(rows, {"done_a"}, 2)
    assert per_cell == {("a",): (1, 1), ("b",): (0, 2)}
    assert sorted(chosen) == ["pend_ab", "pend_b"]                              # pend_ab fills a and b; pend_b the second b


def test_the_power_law_fit():
    a, b = A.fit_power_law([(100, 1000.0), (200, 8000.0), (400, 64000.0)])
    assert b == pytest.approx(3.0) and a == pytest.approx(float(__import__("numpy").log(1000.0 / 100 ** 3)))
    with pytest.raises(SystemExit, match="at least three"):
        A.fit_power_law([(1, 1.0), (2, 2.0)])


def test_an_unreadable_smiles_is_refused():
    with pytest.raises(ValueError, match="unreadable"):
        A.cells("c1cc", "A")
