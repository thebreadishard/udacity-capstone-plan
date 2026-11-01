"""Do v1.5's switches make the network's input independent of the atom order? Feature level only, no network (TASKS 149).

A corpus folder's geometry and low-level Hessian are renumbered (random orders and SMILES-like orders, fixed by --seed). For each
combination of `angle_choice` (geometric | canonical) and `dihedral_encoding` (raw | cos | cossin), the primitives and the pair features are
built for every order and compared with the input order's: primitives by their atoms in the input's numbering, pair features pair by pair
and as a multiset, each column's values sorted (for a symmetric molecule the canonical tie-break can pick a symmetry image, with other
labels but the same features; equal multisets give equal sorted columns). A primitive set that differs means another basis for ΔF;
a pair feature that differs means another input to the head.
Geometries with Gaussian noise of NOISE_BOHR in the input order test the torsion encoding: a raw dihedral or out-of-plane value at ±π
jumps by 2π under such noise (30 Oct 2026). The record also counts the torsion values within 0.1 rad of ±π.

    python probes/v15_feature_order_check.py <molecule folder> ... [--orders 10] [--noisy 5] [--seed 0] [--out <record.json>]
"""
from __future__ import annotations

import argparse
import json
import sys
from itertools import product
from pathlib import Path

import numpy as np

PLAN = Path(__file__).resolve().parents[1]
M05 = PLAN / "modules" / "05_support_predictor" / "m05"
sys.path[:0] = [str(M05), str(PLAN / "src"), str(PLAN / "probes")]
import e7_rungB_pairs as RB  # noqa: E402
import e7_t2_sqm as T2  # noqa: E402
import internal_coords as IC  # noqa: E402
from network_invariance_check import smiles_like_order  # noqa: E402

from dpir.provenance import provenance  # noqa: E402

NEAR_PI_RAD = 0.1
NOISE_BOHR = 1e-4   # the geometry difference between two optimisations of phenanthrene (30 Oct 2026)
LOW_HESSIANS = ("hessian_b3lyp_analytic.npz", "hessian_b3lyp.npz")   # the first the folder has; it only feeds F_low's features


def primitive_keys(symbols: list[str], coords: np.ndarray, angle_choice: str) -> list[tuple]:
    """Each primitive as (class, its atoms in an orientation-free form), in the builder's primitive order and the input's numbering."""
    from geometric.internal import Angle, Dihedral, Distance, OutOfPlane

    if angle_choice == "canonical":
        order = IC.canonical_order(symbols, coords)
        keys = primitive_keys([symbols[k] for k in order], coords[order], "geometric")
        return [(cls, remap(atoms, order)) for cls, atoms in keys]
    prims = _geometric_primitives(symbols, coords)
    keys = []
    for p in prims:
        if isinstance(p, Distance):
            keys.append(("Distance", frozenset((p.a, p.b))))
        elif isinstance(p, Angle):
            keys.append(("Angle", (p.b, frozenset((p.a, p.c)))))
        elif isinstance(p, Dihedral):
            keys.append(("Dihedral", min((p.a, p.b, p.c, p.d), (p.d, p.c, p.b, p.a))))
        elif isinstance(p, OutOfPlane):
            keys.append(("OutOfPlane", (p.a, frozenset((p.b, p.c, p.d)))))
        else:
            keys.append((type(p).__name__, tuple(getattr(p, k) for k in ("a", "b", "c", "d") if hasattr(p, k))))
    return keys


def remap(atoms: object, order: np.ndarray) -> object:
    """An atom key from canonical positions into input indices (the shapes `primitive_keys` writes)."""
    if isinstance(atoms, frozenset):
        return frozenset(int(order[k]) for k in atoms)
    if isinstance(atoms, tuple) and len(atoms) == 2 and isinstance(atoms[1], frozenset):
        return (int(order[atoms[0]]), remap(atoms[1], order))
    path = tuple(int(order[k]) for k in atoms)
    return min(path, path[::-1])


def _geometric_primitives(symbols: list[str], coords: np.ndarray) -> list:
    from geometric.internal import PrimitiveInternalCoordinates
    from geometric.molecule import Molecule

    mol = Molecule()
    mol.elem = [s.capitalize() for s in symbols]
    mol.xyzs = [coords * T2.BOHR2ANG]
    ic = PrimitiveInternalCoordinates(mol, build=True, connect=True, addcart=False)
    return list(ic.Internals)


def to_reference(key: tuple, order: np.ndarray) -> tuple:
    """A key built on the renumbered molecule (atom k = input atom order[k]) in the input's numbering."""
    return (key[0], remap(key[1], order))


def built(symbols: list[str], coords: np.ndarray, H: np.ndarray, settings: IC.PrimitiveSettings) -> dict:
    """Primitive keys, pair features by pair key, and the torsion values near ±π, for one numbering."""
    B, _types = T2.internals(symbols, coords, settings)
    F_low, _ = T2.to_internal(H, B)
    pairs, feat, _cls, _B = RB.molecule_pairs(symbols, coords, F_low, settings=settings)
    keys = primitive_keys(symbols, coords, settings.angle_choice)
    if len(keys) != B.shape[0]:
        raise ValueError(f"{len(keys)} primitive keys against {B.shape[0]} rows of B")
    return {"keys": keys, "pairs": pairs, "feat": feat}


