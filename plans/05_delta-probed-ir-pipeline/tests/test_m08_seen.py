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
