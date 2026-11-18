"""How a corpus folder was labelled, without the trainer's imports (torch): module 08's spectrum and the Atlas export read it per molecule.

One definition, imported by `learning_curve_layerA` (which re-exports it for its callers) and by `m08.spectrum`."""
from __future__ import annotations

import json
from pathlib import Path

ANALYTIC_ONLY = "analytic_only"   # result.json "labels" of a folder labelled by analytic_hessians.py alone, no psi4 layer (TASKS 49, 12 Oct 2026)


def is_analytic_only(mol_dir: str | Path) -> bool:
    """A folder without the psi4 FD pair whose result.json says labels 'analytic_only' and which has both analytic Hessians."""
    mol_dir = Path(mol_dir)
    if (mol_dir / "hessian_b3lyp.npz").exists() or (mol_dir / "hessian_wb97x.npz").exists():
        return False
    if not ((mol_dir / "hessian_b3lyp_analytic.npz").exists() and (mol_dir / "hessian_wb97x_analytic.npz").exists()):
        return False
    result = mol_dir / "result.json"
    if not result.exists():
        return False
    with open(result, encoding="utf-8") as f:
        return json.load(f).get("labels") == ANALYTIC_ONLY
