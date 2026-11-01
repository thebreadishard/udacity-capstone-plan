"""How the redundant primitive internal coordinates are built and encoded, independent of how the molecule was written (TASKS 149).

geomeTRIC's `PrimitiveInternalCoordinates` keeps, at a planar centre with three neighbours, two of the three angles and an out-of-plane
coordinate, and which angle it drops follows the atom numbers (the first planar permutation of the neighbours in index order). Two
writings of one molecule therefore get different primitive sets: on phenanthrene 2–3 angles (30 Oct 2026). The `canonical` angle choice
builds the primitives on the atoms in a canonical order and maps the result back to the input order, so that every writing gets the same
set. Separately, a dihedral's value (geomeTRIC's arctan2, in (−π, π]) jumps by 2π where a planar molecule's dihedral sits at ±π (half
of phenanthrene's 64); the `cos` encoding gives a dihedral cos φ instead of φ, and `cossin` adds sin φ in a slot of its own. sin φ, like
φ itself, changes sign under a reflection (TASKS 52: the head predicts from invariants), so `cos` alone keeps the features
reflection-even; for a planar molecule cos φ = ±1 says everything and sin φ is noise around zero. Out-of-plane values keep their raw
value: they sit near 0 (none within 0.1 rad of ±π on benzene or phenanthrene, 1 Nov 2026), where the raw value is smooth and cos would
flatten its first-order change.

The two belong together. For a molecule with symmetry-equivalent atoms (benzene, phenanthrene) the canonical ranks tie and the
tie-break follows the input order, so another order can give a symmetry image of the primitive set: other labels, the same features
as a set. A raw dihedral at ±π changes sign between mirror images (phenanthrene: 4π in a sum feature, 1 Nov 2026); under `cos` the
image's features equal the original's (`tests/test_internal_coords.py`, `probes/v15_feature_order_check.py`).

The defaults (`geometric`, `raw`) are the carried recipe (v1.3); `canonical` with `cos` is v1.5's candidate.
"""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
from learning_curve_layerA_v2_descriptors import bond_graph

ANGLE_CHOICES: tuple[str, ...] = ("geometric", "canonical")
DIHEDRAL_ENCODINGS: tuple[str, ...] = ("raw", "cos", "cossin")


@dataclass(frozen=True)
class PrimitiveSettings:
    """How the primitives are built and how a torsion's value enters the features; refused when unknown, before anything is built."""

    angle_choice: str = "geometric"
    dihedral_encoding: str = "raw"

    def __post_init__(self) -> None:
        if self.angle_choice not in ANGLE_CHOICES:
            raise ValueError(f"angle_choice must be one of {ANGLE_CHOICES}, got {self.angle_choice!r}")
        if self.dihedral_encoding not in DIHEDRAL_ENCODINGS:
            raise ValueError(f"dihedral_encoding must be one of {DIHEDRAL_ENCODINGS}, got {self.dihedral_encoding!r}")


CARRIED = PrimitiveSettings()   # v1.3's construction and encoding


def canonical_order(symbols: Sequence[str], coords_bohr: np.ndarray) -> np.ndarray:
    """The input's atom indices in canonical order: RDKit's canonical ranks, ties broken, on the element-labelled bond graph that the
    descriptors use. Position q of the result holds the input index of the atom ranked q. Atoms that the ranks cannot tell apart are
    symmetry-equivalent, so a different tie-break changes the primitive set only by a symmetry of the molecule (its features are the
    same under the `cos` encoding)."""
    from rdkit import Chem

    adj = bond_graph(symbols, coords_bohr)
    mol = Chem.RWMol()
    for s in symbols:
        mol.AddAtom(Chem.Atom(s.capitalize()))
    for i, nbrs in enumerate(adj):
        for j in nbrs:
            if i < j:
                mol.AddBond(i, j, Chem.BondType.SINGLE)
    mol.UpdatePropertyCache(strict=False)
    Chem.FastFindRings(mol)
    ranks = list(Chem.CanonicalRankAtoms(mol, breakTies=True))
    return np.argsort(ranks, kind="stable")


def cartesian_columns(order: np.ndarray) -> np.ndarray:
    """The Cartesian columns (3 per atom) of the input atoms `order` names, in canonical position order."""
    return (3 * np.asarray(order)[:, None] + np.arange(3)).ravel()


def to_input_order_B(B_canonical: np.ndarray, order: np.ndarray) -> np.ndarray:
    """A Wilson B built on the canonically ordered atoms, with its columns in the input's atom order."""
    B = np.empty_like(B_canonical)
    B[:, cartesian_columns(order)] = B_canonical
    return B


def to_input_order_atoms(atoms: list[set[int]], order: np.ndarray) -> list[set[int]]:
    """Primitive atom sets in canonical positions, as input atom indices."""
    return [{int(order[k]) for k in s} for s in atoms]


def torsion_values(value: float, encoding: str) -> tuple[float, float]:
    """(value slot, sine slot) of a dihedral: (φ, 0) raw, (cos φ, 0) under `cos`, (cos φ, sin φ) under
    `cossin`."""
    if encoding == "cossin":
        return float(np.cos(value)), float(np.sin(value))
    if encoding == "cos":
        return float(np.cos(value)), 0.0
    return value, 0.0
