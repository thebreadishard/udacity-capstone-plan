"""How far one molecule's corrected bands move when the same molecule is given another way.

Ported from aromir's `src/aromir/own_spread.py` at aromir commit bb8eb62, verbatim in what it draws, in what order, how it pairs
and what it takes as a band's spread; change it there first and port it again. Module 08's own objects stand where aromir's do:
the networks are the pipeline's step 4 (`pipeline.seed_corrections`, which reads a molecule from a folder, so a presentation is
written to a temporary one), the modes are the family rule's (`normal_modes`), the pairing is `rungC_intensities.match_modes`, the
canonical order is `pipeline.smiles_route_order`, the bond check `molecule.changed_bonds`. The pipeline measures after step 4 and
writes `own_spread.json` beside the correction; the certificate reads that file (`of_result`) and runs no network.

The network's answer is not yet invariant: a molecule turned in space, its mirror image or
its atoms listed in another order can get other corrected positions (a sign of the
network's internal coordinates that the molecule does not fix). A release's invariance
record measures that on a handful of molecules; this module measures it on the molecule
at hand, so that each band's licence can rest on its own number. No quantum chemistry is
run: each presentation is the molecule's optimised geometry and the Hessian the networks
read, changed alike; the networks correct it, and the corrected Hessian is brought back to
the molecule as computed.

The presentations, with every draw from one generator seeded ``SEED``, in this order:

1. ``N_ROTATIONS`` random proper rotations (``random_rotation``, one draw each);
2. the mirror image (z → −z; no draw), and the mirror image of one more random rotation;
3. swaps of atoms the bond graph cannot tell apart. The symmetries of the heavy-atom
   skeleton are enumerated whole (``skeleton_symmetries``; those that keep each atom's
   element, charge, aromaticity and number of hydrogens), sorted, and the hydrogens on one
   heavy atom may be exchanged freely. Where skeleton symmetries and hydrogen exchanges
   together give at most ``N_SWAPS`` orders besides the molecule's own, all are tried, in
   sorted order, and nothing is drawn. Otherwise: every skeleton symmetry with the
   hydrogens following their heavy atom, or ``N_SWAPS`` of them drawn without replacement
   (``Generator.choice``, taken in sorted order) where there are more; then, for a
   molecule with a heavy atom that carries two or more hydrogens, ``N_HYDROGEN_SWAPS``
   draws of one skeleton symmetry (``Generator.integers``; the first is the molecule's
   own) with the hydrogens of each such atom, in ascending atom order, permuted
   (``Generator.permutation``);
4. ``N_LISTINGS`` random listings of the atoms (``Generator.permutation``), each put into
   the pipeline's canonical order (``pipeline.smiles_route_order``), as an xyz file listed that way
   would be. Every order the canonical order can give is a swap of step 3; which one a
   listing gives depends on how the running RDKit breaks its ties, so the listings come
   last and no other presentation depends on them.

An order already tried, or the molecule's own, is not tried again. The certificate records
every presentation tried: a rotation by its matrix, an order by its atoms.

Each presentation's corrected Hessian is the seeds' mean correction of the changed
molecule, mapped back (Kᵀ ΔH K for an orthogonal map K applied atom by atom; the 3×3
blocks put back for an order) and added to the low-level Hessian. Its modes are paired
with the printed modes by largest squared overlap (``match_modes``), not by rank, and
a band's shift is the distance of its partner from the printed position. Where a band's
partner holds less than ``PAIRED_OVERLAP`` of its motion, the pairing is not trusted alone:
the band and every band its partner shares ``MIXING_SHARE`` of motion with form a cluster,
whose printed positions and partners are compared in ascending order, and each band of the
cluster gets the larger of the cluster's largest shift and its own paired shift. Which of
the two pairings is right cannot be told, and the number licenses a band, so it takes the
larger. A band whose partner spreads the rest of its motion too thinly to share
``MIXING_SHARE`` with any one band has no cluster: it gets the larger of its paired shift
and its distance from the mode of its own rank. A band's spread is its largest shift over
the presentations: its distance from the printed presentation, not the range between
presentations.

    python -m m08.own_spread <pipeline result folder>      # measures a result of a pipeline before 0.15, with the networks it names
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import os
import sys
import tempfile
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import Any, Final, Literal

import numpy as np
import rdkit
from numpy.typing import NDArray
from rdkit import Chem
from scipy.sparse.csgraph import connected_components

from . import molecule as M
from . import pipeline as P
from . import reuse as R

# isort: split
from rungC_intensities import match_modes  # module 05's code, on the path through m08.pipeline

FloatArray = NDArray[np.float64]

FILE: Final = "own_spread.json"
"""The measurement beside a result's correction: written by the pipeline's step 4, read by the certificate."""
SAME_SPECTRUM_CM: Final = 1e-4
"""How far a stored measurement's printed positions may lie from those of the result's correction: an eigensolver's noise, no more."""

