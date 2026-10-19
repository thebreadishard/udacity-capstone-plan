"""probes/s2b_select.py (S2b registration, 'Training set'), on synthetic manifest rows: every clause of the rule keeps or drops the molecule it
names, a scaffold yields its smallest rigid member with ties broken by the sha1 of the id, S2's scaffolds are not repeated, and the outputs
refuse a member without a geometry."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes"))
pytest.importorskip("rdkit")
S = pytest.importorskip("s2b_select")
sha = S.sha

CATIONS = {"cation", "phen_plus"}


def row(mid, smiles, n_atoms, status="done"):
    return {"id": mid, "smiles": smiles, "n_atoms": str(n_atoms), "status": status}


def state(mol_id):
    return (1, 2) if mol_id in CATIONS else (0, 1)


def universe(rows, excluded=frozenset()):
    return S.universe(rows, excluded=set(excluded), state=state)


@pytest.mark.parametrize(("smiles", "rigid"), [
    ("c1ccc2ccccc2c1", True),          # naphthalene
    ("c1ccc2[nH]ccc2c1", False),       # indole: H on N
    ("Oc1ccccc1", False),              # phenol: H on O
    ("Cc1ccccc1", False),              # toluene: CH₃
    ("c1ccc(-c2ccccc2)cc1", False),    # biphenyl: a rotatable bond
    ("C=Cc1ccccc1", False),            # styrene: the vinyl rotor
    ("c1ccc2occc2c1", True),           # benzofuran
    ("O=C1C=CC(=O)C=C1", True),        # benzoquinone: O without H
    ("C(#Cc1ccccc1)c1ccccc1", False),  # diphenylacetylene: RDKit counts no rotatable bond, the C≡C linker turns
    ("C#Cc1ccccc1", True),             # phenylacetylene: the side chain is no linker
    ("O=C1OC(=O)c2cccc3cccc1c23", True),   # naphthalic anhydride: exocyclic C=O is terminal
    ("c1ccc2c(c1)-c1cccc3cccc-2c13", True),  # fluoranthene: the five-ring bond is in a ring
])
def test_rigid_clause(smiles, rigid):
    assert S.is_rigid(S.Chem.MolFromSmiles(smiles)) is rigid


def test_universe_clauses():
    rows = [row("keep", "c1ccc2ccccc2c1", 18), row("big", "c1ccc2ccccc2c1", 29), row("queued", "c1ccc2ccccc2c1", 18, status="queued"),
            row("cation", "c1ccc2ccccc2c1", 18), row("sulfur", "c1ccsc1", 9), row("held", "c1ccc2ccccc2c1", 18), row("empty", "c1ccccc1", "")]
    ids = [m["id"] for m in universe(rows, excluded={"held"})]
    assert ids == ["keep"]          # 'cation' carries its neutral parent's SMILES, as pool 3's cations do


def test_a_cation_does_not_win_its_neutral_parents_scaffold():
    rows = [row("phen_plus", "c1ccc2c(c1)ccc1ccccc12", 24), row("phen", "c1ccc2c(c1)ccc1ccccc12", 24)]
    assert [m["id"] for m in S.select(universe(rows), s2_scaffolds=set())] == ["phen"]


def test_a_missing_job_json_fails_loudly():
    with pytest.raises(SystemExit, match="no job"):
        S.recorded_state("A_no_such_molecule")


def test_one_smallest_rigid_member_per_new_scaffold():
    rows = [row("naph_methyl", "Cc1ccc2ccccc2c1", 21),             # naphthalene scaffold, not rigid
            row("naph_cyano", "N#Cc1ccc2ccccc2c1", 19),           # naphthalene scaffold, rigid, larger
            row("naph", "c1ccc2ccccc2c1", 18),                    # naphthalene scaffold, rigid, smallest
            row("quin", "c1ccc2ncccc2c1", 17),                    # quinoline scaffold
            row("benz", "c1ccccc1", 12)]                          # benzene scaffold: S2's own
    chosen = S.select(universe(rows), s2_scaffolds={"c1ccccc1"})
    assert [m["id"] for m in chosen] == ["quin", "naph"]          # smallest first


def test_ties_by_sha1_of_the_id():
    a, b = "A_tie_one", "A_tie_two"
    first = min((a, b), key=sha)
    rows = [row(a, "N#Cc1ccc2ccccc2c1", 19), row(b, "N#Cc1cccc2ccccc12", 19)]    # 2- and 1-cyanonaphthalene, one scaffold
    chosen = S.select(universe(rows), s2_scaffolds=set())
    assert [m["id"] for m in chosen] == [first]


def test_a_scaffold_with_no_rigid_member_gives_nothing():
    rows = [row("tol", "Cc1ccccc1", 15), row("phenol", "Oc1ccccc1", 13)]
    assert S.select(universe(rows), s2_scaffolds=set()) == []


def test_outputs_refuse_a_member_without_geometry(tmp_path):
    member = {"id": "A_no_such_molecule", "smiles": "c1ccccc1", "n_atoms": 12, "rigid": True, "scaffold": "c1ccccc1"}
    with pytest.raises(SystemExit, match=r"no geometry\.json"):
        S.write_outputs(str(tmp_path), [member], [member])
    assert not (tmp_path / "selection.json").exists()


def test_outputs_written_with_lf(tmp_path, monkeypatch):
    member = {"id": "A_x", "smiles": "c1ccccc1", "n_atoms": 12, "rigid": True, "scaffold": "c1ccccc1"}
    monkeypatch.setattr(S.os.path, "isfile", lambda _p: True)
    S.write_outputs(str(tmp_path), [member], [member])
    tsv = (tmp_path / "s2b_ids.tsv").read_bytes()
    assert tsv == b"A_x\tmodules/05_support_predictor/corpus/molecules/A_x/geometry.json\n"
    assert '"universe": 1' in (tmp_path / "selection.json").read_text(encoding="utf-8")
