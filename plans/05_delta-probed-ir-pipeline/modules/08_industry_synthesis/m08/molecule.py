"""The molecule the pipeline works on, made from a request in one place (TASKS 278): every caller that names a molecule by its canonical
SMILES — the admission, the start geometry and the atom order the network reads, the corpus reuse, the 'seen' look-up, the catalogue —
goes through `standard_molecule`, so two writings of one molecule, or its SMILES and its xyz file, reach one canonical SMILES and one
atom order (aromir audit of 19 Nov 2026, F1 and F2).

The standardisation is aromir's, ported verbatim (`src/aromir/admission.py` at aromir commit 22016ea: `standardised`, `_composition`,
`_structure`, `_n_aromatic`, `_preference`, `_charge_placement`, `_canonical`, `_resonance_candidates`, `_set_structure`,
`_one_resonance_structure`, `fixed_h_key`), with the same constants, step order, ranking and guards, so that the product and the
capstone pipeline name every molecule alike. Change it there first and port it again. The upstream RDKit tests each call follows are
named where it is made.

An xyz file's bonds are perceived as aromir's are, ported verbatim from `src/aromir/admission.py` at aromir commit 52cf119
(`BOND_ORDER_ATTEMPTS`, `DIAGONAL_STRETCH`, `_distance`, `_longest_diagonal`, `perceive_connectivity`, `_stereo_from_coordinates`,
`_bond_orders`; TASKS 284): the connectivity from the distances, a ring's diagonals dropped, then the bond orders sought in a canonical atom
order, so that every listing of one geometry reads as one molecule. The one change is that the charge is passed on (aromir's is 0, as
the pipeline's admission still requires).

An optimised geometry's bonds are compared with the admitted SMILES's by aromir's `changed_bonds` (`src/aromir/geometry.py` at
aromir commit 52cf119, ported verbatim but for its arguments: module 08 has no Geometry class, and psi4 writes 'CL'; TASKS 279).

A mapped SMILES is accepted: the map numbers are cleared and the admission says so (`ATOM_MAPS_CLEARED`). A sulfoxide's sulfur is a
stereocentre: a SMILES without the mark leaves it open, a geometry has one configuration, and the name of an xyz request says which, as
aromir's does; the 'seen' look-up (`m08.seen`) lets a training row without stereo marks cover every configuration.
"""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import Any, Final

import numpy as np
from rdkit import Chem, rdBase
from rdkit.Chem import rdDetermineBonds
from rdkit.Chem.MolStandardize import rdMolStandardize
from rdkit.Chem.rdMolDescriptors import CalcMolFormula

ATOM_MAPS_CLEARED: Final = ("the input's atom-map numbers were cleared: they label atoms for reaction software and change neither the "
                            "molecule nor its spectrum")      # aromir's sentence, word for word


@dataclass(frozen=True)
class Standardised:
    """The molecule the pipeline works on (same atoms, same indices as the parsed input) and what reading it changed, for the record."""

    mol: Chem.Mol
    notes: tuple[str, ...]


def without_hydrogens(mol: Chem.Mol) -> Chem.Mol:
    """The heavy-atom skeleton. RDKit keeps a hydrogen that defines a double bond's stereo (an imine's N–H read from an xyz file); the
    skeleton has none."""
    parameters: Any = Chem.RemoveHsParameters()
    parameters.removeDefiningBondStereo = True
    return Chem.RemoveHs(mol, parameters)


def canonical_of(mol: Chem.Mol) -> str:
    """The canonical SMILES of a standardised molecule: the name the pipeline gives it, and the order its atoms are read in."""
    return Chem.MolToSmiles(without_hydrogens(mol))


# ---------------------------------------------------------------------------------------------------- aromir 52cf119, verbatim
BOND_ORDER_ATTEMPTS: Final = 16
"""The most atom orders bond orders are sought in (``_bond_orders``): a chosen bound, so a
geometry no neutral pattern fits is refused after a fixed amount of work."""


