"""Is the label's −9.5 cm⁻¹ butterfly of D_ac28161d06 pyscf 2.14.0's Krylov CPHF? (TASKS 49; the user, 12 Nov 2026: test the CPHF cause on
D_ac28161d06 with 2.15.0.)

Option 3 (`probes/butterfly_fd.py`, fd.json) found the mode real: gradients without the grid response, at the label grid (99,590), give a
curvature of +3.4/+3.6 cm⁻¹ along the label Hessian's lowest mode v, against the label's own −9.46. Gradients and the analytic Hessian share
the frozen-grid energy, so the two should agree; the candidate registered there is 2.14.0's multi-root Krylov CPHF, which stops before its
solution satisfies its equations (software ledger 44; pyscf#3384, in 2.15.0). Here pyscf 2.15.0 computes the analytic B3LYP Hessian at the
label geometry with the labels' own SCF and Hessian call (`analytic_hessians.labels_scf`, then `mf.Hessian().kernel()`), so it differs
from the label in the pyscf version only, and the curvature along the same v.

Verdict, registered before the run, on f215 = the 2.15.0 Hessian's frequency along v:
    CPHF        |f215 − control| ≤ CONTROL_TOLERANCE_CM for the control at both steps of the label grid (option 3's rows)
    NOT CPHF    |f215 − label| ≤ CONTROL_TOLERANCE_CM, the label's own frequency along v
    UNRESOLVED  otherwise
Beside it: both Hessians' projected frequencies, their per-mode difference and translation residuals.

    python probes/cphf_check_215.py <label folder> <option 3 fd.json> <out dir> [--threads 8] [--max-memory MB] [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TextIO

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "modules" / "05_support_predictor" / "corpus"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from analytic_hessians import FUNCTIONALS, labels_mol, labels_scf
from butterfly_fd import CONTROL_TOLERANCE_CM, Mode, frequency_cm, lowest_mode
from butterfly_scan import LABEL_GRID, write_json
from hessian_grid_response_fd import frequencies
from library_log import PYSCF_LOG_NAME
from pyscf import __version__ as pyscf_version
from pyscf import lib
from qc_common import translation_residual, write_atomic

XC = "b3lyp"
LOW_MODE_CM = 100.0


@dataclass(frozen=True)
class CphfCheckConfig:
    """The check's settings, checked before any input is read."""

    molecule: Path
    option3: Path
    out: Path
    threads: int
    max_memory_mb: int
    dry_run: bool

    def __post_init__(self) -> None:
        if self.threads < 1 or self.max_memory_mb < 1000:
            raise ValueError(f"threads {self.threads} (≥ 1), max memory {self.max_memory_mb} MB (≥ 1000)")
        for path in (self.molecule / "geometry.json", self.molecule / f"hessian_{XC}_analytic.npz", self.option3):
            if not path.is_file():
                raise FileNotFoundError(f"{path} is missing")


def controls_at_label_grid(option3: dict[str, Any]) -> list[float]:
    """Option 3's frozen-grid curvatures (cm-1) along v at the label grid, one per step; raises when the record does not hold them."""
    if option3.get("xc") != XC:
        raise ValueError(f"option 3's record is for {option3.get('xc')}, not {XC}")
    controls = [float(r["control"]) for r in option3["rows"] if tuple(r["grid"]) == LABEL_GRID]
    if len(controls) < 2:
        raise ValueError(f"option 3's record holds {len(controls)} control rows at {LABEL_GRID}; two steps are needed")
    return controls


def frequency_along(mode: Mode, H: np.ndarray) -> float:
    """The signed frequency (cm-1) of the Hessian H (Cartesian, hartree/bohr²) along the mass-weighted mode vector v."""
    Hmw = 0.5 * (H + H.T) / np.outer(mode.sqrt_m, mode.sqrt_m)
    return frequency_cm(float(mode.v @ Hmw @ mode.v))


def verdict(f215: float, label: float, controls: list[float]) -> str:
    """CPHF, NOT CPHF or UNRESOLVED, the module docstring's rule."""
    if all(abs(f215 - c) <= CONTROL_TOLERANCE_CM for c in controls):
        return "CPHF"
    if abs(f215 - label) <= CONTROL_TOLERANCE_CM:
        return "NOT CPHF"
    return "UNRESOLVED"


def compare(H_label: np.ndarray, H_215: np.ndarray, masses: np.ndarray, coords: np.ndarray, controls: list[float]) -> dict[str, Any]:
    """The verdict and the two Hessians side by side: frequencies along v, projected frequencies, per-mode difference, translation residuals."""
    mode = lowest_mode(coords, masses, H_label)
    along = {"label": frequency_along(mode, H_label), "analytic_215": frequency_along(mode, H_215)}
    freq = {"label": frequencies(H_label, masses, coords), "analytic_215": frequencies(H_215, masses, coords)}
    delta = freq["analytic_215"] - freq["label"]
    low = freq["label"] < LOW_MODE_CM
    residual = {name: translation_residual(H, masses) for name, H in (("label", H_label), ("analytic_215", H_215))}
    return {"verdict": verdict(along["analytic_215"], along["label"], controls), "tolerance_cm": CONTROL_TOLERANCE_CM,
            "along_v_cm": along, "controls_label_grid_cm": controls,
            "lowest_cm": {k: float(v[0]) for k, v in freq.items()},
            "difference_215_minus_label": {"rms_cm": float(np.sqrt(np.mean(delta**2))), "max_abs_cm": float(np.abs(delta).max()),
                                           "rms_below_100_cm": float(np.sqrt(np.mean(delta[low] ** 2))) if low.any() else None,
                                           "modes_below_100": int(low.sum()), "per_mode_cm": delta.tolist()},
            "translation": {k: {"max_Ht": r[0], "frequencies_cm": r[1]} for k, r in residual.items()},
            "frequencies_cm": {k: v.tolist() for k, v in freq.items()}}


