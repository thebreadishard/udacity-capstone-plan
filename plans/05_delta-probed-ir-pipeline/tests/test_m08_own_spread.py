"""A band's licence follows its own spread in module 08 (`m08/own_spread.py`), as aromir's does at bb8eb62 (`tests/test_own_spread.py`
there for the cases ported): the molecule is turned, mirrored and listed in other atom orders, the networks correct each presentation,
and a band whose position lies further from the printed one than the licence line, unrounded, is not licensed; a molecule that cannot
be measured has no licensed band. It replaces the rule by a molecule's group (TASKS 288).

The rule's arithmetic on made-up modes and graphs; the check on the frozen corpus's benzene with stand-in networks and with the pin
model through the pipeline's step 4; the certificate on that benzene after a zero correction with a stored measurement; and the port
against aromir's numbers on the corpus's stored molecules with v1.4's release networks, where both are on this machine."""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pytest
import rdkit

from pin_tools import DATA, PIN_CORPUS, PLAN, require_frozen_corpus

sys.path.insert(0, str(PLAN / "modules" / "08_industry_synthesis"))
from m08 import accuracy as A
from m08 import licence
from m08 import live_certificate as LC
from m08 import own_spread as OS
from m08 import pipeline as P
from m08 import reuse as R
from m08.spectrum import vib_min_cm

BENZENE = "A_8448043181"
PIN_MODEL = DATA / "rungC_cc_pin_model.pt"
V14 = "E7_rungC_v14s3clean_c00_control"
RELEASE = tuple(f"{V14}_release_model_n1132_seed{s}.pt" for s in range(3))
MEASUREMENT = tuple(f"{V14}_model_n1082_seed{s}.pt" for s in range(3))
INVARIANCE_RECORD = A.M05_OUT / "v14" / f"{V14}_release_invariance.json"
LINE = A.LICENCE_LINE_CM
PIN_CM = 0.02
"""How far a pinned spread may lie from the one measured (aromir's tolerance): the networks run in single precision."""

# aromir's certificate.py at bb8eb62, word for word
UNCHECKED = "how far this band moves when the molecule is turned, mirrored or listed in another order could not be measured"
CONDITION = ("own position moved by no more than the licence line in the {n}presentations tried (this molecule turned, mirrored or "
             "listed in another atom order)")


# ------------------------------------------------------------------------------------------------ the rule's arithmetic (aromir's cases)
@pytest.mark.parametrize(("spread", "text"), [(1.4, "1.40"), (3.0, "3.00"), (2.996, "3.00"), (3.004, "3.004"), (3.00004, "3.00004"),
                                              (9.951, "9.95")])
def test_a_spread_is_printed_to_two_decimals_unless_they_hide_its_side(spread, text):
    assert OS.stated(spread, LINE) == text


def modes(wavenumbers: list[float], vectors: list[list[float]]) -> OS.Modes:
    return OS.Modes(np.array(wavenumbers), np.array(vectors, dtype=float).T)


def test_two_bands_that_mix_get_the_larger_of_the_pairs_shift_and_their_own():
    # Printed 1000 and 1002; a presentation shares their motion out 60 to 40 and puts them at 1000 and 1006. As a pair, sorted against
    # sorted, they moved by 0 and 4: 4.
    printed = modes([1000.0, 1002.0], [[1.0, 0.0], [0.0, 1.0]])
    more, less = 0.6**0.5, 0.4**0.5
    # The mode at 1000 is mostly the band printed there: paired by motion the bands moved by 0 and 4, and the band that stayed takes
    # the pair's 4.
    kept = modes([1000.0, 1006.0], [[more, less], [less, -more]])
    assert OS.band_shifts(kept, printed).tolist() == [4.0, 4.0]
    # The mode at 1006 is mostly the band printed at 1000: paired by motion the bands moved by 6 and 2. The first keeps its own 6,
    # larger than the pair's 4; the second takes 4.
    crossed = modes([1000.0, 1006.0], [[less, more], [more, -less]])
    assert OS.band_shifts(crossed, printed).tolist() == [6.0, 4.0]
    # Half and half, the pairing may fall either way: no band gets less than the pair's 4.
    half = float(np.sqrt(0.5))
    even = modes([1000.0, 1006.0], [[half, half], [half, -half]])
    assert OS.band_shifts(even, printed).tolist() in ([4.0, 4.0], [6.0, 4.0])


def thinly_mixed(partner_cm: float, other_cm: float) -> OS.Modes:
    """Six modes, one holding 0.6 of the first printed band and 0.08 of each other. The mode set is a reflection of the printed one, so
    it is orthonormal; the thin mode is the second by position and the first printed band's partner by motion."""
    thin = np.array([0.6**0.5, *[0.08**0.5] * 5])
    normal = np.eye(6)[0] - thin
    vectors = np.eye(6) - 2.0 * np.outer(normal, normal) / (normal @ normal)
    positions = np.array([other_cm, partner_cm, 1020.0, 1030.0, 1040.0, 1050.0])
    return OS.Modes(positions, vectors[:, [1, 0, 2, 3, 4, 5]])


def test_a_mixed_band_with_no_cluster_gets_the_larger_of_its_paired_and_its_rank_shift():
    printed = OS.Modes(np.array([1000.0, 1010.0, 1020.0, 1030.0, 1040.0, 1050.0]), np.eye(6))
    by_rank = OS.band_shifts(thinly_mixed(1000.5, 996.0), printed)        # its partner by motion 0.5 away, the mode of its rank 4 away
    assert by_rank[0] == pytest.approx(4.0)
    by_motion = OS.band_shifts(thinly_mixed(1005.0, 1001.0), printed)     # its partner by motion 5 away, the mode of its rank 1 away
    assert by_motion[0] == pytest.approx(5.0)


def test_two_bands_that_keep_their_motion_are_paired_by_it_not_by_rank():
    printed = modes([1000.0, 1002.0], [[1.0, 0.0], [0.0, 1.0]])
    unmixed = modes([1000.0, 1006.0], [[1.0, 0.0], [0.0, 1.0]])
    assert OS.band_shifts(unmixed, printed).tolist() == [0.0, 4.0]
    crossed = modes([1001.0, 1003.0], [[0.0, 1.0], [1.0, 0.0]])           # the lower mode of the presentation is the upper printed band
    assert OS.band_shifts(crossed, printed).tolist() == [3.0, 1.0]
    small, large = float(np.sqrt(0.05)), float(np.sqrt(0.95))             # a little motion shared with an unmixed neighbour
    nearly = modes([1000.0, 1006.0], [[large, small], [small, -large]])
    assert OS.band_shifts(nearly, printed).tolist() == [0.0, 4.0]