DIAGONAL_STRETCH: Final = 1.1
"""How much longer than every bond of its triangles a contact must be to count as a
ring's diagonal (``perceive_connectivity``): a chosen value between the two cases it
separates. A square's diagonal is √2 = 1.41 times its side, and a biphenylene's
four-membered ring (diagonals at 1.97 Å, sides up to about 1.51 Å) gives 1.3; in aromir's
force-field start geometries the bridgeheads of phenylbicyclo[1.1.1]pentane give 1.25, while the
central bond of phenylbicyclo[1.1.0]butane, a real bond whose two atoms also share two
neighbours, gives 1.03 (1.532 Å against wing bonds up to 1.490 Å)."""


def _distance(molecule: Chem.Mol, first: int, second: int) -> float:
    positions = molecule.GetConformer()
    return float((positions.GetAtomPosition(first) - positions.GetAtomPosition(second)).Length())


def _longest_diagonal(molecule: Chem.Mol) -> tuple[int, int] | None:
    """Return the longest contact that is a ring's diagonal, or None.

    A diagonal joins two atoms that share at least two bonded neighbours and is longer, by
    ``DIAGONAL_STRETCH``, than each bond from its two atoms to those neighbours.
    """
    neighbours = [
        {neighbour.GetIdx() for neighbour in atom.GetNeighbors()} for atom in molecule.GetAtoms()
    ]
    diagonals = []
    for bond in molecule.GetBonds():
        first, second = bond.GetBeginAtomIdx(), bond.GetEndAtomIdx()
        shared = neighbours[first] & neighbours[second]
        if len(shared) < 2:
            continue
        length = _distance(molecule, first, second)
        edges = [_distance(molecule, end, k) for k in shared for end in (first, second)]
        if length > DIAGONAL_STRETCH * max(edges):
            diagonals.append((length, first, second))
    if not diagonals:
        return None
    _, first, second = max(diagonals)
    return first, second


def perceive_connectivity(molecule: Chem.Mol) -> Chem.Mol:
    """Return a molecule with its bonds perceived from its coordinates, all of them single.

    RDKit's ``DetermineConnectivity`` bonds two atoms closer than the sum of their covalent
    radii and 0.45 Å; called as in RDKit's
    ``Code/GraphMol/DetermineBonds/Wrap/testDetermineBonds.py`` (``testCtDConnectivity``).
    That limit is 1.97 Å for two carbons, and the diagonals of a biphenylene's
    four-membered ring lie at 1.969 to 1.973 Å in the force-field geometries of v1.4's
    training biphenylenes. A diagonal (``_longest_diagonal``) is therefore dropped, the
    longest first and the neighbours counted again after each, so that a ring with both
    diagonals short loses those two and keeps its sides. A real bond between two atoms
    with two shared neighbours, as in a bicyclo[1.1.0]butane, is no longer than its
    neighbours' bonds and is kept.
    """
    perceived = Chem.RWMol(molecule)
    rdDetermineBonds.DetermineConnectivity(perceived)
    while (diagonal := _longest_diagonal(perceived)) is not None:
        perceived.RemoveBond(*diagonal)
    return perceived.GetMol()


def _stereo_from_coordinates(molecule: Chem.Mol) -> None:
    """Sanitise a molecule with bond orders and assign its stereo from its coordinates.

    What ``DetermineBondOrders`` does when it embeds the chirality (RDKit's
    ``Code/GraphMol/DetermineBonds/DetermineBonds.cpp``, ``setChirality``).
    """
    Chem.SanitizeMol(molecule)
    Chem.SetDoubleBondNeighborDirections(molecule, molecule.GetConformer())
    Chem.AssignStereochemistryFrom3D(molecule)


