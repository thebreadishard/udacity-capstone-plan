"""P3-6 tooling (decision 54, 3 Oct 2026): the corpus runner's pool-3 cation path. The parent id is read from the row's note; a missing parent
geometry is refused with the reason; the start geometry is the parent's (bohr → Å) with the seeded distortion, deterministic, optimised afterwards;
layer P3c rows get the cation deck (UKS, charge 1, doublet, overrides applied, its own hash) and every other layer the base deck."""
import json
import sys
from pathlib import Path

import pytest

PLAN = Path(__file__).resolve().parents[1]
CORPUS = PLAN / "modules" / "05_support_predictor" / "corpus"
sys.path.insert(0, str(CORPUS))
import run_corpus as R  # noqa: E402

BOHR = 0.529177210903


def test_cation_parent_from_note():
    assert R.cation_parent({"id": "P3c_x", "note": "pool3 cation; parent A_8448043181; charge 1 mult 2"}) == "A_8448043181"
    assert R.cation_parent({"id": "P3c_y", "note": "pool3 cation; parent B_8b12a55d3a"}) == "B_8b12a55d3a"
    with pytest.raises(ValueError):
        R.cation_parent({"id": "P3c_z", "note": "pool3 cation"})


def test_start_geometry_from_parent_with_seeded_distortion(tmp_path, monkeypatch):
    monkeypatch.setattr(R, "HERE", tmp_path)
    row = {"id": "P3c_abc", "layer": "P3c", "note": "pool3 cation; parent A_parent; charge 1 mult 2"}
    with pytest.raises(RuntimeError):
        R.start_geometry(row)
    d = tmp_path / "molecules" / "A_parent"
    d.mkdir(parents=True)
    coords = [[0.0, 0.0, 0.0], [0.0, -1.43, 1.11], [0.0, 1.43, 1.11]]
    (d / "geometry.json").write_text(json.dumps({"symbols": ["O", "H", "H"], "coords_bohr": coords, "masses_amu": [16, 1, 1]}), encoding="utf-8")
    xyz, optimise = R.start_geometry(row)
    assert optimise is True and [a[0] for a in xyz] == ["O", "H", "H"]
    shifts = [abs(xyz[i][k + 1] - coords[i][k] * BOHR) for i in range(3) for k in range(3)]
    assert 0 < max(shifts) < 0.05                                  # distorted, but by the 0.01 Å seed, not more
    assert R.start_geometry(row)[0] == xyz                         # deterministic


def test_deck_for_picks_the_cation_deck_for_p3c_only():
    R._CATION_DECK.clear()
    base = ({"deck": "v1", "threads": 16}, "basehash0000")
    assert R.deck_for({"layer": "B"}, base, {}) is base
    assert R.deck_for({"layer": "P3"}, base, {}) is base
    deck, h = R.deck_for({"layer": "P3c"}, base, {"threads": 8, "memory_gb": 12})
    assert deck["reference"] == "uks" and deck["charge"] == 1 and deck["multiplicity"] == 2
    assert deck["threads"] == 8 and deck["memory_gb"] == 12
    assert h != base[1] and len(h) == 12
    assert R.deck_for({"layer": "P3c"}, base, {})[0] is deck        # loaded once


def test_queue_order_places_pool3_between_the_layers_and_c():
    rows = [{"id": f"{L}_{k}", "layer": L, "priority": f"{k:02d}", "note": ""} for L in ("C", "P3", "P3c", "B", "A2", "A") for k in range(2)]
    order = [r["layer"] for r in R.queue_order(rows)]
    assert order[:2] == ["A", "A"] and order[-2:] == ["C", "C"]
    mid = order[2:-2]
    assert mid[:4] == ["B", "A2", "B", "A2"] and mid[4:] == ["P3c", "P3", "P3c", "P3"]
