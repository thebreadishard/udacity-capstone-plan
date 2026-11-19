"""The molecule the pipeline works on (`modules/08_industry_synthesis/m08/molecule.py`, TASKS 278; aromir audit of 19 Nov 2026, F1 and F2):
atom-map numbers change neither the canonical SMILES, the atom order nor the 'seen' role; an xyz file reaches the SMILES route's name and
order where its perceived bonds are another resonance structure; the canonical forms are aromir's, string for string."""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np
import pytest
from rdkit import Chem

from pin_tools import DATA, PLAN

sys.path.insert(0, str(PLAN / "modules" / "08_industry_synthesis"))
from m08 import molecule as M
from m08 import pipeline as P
from m08 import reuse as R
from m08 import seen as S

PIN_MODEL = DATA / "rungC_cc_pin_model.pt"
TRAINING = (("C", "CL", "F", "H", "N", "O", "S"), (6, 40))

# The expected strings are aromir's (tests/test_admission.py at aromir commit 4d0461c): the product and the pipeline name alike.
MAPPED_PAIRS = [("Cc1ccc(O)cc1Cl", "[CH3:5]c1ccc(O)cc1Cl"), ("c1ccc2ncccc2c1", "c1ccc2[n:1]cccc2c1"),
                ("N#Cc1ccc(F)cc1", "N#[C:2]c1ccc(F)cc1"), ("c1ccccc1", "[cH:1]1ccccc1")]
AZIDE_WRITINGS = ("[N-]=[N+]=Nc1ccccc1", "N#[N+][N-]c1ccccc1", "N#[N+]N=c1cccc[cH-]1")
STANDARD_FORMS = ["c1ccccc1", "Cc1ccccc1", "c1ccc2ccccc2c1", "O=[N+]([O-])c1ccccc1", "[O-][n+]1ccccc1", "N#Cc1ccccc1", "O=c1cccc[nH]1",
                  "CS(=O)(=O)c1ccccc1", "O=C(O)c1ccccc1", "c1ccc2[nH]ccc2c1", "Nc1ccc([N+](=O)[O-])cc1", "[C-]#[N+]c1ccccc1"]
XYZ_CASES = ["[N-]=[N+]=Nc1ccccc1", "CS(=O)c1ccccc1", "[O-][n+]1ccccc1", "CS(=O)(=O)c1ccccc1", "O=c1cccc[nH]1", "Cc1ccc(O)cc1Cl"]


@pytest.fixture
def pin_registry(monkeypatch):
    """The pin model counts as carried and the training set holds S, F and Cl, so the routes are compared without the registry."""
    monkeypatch.setattr(P.MR, "require_carried", lambda p, kind=None: {"status": "carried", "network": P.NETWORK, "version": "pin"})
    monkeypatch.setattr(P, "training_set", lambda models: TRAINING)


def config(tmp_path: Path, **kw) -> P.PipelineConfig:
    base = dict(name="mol", out_root=tmp_path, smiles="c1ccccc1", models=(PIN_MODEL,), psi4_python=Path(sys.executable))
    return P.PipelineConfig(**(base | kw))


def listed_xyz(path: Path, atoms: list[list], seed: int) -> Path:
    """An xyz file of atoms as [symbol, x, y, z] in Å, listed in a random order."""
    order = np.random.default_rng(seed).permutation(len(atoms))
    rows = [f"{atoms[k][0]} {atoms[k][1]:.8f} {atoms[k][2]:.8f} {atoms[k][3]:.8f}" for k in order]
    path.write_text(f"{len(rows)}\nlisted\n" + "\n".join(rows) + "\n", encoding="utf-8")
    return path


def bond_graph(atoms: list[list]) -> tuple[list[str], np.ndarray]:
    """(element per position, adjacency matrix) of atoms as [symbol, x, y, z] in Å."""
    from rdkit.Chem import rdDetermineBonds

    m = Chem.MolFromXYZBlock(f"{len(atoms)}\n\n" + "\n".join(f"{s} {x:.10f} {y:.10f} {z:.10f}" for s, x, y, z in atoms))
    rdDetermineBonds.DetermineConnectivity(m)
    return [a.GetSymbol() for a in m.GetAtoms()], Chem.GetAdjacencyMatrix(m)