SEED: Final = 7
N_ROTATIONS: Final = 8
"""A linear angle is measured against a fixed axis of space, so how far a molecule with a
linear group moves depends on where that axis falls: three rotations gave benzonitrile
1.75 cm⁻¹ on v1.4, eight and twenty-four both 2.78."""
N_LISTINGS: Final = 4
N_SWAPS: Final = 12
N_HYDROGEN_SWAPS: Final = 6
MAX_SYMMETRIES: Final = 1000
"""How many symmetries of the heavy-atom skeleton are enumerated at most. Coronene has 12
and 1,4-di-tert-butylbenzene 144; a molecule that reaches the limit is recorded as capped,
and its swaps are then drawn from those RDKit happened to enumerate first."""
MIRROR: Final = np.diag([1.0, 1.0, -1.0])
PAIRED_OVERLAP: Final = 0.7
"""A band is paired with one mode of a presentation when that mode holds at least this
share of its motion. On v1.4 the lowest shares of the stored molecules are 0.51 (benzene),
0.58 (biphenyl) and 0.64 (diphenyl ether)."""
MIXING_SHARE: Final = 0.1
"""Two bands belong to one cluster when the partner of one holds this share of the other."""
DECIMALS: Final = 2
"""The decimals a spread is stated with (``stated``); the licence reads it unrounded."""
UNBUILT: Final = (ValueError, ArithmeticError, RuntimeError)
"""The errors that mean the networks could not correct one presentation: a value the inputs
refuse (module 05's builders raise ``ValueError``), and geomeTRIC's and torch's, which raise
``RuntimeError``. A presentation that fails so withholds the licence; any other error is a
defect and is raised. (aromir's tuple also names its own error class, which module 08 has not.)"""

Kind = Literal["rotation", "mirror image", "swap", "listing"]
COUNTED: Final[dict[Kind, tuple[str, str]]] = {
    "rotation": ("rotation", "rotations"),
    "mirror image": ("mirror image", "mirror images"),
    "swap": ("swap of equivalent atoms", "swaps of equivalent atoms"),
    "listing": ("other listing of the atoms", "other listings of the atoms"),
}
"""The words a count of each kind of presentation takes."""


@dataclass(frozen=True, eq=False)
class Molecule:
    """A molecule as a result folder's geometry.json holds it: what the networks read of it beside its Hessian.

    Attributes:
        symbols: The elements, as the folder writes them.
        coords_bohr: The positions, shape (N, 3).
        masses_amu: The masses, shape (N,).
        state: The folder's charge and multiplicity, where it names them.
    """

    symbols: tuple[str, ...]
    coords_bohr: FloatArray
    masses_amu: FloatArray
    state: Mapping[str, int]

    @classmethod
    def of_folder(cls, folder: Path) -> Molecule:
        """Return the molecule of a result or corpus folder."""
        g = json.loads((folder / R.GEOMETRY).read_text(encoding="utf-8"))
        state = {key: int(g[key]) for key in ("charge", "multiplicity") if key in g}
        return cls(tuple(g["symbols"]), np.asarray(g["coords_bohr"], float), np.asarray(g["masses_amu"], float), state)

    @property
    def n_atoms(self) -> int:
        """The number of atoms."""
        return len(self.symbols)

    def reordered(self, order: tuple[int, ...]) -> Molecule:
        """Return the molecule with atom ``order[k]`` in position k."""
        picked = list(order)
        return Molecule(tuple(self.symbols[k] for k in picked), self.coords_bohr[picked], self.masses_amu[picked], self.state)

    def geometry_record(self) -> dict[str, Any]:
        """Return the geometry.json the networks' input builders read."""
        return {"symbols": list(self.symbols), "coords_bohr": self.coords_bohr.tolist(), "masses_amu": self.masses_amu.tolist()} | dict(self.state)


Corrector = Callable[[Molecule, FloatArray], FloatArray]
"""The networks as the check uses them: the seeds' mean ΔH of a molecule and the Hessian they read."""