def bonds(graph) -> set[frozenset[int]]:
    return {frozenset((bond.GetBeginAtomIdx(), bond.GetEndAtomIdx())) for bond in graph.GetBonds()}


def keeps_the_graph(graph, order: tuple[int, ...]) -> bool:
    """Whether an order of the atoms leaves every bond and element where it was."""
    place = np.argsort(order)
    same_bonds = {frozenset(int(place[k]) for k in bond) for bond in bonds(graph)} == bonds(graph)
    symbols = [atom.GetSymbol() for atom in graph.GetAtoms()]
    return same_bonds and [symbols[k] for k in order] == symbols


def heavy_atoms(graph) -> list[int]:
    return [atom.GetIdx() for atom in graph.GetAtoms() if atom.GetAtomicNum() > 1]


def test_a_small_molecule_gets_every_order_its_graph_cannot_tell_apart():
    graph = OS.bond_graph("Cc1ccccc1")
    found = OS.skeleton_symmetries(graph)
    assert (len(found.skeleton) + 1, found.n_exchanges, found.n_orders) == (2, 6, 12)
    orders = OS.swaps(found, np.random.default_rng(OS.SEED))
    assert len(set(orders)) == 11 and orders == sorted(orders)
    assert all(keeps_the_graph(graph, order) for order in orders)
    assert sum(all(order[k] == k for k in heavy_atoms(graph)) for order in orders) == 5


def test_a_methyl_rich_molecule_gets_swaps_of_its_heavy_atoms_and_of_its_hydrogens():
    # Hexamethylbenzene has 12 skeleton symmetries and 6 ways to list each methyl's hydrogens: 559,872 orders, of which the first
    # thousand RDKit matches move no carbon.
    graph = OS.bond_graph("Cc1c(C)c(C)c(C)c(C)c1C")
    found = OS.skeleton_symmetries(graph)
    assert (len(found.skeleton) + 1, found.n_orders, found.capped) == (12, 559872, False)
    orders = OS.swaps(found, np.random.default_rng(OS.SEED))
    assert len(orders) == 11 + OS.N_HYDROGEN_SWAPS
    assert all(keeps_the_graph(graph, order) for order in orders)
    heavy = heavy_atoms(graph)
    assert sum(any(order[k] != k for k in heavy) for order in orders[:11]) == 11
    assert orders[0] == found.order(found.skeleton[0], {})
    exchanged = orders[11:]
    assert len(set(exchanged)) == OS.N_HYDROGEN_SWAPS and not set(exchanged) & set(orders[:11])


def test_more_skeleton_symmetries_than_are_tried_are_drawn():
    graph = OS.bond_graph("CC(C)(C)c1ccc(C(C)(C)C)cc1")
    found = OS.skeleton_symmetries(graph)
    assert len(found.skeleton) + 1 == 144 and not found.capped
    orders = OS.swaps(found, np.random.default_rng(OS.SEED))
    assert orders == OS.swaps(found, np.random.default_rng(OS.SEED))
    assert orders != OS.swaps(found, np.random.default_rng(OS.SEED + 1))
    assert len(orders) == OS.N_SWAPS + OS.N_HYDROGEN_SWAPS
    assert all(keeps_the_graph(graph, order) for order in orders)
    skeleton_only = orders[: OS.N_SWAPS]
    assert skeleton_only == sorted(skeleton_only) and len(set(skeleton_only)) == OS.N_SWAPS
    tried = OS.changes(graph, found)
    assert sum(change.kind == "swap" for change in tried) == len(set(orders))


def test_a_molecule_at_the_limit_of_symmetries_is_recorded_as_capped(monkeypatch):
    monkeypatch.setattr(OS, "MAX_SYMMETRIES", 8)
    graph = OS.bond_graph("CC(C)(C)c1ccc(C(C)(C)C)cc1")
    found = OS.skeleton_symmetries(graph)
    assert found.capped and len(found.skeleton) + 1 <= 8
    assert all(keeps_the_graph(graph, order) for order in OS.swaps(found, np.random.default_rng(OS.SEED)))


def test_a_symmetry_of_the_skeleton_keeps_each_atoms_hydrogens():
    # Imidazole's ring maps onto itself with N–H and N exchanged; that is no symmetry.
    assert OS.skeleton_symmetries(OS.bond_graph("c1c[nH]cn1")).skeleton == ()
    assert len(OS.skeleton_symmetries(OS.bond_graph("O=[N+]([O-])c1ccccc1")).skeleton) == 1


def made_up_molecule(graph, seed: int) -> OS.Molecule:
    """A graph's atoms at made-up positions: the presentations are drawn from the graph alone."""
    n = graph.GetNumAtoms()
    rng = np.random.default_rng(seed)
    return OS.Molecule(tuple(atom.GetSymbol() for atom in graph.GetAtoms()), rng.normal(size=(n, 3)), rng.uniform(1.0, 12.0, size=n), {})


def test_the_changes_are_the_same_molecule_and_undo_returns_a_hessian():
    graph = OS.bond_graph("Cc1c2ccccc2cc2ccccc12")                       # 9-methylanthracene
    molecule = made_up_molecule(graph, 3)
    noise = np.random.default_rng(4).normal(scale=0.02, size=(3 * molecule.n_atoms,) * 2)
    hessian = noise + noise.T + 0.5 * np.eye(3 * molecule.n_atoms)
    tried = OS.changes(graph, OS.skeleton_symmetries(graph))
    assert [change.kind for change in tried] == ["rotation"] * OS.N_ROTATIONS + ["mirror image"] * 2 + ["swap"] * 11
    for change in tried:
        changed, changed_hessian = change.apply(molecule, hessian)
        np.testing.assert_allclose(change.undo(changed_hessian), hessian, atol=1e-12)
        assert changed.symbols == tuple(molecule.symbols[k] for k in change.order)
        np.testing.assert_array_equal(changed.masses_amu, molecule.masses_amu[list(change.order)])
        assert keeps_the_graph(graph, change.order)
        assert np.linalg.det(change.matrix) == pytest.approx(-1.0 if change.kind == "mirror image" else 1.0)
        assert ("order" in change.record()) is (change.kind in ("swap", "listing"))