def _bond_orders(molecule: Chem.Mol, charge: int) -> Chem.Mol | None:
    """Perceive a molecule's bonds whatever order its atoms are listed in.

    ``DetermineBondOrders`` keeps the first valid structure of a maximum matching whose
    outcome follows the atom order, and does not try another matching: for one geometry
    of nitrobenzene it fails in 7 of 20 listings. So the connectivity, which depends on
    the distances alone, is perceived first (``perceive_connectivity``); the atoms are put
    in RDKit's canonical ranking of that graph and its elements, with ties broken, which
    gives every listing one graph in one order (atoms the graph cannot tell apart are
    interchangeable in it); and the bond orders are sought in that order and, while none
    is found, in its rotations by one atom, up to ``BOND_ORDER_ATTEMPTS``. The structure
    found is mapped back onto the listing's atoms. Called as in RDKit's
    ``Code/GraphMol/DetermineBonds/Wrap/testDetermineBonds.py`` (``DetermineConnectivity``,
    ``DetermineBondOrders``) and ``Code/GraphMol/Wrap/rough_test.py``
    (``CanonicalRankAtoms``, ``RenumberAtoms``).

    Returns:
        The molecule with its bonds, its atoms in the listing's order; None when no
        structure of that charge is found in any of the orders tried.
    """
    molecule = perceive_connectivity(molecule)
    n_atoms = molecule.GetNumAtoms()
    if n_atoms <= 1:
        return molecule
    molecule.UpdatePropertyCache(strict=False)
    ranks = list(Chem.CanonicalRankAtoms(molecule, breakTies=True, includeChirality=False))
    canonical = sorted(range(n_atoms), key=ranks.__getitem__)
    for shift in range(min(n_atoms, BOND_ORDER_ATTEMPTS)):
        order = canonical[shift:] + canonical[:shift]
        trial = Chem.RenumberAtoms(molecule, order)
        try:
            rdDetermineBonds.DetermineBondOrders(trial, charge=charge, embedChiral=False)
            back = Chem.RenumberAtoms(trial, sorted(range(n_atoms), key=order.__getitem__))
            _stereo_from_coordinates(back)
        except ValueError:  # no structure of that charge in this order, or one that does not sanitise
            continue
        return back
    return None


# ---------------------------------------------------------------------------------------------------- aromir 22016ea, verbatim
_NORMALIZER: Final = rdMolStandardize.Normalizer()
"""RDKit's Normalizer with its default (MolVS) transforms, built once."""

RESONANCE_MAX_STRUCTURES: Final = 256
"""The most resonance structures enumerated; a molecule with more keeps its own structure.
How many RDKit finds depends on the structure and atom order it starts from: 30 to 82 for
the writings and xyz listings of 3-phenylsydnone, so a cap of 64 left some unnamed."""

RESONANCE_FLAGS: Final = Chem.UNCONSTRAINED_ANIONS | Chem.UNCONSTRAINED_CATIONS
"""Let the enumeration move a charge onto any atom. By default RDKit keeps a negative charge
on the most electronegative atoms, so from the structure bond perception gives a pyridinium
methylide (``C=[N+]1C=CC=C[CH-]1``) or a diazo compound it finds no other, and from
``[N-]=[N+]=Cc1ccccc1`` none at all; ``_preference`` still puts carbanions last."""

RESONANCE_MAX_CHARGED_ATOMS: Final = 8
"""The most charged atoms a molecule may have to be enumerated; one with more keeps its own
structure. Twice the most in any entry of the shipped training lists (4, a dinitro
compound); octanitronaphthalene (16) took 6 s to reach the structure cap."""

NITRO_GROUP: Final = Chem.MolFromSmarts("[N+X3](=O)[O-]")
"""A nitro group as the Normalizer writes it. A molecule charged only in such groups is not
enumerated: no structure has fewer charged atoms (the nitrogen needs its positive charge for
its four bonds), one that moves a charge into the ring ranks worse (``_preference``), and the
group's two structures share one canonical SMILES, so the molecule's own structure is the
one chosen. Enumerated, nitro groups conjugated with a ring multiply the structures with
the writing deciding how many RDKit finds: 208 to 295 for 1,5-dinitronaphthalene over ten
writings, 1846 to 3041 for 1,8-dinitropyrene, 5924 to 9897 for 1,3,6-trinitropyrene."""

