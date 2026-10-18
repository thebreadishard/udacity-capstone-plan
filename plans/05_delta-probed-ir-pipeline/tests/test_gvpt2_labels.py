"""probes/gvpt2_labels.py (S2 amendment 2): overtone and combination energies from χ, the polyad-bridge count, GVPT2 = DVPT2 without
resonances (a), and — where pyVPT2 is installed — the trace of a resonant dyad conserved (b). Validation (c), H₂CO end to end against
pyVPT2, is probes/gvpt2_h2co_check.py."""
import importlib.util
import sys
from pathlib import Path

import numpy as np
import pytest

PLAN = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PLAN / "probes"))
sys.path.insert(0, str(PLAN / "src"))
import gvpt2_labels as G  # noqa: E402

HAS_PYVPT2 = importlib.util.find_spec("pyvpt2") is not None


def test_overtones_and_bands_follow_the_chi_expressions():
    w = np.array([500.0, 900.0, 1400.0])
    chi = np.array([[-1.0, -2.0, -3.0], [-2.0, -4.0, -5.0], [-3.0, -5.0, -6.0]])
    overtone, band = G.overtones_and_bands(w, chi)
    assert overtone[0] == pytest.approx(2 * 500 + 6 * -1 + (-2 - 3))
    assert band[0, 1] == pytest.approx(500 + 900 + 2 * -1 + 2 * -4 + 2 * -2 + 0.5 * (-3 + -5))
    assert band[1, 0] == band[0, 1]
    o0, b0 = G.overtones_and_bands(w, np.zeros((3, 3)))
    assert np.allclose(o0, 2 * w) and b0[0, 2] == pytest.approx(1900.0)


def test_an_interaction_that_joins_two_polyads_is_counted():
    assert G.polyad_bridges([(2, (0, 0)), (5, (3, 4))]) == 0
    assert G.polyad_bridges([(2, (0, 0)), (5, (3, 4)), (5, (0, 0))]) == 1


def _force_field(n=4, cubic=0.0, seed=0):
    rng = np.random.default_rng(seed)
    w = np.array([400.0, 820.0, 1300.0, 1650.0])[:n]
    p3 = np.zeros((n, n, n))
    if cubic:
        for i, j, k in ((0, 0, 1), (0, 1, 0), (1, 0, 0)):     # 2ω_0 ≈ ω_1: a Fermi type-1 pair
            p3[i, j, k] = cubic
    p4 = rng.normal(0, 2, (n, n))
    return w, p3, (p4 + p4.T) / 2, np.array([0.2, 0.1, 0.05]), np.zeros((3, n, n))


def test_without_resonances_gvpt2_equals_dvpt2():
    w, p3, p4, B, zeta = _force_field()
    r = G.gvpt2(w, p3, p4, B, zeta)
    assert r["n_resonances"] == 0 and r["moved"] == [] and np.array_equal(r["nu_gvpt2"], r["nu_dvpt2"])


@pytest.mark.skipif(not HAS_PYVPT2, reason="pyVPT2 is installed in the WSL env 'vpt2' only")
def test_a_resonant_dyad_keeps_its_trace():
    w, p3, p4, B, zeta = _force_field(cubic=60.0)
    r = G.gvpt2(w, p3, p4, B, zeta)
    assert r["moved"] == [1]
    _nu, chi, _f = G.vpt2(w, p3, p4, B, zeta, G.FERMI_WINDOW, G.FERMI_MIN_K)
    overtone, _band = G.overtones_and_bands(w, chi)
    # the dyad (ν_1, 2ν_0) is diagonalised: its eigenvalues keep the sum of its diagonal
    from pyvpt2.fermi_solver import Interaction, State, fermi_solver
    states = fermi_solver([Interaction(left=State(state=(1,), nu=r["nu_dvpt2"][1]), right=State(state=(0, 0), nu=overtone[0]), phi=60.0,
                                       ftype=1)])
    assert states[(1,)] + states[(0, 0)] == pytest.approx(r["nu_dvpt2"][1] + overtone[0])
    assert r["nu_gvpt2"][1] == pytest.approx(states[(1,)])
