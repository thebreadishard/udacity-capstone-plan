"""`probes/opt_batch_merge.py` on a small stand-in corpus and fetched batch: what it merges, what it leaves out, what it refuses, the
manifest it writes, a second run, and the guard against merging under a running training."""
import csv
import json
import sys
from pathlib import Path

import numpy as np
import pytest

pytest.importorskip("rdkit")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes"))
import opt_batch_merge as M

FIELDS = ["id", "layer", "priority", "name", "smiles", "qm9_label", "n_heavy", "n_atoms", "status", "machine", "deck", "note"]
DECK = {"low_functional": "B3LYP", "basis": "6-31G*", "threads": 8, "memory_gb": 12}
PYRIDINE = ["C"] * 5 + ["N"] + ["H"] * 5
MOLS = {"B_p1": ("pyridine", "c1ccncc1", PYRIDINE), "B_b1": ("benzene", "c1ccccc1", ["C"] * 6 + ["H"] * 6)}


def molecule(folder: Path, mol_id: str, **vary) -> None:
    """A fetched molecule folder; vary: imaginary, labelled (bool), deck (dict), smiles (str), symbols (list) instead of the molecule's own."""
    name, own_smiles, own_symbols = MOLS[mol_id]
    symbols = vary.get("symbols", own_symbols)
    imaginary, labelled = vary.get("imaginary", False), vary.get("labelled", True)
    folder.mkdir(parents=True)
    job_deck = vary.get("deck", dict(DECK, threads=4, memory_gb=6))
    (folder / "job.json").write_text(json.dumps({"id": mol_id, "deck": job_deck,
                                                 "source": {"smiles": vary.get("smiles", own_smiles), "name": name}}))
    (folder / "geometry.json").write_text(json.dumps({"symbols": symbols, "coords_bohr": [[0, 0, float(k)] for k in range(len(symbols))]}))
    (folder / "result.json").write_text(json.dumps({"status": "done", "labels": "analytic_only"}))
    if labelled:
        freq = np.concatenate([np.zeros(6), np.linspace(400.0, 3200.0, 3 * len(symbols) - 6)])
        if imaginary:
            freq[6] = -55.0
        for tag in ("b3lyp", "wb97x"):
            np.savez(folder / f"hessian_{tag}_analytic.npz", freq_cm=freq)
        np.savez(folder / "dipole_b3lyp_cphf.npz", passed=True)