def mean_correction(networks: list[tuple[Any, Any]], molecule: Molecule, hessian: FloatArray) -> FloatArray:
    """Return the seeds' mean ΔH of a molecule given as arrays, by the pipeline's step 4.

    Step 4 reads a folder (geometry.json and the low-level Hessian), so the molecule is written to a temporary one.
    """
    with tempfile.TemporaryDirectory() as tmp:
        folder = Path(tmp)
        (folder / R.GEOMETRY).write_text(json.dumps(molecule.geometry_record()), encoding="utf-8")
        np.savez(folder / P.RI.LOW_HESSIAN, H_projected=hessian)
        return np.asarray(np.mean(P.seed_corrections(networks, folder), axis=0), dtype=float)


def random_rotation(rng: np.random.Generator) -> FloatArray:
    """Return a random proper rotation (determinant +1)."""
    q, _ = np.linalg.qr(rng.normal(size=(3, 3)))
    return np.asarray(q * np.sign(np.linalg.det(q)))


def moved(molecule: Molecule, hessian: FloatArray, matrix: FloatArray) -> tuple[Molecule, FloatArray]:
    """Return the molecule and its Hessian under an orthogonal map of space."""
    blocks = np.kron(np.eye(molecule.n_atoms), matrix)
    turned = Molecule(molecule.symbols, molecule.coords_bohr @ matrix.T, molecule.masses_amu, molecule.state)
    return turned, blocks @ hessian @ blocks.T


def coordinate_index(order: tuple[int, ...]) -> NDArray[np.int64]:
    """Return the Cartesian coordinates of the atoms in ``order``, three per atom."""
    return np.asarray((3 * np.array(order)[:, None] + np.arange(3)).ravel())


def reordered(molecule: Molecule, hessian: FloatArray, order: tuple[int, ...]) -> tuple[Molecule, FloatArray]:
    """Return the molecule with atom ``order[k]`` in position k."""
    index = coordinate_index(order)
    return molecule.reordered(order), hessian[np.ix_(index, index)]


@dataclass(frozen=True, eq=False)
class Change:
    """One presentation of the molecule: its atoms listed in another order, then moved.

    Attributes:
        name: The words a certificate names it by.
        kind: What kind of presentation it is.
        matrix: An orthogonal map of space, applied to every atom.
        order: Atom ``order[k]`` of the molecule is put in position k.
    """

    name: str
    kind: Kind
    matrix: FloatArray
    order: tuple[int, ...]

    def apply(self, molecule: Molecule, hessian: FloatArray) -> tuple[Molecule, FloatArray]:
        """Return the changed molecule and its Hessian."""
        return moved(*reordered(molecule, hessian, self.order), self.matrix)

    def undo(self, delta: FloatArray) -> FloatArray:
        """Return a Hessian of the changed molecule as one of the molecule itself."""
        blocks = np.kron(np.eye(len(self.order)), self.matrix)
        index = coordinate_index(self.order)
        back = np.zeros_like(delta)
        back[np.ix_(index, index)] = blocks.T @ delta @ blocks
        return back

    def record(self) -> dict[str, Any]:
        """Return what identifies the presentation: its map of space, or its atom order."""
        if self.kind in ("swap", "listing"):
            return {"name": self.name, "kind": self.kind, "order": list(self.order)}
        return {"name": self.name, "kind": self.kind, "matrix": self.matrix.tolist()}


def bond_graph(smiles: str) -> Chem.Mol:
    """Return a molecule's graph with its hydrogens, in the pipeline's canonical atom order.

    That is the order every geometry the pipeline computes is in: the heavy atoms as the
    canonical SMILES writes them, then each heavy atom's hydrogens
    (``pipeline.start_geometry``).

    Raises:
        ValueError: The SMILES does not parse.
    """
    parsed: Chem.Mol | None = Chem.MolFromSmiles(smiles)  # RDKit's stubs omit the None
    if parsed is None:
        msg = f"{smiles!r} does not parse as a SMILES"
        raise ValueError(msg)
    return Chem.AddHs(parsed)


def graph_of(smiles: str, molecule: Molecule) -> Chem.Mol:
    """Return the bond graph of a geometry that is in the canonical order of its SMILES.

    Raises:
        ValueError: The geometry's atoms or bonds are not those of the SMILES in its order
            (``molecule.changed_bonds``).
    """
    changed = M.changed_bonds(smiles, molecule.symbols, molecule.coords_bohr * R.BOHR_ANGSTROM)
    if changed:
        msg = f"the geometry is not the molecule of its SMILES in the canonical atom order: {'; '.join(changed)}"
        raise ValueError(msg)
    return bond_graph(smiles)


