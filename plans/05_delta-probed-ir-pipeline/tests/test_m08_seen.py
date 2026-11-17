"""Has the network seen the molecule? (`modules/08_industry_synthesis/m08/seen.py`, TASKS 155): every role on a synthetic index, the match by
canonical SMILES rather than by id, a hold-out molecule trained on under a twin id, and the truth set beside a spectrum."""
from __future__ import annotations

import json
import sys

import numpy as np
import pytest

from pin_tools import PLAN

sys.path.insert(0, str(PLAN / "modules" / "08_industry_synthesis"))
from m08 import pipeline as P
from m08 import seen as S

SMILES = {"A_naph": "c1ccc2ccccc2c1", "A_benz": "c1ccccc1", "B_twin": "N#Cc1ccccc1", "A_cn": "c1ccc(C#N)cc1", "B_tol": "Cc1ccccc1"}
SEEN = S.build({"A_naph", "B_twin"}, {"a": {"A_benz", "A_cn"}, "b": set()}, SMILES)


@pytest.mark.parametrize(("smiles", "listed", "role", "ids"), [
    ("C1=CC=C2C=CC=CC2=C1", None, "trained", ["A_naph"]),          # another writing of naphthalene
    ("c1ccccc1", "A_benz", "a", ["A_benz"]),
    ("N#Cc1ccccc1", "A_cn", "trained_and_held_out", ["B_twin"]),
    ("Cc1ccccc1", "B_tol", "catalogue", ["B_tol"]),
    ("c1ccc2cc3ccccc3cc2c1", None, "unseen", []),
])
def test_each_role_by_canonical_smiles(smiles, listed, role, ids):
    got = S.status(smiles, SEEN, listed)
    assert (got["role"], got["ids"]) == (role, ids)
    assert all(i in got["text"] for i in ids)


def test_a_twin_says_the_hold_out_was_not_clean_and_is_listed_as_a_leak():
    assert "not clean" in S.status("N#Cc1ccccc1", SEEN, None)["text"]
    assert S.leaks(SEEN) == {"N#Cc1ccccc1": ("a", ["A_cn"], ["B_twin"])}


def test_an_id_outside_the_manifest_is_refused():
    with pytest.raises(KeyError, match="A_gone"):
        S.build({"A_gone"}, {"a": set()}, SMILES)


def test_no_truth_in_the_corpus_gives_none(tmp_path, monkeypatch):
    monkeypatch.setattr(P, "CORPUS", tmp_path)
    (tmp_path / "A_x").mkdir()
    assert S.truth_beside("A_x", [{"omega_cm": 1000.0, "km_mol": 1.0}]) is None


def test_the_truth_against_itself_is_exact():
    d = P.CORPUS / "A_8448043181"
    if not (d / P.TRUTH_HESSIAN).exists():
        pytest.skip("the corpus's benzene with its ωB97X Hessian is not on this machine")
    masses = np.asarray(json.loads((d / "geometry.json").read_text(encoding="utf-8"))["masses_amu"], float)
    own = S.series(d / P.TRUTH_HESSIAN, masses, S.cheap_apt(d))["sticks"]
    t = S.truth_beside("A_8448043181", own)
    assert t["rms_by_rank_cm"] == 0.0 and t["overlap"] == pytest.approx(1.0) and t["n_bands"] == len(own)
    assert S.truth_beside("A_8448043181", own[1:])["rms_by_rank_cm"] is None          # unequal counts are not paired by rank


def test_the_carried_models_index_names_the_two_hold_out_twins():
    models = tuple(sorted((P.M05 / "out").glob("E7_rungC_chain35_analytic_model_n750_seed*.pt")))
    if len(models) != 3 or not S.MANIFEST.exists():
        pytest.skip("the carried models or the manifest are not on this machine")
    held = {v[1][0] for v in S.leaks(S.load(models)).values()}
    assert held == {"A_07cadc7923", "A_3100da3761"}                                  # 2-naphthoic acid and benzonitrile (30 Oct 2026)


CATIONS = {"P3c_benz": "c1ccccc1", "P3c_tol": "Cc1ccccc1", "P3c_naph": "c1ccc2ccccc2c1"}
WITH_CATIONS = S.build({"A_naph", "B_twin", "P3c_benz", "P3c_tol"}, {"a": {"A_benz", "A_cn"}, "b": set()}, SMILES, CATIONS)


@pytest.mark.parametrize(("smiles", "listed", "role", "cation"), [
    ("c1ccccc1", "A_benz", "a", "P3c_benz"),                 # a hold-out molecule whose cation was trained stays held out
    ("Cc1ccccc1", "B_tol", "catalogue", "P3c_tol"),          # a cation never makes its parent 'trained'
])
def test_a_trained_cation_gives_its_parent_a_clause_not_a_role(smiles, listed, role, cation):
    got = S.status(smiles, WITH_CATIONS, listed)
    plain = S.status(smiles, SEEN, listed)
    assert (got["role"], got["ids"], got["cation_trained"]) == (role, plain["ids"], [cation])
    assert got["text"] == f"{plain['text']}; " + S.TEXT["cation_trained"].format(ids=cation)
    assert WITH_CATIONS.trained == SEEN.trained and WITH_CATIONS.cations == {"c1ccccc1": ["P3c_benz"], "Cc1ccccc1": ["P3c_tol"]}


