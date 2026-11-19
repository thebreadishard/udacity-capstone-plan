"""An optimisation that forms or breaks a bond is refused before the Hessian (`modules/08_industry_synthesis/m08/molecule.py`
`changed_bonds`, `m08/pipeline.py` `same_molecule`; TASKS 279; aromir's `tests/test_geometry.py` and `tests/test_pipeline.py` at commit
52cf119). The geometries are made, not optimised: no quantum chemistry runs."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np
import pytest
from rdkit import Chem

from pin_tools import DATA, PLAN
from test_m08_xyz_listings import LISTING_FREE, SMALL_RINGS, TRAINING_BIPHENYLENES, distorted, listed_xyz

sys.path.insert(0, str(PLAN / "modules" / "08_industry_synthesis"))
from m08 import molecule as M
from m08 import pipeline as P

PIN_MODEL = DATA / "rungC_cc_pin_model.pt"
ZWITTERION = "[NH3+]c1ccccc1C(=O)[O-]"
"""aromir's: anthranilic acid's zwitterion, whose proton B3LYP moves back to the acid in the gas phase."""
PROTON_TO_OXYGEN_ANGSTROM = 1.0
RING_OPENED_BY_ANGSTROM = 0.8          # aromir's 1.5 bohr


def config(tmp_path: Path, **kw) -> P.PipelineConfig:
    base = dict(name="mol", out_root=tmp_path, smiles="c1ccccc1", models=(PIN_MODEL,), psi4_python=Path(sys.executable))
    return P.PipelineConfig(**(base | kw))


def start(tmp_path: Path, smiles: str) -> tuple[str, list[str], np.ndarray]:
    """(the admitted canonical SMILES, the symbols, the coordinates in Å) of the pipeline's start geometry from a SMILES."""
    atoms, _ = P.start_geometry(config(tmp_path, smiles=smiles))
    return P.canonical_smiles(smiles), [a[0] for a in atoms], np.array([a[1:] for a in atoms], float)


def proton_moved(smiles: str, symbols: list[str], xyz: np.ndarray) -> np.ndarray:
    """aromir's `proton_moved`: an N–H proton put at `PROTON_TO_OXYGEN_ANGSTROM` from the O⁻, along its old direction from it."""
    molecule = Chem.AddHs(Chem.MolFromSmiles(smiles))
    proton = next(a.GetIdx() for a in molecule.GetAtoms() if a.GetSymbol() == "H" and a.GetNeighbors()[0].GetSymbol() == "N")
    oxygen = next(a.GetIdx() for a in molecule.GetAtoms() if a.GetFormalCharge() < 0)
    moved = xyz.copy()
    away = moved[proton] - moved[oxygen]
    moved[proton] = moved[oxygen] + PROTON_TO_OXYGEN_ANGSTROM * away / np.linalg.norm(away)
    return moved


def test_a_start_geometry_keeps_the_bonds_of_its_smiles(tmp_path):
    assert M.changed_bonds(*start(tmp_path, ZWITTERION)) == []


def test_a_proton_that_moved_is_named_by_the_bond_it_broke_and_the_one_it_formed(tmp_path):
    smiles, symbols, xyz = start(tmp_path, ZWITTERION)
    changes = M.changed_bonds(smiles, symbols, proton_moved(smiles, symbols, xyz))
    assert len(changes) == 2
    assert re.fullmatch(r"the bond N\d+–H\d+ broke", changes[0])
    assert re.fullmatch(r"a bond O\d+–H\d+ formed", changes[1])


def test_a_ring_that_opened_is_named(tmp_path):
    smiles, symbols, xyz = start(tmp_path, "c1ccccc1")
    xyz[0] += RING_OPENED_BY_ANGSTROM * (xyz[0] - xyz[1]) / np.linalg.norm(xyz[0] - xyz[1])
    assert "the bond C1–C2 broke" in M.changed_bonds(smiles, symbols, xyz)


def test_the_diagonals_of_every_training_biphenylene_are_no_bonds_formed(tmp_path):
    for smiles in TRAINING_BIPHENYLENES:
        named, symbols, xyz = start(tmp_path, smiles)
        for variant in distorted([[s, *r] for s, r in zip(symbols, xyz, strict=True)]):
            assert M.changed_bonds(named, symbols, np.array([a[1:] for a in variant])) == [], smiles


