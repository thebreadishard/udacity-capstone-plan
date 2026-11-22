"""`probes/opt_batch_merge.py` on a small stand-in corpus and fetched batch: what it merges, what it leaves out, what it refuses, the
manifest it writes, a second run, and the guards against merging beside another writer of the manifest or a reader of the corpus."""
import csv
import json
import sys
from pathlib import Path

import numpy as np
import pytest

pytest.importorskip("rdkit")
from rdkit import Chem
from rdkit.Chem import AllChem

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes"))
import opt_batch_merge as M

FIELDS = ["id", "layer", "priority", "name", "smiles", "qm9_label", "n_heavy", "n_atoms", "status", "machine", "deck", "note"]
DECK = {"low_functional": "B3LYP", "basis": "6-31G*", "threads": 8, "memory_gb": 12}
JOB_DECK = dict(DECK, threads=4, memory_gb=6)
MOLS = {"B_p1": ("pyridine", "c1ccncc1"), "B_b1": ("benzene", "c1ccccc1")}
PYRIDINE_OPEN_ISOMER = "C#CC=CC=N"                                               # C5H5N as well, bonded otherwise


def geometry(smiles: str, seed: int = 7) -> dict:
    """A force-field geometry of the SMILES in the corpus's geometry.json form."""
    mol = Chem.AddHs(Chem.MolFromSmiles(smiles))
    AllChem.EmbedMolecule(mol, randomSeed=seed)
    AllChem.MMFFOptimizeMolecule(mol)
    return {"symbols": [a.GetSymbol() for a in mol.GetAtoms()], "coords_bohr": (mol.GetConformer().GetPositions() / M.BOHR).tolist()}


def molecule(folder: Path, mol_id: str, **vary) -> None:
    """A fetched molecule folder; vary: imaginary, labelled, job (bool), deck (dict), smiles (str), geometry (dict) instead of the
    molecule's own."""
    name, own_smiles = MOLS[mol_id]
    geom = vary.get("geometry") or geometry(own_smiles)
    folder.mkdir(parents=True)
    if vary.get("job", True):
        job = {"id": mol_id, "deck": vary.get("deck", JOB_DECK), "source": {"smiles": vary.get("smiles", own_smiles), "name": name}}
        if job["deck"] is None:                                                 # a job file cut short of its source and deck
            job = {"id": mol_id}
        (folder / "job.json").write_text(json.dumps(job))
    (folder / "geometry.json").write_text(json.dumps(geom))
    (folder / "result.json").write_text(json.dumps({"status": "done", "labels": "analytic_only"}))
    if vary.get("labelled", True):
        freq = np.concatenate([np.zeros(6), np.linspace(400.0, 3200.0, 3 * len(geom["symbols"]) - 6)])
        if vary.get("imaginary", False):
            freq[6] = -55.0
        for tag in ("b3lyp", "wb97x"):
            np.savez(folder / f"hessian_{tag}_analytic.npz", freq_cm=freq)
        np.savez(folder / "dipole_b3lyp_cphf.npz", passed=True)


