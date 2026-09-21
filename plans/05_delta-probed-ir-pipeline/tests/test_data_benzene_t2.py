"""Benzene T2, the pre-registered set: 61 analytic pyscf B3LYP/6-31G* Hessians at the pyVPT2 geometries, step 0.05
(21 September 2026). The package must reproduce the probe's arrays bit-for-bit within round-off, and the pre-registered
bounds must hold: route disagreement median < 1, maximum < 1 after the degenerate-subspace alignment."""

import numpy as np
import pytest

from dpir.qff import coriolis_zeta, load_results, qff_from_records, rotational_constants, symmetry_average, vpt2

pytestmark = pytest.mark.data

EXPERIMENT = {"ring breathing": 992.0, "CH bend": 1310.0, "ring": 849.0}  # Shimanouchi, for orientation only


@pytest.fixture(scope="module")
def t2(benzene_t2_dir_module):
    recs = load_results(str(benzene_t2_dir_module))
    assert len(recs) == 61
    return qff_from_records(recs, 0.05)


@pytest.fixture(scope="module")
def benzene_t2_dir_module():
    from conftest import BENZENE_T2_DIR, _need

    return _need(BENZENE_T2_DIR)


def test_reproduces_the_probe_arrays(t2, benzene_t2_npz):
    qff, harm, ref, info = t2
    np.testing.assert_allclose(qff.omega_cm, benzene_t2_npz["omega_cm"], rtol=1e-10)
    np.testing.assert_allclose(qff.phi3, benzene_t2_npz["phi_ijk"], rtol=1e-8, atol=1e-8)
    np.testing.assert_allclose(qff.phi4, benzene_t2_npz["phi_iijj"], rtol=1e-8, atol=1e-8)
    np.testing.assert_allclose(qff.route_a, benzene_t2_npz["phi_iijj_route_a"], rtol=1e-8, atol=1e-8)
    np.testing.assert_allclose(qff.route_b, benzene_t2_npz["phi_iijj_route_b"], rtol=1e-8, atol=1e-8)
    phi4s = symmetry_average(qff.phi4, qff.pairs)
    np.testing.assert_allclose(phi4s, benzene_t2_npz["phi_iijj_sym"], rtol=1e-8, atol=1e-8)
    B = rotational_constants(ref.geom, ref.symbols)
    zeta = coriolis_zeta(harm.q, ref.symbols)
    nu_raw, chi_raw, _ = vpt2(qff.omega_cm, qff.phi3, qff.phi4, B, zeta)
    nu_sym, chi_sym, _ = vpt2(qff.omega_cm, qff.phi3, phi4s, B, zeta)
    np.testing.assert_allclose(nu_raw, benzene_t2_npz["nu_raw"], atol=1e-6)
    np.testing.assert_allclose(nu_sym, benzene_t2_npz["nu_sym"], atol=1e-6)


def test_preregistered_bounds_hold(t2):
    qff, harm, ref, info = t2
    assert info["subspaces_aligned"] >= 1, "benzene has degenerate pairs; the alignment must have acted"
    assert info["assignment_residual_max"] < 1e-2
    d = qff.route_disagreement
    assert np.median(d) < 1.0
    assert np.percentile(d, 90) < 1.0
    assert d.max() < 1.0
    # degenerate partners (a, b) carry equal φ_aa,jj for every totally symmetric j, within the route noise
    in_pair = {i for p in qff.pairs for i in p}
    ts = [i for i in range(len(qff.omega_cm)) if abs(qff.phi3[i, i, i]) > 5 and i not in in_pair]
    assert len(ts) >= 2, "benzene has two a1g modes"
    for a, b in qff.pairs:
        for j in ts:
            assert abs(qff.phi4[a, j] - qff.phi4[b, j]) < 2.0, (a, b, j)


def test_three_bands_within_the_cheap_functional_error(t2):
    """850.6 / 1004.4 / 1324.1 cm⁻¹ on 21 September 2026; what remains against experiment is the B3LYP/6-31G* error."""
    qff, harm, ref, info = t2
    phi4s = symmetry_average(qff.phi4, qff.pairs)
    nu_sym, _, _ = vpt2(qff.omega_cm, qff.phi3, phi4s, rotational_constants(ref.geom, ref.symbols), coriolis_zeta(harm.q, ref.symbols))
    for target in (850.6, 1004.4, 1324.1):
        assert np.abs(nu_sym - target).min() < 0.05, f"band near {target} moved"
    for name, exp in EXPERIMENT.items():
        assert np.abs(nu_sym - exp).min() < 20.0, f"{name} further than 20 cm⁻¹ from experiment"
