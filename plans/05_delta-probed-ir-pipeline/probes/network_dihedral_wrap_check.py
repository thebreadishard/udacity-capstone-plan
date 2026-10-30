"""Does the carried network jump where a dihedral wraps from +π to −π (TASKS 149)?

v1.3's pair features carry each internal primitive's raw value (`e7_rungB_pairs.molecule_pairs`), and a planar molecule's dihedrals sit at
0 or ±π, so geometry noise far below an optimiser's tolerance can move a value by 2π. This check takes two result folders of one molecule
in one atom order (a pipeline result and its corpus folder, say), counts the primitives whose value differs by more than 0.1 rad, and runs
the carried models (read-only) on both: as built, and with geomeTRIC's `Dihedral.value` mapped onto one side of the wrap — in this process
only. Writes a JSON record.

    python probes/network_dihedral_wrap_check.py <folder a> <folder b> --out <record.json>
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from collections import Counter
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import numpy as np
from geometric.internal import Dihedral, PrimitiveInternalCoordinates
from geometric.molecule import Molecule

sys.path.insert(0, str(Path(__file__).resolve().parent))
import network_invariance_check as N

BOHR_TO_ANGSTROM = 0.529177210903
JUMP_RAD = 0.1             # a smooth difference between two converged geometries is ~1e-4 rad; a wrap is ~2π
WRAP_WINDOW_RAD = 1e-3     # values within this of −π are mapped onto +π


def _geometry(folder: Path) -> dict:
    return json.loads((folder / "geometry.json").read_text(encoding="utf-8"))


def value_jumps(a: Path, b: Path) -> dict:
    """Primitives (built on folder a's geometry) whose value differs between the two geometries by more than JUMP_RAD, per kind."""
    ga, gb = _geometry(a), _geometry(b)
    if ga["symbols"] != gb["symbols"]:
        raise ValueError("the two folders hold other atom orders; this check compares one order")
    mol = Molecule()
    mol.elem = [s.capitalize() for s in ga["symbols"]]
    mol.xyzs = [np.asarray(ga["coords_bohr"], float) * BOHR_TO_ANGSTROM]
    ic = PrimitiveInternalCoordinates(mol, build=True, connect=True, addcart=False)
    xa, xb = (np.asarray(g["coords_bohr"], float).reshape(-1) for g in (ga, gb))
    diff = np.array([abs(float(p.value(xa)) - float(p.value(xb))) for p in ic.Internals])
    kinds = [type(p).__name__ for p in ic.Internals]
    return {"geometry_max_diff_bohr": float(np.abs(xa - xb).max()),
            "primitives": dict(Counter(kinds)),
            "jumps": dict(Counter(k for k, d in zip(kinds, diff, strict=True) if d > JUMP_RAD)),
            "largest_smooth_diff_rad": float(diff[diff <= JUMP_RAD].max())}


@contextmanager
def one_sided_dihedrals() -> Iterator[None]:
    """geomeTRIC's Dihedral.value with (−π, −π + WRAP_WINDOW_RAD) mapped onto +π, restored on exit."""
    original = Dihedral.value

    def one_sided(self: Dihedral, xyz: np.ndarray) -> float:
        v = original(self, xyz)
        return v + 2 * np.pi if v < -np.pi + WRAP_WINDOW_RAD else v

    Dihedral.value = one_sided
    try:
        yield
    finally:
        Dihedral.value = original


def network_difference(a: Path, b: Path) -> float:
    """Largest difference (cm⁻¹) between the carried network's corrected frequencies on the two folders' geometries and Hessians."""
    with tempfile.TemporaryDirectory() as t:
        out = []
        for i, src in enumerate((a, b)):
            d = Path(t) / str(i)
            d.mkdir()
            shutil.copy(src / "geometry.json", d / "geometry.json")
            with np.load(src / N.P.RI.LOW_HESSIAN) as z:
                np.savez(d / N.P.RI.LOW_HESSIAN, H_projected=z["H_projected"])
            out.append(N.corrected_frequencies(d)[0])
    return round(float(np.abs(out[0] - out[1]).max()), 4)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("a", type=Path)
    ap.add_argument("b", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)
    record = {"a": str(args.a), "b": str(args.b), "models": [m.name for m in N.P.carried_models()], **value_jumps(args.a, args.b),
              "network_max_diff_cm": network_difference(args.a, args.b)}
    with one_sided_dihedrals():
        record["network_max_diff_cm_one_sided"] = network_difference(args.a, args.b)
    tmp = args.out.with_name(args.out.name + ".tmp")
    tmp.write_text(json.dumps(record, indent=1), encoding="utf-8")
    tmp.replace(args.out)
    print(json.dumps({k: v for k, v in record.items() if k not in ("a", "b", "models")}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
