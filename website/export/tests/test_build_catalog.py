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


def test_heights_for_benzene_aligned_and_none_for_naphthalene(built):
    """TASKS 44 (10 Oct 2026): band heights from module 08's shape, aligned with the listed B3LYP positions; positions only without an APT."""
    out, summary = built
    def read(name):
        with open(os.path.join(out, "molecules", name), encoding="utf-8") as f:
            return json.load(f)
    b = read("A_8448043181.json")
    pos, h = b["frequencies_cm"]["b3lyp"]["vibrational"], b["intensities_km_mol"]["b3lyp"]
    assert len(h) == len(pos) == 30 and b["shape"]["n_ir_active"] == 7 and b["predicted_spectrum"] is None
    i = max(range(30), key=lambda k: h[k])
    assert abs(pos[i] - 694.6) < 0.5 and 70 < h[i] < 85                  # benzene's C–H out-of-plane band (a2u)
    n = read("A_01f3186607.json")
    assert n["intensities_km_mol"] is None and n["shape"] is None
    assert summary["n_with_intensities"] >= 1 and summary["shape_accuracy"]["proxy"]["corrected"]["spectrum_overlap"] > 0.9


def test_heights_refused_when_positions_differ():
    sh = {"kind": "positions and heights", "sticks": [{"omega_cm": 100.0, "km_mol": 1.0}], "max_dev_from_listed_cm": 2.0}
    assert bc.heights_for(sh, [102.0]) is None
    assert bc.heights_for(dict(sh, max_dev_from_listed_cm=0.0), [100.0]) == [1.0]
    assert bc.heights_for({"kind": "positions only"}, [100.0]) is None


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


def test_source_per_layer(built):
    out, summary = built
    catalog = json.load(open(os.path.join(out, "catalog.json"), encoding="utf-8"))
    assert all(r["source"] for r in catalog) and sum(summary["source_counts"].values()) == len(catalog)
    known = bc.source_of(dict(layer="G", note="source=generator v0.1+v0.2; list abc; system c1ccc2ccccc2c1; bare system; pubchem yes; rank 1"))
    new = bc.source_of(dict(layer="G", note="source=generator v0.1+v0.2; list abc; system c1ccncc1; most frequent molecule; pubchem no; rank 2"))
    assert known.endswith("known to PubChem") and new.endswith("not in PubChem")
    assert bc.source_of(dict(layer="C", note="")) == bc.SOURCES["C"]
    with pytest.raises(KeyError):
        bc.source_of(dict(layer="Z", note=""))


def test_anchored_rows_follow_the_registry(built):
    out, _ = built
    cat = {r["id"]: r for r in json.load(open(out / "catalog.json", encoding="utf-8"))}
    ev, level = bc.anchored_from_registry(os.path.join(REPO, "plans", "05_delta-probed-ir-pipeline"))
    for mid, row in cat.items():
        if row["rung"] >= 4:
            assert row["evidence"][0] == ev[mid][0] and row["anchor_level"] == level[mid]
    assert level.get("A_8448043181") == "CCSD(T)/cc-pVTZ"


def test_anchor_readings_travel_with_the_registry_file(built):
    """8 Oct 2026: benzene's R0 diagonal reading stays in its evidence after the registry's Hessian (module 08's certificate reads it)."""
    out, _ = built
    b = {r["id"]: r for r in json.load(open(out / "catalog.json", encoding="utf-8"))}["A_8448043181"]
    assert any(f.endswith("R0_DIAGONAL_READING_2026-09-22.md") for f in b["evidence"][1:])
