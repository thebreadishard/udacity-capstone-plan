"""probes/e8_symmetry.py degenerate_pairs (TASKS 53, 12 Nov 2026): degeneracy comes from the point group, not from a frequency gap.
Benzene (D6h) has ten pairs, also when noise splits them by more than the old 0.5 cm-1 gap; ideal tetracene (D2h) has none, however close
two of its modes lie; a mode set that does not carry the group's pairs is refused."""
import sys
from pathlib import Path

import numpy as np
import pytest

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
sys.path.insert(0, str(PLAN / "src"))
from e8_symmetry import degenerate_pairs, point_group_ops, rep_matrices, symmetrize  # noqa: E402
from qff_symmetry_count import BOHR, tetracene_ideal  # noqa: E402

from dpir.qff import harmonic  # noqa: E402


def _benzene():
    """Ideal D6h benzene (C-C 1.39 Å, C-H 1.09 Å), bohr; built here because the corpus geometry is not in git."""
    ang = np.arange(6) * np.pi / 3
    ring = np.stack([np.cos(ang), np.sin(ang), np.zeros(6)], 1)
    return ["C"] * 6 + ["H"] * 6, np.vstack([1.39 * ring, 2.48 * ring]) / BOHR


def _symmetric_hessian(symbols, x, seed=1, noise=0.0):
    """A positive definite Cartesian Hessian with the molecule's symmetry, plus optional symmetric noise that breaks it."""
    x = symmetrize(symbols, x)
    D = rep_matrices(point_group_ops(symbols, x, tol=1e-6), len(symbols))
    rng = np.random.default_rng(seed)
    A = rng.standard_normal((3 * len(symbols), 3 * len(symbols)))
    H0 = A @ A.T / A.shape[0] * 0.5
    H = sum(d @ H0 @ d.T for d in D) / len(D)
    if noise:
        E = rng.standard_normal(H.shape)
        H = H + noise * np.abs(H).max() * (E + E.T) / 2
    return x, H


def test_benzene_has_ten_pairs():
    symbols, x = _benzene()
    x, H = _symmetric_hessian(symbols, x)
    h = harmonic(H, symbols, x)
    pairs = degenerate_pairs(symbols, x, h.q)
    assert len(pairs) == 10
    w = h.omega_cm
    assert max(abs(w[b] - w[a]) for a, b in pairs) < 1e-3


def test_benzene_pairs_split_by_noise_are_still_pairs():
    symbols, x = _benzene()
    x, H = _symmetric_hessian(symbols, x, noise=2e-4)
    h = harmonic(H, symbols, x)
    pairs = degenerate_pairs(symbols, x, h.q)
    w = h.omega_cm
    assert len(pairs) == 10
    assert max(abs(w[b] - w[a]) for a, b in pairs) > 0.5      # the old gap rule would have lost these


def test_tetracene_has_no_pair_even_with_near_degenerate_modes():
    symbols, x = tetracene_ideal()
    x, H = _symmetric_hessian(symbols, x)
    h = harmonic(H, symbols, x)
    assert degenerate_pairs(symbols, x, h.q) == []
    gaps = np.diff(np.sort(h.omega_cm))
    assert gaps.min() < 5.0                                   # neighbours a gap rule could pair; the group pairs none


def test_modes_that_do_not_carry_the_pairs_are_refused():
    symbols, x = _benzene()
    x, H = _symmetric_hessian(symbols, x)
    q = harmonic(H, symbols, x).q
    rng = np.random.default_rng(3)
    mix, _ = np.linalg.qr(rng.standard_normal((q.shape[1], q.shape[1])))
    with pytest.raises(ValueError, match=r"more than a plane|not carried|name a partner"):
        degenerate_pairs(symbols, x, q @ mix)