@pytest.mark.parametrize("smiles", SMALL_RINGS)
def test_a_small_ring_keeps_its_bonds_and_gains_none(tmp_path, smiles):
    named, symbols, xyz = start(tmp_path, smiles)
    for variant in distorted([[s, *r] for s, r in zip(symbols, xyz, strict=True)]):
        assert M.changed_bonds(named, symbols, np.array([a[1:] for a in variant])) == []


def test_psi4s_upper_case_symbols_are_read(tmp_path):
    smiles, symbols, xyz = start(tmp_path, "Clc1ccccc1")
    assert "Cl" in symbols and M.changed_bonds(smiles, [s.upper() for s in symbols], xyz) == []


def test_a_geometry_of_other_atoms_is_an_error(tmp_path):
    _, symbols, xyz = start(tmp_path, "c1ccccc1")
    with pytest.raises(ValueError, match="are not those of"):
        M.changed_bonds("c1ccncc1", symbols, xyz)


@pytest.mark.parametrize("smiles", LISTING_FREE)
def test_an_xyz_request_in_the_pipelines_order_keeps_its_bonds(tmp_path, monkeypatch, smiles):
    """The xyz route's start geometry is in the SMILES route's order (`xyz_order`), so the admitted SMILES's bonds are its own."""
    monkeypatch.setattr(P.MR, "require_carried", lambda p, kind=None: {"status": "carried", "network": P.NETWORK, "version": "pin"})
    monkeypatch.setattr(P, "training_set", lambda models: (("C", "H", "N", "O"), (6, 40)))
    made, _ = P.start_geometry(config(tmp_path, smiles=smiles))
    for seed in range(3):
        cfg = config(tmp_path, smiles=None, xyz=listed_xyz(tmp_path / f"{seed}.xyz", made, seed))
        atoms, _ = P.start_geometry(cfg)
        named = P.admit(cfg).smiles
        assert M.changed_bonds(named, [a[0] for a in atoms], np.array([a[1:] for a in atoms])) == []


def fake_optimisation(cfg: P.PipelineConfig, symbols: list[str], xyz: np.ndarray):
    """A psi4 run that writes `xyz` (Å) as its optimised geometry."""
    def run(argv, log, what):
        (cfg.folder / "result.json").write_text(json.dumps({"status": "done", "e_opt": -1.0}), encoding="utf-8")
        geometry = {"symbols": [s.upper() for s in symbols], "coords_bohr": (xyz / P.R.BOHR_ANGSTROM).tolist()}
        (cfg.folder / "geometry.json").write_text(json.dumps(geometry), encoding="utf-8")
        return 0
    return run


def test_an_optimisation_that_moved_a_proton_is_refused_before_the_hessian(tmp_path, monkeypatch):
    cfg = config(tmp_path, smiles=ZWITTERION, reuse_corpus=False)
    cfg.folder.mkdir()
    smiles, symbols, xyz = start(tmp_path, ZWITTERION)
    monkeypatch.setattr(P, "_run", fake_optimisation(cfg, symbols, proton_moved(smiles, symbols, xyz)))
    monkeypatch.setattr(P, "low_level", lambda cfg: pytest.fail("the Hessian step ran on another molecule"))
    with pytest.raises(P.AnotherMolecule, match=r"another molecule than .*: the bond N\d+–H\d+ broke; a bond O\d+–H\d+ formed"
                                                r" \(atoms numbered in the canonical order\)\. Its spectrum would be named after a "
                                                r"molecule it is not\. The geometry is kept in "):
        P.low_level_files(cfg, {}, P.Progress(cfg.folder, cfg.name, P.PIPELINE_VERSION, {}))
    assert (cfg.folder / "geometry.json").is_file()


def test_an_optimisation_that_kept_the_bonds_goes_on(tmp_path, monkeypatch):
    cfg = config(tmp_path, smiles=ZWITTERION)
    cfg.folder.mkdir()
    _, symbols, xyz = start(tmp_path, ZWITTERION)
    monkeypatch.setattr(P, "_run", fake_optimisation(cfg, symbols, xyz))
    assert P.optimise(cfg, [], None)["status"] == "done"
