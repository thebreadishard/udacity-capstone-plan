"""probes/cc_composite_full_check.py's out-of-plane helpers (TASKS 184): the pin against the inline formula test 3's repair used before
(equal to the bit), and the block replacement's two properties (the target's block in, everything else kept)."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes"))
C = pytest.importorskip("cc_composite_full_check")

N = 4


def _symmetric(rng: np.random.Generator) -> np.ndarray:
    A = rng.normal(size=(3 * N, 3 * N))
    return A + A.T


def _rotation(rng: np.random.Generator) -> np.ndarray:
    Q, _ = np.linalg.qr(rng.normal(size=(3, 3)))
    return Q * np.sign(np.linalg.det(Q))


def test_the_repair_formula_is_unchanged_to_the_bit():
    rng = np.random.default_rng(0)
    H, step, V = _symmetric(rng), _symmetric(rng), _rotation(rng)
    T = np.kron(np.eye(N), V)                                   # the repair's inline formula before 5 Nov 2026
    H_r = T.T @ H @ T
    zi = np.arange(2, 3 * N, 3)
    inline = np.zeros_like(H_r)
    inline[np.ix_(zi, zi)] = step[np.ix_(zi, zi)]
    assert np.array_equal(C.oop_part(step), inline)
    assert np.array_equal(C.oop_step_added(H, V, step), T @ (H_r + inline) @ T.T)


def test_the_replaced_block_carries_the_target_and_keeps_the_rest():
    rng = np.random.default_rng(1)
    H, block, V = _symmetric(rng), _symmetric(rng), _rotation(rng)
    T = C.plane_rotation(V, N)
    out_r = T.T @ C.oop_block_replaced(H, V, block) @ T
    H_r = T.T @ H @ T
    zi, ip = C.oop_indices(N)
    assert np.allclose(out_r[np.ix_(zi, zi)], block[np.ix_(zi, zi)], atol=1e-12)
    assert np.allclose(out_r[np.ix_(ip, ip)], H_r[np.ix_(ip, ip)], atol=1e-12)
    assert np.allclose(out_r[np.ix_(zi, ip)], H_r[np.ix_(zi, ip)], atol=1e-12)
    assert np.allclose(C.oop_block_replaced(H, V, H_r), H, atol=1e-12)     # its own block back: nothing changes


def test_the_indices_split_every_coordinate_once():
    zi, ip = C.oop_indices(N)
    assert sorted([*zi, *ip]) == list(range(3 * N)) and all(k % 3 == 2 for k in zi)