def test_the_presentations_are_drawn_in_aromirs_order_from_one_generator():
    graph = OS.bond_graph("N#Cc1ccccc1")
    tried = OS.changes(graph, OS.skeleton_symmetries(graph))
    rng = np.random.default_rng(OS.SEED)
    for change in tried[: OS.N_ROTATIONS]:
        q, _ = np.linalg.qr(rng.normal(size=(3, 3)))
        np.testing.assert_array_equal(change.matrix, q * np.sign(np.linalg.det(q)))
    np.testing.assert_array_equal(tried[OS.N_ROTATIONS].matrix, np.diag([1.0, 1.0, -1.0]))        # the mirror image: no draw
    q, _ = np.linalg.qr(rng.normal(size=(3, 3)))
    np.testing.assert_array_equal(tried[OS.N_ROTATIONS + 1].matrix, np.diag([1.0, 1.0, -1.0]) @ (q * np.sign(np.linalg.det(q))))
    assert [change.name for change in tried[OS.N_ROTATIONS:]] == ["the mirror image", "the mirror image, rotated", "a swap of equivalent atoms 1"]
    identity = tuple(range(graph.GetNumAtoms()))
    assert all(change.order == identity for change in tried[: OS.N_ROTATIONS + 2]) and tried[-1].order != identity


# ---------------------------------------------------------------------------------- the check on benzene, with networks that stand in
def benzene() -> tuple[OS.Molecule, np.ndarray]:
    """The frozen corpus's benzene, whose atoms are in the canonical order of c1ccccc1, with its B3LYP Hessian."""
    require_frozen_corpus()
    folder = PIN_CORPUS / "molecules" / BENZENE
    with np.load(folder / R.HESSIAN) as z:
        return OS.Molecule.of_folder(folder), np.asarray(z["H_projected"], float)


@dataclass
class StandIn:
    """Networks whose answer is a fixed function of the Hessian they read."""

    answer: str
    fails_at: int = 0
    failure: type[Exception] = RuntimeError
    nan_at: int = 0
    calls: int = 0

    def __call__(self, molecule: OS.Molecule, hessian: np.ndarray) -> np.ndarray:
        self.calls += 1
        if self.calls == self.fails_at:
            raise self.failure("the internal coordinates could not be built")
        if self.calls == self.nan_at:
            return np.full_like(hessian, np.nan)
        # The other answer is stiffer along the laboratory's z axis: no rotation leaves it alone.
        laboratory_z = np.kron(np.eye(molecule.n_atoms), np.diag([0.0, 0.0, 1.0]))
        return np.asarray(0.01 * hessian if self.answer == "scaled" else 0.02 * laboratory_z)


def measured(networks: StandIn) -> OS.OwnSpread:
    molecule, hessian = benzene()
    correction = 0.01 * hessian if networks.answer == "scaled" else np.zeros_like(hessian)
    return OS.measure(networks, "c1ccccc1", molecule, hessian, correction)


def test_networks_that_turn_with_the_molecule_move_no_band():
    found = measured(StandIn("scaled"))
    assert len(found.spread_cm) == 30 and max(found.spread_cm) < 1e-6
    assert found.record()["counts"] == {"rotation": OS.N_ROTATIONS, "mirror image": 2, "swap": 11, "listing": 0}


def test_networks_tied_to_the_laboratory_axes_move_bands_under_a_rotation_only():
    networks = StandIn("laboratory z")
    molecule, hessian = benzene()
    found = OS.measure(networks, "c1ccccc1", molecule, hessian, networks(molecule, hessian))
    assert max(found.spread_cm) > LINE
    kinds = {change.name: change.kind for change in found.tried}
    moving = {name for name, spread in zip(found.change, found.spread_cm, strict=True) if spread > 1e-6}
    assert moving and {kinds[name] for name in moving} <= {"rotation", "mirror image"} and "the mirror image" not in moving


@pytest.mark.parametrize("failure", OS.UNBUILT)
def test_a_presentation_the_networks_cannot_correct_withholds_the_licence_by_name(failure):
    found = measured(StandIn("scaled", fails_at=3, failure=failure)).measurement()
    assert found.spread_cm == () and found.change == () and found.n_tried == 0
    assert found.refusal == (f"the networks could not correct the molecule given as rotation 3: {failure.__name__}: the internal "
                             "coordinates could not be built")
    assert (ValueError, ArithmeticError, RuntimeError) == OS.UNBUILT


def test_a_correction_that_is_not_finite_is_a_refusal_by_name_not_a_crash():
    found = measured(StandIn("scaled", nan_at=9)).measurement()
    assert found.spread_cm == () and found.n_tried == 0
    assert found.refusal == ("the networks could not correct the molecule given as the mirror image: ValueError: the correction is not "
                             "finite")


def test_a_defect_in_the_check_is_raised_not_turned_into_a_refusal():
    with pytest.raises(TypeError, match="could not be built"):
        measured(StandIn("scaled", fails_at=3, failure=TypeError))


def test_a_geometry_that_is_not_its_smiles_in_the_canonical_order_is_not_measured():
    molecule, hessian = benzene()
    swapped = list(range(molecule.n_atoms))
    swapped[-2:] = swapped[-1], swapped[-2]                                 # two hydrogens of different carbons in each other's place
    found = OS.measure(StandIn("scaled"), "c1ccccc1", *OS.reordered(molecule, hessian, tuple(swapped)), np.zeros_like(hessian))
    assert found.spread_cm == () and found.tried == ()
    assert found.refusal.startswith("the geometry is not the molecule of its SMILES in the canonical atom order: ")
    with pytest.raises(ValueError, match="are not those of"):
        OS.graph_of("c1ccccc1", molecule.reordered(tuple(range(molecule.n_atoms))[::-1]))
    with pytest.raises(ValueError, match="does not parse as a SMILES"):
        OS.bond_graph("c1ccccc")


def test_the_check_is_the_same_every_time():
    first, again = measured(StandIn("laboratory z")), measured(StandIn("laboratory z"))
    assert first.spread_cm == again.spread_cm and first.change == again.change and first.record() == again.record()
    made = first.record()
    assert (made["seed"], made["rdkit"], made["max_symmetries"]) == (OS.SEED, rdkit.__version__, OS.MAX_SYMMETRIES)
    assert (made["skeleton_symmetries"], made["equivalent_orders"], made["symmetries_capped"]) == (12, 12, False)
    assert (made["paired_overlap"], made["mixing_share"], made["not_measured_because"]) == (0.7, 0.1, "")
    orders = [tried["order"] for tried in made["presentations"] if "order" in tried]
    assert len(orders) == 11 and all(sorted(order) == list(range(12)) for order in orders)
    matrices = [tried["matrix"] for tried in made["presentations"] if "matrix" in tried]
    assert len(matrices) == OS.N_ROTATIONS + 2
    for matrix in matrices:
        np.testing.assert_allclose(np.array(matrix) @ np.array(matrix).T, np.eye(3), atol=1e-12)