@dataclass(frozen=True)
class Symmetries:
    """The orders of a molecule's atoms that its bond graph cannot tell apart.

    Attributes:
        n_atoms: The number of atoms, hydrogens included.
        skeleton: Each symmetry of the heavy-atom skeleton other than the identity, as the
            heavy atom put in each heavy atom's place, in the graph's atom indices, sorted.
        hydrogens: The hydrogens of each heavy atom that carries any, ascending.
        capped: Whether the enumeration stopped at ``MAX_SYMMETRIES``.
    """

    n_atoms: int
    skeleton: tuple[dict[int, int], ...]
    hydrogens: dict[int, tuple[int, ...]]
    capped: bool

    @property
    def n_exchanges(self) -> int:
        """In how many ways the hydrogens can be listed on their own heavy atoms."""
        return math.prod(math.factorial(len(found)) for found in self.hydrogens.values())

    @property
    def n_orders(self) -> int:
        """How many orders the graph cannot tell apart, the molecule's own included."""
        return (len(self.skeleton) + 1) * self.n_exchanges

    def order(self, skeleton: dict[int, int], exchange: dict[int, tuple[int, ...]]) -> tuple[int, ...]:
        """Return the atom order of a skeleton symmetry with the hydrogens exchanged.

        The hydrogens of a heavy atom take the places of the hydrogens of the atom it
        replaces, in ascending order unless ``exchange`` permutes them.
        """
        order = list(range(self.n_atoms))
        for place, atom in skeleton.items():
            order[place] = atom
        for place, found in self.hydrogens.items():
            taken = self.hydrogens[skeleton.get(place, place)]
            permuted = exchange.get(place, tuple(range(len(found))))
            for position, hydrogen in enumerate(found):
                order[hydrogen] = taken[permuted[position]]
        return tuple(order)


def _alike(first: Chem.Atom, second: Chem.Atom) -> bool:
    """Tell whether two heavy atoms are of one kind for a symmetry of the skeleton."""
    return bool(
        first.GetAtomicNum() == second.GetAtomicNum()
        and first.GetFormalCharge() == second.GetFormalCharge()
        and first.GetIsAromatic() == second.GetIsAromatic()
        and first.GetTotalNumHs(includeNeighbors=True) == second.GetTotalNumHs(includeNeighbors=True)
    )


def skeleton_symmetries(graph: Chem.Mol) -> Symmetries:
    """Return the symmetries of a molecule's heavy-atom skeleton and its hydrogens.

    RDKit matches the skeleton onto itself (``GetSubstructMatches`` with
    ``uniquify=False``, the call of ``testSubstructMatchAcetate`` in RDKit's
    ``Code/GraphMol/Wrap/rough_test.py``, which counts every match of a query's atoms and
    not one per set of atoms); a match is kept when every atom lands on one of its own kind
    (``_alike``), which a match alone does not ask of the hydrogens.

    Raises:
        ValueError: A hydrogen is not an ordinary one on a single heavy atom.
    """
    heavy = [atom.GetIdx() for atom in graph.GetAtoms() if atom.GetAtomicNum() > 1]
    skeleton = M.without_hydrogens(graph)
    if skeleton.GetNumAtoms() != len(heavy):
        msg = "a hydrogen is not an ordinary one on a single heavy atom"
        raise ValueError(msg)
    matches = skeleton.GetSubstructMatches(skeleton, uniquify=False, useChirality=False, maxMatches=MAX_SYMMETRIES)
    kept = sorted(
        tuple(int(k) for k in match)
        for match in matches
        if all(_alike(graph.GetAtomWithIdx(heavy[k]), graph.GetAtomWithIdx(heavy[image])) for k, image in enumerate(match))
    )
    hydrogens = {
        atom: tuple(sorted(neighbour.GetIdx() for neighbour in graph.GetAtomWithIdx(atom).GetNeighbors() if neighbour.GetAtomicNum() == 1))
        for atom in heavy
    }
    return Symmetries(
        n_atoms=graph.GetNumAtoms(),
        skeleton=tuple({heavy[k]: heavy[image] for k, image in enumerate(match)} for match in kept if match != tuple(range(len(heavy)))),
        hydrogens={atom: found for atom, found in hydrogens.items() if found},
        capped=len(matches) >= MAX_SYMMETRIES,
    )


def _every_order(found: Symmetries) -> list[tuple[int, ...]]:
    """Return every order of the atoms the graph cannot tell apart but its own, sorted."""
    places = sorted(found.hydrogens)
    exchanges = [
        dict(zip(places, permuted, strict=True))
        for permuted in itertools.product(*(itertools.permutations(range(len(found.hydrogens[place]))) for place in places))
    ]
    orders = {found.order(skeleton, exchange) for skeleton in ({}, *found.skeleton) for exchange in exchanges}
    identity = found.order({}, {})
    return sorted(orders - {identity})


