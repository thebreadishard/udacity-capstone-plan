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


def test_deal_largest_first_balances_hours_and_each_list_is_cheapest_first():
    items = [cand("a", 1), cand("b", 2), cand("c", 3), cand("d", 10), cand("e", 11)]
    lists = W.deal(items, ["h1", "h2"])
    # largest first: e→h1 (11), d→h2 (10), c→h2 (13), b→h1 (13), a→h1 (14)
    assert [c.mol_id for c in lists["h1"]] == ["a", "b", "e"]
    assert [c.mol_id for c in lists["h2"]] == ["c", "d"]
    loads = sorted(sum(c.hours for c in v) for v in lists.values())
    assert loads == [13, 14]
    for v in lists.values():
        assert [c.hours for c in v] == sorted(c.hours for c in v)


def test_deal_does_not_depend_on_the_input_order():
    items = [cand("a", 1), cand("b", 2), cand("c", 3), cand("d", 10), cand("e", 11)]
    assert W.deal(items, ["h1", "h2"]) == W.deal(list(reversed(items)), ["h1", "h2"])


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


def test_candidates_refuse_plan_ids_missing_from_the_corpus_rows_by_name():
    with pytest.raises(SystemExit, match="X9"):
        W.candidates({"chosen": {"single": ["X2", "X9"]}}, {"X2": "c1ccccc1"})


@pytest.mark.parametrize(("status", "geometry", "ready"), [
    ("done", True, True), ("pending", True, False), ("done", False, False), ("failed", True, False)])
def test_is_ready_needs_a_done_row_and_its_geometry(tmp_path, status, geometry, ready):
    if geometry:
        (tmp_path / "geometry.json").write_text("{}")
    assert W.is_ready(status, tmp_path) is ready


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


def test_earlier_wave_ids_are_the_first_fields_of_every_hosts_wave(tmp_path):
    for host, names in (("h1", ["M1", "M2"]), ("h2", ["M3"])):
        (tmp_path / host).mkdir()
        (tmp_path / host / "wave.txt").write_text("".join(W.wave_line(cand(n, 1.0)) + "\n" for n in names), encoding="utf-8")
    (tmp_path / "plan.md").write_text("not a wave", encoding="utf-8")
    assert W.earlier_wave_ids([tmp_path]) == {"M1", "M2", "M3"}
    assert W.earlier_wave_ids([]) == set()


def test_earlier_wave_ids_refuse_a_folder_without_a_wave_list(tmp_path):
    (tmp_path / "h1").mkdir()
    with pytest.raises(SystemExit, match=r"no <host>/wave\.txt"):
        W.earlier_wave_ids([tmp_path])


def test_an_empty_wave_list_of_a_host_counts_as_a_list(tmp_path):
    (tmp_path / "h1").mkdir()
    (tmp_path / "h1" / "wave.txt").write_text("", encoding="utf-8")
    assert W.earlier_wave_ids([tmp_path]) == set()


def test_report_names_what_an_earlier_wave_holds():
    text = W.report({"h1": [cand("M9", 2.0)]}, ["C1"], [], ["M1", "M2"])
    assert "dealt in an earlier wave and not carried yet: 2 (M1, M2)" in text
    assert "dealt in an earlier wave and not carried yet: 0 (none)" in W.report({"h1": []}, [], [])