Composition = tuple[str, tuple[int, ...], tuple[int, ...]]
"""The formula and each atom's hydrogens and unpaired electrons: what no step may change."""


def _composition(molecule: Chem.Mol) -> Composition:
    atoms = list(molecule.GetAtoms())
    return (
        CalcMolFormula(molecule),
        tuple(atom.GetTotalNumHs(includeNeighbors=True) for atom in atoms),
        tuple(atom.GetNumRadicalElectrons() for atom in atoms),
    )


def _structure(molecule: Chem.Mol) -> tuple[tuple[int, ...], tuple[Any, ...]]:
    """Return each atom's formal charge and each bond's type: the Lewis structure."""
    return (
        tuple(atom.GetFormalCharge() for atom in molecule.GetAtoms()),
        tuple(bond.GetBondType() for bond in molecule.GetBonds()),
    )


def _n_aromatic(molecule: Chem.Mol) -> int:
    return sum(atom.GetIsAromatic() for atom in molecule.GetAtoms())


def _preference(form: Chem.Mol) -> tuple[int, int, int, int]:
    """Rank a resonance structure: the smallest key is preferred.

    Fewest charged atoms first, then no negative and then no positive charge on carbon
    (a pyridinium ylide is ``[CH2-][n+]1ccccc1``, not ``[CH2-]n1cccc[cH+]1``), then negative
    charges on terminal atoms (the usual writing of an azide, a nitro group, an N-oxide).
    """
    charged = [atom for atom in form.GetAtoms() if atom.GetFormalCharge()]
    anions = [atom for atom in charged if atom.GetFormalCharge() < 0]
    return (
        len(charged),
        sum(atom.GetAtomicNum() == 6 for atom in anions),
        sum(atom.GetAtomicNum() == 6 and atom.GetFormalCharge() > 0 for atom in charged),
        sum(neighbour.GetAtomicNum() > 1 for atom in anions for neighbour in atom.GetNeighbors()),
    )


def _charge_placement(form: Chem.Mol) -> tuple[tuple[int, int], ...]:
    """Return (atom index, formal charge) of the charged atoms: the last tie-break."""
    return tuple(
        (atom.GetIdx(), atom.GetFormalCharge())
        for atom in form.GetAtoms()
        if atom.GetFormalCharge()
    )


def _canonical(form: Chem.Mol) -> str:
    """Return a structure's canonical SMILES without stereo: what tells structures apart."""
    return str(Chem.MolToSmiles(without_hydrogens(form), isomericSmiles=False))


def _resonance_candidates(molecule: Chem.Mol) -> list[Chem.Mol]:
    """Return the resonance structures that may replace a molecule's own; none to keep it.

    A structure qualifies when it sanitises, keeps the formula and every atom's hydrogens
    and unpaired electrons, and keeps at least as many aromatic atoms as the molecule
    (a betaine is not swapped for its quinoid form). A molecule with more than
    ``RESONANCE_MAX_CHARGED_ATOMS`` charged atoms is not enumerated, nor one charged only in
    nitro groups (``NITRO_GROUP``), and an enumeration
    that finds nothing or reaches ``RESONANCE_MAX_STRUCTURES`` (the choice would depend on
    which ones it found) keeps the molecule as it is: both bounds are counts, so the
    result does not depend on the machine. The supplier is built as in RDKit's
    ``Code/GraphMol/Wrap/rough_test.py`` (its resonance supplier tests).
    """
    charged = {atom.GetIdx() for atom in molecule.GetAtoms() if atom.GetFormalCharge()}
    if len(charged) > RESONANCE_MAX_CHARGED_ATOMS:
        return []
    in_nitro = {index for match in molecule.GetSubstructMatches(NITRO_GROUP) for index in match}
    if charged <= in_nitro:
        return []
    supplier = Chem.ResonanceMolSupplier(molecule, RESONANCE_FLAGS, RESONANCE_MAX_STRUCTURES)
    supplier.Enumerate()
    if not 0 < len(supplier) < RESONANCE_MAX_STRUCTURES:
        return []
    composition, n_aromatic = _composition(molecule), _n_aromatic(molecule)
    candidates = []
    for form in supplier:
        if form is None or Chem.SanitizeMol(form, catchErrors=True) != Chem.SANITIZE_NONE:
            continue
        if _composition(form) == composition and _n_aromatic(form) >= n_aromatic:
            candidates.append(form)
    return candidates