@pytest.fixture
def world(tmp_path, monkeypatch):
    monkeypatch.setattr(M, "command_lines", list)                               # no other process, unless a test names one
    corpus = tmp_path / "corpus"
    (corpus / "molecules").mkdir(parents=True)
    (corpus / "decks").mkdir()
    (corpus / "decks" / "deck_v1.json").write_text(json.dumps(DECK))
    with (corpus / "manifest.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerow(dict.fromkeys(FIELDS, "") | {"id": "A_old", "layer": "A", "smiles": "C", "status": "done", "deck": "abc", "note": "kept"})
        for mol_id, (name, smiles) in MOLS.items():
            w.writerow(dict.fromkeys(FIELDS, "") | {"id": mol_id, "layer": "B", "name": name, "smiles": smiles,
                                                   "n_atoms": len(geometry(smiles)["symbols"]), "status": "pending",
                                                   "note": "rehash-2026-09-28"})
    batch = tmp_path / "fetch" / "anc1" / "dft1"
    (batch / "molecules").mkdir(parents=True)
    (batch / "ids.txt").write_text("# header\nB_p1\nB_b1\n")
    return {"corpus": corpus, "batch": batch, "argv": ["--source", f"anc1={batch}", "--corpus", str(corpus)]}


def both(world) -> None:
    for mol_id in MOLS:
        molecule(world["batch"] / "molecules" / mol_id, mol_id)


def manifest(world) -> dict[str, dict]:
    with (world["corpus"] / "manifest.csv").open(newline="", encoding="utf-8") as f:
        return {r["id"]: r for r in csv.DictReader(f)}


def set_row(world, mol_id: str, **values) -> None:
    rows = manifest(world)
    rows[mol_id].update(values)
    with (world["corpus"] / "manifest.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows.values())


def test_a_ready_molecule_is_merged_and_one_with_an_imaginary_mode_is_named_and_left_out(world, capsys):
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


def test_a_label_file_that_cannot_be_read_leaves_the_molecule_out_by_name(world, capsys):
    both(world)
    (world["batch"] / "molecules" / "B_p1" / "hessian_b3lyp_analytic.npz").write_bytes(b"PK\x03\x04 cut short")
    assert M.main([*world["argv"], "--write"]) == 0
    assert "left out  B_p1: unreadable (" in capsys.readouterr().out
    assert manifest(world)["B_p1"]["status"] == "pending" and manifest(world)["B_b1"]["status"] == "done"


@pytest.mark.parametrize(("kwargs", "says"), [
    ({"smiles": "c1ccccc1"}, "the manifest row is 'c1ccncc1'"),
    ({"deck": dict(DECK, basis="cc-pVDZ")}, "differs from deck_v1.json in basis"),
    ({"geometry": geometry("c1ccccc1")}, "is not the molecule c1ccncc1"),
    ({"geometry": geometry(PYRIDINE_OPEN_ISOMER)}, "is not the molecule c1ccncc1"),
    ({"job": False}, "B_p1: no job.json in"),
    ({"geometry": {"symbols": ["Xx", "C"], "coords_bohr": [[0, 0, 0], [0, 0, 2.5]]}}, "B_p1: its geometry or SMILES cannot be read"),
    ({"deck": None}, "B_p1: its job.json cannot be read"),
])
def test_a_molecule_that_is_not_the_row_s_at_the_corpus_deck_is_refused(world, kwargs, says):
    molecule(world["batch"] / "molecules" / "B_p1", "B_p1", **kwargs)
    molecule(world["batch"] / "molecules" / "B_b1", "B_b1")
    with pytest.raises(SystemExit, match="refused, nothing written") as e:
        M.main([*world["argv"], "--write"])
    assert says in str(e.value) and not (world["corpus"] / "molecules" / "B_b1").exists()


def test_an_id_without_a_row_or_listed_in_two_sources_is_refused(world, tmp_path):
    both(world)
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
    both(world)
    molecule(world["corpus"] / "molecules" / "B_p1", "B_p1", geometry=geometry("c1ccncc1", seed=11))
    with pytest.raises(SystemExit, match="exists and is not this batch's ready folder"):
        M.main(world["argv"])


def test_a_row_already_done_at_the_deck_without_its_folder_gets_the_folder_and_the_note(world, capsys):
    both(world)
    deck_hash = M.LM.deck_hash(JOB_DECK, world["corpus"] / "decks" / "deck_v1.json")
    set_row(world, "B_p1", status="done", deck=deck_hash, machine="elsewhere")
    assert M.main([*world["argv"], "--write"]) == 0
    assert "2 folders to copy, 2 rows to bring up to date" in capsys.readouterr().out
    row = manifest(world)["B_p1"]
    assert row["machine"] == "anc1" and M.NOTE_MARK in row["note"] and (world["corpus"] / "molecules" / "B_p1").is_dir()


def test_a_row_done_at_another_deck_is_refused(world):
    both(world)
    set_row(world, "B_p1", status="done", deck="0123456789ab")
    with pytest.raises(SystemExit, match="its manifest row is 'done' with deck '0123456789ab'"):
        M.main(world["argv"])


def test_writing_is_refused_while_a_reader_of_the_corpus_runs_unless_a_reason_is_given(world, monkeypatch, capsys):
    both(world)
    monkeypatch.setattr(M, "command_lines", lambda: ["bash", "python m05/rungC_eval_saved.py --run v14"])
    with pytest.raises(SystemExit, match="a chain, training or evaluation runs here"):
        M.main([*world["argv"], "--write"])
    assert not (world["corpus"] / "molecules" / "B_p1").exists() and manifest(world)["B_p1"]["status"] == "pending"
    assert M.main([*world["argv"], "--write", "--beside-training", "the chain's last step has loaded its pool"]) == 0
    assert "merged beside a running reader of the corpus: the chain's last step has loaded its pool" in capsys.readouterr().out
    assert manifest(world)["B_b1"]["status"] == "done"


@pytest.mark.parametrize("writer", ["python run_corpus.py --layer B", "python corpus/merge_shards.py shard1"])
def test_writing_is_refused_beside_another_writer_of_the_manifest_whatever_the_reason(world, monkeypatch, writer):
    both(world)
    monkeypatch.setattr(M, "command_lines", lambda: [writer])
    with pytest.raises(SystemExit, match="another writer of the manifest runs here"):
        M.main([*world["argv"], "--write", "--beside-training", "a reason does not help here"])
    assert manifest(world)["B_p1"]["status"] == "pending" and not (world["corpus"] / "molecules" / "B_p1").exists()
    assert M.main(world["argv"]) == 0                                           # the plan alone is still given


def test_writing_is_refused_while_the_corpus_lock_exists_and_another_s_lock_is_left_alone(world):
    both(world)
    (world["corpus"] / "corpus.lock").write_text("laptop 2026-11-22 09:00 pid 1234")
    with pytest.raises(SystemExit, match=r"corpus\.lock"):
        M.main([*world["argv"], "--write", "--beside-training", "x"])
    assert not (world["corpus"] / "molecules" / "B_p1").exists()
    assert (world["corpus"] / "corpus.lock").read_text() == "laptop 2026-11-22 09:00 pid 1234"


def test_the_merge_holds_the_corpus_lock_in_the_runner_s_format_while_it_writes_and_frees_it(world, monkeypatch):
    both(world)
    seen = []
    copy = M.copy_folders
    monkeypatch.setattr(M, "copy_folders", lambda *a: (seen.append((world["corpus"] / "corpus.lock").read_text()), copy(*a)))
    assert M.main([*world["argv"], "--write"]) == 0
    host, day, clock, word, pid = seen[0].split()                               # run_corpus.py reads parts[0] and parts[-1]
    assert (host, word, pid) == (M.socket.gethostname(), "pid", str(M.os.getpid())) and len(day) == 10 and len(clock) == 5
    assert not (world["corpus"] / "corpus.lock").exists()
    monkeypatch.setattr(M, "command_lines", lambda: ["python run_corpus.py"])    # a refusal frees the lock too
    with pytest.raises(SystemExit, match="another writer"):
        M.main([*world["argv"], "--write"])
    assert not (world["corpus"] / "corpus.lock").exists()


def test_a_process_list_that_cannot_be_read_refuses_the_write_by_name(world, monkeypatch):
    both(world)

    def fail() -> list[str]:
        raise RuntimeError("-d Ubuntu -e ps -eww -o args gave no answer (TimeoutExpired)")
    monkeypatch.setattr(M, "command_lines", fail)
    with pytest.raises(SystemExit, match="the guards cannot see this machine's jobs"):
        M.main([*world["argv"], "--write"])
    assert manifest(world)["B_p1"]["status"] == "pending" and not (world["corpus"] / "corpus.lock").exists()


def test_the_previous_manifest_s_copy_is_never_written_over(world, monkeypatch):
    both(world)
    monkeypatch.setattr(M.time, "strftime", lambda fmt: "2026-11-22_101500")
    item = M.Item("B_p1", "anc1", world["batch"] / "molecules" / "B_p1", "0123456789ab")
    backup = M.update_manifest((item,), world["corpus"] / "manifest.csv")
    kept = backup.read_text()
    assert "pending" in kept
    with pytest.raises(FileExistsError, match="pre_opt_batch_merge_2026-11-22_101500"):
        M.update_manifest((item,), world["corpus"] / "manifest.csv")
    assert backup.read_text() == kept


def test_bad_sources_and_a_reason_without_write_are_refused(world, tmp_path):
    with pytest.raises(SystemExit, match="each host once"):
        M.main(["--source", "anc1", "--corpus", str(world["corpus"])])
    with pytest.raises(SystemExit, match=r"no ids\.txt and molecules/"):
        M.main(["--source", f"anc1={tmp_path}", "--corpus", str(world["corpus"])])
    with pytest.raises(SystemExit, match="belongs to --write"):
        M.main([*world["argv"], "--beside-training", "x"])


def test_command_lines_reads_the_process_table_and_only_python_lines_count_as_runs(monkeypatch):
    monkeypatch.setattr(M, "wsl_command_lines", lambda: ["/usr/bin/python3 probes/chain_runner.py b.json"])
    lines = M.command_lines()
    assert len(lines) > 1 and lines[-1] == "/usr/bin/python3 probes/chain_runner.py b.json"
    seen = ["x", "python probes/chain_runner.py a.json", "tail -f chain_runner.py.log", "code.exe probes/chain_runner.py"]
    assert M.at_work(("chain_runner.py",), seen) == ["python probes/chain_runner.py a.json"]


def test_wsl_is_asked_only_for_its_running_distributions(monkeypatch):
    calls = []

    def answer(args: list[str]) -> str:
        calls.append(args[1:])
        return "Ubuntu\n\nDebian\n" if "--running" in args else f"python job_in_{args[2]}.py\n"
    monkeypatch.setattr(M.shutil, "which", lambda name: "wsl.exe")
    monkeypatch.setattr(M, "wsl_text", answer)
    assert M.wsl_command_lines() == ["python job_in_Ubuntu.py", "python job_in_Debian.py"]
    assert calls[0] == ["-l", "--running", "-q"] and calls[1][:3] == ["-d", "Ubuntu", "-e"]

    def none_running(args: list[str]) -> str:
        raise RuntimeError("-l --running -q failed (There are no running distributions.)")
    monkeypatch.setattr(M, "wsl_text", none_running)
    assert M.wsl_command_lines() == []
    monkeypatch.setattr(M.shutil, "which", lambda name: None)
    assert M.wsl_command_lines() == []


def test_wsl_text_drops_utf16_nul_bytes_and_names_a_failed_call(monkeypatch):
    class Done:
        returncode, stdout, stderr = 0, "Ubuntu\r\n".encode("utf-16-le"), b""
    monkeypatch.setattr(M.subprocess, "run", lambda *a, **k: Done)
    assert M.wsl_text(["wsl.exe", "-l", "--running", "-q"]).split() == ["Ubuntu"]
    Done.returncode, Done.stderr = 1, "no such distribution".encode("utf-16-le")
    with pytest.raises(RuntimeError, match=r"-d Nope failed \(no such distribution\)"):
        M.wsl_text(["wsl.exe", "-d", "Nope"])


def test_psi4_s_capital_element_symbols_are_the_smiles_s_atoms(tmp_path):
    """Found on the first real batch (22 Nov 2026): 2-chloropyrimidine's geometry.json lists 'CL'."""
    folder = tmp_path / "B_c1"
    folder.mkdir()
    geom = geometry("Clc1ncccn1")
    geom["symbols"] = [s.upper() for s in geom["symbols"]]
    (folder / "job.json").write_text(json.dumps({"id": "B_c1", "deck": dict(DECK, threads=4), "source": {"smiles": "Clc1ncccn1"}}))
    (folder / "geometry.json").write_text(json.dumps(geom))
    deck_file = tmp_path / "deck_v1.json"
    deck_file.write_text(json.dumps(DECK))
    assert len(M.check_molecule("B_c1", folder, {"smiles": "Clc1ncccn1"}, deck_file)) == 12