@pytest.mark.parametrize(("plain", "mapped"), MAPPED_PAIRS)
def test_atom_map_numbers_are_cleared_and_said(tmp_path, pin_registry, plain, mapped):
    unmapped = P.admit(config(tmp_path, smiles=plain))
    cleared = P.admit(config(tmp_path, smiles=mapped))
    assert cleared.smiles == unmapped.smiles == plain
    assert unmapped.input_changes == () and "input_changes" not in unmapped.record()
    assert cleared.input_changes == (M.ATOM_MAPS_CLEARED,) and cleared.record()["input_changes"] == (M.ATOM_MAPS_CLEARED,)


def test_a_mapped_smiles_starts_from_the_same_geometry_in_the_same_order(tmp_path):
    assert P.start_geometry(config(tmp_path, smiles="[CH3:5]c1ccc(O)cc1Cl")) == P.start_geometry(config(tmp_path, smiles="Cc1ccc(O)cc1Cl"))


def test_a_mapped_benzene_is_trained_like_benzene():
    release = S.build({"A_benz"}, {}, {"A_benz": "c1ccccc1"})
    assert S.status("[cH:1]1ccccc1", release, None) == S.status("c1ccccc1", release, None)
    assert S.status("[cH:1]1ccccc1", release, None)["role"] == "trained"


def test_the_seen_index_standardises_the_training_smiles_on_load():
    """A training row written in another Lewis structure (a pentavalent nitro) is found by the request's standard form."""
    seen = S.build({"A_nitro"}, {}, {"A_nitro": "O=N(=O)c1ccccc1"})
    assert S.status("O=[N+]([O-])c1ccccc1", seen, None)["role"] == "trained"


def test_a_stereo_free_trained_row_covers_every_configuration(tmp_path, pin_registry):
    """The xyz sulfoxide names its configuration; the training row leaves it open, so the molecule is trained, also for release."""
    made, _ = P.start_geometry(config(tmp_path, smiles="CS(=O)c1ccccc1"))
    from_xyz = P.admit(config(tmp_path, smiles=None, xyz=listed_xyz(tmp_path / "s.xyz", made, 0))).smiles
    assert "@" in from_xyz
    seen = S.build({"A_sox"}, {"a": {"A_benz"}}, {"A_sox": "CS(=O)c1ccccc1", "A_benz": "c1ccccc1"})
    got = S.status(from_xyz, seen, None)
    assert (got["role"], got["ids"]) == ("trained", ["A_sox"])
    assert S.status(from_xyz, seen, None, release=seen)["role"] == "release_trained"
    assert S.status("c1ccccc1", seen, None)["role"] == "a"
    assert S.status("CC(O)c1ccccc1", seen, None)["role"] == "unseen"


def test_a_diastereomer_of_a_trained_or_held_out_molecule_is_a_stereoisomer():
    trained, other = "C[C@H](O)[C@H](C)c1ccccc1", "C[C@H](O)[C@@H](C)c1ccccc1"
    seen = S.build({"A_one"}, {}, {"A_one": trained})
    got = S.status(other, seen, None)
    assert (got["role"], got["ids"]) == ("stereoisomer", ["A_one"]) and "A_one" in got["text"]
    assert S.status(trained, seen, None)["role"] == "trained"
    held = S.status(other, S.build(set(), {"a": {"A_one"}, "b": set()}, {"A_one": trained}), None)
    assert (held["role"], held["ids"]) == ("stereoisomer_held_out", ["A_one"]) and "hold-out (a)" in held["text"]


def test_without_stereo_refuses_a_string_that_is_no_smiles():
    with pytest.raises(ValueError, match="does not parse"):
        M.without_stereo("c1ccc")


@pytest.mark.parametrize("writing", AZIDE_WRITINGS)
def test_every_resonance_structure_of_an_azide_gets_one_name(writing):
    assert M.canonical(writing) == "[N-]=[N+]=Nc1ccccc1"


def test_the_resonance_structure_does_not_depend_on_the_atom_order():
    for writing in AZIDE_WRITINGS:
        listings = Chem.MolToRandomSmilesVect(Chem.MolFromSmiles(writing), 20, randomSeed=7)
        assert {M.canonical(listing) for listing in listings} == {"[N-]=[N+]=Nc1ccccc1"}