def _set_structure(molecule: Chem.Mol, form: Chem.Mol) -> None:
    """Give a molecule, in place, the bonds and charges of one of its resonance structures.

    The molecule's own atoms are kept, so an xyz file's coordinates still belong to them;
    the stereo is assigned again, from the coordinates where there are any, as in RDKit's
    ``Code/GraphMol/Wrap/rough_test.py`` (``AssignStereochemistryFrom3D``).
    """
    chosen = Chem.Mol(form)
    Chem.Kekulize(chosen, clearAromaticFlags=True)
    Chem.Kekulize(molecule, clearAromaticFlags=True)
    for atom in molecule.GetAtoms():
        atom.SetFormalCharge(chosen.GetAtomWithIdx(atom.GetIdx()).GetFormalCharge())
    for bond in molecule.GetBonds():
        bond.SetBondType(chosen.GetBondWithIdx(bond.GetIdx()).GetBondType())
    Chem.SanitizeMol(molecule)
    if molecule.GetNumConformers():
        Chem.AssignStereochemistryFrom3D(molecule)
    else:
        Chem.AssignStereochemistry(molecule, cleanIt=True, force=True)


def _one_resonance_structure(molecule: Chem.Mol) -> None:
    """Give a charge-separated molecule, in place, its preferred resonance structure.

    Bond perception from a geometry places the charges of an azide where it happens to
    (``N#[N+][N-]R`` or ``N#[N+]N=c1cccc[cH-]1`` for ``[N-]=[N+]=NR``). Among the
    candidates (``_resonance_candidates``) and the molecule itself, those with the smallest
    ``_preference`` tie; of them the one with the smallest canonical SMILES is taken, so
    two writings of a sydnone get one name. The molecule keeps its own bonds and charges
    when it is one of those (a nitro group keeps its charge on the oxygen it was given);
    otherwise a remaining tie is broken by ``_charge_placement``.
    """
    candidates = _resonance_candidates(molecule)
    if not candidates:
        return
    own = _preference(molecule)
    best = min(*map(_preference, candidates), own)
    tied = [form for form in candidates if _preference(form) == best]
    chosen = min(
        [_canonical(form) for form in tied] + ([_canonical(molecule)] if own == best else [])
    )
    if own == best and _canonical(molecule) == chosen:
        return
    named = (form for form in tied if _canonical(form) == chosen)
    _set_structure(molecule, min(named, key=_charge_placement))