def _drawn_orders(found: Symmetries, rng: np.random.Generator) -> list[tuple[int, ...]]:
    """Return the swaps of a molecule with more orders than are all tried, as drawn."""
    skeleton = list(found.skeleton)
    if len(skeleton) > N_SWAPS:
        drawn = rng.choice(len(skeleton), size=N_SWAPS, replace=False)
        skeleton = [skeleton[k] for k in sorted(int(k) for k in drawn)]
    orders = [found.order(symmetry, {}) for symmetry in skeleton]
    places = sorted(place for place, held in found.hydrogens.items() if len(held) > 1)
    if not places:
        return orders
    with_own = [{}, *found.skeleton]
    for _ in range(N_HYDROGEN_SWAPS):
        symmetry = with_own[int(rng.integers(len(with_own)))]
        exchange = {place: tuple(int(k) for k in rng.permutation(len(found.hydrogens[place]))) for place in places}
        orders.append(found.order(symmetry, exchange))
    return orders


def swaps(found: Symmetries, rng: np.random.Generator) -> list[tuple[int, ...]]:
    """Return the swaps of equivalent atoms the check tries (the module's step 3)."""
    if not found.capped and found.n_orders - 1 <= N_SWAPS:
        return _every_order(found)
    return _drawn_orders(found, rng)


def _listings(graph: Chem.Mol, rng: np.random.Generator) -> list[tuple[int, ...]]:
    """Return the canonical orders of random listings, in terms of the molecule's atoms."""
    orders = []
    for _ in range(N_LISTINGS):
        listing = [int(atom) for atom in rng.permutation(graph.GetNumAtoms())]
        relisted = Chem.RenumberAtoms(graph, listing)
        orders.append(tuple(listing[k] for k in P.smiles_route_order(relisted)))
    return orders


def changes(graph: Chem.Mol, found: Symmetries) -> list[Change]:
    """Return the presentations the check tries, in the order they are drawn.

    Raises:
        ValueError: A hydrogen of the graph has no place in the canonical order.
    """
    rng = np.random.default_rng(SEED)
    identity = tuple(range(graph.GetNumAtoms()))
    tried = [Change(f"rotation {k + 1}", "rotation", random_rotation(rng), identity) for k in range(N_ROTATIONS)]
    tried.append(Change("the mirror image", "mirror image", MIRROR, identity))
    turned = MIRROR @ random_rotation(rng)
    tried.append(Change("the mirror image, rotated", "mirror image", turned, identity))
    seen = {identity}
    named: tuple[tuple[Kind, str, list[tuple[int, ...]]], ...] = (
        ("swap", "a swap of equivalent atoms", swaps(found, rng)),
        ("listing", "another listing", _listings(graph, rng)),
    )
    for kind, words, orders in named:
        new = [order for order in dict.fromkeys(orders) if order not in seen]
        seen.update(new)
        tried += [Change(f"{words} {k + 1}", kind, np.eye(3), order) for k, order in enumerate(new)]
    return tried


def describe(counts: Mapping[str, int]) -> str:
    """Say how many presentations of each kind were tried, as "8 rotations, 2 mirror images".

    ``counts`` is the record's count per kind (``OwnSpread.record``): the certificate reads the stored record, where
    aromir's reads the presentations themselves.
    """
    parts = []
    for kind, (one, many) in COUNTED.items():
        n = counts[kind]
        if n:
            parts.append(f"{n} {one if n == 1 else many}")
    return ", ".join(parts)


def stated(spread_cm: float, line_cm: float) -> str:
    """Return a spread as it is printed: to ``DECIMALS``, or to as many as show its side.

    A spread just beyond the licence line is not printed as the line itself: 3.004 against
    a line of 3 is "3.004", not "3.00".
    """
    for decimals in range(DECIMALS, 12):
        text = f"{spread_cm:.{decimals}f}"
        if (float(text) > line_cm) == (spread_cm > line_cm):
            return text
    return repr(spread_cm)


N_MIRROR_IMAGES: Final = 2
"""The mirror image and the mirror image of one more rotation (``changes``)."""


def _rule() -> dict[str, Any]:
    """Return the constants a measurement is made under: a record made under others is another rule's."""
    return {
        "seed": SEED,
        "rotations": N_ROTATIONS,
        "listings": N_LISTINGS,
        "swaps": N_SWAPS,
        "hydrogen_swaps": N_HYDROGEN_SWAPS,
        "max_symmetries": MAX_SYMMETRIES,
        "paired_overlap": PAIRED_OVERLAP,
        "mixing_share": MIXING_SHARE,
    }


