"""The molecules and the record format of tests/data/point_group_ops_golden.json (TASKS 204): the operations `probes/e8_symmetry.py`'s
point_group_ops found before it moved into src/dpir/symmetry.py, pinned so the move is shown to change nothing.

    python tests/symmetry_golden.py        writes the golden file with the implementation importable as e8_symmetry.point_group_ops
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

PLAN = Path(__file__).resolve().parents[1]
GOLDEN = PLAN / "tests" / "data" / "point_group_ops_golden.json"
BOHR = 0.529177210903


def _ring(n: int, radius: float, phase: float = 0.0) -> np.ndarray:
    ang = phase + np.arange(n) * 2 * np.pi / n
    return np.stack([radius * np.cos(ang), radius * np.sin(ang), np.zeros(n)], 1)


def molecules() -> dict[str, tuple[list[str], np.ndarray]]:
    """Symbols and coordinates (bohr) of the pinned molecules: point groups D6h, D2h, C2v, D3h, Cs and C1."""
    sys.path.insert(0, str(PLAN / "probes"))
    from qff_symmetry_count import tetracene_ideal
    benzene = (["C"] * 6 + ["H"] * 6, np.vstack([_ring(6, 1.39), _ring(6, 2.48)]) / BOHR)
    water = (["O", "H", "H"], np.array([[0.0, 0.0, 0.0], [0.0, -1.4305, 1.1093], [0.0, 1.4305, 1.1093]]))
    triazine = (["C", "N"] * 3 + ["H"] * 3,
                np.vstack([_ring(6, 1.34), _ring(3, 2.42)]) / BOHR)
    cs = (["O", "H", "H"], np.array([[0.0, 0.0, 0.0], [0.0, -1.4305, 1.1093], [0.0, 1.5305, 1.0093]]))
    c1 = (["C", "N", "O", "H"], np.array([[0.0, 0.0, 0.0], [2.6, 0.1, 0.0], [0.3, 2.4, 0.4], [-1.0, -0.9, 1.3]]))
    return {"benzene": benzene, "tetracene": tetracene_ideal(), "water": water, "triazine": triazine, "water_cs": cs, "c1": c1}


def record(ops: list) -> list[dict]:
    """Operations as JSON: the permutation, whether improper, and R; sorted by (perm, improper)."""
    out = [{"perm": [int(i) for i in p], "improper": bool(np.linalg.det(R) < 0), "R": np.asarray(R).tolist()} for R, p in ops]
    return sorted(out, key=lambda o: (o["perm"], o["improper"]))


def main() -> int:
    sys.path.insert(0, str(PLAN / "probes"))
    if GOLDEN.exists():
        raise SystemExit(f"{GOLDEN} exists: it pins the implementation before the move; re-pinning with the moved code proves nothing")
    from e8_symmetry import point_group_ops
    golden = {name: record(point_group_ops(sym, x)) for name, (sym, x) in molecules().items()}
    GOLDEN.parent.mkdir(exist_ok=True)
    tmp = GOLDEN.with_suffix(".tmp")
    tmp.write_text(json.dumps(golden, indent=1) + "\n", encoding="utf-8")
    tmp.replace(GOLDEN)
    print({k: len(v) for k, v in golden.items()})
    return 0


if __name__ == "__main__":
    sys.exit(main())
