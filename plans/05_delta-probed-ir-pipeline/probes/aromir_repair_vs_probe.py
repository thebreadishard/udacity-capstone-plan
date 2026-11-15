"""aromir's soft-mode repair against the probe's patch on a corpus molecule with a genuinely soft mode (TASKS 73, 216).

aromir's repair (`aromir.repair`) was validated in the cloud on water's bend with the threshold raised; no molecule with a mode below
20 cm⁻¹ was run there. `probes/low_mode_patch_run.py` patched D_ac28161d06's B3LYP label on 13 Nov (lowest mode −7.48 → +7.05 cm⁻¹)
and kept the direction and the measured column. Here `aromir.repair.repair` gets the same geometry and the same unpatched label
Hessian, and its repaired lowest mode and measured column are compared with the probe's.

The two differ on purpose in two places (`docs/HANDOFF_2026-11-15_aromir_stage4.md`): aromir's direction is the B3LYP Hessian's own
soft mode, the probe's is merged from both labels' soft modes; aromir calls pyscf's grid-response gradient, the probe the blocked one.
The record therefore carries the overlap of the two directions, and compares the two measured columns only through the cross
element u_probe · (H u_aromir) = u_aromir · (H u_probe), which both routes measured and which the Hessian's symmetry makes equal;
the columns themselves belong to different directions and differ by the stiff modes' share of that difference.

    python probes/aromir_repair_vs_probe.py --id D_ac28161d06 --out <folder> [--threads 8] [--max-memory 5000] [--dry-run]

Runs in an environment with aromir and pyscf 2.15.0 (WSL ~/aromir_v13). --dry-run loads everything, checks the unpatched Hessian's
lowest mode against the probe's record and stops before the first SCF.
"""
from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from aromir import repair as aromir_repair
from aromir import vibrations as aromir_vibrations
from aromir.dft import Resources
from aromir.molecule import Geometry
from aromir_common import aromir_symbol

PLAN = Path(__file__).resolve().parents[1]
CORPUS = PLAN / "modules" / "05_support_predictor" / "corpus"
UNPATCHED = CORPUS / "superseded_2026-11-14"          # the label Hessians as they were before the swap of 14 Nov
PROBE = PLAN / "probes" / "results_m1" / "low_mode_patch_2026-11-13" / "corpus"
LABEL = "hessian_b3lyp_analytic"
SAME_START_CM = 0.01                                   # the two routes start from the same Hessian only if its lowest mode agrees to this


@dataclass(frozen=True)
class Case:
    """One molecule as the probe patched it: the geometry, the unpatched label Hessian and what the probe measured."""

    molecule_id: str
    geometry: Geometry
    hessian: np.ndarray
    probe_direction: np.ndarray
    probe_column: np.ndarray
    probe_lowest_label_cm: float
    probe_lowest_patched_cm: float


def load_case(molecule_id: str) -> Case:
    stored = json.loads((CORPUS / "molecules" / molecule_id / "geometry.json").read_text(encoding="utf-8"))
    geometry = Geometry(tuple(aromir_symbol(s) for s in stored["symbols"]), np.array(stored["coords_bohr"], float))
    with np.load(UNPATCHED / molecule_id / f"{LABEL}.npz") as label:
        hessian = np.array(label["H_raw"], float)
    with np.load(PROBE / molecule_id / f"{LABEL}_grfpatch.npz") as patch:
        directions, columns = np.array(patch["directions"], float), np.array(patch["columns"], float)
    if directions.shape[1] != 1:
        raise SystemExit(f"{molecule_id}: the probe measured {directions.shape[1]} directions; this comparison is written for one")
    report = json.loads((PROBE / molecule_id / "report.json").read_text(encoding="utf-8"))["functionals"]["b3lyp"]
    return Case(molecule_id, geometry, hessian, directions[:, 0], columns[:, 0], report["lowest_label_cm"], report["lowest_patched_cm"])


