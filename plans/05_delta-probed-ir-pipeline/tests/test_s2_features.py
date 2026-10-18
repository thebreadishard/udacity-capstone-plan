"""probes/s2_features.py: bonds and rings from a geometry, the C–H adjacency classes, the kinetic-energy shares, and resonance proximity
from ω alone — on RDKit geometries of molecules whose classes are known."""
import sys
from pathlib import Path

import numpy as np
import pytest

PLAN = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PLAN / "probes"))
import s2_features as S  # noqa: E402

rdkit = pytest.importorskip("rdkit")
from rdkit import Chem  # noqa: E402
from rdkit.Chem import AllChem  # noqa: E402


def geometry(smiles):
    m = Chem.AddHs(Chem.MolFromSmiles(smiles))
    AllChem.EmbedMolecule(m, randomSeed=7)
    AllChem.MMFFOptimizeMolecule(m)
    return [a.GetSymbol() for a in m.GetAtoms()], m.GetConformer().GetPositions() * S.BOHR_PER_ANGSTROM


def classes(smiles):
    sym, x = geometry(smiles)
    bl = S.bonds(sym, x)
    rings = S.ring_counts(len(sym), bl)
    cls = S.hydrogen_classes(sym, bl, rings)
    return sym, rings, sorted(int(c) for c in cls[np.array(sym) == "H"])


def test_adjacency_classes_of_known_molecules():
    assert classes("c1ccc2ccccc2c1")[2] == [4] * 8                       # naphthalene: two quartets
    assert classes("c1ccccc1")[2] == [5] * 6                             # benzene: a sextet, capped at 5
    assert classes("c1ccc2c(c1)ccc1ccccc12")[2] == [2] * 2 + [4] * 8      # phenanthrene: one duo, two quartets
    assert classes("C#Cc1ccccc1")[2] == [0] + [5] * 5                    # phenylacetylene: the ≡C–H is on no ring carbon


def test_fusion_atoms_are_in_two_rings():
    _sym, rings, _ = classes("c1ccc2ccccc2c1")
    assert int((rings >= 2).sum()) == 2 and int((rings == 1).sum()) == 8


def test_shares_sum_to_one_and_follow_the_moving_atom():
    sym, x = geometry("Nc1ccccc1")                                       # aniline
    n = len(sym)
    h_on_n = next(i for i, s in enumerate(sym) if s == "H" and np.linalg.norm(x[i] - x[0]) < 1.2 * S.BOHR_PER_ANGSTROM)
    q = np.zeros((3 * n, 2))
    q[3 * h_on_n, 0] = 1.0                                               # mode 0: a hydrogen of the NH2
    q[3 * 1 + 2, 1] = 1.0                                                # mode 1: the ring carbon bonded to N
    f = S.local_environment(q, sym, x)
    col = dict(zip(S.LOCAL_NAMES, f.T, strict=True))
    assert col["h_class_0"][0] == pytest.approx(1.0) and col["hetero"][0] == pytest.approx(1.0) and col["substituent"][0] == pytest.approx(1.0)
    assert col["hetero"][1] == 0.0 and col["substituent"][1] == 0.0 and col["fusion"][1] == 0.0
    assert np.allclose(f[:, :len(S.ADJACENCY_CLASSES)].sum(axis=1), [1.0, 0.0])


def test_resonance_proximity_from_omega():
    p = S.resonance_proximity([500.0, 1003.0, 1600.0, 2100.0])
    assert p[1, 0] == pytest.approx(np.log10(1 + 3.0))                  # 2·500 vs 1003
    assert p[3, 1] == pytest.approx(np.log10(1 + 0.0))                  # 500 + 1600 = 2100
