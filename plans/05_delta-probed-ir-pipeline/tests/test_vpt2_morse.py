"""VPT2 on a Morse oscillator, for which second-order perturbation theory is exact: χ = −ω²/(4D), ν = ω − ω²/(2D)."""

import numpy as np

from dpir.qff import HARTREE_CM, vpt2


def morse_reduced_constants(D, a, mu):
    """ω and the reduced-coordinate derivatives of V = D(1 − e^{−ax})²: φ₃ = V‴/(μω)^{3/2}, φ₄ = V⁗/(μω)² (atomic units)."""
    omega = a * np.sqrt(2 * D / mu)
    phi3 = -6 * D * a**3 / (mu * omega) ** 1.5
    phi4 = 14 * D * a**4 / (mu * omega) ** 2
    return omega, phi3, phi4


def test_morse_anharmonicity_is_exact():
    D, a, mu = 0.17, 0.988, 1785.7  # HCl-like: E_h, bohr⁻¹, m_e
    omega, phi3, phi4 = morse_reduced_constants(D, a, mu)
    w = np.array([omega * HARTREE_CM])
    p3 = np.full((1, 1, 1), phi3 * HARTREE_CM)
    p4 = np.full((1, 1), phi4 * HARTREE_CM)
    nu, chi, fermi = vpt2(w, p3, p4, np.zeros(3), np.zeros((3, 1, 1)))
    D_cm = D * HARTREE_CM
    assert fermi == []
    np.testing.assert_allclose(chi[0, 0], -w[0] ** 2 / (4 * D_cm), rtol=1e-10)
    np.testing.assert_allclose(nu[0], w[0] - w[0] ** 2 / (2 * D_cm), rtol=1e-10)
    assert 2500 < w[0] < 3500 and nu[0] < w[0]


def test_two_uncoupled_morse_oscillators_do_not_talk():
    """Zero cubic coupling and zero quartic coupling: each mode keeps its own Morse result."""
    ws, p3s, p4s = [], [], []
    for D, a, mu in ((0.17, 0.988, 1785.7), (0.20, 1.20, 1000.0)):
        omega, phi3, phi4 = morse_reduced_constants(D, a, mu)
        ws.append(omega * HARTREE_CM)
        p3s.append(phi3 * HARTREE_CM)
        p4s.append(phi4 * HARTREE_CM)
    w = np.array(ws)
    p3 = np.zeros((2, 2, 2))
    p4 = np.zeros((2, 2))
    for i in range(2):
        p3[i, i, i] = p3s[i]
        p4[i, i] = p4s[i]
    nu, chi, _ = vpt2(w, p3, p4, np.zeros(3), np.zeros((3, 2, 2)))
    for i, (D, _a, _mu) in enumerate(((0.17, 0.988, 1785.7), (0.20, 1.20, 1000.0))):
        np.testing.assert_allclose(nu[i], w[i] - w[i] ** 2 / (2 * D * HARTREE_CM), rtol=1e-10)
    assert chi[0, 1] == 0.0 and chi[1, 0] == 0.0
