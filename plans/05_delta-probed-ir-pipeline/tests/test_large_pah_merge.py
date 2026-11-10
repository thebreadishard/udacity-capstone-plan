"""The large-PAH merge (`probes/large_pah_merge.py`, TASKS 49) on a synthetic corpus: the SMILES read from a geometry, the rows and folders
a merge writes, a second run that writes nothing, and every check that stops a merge. Naphthalene stands in for a layer-D molecule and
pyrene for a test molecule."""
from __future__ import annotations

import csv
import hashlib
import json
import shutil
import sys
from pathlib import Path

import numpy as np
import pytest
from rdkit import Chem
from rdkit.Chem import AllChem

from pin_tools import PLAN

sys.path.insert(0, str(PLAN / "probes"))
import large_pah_merge as LM

NAPH = "c1ccc2ccccc2c1"
PYRENE = "c1cc2ccc3cccc4ccc(c1)c2c34"
DECK = {"deck": "v1", "basis": "6-31G*", "low_functional": "B3LYP", "threads": 4, "memory_gb": 12}


def _geometry(smiles: str) -> tuple[list[str], list[list[float]]]:
    """A force-field geometry (Å) with hydrogens, the same at every call."""
    mol = Chem.AddHs(Chem.MolFromSmiles(smiles))
    if AllChem.EmbedMolecule(mol, randomSeed=7) != 0:
        raise RuntimeError(f"{smiles}: no embedding")
    AllChem.MMFFOptimizeMolecule(mol)
    xyz = mol.GetConformer().GetPositions().tolist()
    return [a.GetSymbol() for a in mol.GetAtoms()], xyz


def _folder(root: Path, layer: str, smiles: str, formula: str) -> str:
    """A complete fetched folder for the molecule; its id."""
    symbols, xyz = _geometry(smiles)
    skeleton = LM.LS.skeleton_from_xyz(symbols, xyz)
    mol_id = LM.LJ.mol_id(layer, skeleton)
    d = root / mol_id
    d.mkdir(parents=True)
    geometry = {"symbols": symbols, "coords_bohr": [[x / LM.BOHR_ANGSTROM for x in atom] for atom in xyz], "charge": 0,
                "multiplicity": 1}
    job = {"id": mol_id, "layer": layer, "deck": dict(DECK, threads=8, memory_gb=24),
           "source": {"pahdb_uid": 1, "formula": formula, "name": "", "skeleton": skeleton}}
    result = {"id": mol_id, "layer": layer, "status": "done", "labels": "analytic_only", "n_imaginary_b3lyp": 0, "n_imaginary_wb97x": 0}
    for name, record in (("geometry.json", geometry), ("job.json", job), ("result.json", result)):
        (d / name).write_text(json.dumps(record), encoding="utf-8")
    for name in ("hessian_b3lyp_analytic.npz", "hessian_wb97x_analytic.npz"):
        np.savez(d / name, H=np.zeros(1))
    np.savez(d / "dipole_b3lyp_cphf.npz", passed=True)
    return mol_id


