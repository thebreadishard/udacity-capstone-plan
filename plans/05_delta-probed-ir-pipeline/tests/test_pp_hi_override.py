"""Standout core, `hi_override` (28 Sep 2026, the CC-level test): naming the corpus's own ωB97X Hessian as the override reproduces the standard Δ₂
exactly, a Hessian at another geometry is refused, and the deck hash does not depend on the high level. Uses benzene's corpus folder when present."""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "modules" / "standout_pattern_proposer"))
from pp import core as C  # noqa: E402

BENZENE = PLAN / "modules" / "05_support_predictor" / "corpus" / "molecules" / "A_8448043181"


@pytest.mark.skipif(not (BENZENE / "hessian_wb97x.npz").exists(), reason="corpus benzene folder not on this machine")
def test_override_with_the_same_file_reproduces_delta2_and_the_deck(tmp_path):
    ref = C.export_molecule(BENZENE, quick=True)
    over = C.export_molecule(BENZENE, quick=True, hi_override=BENZENE / "hessian_wb97x.npz")
    assert np.allclose(ref["D2"], over["D2"]) and ref["deck_hash"] == over["deck_hash"] and np.allclose(ref["R"], over["R"])


@pytest.mark.skipif(not (BENZENE / "hessian_wb97x.npz").exists(), reason="corpus benzene folder not on this machine")
def test_override_at_another_geometry_is_refused(tmp_path):
    z = np.load(BENZENE / "hessian_wb97x.npz")
    g = json.load(open(BENZENE / "geometry.json", encoding="utf-8"))
    coords = np.asarray(g["coords_bohr"], float) + 0.01
    p = tmp_path / "shifted.npz"
    np.savez(p, H_projected=z["H_projected"], coords_bohr=coords)
    with pytest.raises(ValueError):
        C.delta2(BENZENE, hi_override=p)