def soft_direction(case: Case) -> np.ndarray:
    """aromir's own soft direction of the unpatched Hessian; refused unless it is exactly one and the start agrees with the probe's."""
    modes = aromir_vibrations.vibrational_modes(case.hessian, case.geometry)
    lowest = float(modes.wavenumbers[0])
    if abs(lowest - case.probe_lowest_label_cm) > SAME_START_CM:
        raise SystemExit(f"{case.molecule_id}: the unpatched Hessian's lowest mode is {lowest:.4f} cm-1 in aromir's arithmetic, the "
                         f"probe recorded {case.probe_lowest_label_cm:.4f}: not the same Hessian or geometry")
    soft = modes.vectors[:, np.abs(modes.wavenumbers) < aromir_repair.SOFT_BELOW_CM]
    if soft.shape[1] != 1:
        raise SystemExit(f"{case.molecule_id}: aromir finds {soft.shape[1]} soft modes, the probe measured one direction")
    return soft[:, 0]


def compare(case: Case, direction: np.ndarray, repaired: np.ndarray, record: aromir_repair.Repair) -> dict:
    """aromir's repaired Hessian against the probe's record: the lowest mode, the direction and the cross element of the
    two measured columns (mass-weighted, hartree/(bohr² mₑ), as `corpus/vibrations.column` stores the probe's)."""
    weights = aromir_vibrations.mass_weights(case.geometry.masses_amu)
    column = (repaired / np.outer(weights, weights)) @ direction
    sign = 1.0 if float(direction @ case.probe_direction) >= 0 else -1.0
    return {"id": case.molecule_id, "n_directions": record.n_directions,
            "lowest_before_cm": {"aromir": record.lowest_before_cm, "probe": case.probe_lowest_label_cm},
            "lowest_after_cm": {"aromir": record.lowest_after_cm, "probe": case.probe_lowest_patched_cm,
                                "difference": record.lowest_after_cm - case.probe_lowest_patched_cm},
            "largest_change_cm": record.largest_change_cm,
            "direction_overlap": abs(float(direction @ case.probe_direction)),
            "curvature_along_own_direction_au": {"aromir": float(direction @ column),
                                                 "probe": float(case.probe_direction @ case.probe_column)},
            "cross_curvature_au": {"probe_direction_on_aromir_column": sign * float(case.probe_direction @ column),
                                   "aromir_direction_on_probe_column": sign * float(direction @ case.probe_column)}}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--id", required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--threads", type=int, default=8)
    ap.add_argument("--max-memory", type=int, default=5000, help="pyscf's max_memory, MB; aromir refuses the gradient when it cannot fit")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    case = load_case(a.id)
    direction = soft_direction(case)
    print(f"(ARVP) {a.id}: {case.geometry.n_atoms} atoms, lowest mode {case.probe_lowest_label_cm:.4f} cm-1 in both arithmetics, "
          f"overlap of aromir's soft direction with the probe's {abs(float(direction @ case.probe_direction)):.6f}", flush=True)
    if a.dry_run:
        return
    a.out.mkdir(parents=True, exist_ok=True)
    with (a.out / "pyscf.log").open("w", encoding="utf-8") as log:
        repaired, record = aromir_repair.repair(case.geometry, case.hessian, Resources(threads=a.threads, max_memory_mb=a.max_memory), log)
    if record is None:
        raise SystemExit(f"{a.id}: aromir's repair found no soft mode after soft_direction found one")
    result = compare(case, direction, repaired, record)
    tmp_hessian = a.out / "repaired_hessian.tmp.npz"
    np.savez_compressed(tmp_hessian, H_raw=repaired, direction=direction)
    os.replace(tmp_hessian, a.out / "repaired_hessian.npz")
    tmp = a.out / "aromir_repair_vs_probe.json.tmp"
    tmp.write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8")
    os.replace(tmp, a.out / "aromir_repair_vs_probe.json")
    after, cross = result["lowest_after_cm"], result["cross_curvature_au"]
    print(f"(ARVP) lowest mode after the repair: aromir {after['aromir']:.4f} cm-1, the probe {after['probe']:.4f} "
          f"(difference {after['difference']:+.4f}); cross element {cross['probe_direction_on_aromir_column']:.4e} (aromir's "
          f"column) against {cross['aromir_direction_on_probe_column']:.4e} (the probe's)", flush=True)


if __name__ == "__main__":
    main()