# ------------------------------------------------------------------------------------------------- the certificate reads the measurement
class NoCatalog:
    def find(self, smiles: str) -> None:
        return None

    def u_band(self, species: str) -> dict:
        return {}


def with_spreads(spreads: list[float]) -> OS.Measurement:
    """A measurement of given spreads, each under 'rotation 1', of a molecule without symmetry: the rule's rotations and mirror images
    and nothing else were tried."""
    tried = tuple(OS.Change(f"rotation {k + 1}", "rotation", np.eye(3), ()) for k in range(OS.N_ROTATIONS))
    tried += (OS.Change("the mirror image", "mirror image", OS.MIRROR, ()), OS.Change("the mirror image, rotated", "mirror image", OS.MIRROR, ()))
    return OS.OwnSpread(spread_cm=tuple(spreads), change=("rotation 1",) * len(spreads), tried=tried, symmetries=None,
                        refusal="").measurement()


def uniform(n_modes: int, spread_cm: float) -> OS.Measurement:
    """The own spread of a molecule whose every band moved alike under one rotation (aromir's `support.uniform_spread`)."""
    return with_spreads([spread_cm] * n_modes)


def every_mode_a_band(measured: OS.Measurement) -> LC.Spreads:
    """A measurement as the certificate reads it for a molecule whose every mode is a band of the spectrum."""
    return LC.Spreads(measured, tuple(zip(measured.spread_cm, measured.change, strict=True)))


UNMOVED = every_mode_a_band(uniform(30, 0.0))
"""Benzene's own spread under networks that move no band."""
OWN_SPREAD = {"own_spread": {"n_presentations": UNMOVED.measured.n_tried, "text": LC.own_spread_text(UNMOVED, LINE)}}
"""What a licence block says of that spread (`LC.licence_block`), for a statement built from a made-up block."""


def benzene_folder(tmp_path: Path, admission: dict, n_models: int, spread_cm: float | None = 0.0) -> Path:
    """Benzene's folder as the pipeline leaves it after a zero correction by the admission's models, with the own spread of networks
    that moved every band by `spread_cm` (None: no measurement, a result of a pipeline before 0.15)."""
    require_frozen_corpus()
    d = tmp_path / BENZENE
    shutil.copytree(PIN_CORPUS / "molecules" / BENZENE, d)
    zero = np.zeros((36, 36))
    names = tuple(Path(m["path"]).name for m in admission["models"])
    P.save_correction(d, zero, [zero] * n_models, tuple(Path(n) for n in names))
    P.write_json(d / "pipeline.json", {"pipeline_version": P.PIPELINE_VERSION, "name": "benzene", "spectra": P.spectra(d, zero, [zero] * n_models),
                                       "admission": {"smiles": "c1ccccc1", "formula": "C6H6", "n_atoms": 12, "elements": ["C", "H"],
                                                     "training_atoms": [6, 40], "inside_training_sizes": True} | admission,
                                       "seconds": {"low_level": 60.0}, "provenance": {"host": "laptop", "commit": "0" * 40, "dirty": False},
                                       "deck": {"sha16": "d" * 16}, "low_level": {"b3lyp": {"software": {"pyscf": "2.15.0"}}}})
    if spread_cm is not None:
        OS.save(d, uniform(30, spread_cm), 0.0)
    return d


def entries(names: tuple[str, ...], hashes: dict[str, str], version: str, folder: str = "") -> list[dict]:
    return [{"path": f"out/{folder}{n}", "sha16": hashes[n], "network": P.NETWORK, "version": version, "status": "carried"} for n in names]


@pytest.fixture
def v14_release(monkeypatch) -> dict:
    """v1.4's release networks that ran, with the hashes their invariance record names, and its measurement networks for the error
    bars. The checkpoints are not in git, so the training ids and the inner-validation share are given."""
    measured_files = json.loads(INVARIANCE_RECORD.read_text(encoding="utf-8"))["provenance"]["networks"]
    with open(A.product_error_path(tuple(f"v14/{n}" for n in MEASUREMENT)), encoding="utf-8") as f:
        product = json.load(f)["model_sha16"]
    monkeypatch.setattr(P, "train_ids", lambda models: set())
    monkeypatch.setattr(P, "inner_validation_share", lambda models: 0.15)
    released = [e | {P.NK.FIELD: P.NK.RELEASE} for e in entries(RELEASE, {n: h[:16] for n, h in measured_files.items()}, "1.4", "v14/")]
    return {"models": released, "measurement_models": entries(MEASUREMENT, product, "1.4", "v14/")}


def moved_note(text: str) -> str:
    return f"its position moved by {text} cm⁻¹ under rotation 1 of this molecule, more than the licence line"


def test_a_spread_at_the_line_keeps_the_licence_and_one_above_withholds_it(tmp_path, v14_release):
    plain = LC.certificate(benzene_folder(tmp_path / "plain", v14_release, 3), NoCatalog())
    at_line = LC.certificate(benzene_folder(tmp_path / "at", v14_release, 3, LINE), NoCatalog())
    assert len(plain["bands"]) == 30 and all(b["licensed"] for b in plain["bands"]) and all(b["licensed"] for b in at_line["bands"])
    assert not any("licence_note" in b for b in at_line["bands"]) and "withheld" not in at_line["licence"]
    above = LC.certificate(benzene_folder(tmp_path / "above", v14_release, 3, 3.01), NoCatalog())
    assert not any(b["licensed"] for b in above["bands"]) and {b["licence_note"] for b in above["bands"]} == {moved_note("3.01")}
    unchanged = ("network_cm", "printed_cm", "b3lyp_cm", "baseline_cm", "km_mol", "seed_range_cm", "family")
    assert [{k: b[k] for k in unchanged} for b in above["bands"]] == [{k: b[k] for k in unchanged} for b in plain["bands"]]
    assert "withheld" not in above["licence"] and LC.withheld_reason(above["licence"]) is None       # band by band, not the molecule
    assert f"| no: {moved_note('3.01')} | 3.01, rotation 1 |" in LC.to_markdown(above)
    assert "| yes | 0.00, rotation 1 |" in LC.to_markdown(plain)