def standardised(molecule: Chem.Mol) -> Chem.Mol:
    """Return a molecule in the package's standard form: one Lewis structure, no atom maps.

    The network reads the atoms in the order of the canonical SMILES, and the 'seen'
    look-up compares canonical SMILES, so one molecule should have one canonical SMILES
    however it was written. Atom indices and coordinates are kept throughout.

    1. Atom-map numbers are cleared: RDKit's canonical ranking reads them, so a mapped
       SMILES would be numbered and named as another molecule.
    2. Every atom's hydrogen count is fixed (``SetNoImplicit``) while the bonds change, so
       a step that lowers a bond order cannot add a hydrogen.
    3. RDKit's Normalizer (the MolVS transforms) writes a hypervalent group the way bond
       perception from a geometry does: a sulfoxide ``S=O`` as ``[S+][O-]``, a nitro group
       ``N(=O)=O`` as ``[N+](=O)[O-]``. Called as in RDKit's
       ``Code/GraphMol/MolStandardize/Wrap/testMolStandardize.py``.
    4. A molecule that still carries formal charges gets its preferred resonance structure
       (``_one_resonance_structure``). A molecule without charges is left as it is: its
       Kekulé structures are one aromatic structure to RDKit already.

    A step whose result has another formula, or another hydrogen count or unpaired
    electron on any atom, is discarded: the molecule keeps its given structure.
    """
    given = Chem.Mol(molecule)
    for atom in given.GetAtoms():
        atom.SetAtomMapNum(0)
    composition = _composition(given)
    standard = Chem.Mol(given)
    for atom in standard.GetAtoms():
        atom.SetNoImplicit(True)
    fixed = Chem.Mol(standard)
    _NORMALIZER.normalizeInPlace(standard)
    # normalizeInPlace may leave a molecule that does not sanitise (RDKit's own
    # MolStandardize/Pipeline.cpp checks for it), as on a sydnone read from an xyz file.
    if (
        Chem.SanitizeMol(standard, catchErrors=True) != Chem.SANITIZE_NONE
        or _composition(standard) != composition
    ):
        standard = fixed
    if any(atom.GetFormalCharge() for atom in standard.GetAtoms()):
        _one_resonance_structure(standard)
    if _structure(standard) == _structure(given):
        return given  # untouched: the Normalizer may still have rewritten its stereo marks
    for atom in standard.GetAtoms():
        atom.SetNoImplicit(given.GetAtomWithIdx(atom.GetIdx()).GetNoImplicit())
    standard.UpdatePropertyCache(strict=False)
    return standard if _composition(standard) == composition else given


FIXED_H_OPTIONS: Final = "/FixedH"
"""InChI's fixed-hydrogen layer: the key keeps tautomers apart (2-pyridone is not
2-hydroxypyridine) while staying the same for every resonance structure."""


@cache
def fixed_h_key(smiles: str) -> str | None:
    """Return a SMILES's InChIKey with the fixed-hydrogen layer; None where InChI makes none.

    The second key of the 'seen' look-up: a molecule whose standard form still depends on
    how it was given (one past the resonance step's bounds) is found by it. RDKit
    hands ``options`` to InChI as its command-line options; ``/FixedH`` is used so in RDKit's
    ``rdkit/Chem/UnitTestInchi.py`` and, for the key, ``Code/PgSQL/rdkit/sql/inchi.sql``.
    """
    molecule: Chem.Mol | None = Chem.MolFromSmiles(smiles)
    if molecule is None:
        return None
    with rdBase.BlockLogs():  # InChI's warnings (undefined stereo) are no message to the user
        key = str(Chem.MolToInchiKey(molecule, options=FIXED_H_OPTIONS))
    return key or None
# ---------------------------------------------------------------------------------------------------- end of the port


def standard_molecule(mol: Chem.Mol) -> Standardised:
    """A parsed request with explicit hydrogens (a SMILES after AddHs, or an xyz file after bond perception) as the pipeline works on
    it (`standardised`), and whether its atom-map numbers were cleared; every atom keeps its index."""
    mapped = any(atom.GetAtomMapNum() for atom in mol.GetAtoms())
    return Standardised(standardised(mol), (ATOM_MAPS_CLEARED,) if mapped else ())


def from_smiles(smiles: str | None) -> Standardised | None:
    """A SMILES as the pipeline's molecule, with explicit hydrogens; None when it is empty or does not parse."""
    if not smiles:
        return None
    with rdBase.BlockLogs():           # an unparsable request is answered by None, not by RDKit's log (rough_test.py::test_blocklogs)
        mol = Chem.MolFromSmiles(smiles)
    return None if mol is None else standard_molecule(Chem.AddHs(mol))


