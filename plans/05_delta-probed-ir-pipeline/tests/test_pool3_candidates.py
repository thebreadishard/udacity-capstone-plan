"""P3-3 (decision 54, 3 Oct 2026): the frozen pool-3 candidate list. Deterministic bytes; quotas 30/30/60; no duplicate SMILES inside the list or
against the manifest's neutral rows; heavy-atom cap; the five-ring parents have the right formula and five rings; every aza parent is C15H9N;
every cation has a finished neutral parent; hold-out (c) = three parents per family, never ranked; curve ranks are 1..n without gaps; the manifest
append adds the rows once with the manifest's own id scheme and leaves them alone on a second call."""
import csv
import shutil
import sys
from pathlib import Path

import pytest

pytest.importorskip("rdkit")
PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
import pool3_candidates as P  # noqa: E402

MANIFEST = PLAN / "modules" / "05_support_predictor" / "corpus" / "manifest.csv"
pytestmark = pytest.mark.skipif(not MANIFEST.exists(), reason="corpus manifest not present")


@pytest.fixture(scope="module")
def rows():
    return P.build(MANIFEST)


def test_quotas_and_determinism(rows, tmp_path):
    assert {f: sum(r["family"] == f for r in rows) for f in P.QUOTA} == P.QUOTA
    d1 = P.write_csv(rows, tmp_path / "a.csv")
    d2 = P.write_csv(P.build(MANIFEST), tmp_path / "b.csv")
    assert d1 == d2 and (tmp_path / "a.csv").read_bytes() == (tmp_path / "b.csv").read_bytes()
    assert (tmp_path / "a.csv.sha256").read_text().startswith(d1)


def test_no_duplicates_and_caps(rows):
    neutral = [r for r in rows if r["layer"] == "P3"]
    smiles = [r["smiles"] for r in neutral]
    assert len(set(smiles)) == len(smiles)
    known = {r["smiles"] for r in P.manifest_rows(MANIFEST) if r["smiles"]}
    assert not known & set(smiles)
    assert len({r["id"] for r in rows}) == len(rows)
    assert max(r["n_atoms"] for r in rows) <= P.MAX_ATOMS
    for r in rows:
        assert r["id"].startswith(r["layer"] + "_") and len(r["id"]) == len(r["layer"]) + 11


def test_parents_are_what_they_claim():
    for name, smi in P.FIVE_PARENTS.items():
        from rdkit import Chem
        m = Chem.MolFromSmiles(smi)
        assert m is not None and m.GetRingInfo().NumRings() == 5, name
        assert P.formula(smi) in ("C20H12", "C22H14"), name
    az = P.aza_parents()
    assert len(az) == 8 and all(P.formula(s) == "C15H9N" for s in az.values())


def test_cations_have_finished_parents_and_charge(rows):
    done = {r["id"] for r in P.manifest_rows(MANIFEST) if r["status"] == "done"}
    cats = [r for r in rows if r["family"] == "cation"]
    assert len(cats) == 60 and all(r["parent_id"] in done for r in cats)
    assert all(r["charge"] == 1 and r["multiplicity"] == 2 and r["layer"] == "P3c" for r in cats)
    assert all(r["charge"] == 0 and r["multiplicity"] == 1 for r in rows if r["family"] != "cation")
    assert sum(r["is_parent"] for r in cats) == len(P.CATION_PARENTS)


def test_holdout_c_and_curve_ranks(rows):
    for fam in P.QUOTA:
        fr = [r for r in rows if r["family"] == fam]
        held = [r for r in fr if r["holdout_c"]]
        assert len(held) == P.HOLDOUT_PARENTS and all(r["is_parent"] for r in held)
        assert all(r["curve_rank"] == 0 for r in held)
        ranks = sorted(r["curve_rank"] for r in fr if not r["holdout_c"])
        assert ranks == list(range(1, len(fr) - P.HOLDOUT_PARENTS + 1))


def test_manifest_append_is_idempotent(rows, tmp_path):
    m = tmp_path / "manifest.csv"
    shutil.copy(MANIFEST, m)
    n0 = len(P.manifest_rows(m))
    assert P.append_manifest(rows, m) == len(rows)
    assert P.append_manifest(rows, m) == 0
    out = P.manifest_rows(m)
    assert len(out) == n0 + len(rows)
    new = [r for r in out if r["layer"] in ("P3", "P3c")]
    assert all(r["status"] == "pending" and r["note"].startswith("pool3 ") for r in new)
    assert all("charge 1 mult 2" in r["note"] for r in new if r["layer"] == "P3c")
    with open(m, newline="", encoding="utf-8") as f:
        assert csv.DictReader(f).fieldnames == P.BM.FIELDS
