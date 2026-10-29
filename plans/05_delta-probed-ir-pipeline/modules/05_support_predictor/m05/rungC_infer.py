"""The ΔH network on a molecule without its truth — the pipeline's step 4 (TASKS 146; `modules/08_industry_synthesis/
PIPELINE_BUILD_NOTE_2026-10-29.md`). A folder holds the molecule's geometry (`geometry.json`, the corpus deck's optimisation) and its
analytic B3LYP Hessian (`hessian_b3lyp_analytic.npz`, `corpus/analytic_hessians.py`); no ωB97X Hessian is read.

The inputs are built by the training path's own functions — `rungC_equivariant.low_level_inputs`, the rung-B loader's internal coordinates
(`e7_t2_sqm.internals`, `to_internal`), `rungC_train.input_tensors` — so that a corpus molecule gives the trainer's tensors and the trainer's
ΔH to the bit (`tests/test_rungC_infer.py`).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import e7_t2_sqm as T2
from learning_curve_layerA import normal_modes
from rungC_equivariant import low_level_inputs
from rungC_train import TensorSettings, input_tensors

LOW_HESSIAN = "hessian_b3lyp_analytic.npz"


def low_level(d: Path) -> tuple[dict, dict]:
    """(m, mol) of one folder, as the trainer's loader builds them under --use-analytic: the Cartesian inputs, and the internal-coordinate
    entry — Wilson B and its primitive types, the low level's internal force constants F_low, the masses, its normal modes (w, freq, V)
    and the charge index."""
    path = d / LOW_HESSIAN
    if not path.exists():
        raise FileNotFoundError(f"{d.name}: no {LOW_HESSIAN} (corpus/analytic_hessians.py writes it)")
    with np.load(path) as z:
        lo = z["H_projected"]
    m = low_level_inputs(d, lo)
    B, types = T2.internals(m["symbols"], m["pos"])
    F_low, _ = T2.to_internal(lo, B)
    w, freq, V, _ = normal_modes(lo, m["masses"])
    return m, {"B": B, "types": types, "F_low": F_low, "masses": m["masses"], "w": w, "freq": freq, "V": V, "qidx": m["qidx"]}


def input_tensors_of(d: Path, cfg: TensorSettings) -> dict:
    """The network's input tensors for one folder (`rungC_train.input_tensors` on `low_level`)."""
    m, mol = low_level(d)
    return input_tensors(m, mol, d, cfg)


def delta_H(model: torch.nn.Module, t: dict) -> torch.Tensor:
    """The model's Cartesian ΔH (hartree/bohr², the low level's frame) for one molecule's input tensors."""
    model.eval()
    with torch.no_grad():
        return model(t["Z"], t["pos"], t["H_low"], t)