def test_a_hypervalent_sulfoxide_is_written_charge_separated():
    assert M.canonical("CS(=O)c1ccccc1") == M.canonical("C[S+]([O-])c1ccccc1") == "C[S+]([O-])c1ccccc1"


@pytest.mark.parametrize("smiles", STANDARD_FORMS)
def test_a_molecule_already_in_standard_form_keeps_its_name(smiles):
    assert M.canonical(smiles) == smiles == P.canonical_smiles(smiles)


def test_a_nitro_group_written_hypervalent_gets_the_usual_name():
    assert M.canonical("O=N(=O)c1ccccc1") == "O=[N+]([O-])c1ccccc1"


def test_a_molecule_without_formal_charges_takes_no_resonance_pass(monkeypatch):
    def refuse(mol):
        raise AssertionError("called")

    monkeypatch.setattr(M, "_one_resonance_structure", refuse)
    assert M.canonical_of(M.from_smiles("Oc1ccccc1").mol) == "Oc1ccccc1"        # from_smiles: `canonical` is cached
    with pytest.raises(AssertionError, match="called"):
        M.from_smiles("[O-][n+]1ccccc1")


def test_an_unparsable_or_empty_smiles_has_no_canonical_form():
    assert M.canonical("") is None and M.canonical(None) is None and M.canonical("c1ccc") is None
    with pytest.raises(ValueError, match="does not parse"):
        P.canonical_smiles("c1ccc")


@pytest.mark.parametrize("smiles", XYZ_CASES)
def test_an_xyz_file_gets_the_name_and_the_atom_order_of_its_smiles(tmp_path, pin_registry, smiles):
    """aromir's six cases, nitro left out: RDKit's bond perception refuses some atom listings of nitrobenzene, outside TASKS 278."""
    by_smiles = P.admit(config(tmp_path, smiles=smiles))
    made, _ = P.start_geometry(config(tmp_path, smiles=smiles))
    ref_graph = bond_graph(made)
    for seed in range(3):
        cfg = config(tmp_path, smiles=None, xyz=listed_xyz(tmp_path / f"{seed}.xyz", made, seed))
        assert M.without_stereo(P.admit(cfg).smiles) == by_smiles.smiles
        elements, adjacency = bond_graph(P.start_geometry(cfg)[0])
        assert elements == ref_graph[0] and (adjacency == ref_graph[1]).all()


def test_an_xyz_sulfoxide_keeps_the_configuration_of_its_geometry(tmp_path, pin_registry):
    made, _ = P.start_geometry(config(tmp_path, smiles="CS(=O)c1ccccc1"))
    from_xyz = P.admit(config(tmp_path, smiles=None, xyz=listed_xyz(tmp_path / "s.xyz", made, 0)))
    assert from_xyz.smiles in {"C[S@+]([O-])c1ccccc1", "C[S@@+]([O-])c1ccccc1"}


def test_an_xyz_file_without_a_bonding_pattern_is_refused(tmp_path, pin_registry, monkeypatch):
    from rdkit.Chem import rdDetermineBonds

    def never(mol, charge):
        raise ValueError("could not find valid bond ordering")

    made, _ = P.start_geometry(config(tmp_path))
    xyz = listed_xyz(tmp_path / "r.xyz", made, 0)
    monkeypatch.setattr(rdDetermineBonds, "DetermineBonds", never)
    assert M.from_xyz(xyz, 0) is None
    with pytest.raises(P.Refused, match="does not parse"):
        P.admit(config(tmp_path, smiles=None, xyz=xyz))


def test_the_corpus_folders_are_matched_by_the_standard_form(tmp_path):
    with (tmp_path / "manifest.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id", "smiles", "status"])
        w.writeheader()
        w.writerows([{"id": "A_nitro", "smiles": "O=N(=O)c1ccccc1", "status": "done"},
                     {"id": "A_benz", "smiles": "[cH:1]1ccccc1", "status": "done"}])
    assert [p.name for p, _ in R.corpus_folders("O=[N+]([O-])c1ccccc1", tmp_path).folders] == ["A_nitro"]
    assert [p.name for p, _ in R.corpus_folders("c1ccccc1", tmp_path).folders] == ["A_benz"]