def test_the_line_is_held_against_the_unrounded_spread(tmp_path, v14_release):
    # 3.004 rounds to 3.00, the line itself: it is beyond the line, and printed as it is.
    just_above = LC.certificate(benzene_folder(tmp_path / "above", v14_release, 3, 3.004), NoCatalog())
    assert {b["licence_note"] for b in just_above["bands"]} == {moved_note("3.004")}
    assert {b["own_spread_cm"] for b in just_above["bands"]} == {3.004}
    assert "The largest is 3.004 cm⁻¹, under rotation 1, and 30 band(s) moved by more than the licence line" in just_above["statement"]
    just_below = LC.certificate(benzene_folder(tmp_path / "below", v14_release, 3, 2.996), NoCatalog())
    assert all(b["licensed"] for b in just_below["bands"]) and {b["own_spread_cm"] for b in just_below["bands"]} == {3.0}
    assert "| yes | 3.00, rotation 1 |" in LC.to_markdown(just_below)


def test_one_band_beyond_the_line_loses_its_licence_and_the_others_keep_theirs(tmp_path, v14_release):
    d = benzene_folder(tmp_path, v14_release, 3)
    OS.save(d, with_spreads([0.5] * 7 + [5.16] + [0.5] * 22), 0.0)
    c = LC.certificate(d, NoCatalog())
    assert [b["licensed"] for b in c["bands"]] == [True] * 7 + [False] + [True] * 22
    assert c["bands"][7]["licence_note"] == moved_note("5.16") and c["bands"][7]["own_spread_cm"] == 5.16
    assert sum("licence_note" in b for b in c["bands"]) == 1 and "withheld" not in c["licence"]
    families = ", ".join(c["licence"]["licensed_families"])
    assert (f"harmonic positions ω are licensed for {families} (decision 65) where a band's {CONDITION.format(n='10 ')}, each band "
            "marked; at ") in c["statement"]
    assert ("Each band's own spread was measured for this molecule: the networks corrected it again in 10 other presentations "
            "(8 rotations, 2 mirror images), and a band's spread is the furthest its position lay from the printed one in any of them: its distance from "
            "the printed presentation, not the range between presentations. The largest is 5.16 cm⁻¹, under rotation 1, and 1 band(s) "
            "moved by more than the licence line, so none of them is licensed; the corrected positions are still printed. The scaled "
            "B3LYP spectrum is shown as the baseline only.") in c["statement"]
    assert c["licence"]["own_spread"]["n_presentations"] == 10


def test_a_molecule_whose_bands_stay_within_the_line_says_so(tmp_path, v14_release):
    c = LC.certificate(benzene_folder(tmp_path, v14_release, 3, 0.88), NoCatalog())
    assert "The largest is 0.88 cm⁻¹, under rotation 1, and no band moved by more than the licence line. The scaled" in c["statement"]
    assert "0 of " not in c["statement"] and "For this molecule it is withheld" not in LC.to_markdown(c)
    assert c["statement"].endswith(f"This molecule and the ΔH network: {c['molecule']['seen']['text']}.")


def test_a_result_without_a_measurement_licenses_no_band_and_says_why(tmp_path, v14_release):
    plain = LC.certificate(benzene_folder(tmp_path / "plain", v14_release, 3), NoCatalog())
    c = LC.certificate(benzene_folder(tmp_path / "old", v14_release, 3, None), NoCatalog())
    refusal = c["own_spread"]["not_measured_because"]
    assert refusal.startswith("the result holds no own_spread.json") and c["own_spread"]["presentations"] == []
    assert not any(b["licensed"] for b in c["bands"]) and {b["licence_note"] for b in c["bands"]} == {UNCHECKED}
    assert all(b["own_spread_cm"] is None and b["own_spread_change"] == "" for b in c["bands"])
    assert [b["network_cm"] for b in c["bands"]] == [b["network_cm"] for b in plain["bands"]]
    reason = ("how far this molecule's bands move when it is turned, mirrored or listed in another order could not be measured "
              f"({refusal}), so no band is licensed; the corrected positions are still printed")
    assert c["licence"]["withheld"] == {"note": UNCHECKED, "reason": reason, "n_bands": 30} and LC.withheld_reason(c["licence"]) == reason
    families = ", ".join(c["licence"]["licensed_families"])
    assert (f"0 of 30 bands are licensed: the version's harmonic positions ω are licensed for {families} (decision 65) where a band's "
            f"{CONDITION.format(n='')}, and for this molecule that licence is withheld — {reason} — each band marked; at ") in c["statement"]
    assert "Each band's own spread was measured" not in c["statement"] and "; 0 of 30 bands are licensed: " in c["statement"]
    page = LC.to_markdown(c)
    assert f"| no: {UNCHECKED} | not measured |" in page and f"For this molecule it is withheld: H{reason[1:]}." in page
    assert f"- own spread: not measured — {refusal}" in page


def test_a_band_that_was_never_licensable_says_that_before_its_spread():
    """aromir's order of a band's licence note: a flat coordinate, an imaginary position, imaginary for a seed, then the own spread."""
    moved = moved_note("9.95")
    assert LC.licence_note(LC.BandState(-50.8, -25.2, -30.0, 9.951, "rotation 1"), "") == LC.FLAT_COORDINATE
    assert LC.licence_note(LC.BandState(40.0, -25.2, -30.0, 9.951, "rotation 1"), "") == LC.IMAGINARY
    assert LC.licence_note(LC.BandState(40.0, 25.2, -3.0, None, ""), "") == LC.IMAGINARY_FOR_A_SEED
    assert LC.licence_note(LC.BandState(40.0, 25.2, 3.0, None, ""), "outside") == UNCHECKED
    assert LC.licence_note(LC.BandState(40.0, 25.2, 3.0, 9.951, "rotation 1"), "outside") == moved
    assert LC.licence_note(LC.BandState(40.0, 25.2, 3.0, 1.0, "rotation 1"), "outside") == "outside"
    assert LC.licence_note(LC.BandState(40.0, 25.2, 3.0, LINE, "rotation 1"), "") == ""
    assert LC.FLAT_COORDINATE == "a flat coordinate: its low-level mode is imaginary, so this is no band position"      # aromir's words


