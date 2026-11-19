"""Two features of a molecule that the network's training molecules may lack (TASKS 279), ported verbatim from aromir's
`src/aromir/domain.py` at aromir commit 52cf119; change it there first and port it again.

Admission takes any neutral, closed-shell aromatic molecule of the supported elements. Two
things about it are compared with the release's training list: its kinds of charged atom
(v1.4's list holds those of nitro groups and of one aromatic N-oxide) and the sizes of its
rings of aromatic atoms (v1.4's: 4, 5, 6 and 7). A molecule with a kind or a size the list
lacks is computed and printed, and named as outside the training chemistry; no band of it
is licensed, as for a molecule outside the training sizes. Nothing else about the chemistry
is compared. What counts as inside is read from the release's own list, not from a
hand-kept one, so a release trained on more admits more.

In module 08 the training list is that of the networks that run: the canonical SMILES of the neutral molecules their checkpoints
fitted or stopped on (`m08.seen.trained_smiles`), in the standard form `m08.molecule` writes.
"""

from __future__ import annotations

from collections.abc import Iterable
from functools import cache
from typing import Any, Final

from rdkit import Chem

OUTSIDE_SIZES: Final = "the molecule is outside the training sizes"
"""aromir's `certificate.OUTSIDE_SIZES`, word for word: each band's licence note for a molecule outside the training sizes."""
OUTSIDE_CHEMISTRY: Final = "the molecule holds chemistry no training molecule does"
"""aromir's `certificate.OUTSIDE_CHEMISTRY`, word for word: each band's licence note for a molecule outside the training chemistry."""


def domain_note(*, inside_training_sizes: bool, outside_chemistry: tuple[str, ...]) -> str:
    """Say why a molecule lies outside the training domain; "" when inside (aromir's `certificate.domain_note`: the sizes first)."""
    if not inside_training_sizes:
        return OUTSIDE_SIZES
    if outside_chemistry:
        return OUTSIDE_CHEMISTRY
    return ""

ChargeSite = tuple[str, int, bool, int, tuple[tuple[str, int, str], ...]]
"""A charged atom's kind: its element, formal charge, aromaticity and hydrogens, and each
neighbour's element and formal charge with the type of the bond to it."""

Shown = tuple[int, str]
"""How a kind is shown: minus the aromatic atoms of a fragment SMILES, and the fragment."""


def _molecule(smiles: str) -> Chem.Mol:
    molecule: Chem.Mol | None = Chem.MolFromSmiles(smiles)  # RDKit's stubs omit the None
    if molecule is None:
        msg = f"{smiles!r} does not parse as a SMILES"
        raise ValueError(msg)
    return molecule


def _site(atom: Any) -> ChargeSite:  # an RDKit atom
    molecule = atom.GetOwningMol()
    neighbours = sorted(
        (
            neighbour.GetSymbol(),
            neighbour.GetFormalCharge(),
            str(molecule.GetBondBetweenAtoms(atom.GetIdx(), neighbour.GetIdx()).GetBondType()),
        )
        for neighbour in atom.GetNeighbors()
    )
    return (
        atom.GetSymbol(),
        atom.GetFormalCharge(),
        atom.GetIsAromatic(),
        atom.GetTotalNumHs(),
        tuple(neighbours),
    )


def _shown_sites(smiles: str) -> dict[ChargeSite, Shown]:
    """Return each kind of charged atom with the fragment that shows it best.

    The fragment is the charged atom with its neighbours. Of the atoms of one kind the one
    with the most aromatic atoms in its fragment is shown, so a nitro group on a ring reads
    ``c[N+](=O)[O-]``, and of those the smallest fragment, so the choice does not follow
    the order of the atoms or of the list.
    """
    molecule = _molecule(smiles)
    sites: dict[ChargeSite, Shown] = {}
    for atom in molecule.GetAtoms():
        if atom.GetFormalCharge():
            used = [atom, *atom.GetNeighbors()]
            fragment = str(
                Chem.MolFragmentToSmiles(molecule, atomsToUse=[a.GetIdx() for a in used])
            )
            shown = (-sum(a.GetIsAromatic() for a in used), fragment)
            site = _site(atom)
            sites[site] = min(sites.get(site, shown), shown)
    return sites


def charge_sites(smiles: str) -> dict[ChargeSite, str]:
    """Return each kind of charged atom a SMILES holds, with a fragment SMILES that shows it.

    Raises:
        ValueError: The string does not parse as a SMILES.
    """
    return {site: fragment for site, (_, fragment) in _shown_sites(smiles).items()}


def aromatic_ring_sizes(smiles: str) -> frozenset[int]:
    """Return the sizes of the rings of a SMILES's smallest set whose atoms are all aromatic.

    The atoms, not the bonds, decide: RDKit writes the bond azulene's two rings share, and
    the bonds of a biphenylene's four-membered ring, as single bonds between aromatic atoms.

    Raises:
        ValueError: The string does not parse as a SMILES.
    """
    molecule = _molecule(smiles)
    return frozenset(
        len(ring)
        for ring in molecule.GetRingInfo().AtomRings()
        if all(molecule.GetAtomWithIdx(atom).GetIsAromatic() for atom in ring)
    )


@cache
def _training_chemistry(trained: tuple[str, ...]) -> tuple[dict[ChargeSite, Shown], frozenset[int]]:
    sites: dict[ChargeSite, Shown] = {}
    sizes: set[int] = set()
    for smiles in trained:
        for site, shown in _shown_sites(smiles).items():
            sites[site] = min(sites.get(site, shown), shown)
        sizes |= aromatic_ring_sizes(smiles)
    return sites, frozenset(sizes)


def outside_training_chemistry(smiles: str, trained: Iterable[str]) -> tuple[str, ...]:
    """Name what a molecule holds that no training molecule does, one sentence per feature.

    Two features are compared: a charged atom whose element, charge, aromaticity,
    hydrogens and bonded neighbours no training molecule's charged atom shares (the
    charge separation of a zwitterion, an azide, an ylide or a sulfoxide in a release
    trained on nitro groups alone), and a ring of aromatic atoms of a size no training
    molecule has. Both the molecule and the training list are read from SMILES in the
    standard form admission writes.

    Raises:
        ValueError: A string does not parse as a SMILES.
    """
    known_sites, known_sizes = _training_chemistry(tuple(trained))
    caveats = []
    unseen = sorted(
        {fragment for site, fragment in charge_sites(smiles).items() if site not in known_sites}
    )
    if unseen:
        held = ", ".join(sorted({fragment for _, fragment in known_sites.values()})) or "none"
        caveats.append(
            f"charge separation of a kind no training molecule holds: {', '.join(unseen)} "
            f"(the charged atoms of the training molecules: {held})"
        )
    sizes = sorted(aromatic_ring_sizes(smiles) - known_sizes)
    if sizes:
        held_sizes = ", ".join(str(size) for size in sorted(known_sizes)) or "none"
        caveats.append(
            f"an aromatic ring of {' and '.join(str(size) for size in sizes)} atoms, a size no "
            f"training molecule has (theirs: {held_sizes})"
        )
    return tuple(caveats)
