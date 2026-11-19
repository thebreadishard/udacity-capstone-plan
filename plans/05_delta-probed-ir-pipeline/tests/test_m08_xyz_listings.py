"""An xyz request reads as one molecule whatever order its file lists the atoms in (`modules/08_industry_synthesis/m08/molecule.py`,
TASKS 284; aromir's `tests/test_admission.py` at commit 52cf119): nitro compounds that RDKit's plain `DetermineBonds` refused in some
listings, the training biphenylenes whose four-membered ring's diagonals lie at RDKit's bonding limit, and small rings whose real bonds
join atoms with two shared neighbours."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest
from rdkit import Chem
from rdkit.Chem import rdDetermineBonds

from pin_tools import DATA, PLAN

sys.path.insert(0, str(PLAN / "modules" / "08_industry_synthesis"))
from m08 import molecule as M
from m08 import pipeline as P
from m08 import seen as S

PIN_MODEL = DATA / "rungC_cc_pin_model.pt"
TRAINING = (("C", "CL", "F", "H", "N", "O", "S"), (6, 40))
N_LISTINGS = 20
SCALE = 0.995                      # aromir's `distorted`: the diagonals on both sides of RDKit's 1.97 Å limit for two carbons
NOISE_ANGSTROM = 0.02
N_NOISY = 5

LISTING_FREE = [
    "O=[N+]([O-])c1ccccc1",
    "O=[N+]([O-])c1cccc([N+](=O)[O-])c1",
    "O=[N+]([O-])c1ccc2ccccc2c1",
    "Nc1ccc([N+](=O)[O-])cc1",
    "[N-]=[N+]=Nc1ccccc1",
    "[O-][n+]1ccccc1",
    "N#Cc1ccccc1",
]
"""aromir's list: nitro compounds RDKit's DetermineBonds refused in some listings, and three that it did not."""

TRAINING_BIPHENYLENES = (
    "C#Cc1cccc2c1-c1ccccc1-2",
    "COc1cccc2c1-c1ccccc1-2",
    "Cc1ccc2c(c1)-c1ccccc1-2",
    "FC(F)(F)c1ccc2c(c1)-c1ccccc1-2",
    "N#Cc1cccc2c1-c1ccccc1-2",
    "O=Cc1cccc2c1-c1ccccc1-2",
    "O=[N+]([O-])c1cccc2c1-c1ccccc1-2",
    "Oc1ccc2c(c1)-c1ccccc1-2",
    "c1ccc2c(c1)-c1ccccc1-2",
)
"""The carried release networks' training molecules with a ring of four aromatic atoms (`seen.release_index` of v1.4's release networks,
19 Nov 2026; `test_the_biphenylenes_are_the_release_networks` checks the list where the checkpoints are present)."""

SMALL_RINGS = (
    "c1ccc(cc1)C12CC1C2",
    "c1ccc(cc1)C12C(C)(C)C1C2",
    "c1ccc(cc1)C12C3C4C1C5C2C3C45",
    "c1ccc(cc1)C12CC(C1)C2",
)
"""aromir's: phenylbicyclo[1.1.0]butane and its 2,2-dimethyl analogue, whose central bond joins two atoms that share two neighbours;
phenylcubane; and phenylbicyclo[1.1.1]pentane, whose bridgeheads share three neighbours and lie within bonding distance."""


@pytest.fixture
def pin_registry(monkeypatch):
    """The pin model counts as carried and the training set holds S, F and Cl, so the routes are compared without the registry."""
    monkeypatch.setattr(P.MR, "require_carried", lambda p, kind=None: {"status": "carried", "network": P.NETWORK, "version": "pin"})
    monkeypatch.setattr(P, "training_set", lambda models: TRAINING)


def config(tmp_path: Path, **kw) -> P.PipelineConfig:
    base = dict(name="mol", out_root=tmp_path, smiles="c1ccccc1", models=(PIN_MODEL,), psi4_python=Path(sys.executable))
    return P.PipelineConfig(**(base | kw))


def listed_xyz(path: Path, atoms: list[list], seed: int) -> Path:
    """An xyz file of atoms as [symbol, x, y, z] in Å, listed in a random order."""
    order = np.random.default_rng(seed).permutation(len(atoms))
    rows = [f"{atoms[k][0]} {atoms[k][1]:.8f} {atoms[k][2]:.8f} {atoms[k][3]:.8f}" for k in order]
    path.write_text(f"{len(rows)}\nlisted\n" + "\n".join(rows) + "\n", encoding="utf-8")
    return path


def distorted(atoms: list[list]) -> list[list[list]]:
    """aromir's `distorted`: a start geometry as it is, scaled by `SCALE` and with `NOISE_ANGSTROM` of noise (`N_NOISY` seeds)."""
    xyz = np.array([row[1:] for row in atoms], float)
    symbols = [row[0] for row in atoms]
    variants = [xyz, xyz * SCALE] + [xyz + np.random.default_rng(seed).normal(scale=NOISE_ANGSTROM, size=xyz.shape)
                                     for seed in range(N_NOISY)]
    return [[[s, *map(float, r)] for s, r in zip(symbols, v, strict=True)] for v in variants]


