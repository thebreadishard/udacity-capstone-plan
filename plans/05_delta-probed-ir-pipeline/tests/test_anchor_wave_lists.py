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


def test_registry_statuses_keep_every_status_of_a_molecule_in_order(tmp_path):
    registry = tmp_path / "ANCHORS_STATUS.json"
    registry.write_text(json.dumps({"anchors": [
        {"mol_id": "A", "status": "superseded"}, {"mol_id": "A", "status": "carried"}, {"mol_id": "C", "status": "imaginary"}]}))
    assert W.registry_statuses(registry) == {"A": ["superseded", "carried"], "C": ["imaginary"]}


def test_write_lists_copies_geometries_and_writes_the_wave(tmp_path):
    corpus = tmp_path / "molecules"
    (corpus / "M1").mkdir(parents=True)
    (corpus / "M1" / "geometry.json").write_text('{"symbols": ["H", "H"]}')
    out = tmp_path / "out"
    W.write_lists(out, {"h1": [cand("M1", 2.0)], "h2": []}, corpus, "wave2.txt")
    assert (out / "h1" / "geoms" / "M1" / "geometry.json").read_text() == '{"symbols": ["H", "H"]}'
    assert (out / "h1" / "wave2.txt").read_text() == W.wave_line(cand("M1", 2.0)) + "\n"
    assert (out / "h2" / "wave2.txt").read_text() == ""
    assert not (out / "h1" / "wave.txt").exists()


def test_main_refuses_an_existing_out_folder(tmp_path):
    with pytest.raises(SystemExit, match="exists"):
        W.main(["--hosts", "h1", "--out", str(tmp_path)])


def test_main_refuses_a_host_named_twice(tmp_path):
    with pytest.raises(SystemExit, match="named twice"):
        W.main(["--hosts", "h1,h1", "--out", str(tmp_path / "new")])


def wave_folder(root, lists, name="wave.txt"):
    for host, names in lists.items():
        (root / host).mkdir(parents=True)
        (root / host / name).write_text("".join(W.wave_line(cand(n, 1.0)) + "\n" for n in names), encoding="utf-8")
    return root


def test_earlier_lists_and_their_ids(tmp_path):
    folder = wave_folder(tmp_path / "w1", {"h1": ["M1", "M2"], "h2": ["M3"]})
    (folder / "plan.md").write_text("not a wave", encoding="utf-8")
    (folder / "h1" / "waveform.csv").write_text("X|y\n", encoding="utf-8")
    lists = W.earlier_lists([folder])
    assert [p.relative_to(folder).as_posix() for p in lists] == ["h1/wave.txt", "h2/wave.txt"]
    assert W.wave_ids(lists) == {"M1", "M2", "M3"}
    assert W.earlier_lists([]) == [] and W.wave_ids([]) == set()


def test_an_empty_list_of_a_host_counts_as_a_list(tmp_path):
    assert W.wave_ids(W.earlier_lists([wave_folder(tmp_path / "w1", {"h1": []})])) == set()


def test_earlier_lists_refuse_a_folder_without_a_wave_list(tmp_path):
    (tmp_path / "h1").mkdir()
    with pytest.raises(SystemExit, match=r"no <host>/wave\*\.txt"):
        W.earlier_lists([tmp_path])


def test_earlier_lists_refuse_a_staging_folder(tmp_path):
    with pytest.raises(SystemExit, match="did not finish"):
        W.earlier_lists([wave_folder(tmp_path / "w1.partial", {"h1": ["M1"]})])


def test_partition_leaves_out_carried_and_earlier_and_splits_the_rest():
    items = [cand(n, h) for n, h in (("C1", 1.0), ("E1", 2.0), ("EC", 3.0), ("R1", 4.0), ("D1", 5.0))]
    part = W.partition(items, {"C1", "EC"}, {"E1", "EC"}, lambda c: c.mol_id != "D1")
    assert part.carried == ["C1", "EC"]            # a carried molecule of an earlier wave counts as carried only
    assert part.in_earlier == ["E1"]
    assert [c.mol_id for c in part.ready] == ["R1"]
    assert [c.mol_id for c in part.needs_dft] == ["D1"]


def test_partition_refuses_an_earlier_id_the_plan_does_not_hold():
    with pytest.raises(SystemExit, match=r"1 ids of an earlier wave are not in this plan.*X9"):
        W.partition([cand("M1", 1.0)], set(), {"M1", "X9"}, lambda c: True)