def markdown(record: dict[str, Any]) -> str:
    """The report: the verdict, the curvature along v by three routes, and the whole-spectrum difference."""
    a, d = record["along_v_cm"], record["difference_215_minus_label"]
    controls = " / ".join(f"{c:+.2f}" for c in record["controls_label_grid_cm"])
    lines = [f"# CPHF check, {record['molecule']} ({XC}, grid {tuple(record['grid'])}, pyscf {record['pyscf']})", "",
             f"Verdict: **{record['verdict']}** (tolerance {record['tolerance_cm']} cm-1)", "",
             "| route | frequency along v (cm-1) |", "|---|---|",
             f"| label (pyscf 2.14.0 analytic) | {a['label']:+.2f} |",
             f"| pyscf {record['pyscf']} analytic | {a['analytic_215']:+.2f} |",
             f"| option 3 control (frozen-grid gradients, steps 0.01/0.02 bohr) | {controls} |", "",
             f"Lowest projected frequency: label {record['lowest_cm']['label']:+.2f}, {record['pyscf']} "
             f"{record['lowest_cm']['analytic_215']:+.2f} cm-1.",
             f"Per mode, {record['pyscf']} minus label: rms {d['rms_cm']:.3f}, max |Δ| {d['max_abs_cm']:.3f} cm-1; "
             f"below 100 cm-1 ({d['modes_below_100']} modes) rms {d['rms_below_100_cm']} cm-1.",
             "Translation residual max|H t|: " + ", ".join(f"{k} {v['max_Ht']:.2e}" for k, v in record["translation"].items()) + "."]
    return "\n".join(lines) + "\n"


def analytic_hessian(geometry: dict, max_memory_mb: int, lib_log: TextIO) -> np.ndarray:
    """The labels route's B3LYP Hessian (3N, 3N), symmetrised, at the label grid, on the running pyscf."""
    mol = labels_mol(geometry, lib_log, max_memory=max_memory_mb)
    mf, _energy = labels_scf(mol, dict(FUNCTIONALS)[XC], LABEL_GRID, newton_finish=True)
    n3 = 3 * mol.natm
    H = mf.Hessian().kernel().transpose(0, 2, 1, 3).reshape(n3, n3)
    return 0.5 * (H + H.T)


def parse_args(argv: list[str] | None = None) -> CphfCheckConfig:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("molecule", type=Path, help="folder with geometry.json and hessian_b3lyp_analytic.npz (the label)")
    ap.add_argument("option3", type=Path, help="option 3's fd.json for the same molecule")
    ap.add_argument("out", type=Path)
    ap.add_argument("--threads", type=int, default=8)
    ap.add_argument("--max-memory", type=int, default=6144)
    ap.add_argument("--dry-run", action="store_true", help="read the inputs and build the molecule, compute nothing")
    a = ap.parse_args(argv)
    return CphfCheckConfig(a.molecule, a.option3, a.out, a.threads, a.max_memory, a.dry_run)


def main(argv: list[str] | None = None) -> None:
    cfg = parse_args(argv)
    geometry = json.loads((cfg.molecule / "geometry.json").read_text(encoding="utf-8"))
    coords, masses = np.asarray(geometry["coords_bohr"], dtype=float), np.asarray(geometry["masses_amu"], dtype=float)
    with np.load(cfg.molecule / f"hessian_{XC}_analytic.npz") as z:
        H_label = np.asarray(z["H_raw"], dtype=float)
    controls = controls_at_label_grid(json.loads(cfg.option3.read_text(encoding="utf-8")))
    label_along = frequency_along(lowest_mode(coords, masses, H_label), H_label)
    if cfg.dry_run:
        with open(os.devnull, "w", encoding="utf-8") as quiet:
            mol = labels_mol(geometry, quiet, max_memory=cfg.max_memory_mb)
        print(f"(CPHF) dry run: {cfg.molecule.name}, {mol.natm} atoms, {mol.nao} basis functions; label along v {label_along:+.2f} cm-1, "
              f"controls {controls}", flush=True)
        return
    lib.num_threads(cfg.threads)
    cfg.out.mkdir(parents=True, exist_ok=True)
    with open(cfg.out / PYSCF_LOG_NAME, "a", encoding="utf-8") as lib_log:
        H_215 = analytic_hessian(geometry, cfg.max_memory_mb, lib_log)
    print(f"(CPHF) {cfg.molecule.name}: pyscf {pyscf_version} analytic Hessian done", flush=True)
    np.savez_compressed(cfg.out / f"hessian_{XC}_analytic_{pyscf_version.replace('.', '')}.npz", H_raw=H_215, grid=np.array(LABEL_GRID))
    record = {"molecule": cfg.molecule.name, "xc": XC, "grid": list(LABEL_GRID), "pyscf": pyscf_version,
              **compare(H_label, H_215, masses, coords, controls)}
    write_json(cfg.out / "report.json", record)
    write_atomic(cfg.out / "report.md", markdown(record))
    print(markdown(record), flush=True)
    print(f"(CPHF) verdict {record['verdict']}", flush=True)


if __name__ == "__main__":
    main()