def test_a_band_on_an_imaginary_b3lyp_mode_is_a_flat_coordinate_on_the_certificate(tmp_path, v14_release):
    d = benzene_folder(tmp_path, v14_release, 3, 9.95)
    hessian = d / R.HESSIAN
    with np.load(hessian) as z:
        arrays = {k: z[k] for k in z.files}
    masses = OS.Molecule.of_folder(d).masses_amu
    s = np.sqrt(np.repeat(masses, 3))
    lam, V = np.linalg.eigh(arrays["H_projected"] / np.outer(s, s))
    lam[6] = -lam[6]                                                        # the softest vibration, made imaginary at its own size
    np.savez(hessian, **(arrays | {"H_projected": np.outer(s, s) * ((V * lam) @ V.T)}))
    zero = np.zeros((36, 36))
    rec = json.loads((d / "pipeline.json").read_text(encoding="utf-8"))
    P.write_json(d / "pipeline.json", rec | {"spectra": P.spectra(d, zero, [zero] * 3)})
    OS.save(d, uniform(30, 9.95), 0.0)
    c = LC.certificate(d, NoCatalog())
    assert c["bands"][0]["b3lyp_cm"] < 0 and c["bands"][0]["licence_note"] == LC.FLAT_COORDINATE and not c["bands"][0]["licensed"]
    assert {b["licence_note"] for b in c["bands"][1:]} == {moved_note("9.95")}
    assert f"| no: {LC.FLAT_COORDINATE} | 9.95, rotation 1 |" in LC.to_markdown(c)


def test_a_measurement_of_another_correction_is_refused(tmp_path, v14_release):
    d = benzene_folder(tmp_path, v14_release, 3)
    stored = json.loads((d / OS.FILE).read_text(encoding="utf-8"))
    (d / OS.FILE).write_text(json.dumps(stored | {"models": stored["models"][:2]}), encoding="utf-8")
    with pytest.raises(RuntimeError, match="measured with"):
        LC.certificate(d, NoCatalog())
    (d / OS.FILE).write_text(json.dumps(stored | {"printed_cm": [w + 0.01 for w in stored["printed_cm"]]}), encoding="utf-8")
    with pytest.raises(RuntimeError, match="other printed positions"):
        LC.certificate(d, NoCatalog())
    (d / OS.FILE).write_text(json.dumps(stored | {"spread_cm": stored["spread_cm"][:5]}), encoding="utf-8")
    with pytest.raises(RuntimeError, match="30 presentations named for 5 spreads; 5 spreads for 30 modes"):
        LC.certificate(d, NoCatalog())


OTHER_RULE = {"seed": 99, "rotations": 3, "listings": 0, "swaps": 6, "hydrogen_swaps": 0, "max_symmetries": 10, "paired_overlap": 0.5,
              "mixing_share": 0.2}


@pytest.mark.parametrize("key", list(OTHER_RULE))
def test_a_measurement_made_under_other_constants_is_refused_not_read(tmp_path, v14_release, key):
    d = benzene_folder(tmp_path, v14_release, 3, 0.5)
    stored = json.loads((d / OS.FILE).read_text(encoding="utf-8"))
    assert stored["record"][key] == OS._rule()[key] != OTHER_RULE[key]
    (d / OS.FILE).write_text(json.dumps(stored | {"record": stored["record"] | {key: OTHER_RULE[key]}}), encoding="utf-8")
    with pytest.raises(RuntimeError, match=f"not a measurement under this rule \\({key} is .*measure the result again"):
        LC.certificate(d, NoCatalog())
    without = {k: v for k, v in stored["record"].items() if k != key}                 # a record that does not name the constant
    (d / OS.FILE).write_text(json.dumps(stored | {"record": without}), encoding="utf-8")
    with pytest.raises(RuntimeError, match=f"{key} is None"):
        OS.of_result(d)


def test_a_measurement_that_is_not_whole_is_refused(tmp_path, v14_release):
    d = benzene_folder(tmp_path, v14_release, 3, 0.5)
    stored = json.loads((d / OS.FILE).read_text(encoding="utf-8"))
    record = stored["record"]

    def refused(changed: dict, match: str) -> None:
        (d / OS.FILE).write_text(json.dumps(stored | changed), encoding="utf-8")
        with pytest.raises(RuntimeError, match=match):
            OS.of_result(d)

    refused({"record": record | {"presentations": []}}, "0 presentations where its counts give 10")       # the reviewer's record
    refused({"record": record | {"presentations": record["presentations"][:4]}}, "4 presentations where its counts give 10")
    refused({"record": record | {"counts": record["counts"] | {"rotation": 7}, "presentations": record["presentations"][1:]}},
            "7 rotations and 2 mirror images, the rule's are 8 and 2")
    refused({"change": stored["change"][:29]}, "29 presentations named for 30 spreads")
    refused({"change": ["rotation 11"] * 30}, "presentations it does not hold")
    refused({"record": record | {"not_measured_because": "it failed"}}, "names a refusal and holds spreads")
    (d / OS.FILE).write_text(json.dumps(stored), encoding="utf-8")
    assert OS.of_result(d).spread_cm == (0.5,) * 30


def test_the_certificate_keeps_the_record_of_the_check(tmp_path, v14_release):
    d = benzene_folder(tmp_path, v14_release, 3)
    molecule, hessian = benzene()
    networks = StandIn("laboratory z")
    OS.save(d, OS.measure(networks, "c1ccccc1", molecule, hessian, np.zeros_like(hessian)).measurement(), 1.5)
    c = LC.certificate(d, NoCatalog())
    made = c["own_spread"]
    assert made["counts"] == {"rotation": OS.N_ROTATIONS, "mirror image": 2, "swap": 11, "listing": 0} and len(made["presentations"]) == 21
    assert (made["seed"], made["rdkit"], made["max_symmetries"], made["paired_overlap"], made["mixing_share"]) == (
        OS.SEED, rdkit.__version__, OS.MAX_SYMMETRIES, OS.PAIRED_OVERLAP, OS.MIXING_SHARE)
    assert "in the 21 presentations tried (this molecule turned, mirrored or listed in another atom order)" in c["statement"]
    assert "in 21 other presentations (8 rotations, 2 mirror images, 11 swaps of equivalent atoms)" in c["statement"]
    assert (f"- own spread: 8 rotations, 2 mirror images, 11 swaps of equivalent atoms, drawn with the seed 7 under RDKit "
            f"{rdkit.__version__}; each presentation is in certificate.json") in LC.to_markdown(c)
    worst = max(c["bands"], key=lambda b: b["own_spread_cm"])
    assert worst["own_spread_change"] in {p["name"] for p in made["presentations"]} and not worst["licensed"]


