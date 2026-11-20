"""Label Hessians repaired along their low modes with grid-response curvature (TASKS 201 step 3; the user, 12 Nov 2026: problems are solved
at the source, not swept under the rug).

pyscf's CPU DFT Hessian leaves out the derivative of the quadrature weights (software ledger 56). TASKS 201 step 2 measured what that does
to vibrations: B_0f06474656's lowest B3LYP mode moves from 9.5 to 15.7 cm⁻¹ against a finite-difference Hessian of grid-response gradients,
while every other mode of it and of benzene moves less than 0.43 cm⁻¹. The error lives in the low modes, so only those are repaired.

For a set of mass-weighted directions U (orthonormal columns, inside the vibrational space) the true Hessian's columns C = H U come from
central differences of grid-response gradients along each direction. The repaired mass-weighted Hessian keeps the label outside span(U)
and takes the measured columns inside it:

    H' = Q H Q + C Uᵀ + U Cᵀ − U S Uᵀ,   Q = 1 − U Uᵀ,   S = (UᵀC + CᵀU) / 2,

which is exact when the label's error lies in the rows and columns along U (TASKS 49's option 3: the patched lowest mode of
D_ac28161d06 agreed with the gradient and energy routes to 0.04 cm⁻¹). The directions are the label modes below LOW_MODE_CM in either
functional, merged into one orthonormal set, so both functionals are repaired along the same directions.

This module is numpy only (the arithmetic, and `select` with its command line); probes/low_mode_patch_run.py computes the gradients.

    python probes/low_mode_patch.py <corpus molecules dir> <ids out> [--below 20]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from qc_common import write_atomic

CORPUS_CODE = Path(__file__).resolve().parents[1] / "modules" / "05_support_predictor" / "corpus"
RUN_SETTINGS_NAME = "run_settings.json"   # in a patch run's out folder: the step, threshold and grid its points were made with
sys.path.insert(0, str(CORPUS_CODE))
from vibrations import (  # noqa: E402  (the arithmetic lives beside the label route that runs it now: TASKS 216)
    LABEL_TAGS,
    LOW_MODE_CM,
    low_mode_directions,
    vibrational_modes,
)


def read_label(molecule_dir: Path) -> tuple[dict, dict[str, np.ndarray]]:
    """A corpus folder's geometry.json and its two analytic label Hessians (H_raw, hartree/bohr²) by functional tag."""
    geometry = json.loads((molecule_dir / "geometry.json").read_text(encoding="utf-8"))
    hessians = {}
    for tag in LABEL_TAGS:
        with np.load(molecule_dir / f"hessian_{tag}_analytic.npz") as z:
            hessians[tag] = np.asarray(z["H_raw"], float)
    return geometry, hessians


def label_directions(molecule_dir: Path, below_cm: float = LOW_MODE_CM) -> np.ndarray:
    """The merged low-mode directions (3N, k) of one corpus folder's two analytic labels."""
    geometry, hessians = read_label(molecule_dir)
    masses, coords = np.asarray(geometry["masses_amu"], float), np.asarray(geometry["coords_bohr"], float)
    return low_mode_directions([vibrational_modes(H, masses, coords) for H in hessians.values()], below_cm)


def settings_conflict(recorded: dict | None, wanted: dict, has_results: bool) -> str | None:
    """Why the runner may not write into an out folder with the settings `wanted`, or None when it may. The runner keeps every point
    file and every finished molecule it finds, so a folder made at another step or threshold would mix two measurements; a folder with
    results and no record of its settings (made before 20 November 2026) cannot be told apart from one."""
    if recorded is None:
        if has_results:
            return f"the out folder holds results but no {RUN_SETTINGS_NAME}: their step and threshold are unknown, so nothing is reused; " \
                   "give a fresh out folder"
        return None
    different = {key: (recorded.get(key), value) for key, value in wanted.items() if recorded.get(key) != value}
    if different:
        return "the out folder was made with other settings (" + ", ".join(f"{k}: {old} there, {new} asked" for k, (old, new) in
                                                                         different.items()) + "); give a fresh out folder"
    return None


def select(molecules: Path, below_cm: float = LOW_MODE_CM) -> dict[str, int]:
    """Every corpus folder with both analytic labels and at least one low-mode direction, with its count."""
    dirs = sorted(d for d in molecules.iterdir() if all((d / f"hessian_{t}_analytic.npz").is_file() for t in LABEL_TAGS))
    counts = {d.name: int(label_directions(d, below_cm).shape[1]) for d in dirs}
    return {i: n for i, n in counts.items() if n}


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description="Write the ids of the corpus folders whose labels have modes below the threshold.")
    ap.add_argument("molecules", type=Path)
    ap.add_argument("ids_out", type=Path)
    ap.add_argument("--below", type=float, default=LOW_MODE_CM)
    a = ap.parse_args(argv)
    chosen = select(a.molecules, a.below)
    lines = [f"# low_mode_patch.py select: folders with label modes below {a.below} cm⁻¹ (id, directions)"]
    write_atomic(a.ids_out, "\n".join([*lines, *(f"{i} {n}" for i, n in chosen.items())]) + "\n")
    print(f"{len(chosen)} molecules, {sum(chosen.values())} directions below {a.below} cm⁻¹ → {a.ids_out}")


if __name__ == "__main__":
    main()