def compare(ref: dict, other: dict, order: np.ndarray) -> dict:
    """Differences of a renumbered build against the input order's, in the input's numbering."""
    other_keys = [to_reference(k, order) for k in other["keys"]]
    ref_set, other_set = set(ref["keys"]), set(other_keys)

    def by_pair(build: dict, keys: list[tuple]) -> dict:
        return {frozenset((keys[i], keys[j])) if i != j else (keys[i],): f for (i, j), f in zip(build["pairs"], build["feat"], strict=True)}

    ref_pairs, other_pairs = by_pair(ref, ref["keys"]), by_pair(other, other_keys)
    common = ref_pairs.keys() & other_pairs.keys()
    diffs = [float(np.max(np.abs(ref_pairs[k] - other_pairs[k]))) for k in common]
    return {"primitives_only_in_input": len(ref_set - other_set), "primitives_only_in_order": len(other_set - ref_set),
            "pairs_only_in_input": len(ref_pairs.keys() - other_pairs.keys()),
            "pairs_only_in_order": len(other_pairs.keys() - ref_pairs.keys()),
            "max_feature_difference": max(diffs) if diffs else 0.0,
            "pairs_feature_differs_1e-4": int(sum(d > 1e-4 for d in diffs)),
            "max_sorted_column_difference": sorted_column_difference(ref["feat"], other["feat"])}


def sorted_column_difference(a: np.ndarray, b: np.ndarray) -> float | None:
    """Largest difference between two sets of pair feature rows, each column sorted on its own (None when their counts differ)."""
    if a.shape != b.shape:
        return None
    return float(np.max(np.abs(np.sort(a, axis=0) - np.sort(b, axis=0))))


def near_pi(symbols: list[str], coords: np.ndarray) -> dict:
    """Dihedral and out-of-plane values within NEAR_PI_RAD of ±π (raw values, geomeTRIC's construction)."""
    from geometric.internal import Dihedral, OutOfPlane

    prims = _geometric_primitives(symbols, coords)
    xyz = coords.flatten()
    out = {}
    for cls in (Dihedral, OutOfPlane):
        vals = [float(p.value(xyz)) for p in prims if isinstance(p, cls)]
        out[cls.__name__] = {"count": len(vals), "near_pi": int(sum(np.pi - abs(v) < NEAR_PI_RAD for v in vals))}
    return out


def variants(coords: np.ndarray, symbols: list[str], counts: tuple[int, int], rng: np.random.Generator) -> list[tuple[str, np.ndarray, np.ndarray]]:
    """(kind, order, coordinates in that order): counts[0] renumberings, half random and half SMILES-like, then counts[1] noisy
    geometries in the input order."""
    n_orders, n_noisy = counts
    half = n_orders // 2
    out = [("random", o, coords[o]) for o in (rng.permutation(len(symbols)) for _ in range(n_orders - half))]
    out += [("smiles", o, coords[o]) for o in (smiles_like_order(symbols, coords, rng) for _ in range(half))]
    identity = np.arange(len(symbols))
    out += [("noise", identity, coords + rng.normal(0.0, NOISE_BOHR, coords.shape)) for _ in range(n_noisy)]
    return out


def check_molecule(folder: Path, counts: tuple[int, int], seed: int) -> dict:
    g = json.loads((folder / "geometry.json").read_text(encoding="utf-8"))
    symbols, coords = list(g["symbols"]), np.asarray(g["coords_bohr"], float)
    hessian = next((folder / name for name in LOW_HESSIANS if (folder / name).exists()), None)
    if hessian is None:
        raise FileNotFoundError(f"{folder.name}: none of {LOW_HESSIANS}")
    with np.load(hessian) as z:
        H = np.asarray(z["H_projected"], float)
    rng = np.random.default_rng(seed)
    cases = variants(coords, symbols, counts, rng)
    record = {"id": folder.name, "atoms": len(symbols), "hessian": hessian.name, "near_pi": near_pi(symbols, coords), "modes": {}}
    for angle_choice, encoding in product(IC.ANGLE_CHOICES, IC.DIHEDRAL_ENCODINGS):
        settings = IC.PrimitiveSettings(angle_choice=angle_choice, dihedral_encoding=encoding)
        ref = built(symbols, coords, H, settings)
        rows = []
        for kind, order, coords_case in cases:
            cols = IC.cartesian_columns(order)
            other = built([symbols[k] for k in order], coords_case, H[np.ix_(cols, cols)], settings)
            rows.append({"kind": kind, **compare(ref, other, order)})
        record["modes"][f"{angle_choice}/{encoding}"] = {
            "primitives": len(ref["keys"]), "pairs": len(ref["pairs"]), "worst": worst(rows), "cases": rows}
        print(f"{folder.name} {angle_choice}/{encoding}: {record['modes'][f'{angle_choice}/{encoding}']['worst']}", flush=True)
    return record


def worst(rows: list[dict]) -> dict:
    """The largest value of each measure, per kind of case (renumberings and noisy geometries apart)."""
    out = {}
    for kind in sorted({r["kind"] for r in rows}):
        mine = [r for r in rows if r["kind"] == kind]
        out[kind] = {k: (None if any(r[k] is None for r in mine) else max(r[k] for r in mine)) for k in mine[0] if k != "kind"}
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("folders", nargs="+", type=Path)
    ap.add_argument("--orders", type=int, default=10)
    ap.add_argument("--noisy", type=int, default=5)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", type=Path)
    a = ap.parse_args()
    if a.orders < 2:
        raise SystemExit("--orders must be at least 2 (one random and one SMILES-like order)")
    record = {"molecules": [check_molecule(f, (a.orders, a.noisy), a.seed) for f in a.folders], "orders": a.orders, "noisy": a.noisy,
              "noise_bohr": NOISE_BOHR, "seed": a.seed, "provenance": provenance()}
    if a.out:
        tmp = a.out.with_suffix(".tmp")
        tmp.write_text(json.dumps(record, indent=1, default=str), encoding="utf-8")
        tmp.replace(a.out)


if __name__ == "__main__":
    main()