def test_the_licence_rule_states_the_own_spread_in_aromirs_words():
    assert ("8 random rotations, the mirror image and a rotated mirror image, 4 random listings of the atoms put into the canonical "
            "order and swaps of atoms the bond graph cannot tell apart (all of them up to 12; of more, 12 symmetries of the heavy-atom "
            "skeleton and 6 exchanges of hydrogens), drawn with the seed 7") in licence.RULE
    assert ("it is licensed only when its position lay no more than 3 cm⁻¹ from the printed one in every presentation tried: the "
            "distance from the printed presentation, not the range between presentations, and a sample, not a bound") in licence.RULE
    assert "describes the network and decides no licence" in licence.RULE and "linear group" not in licence.RULE


def test_the_v14_invariance_record_that_motivated_the_rule_stays_beside_the_release_networks():
    record = json.loads(INVARIANCE_RECORD.read_text(encoding="utf-8"))
    assert record["network_version"] == "1.4" and sorted(record["provenance"]["networks"]) == list(RELEASE)
    assert record["rotation"]["with_linear_group_cm"] == 11.2 and record["xyz_atom_order"]["without_linear_group_cm"] == 2.85
    for name, digest in record["provenance"]["networks"].items():
        path = INVARIANCE_RECORD.parent / name
        if path.is_file():                                                   # the checkpoints are not in git
            assert hashlib.sha256(path.read_bytes()).hexdigest() == digest


def test_the_show_page_prints_the_reason_beside_its_family_table():
    template = (PLAN / "modules" / "08_industry_synthesis" / "m08" / "show_template.html").read_text(encoding="utf-8")
    assert "m.licence_withheld ?" in template and "Not licensed for this molecule: ${esc(m.licence_withheld)}" in template


@pytest.mark.parametrize("spread_cm", [0.5, None])
def test_the_show_card_carries_the_reason_only_when_the_molecule_is_withheld(tmp_path, v14_release, spread_cm):
    from m08 import show
    d = benzene_folder(tmp_path, v14_release, 3, spread_cm)
    rec = json.loads((d / "pipeline.json").read_text(encoding="utf-8"))
    seconds = {"optimise": 5.0, "low_level": 60.0, "correction_and_spectra": 2.0, "own_spread": 8.0}
    P.write_json(d / "pipeline.json", rec | {"reuse": {"reused": False, "source": None}, "seconds": seconds})
    c = LC.certificate(d, NoCatalog())
    LC.write(c, d)
    card = show.molecule(d)
    if spread_cm is None:
        assert card["licence_withheld"] == c["licence"]["withheld"]["reason"]
    else:
        assert "licence_withheld" not in card


MIXED = [0.5] * 7 + [5.16] + [0.5] * 22
"""Benzene with one band beyond the line: its family has licensed bands and one that is not."""


def shown(d: Path) -> tuple[dict, dict]:
    """A folder's certificate written beside it, and the show page's card of it."""
    from m08 import show
    rec = json.loads((d / "pipeline.json").read_text(encoding="utf-8"))
    seconds = {"optimise": 5.0, "low_level": 60.0, "correction_and_spectra": 2.0, "own_spread": 8.0}
    P.write_json(d / "pipeline.json", rec | {"reuse": {"reused": False, "source": None}, "seconds": seconds})
    c = LC.certificate(d, NoCatalog())
    LC.write(c, d)
    return c, show.molecule(d)


def test_a_family_with_one_band_beyond_the_line_says_how_many_are_licensed_on_the_show_and_demo_pages(tmp_path, v14_release):
    from m08 import demo_page as D
    d = benzene_folder(tmp_path, v14_release, 3)
    OS.save(d, with_spreads(MIXED), 0.0)
    c, card = shown(d)
    family = c["bands"][7]["family"]
    n = sum(b["family"] == family for b in c["bands"])
    rows = {row["family"]: row for row in card["families"]}
    assert (rows[family]["licensed"], rows[family]["n_licensed"], rows[family]["licence"]) == (False, n - 1, f"{n - 1} of {n} licensed")
    assert all((row["licensed"], row["licence"]) == (True, "licensed") for name, row in rows.items() if name != family)
    assert (rows[family]["error_a"], rows[family]["error_b"]) == (c["bands"][7]["error_cm"]["a"], c["bands"][7]["error_cm"]["b"])
    _, errors = A.stated_errors(c["accuracy"])
    demo = {row["family"]: row for row in D.family_rows(c["bands"], errors)}
    assert {name: (row["licensed"], row["n_licensed"], row["licence"]) for name, row in demo.items()} == {
        name: (row["licensed"], row["n_licensed"], row["licence"]) for name, row in rows.items()}
    table = D._family_table(D.Panel(demo=None, record={}, certificate=c, vs_corpus=None, grid=np.zeros(1), curves={}))
    assert f'<span class="chip no">{n - 1} of {n} licensed</span>' in table
    assert table.count('<span class="chip ok">licensed</span>') == len(rows) - 1
    from m08 import show
    assert card["stations"][4]["time"] == f"{show.duration(10.0)} with the spectrum"      # the correction's 2 s and the own spread's 8 s


@pytest.mark.parametrize(("spread_cm", "words", "all_licensed"), [(0.5, "licensed", True), (3.01, "not licensed", False)])
def test_a_family_licensed_or_unlicensed_as_a_whole_reads_as_before(tmp_path, v14_release, spread_cm, words, all_licensed):
    from m08 import demo_page as D
    c, card = shown(benzene_folder(tmp_path, v14_release, 3, spread_cm))
    assert all((row["licensed"], row["licence"]) == (all_licensed, words) for row in card["families"])
    assert all(row["n_licensed"] == (row["bands"] if all_licensed else 0) for row in card["families"])
    _, errors = A.stated_errors(c["accuracy"])
    assert all((row["licensed"], row["licence"]) == (all_licensed, words) for row in D.family_rows(c["bands"], errors))


def test_the_show_page_refuses_bands_that_disagree_on_their_familys_error(tmp_path, v14_release):
    from m08 import show
    c = LC.certificate(benzene_folder(tmp_path, v14_release, 3), NoCatalog())
    c["bands"][0]["error_cm"] = {"a": 9.0, "b": 9.0}
    with pytest.raises(ValueError, match="disagree on the family's error"):
        show.families(c["bands"])