def _refusal_record(reason: str) -> dict[str, Any]:
    """Return the record of a check that did not run, in the shape of one that did."""
    return _rule() | {
        "rdkit": rdkit.__version__,
        "skeleton_symmetries": None,
        "equivalent_orders": None,
        "symmetries_capped": None,
        "counts": dict.fromkeys(COUNTED, 0),
        "presentations": [],
        "not_measured_because": reason,
    }


@dataclass(frozen=True, eq=False)
class Measurement:
    """What a certificate reads of the check: the stored form of an ``OwnSpread``.

    Attributes:
        spread_cm: Per vibrational mode of the corrected Hessian, ascending (all 3N−6, the
            family rule's ``normal_modes``), its largest distance from the printed position,
            cm⁻¹, unrounded; empty when the check did not run.
        change: Per mode, the name of the presentation that gave it.
        record: What identifies the check and every presentation tried (``OwnSpread.record``).
    """

    spread_cm: tuple[float, ...]
    change: tuple[str, ...]
    record: Mapping[str, Any]

    @property
    def refusal(self) -> str:
        """Why the check could not run; empty when it ran."""
        return str(self.record["not_measured_because"])

    @property
    def n_tried(self) -> int:
        """How many presentations were tried."""
        return len(self.record["presentations"])


def not_measured(reason: str) -> Measurement:
    """Return the measurement of a molecule whose check did not run, with the reason."""
    return Measurement(spread_cm=(), change=(), record=_refusal_record(reason))


@dataclass(frozen=True, eq=False)
class OwnSpread:
    """How far each printed band moved over the presentations, or why that was not measured.

    Attributes:
        spread_cm: Per band, in the order of the printed spectrum, its largest distance
            from the printed position, cm⁻¹, unrounded; empty when the check did not run.
        change: Per band, the name of the presentation that gave it.
        tried: Every presentation tried.
        symmetries: The molecule's graph symmetries; None when the check did not get there.
        refusal: Why the check could not run; empty when it ran.
    """

    spread_cm: tuple[float, ...]
    change: tuple[str, ...]
    tried: tuple[Change, ...]
    symmetries: Symmetries | None
    refusal: str

    def record(self) -> dict[str, Any]:
        """Return what a certificate keeps of the check, enough to make each presentation again.

        The RDKit version is named because the listings, and the swaps of a molecule whose
        symmetries reached ``MAX_SYMMETRIES``, depend on it.
        """
        found = self.symmetries
        return _refusal_record(self.refusal) | {
            "skeleton_symmetries": None if found is None else len(found.skeleton) + 1,
            "equivalent_orders": None if found is None else found.n_orders,
            "symmetries_capped": None if found is None else found.capped,
            "counts": {kind: sum(c.kind == kind for c in self.tried) for kind in COUNTED},
            "presentations": [change.record() for change in self.tried],
        }

    def measurement(self) -> Measurement:
        """Return the check as a certificate reads it."""
        return Measurement(self.spread_cm, self.change, self.record())


def _not_measured(reason: str) -> OwnSpread:
    return OwnSpread(spread_cm=(), change=(), tried=(), symmetries=None, refusal=reason)


@dataclass(frozen=True, eq=False)
class Modes:
    """The vibrational modes of a Hessian by the family rule (``normal_modes``: all but the six of smallest |ω|).

    Attributes:
        wavenumbers: Signed harmonic wavenumbers in cm⁻¹, ascending, shape (3N−6,).
        vectors: Mass-weighted, orthonormal mode vectors as columns, shape (3N, 3N−6).
    """

    wavenumbers: FloatArray
    vectors: FloatArray


def modes_of(hessian: FloatArray, masses_amu: FloatArray) -> Modes:
    """Return the modes of a projected Cartesian Hessian, as the pipeline's spectrum and seed ranges take them."""
    _, wavenumbers, vectors, _ = P.normal_modes(hessian, masses_amu)
    return Modes(np.asarray(wavenumbers, dtype=float), np.asarray(vectors, dtype=float))


