"""Step (c) of the batch route (5 Oct 2026): layer G of the manifest from the frozen gated list — one row per new ring system; the bare system is the
representative when it passed the gate, else the most frequent molecule (ties by SMILES); PubChem-known systems first, then occurrences; systems whose
representative is already in the manifest are skipped; ids follow the manifest scheme; the append is idempotent and keeps the file's line ending."""
import csv
import sys
from pathlib import Path

import pytest

pytest.importorskip("rdkit")
PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
import layer_g_candidates as G  # noqa: E402

NAPH = "c1ccc2ccccc2c1"
TETRAPHENE = "c1ccc2cc3c(ccc4ccccc43)cc2c1"
AZA = "c1ccc2ncc3ccccc3c2c1"


def _row(smiles, system, occ, ring_class="r3", hetero="none"):
    return dict(smiles=smiles, stage="pass", occurrences=str(occ), runs="seed0", in_pubchem_set="False", n_heavy="", n_arom_rings="", ring_class=ring_class,
                hetero_class=hetero, ring_system=system, scaffold=system)


def test_representative_order_and_skip():
    rows = [_row("Cc1c2ccccc2c(C)c2c1ccc1ccccc12", TETRAPHENE, 613, "r4+"), _row(TETRAPHENE, TETRAPHENE, 389, "r4+"),
            _row("Cc1ccc2ncc3ccccc3c2c1", AZA, 50, "r3", "N"), _row("CCc1ccc2ncc3ccccc3c2c1", AZA, 50, "r3", "N"),
            _row("Cc1ccc2ccccc2c1", NAPH, 999, "r2")]
    out = G.build(rows, manifest_smiles={"Cc1ccc2ccccc2c1"}, known={AZA}, gated_sha="deadbeef")
    assert [r["ring_system"] for r in out] == [AZA, TETRAPHENE]                         # PubChem-known first; naphthalene is skipped (in the manifest)
    assert out[0]["smiles"] == "CCc1ccc2ncc3ccccc3c2c1" and out[0]["representative"] == "most frequent molecule"   # tie 50/50 → smaller SMILES
    assert out[1]["smiles"] == TETRAPHENE and out[1]["representative"] == "bare system" and out[1]["system_occurrences"] == 1002
    assert out[0]["id"] == "G_" + G.sha(out[0]["smiles"])[:10] and out[0]["rank"] == 1 and out[1]["rank"] == 2
    assert out[1]["n_heavy"] == 18 and out[1]["n_atoms"] == 30 and out[0]["name"].endswith("(PubChem)")


def test_csv_and_manifest_append_idempotent(tmp_path):
    rows = [_row(TETRAPHENE, TETRAPHENE, 10, "r4+")]
    out = G.build(rows, set(), set(), "deadbeef")
    digest = G.write_csv(out, tmp_path / "g.csv")
    assert len(digest) == 64 and list(csv.DictReader(open(tmp_path / "g.csv", encoding="utf-8")))[0]["id"] == out[0]["id"]
    man = tmp_path / "manifest.csv"
    man.write_bytes(("\r\n".join([",".join(G.BM.FIELDS), "A_x,A,p,benzene,c1ccccc1,,6,12,done,,,"]) + "\r\n").encode())
    assert G.append_manifest(out, man, digest) == 1
    assert G.append_manifest(out, man, digest) == 0
    rows_after = G.manifest_rows(man)
    assert len(rows_after) == 2 and rows_after[1]["layer"] == "G" and rows_after[1]["status"] == "pending" and "source=generator" in rows_after[1]["note"]
    assert b"\r\n" in man.read_bytes()[-4:]
