"""The molecule the pipeline works on, made from a request in one place (TASKS 278): every caller that names a molecule by its canonical
SMILES — the admission, the start geometry and the atom order the network reads, the corpus reuse, the 'seen' look-up, the catalogue —
goes through `standard_molecule`, so two writings of one molecule, or its SMILES and its xyz file, reach one canonical SMILES and one
atom order.

The steps are aromir's (`src/aromir/admission.py`, `standardised`, aromir commit 4d0461c of 19 Nov 2026), in the same order and with
the same ranking, so that the product and the capstone pipeline name every molecule alike. Each keeps every atom's index, so an xyz
file's coordinates still belong to its atoms:
1. **Atom-map numbers are cleared.** Reaction tools and many exports write them (`[CH3:5]c1ccc(O)cc1Cl`); RDKit's canonical ranking
   reads them, so they changed the atom order and made benzene 'unseen' (aromir audit of 19 Nov 2026, F1). They are no part of the
   molecule, so a mapped SMILES is accepted and the record says the numbers were cleared.
2. **RDKit's Normalizer** with its default (MolVS) transforms writes a hypervalent group the way bond perception from a geometry does:
   a sulfoxide `S=O` as `[S+][O-]`, a nitro group `N(=O)=O` as `[N+](=O)[O-]`. Called as in RDKit's
   `Code/GraphMol/MolStandardize/Wrap/testMolStandardize.py::test8Normalize` (`Normalizer().normalizeInPlace`).
3. **One resonance structure** for a molecule that still carries formal charges. Bond perception from a geometry places an azide's
   charges where it happens to (`N#[N+]N=c1cccc[cH-]1` for phenyl azide, F2), and RDKit leaves the tie between the azide's structures
   to the atom order. Every structure `Chem.ResonanceMolSupplier` enumerates (called as in RDKit's
   `Code/GraphMol/Wrap/rough_test.py::testResMolSupplier`) is ranked by `_preference`; the first one's bonds and charges are set on the
   molecule's own atoms and the stereo is assigned again, from the coordinates where there are any (`AssignStereochemistryFrom3D`, as
   in the same file's tests).

A sulfoxide's sulfur is a stereocentre: a SMILES without the mark leaves it open, a geometry has one configuration, and the name of an
xyz request says which, as aromir's does. The 'seen' look-up (`m08.seen`) then matches it without its stereo labels.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import Final

from rdkit import Chem, rdBase
from rdkit.Chem import rdDetermineBonds
from rdkit.Chem.MolStandardize import rdMolStandardize

ATOM_MAPS_CLEARED: Final = ("the input's atom-map numbers were cleared: they label atoms for reaction software and change neither the "
                            "molecule nor its spectrum")      # aromir's sentence, word for word
_NORMALIZER: Final = rdMolStandardize.Normalizer()            # RDKit's default (MolVS) transforms, built once


@dataclass(frozen=True)
class Standardised:
    """The molecule the pipeline works on (same atoms, same indices as the parsed input) and what reading it changed, for the record."""

    mol: Chem.Mol
    notes: tuple[str, ...]


def without_hydrogens(mol: Chem.Mol) -> Chem.Mol:
    """The heavy-atom skeleton. RDKit keeps a hydrogen that defines a double bond's stereo (an imine's N–H read from an xyz file); the
    skeleton has none."""
    parameters = Chem.RemoveHsParameters()
    parameters.removeDefiningBondStereo = True
    return Chem.RemoveHs(mol, parameters)


def canonical_of(mol: Chem.Mol) -> str:
    """The canonical SMILES of a standardised molecule: the name the pipeline gives it, and the order its atoms are read in."""
    return Chem.MolToSmiles(without_hydrogens(mol))


def _preference(form: Chem.Mol) -> tuple[int, int, int, str]:
    """A resonance structure's rank, smallest first: fewest charged atoms, then no negative charge on carbon, then negative charges on
    terminal atoms (the usual writing of an azide, a nitro group, an N-oxide); the canonical SMILES breaks a remaining tie, so the choice
    depends on the molecule alone, not on the order or the structure it was given in."""
    anions = [atom for atom in form.GetAtoms() if atom.GetFormalCharge() < 0]
    return (sum(atom.GetFormalCharge() != 0 for atom in form.GetAtoms()),
            sum(atom.GetAtomicNum() == 6 for atom in anions),
            sum(neighbour.GetAtomicNum() > 1 for atom in anions for neighbour in atom.GetNeighbors()),
            canonical_of(form))


def _one_resonance_structure(mol: Chem.Mol) -> None:
    """Give a charge-separated molecule, in place, its preferred resonance structure (`_preference`) on its own atoms."""
    forms = []
    for form in Chem.ResonanceMolSupplier(mol):
        Chem.SanitizeMol(form)
        forms.append(form)
    chosen = min(forms, key=_preference)
    Chem.Kekulize(chosen, clearAromaticFlags=True)
    Chem.Kekulize(mol, clearAromaticFlags=True)
    for atom in mol.GetAtoms():
        atom.SetFormalCharge(chosen.GetAtomWithIdx(atom.GetIdx()).GetFormalCharge())
    for bond in mol.GetBonds():
        bond.SetBondType(chosen.GetBondWithIdx(bond.GetIdx()).GetBondType())
    Chem.SanitizeMol(mol)
    if mol.GetNumConformers():
        Chem.AssignStereochemistryFrom3D(mol)
    else:
        Chem.AssignStereochemistry(mol, cleanIt=True, force=True)


def standard_molecule(mol: Chem.Mol) -> Standardised:
    """A parsed request with explicit hydrogens (a SMILES after AddHs, or an xyz file after bond perception) as the pipeline works on
    it: atom maps cleared, normalised, one resonance structure; every atom keeps its index."""
    standard = Chem.Mol(mol)
    mapped = any(atom.GetAtomMapNum() for atom in standard.GetAtoms())
    for atom in standard.GetAtoms():
        atom.SetAtomMapNum(0)
    _NORMALIZER.normalizeInPlace(standard)
    if any(atom.GetFormalCharge() for atom in standard.GetAtoms()):
        _one_resonance_structure(standard)
    return Standardised(standard, (ATOM_MAPS_CLEARED,) if mapped else ())


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