def read_as_listed(tmp_path: Path, variants: list[list[list]]) -> set[str]:
    """The names, without stereo labels, the pipeline's admission gives geometries read as xyz files, each in another listing."""
    return {M.without_stereo(P.admit(config(tmp_path, smiles=None, xyz=listed_xyz(tmp_path / f"{k}.xyz", atoms, k))).smiles)
            for k, atoms in enumerate(variants)}


@pytest.mark.parametrize("smiles", LISTING_FREE)
def test_every_listing_of_an_xyz_file_is_admitted_under_one_name(tmp_path, pin_registry, smiles):
    named = P.admit(config(tmp_path, smiles=smiles)).smiles
    made, _ = P.start_geometry(config(tmp_path, smiles=smiles))
    names = {P.admit(config(tmp_path, smiles=None, xyz=listed_xyz(tmp_path / f"{seed}.xyz", made, seed))).smiles
             for seed in range(N_LISTINGS)}
    assert names == {named}


def test_the_listings_of_nitrobenzene_include_some_the_plain_call_refuses(tmp_path):
    """What the test above holds: bond orders sought in the file's own order fail for some listings of nitrobenzene."""
    made, _ = P.start_geometry(config(tmp_path, smiles="O=[N+]([O-])c1ccccc1"))
    refused = 0
    for seed in range(N_LISTINGS):
        molecule = Chem.MolFromXYZFile(str(listed_xyz(tmp_path / "n.xyz", made, seed)))
        try:
            rdDetermineBonds.DetermineBonds(molecule, charge=0)
        except ValueError:
            refused += 1
    assert refused > 0


def test_every_training_biphenylene_is_read_with_its_four_membered_ring(tmp_path, pin_registry):
    for smiles in TRAINING_BIPHENYLENES:
        made, _ = P.start_geometry(config(tmp_path, smiles=smiles))
        assert read_as_listed(tmp_path, distorted(made)) == {M.without_stereo(smiles)}, smiles


@pytest.mark.parametrize("smiles", SMALL_RINGS)
def test_a_small_ring_is_read_from_an_xyz_file_as_its_smiles(tmp_path, pin_registry, smiles):
    named = P.admit(config(tmp_path, smiles=smiles)).smiles
    made, _ = P.start_geometry(config(tmp_path, smiles=smiles))
    assert read_as_listed(tmp_path, distorted(made)) == {M.without_stereo(named)}


def test_the_biphenylenes_are_the_release_networks():
    models = P.carried_models(P.NK.RELEASE)
    if not models or not all(p.is_file() for p in models):
        pytest.skip("the carried release networks' checkpoints are not on this machine")
    four = Chem.MolFromSmarts("a1aaa1")
    trained = S.release_index(models).trained
    assert tuple(sorted(s for s in trained if Chem.MolFromSmiles(s).HasSubstructMatch(four))) == TRAINING_BIPHENYLENES


def test_no_bonding_pattern_in_any_order_is_no_molecule(tmp_path, pin_registry, monkeypatch):
    tried = []

    def never(mol, charge, embedChiral):
        tried.append(charge)
        raise ValueError("could not find valid bond ordering")

    made, _ = P.start_geometry(config(tmp_path))
    xyz = listed_xyz(tmp_path / "r.xyz", made, 0)
    monkeypatch.setattr(rdDetermineBonds, "DetermineBondOrders", never)
    assert M.from_xyz(xyz, 0) is None
    assert tried == [0] * min(len(made), M.BOND_ORDER_ATTEMPTS)
    with pytest.raises(P.Refused, match="does not parse"):
        P.admit(config(tmp_path, smiles=None, xyz=xyz))