# ----------------------------------------------------------------------------------------------------- the networks, through step 4
def test_the_pipelines_step_measures_benzene_with_the_networks_that_corrected_it(tmp_path):
    require_frozen_corpus()
    d = tmp_path / BENZENE
    shutil.copytree(PIN_CORPUS / "molecules" / BENZENE, d)
    models = (PIN_MODEL, PIN_MODEL)
    dH, seeds = P.correction(models, d)
    P.save_correction(d, dH, seeds, models)
    molecule, hessian = benzene()
    np.testing.assert_allclose(OS.mean_correction(P.load_networks(models), molecule, hessian), dH, rtol=0, atol=1e-12)
    assert P.measure_own_spread(models, d, "c1ccccc1") >= 0
    stored = json.loads((d / OS.FILE).read_text(encoding="utf-8"))
    found = OS.of_result(d)
    assert stored["models"] == [PIN_MODEL.name] * 2 and len(found.spread_cm) == 30 and found.refusal == ""
    assert found.record["counts"] == {"rotation": OS.N_ROTATIONS, "mirror image": 2, "swap": 11, "listing": 0}
    assert set(found.change) <= {made["name"] for made in found.record["presentations"]} and min(found.spread_cm) >= 0
    first = (d / OS.FILE).read_text(encoding="utf-8")
    P.measure_own_spread(models, d, "c1ccccc1")
    again = json.loads((d / OS.FILE).read_text(encoding="utf-8"))
    assert {k: v for k, v in again.items() if k != "seconds"} == {k: v for k, v in json.loads(first).items() if k != "seconds"}
    with pytest.raises(RuntimeError, match="names the models"):
        OS.measure_result((PIN_MODEL,), d, "c1ccccc1")


def test_the_split_of_step_4_gives_the_release_networks_correction_as_before():
    """`P.correction` is `seed_corrections(load_networks(...))` since 0.15: the same ΔH as each seed's operations done one by one."""
    require_frozen_corpus()
    models = tuple(A.M05_OUT / "v14" / n for n in RELEASE)
    if not all(p.is_file() for p in models):
        pytest.skip("v1.4's release checkpoints are not on this machine")
    folder = PIN_CORPUS / "molecules" / BENZENE
    direct = []
    for path in models:
        model, checkpoint = P.RT.load_hybrid_model(path)
        direct.append(P.RI.delta_H(model, P.RI.input_tensors_of(folder, P.RT.tensor_config(checkpoint))).numpy().astype(float))
    mean, seeds = P.correction(models, folder)
    assert len(seeds) == 3 and all(np.array_equal(a, b) for a, b in zip(seeds, direct, strict=True))
    assert np.array_equal(mean, np.mean(direct, axis=0)) and np.abs(mean).max() > 0


RING_FLIP = (0, 1, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 15, 17, 16, 26, 25, 24, 23, 22, 21, 20, 19, 18)
"""9-methylanthracene's two outer rings exchanged and two methyl hydrogens with them (aromir's pin)."""
STORED = {
    # name: (corpus folder, its SMILES, aromir's largest spread on v1.4, the presentation that gave it, bands beyond the line, bands)
    "benzene": (BENZENE, "c1ccccc1", 0.88, (2, 3, 4, 5, 0, 1, 8, 9, 10, 11, 6, 7), 0, 30),
    "benzonitrile": ("A_3100da3761", "N#Cc1ccccc1", 2.78, 7, 0, 33),
    "biphenyl": ("A_fdc27f1bd1", "c1ccc(-c2ccccc2)cc1", 2.85,
                 (0, 11, 10, 3, 4, 5, 6, 7, 8, 9, 2, 1, 12, 21, 20, 15, 16, 17, 18, 19, 14, 13), 0, 60),
    "9-methylanthracene": ("A_78896cfe24", "Cc1c2ccccc2cc2ccccc12", 9.95, RING_FLIP, 1, 75),
}
"""aromir's pins of 20 Nov 2026 (`tests/test_own_spread.py` at bb8eb62: `LARGEST_CM`, `BEYOND_THE_LINE`), measured there with v1.4's
release networks on these stored B3LYP Hessians in the canonical order: the presentation is a swap's atom order, or which of the
generator's rotations it was. 9-methylanthracene's band beyond the line is its methyl torsion, imaginary in the stored Hessian."""


@pytest.mark.parametrize("name", list(STORED))
def test_the_port_gives_aromirs_spread_on_a_stored_molecule_with_v14s_release_networks(tmp_path, name):
    mol_id, source, largest_cm, pinned, n_beyond, n_bands = STORED[name]
    models = tuple(A.M05_OUT / "v14" / n for n in RELEASE)
    src = P.CORPUS / mol_id
    if not all(p.is_file() for p in models) or not (src / R.HESSIAN).is_file():
        pytest.skip("v1.4's release checkpoints or the corpus folder are not on this machine")
    canonical = P.canonical_smiles(source)
    as_stored = OS.Molecule.of_folder(src)
    order = tuple(int(k) for k in R.atom_order(source, canonical, list(as_stored.symbols), as_stored.coords_bohr))
    with np.load(src / R.HESSIAN) as z:
        molecule, hessian = OS.reordered(as_stored, np.asarray(z["H_projected"], float), order)
    (tmp_path / R.GEOMETRY).write_text(json.dumps(molecule.geometry_record()), encoding="utf-8")
    np.savez(tmp_path / R.HESSIAN, H_projected=hessian)
    dH, seeds = P.correction(models, tmp_path)
    P.save_correction(tmp_path, dH, seeds, models)
    P.measure_own_spread(models, tmp_path, canonical)
    found = OS.of_result(tmp_path)
    worst = int(np.argmax(found.spread_cm))
    value, change = found.spread_cm[worst], found.change[worst]
    assert value == pytest.approx(largest_cm, abs=PIN_CM)
    assert len(found.spread_cm) == n_bands and sum(x > LINE for x in found.spread_cm) == n_beyond
    assert (np.abs(OS.modes_of(hessian + dH, molecule.masses_amu).wavenumbers) > vib_min_cm()).all()    # every mode is a band of the spectrum
    (made,) = [tried for tried in found.record["presentations"] if tried["name"] == change]
    if isinstance(pinned, tuple):
        assert made["order"] == list(pinned)
    else:
        rotations = [tried["matrix"] for tried in found.record["presentations"] if tried["kind"] == "rotation"]
        assert made["matrix"] == rotations[pinned - 1]
    assert found.record["counts"]["rotation"] == OS.N_ROTATIONS and found.record["counts"]["mirror image"] == 2
    assert found.record["counts"]["listing"] == 0
