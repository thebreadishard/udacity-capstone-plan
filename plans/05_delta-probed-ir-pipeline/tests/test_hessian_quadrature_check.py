"""probes/hessian_quadrature_check.py (TASKS 201): the translation residual is zero for a translation-invariant Hessian and gives the known
curvature for a known error; the summary's percentiles, counts and per-family noise on synthetic rows, an empty family included."""
import math
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes"))
HQC = pytest.importorskip("hessian_quadrature_check")
QC = pytest.importorskip("qc_common")


def _spring_hessian(coords: np.ndarray, k: float = 0.3) -> np.ndarray:
    """A Hessian of pair springs between all atoms: invariant under translation by construction."""
    n = len(coords)
    H = np.zeros((3 * n, 3 * n))
    for i in range(n):
        for j in range(i + 1, n):
            e = coords[j] - coords[i]
            block = k * np.outer(e, e) / (e @ e)
            for a, b, s in ((i, i, 1), (j, j, 1), (i, j, -1), (j, i, -1)):
                H[3 * a:3 * a + 3, 3 * b:3 * b + 3] += s * block
    return H


def test_a_translation_invariant_hessian_has_no_residual_and_a_known_error_is_read_back():
    coords = np.array([[0.0, 0.0, 0.0], [1.4, 0.2, 0.0], [-0.3, 1.1, 0.4], [0.5, -0.9, 1.2]])
    masses = np.array([12.0, 1.008, 15.995, 14.003])
    H = _spring_hessian(coords)
    worst, freqs = HQC.translation_residual(H, masses)
    assert worst < 1e-12 and max(abs(f) for f in freqs) < 1e-3
    eps = 1e-5
    worst, freqs = HQC.translation_residual(H + eps * np.eye(12), masses)
    expected = math.sqrt(eps * len(masses) / (masses.sum() * QC.AMU2AU)) * QC.HARTREE2CM
    assert np.isclose(worst, eps) and np.allclose(freqs, expected)
    assert HQC.translation_residual(H - eps * np.eye(12), masses)[1][0] < 0


def test_the_summary_counts_percentiles_and_family_noise():
    rows = [{"w_t_b3lyp": w, "w_t_wb97x": 2 * w, "w_t_dH": -w, "n_unresolved": n} for w, n in ((1.0, 0), (3.0, 2), (-10.0, 1))]
    noise = {"CH-stretch": [0.1, 0.1], "CH-oop": [], "ring-ip": [0.6, 1.2, 4.0], "other": [2.0]}
    s = HQC.summary(rows, noise)
    assert s["w_t_b3lyp_cm"] == {"median": 3.0, "p90": pytest.approx(8.6), "max": 10.0}
    assert s["unresolved_modes"] == 3 and s["molecules_with_unresolved"] == 2
    ring = s["noise_by_family_cm"]["ring-ip"]
    assert ring["modes"] == 3 and ring["above_0.5"] == 3 and ring["above_1"] == 2 and ring["above_3"] == 1
    assert math.isnan(s["noise_by_family_cm"]["CH-oop"]["rms"])
    assert "| CH-oop | 0 | nan |" in HQC.markdown({**s, "molecules": 3})
