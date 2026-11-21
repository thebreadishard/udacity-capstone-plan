"""The split of the anchor plan over servers (`probes/anchor_wave_lists.py`): order, dealing, the wave line, the refusals."""
import json
import sys
from pathlib import Path

import pytest

pytest.importorskip("rdkit")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes"))
import anchor_wave_lists as W


def cand(mol_id, hours, n_atoms=12):
    return W.Candidate(mol_id, "single", n_atoms, 100, hours)


def test_deal_balances_hours_and_keeps_each_list_cheapest_first():
    ordered = [cand("a", 1), cand("b", 2), cand("c", 3), cand("d", 10), cand("e", 11)]
    lists = W.deal(ordered, ["h1", "h2"])
    assert [c.mol_id for c in lists["h1"]] == ["a", "c", "e"]
    assert [c.mol_id for c in lists["h2"]] == ["b", "d"]
    for items in lists.values():
        assert [c.hours for c in items] == sorted(c.hours for c in items)


def test_deal_tie_goes_to_the_host_listed_first():
    lists = W.deal([cand("a", 1)], ["h2", "h1"])
    assert [c.mol_id for c in lists["h2"]] == ["a"] and lists["h1"] == []


def test_deal_refuses_no_hosts():
    with pytest.raises(ValueError, match="no hosts"):
        W.deal([cand("a", 1)], [])


def test_candidates_are_ordered_by_rule_hours_then_atoms_then_id():
    plan = {"chosen": {"single": ["X1", "X2"], "fused": ["X3"]}}
    smiles = {"X1": "c1ccc2ccccc2c1", "X2": "c1ccccc1", "X3": "c1ccncc1"}   # naphthalene, benzene, pyridine
    got = [c.mol_id for c in W.candidates(plan, smiles)]
    assert got == ["X3", "X2", "X1"]   # pyridine: 11 atoms, 109 functions; benzene: 12 atoms, 114 functions
    assert {c.context for c in W.candidates(plan, smiles)} == {"single", "fused"}


def test_wave_line_is_what_anchor_wave_reads():
    line = W.wave_line(cand("B_0123456789", 5.0))
    name, geom, workers, threads, mem = line.split("|")
    assert name == "B_0123456789"
    assert geom == "/root/dpir/geoms/B_0123456789/geometry.json"
    assert (int(workers), int(threads), int(mem)) == (W.WORKERS, W.THREADS, W.MEM_MB)


def test_carried_ids_reads_only_carried_entries(tmp_path):
    registry = tmp_path / "ANCHORS_STATUS.json"
    registry.write_text(json.dumps({"anchors": [
        {"mol_id": "A", "status": "carried"}, {"mol_id": "B", "status": "superseded"}, {"mol_id": "C", "status": "invalid"}]}))
    assert W.carried_ids(registry) == {"A"}


def test_write_lists_copies_geometries_and_writes_the_wave(tmp_path):
    corpus = tmp_path / "molecules"
    (corpus / "M1").mkdir(parents=True)
    (corpus / "M1" / "geometry.json").write_text('{"symbols": ["H", "H"]}')
    out = tmp_path / "out"
    W.write_lists(out, {"h1": [cand("M1", 2.0)], "h2": []}, corpus)
    assert (out / "h1" / "geoms" / "M1" / "geometry.json").read_text() == '{"symbols": ["H", "H"]}'
    assert (out / "h1" / "wave.txt").read_text() == W.wave_line(cand("M1", 2.0)) + "\n"
    assert (out / "h2" / "wave.txt").read_text() == ""


def test_main_refuses_an_existing_out_folder(tmp_path):
    with pytest.raises(SystemExit, match="exists"):
        W.main(["--hosts", "h1", "--out", str(tmp_path)])


def test_main_refuses_a_host_named_twice(tmp_path):
    with pytest.raises(SystemExit, match="named twice"):
        W.main(["--hosts", "h1,h1", "--out", str(tmp_path / "new")])
