"""rungC_eval_saved.py --holdout-b-file (8 Oct 2026): the coverage test reads (b) on the frozen pre-merge list; new children of the (b) scaffolds that the
corpus split adds are read apart as (b+), and frozen ids the loader does not admit drop out as the trainer drops them."""
import argparse
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


KEYS = {"x1": ("c1ccccc1", 0), "x2": ("Cc1ccccc1", 0), "gone": ("Oc1ccccc1", 0), "p1": ("Nc1ccccc1", 0), "B_twin": ("c1ccccc1", 0),
        "P3c_x1": ("c1ccccc1", 1)}


def test_eval_sets_read_an_explicit_list_and_refuse_trained_ids(tmp_path):
    """--eval-ids-file (12 Oct 2026; chain 41, TASKS 49): unadmitted ids drop out and are counted; any trained id refuses the set."""
    f = tmp_path / "s5.txt"
    f.write_text("# five-ring neutrals\nx1\nx2\ngone\n", encoding="utf-8")
    sets = ES.eval_sets([f"s5={f}"], admitted={"x1": 0, "x2": 0, "p1": 0}, train_ids=["p1"], keys=KEYS, substituted=["x2"])
    assert sets["s5"]["ids"] == ["x1", "x2"] and sets["s5"]["dropped"] == ["gone"] and sets["s5"]["n_analytic"] == 1
    with pytest.raises(SystemExit, match="training set"):
        ES.eval_sets([f"s5={f}"], admitted={"x1": 0, "x2": 0}, train_ids=["x1"], keys=KEYS)


def test_eval_sets_refuse_a_trained_molecule_under_another_id_or_charge(tmp_path):
    """TASKS 157 (30 Oct 2026): v1.3 trained on two hold-out (a) molecules as their layer-B twins. TASKS 253: a model that trained a
    listed molecule's radical cation carries its correction onto the neutral, so that is no test either."""
    f = tmp_path / "s5.txt"
    f.write_text("x1\nx2\n", encoding="utf-8")
    with pytest.raises(SystemExit, match=r"under other ids or charges \(B_twin\)"):
        ES.eval_sets([f"s5={f}"], admitted={"x1": 0, "x2": 0}, train_ids=["B_twin"], keys=KEYS)
    with pytest.raises(SystemExit, match=r"under other ids or charges \(P3c_x1\) — not a test \(TASKS 157, 253\)"):
        ES.eval_sets([f"s5={f}"], admitted={"x1": 0, "x2": 0}, train_ids=["P3c_x1"], keys=KEYS)
    assert ES.eval_sets([f"s5={f}"], admitted={"x1": 0, "x2": 0}, train_ids=["p1"], keys=KEYS)["s5"]["ids"] == ["x1", "x2"]


def test_the_built_in_hold_out_b_refuses_a_trained_molecule_by_id_or_as_a_twin_of_any_charge(monkeypatch):
    """Hold-out (b) decides: it passes the same check as an --eval-ids-file set (TASKS 157, 253); so does an id overlap with (a)."""
    monkeypatch.setattr(ES.HT, "manifest_keys", lambda molecules: KEYS)
    a = argparse.Namespace(holdout_b_file=None, eval_ids_file=[], molecules="corpus/molecules")
    held = {"a": ["x2"], "b": ["x1"]}
    assert [s[0] for s in ES.measurement_sets(a, {}, held, ["p1"], [])] == ["a", "b"]
    for trained, why in ((["x1"], r"hold-out \(b\): 1 ids are in the model's training set \(x1\)"),
                         (["x2"], r"hold-out \(a\): 1 ids are in the model's training set \(x2\)"),
                         (["P3c_x1"], r"hold-out \(b\): the training set holds 1 of its molecules under other ids or charges \(P3c_x1\)"),
                         (["B_twin"], r"hold-out \(b\): .* \(B_twin\) — not a test \(TASKS 157, 253\)")):
        with pytest.raises(SystemExit, match=why):
            ES.measurement_sets(a, {}, held, trained, [])


def test_the_built_in_hold_out_a_names_its_trained_twins_and_reads_on(monkeypatch, capsys):
    """Hold-out (a)'s ten decide nothing since 16 Nov (the clean eight do), and the carried version trained two of its molecules'
    neutral twins: a twin of any charge is named in the log and the record, not refused."""
    monkeypatch.setattr(ES.HT, "manifest_keys", lambda molecules: KEYS)
    a = argparse.Namespace(holdout_b_file=None, eval_ids_file=[], molecules="corpus/molecules")
    held = {"a": ["x1"], "b": ["x2"]}
    sets = ES.measurement_sets(a, {}, held, ["B_twin", "P3c_x1", "p1"], [])
    assert sets[0] == ("a", ["x1"], {"trained_twins": ["B_twin", "P3c_x1"]}) and sets[1] == ("b", ["x2"], {})
    assert ("hold-out (a): the model trained twins of 2 of its molecules (B_twin, P3c_x1) — not a held-out read for those molecules; the "
            "clean eight decide") in capsys.readouterr().out
    assert ES.measurement_sets(a, {}, held, ["p1"], [])[0][2] == {"trained_twins": []}


def test_eval_sets_refuse_a_taken_name_or_a_malformed_spec(tmp_path):
    f = tmp_path / "t.txt"
    f.write_text("x1\n", encoding="utf-8")
    for specs in ([f"b={f}"], [f"t={f}", f"t={f}"], [str(f)]):
        with pytest.raises(SystemExit):
            ES.eval_sets(specs, admitted={"x1": 0}, train_ids=[], keys=KEYS)
