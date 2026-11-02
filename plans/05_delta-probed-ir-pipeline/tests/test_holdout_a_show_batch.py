"""probes/holdout_a_show_batch.py: the hold-out (a) batch rows in show_batch_select's format, smallest carbon count first; an id the
manifest lacks or one the network's record does not hold out as (a) is refused. The network's record is a stand-in."""
import sys
from pathlib import Path

import pytest

pytest.importorskip("rdkit")
PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
import holdout_a_show_batch as H  # noqa: E402

MANIFEST = {"A_1": {"name": "naphthalene", "smiles": "c1ccc2ccccc2c1"}, "A_2": {"name": "benzene", "smiles": "c1ccccc1"}}


def _roles(monkeypatch, roles):
    monkeypatch.setattr(H.S, "status", lambda smiles, seen, mol_id: {"role": roles[mol_id]})


def test_rows_are_in_the_batch_format_smallest_first(monkeypatch):
    _roles(monkeypatch, {"A_1": "a", "A_2": "a"})
    assert H.batch_rows(["A_1", "A_2"], MANIFEST, seen=None) == [["benzene_A_2", "c1ccccc1", "A_2", "a", 6],
                                                                 ["naphthalene_A_1", "c1ccc2ccccc2c1", "A_1", "a", 10]]


def test_a_molecule_not_held_out_as_a_is_refused(monkeypatch):
    _roles(monkeypatch, {"A_1": "a", "A_2": "trained"})
    with pytest.raises(SystemExit, match=r"A_2 .*'trained'"):
        H.batch_rows(["A_1", "A_2"], MANIFEST, seen=None)


def test_an_id_the_manifest_lacks_is_refused(monkeypatch):
    _roles(monkeypatch, {})
    with pytest.raises(SystemExit, match="A_9 is not in"):
        H.batch_rows(["A_9"], MANIFEST, seen=None)


def test_read_ids_skips_comments_and_blank_lines(tmp_path):
    p = tmp_path / "ids.tsv"
    p.write_text("# header\nA_1\tapt\t26\n\nA_2\thessian\t12\n", encoding="utf-8")
    assert H.read_ids(p) == ["A_1", "A_2"]