def band_shifts(modes: Modes, printed: Modes) -> FloatArray:
    """Return how far each printed band lies from its place in one presentation's modes.

    A band whose partner holds at least ``PAIRED_OVERLAP`` of its motion is at the distance
    of that partner. Bands that mix — two near-degenerate bands whose motion a presentation
    shares out anew — have no partner of their own, and the pairing may give the band that
    moved the partner that stayed: they are also compared as a cluster, the printed
    positions and the partners' in ascending order, and each gets the larger of the
    cluster's largest distance and its own partner's. Neither pairing can be told to be the
    right one, so neither may license a band the other withholds. A mixed band alone in its
    cluster — its partner's other motion spread under ``MIXING_SHARE`` a band — is compared
    with the mode of its own rank in the whole spectrum instead.
    """
    overlap = (modes.vectors.T @ printed.vectors) ** 2
    partner = match_modes(modes.vectors, printed.vectors)
    shifts = np.zeros(len(printed.wavenumbers))
    shifts[partner] = np.abs(modes.wavenumbers - printed.wavenumbers[partner])
    of_band = np.argsort(partner)
    share = overlap[of_band]
    mixed = np.flatnonzero(np.diag(share) < PAIRED_OVERLAP)
    if not mixed.size:
        return shifts
    linked = share >= MIXING_SHARE
    _, cluster_of = connected_components(linked | linked.T, directed=False)
    for cluster in np.unique(cluster_of[mixed]):
        bands = np.flatnonzero(cluster_of == cluster)
        ranked = bands if bands.size == 1 else of_band[bands]
        here = np.sort(printed.wavenumbers[bands])
        there = np.sort(modes.wavenumbers[ranked])
        shifts[bands] = np.maximum(shifts[bands], np.abs(there - here).max())
    return shifts


def corrected_modes(networks: Corrector, molecule: Molecule, hessian: FloatArray, change: Change) -> Modes:
    """Return the modes of the low-level Hessian with the changed molecule's correction.

    Raises:
        ValueError: The networks' answer or the modes it gives are not finite: no band can be paired with them.
    """
    answer = networks(*change.apply(molecule, hessian))
    if not np.isfinite(answer).all():
        msg = "the correction is not finite"
        raise ValueError(msg)
    modes = modes_of(hessian + change.undo(answer), molecule.masses_amu)
    if not (np.isfinite(modes.wavenumbers).all() and np.isfinite(modes.vectors).all()):
        msg = "the corrected modes are not finite"
        raise ValueError(msg)
    return modes


def measure(networks: Corrector, smiles: str, molecule: Molecule, hessian: FloatArray, correction: FloatArray) -> OwnSpread:
    """Return how far the bands of ``hessian + correction`` move over the presentations.

    A molecule whose presentations cannot be drawn, or one of whose presentations the
    networks cannot correct (``UNBUILT``), is not measured, and the reason names which.

    Args:
        networks: The networks whose answer is checked.
        smiles: The molecule's SMILES as admission writes it.
        molecule: Its geometry, in the pipeline's canonical atom order.
        hessian: Its low-level Hessian, the one the networks read.
        correction: The printed correction, the seeds' mean for the molecule as computed.
    """
    printed = modes_of(hessian + correction, molecule.masses_amu)
    try:
        graph = graph_of(smiles, molecule)
        found = skeleton_symmetries(graph)
        tried = changes(graph, found)
    except ValueError as error:
        return _not_measured(str(error))
    shifts = np.zeros((len(tried), len(printed.wavenumbers)))
    for row, change in zip(shifts, tried, strict=True):
        try:
            modes = corrected_modes(networks, molecule, hessian, change)
        except UNBUILT as error:
            return _not_measured(f"the networks could not correct the molecule given as {change.name}: {type(error).__name__}: {error}")
        row[:] = band_shifts(modes, printed)
    worst = shifts.argmax(axis=0)
    return OwnSpread(
        spread_cm=tuple(float(x) for x in shifts.max(axis=0)),
        change=tuple(tried[k].name for k in worst),
        tried=tuple(tried),
        symmetries=found,
        refusal="",
    )


def _result_arrays(folder: Path) -> tuple[FloatArray, FloatArray, tuple[str, ...]]:
    """Return a result folder's low-level Hessian, its printed correction and the names of the models that made it."""
    with np.load(folder / P.RI.LOW_HESSIAN) as z:
        hessian = np.asarray(z["H_projected"], dtype=float)
    with np.load(folder / P.CORRECTION) as z:
        return hessian, np.asarray(z["dH"], dtype=float), tuple(str(name) for name in z["models"])


def save(folder: Path, found: Measurement, seconds: float) -> Path:
    """Write a measurement beside the correction it was made from, with the models and the printed positions that name that correction."""
    hessian, correction, made_by = _result_arrays(folder)
    stored = {
        "models": list(made_by),
        "printed_cm": modes_of(hessian + correction, Molecule.of_folder(folder).masses_amu).wavenumbers.tolist(),
        "spread_cm": list(found.spread_cm),
        "change": list(found.change),
        "seconds": seconds,
        "record": dict(found.record),
    }
    path = folder / FILE
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(stored, indent=1, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, path)
    return path


