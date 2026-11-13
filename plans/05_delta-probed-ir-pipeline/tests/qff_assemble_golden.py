"""The inputs and the record of tests/data/qff_assemble_golden.npz: dpir.qff.assemble_qff's output on fixed synthetic Hessians, pinned
before the full semi-diagonal quartic tensor phi_ijkk was added beside it (13 Nov 2026, TASKS 209 stage 2). Every array it pins must
come back bit for bit from any later version; a new array is an addition, never a change.

    python tests/qff_assemble_golden.py        writes the golden file; refuses when it exists
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

PLAN = Path(__file__).resolve().parents[1]
GOLDEN = PLAN / "tests" / "data" / "qff_assemble_golden.npz"
DISP = 0.05
N_MODES = 5
PAIRS = [(1, 2)]


def inputs() -> tuple[np.ndarray, np.ndarray, dict[int, np.ndarray], dict[int, np.ndarray]]:
    """ω and the reference and displaced reduced-coordinate Hessians: a symmetric random perturbation per displaced mode, so every
    route of every constant is exercised and the three cubic routes disagree as they do on real data."""
    rng = np.random.default_rng(20261113)
    omega = np.array([420.0, 780.0, 780.0, 1310.0, 2950.0])
    h0 = np.diag(omega) / 219474.6313632
    h0 = h0 + 1e-5 * _symmetric(rng, N_MODES)
    plus = {i: h0 + DISP * 1e-3 * _symmetric(rng, N_MODES) + DISP**2 * 1e-2 * _symmetric(rng, N_MODES) for i in range(N_MODES)}
    minus = {i: h0 - DISP * 1e-3 * _symmetric(rng, N_MODES) + DISP**2 * 1e-2 * _symmetric(rng, N_MODES) for i in range(N_MODES)}
    return omega, h0, plus, minus


def _symmetric(rng: np.random.Generator, n: int) -> np.ndarray:
    a = rng.normal(0.0, 1.0, (n, n))
    return (a + a.T) / 2.0


def pinned(qff) -> dict[str, np.ndarray]:
    """The arrays this golden file holds: everything assemble_qff produced before the tensor was added."""
    return {"omega_cm": qff.omega_cm, "phi3": qff.phi3, "cubic_spread": qff.cubic_spread, "phi4": qff.phi4,
            "route_a": qff.route_a, "route_b": qff.route_b, "pairs": np.array(qff.pairs, dtype=int).reshape(-1, 2)}


def main() -> int:
    if GOLDEN.exists():
        print(f"{GOLDEN} is already there; delete it deliberately to re-pin")
        return 1
    sys.path.insert(0, str(PLAN / "src"))
    from dpir.qff import assemble_qff

    omega, h0, plus, minus = inputs()
    GOLDEN.parent.mkdir(parents=True, exist_ok=True)
    np.savez(GOLDEN, **pinned(assemble_qff(omega, h0, plus, minus, DISP, PAIRS)))
    print(f"wrote {GOLDEN}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
