"""Water, the first real ijk set: 7 psi4 B3LYP/6-31G* finite-difference Hessians (16 September 2026, step 0.05) with the
pyVPT2 0.1.2 result on the same Hessians next to them. Harmonic frequencies must agree to the print precision; the
fundamentals must agree to within the finite-difference noise of that set."""

import numpy as np
import pytest

from dpir.qff import coriolis_zeta, load_results, qff_from_records, rotational_constants, vpt2

pytestmark = pytest.mark.data


def pyvpt2_vibrational(water_pyvpt2, key):
    """pyVPT2 stores 3N entries (translations/rotations as zeros); keep the vibrational ones."""
    v = np.array(water_pyvpt2[key], float)
    return v[np.array(water_pyvpt2["omega"], float) > 1.0]


def test_water_harmonic_frequencies_match_pyvpt2(water_cache, water_pyvpt2):
    recs = load_results(str(water_cache))
    assert len(recs) == 7
    qff, harm, ref, info = qff_from_records(recs, 0.05)
    assert info["assignment_residual_max"] < 1e-6
    assert info["subspaces_aligned"] == 0
    np.testing.assert_allclose(qff.omega_cm, pyvpt2_vibrational(water_pyvpt2, "omega"), atol=0.01)


def test_water_force_field_and_vpt2_match_pyvpt2(water_cache, water_pyvpt2):
    """Independent implementation on the same Hessians: pyVPT2 0.1.2 (16 Sep 2026) and this package agree on every cubic and
    semi-diagonal quartic constant, every χ_ij (this covers the Coriolis term and the resonance-free denominators) and every
    fundamental to 1e-5 cm⁻¹ (measured 21 Sep 2026: 7e-8, 2e-8, 1.6e-8, 1.4e-7). The two-route disagreement of this
    finite-difference set is 1.5 cm⁻¹; both codes average the routes, so it does not enter here."""
    recs = load_results(str(water_cache))
    qff, harm, ref, info = qff_from_records(recs, 0.05)
    B = rotational_constants(ref.geom, ref.symbols)
    zeta = coriolis_zeta(harm.q, ref.symbols)
    nu, chi, fermi = vpt2(qff.omega_cm, qff.phi3, qff.phi4, B, zeta)
    keep = np.array(water_pyvpt2["omega"], float) > 1.0
    py_phi3 = np.array(water_pyvpt2["phi_ijk"], float)[np.ix_(keep, keep, keep)]
    py_phi4 = np.array(water_pyvpt2["phi_iijj"], float)[np.ix_(keep, keep)]
    py_chi = np.array(water_pyvpt2["chi"], float)[np.ix_(keep, keep)]
    assert fermi == []
    np.testing.assert_allclose(np.abs(qff.phi3), np.abs(py_phi3), atol=1e-5)  # mode signs are a convention
    np.testing.assert_allclose(qff.phi4, py_phi4, atol=1e-5)
    np.testing.assert_allclose(chi, py_chi, atol=1e-5)
    np.testing.assert_allclose(nu, pyvpt2_vibrational(water_pyvpt2, "nu"), atol=1e-5)
    np.testing.assert_allclose(np.sort(B)[::-1], np.sort(np.array(water_pyvpt2["rotational_constants"], float))[::-1], atol=1e-6)
    assert 1.0 < qff.route_disagreement.max() < 2.0, "the FD noise of this set, pinned so that a silent change shows"
    assert np.all(nu < qff.omega_cm), "anharmonic fundamentals of water lie below the harmonic ones"