def measure_result(models: tuple[Path, ...], folder: Path, smiles: str) -> Path:
    """Measure a result folder's own spread with the networks that made its correction, and write it beside it.

    Raises:
        RuntimeError: The folder's correction names other models than ``models``.
    """
    started = time.time()
    hessian, correction, made_by = _result_arrays(folder)
    if made_by != tuple(path.name for path in models):
        msg = f"{folder}: {P.CORRECTION} names the models {list(made_by)}, and {[path.name for path in models]} are to measure its spread"
        raise RuntimeError(msg)
    networks = partial(mean_correction, P.load_networks(models))
    found = measure(networks, smiles, Molecule.of_folder(folder), hessian, correction)
    return save(folder, found.measurement(), round(time.time() - started, 1))


def _other_rule(stored: dict[str, Any], n_modes: int) -> list[str]:
    """Name what makes a stored measurement another rule's, or not a whole one: such a record is measured again, not read."""
    record, spreads, changes_ = stored["record"], stored["spread_cm"], stored["change"]
    reasons = [f"{key} is {record.get(key)!r}, the rule's is {value!r}" for key, value in _rule().items() if record.get(key) != value]
    made, counts = record["presentations"], record["counts"]
    if len(changes_) != len(spreads):
        reasons.append(f"{len(changes_)} presentations named for {len(spreads)} spreads")
    if record["not_measured_because"]:
        if spreads or made:
            reasons.append("it names a refusal and holds spreads or presentations")
        return reasons
    if len(spreads) != n_modes:
        reasons.append(f"{len(spreads)} spreads for {n_modes} modes")
    if not made or len(made) != sum(counts.values()):
        reasons.append(f"{len(made)} presentations where its counts give {sum(counts.values())}")
    if (counts["rotation"], counts["mirror image"]) != (N_ROTATIONS, N_MIRROR_IMAGES):
        reasons.append(f"{counts['rotation']} rotations and {counts['mirror image']} mirror images, the rule's are "
                       f"{N_ROTATIONS} and {N_MIRROR_IMAGES}")
    unknown = sorted(set(changes_) - {tried["name"] for tried in made})
    if unknown:
        reasons.append(f"spreads under presentations it does not hold: {unknown}")
    return reasons


def of_result(folder: Path) -> Measurement:
    """Return the own spread a result folder holds, for the certificate.

    A folder without one — a result of a pipeline before 0.15 — is not measured, and the reason says how to measure it.
    The licence line is not among the constants compared: a spread is stored unrounded and no line enters its measurement.

    Raises:
        RuntimeError: The stored measurement is of other models or of another correction than the folder's, or was not made
            under this module's constants (``_other_rule``).
    """
    path = folder / FILE
    if not path.is_file():
        return not_measured(f"the result holds no {FILE}: the pipeline writes it since 0.15, and python -m m08.own_spread measures an earlier result")
    stored = json.loads(path.read_text(encoding="utf-8"))
    hessian, correction, made_by = _result_arrays(folder)
    printed = modes_of(hessian + correction, Molecule.of_folder(folder).masses_amu).wavenumbers
    if tuple(stored["models"]) != made_by:
        msg = f"{path}: measured with {stored['models']}, and {P.CORRECTION} is of {list(made_by)}"
        raise RuntimeError(msg)
    measured = np.asarray(stored["printed_cm"], dtype=float)
    if measured.shape != printed.shape or np.abs(measured - printed).max() > SAME_SPECTRUM_CM:
        msg = f"{path}: measured from other printed positions than {P.CORRECTION} gives"
        raise RuntimeError(msg)
    reasons = _other_rule(stored, len(printed))
    if reasons:
        msg = f"{path}: not a measurement under this rule ({'; '.join(reasons)}); measure the result again"
        raise RuntimeError(msg)
    return Measurement(tuple(float(x) for x in stored["spread_cm"]), tuple(stored["change"]), stored["record"])


def main(argv: list[str] | None = None) -> int:
    """Measure the own spread of a pipeline result with the networks its record names."""
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("result", type=Path, help="a pipeline result folder (pipeline.json, correction.npz, the B3LYP Hessian)")
    folder = ap.parse_args(argv).result.resolve()
    admission = json.loads((folder / "pipeline.json").read_text(encoding="utf-8"))["admission"]
    path = measure_result(tuple(Path(entry["path"]) for entry in admission["models"]), folder, admission["smiles"])
    print(f"[own spread] {path}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