@pytest.fixture
def world(tmp_path):
    corpus = tmp_path / "corpus"
    (corpus / "molecules").mkdir(parents=True)
    (corpus / "decks").mkdir()
    (corpus / "decks" / "deck_v1.json").write_text(json.dumps(DECK))
    with (corpus / "manifest.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerow(dict.fromkeys(FIELDS, "") | {"id": "A_old", "layer": "A", "smiles": "C", "status": "done", "deck": "abc", "note": "kept"})
        for mol_id, (name, smiles, symbols) in MOLS.items():
            w.writerow(dict.fromkeys(FIELDS, "") | {"id": mol_id, "layer": "B", "name": name, "smiles": smiles, "n_atoms": len(symbols),
                                                   "status": "pending", "note": "rehash-2026-09-28"})
    batch = tmp_path / "fetch" / "anc1" / "dft1"
    (batch / "molecules").mkdir(parents=True)
    (batch / "ids.txt").write_text("# header\nB_p1\nB_b1\n")
    return {"corpus": corpus, "batch": batch, "argv": ["--source", f"anc1={batch}", "--corpus", str(corpus)]}


def manifest(world) -> dict[str, dict]:
    with (world["corpus"] / "manifest.csv").open(newline="", encoding="utf-8") as f:
        return {r["id"]: r for r in csv.DictReader(f)}


def test_a_ready_molecule_is_merged_and_one_with_an_imaginary_mode_is_named_and_left_out(world, monkeypatch, capsys):
    monkeypatch.setattr(M, "training_at_work", list)
    molecule(world["batch"] / "molecules" / "B_p1", "B_p1")
    molecule(world["batch"] / "molecules" / "B_b1", "B_b1", imaginary=True)
    before = (world["corpus"] / "manifest.csv").read_text()
    assert M.main(world["argv"]) == 0                                           # the plan alone writes nothing
    assert (world["corpus"] / "manifest.csv").read_text() == before and not (world["corpus"] / "molecules" / "B_p1").exists()
    assert M.main([*world["argv"], "--write"]) == 0
    out = capsys.readouterr().out
    assert "left out  B_b1: IMAGINARY" in out and "1 folders to copy, 1 rows to bring up to date, 1 molecules left out" in out
    rows = manifest(world)
    assert (rows["B_p1"]["status"], rows["B_p1"]["machine"], len(rows["B_p1"]["deck"])) == ("done", "anc1", 12)
    assert rows["B_p1"]["note"].startswith("rehash-2026-09-28; anchor-plan DFT batch of 21 Nov 2026 on anc1")
    assert rows["B_b1"]["status"] == "pending" and rows["A_old"] == {**dict.fromkeys(FIELDS, ""), "id": "A_old", "layer": "A", "smiles": "C",
                                                                    "status": "done", "deck": "abc", "note": "kept"}
    assert (world["corpus"] / "molecules" / "B_p1" / "hessian_wb97x_analytic.npz").exists()
    assert not (world["corpus"] / "molecules" / "B_b1").exists() and not (world["corpus"] / M.STAGING).exists()
    assert len(list(world["corpus"].glob("manifest.csv.pre_opt_batch_merge_*"))) == 1
    assert M.main([*world["argv"], "--write"]) == 0                             # a second run finds it in place
    assert "0 folders to copy, 0 rows to bring up to date, 1 molecules left out" in capsys.readouterr().out
    assert len(list(world["corpus"].glob("manifest.csv.pre_opt_batch_merge_*"))) == 1


def test_a_molecule_optimised_but_not_labelled_yet_is_left_out(world, capsys):
    molecule(world["batch"] / "molecules" / "B_p1", "B_p1", labelled=False)
    molecule(world["batch"] / "molecules" / "B_b1", "B_b1")
    assert M.main(world["argv"]) == 0
    assert "left out  B_p1: no hessian_b3lyp_analytic.npz" in capsys.readouterr().out


@pytest.mark.parametrize(("kwargs", "says"), [
    ({"smiles": "c1ccccc1"}, "the manifest row is 'c1ccncc1'"),
    ({"deck": dict(DECK, basis="cc-pVDZ")}, "differs from deck_v1.json in basis"),
    ({"symbols": ["C"] * 6 + ["H"] * 5}, "are not those of c1ccncc1"),
])
def test_a_molecule_that_is_not_the_row_s_at_the_corpus_deck_is_refused(world, kwargs, says):
    molecule(world["batch"] / "molecules" / "B_p1", "B_p1", **kwargs)
    molecule(world["batch"] / "molecules" / "B_b1", "B_b1")
    with pytest.raises(SystemExit, match="refused, nothing written") as e:
        M.main([*world["argv"], "--write"])
    assert says in str(e.value) and not (world["corpus"] / "molecules" / "B_b1").exists()


def test_an_id_without_a_row_or_listed_in_two_sources_is_refused(world, tmp_path):
    for mol_id in MOLS:
        molecule(world["batch"] / "molecules" / mol_id, mol_id)
    other = tmp_path / "fetch" / "anc2" / "dft1"
    (other / "molecules").mkdir(parents=True)
    (other / "ids.txt").write_text("B_p1\n")
    with pytest.raises(SystemExit, match="more than one source"):
        M.main([*world["argv"], "--source", f"anc2={other}"])
    (other / "ids.txt").write_text("B_zz\n")
    molecule(other / "molecules" / "B_zz", "B_p1")
    with pytest.raises(SystemExit, match="B_zz: no manifest row"):
        M.main([*world["argv"], "--source", f"anc2={other}"])


def test_another_folder_already_in_the_corpus_under_the_id_is_refused(world):
    molecule(world["batch"] / "molecules" / "B_p1", "B_p1")
    molecule(world["batch"] / "molecules" / "B_b1", "B_b1")
    molecule(world["corpus"] / "molecules" / "B_p1", "B_p1", symbols=list(reversed(PYRIDINE)))
    with pytest.raises(SystemExit, match="exists and is not this batch's ready folder"):
        M.main(world["argv"])


def test_writing_is_refused_while_a_training_runs_unless_a_reason_is_given(world, monkeypatch, capsys):
    for mol_id in MOLS:
        molecule(world["batch"] / "molecules" / mol_id, mol_id)
    monkeypatch.setattr(M, "training_at_work", lambda: ["python chain_runner.py probes/runs/v14_stage1.json"])
    with pytest.raises(SystemExit, match="a chain or training runs here"):
        M.main([*world["argv"], "--write"])
    assert not (world["corpus"] / "molecules" / "B_p1").exists() and manifest(world)["B_p1"]["status"] == "pending"
    assert M.main([*world["argv"], "--write", "--beside-training", "the chain's last step has loaded its pool"]) == 0
    assert "merged beside a running training: the chain's last step has loaded its pool" in capsys.readouterr().out
    assert manifest(world)["B_b1"]["status"] == "done"


def test_bad_sources_and_a_reason_without_write_are_refused(world, tmp_path):
    with pytest.raises(SystemExit, match="each host once"):
        M.main(["--source", "anc1", "--corpus", str(world["corpus"])])
    with pytest.raises(SystemExit, match=r"no ids\.txt and molecules/"):
        M.main(["--source", f"anc1={tmp_path}", "--corpus", str(world["corpus"])])
    with pytest.raises(SystemExit, match="belongs to --write"):
        M.main([*world["argv"], "--beside-training", "x"])


def test_training_at_work_reads_the_process_table():
    assert isinstance(M.training_at_work(), list)


def test_psi4_s_capital_element_symbols_are_the_smiles_s_atoms(tmp_path):
    """Found on the first real batch (22 Nov 2026): 2-chloropyrimidine's geometry.json lists 'CL'."""
    folder = tmp_path / "B_c1"
    folder.mkdir()
    (folder / "job.json").write_text(json.dumps({"id": "B_c1", "deck": dict(DECK, threads=4), "source": {"smiles": "Clc1ncccn1"}}))
    (folder / "geometry.json").write_text(json.dumps({"symbols": ["CL", "C", "N", "C", "C", "C", "N", "H", "H", "H"]}))
    deck_file = tmp_path / "deck_v1.json"
    deck_file.write_text(json.dumps(DECK))
    assert len(M.check_molecule("B_c1", folder, {"smiles": "Clc1ncccn1"}, deck_file)) == 12
