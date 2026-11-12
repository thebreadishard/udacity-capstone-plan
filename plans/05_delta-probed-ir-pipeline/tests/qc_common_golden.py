"""The inputs and the record of tests/data/qc_common_project_tr_golden.npz: probes/qc_common.py project_tr's output on three molecules and
random symmetric Hessians, pinned before its rigid-body basis became the shared `rigid_basis` (13 Nov 2026, TASKS 201 step 3).

    python tests/qc_common_golden.py        writes the golden file; refuses when it exists
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

PLAN = Path(__file__).resolve().parents[1]
GOLDEN = PLAN / "tests" / "data" / "qc_common_project_tr_golden.npz"


def cases() -> dict[str, tuple[np.ndarray, np.ndarray, np.ndarray]]:
    """(masses amu, coordinates bohr, Cartesian Hessian) per case: water, a planar six-ring and a random non-planar seven-atom molecule."""
    rng = np.random.default_rng(2026)
    out = {}
    geometries = {
        "water": (np.array([15.995, 1.008, 1.008]), np.array([[0.0, 0.0, 0.0], [0.0, -1.43, 1.11], [0.0, 1.43, 1.11]])),
        "ring": (np.array([12.0] * 6), np.stack([2.6 * np.cos(np.arange(6) * np.pi / 3), 2.6 * np.sin(np.arange(6) * np.pi / 3),
                                                  np.zeros(6)], 1)),
        "random": (rng.uniform(1.0, 16.0, 7), rng.normal(scale=2.0, size=(7, 3))),
    }
    for name, (m, x) in geometries.items():
        A = rng.normal(size=(3 * len(m), 3 * len(m)))
        out[name] = (m, x, 0.05 * (A + A.T))
    return out


def main() -> int:
    if GOLDEN.exists():
        raise SystemExit(f"{GOLDEN} exists: it pins project_tr before the refactor; re-pinning with the new code proves nothing")
    sys.path.insert(0, str(PLAN / "probes"))
    from qc_common import project_tr
    arrays = {}
    for name, (m, x, H) in cases().items():
        Hp, Hmw = project_tr(H, m, x)
        arrays[f"{name}_Hp"], arrays[f"{name}_Hmw"] = Hp, Hmw
    tmp = GOLDEN.with_suffix(".tmp.npz")
    np.savez(tmp, **arrays)
    tmp.replace(GOLDEN)
    print(sorted(arrays))
    return 0


if __name__ == "__main__":
    sys.exit(main())