def _manifest(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=LM.CF.BM.FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows({**{k: "" for k in LM.CF.BM.FIELDS}, **r} for r in rows)


class Tree:
    """A corpus with one benzene row, and one fetched folder each for naphthalene (D) and pyrene (T)."""

    def __init__(self, root: Path) -> None:
        self.fetched = root / "fetched"
        corpus = root / "corpus"
        (corpus / "molecules").mkdir(parents=True)
        (corpus / "decks").mkdir()
        (corpus / "decks" / "deck_v1.json").write_text(json.dumps(DECK), encoding="utf-8")
        _manifest(corpus / "manifest.csv", [{"id": "A_benzene", "layer": "A", "name": "benzene", "smiles": "c1ccccc1", "status": "done"}])
        self.d_id = _folder(self.fetched, "D", NAPH, "C10H8")
        self.t_id = _folder(self.fetched, "T", PYRENE, "C16H10")
        self.ids = [self.t_id, self.d_id]
        self.expected = {self.t_id: ("pyrene", LM.HT.canonical(PYRENE))}
        self.target = LM.Target((self.fetched,), corpus)

    def plan(self) -> LM.Plan:
        return LM.plan(self.ids, self.target, self.expected)

    def rewrite(self, mol_id: str, name: str, **change) -> None:
        path = self.fetched / mol_id / name
        path.write_text(json.dumps({**json.loads(path.read_text(encoding="utf-8")), **change}), encoding="utf-8")


@pytest.fixture
def tree(tmp_path) -> Tree:
    return Tree(tmp_path)


@pytest.mark.parametrize("smiles", [NAPH, PYRENE])
def test_the_smiles_read_from_a_geometry_is_the_molecule(smiles):
    assert LM.aromatic_smiles(*_geometry(smiles)) == LM.HT.canonical(smiles)


@pytest.mark.parametrize(("smiles", "reason"), [("C1CCCCC1", "neighbours"), ("c1ccncc1", "hydrocarbon")])
def test_a_geometry_that_is_not_an_sp2_hydrocarbon_is_refused(smiles, reason):
    with pytest.raises(ValueError, match=reason):
        LM.aromatic_smiles(*_geometry(smiles))


def test_the_selection_s_structures_are_the_frozen_test_ids():
    frozen = (LM.CORPUS / "large_pah_test_ids_2026-10-12.txt").read_text(encoding="utf-8").splitlines()
    assert set(LM.selection_structures()) == {s.strip() for s in frozen if s.strip() and not s.startswith("#")}


def test_a_checked_folder_becomes_a_done_row(tree):
    p = tree.plan()
    rows = {r["id"]: r for r in p.rows}
    assert [i for i, _ in p.folders] == tree.ids and p.rows_written == () and p.folders_in_place == ()
    assert all(isinstance(f, tuple) for f in (p.rows, p.folders, p.rows_written, p.folders_in_place))
    d, t = rows[tree.d_id], rows[tree.t_id]
    assert (d["layer"], d["name"], d["smiles"], d["n_heavy"], d["n_atoms"]) == ("D", "PAHdb 1 C10H8", LM.HT.canonical(NAPH), 10, 18)
    assert (t["layer"], t["name"], t["n_atoms"]) == ("T", "pyrene", 26)
    deck_file = tree.target.deck
    assert {(r["status"], r["machine"], r["deck"]) for r in p.rows} == {("done", LM.MACHINE, hashlib.sha256(deck_file.read_bytes()).hexdigest()[:12])}


def test_the_merge_writes_rows_and_whole_folders_and_a_second_run_nothing(tree, monkeypatch, capsys):
    monkeypatch.setattr(LM, "default_target", lambda: tree.target)
    monkeypatch.setattr(LM.LR, "ids", lambda: tree.ids)
    monkeypatch.setattr(LM, "selection_structures", lambda: tree.expected)
    before = tree.target.manifest.read_bytes()
    assert LM.main([]) == 0
    assert tree.target.manifest.read_bytes() == before and not any(tree.target.molecules.iterdir())
    assert LM.main(["--write"]) == 0
    assert tree.target.manifest.read_bytes().startswith(before)
    assert [r["id"] for r in LM.P3.manifest_rows(tree.target.manifest)] == ["A_benzene", *tree.ids]
    assert all(LM.LR.state(str(tree.target.molecules / i)) == "ready" for i in tree.ids)
    assert sorted(p.name for p in tree.target.corpus.iterdir() if p.name.startswith("manifest.csv.pre_large_pah_merge_"))
    assert not (tree.target.corpus / "large_pah_merge_staging").exists()
    again = tree.plan()
    assert not again.rows and not again.folders and again.rows_written == tuple(tree.ids) and again.folders_in_place == tuple(tree.ids)
    written = tree.target.manifest.read_bytes()
    assert LM.main(["--write"]) == 0 and tree.target.manifest.read_bytes() == written
    assert "0 rows to append (2 written already), 0 folders to copy (2 in place already)" in capsys.readouterr().out


def test_a_twin_in_the_manifest_stops_the_merge(tree):
    _manifest(tree.target.manifest, [{"id": "B_naph", "layer": "B", "name": "naphthalene", "smiles": "C1=CC=C2C=CC=CC2=C1", "status": "done"}])
    with pytest.raises(ValueError, match="manifest rows with the same molecule as a merge row: B_naph"):
        tree.plan()


def test_two_merge_rows_of_one_molecule_stop_the_merge(tree):
    pyrene_in_d = _folder(tree.fetched, "D", PYRENE, "C16H10")              # a test molecule in the training layer
    tree.ids = [*tree.ids, pyrene_in_d]
    with pytest.raises(ValueError, match=f"merge rows that are the same molecule: {pyrene_in_d}, {tree.t_id}"):
        tree.plan()


def test_a_row_written_with_other_values_stops_the_merge(tree):
    _manifest(tree.target.manifest, [{"id": tree.d_id, "layer": "D", "name": "another", "smiles": NAPH, "status": "done"}])
    with pytest.raises(ValueError, match="in the manifest with other values"):
        tree.plan()


def test_a_wrong_formula_stops_the_merge(tree):
    job = json.loads((tree.fetched / tree.d_id / "job.json").read_text(encoding="utf-8"))
    tree.rewrite(tree.d_id, "job.json", source=dict(job["source"], formula="C10H10"))
    with pytest.raises(ValueError, match="the job says C10H10"):
        tree.plan()


def test_another_deck_stops_the_merge(tree):
    tree.rewrite(tree.d_id, "job.json", deck=dict(DECK, basis="def2-SVP"))
    with pytest.raises(ValueError, match=r"differs from deck_v1\.json in basis"):
        tree.plan()


def test_a_test_molecule_that_is_not_the_selection_s_stops_the_merge(tree):
    tree.expected = {}
    with pytest.raises(ValueError, match="not the selection's structure"):
        tree.plan()


def test_a_charged_geometry_stops_the_merge(tree):
    tree.rewrite(tree.d_id, "geometry.json", charge=1, multiplicity=2)
    with pytest.raises(ValueError, match="neutral closed-shell"):
        tree.plan()


def test_an_incomplete_or_a_double_fetch_stops_the_merge(tree, tmp_path):
    second = tmp_path / "fetched_again"
    shutil.copytree(tree.fetched, second)
    tree.target = LM.Target((tree.fetched, second), tree.target.corpus)
    with pytest.raises(ValueError, match="2 ready fetched folders"):
        tree.plan()
    shutil.rmtree(second)
    (tree.fetched / tree.d_id / "hessian_wb97x_analytic.npz").unlink()
    with pytest.raises(ValueError, match=r"0 ready fetched folders \(.*no hessian_wb97x_analytic.npz"):
        tree.plan()


def test_a_folder_in_the_corpus_that_is_not_ready_stops_the_merge(tree):
    (tree.target.molecules / tree.d_id).mkdir()
    with pytest.raises(ValueError, match="exists and is not ready"):
        tree.plan()


def test_a_copy_that_fails_halfway_leaves_only_whole_folders_and_stops_the_next_copy(tree, monkeypatch):
    p, real = tree.plan(), shutil.copytree

    def copy_all_but_d(src, dst, *args, **kwargs):
        if Path(src).name == tree.d_id:
            raise OSError("disk full")
        return real(src, dst, *args, **kwargs)

    monkeypatch.setattr(LM.shutil, "copytree", copy_all_but_d)
    with pytest.raises(OSError, match="disk full"):
        LM.copy_folders(p.folders, tree.target)
    assert [d.name for d in tree.target.molecules.iterdir()] == [tree.t_id]
    assert LM.LR.state(str(tree.target.molecules / tree.t_id)) == "ready"
    with pytest.raises(FileExistsError, match="interrupted merge"):
        LM.copy_folders(tree.plan().folders, tree.target)


def test_a_left_staging_folder_stops_the_copy(tree):
    p = tree.plan()
    (tree.target.corpus / "large_pah_merge_staging").mkdir()
    with pytest.raises(FileExistsError, match="interrupted merge"):
        LM.copy_folders(p.folders, tree.target)
    assert not any(tree.target.molecules.iterdir())
