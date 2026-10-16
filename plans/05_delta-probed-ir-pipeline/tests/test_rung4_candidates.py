"""TASKS 61 step 1 (14 Oct 2026): the frozen rung-4 list. Parents are the five four-ring benzenoids other than pyrene (C18H12, four rings);
30 rows per family, ≤ 40 atoms, deterministic bytes; no SMILES of the manifest (except each parent's pending layer-G twin, recorded in
same_as), of pool 3's frozen list, or twice in the list; the first fifteen children of a family carry fifteen different substituents;
tetracene is the test family (never ranked), the other families rank 1..30 with the parent first; the manifest append adds the rows once,
moves the layer-G twins, and leaves every other row byte-identical."""
import csv
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


def test_the_build_reproduces_the_frozen_list_after_its_own_append(rows, tmp_path):
    """16 Oct 2026: after the append the manifest holds the 150 rows and the five twins 'moved'; the build must still give the frozen bytes."""
    frozen = PLAN / "modules" / "05_support_predictor" / "out" / "rung4_candidates_2026-10-14.csv"
    if not frozen.exists():
        pytest.skip("the frozen list is not present")
    R.write_csv(rows, tmp_path / "now.csv")
    assert (tmp_path / "now.csv").read_bytes() == frozen.read_bytes()


def test_nothing_already_known_except_the_parents_layer_g_twins(rows):
    man = {R.BM.canon(r["smiles"]): r for r in R.manifest_rows(MANIFEST) if r["smiles"] and r["layer"] != R.LAYER}
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


def before_the_append(src: Path, dst: Path) -> None:
    """The manifest as it was before rung 4's append: without the R4 rows, the twins pending again."""
    with open(src, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fields, kept = reader.fieldnames, [r for r in reader if r["layer"] != R.LAYER]
    for r in kept:
        if r["layer"] == "G" and r["status"] == "moved":
            r["status"] = "pending"
    with open(dst, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(kept)


def test_manifest_append_is_idempotent_and_touches_only_the_twins(rows, tmp_path):
    m = tmp_path / "manifest.csv"
    before_the_append(MANIFEST, m)
    before = m.read_bytes().splitlines()
    assert R.append_manifest(rows, m) == 150 and R.append_manifest(rows, m) == 0
    after = m.read_bytes().splitlines()
    twins = {r["same_as"] for r in rows if r["same_as"]}
    changed = [i for i, (a, b) in enumerate(zip(before, after[:len(before)], strict=True)) if a != b]
    assert len(after) == len(before) + 150 and len(changed) == len(twins) == 5
    by_id = {r["id"]: r for r in csv.DictReader(open(m, newline="", encoding="utf-8"))}
    assert all(by_id[g]["status"] == "moved" for g in twins) and all(by_id[r["id"]]["status"] == "pending" for r in rows)


def test_jobs_from_the_frozen_list(tmp_path):
    """probes/rung4_jobs.py (15 Oct 2026): every row becomes an optimise-only psi4 job with the list's atom count and the server's out_dir."""
    import json as _json

    import rung4_jobs as J
    rows = list(csv.DictReader(open(J.CSV, encoding="utf-8")))
    deck = dict(_json.load(open(J.DECK, encoding="utf-8")), threads=8, memory_gb=24)
    for r in rows[:3] + [next(x for x in rows if x["test_family"] == "1")]:
        j = J.job(r, deck, "/srv/r4")
        assert len(j["xyz_angstrom"]) == int(r["n_atoms"]) and j["out_dir"] == f"/srv/r4/{r['id']}"
        assert j["optimise"] and not j["hessians"] and j["layer"] == "R4" and j["source"]["test_family"] == int(r["test_family"])
    assert J.job(rows[0], deck, "/srv/r4") == J.job(rows[0], deck, "/srv/r4")                        # deterministic (seed 0)
