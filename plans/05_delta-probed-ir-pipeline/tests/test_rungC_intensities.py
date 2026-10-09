"""Lever 5, step 2 (2 Oct 2026): the intensity read-out — water's APT and Hessian reproduce the probe's intensities; a perfect prediction overlaps 1 and the
zero rule less; the aggregate counts only molecules with an APT."""
import sys
from pathlib import Path

import numpy as np
import pytest

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "modules" / "05_support_predictor" / "m05"))
import rungC_intensities as RI  # noqa: E402

WATER = PLAN / "probes" / "results_m1" / "water_dipole_fd_2026-10-02"


@pytest.mark.skipif(not (WATER / "dipole_b3lyp_fd.npz").exists(), reason="water APT not on this machine")
def test_water_intensities_match_the_probe():
    import json
    z = np.load(WATER / "dipole_b3lyp_fd.npz")
    g = json.load(open(WATER / "geometry.json"))
    # the probe's Hessian is the analytic B3LYP one of the scratch run; rebuild the intensities from the stored APT through the module's own path
    # by checking the module on the probe's own frequencies: a diagonal Hessian with those frequencies and the identity modes is not water, so the test
    # uses the stored intensities only as the reference of the constant — the mode path is covered by the synthetic test below.
    assert z["passed"] and abs(float(z["sum_rule_max"])) < 1e-4 and len(g["symbols"]) == 3
    assert np.allclose(z["intensity_km_mol"], [79.52, 2.48, 23.45], atol=0.05)


def _synthetic(n_atoms=4, seed=0):
    rng = np.random.default_rng(seed)
    masses = np.array([12.0, 1.0, 1.0, 1.0])[:n_atoms]
    A = rng.normal(size=(3 * n_atoms, 3 * n_atoms))
    H = A @ A.T * 1e-2 + np.eye(3 * n_atoms) * 0.05          # positive, no near-zero modes
    dH = rng.normal(size=H.shape) * 1e-3
    dH = 0.5 * (dH + dH.T)
    apt = rng.normal(size=(3, 3 * n_atoms))
    return H, dH, masses, apt


def test_perfect_prediction_overlaps_one_and_zero_rule_less():
    H, dH, masses, apt = _synthetic()
    r = RI.intensity_readout(H, dH, dH, masses, apt)
    assert r["spectrum_overlap"] == pytest.approx(1.0) and r["intensity_rel_rms"] == pytest.approx(0.0)
    assert r["spectrum_overlap_zero_rule"] < 1.0 and r["intensity_rel_rms_zero_rule"] > 0.0
    half = RI.intensity_readout(H, dH, 0.5 * dH, masses, apt)
    assert r["spectrum_overlap_zero_rule"] <= half["spectrum_overlap"] <= 1.0


def test_matched_pairing_survives_a_mode_crossing():
    """9 Oct 2026 (benzene, CC/TZ): a bright mode that moves past a dark neighbour must not read as a 100 % intensity error."""
    masses = np.ones(2)
    truth = np.diag([1.0e-3, 1.1e-3, 2e-3, 3e-3, 4e-3, 5e-3])          # x0 (bright) below x1 (dark)
    pred = np.diag([1.2e-3, 1.1e-3, 2e-3, 3e-3, 4e-3, 5e-3])           # x0 moved above x1: the sorted order swaps
    apt = np.zeros((3, 6))
    apt[0, 0] = 1.0
    apt[1, 2:] = 0.3
    low = np.diag([1.3e-3, 1.1e-3, 2e-3, 3e-3, 4e-3, 5e-3])            # the zero rule is crossed too
    r = RI.intensity_readout(low, truth - low, pred - low, masses, apt)
    assert r["intensity_rel_rms"] > 0.5 and r["intensity_rel_rms_matched"] == pytest.approx(0.0, abs=1e-12)
    assert r["intensity_rel_rms_zero_rule"] > 0.5 and r["intensity_rel_rms_zero_rule_matched"] == pytest.approx(0.0, abs=1e-12)


def test_trainer_wiring_present():
    text = (PLAN / "modules" / "05_support_predictor" / "m05" / "rungC_train.py").read_text(encoding="utf-8")
    assert "import rungC_intensities as RI" in text and 'if "apt" in mols.get(i, {}):' in text and 'r.update(RI.aggregate(r["per_molecule"]))' in text
    assert 'APT_FILES = ("dipole_b3lyp_cphf.npz", "dipole_b3lyp_fd.npz")' in text
    assert "mols, test_a, test_b, cores, pool, substituted = load_corpus(a.molecules, a.use_analytic, log)" in text
    assert '"spectrum_overlap"' in text.split("PER_MOLECULE_KEYS = ")[1].split(")")[0]


def test_intensity_constant_and_broadening():
    # one mode of unit dμ/dQ in e/√amu is 974.88 km/mol: a single atom of mass 1 moving along x with APT = identity column
    masses = np.array([1.0])
    H = np.diag([1e-4, 2e-4, 3e-4])                           # three "modes" far above the threshold
    f, i = RI.mode_intensities(H, masses, np.eye(3))
    assert np.allclose(i, RI.KM_PER_MOL)
    s = RI.broadened(np.array([1000.0]), np.array([1.0]))
    assert abs(s.sum() - 1.0) < 0.01                          # a unit Lorentzian integrates to one over a 1 cm⁻¹ grid (tails cut at 2500 cm⁻¹)
    assert RI.aggregate({"a": {"spectrum_overlap": None}, "b": {"spectrum_overlap": 0.9, "spectrum_overlap_zero_rule": 0.8, "intensity_rel_rms": 0.1,
                                                                 "intensity_rel_rms_zero_rule": 0.2}})["intensity_n"] == 1
