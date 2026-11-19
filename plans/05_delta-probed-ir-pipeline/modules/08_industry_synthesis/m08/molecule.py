"""The molecule the pipeline works on, made from a request in one place (TASKS 278): every caller that names a molecule by its canonical
SMILES — the admission, the start geometry and the atom order the network reads, the corpus reuse, the 'seen' look-up, the catalogue —
goes through `standard_molecule`, so two writings of one molecule, or its SMILES and its xyz file, reach one canonical SMILES and one
atom order (aromir audit of 19 Nov 2026, F1 and F2).

The standardisation is aromir's, ported verbatim (`src/aromir/admission.py` at aromir commit 1636fde: `standardised`, `_composition`,
`_structure`, `_n_aromatic`, `_preference`, `_charge_placement`, `_canonical`, `_resonance_candidates`, `_set_structure`,
`_one_resonance_structure`, `fixed_h_key`), with the same constants, step order, ranking and guards, so that the product and the
capstone pipeline name every molecule alike. Change it there first and port it again. The upstream RDKit tests each call follows are
named where it is made.

A mapped SMILES is accepted: the map numbers are cleared and the admission says so (`ATOM_MAPS_CLEARED`). A sulfoxide's sulfur is a
stereocentre: a SMILES without the mark leaves it open, a geometry has one configuration, and the name of an xyz request says which, as
aromir's does; the 'seen' look-up (`m08.seen`) lets a training row without stereo marks cover every configuration.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import Any, Final

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


# ---------------------------------------------------------------------------------------------------- aromir 1636fde, verbatim
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
    ``RESONANCE_MAX_CHARGED_ATOMS`` charged atoms is not enumerated, and an enumeration
    that finds nothing or reaches ``RESONANCE_MAX_STRUCTURES`` (the choice would depend on
    which ones it found) keeps the molecule as it is: both bounds are counts, so the
    result does not depend on the machine. The supplier is built as in RDKit's
    ``Code/GraphMol/Wrap/rough_test.py`` (its resonance supplier tests).
    """
    n_charged = sum(atom.GetFormalCharge() != 0 for atom in molecule.GetAtoms())
    if n_charged > RESONANCE_MAX_CHARGED_ATOMS:
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
    """An xyz file as the pipeline's molecule, its bonds perceived from the geometry and its atoms in the file's order; None when it does
    not parse or no bonding pattern of that charge fits it."""
    mol = Chem.MolFromXYZFile(str(path))
    if mol is None:
        return None
    try:
        rdDetermineBonds.DetermineBonds(mol, charge=charge)
    except ValueError:
        return None
    return standard_molecule(mol)


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
