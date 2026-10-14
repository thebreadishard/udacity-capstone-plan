"""TASKS 61 step 1 (14 Oct 2026): the frozen rung-4 list. Parents are the five four-ring benzenoids other than pyrene (C18H12, four rings);
30 rows per family, ≤ 40 atoms, deterministic bytes; no SMILES of the manifest (except each parent's pending layer-G twin, recorded in
same_as), of pool 3's frozen list, or twice in the list; the first fifteen children of a family carry fifteen different substituents;
tetracene is the test family (never ranked), the other families rank 1..30 with the parent first; the manifest append adds the rows once,
moves the layer-G twins, and leaves every other row byte-identical."""
import csv
import shutil
import sys
from pathlib import Path

import pytest

pytest.importorskip("rdkit")
PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
import rung4_candidates as R  # noqa: E402
from rdkit import Chem  # noqa: E402
from rdkit.Chem import rdMolDescriptors  # noqa: E402

MANIFEST = PLAN / "modules" / "05_support_predictor" / "corpus" / "manifest.csv"
pytestmark = pytest.mark.skipif(not MANIFEST.exists(), reason="corpus manifest not present")


@pytest.fixture(scope="module")
def rows():
    return R.build(MANIFEST)


def test_parents_are_the_four_ring_benzenoids_other_than_pyrene():
    smis = {Chem.CanonSmiles(s) for s in R.PARENTS.values()}
    assert len(smis) == 5 and Chem.CanonSmiles("c1cc2ccc3cccc4ccc(c1)c2c34") not in smis
    for s in smis:
        m = Chem.MolFromSmiles(s)
        assert rdMolDescriptors.CalcMolFormula(m) == "C18H12" and m.GetRingInfo().NumRings() == 4


def test_counts_sizes_and_determinism(rows, tmp_path):
    assert {f: sum(r["family"] == f for r in rows) for f in R.PARENTS} == {f: 30 for f in R.PARENTS}
    assert max(r["n_atoms"] for r in rows) <= R.MAX_ATOMS and len({r["smiles"] for r in rows}) == len(rows) == len({r["id"] for r in rows})
    d1 = R.write_csv(rows, tmp_path / "a.csv")
    d2 = R.write_csv(R.build(MANIFEST), tmp_path / "b.csv")
    assert d1 == d2 and (tmp_path / "a.csv").read_bytes() == (tmp_path / "b.csv").read_bytes()


def test_nothing_already_known_except_the_parents_layer_g_twins(rows):
    man = {R.BM.canon(r["smiles"]): r for r in R.manifest_rows(MANIFEST) if r["smiles"]}
    pool3 = {R.BM.canon(r["smiles"]) for r in R.manifest_rows(R.POOL3_LIST)} if R.POOL3_LIST.exists() else set()
    for r in rows:
        if r["is_parent"]:
            assert r["same_as"] == man[r["smiles"]]["id"] and man[r["smiles"]]["layer"] == "G"
        else:
            assert r["smiles"] not in man and r["smiles"] not in pool3


def test_substituents_spread_before_positions(rows):
    for f in R.PARENTS:
        kids = [r for r in rows if r["family"] == f and not r["is_parent"]]
        assert len({r["name"].split("+")[1] for r in kids[:15]}) == 15


def test_tetracene_is_the_test_family_and_ranks_are_nested(rows):
    for f in R.PARENTS:
        fr = [r for r in rows if r["family"] == f]
        if f == R.TEST_FAMILY:
            assert all(r["test_family"] == 1 and r["curve_rank"] == 0 for r in fr)
        else:
            assert sorted(r["curve_rank"] for r in fr) == list(range(1, 31))
            assert next(r for r in fr if r["is_parent"])["curve_rank"] == 1 and all(r["test_family"] == 0 for r in fr)


def test_manifest_append_is_idempotent_and_touches_only_the_twins(rows, tmp_path):
    m = tmp_path / "manifest.csv"
    shutil.copy(MANIFEST, m)
    before = m.read_bytes().splitlines()
    assert R.append_manifest(rows, m) == 150 and R.append_manifest(rows, m) == 0
    after = m.read_bytes().splitlines()
    twins = {r["same_as"] for r in rows if r["same_as"]}
    changed = [i for i, (a, b) in enumerate(zip(before, after[:len(before)], strict=True)) if a != b]
    assert len(after) == len(before) + 150 and len(changed) == len(twins) == 5
    by_id = {r["id"]: r for r in csv.DictReader(open(m, newline="", encoding="utf-8"))}
    assert all(by_id[g]["status"] == "moved" for g in twins) and all(by_id[r["id"]]["status"] == "pending" for r in rows)
