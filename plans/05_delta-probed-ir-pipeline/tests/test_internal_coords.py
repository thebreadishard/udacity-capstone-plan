"""v1.5's primitive switches (TASKS 149, `m05/internal_coords.py`): the canonical angle choice makes the primitives and the pair features
independent of the atom order, the cos encoding makes a dihedral's feature continuous across ±π, and the defaults are the carried recipe.

On the frozen corpus: B_0da4a5aea1 has no topological symmetry (every canonical rank distinct), so its canonical build is the same to the
last bit in every order. Phenanthrene (C2v; half of its 64 dihedrals at ±π) has symmetry-equivalent atoms, and the canonical tie-break can
pick a symmetry image: other primitive labels, the same features as a set — but only under `cos`, because a raw dihedral at ±π changes
sign between mirror images (1 Nov 2026: 12.6 = 4π in a sum feature)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest

from pin_tools import M05, PIN_CORPUS

sys.path.insert(0, str(M05))
import e7_rungB_pairs as RB
import e7_t2_sqm as T2
import internal_coords as IC

ASYMMETRIC = PIN_CORPUS / "molecules" / "B_0da4a5aea1"
PHENANTHRENE = PIN_CORPUS / "molecules" / "A_541c53d1a5"
CANONICAL = IC.PrimitiveSettings(angle_choice="canonical")
CANONICAL_COS = IC.PrimitiveSettings(angle_choice="canonical", dihedral_encoding="cos")
NOISE_BOHR = 1e-4
ORDERS = 4


def load(folder: Path, hessian: str) -> tuple[list[str], np.ndarray, np.ndarray]:
    g = json.loads((folder / "geometry.json").read_text(encoding="utf-8"))
    with np.load(folder / hessian) as z:
        H = np.asarray(z["H_projected"], float)
    return list(g["symbols"]), np.asarray(g["coords_bohr"], float), H


@pytest.fixture(scope="module")
def asymmetric() -> tuple[list[str], np.ndarray, np.ndarray]:
    return load(ASYMMETRIC, "hessian_b3lyp.npz")


@pytest.fixture(scope="module")
def phenanthrene() -> tuple[list[str], np.ndarray, np.ndarray]:
    return load(PHENANTHRENE, "hessian_b3lyp_analytic.npz")


def pair_build(symbols: list[str], coords: np.ndarray, H: np.ndarray, settings: IC.PrimitiveSettings) -> tuple:
    B, _types = T2.internals(symbols, coords, settings)
    F_low, _ = T2.to_internal(H, B)
    return RB.molecule_pairs(symbols, coords, F_low, settings=settings)


def renumbered(symbols: list[str], coords: np.ndarray, H: np.ndarray, order: np.ndarray) -> tuple:
    cols = IC.cartesian_columns(order)
    return [symbols[k] for k in order], coords[order], H[np.ix_(cols, cols)]


def same(a: np.ndarray, b: np.ndarray) -> bool:
    return a.shape == b.shape and bool(np.allclose(a, b))


@pytest.mark.parametrize("field, value", [("angle_choice", "alphabetical"), ("dihedral_encoding", "sin")])
def test_an_unknown_setting_is_refused(field: str, value: str) -> None:
    with pytest.raises(ValueError, match=field):
        IC.PrimitiveSettings(**{field: value})


def test_the_defaults_are_the_carried_recipe() -> None:
    assert IC.PrimitiveSettings(angle_choice="geometric", dihedral_encoding="raw") == IC.CARRIED


@pytest.mark.parametrize("encoding, expected", [("raw", (3.0, 0.0)), ("cos", (np.cos(3.0), 0.0)), ("cossin", (np.cos(3.0), np.sin(3.0)))])
def test_torsion_values(encoding: str, expected: tuple[float, float]) -> None:
    assert IC.torsion_values(3.0, encoding) == pytest.approx(expected, abs=1e-15)


def test_without_symmetry_the_canonical_build_is_the_same_in_every_order(asymmetric) -> None:
    symbols, coords, H = asymmetric
    _pairs, feat, _cls, B = pair_build(symbols, coords, H, CANONICAL)
    carried = pair_build(symbols, coords, H, IC.CARRIED)[1]
    rng = np.random.default_rng(0)
    dx = rng.normal(size=coords.size)
    carried_differs = False
    for _ in range(ORDERS):
        order = rng.permutation(len(symbols))
        s2, c2, H2 = renumbered(symbols, coords, H, order)
        _p2, feat2, _c2, B2 = pair_build(s2, c2, H2, CANONICAL)
        np.testing.assert_allclose(feat2, feat, atol=1e-10)
        np.testing.assert_allclose(B2 @ dx[IC.cartesian_columns(order)], B @ dx, atol=1e-10)   # B's columns are in each input's order
        carried_differs |= not same(pair_build(s2, c2, H2, IC.CARRIED)[1], carried)
    assert carried_differs, "the carried construction should depend on the order here; the test would prove nothing"


def test_with_symmetry_canonical_and_cos_give_the_same_feature_set_in_every_order(phenanthrene) -> None:
    symbols, coords, H = phenanthrene
    feat = pair_build(symbols, coords, H, CANONICAL_COS)[1]
    rng = np.random.default_rng(0)
    for _ in range(ORDERS):
        feat2 = pair_build(*renumbered(symbols, coords, H, rng.permutation(len(symbols))), CANONICAL_COS)[1]
        assert feat2.shape == feat.shape
        np.testing.assert_allclose(np.sort(feat2, axis=0), np.sort(feat, axis=0), atol=1e-6)   # the geometry is C2v to ~1e-7 bohr


@pytest.mark.parametrize("folder", [ASYMMETRIC, PHENANTHRENE], ids=["asymmetric", "phenanthrene"])
def test_the_loader_and_the_pair_builder_agree_under_the_canonical_choice(folder: Path) -> None:
    symbols, coords, H = load(folder, "hessian_b3lyp_analytic.npz" if folder == PHENANTHRENE else "hessian_b3lyp.npz")
    B_loader, _ = T2.internals(symbols, coords, CANONICAL)
    np.testing.assert_allclose(pair_build(symbols, coords, H, CANONICAL)[3], B_loader, atol=1e-8)   # the trainer's _checked_pairs bound


def test_cos_keeps_the_dihedral_features_continuous_across_the_wrap(phenanthrene) -> None:
    symbols, coords, H = phenanthrene
    noisy = coords + np.random.default_rng(1).normal(0.0, NOISE_BOHR, coords.shape)
    jumps = {}
    for encoding in ("raw", "cos"):
        settings = IC.PrimitiveSettings(dihedral_encoding=encoding)
        f0, f1 = pair_build(symbols, coords, H, settings)[1], pair_build(symbols, noisy, H, settings)[1]
        jumps[encoding] = float(np.max(np.abs(f1 - f0)))
    assert jumps["raw"] > 6.0, jumps     # a dihedral at ±π changed side: 2π in its sum and difference features
    assert jumps["cos"] < 1e-2, jumps


def test_cossin_adds_one_slot_to_each_primitive(phenanthrene) -> None:
    symbols, coords, H = phenanthrene
    widths = {e: pair_build(symbols, coords, H, IC.PrimitiveSettings(dihedral_encoding=e))[1].shape[1] for e in IC.DIHEDRAL_ENCODINGS}
    assert widths["cos"] == widths["raw"]
    assert widths["cossin"] == widths["raw"] + 2     # the sum and the difference of the two primitive vectors
