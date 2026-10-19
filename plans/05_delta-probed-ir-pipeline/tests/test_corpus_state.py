"""probes/corpus_state.py — a corpus molecule's charge and multiplicity come from the deck in its job.json, a missing file or key fails loudly —
and its use in the error map: a computed pool 3 cation, whose SMILES is its neutral parent's, gets a cation kind."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes"))
C = pytest.importorskip("corpus_state")


def job(tmp_path, mol_id, deck):
    d = tmp_path / "molecules" / mol_id
    d.mkdir(parents=True)
    (d / "job.json").write_text(json.dumps({"id": mol_id, "deck": deck}), encoding="utf-8")


def test_the_deck_gives_charge_and_multiplicity(tmp_path):
    job(tmp_path, "P3c_x", {"reference": "uks", "charge": 1, "multiplicity": 2})
    job(tmp_path, "A_x", {"reference": "rhf", "charge": 0, "multiplicity": 1})
    assert C.recorded_state("P3c_x", str(tmp_path)) == (1, 2)
    assert C.recorded_state("A_x", str(tmp_path)) == C.NEUTRAL_SINGLET


def test_a_missing_job_or_key_fails_loudly(tmp_path):
    job(tmp_path, "A_nokey", {"reference": "rhf"})
    with pytest.raises(SystemExit, match=r"no job\.json"):
        C.recorded_state("A_absent", str(tmp_path))
    with pytest.raises(SystemExit, match="names no charge"):
        C.recorded_state("A_nokey", str(tmp_path))


def test_the_real_corpus_knows_a_pool3_cation_by_its_deck():
    if not Path(C.CORPUS, "molecules", "P3c_541c53d1a5", "job.json").is_file():
        pytest.skip("the git-ignored corpus is not on this machine")
    assert C.recorded_state("P3c_541c53d1a5") == (1, 2) and C.recorded_state("A_541c53d1a5") == C.NEUTRAL_SINGLET


def test_the_error_map_kind_carries_the_recorded_charge():
    pytest.importorskip("rdkit")
    E = pytest.importorskip("rungC_error_map")
    phenanthrene = "c1ccc2c(c1)ccc1ccccc12"
    assert not E.kind_of(phenanthrene)["kind"].endswith("|cation")
    assert E.kind_of(phenanthrene, 1)["kind"].endswith("|cation") and E.kind_of(phenanthrene, 1)["charge"] == 1
    assert E.kind_of("c1cc[nH+]cc1")["kind"].endswith("|cation")       # without a record, the SMILES's own charge as before
