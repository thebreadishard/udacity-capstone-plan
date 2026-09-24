"""Tests of the Spectrum Atlas export on three molecules of the real corpus (benzene, naphthalene, one A2 molecule) — no compute, seconds."""
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import build_catalog as bc  # noqa: E402

REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CORPUS = os.path.join(REPO, "plans", "05_delta-probed-ir-pipeline", "modules", "05_support_predictor", "corpus", "molecules")


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    out = tmp_path_factory.mktemp("atlas")
    summary = bc.build(REPO, str(out), limit=60)
    return out, summary


def test_rung_counts_add_up(built):
    out, s = built
    cat = json.load(open(out / "catalog.json", encoding="utf-8"))
    assert sum(s["rung_counts"].values()) == len(cat) == s["n_molecules"]


def test_benzene_is_validated_with_evidence(built):
    out, _ = built
    cat = {r["id"]: r for r in json.load(open(out / "catalog.json", encoding="utf-8"))}
    b = cat["A_8448043181"]
    assert b["rung_label"] == "validated" and b["formula"] == "C6H6"
    for f in b["evidence"]:
        assert os.path.exists(os.path.join(REPO, "plans", "05_delta-probed-ir-pipeline", f))


def test_naphthalene_molecule_file(built):
    out, _ = built
    m = json.load(open(out / "molecules" / "A_01f3186607.json", encoding="utf-8"))
    assert m["formula"] == "C10H8" and m["n_atoms"] == 18
    for tag in ("b3lyp", "wb97x"):
        assert len(m["frequencies_cm"][tag]["all"]) == 54 and len(m["frequencies_cm"][tag]["vibrational"]) == 48
    assert any(r.startswith("layerA_") for r in m["releases"])


def test_second_route_flag_on_benzene(built):
    out, _ = built
    cat = {r["id"]: r for r in json.load(open(out / "catalog.json", encoding="utf-8"))}
    assert "second_route_disagrees" in cat["A_8448043181"]["flags"] and "replaced_by_second_route" in cat["A_8448043181"]["flags"]


def test_frequency_lengths_are_3N_everywhere(built):
    out, _ = built
    for p in (out / "molecules").glob("*.json"):
        m = json.load(open(p, encoding="utf-8"))
        for tag in ("b3lyp", "wb97x"):
            assert len(m["frequencies_cm"][tag]["all"]) == 3 * m["n_atoms"]


def test_vib_only_drops_six():
    import numpy as np
    f = np.array([-30.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 100.0, 200.0])
    assert list(bc.vib_only(f)) == [-30.0, 100.0, 200.0]
