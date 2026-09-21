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


def _pair_sorted(v, pairs):
    """1-D per-mode array with the two values of every degenerate pair put in ascending order (the order of the two
    members inside a pair is a convention, not a physical statement)."""
    v = np.array(v, float).copy()
    for a, b in pairs:
        v[[a, b]] = np.sort(v[[a, b]])
    return v


def _magnitudes(t):
    return np.sort(np.abs(np.asarray(t)).ravel())


def test_reproduces_the_probe_arrays(t2, benzene_t2_npz):
    """The probe's arrays were made on Windows numpy, whose eigh chose other mode signs and another order inside two
    degenerate pairs than Linux numpy does (first CI run, 21 Sep 2026). The physics is convention-free, so the pin is:
    frequencies exactly, every fundamental to 1e-6 (pair members may swap), and the constants as multisets of magnitudes."""
    qff, harm, ref, info = t2
    np.testing.assert_allclose(qff.omega_cm, benzene_t2_npz["omega_cm"], rtol=1e-10)
    for ours, key in ((qff.phi3, "phi_ijk"), (qff.phi4, "phi_iijj"), (qff.route_a, "phi_iijj_route_a"), (qff.route_b, "phi_iijj_route_b")):
        np.testing.assert_allclose(_magnitudes(ours), _magnitudes(benzene_t2_npz[key]), rtol=1e-8, atol=1e-8, err_msg=key)
    probe_diff = np.abs(benzene_t2_npz["phi_iijj_route_a"] - benzene_t2_npz["phi_iijj_route_b"])[np.triu_indices(30, 1)]
    np.testing.assert_allclose(np.sort(qff.route_disagreement), np.sort(probe_diff), rtol=1e-8, atol=1e-8)
    phi4s = symmetry_average(qff.phi4, qff.pairs)
    np.testing.assert_allclose(_magnitudes(phi4s), _magnitudes(benzene_t2_npz["phi_iijj_sym"]), rtol=1e-8, atol=1e-8)
    B = rotational_constants(ref.geom, ref.symbols)
    zeta = coriolis_zeta(harm.q, ref.symbols)
    nu_raw, chi_raw, _ = vpt2(qff.omega_cm, qff.phi3, qff.phi4, B, zeta)
    nu_sym, chi_sym, _ = vpt2(qff.omega_cm, qff.phi3, phi4s, B, zeta)
    # Fundamentals: exact outside the pairs. Inside a pair the two harmonic values differ by ≤ 0.01 cm⁻¹ (numerical
    # splitting of an exact degeneracy) and which of them a column carries is a convention; swapping moves the two ν by
    # ≈ 0.03 cm⁻¹ against each other while their mean stays. So: mean of the pair to 0.02, each member to 0.1.
    in_pair = np.zeros(30, bool)
    for a, b in qff.pairs:
        in_pair[[a, b]] = True
    for ours, key in ((nu_raw, "nu_raw"), (nu_sym, "nu_sym")):
        probe = benzene_t2_npz[key]
        np.testing.assert_allclose(ours[~in_pair], probe[~in_pair], atol=1e-6, err_msg=key)
        for a, b in qff.pairs:
            assert abs(ours[[a, b]].mean() - probe[[a, b]].mean()) < 0.02, (key, a, b)
            np.testing.assert_allclose(_pair_sorted(ours, qff.pairs)[[a, b]], _pair_sorted(probe, qff.pairs)[[a, b]], atol=0.1, err_msg=key)
    np.testing.assert_allclose(np.diag(chi_sym)[~in_pair], np.diag(benzene_t2_npz["chi_sym"])[~in_pair], atol=1e-6)


def test_conventions_are_fixed(t2):
    """Largest component of every mode positive; inside every aligned pair the members are ordered by the name of their
    +displacement file. Both are set by the package, not by the linear-algebra backend, so the report is the same on
    every machine (checked Windows vs Linux numpy, 21 Sep 2026)."""
    qff, harm, ref, info = t2
    for j in range(harm.q.shape[1]):
        assert harm.q[np.argmax(np.abs(harm.q[:, j])), j] > 0, j
    assert info["subspaces_aligned"] == 10


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