def from_xyz(path: Path, charge: int) -> Standardised | None:
    """An xyz file as the pipeline's molecule, its bonds perceived from the geometry whatever order the file lists its atoms in
    (`_bond_orders`) and its atoms in the file's order; None when it does not parse or no bonding pattern of that charge fits it."""
    mol = Chem.MolFromXYZFile(str(path))
    if mol is None:
        return None
    bonded = _bond_orders(mol, charge)
    return None if bonded is None else standard_molecule(bonded)


# ---------------------------------------------------------------------------------------------------- aromir 52cf119 geometry.py, verbatim
def _pairs(molecule: Chem.Mol) -> set[tuple[int, int]]:
    pairs = set()
    for bond in molecule.GetBonds():
        first, second = sorted((bond.GetBeginAtomIdx(), bond.GetEndAtomIdx()))
        pairs.add((first, second))
    return pairs


def changed_bonds(admitted_smiles: str, symbols: Sequence[str], coords_angstrom: np.ndarray) -> list[str]:
    """Name the bonds a geometry in the canonical order has formed or broken.

    The admitted molecule's bonds are read from its canonical SMILES, whose atoms with
    their hydrogens added are in the canonical order (``start_geometry``); the
    geometry's are perceived from its interatomic distances with RDKit's
    ``DetermineConnectivity``, called as in RDKit's
    ``Code/GraphMol/DetermineBonds/Wrap/testDetermineBonds.py`` (``testCtDConnectivity``,
    which compares the bonds so perceived on a geometry with those of its SMILES). An
    optimisation that moved a proton, opened a ring or joined two atoms has computed
    another molecule than the one admitted.

    The contacts are judged against the SMILES's bonds, which are known here: a contact
    that is no bond of the SMILES is not called a bond formed when its two atoms share two
    neighbours in the SMILES, as the diagonals of a biphenylene's four-membered ring
    (1.969 to 1.973 Å in the force-field geometries of v1.4's training biphenylenes,
    against 1.97 Å for two carbons) or the bridgeheads of a bicyclo[1.1.1]pentane do. A bond
    of the SMILES is kept whatever its neighbours.

    Raises:
        ValueError: The geometry's atoms are not the SMILES's, in its order.
    """
    admitted = Chem.AddHs(Chem.MolFromSmiles(admitted_smiles))
    elements = tuple(symbol.capitalize() for symbol in symbols)  # psi4's geometry files write 'CL'
    if tuple(atom.GetSymbol() for atom in admitted.GetAtoms()) != elements:
        msg = f"the geometry's atoms {elements} are not those of {admitted_smiles}"
        raise ValueError(msg)
    rows = [
        f"{s} {x:.10f} {y:.10f} {z:.10f}"
        for s, (x, y, z) in zip(elements, coords_angstrom, strict=True)
    ]
    perceived = Chem.MolFromXYZBlock("\n".join([str(len(elements)), "", *rows]) + "\n")
    rdDetermineBonds.DetermineConnectivity(perceived)
    expected, found = _pairs(admitted), _pairs(perceived)
    neighbours = [
        {neighbour.GetIdx() for neighbour in atom.GetNeighbors()} for atom in admitted.GetAtoms()
    ]
    formed = [
        (first, second)
        for first, second in sorted(found - expected)
        if len(neighbours[first] & neighbours[second]) < 2
    ]

    def named(pair: tuple[int, int]) -> str:
        return "–".join(f"{elements[k]}{k + 1}" for k in pair)

    return [f"the bond {named(pair)} broke" for pair in sorted(expected - found)] + [
        f"a bond {named(pair)} formed" for pair in formed
    ]
# ---------------------------------------------------------------------------------------------------- end of the port


@cache
def canonical(smiles: str | None) -> str | None:
    """The canonical SMILES of the pipeline's molecule — the one key every look-up compares — or None when the SMILES does not parse."""
    got = from_smiles(smiles)
    return None if got is None else canonical_of(got.mol)


def without_stereo(smiles: str) -> str:
    """A canonical SMILES without its stereo labels."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"{smiles!r} does not parse as a SMILES")
    return Chem.MolToSmiles(mol, isomericSmiles=False)
