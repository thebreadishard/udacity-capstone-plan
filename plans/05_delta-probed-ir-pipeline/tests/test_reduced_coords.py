"""Known-answer and negative-control tests for probes/reduced_coords.py (25 September 2026): a displacement of q = 1 along a mode must cost ω/2 on
the harmonic surface; the bug of that day (dividing by ω instead of sqrt(ω)) must be rejected by the check."""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes"))
from reduced_coords import harmonic_check, omega_from_eigenvalue, reduced_displacement  # noqa: E402

AMU2AU = 1822.888486209


def _diatomic(k_au=0.5, m1=12.0, m2=1.008, r=2.0):
    """Two atoms on the x axis with a harmonic bond (force constant k in E_h/bohr²): the Cartesian Hessian, masses and a mass-weighted eigen-decomposition."""
    H = np.zeros((6, 6))
    H[0, 0] = H[3, 3] = k_au
    H[0, 3] = H[3, 0] = -k_au
    m = np.repeat(np.array([m1, m2]) * AMU2AU, 3)
    Minv = 1 / np.sqrt(m)
    w, L = np.linalg.eigh(H * np.outer(Minv, Minv))
    k = int(np.argmax(w))  # the one vibration
    coords0 = np.array([[0.0, 0, 0], [r, 0, 0]])
    return H, Minv, w[k], L[:, k], coords0


def test_q1_costs_half_omega():
    H, Minv, wk, Lk, x0 = _diatomic()
    omega = omega_from_eigenvalue(wk)
    mu = (12.0 * 1.008 / (12.0 + 1.008)) * AMU2AU
    assert omega == pytest.approx(np.sqrt(0.5 / mu), rel=1e-10)  # ω = sqrt(k/μ)
    for q in (0.25, 0.5, 1.0, -1.0):
        x = reduced_displacement(x0, Lk, omega, Minv, q)
        d = (x - x0).reshape(-1)
        e = 0.5 * d @ H @ d
        assert e == pytest.approx(0.5 * omega * q * q, rel=1e-9)
        assert harmonic_check(H, x0, x, omega, q) == pytest.approx(1.0, abs=1e-9)


def test_dividing_by_omega_is_rejected():
    H, Minv, wk, Lk, x0 = _diatomic()
    omega = omega_from_eigenvalue(wk)
    x_bug = x0 + ((Lk * 1.0 / omega) * Minv).reshape(-1, 3)  # the 25 Sep mistake: ÷ω instead of ÷sqrt(ω)
    with pytest.raises(ValueError, match="divided by"):
        harmonic_check(H, x0, x_bug, omega, 1.0)


def test_displacement_size_for_a_stretch_is_tenths_of_a_bohr():
    """A C–H-like stretch displaced by q = 1 moves the light atom by tenths of a bohr; the ÷ω mistake moves it by bohrs."""
    H, Minv, wk, Lk, x0 = _diatomic(k_au=0.2)
    omega = omega_from_eigenvalue(wk)
    x = reduced_displacement(x0, Lk, omega, Minv, 1.0)
    x_bug = x0 + ((Lk * 1.0 / omega) * Minv).reshape(-1, 3)
    assert np.linalg.norm(x - x0, axis=1).max() < 0.3
    assert np.linalg.norm(x_bug - x0, axis=1).max() > 5 * np.linalg.norm(x - x0, axis=1).max()
