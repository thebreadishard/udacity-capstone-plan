"""Rotational constants and Coriolis constants against known values."""

import numpy as np
import pytest

from dpir.qff import BOHR_ANGSTROM, coriolis_zeta, rotational_constants


def test_h2_equilibrium_rotational_constant():
    """B_e(H₂) = 60.853 cm⁻¹ (Huber & Herzberg 1979) at r_e = 0.74144 Å; the axis along the bond has zero inertia."""
    r = 0.74144 / BOHR_ANGSTROM
    with np.errstate(divide="ignore"):
        B = rotational_constants(np.array([0, 0, 0, 0, 0, r], float), ["H", "H"])
    finite = np.sort(B[np.isfinite(B)])
    assert len(finite) == 2
    np.testing.assert_allclose(finite, [60.853, 60.853], atol=0.01)


@pytest.mark.data
def test_water_rotational_constants_match_pyvpt2(water_pyvpt2):
    """Same geometry and masses as pyVPT2 0.1.2 used on 16 September 2026 → same A, B, C."""
    geom = np.array(water_pyvpt2["coords_bohr"], float).ravel()
    symbols = list(water_pyvpt2["symbols"])
    expected = np.array(water_pyvpt2["rotational_constants"], float)
    got = np.sort(rotational_constants(geom, symbols))[::-1]
    np.testing.assert_allclose(got, np.sort(expected)[::-1], atol=2e-3)


def test_coriolis_zeta_is_antisymmetric_and_bounded(model_molecule):
    from test_harmonic import vibrational_basis

    symbols, geom, m, rng = model_molecule
    q = vibrational_basis(geom, m, rng)
    z = coriolis_zeta(q, symbols)
    assert z.shape == (3, 6, 6)
    np.testing.assert_allclose(z, -z.transpose(0, 2, 1), atol=1e-14)
    assert np.abs(z).max() <= 1.0 + 1e-12