def test_report_gives_the_registry_status_of_an_earlier_molecule():
    part = W.Partition(carried=["C1"], in_earlier=["M1", "M2"], ready=[cand("M9", 2.0)], needs_dft=[])
    text = W.report({"h1": [cand("M9", 2.0)]}, part, {"M2": ["imaginary"], "C1": ["carried"]})
    assert "dealt in an earlier wave and not carried: 2 (M1, M2 [imaginary])" in text
    assert "carried anchor already: 1 (C1)" in text


@pytest.fixture
def small_plan(tmp_path, monkeypatch):
    """A plan of four molecules: one carried, one in wave 1, one ready, one without its DFT row."""
    smiles = {"C1": "c1ccccc1", "E1": "c1ccncc1", "R1": "c1ccc2ccccc2c1", "D1": "c1ccoc1"}
    plan = tmp_path / "plan.json"
    plan.write_text(json.dumps({"chosen": {"single": ["C1", "E1", "D1"], "fused": ["R1"]}}), encoding="utf-8")
    corpus = tmp_path / "corpus"
    for mol_id in ("C1", "E1", "R1"):
        (corpus / "molecules" / mol_id).mkdir(parents=True)
        (corpus / "molecules" / mol_id / "geometry.json").write_text("{}", encoding="utf-8")
    rows = {i: {"smiles": s, "status": "pending" if i == "D1" else "done"} for i, s in smiles.items()}
    monkeypatch.setattr(W.A, "corpus_cells", lambda: rows)
    monkeypatch.setattr(W.A, "CORPUS", corpus)
    monkeypatch.setattr(W, "registry_statuses", lambda: {"C1": ["carried"]})
    return plan, wave_folder(tmp_path / "wave1", {"h1": ["C1", "E1"]})


def test_main_deals_only_what_no_earlier_wave_holds(small_plan, tmp_path, capsys):
    plan, wave1 = small_plan
    out = tmp_path / "wave2"
    assert W.main(["--hosts", "h1,h2", "--out", str(out), "--plan", str(plan), "--earlier", str(wave1), "--list-name", "wave2.txt"]) == 0
    dealt = [line.split("|")[0] for host in ("h1", "h2") for line in (out / host / "wave2.txt").read_text().splitlines()]
    assert dealt == ["R1"]
    assert (out / "needs_dft.txt").read_text() == "D1\n"
    assert "not carried: 1 (E1)" in capsys.readouterr().out


def test_main_without_earlier_deals_the_earlier_waves_molecule_again(small_plan, tmp_path):
    plan, _ = small_plan
    out = tmp_path / "wave2"
    W.main(["--hosts", "h1", "--out", str(out), "--plan", str(plan)])
    assert sorted(line.split("|")[0] for line in (out / "h1" / "wave.txt").read_text().splitlines()) == ["E1", "R1"]


def test_main_refuses_the_list_name_of_an_earlier_wave_before_reading_data(small_plan, tmp_path, monkeypatch):
    plan, wave1 = small_plan
    monkeypatch.setattr(W.A, "corpus_cells", lambda: pytest.fail("data was read before the request was checked"))
    with pytest.raises(SystemExit, match="would replace a list a wave is reading"):
        W.main(["--hosts", "h1", "--out", str(tmp_path / "wave2"), "--plan", str(plan), "--earlier", str(wave1)])
    with pytest.raises(SystemExit, match=r"a name like wave\.txt"):
        W.main(["--hosts", "h1", "--out", str(tmp_path / "wave2"), "--plan", str(plan), "--list-name", "list.txt"])
    with pytest.raises(SystemExit, match=r"no <host>/wave\*\.txt"):
        W.main(["--hosts", "h1", "--out", str(tmp_path / "wave2"), "--plan", str(plan), "--earlier", str(tmp_path / "nowhere")])


def test_main_refuses_a_staging_folder_left_by_a_failed_run(small_plan, tmp_path):
    plan, _ = small_plan
    (tmp_path / "wave2.partial").mkdir()
    with pytest.raises(SystemExit, match="failed earlier run"):
        W.main(["--hosts", "h1", "--out", str(tmp_path / "wave2"), "--plan", str(plan)])
