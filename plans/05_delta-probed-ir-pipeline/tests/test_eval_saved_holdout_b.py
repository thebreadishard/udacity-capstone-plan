"""rungC_eval_saved.py --holdout-b-file (8 Oct 2026): the coverage test reads (b) on the frozen pre-merge list; new children of the (b) scaffolds that the
corpus split adds are read apart as (b+), and frozen ids the loader does not admit drop out as the trainer drops them."""
import sys
from pathlib import Path

import pytest

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
import rungC_eval_saved as ES  # noqa: E402


def test_split_holdout_b_freezes_the_list_and_separates_the_new_children():
    derived = ["b1", "b2", "new1", "new2"]           # what E6.splits gives after the merge
    frozen = ["b1", "b2", "b3"]                      # b3: not admitted by the loader (e.g. imaginary) — dropped, as in the trainer
    b, b_plus = ES.split_holdout_b(derived, frozen, admitted={"b1": 0, "b2": 0, "new1": 0, "new2": 0, "pool1": 0})
    assert b == ["b1", "b2"] and b_plus == ["new1", "new2"]


def test_split_holdout_b_refuses_a_list_with_no_admitted_id():
    with pytest.raises(SystemExit):
        ES.split_holdout_b(["b1"], ["x", "y"], admitted={"b1": 0})


def test_training_ids_come_from_the_checkpoint_when_it_has_them():
    """8 Oct 2026: after a merge, the first n of today's pool is no longer the model's training set; the checkpoint's own list is used."""
    pool = ["new1", "p1", "p2", "p3"]
    tr, src = ES.training_ids({"n": 2, "train_ids": ["p1", "p2", "gone"]}, pool, admitted={"p1": 0, "p2": 0, "p3": 0, "new1": 0})
    assert tr == ["p1", "p2"] and src == "checkpoint"
    tr, src = ES.training_ids({"n": 2}, pool, admitted={})
    assert tr == ["new1", "p1"] and src.startswith("pool order")
