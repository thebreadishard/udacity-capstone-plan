"""Does the carried network jump where a dihedral wraps from +π to −π (TASKS 149)?

v1.3's pair features carry each internal primitive's raw value (`e7_rungB_pairs.molecule_pairs`), and a planar molecule's dihedrals sit at
0 or ±π, so geometry noise far below an optimiser's tolerance can move a value by 2π. This check takes two result folders of one molecule
in one atom order (a pipeline result and its corpus folder, say), counts the primitives whose value differs by more than 0.1 rad, and runs
the carried models (read-only) on both: as built, and with geomeTRIC's `Dihedral.value` mapped onto one side of the wrap — in this process
only. The second action measures what the wrap costs on the evaluation: for every hold-out (a) molecule with a ωB97X analytic truth, the
rms position error (B3LYP modes paired by shape, as `pipeline_vs_corpus.against_truth` pairs them) as stored, under K random choices of
side for each near-π dihedral, and with the mean correction over those choices. Each writes a JSON record.

    python probes/network_dihedral_wrap_check.py pair <folder a> <folder b> --out <record.json>
    python probes/network_dihedral_wrap_check.py patterns [--k 8] --out <record.json>
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
import zlib
from collections import Counter
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import numpy as np
from geometric.internal import Dihedral, PrimitiveInternalCoordinates
from geometric.molecule import Molecule

sys.path.insert(0, str(Path(__file__).resolve().parent))
import network_invariance_check as N
import pipeline_vs_corpus as V

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


@contextmanager
def random_sides(seed: int) -> Iterator[None]:
    """geomeTRIC's Dihedral.value with each near-π value put on a side of the wrap drawn from the seed and the dihedral's atoms, restored on
    exit."""
    original = Dihedral.value

    def drawn(self: Dihedral, xyz: np.ndarray) -> float:
        v = original(self, xyz)
        if abs(v) < np.pi - WRAP_WINDOW_RAD:
            return v
        side = zlib.crc32(f"{seed}:{self.a},{self.b},{self.c},{self.d}".encode()) & 1
        return abs(v) if side else -abs(v)

    Dihedral.value = drawn
    try:
        yield
    finally:
        Dihedral.value = original


def _frequencies(H: np.ndarray, masses: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    f, _, L = N.mode_intensities(H, masses, np.zeros((3, H.shape[0])), return_modes=True)
    return f, L


def holdout_a_with_truth() -> list[str]:
    """Hold-out (a) molecules of the carried models' evaluation records that hold a ωB97X analytic truth."""
    models = tuple(m.name for m in N.P.carried_models())
    ids = {k for p in V.A.evaluation_records(models) for k in json.loads(p.read_text(encoding="utf-8"))["a"]["per_molecule"]}
    return sorted(i for i in ids if (N.P.CORPUS / i / V.TRUTH).exists())


def pattern_errors(mol_id: str, k: int) -> dict:
    """rms position error (cm⁻¹) against the ωB97X truth: as stored, under k random sides of the wrap, and with their mean correction."""
    d = N.P.CORPUS / mol_id
    masses = np.asarray(_geometry(d)["masses_amu"], float)
    with np.load(d / N.P.RI.LOW_HESSIAN) as z:
        H = z["H_projected"]
    with np.load(d / V.TRUTH) as z:
        H_true = z["H_projected"]
    _, L0 = _frequencies(H, masses)
    ft, Lt = _frequencies(H_true, masses)
    truth = ft[V.match_modes(L0, Lt)]

    def rms(dH: np.ndarray) -> float:
        fp, Lp = _frequencies(H + dH, masses)
        return round(float(np.sqrt(np.mean((fp[V.match_modes(L0, Lp)] - truth) ** 2))), 3)

    models = N.P.carried_models()
    stored = N.P.correction(models, d)[0]
    drawn = []
    for seed in range(k):
        with random_sides(seed):
            drawn.append(N.P.correction(models, d)[0])
    errors = [rms(x) for x in drawn]
    return {"n_atoms": len(masses), "as_stored": rms(stored), "drawn_min": min(errors), "drawn_max": max(errors),
            "drawn_mean": round(float(np.mean(errors)), 3), "mean_correction": rms(np.mean(drawn, 0))}


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
    sub = ap.add_subparsers(dest="action", required=True)
    pair = sub.add_parser("pair", help="two folders of one molecule in one atom order")
    pair.add_argument("a", type=Path)
    pair.add_argument("b", type=Path)
    patterns = sub.add_parser("patterns", help="hold-out (a) against ωB97X under random sides of the wrap")
    patterns.add_argument("--k", type=int, default=8, help="random choices of side per molecule")
    for p in (pair, patterns):
        p.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)
    record: dict = {"action": args.action, "models": [m.name for m in N.P.carried_models()]}
    if args.action == "pair":
        record |= {"a": str(args.a), "b": str(args.b), **value_jumps(args.a, args.b), "network_max_diff_cm": network_difference(args.a, args.b)}
        with one_sided_dihedrals():
            record["network_max_diff_cm_one_sided"] = network_difference(args.a, args.b)
    else:
        if args.k < 1:
            ap.error("--k must be at least 1")
        record |= {"k": args.k, "molecules": {}}
        for mol_id in holdout_a_with_truth():
            record["molecules"][mol_id] = pattern_errors(mol_id, args.k)
            print(mol_id, record["molecules"][mol_id], flush=True)
    tmp = args.out.with_name(args.out.name + ".tmp")
    tmp.write_text(json.dumps(record, indent=1), encoding="utf-8")
    tmp.replace(args.out)
    print(json.dumps({k: v for k, v in record.items() if k not in ("a", "b", "models", "molecules")}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