@pytest.mark.parametrize("smiles", ["c1ccc2ccccc2c1", "N#Cc1ccccc1", "c1ccc2cc3ccccc3cc2c1"])
def test_a_molecule_without_a_trained_cation_is_unchanged(smiles):
    assert S.status(smiles, WITH_CATIONS, None) == S.status(smiles, SEEN, None)          # P3c_naph is a row, but was not trained


def test_a_cation_twin_is_not_a_leak():
    assert S.leaks(WITH_CATIONS) == S.leaks(SEEN)


def test_an_id_outside_the_manifest_is_refused_beside_cation_rows():
    with pytest.raises(KeyError, match="A_gone"):
        S.build({"A_gone", "P3c_benz"}, {"a": set()}, SMILES, CATIONS)


def test_load_reads_the_cation_rows_of_the_manifest(tmp_path, monkeypatch):
    manifest = tmp_path / "manifest.csv"
    manifest.write_text("id,smiles,layer\nA_benz,c1ccccc1,A\nB_tol,Cc1ccccc1,B\nP3c_benz,c1ccccc1,P3c\n", encoding="utf-8")
    record = tmp_path / "eval.json"
    record.write_text(json.dumps({"a": {"per_molecule": {"A_benz": {}}}, "b": {"per_molecule": {}}}), encoding="utf-8")
    monkeypatch.setattr(S, "MANIFEST", manifest)
    monkeypatch.setattr(P, "train_ids", lambda models: {"B_tol", "P3c_benz"})
    monkeypatch.setattr(S.A, "evaluation_records", lambda keys: [record] if keys == ("v14/m.pt",) else pytest.fail(f"keys {keys}"))
    model = S.A.M05_OUT / "v14" / "m.pt"             # the records are found by the model's key under module 05's out/ (TASKS 264)
    seen = S.load((model,))
    assert (seen.trained, seen.holdout, seen.cations) == ({"Cc1ccccc1": ["B_tol"]}, {"c1ccccc1": ("a", ["A_benz"])}, {"c1ccccc1": ["P3c_benz"]})
    assert S.status("c1ccccc1", seen, "A_benz")["cation_trained"] == ["P3c_benz"]
    monkeypatch.setattr(P, "train_ids", lambda models: {"B_tol", "P3c_gone"})
    with pytest.raises(KeyError, match="P3c_gone"):
        S.load((model,))


BOTH = S.build({"A_naph", "B_twin", "P3c_naph", "P3c_cn"}, {"a": {"A_benz", "A_cn"}, "b": set()}, SMILES,
               CATIONS | {"P3c_cn": "N#Cc1ccccc1"})


@pytest.mark.parametrize(("smiles", "role", "ids", "cation"), [
    ("c1ccc2ccccc2c1", "trained", ["A_naph"], "P3c_naph"),                   # trained itself, and its cation too
    ("N#Cc1ccccc1", "trained_and_held_out", ["B_twin"], "P3c_cn"),           # a hold-out twin trained, and its cation too
])
def test_a_trained_cation_beside_a_trained_parent_adds_its_clause(smiles, role, ids, cation):
    got = S.status(smiles, BOTH, None)
    assert (got["role"], got["ids"], got["cation_trained"]) == (role, ids, [cation])
    assert got["text"] == f"{S.status(smiles, SEEN, None)['text']}; " + S.TEXT["cation_trained"].format(ids=cation)


def test_the_cations_of_measurement_and_release_networks_are_one_list():
    release = S.build({"A_naph", "P3c_benz", "P3c_benz2"}, {}, SMILES, CATIONS | {"P3c_benz2": "C1=CC=CC=C1"})
    got = S.status("c1ccccc1", WITH_CATIONS, "A_benz", release)
    assert (got["role"], got["cation_trained"]) == ("a", ["P3c_benz", "P3c_benz2"])
    assert got["text"].count("radical cation (P3c_benz, P3c_benz2)") == 1


def test_an_unseen_molecule_with_a_trained_cation_is_unseen_as_a_neutral_one():
    seen = S.build({"P3c_pyr"}, {}, SMILES, {"P3c_pyr": "c1ccc2cc3ccccc3cc2c1"})
    got = S.status("c1ccc2cc3ccccc3cc2c1", seen, None)
    assert (got["role"], got["ids"], got["cation_trained"]) == ("unseen", [], ["P3c_pyr"])
    assert got["text"] == S.TEXT["unseen_neutral"] + "; " + S.TEXT["cation_trained"].format(ids="P3c_pyr")
    assert not got["text"].startswith(S.TEXT["unseen"])
