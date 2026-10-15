"""probes/qff_noise_diagnosis.py (15 Oct 2026): decoupling a mode removes every cubic, quartic and Coriolis coupling it has and nothing else;
on styrene's S2 report (when present) the worst constants all couple the 40 cm⁻¹ vinyl torsion, and the script reproduces the report's ν."""
import sys
from pathlib import Path

import numpy as np
import pytest

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
import qff_noise_diagnosis as Q  # noqa: E402

STY = PLAN / "probes" / "results_m1" / "qff_noise_styrene_2026-10-15"


def test_decoupling_zeroes_only_the_chosen_mode():
    rng = np.random.default_rng(0)
    p3, p4, zeta = rng.normal(size=(4, 4, 4)), rng.normal(size=(4, 4)), rng.normal(size=(3, 4, 4))
    q3, q4, qz = Q.decoupled(p3, p4, zeta, [1])
    assert not q3[1].any() and not q3[:, 1].any() and not q3[:, :, 1].any() and not q4[1].any() and not q4[:, 1].any() and not qz[:, 1].any()
    keep = [0, 2, 3]
    assert np.array_equal(q3[np.ix_(keep, keep, keep)], p3[np.ix_(keep, keep, keep)]) and np.array_equal(q4[np.ix_(keep, keep)], p4[np.ix_(keep, keep)])
    assert p3[1].any()                                                     # the inputs are not modified


@pytest.mark.skipif(not (STY / "qff_report.npz").exists(), reason="styrene's report not here")
def test_styrene_noise_sits_on_the_vinyl_torsion():
    d = Q.diagnose(str(STY))                                               # raises if the report's ν is not reproduced
    assert all(x["j"] == 0 or x["i"] == 0 for x in d["worst"]) and d["lowest_modes"][0] == pytest.approx(39.85, abs=0.01)
    assert d["worst"][0]["disagreement"] == pytest.approx(10.65, abs=0.01)
    assert d["dnu_routes_window_max"] == pytest.approx(1.153, abs=1e-3) and d["decoupling"]["window_max_abs_shift"] == pytest.approx(4.614, abs=1e-3)
