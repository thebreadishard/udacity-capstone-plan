"""Re-optimise a corpus molecule at the labels route's own settings, into a new folder (TASKS 49, chain 42's sixth large molecule).

The corpus optimises with psi4 (B3LYP/6-31G*, density fitting, grid 75/302); the labels are pyscf analytic Hessians at B3LYP/6-31G* with
Cartesian d, no density fitting and an unpruned (99,590) grid (`analytic_hessians.py`). A soft mode can then come out slightly negative at
the labels' settings (D_ac28161d06: -7.48 cm-1), and the trainer drops a molecule with any negative mode. Chain 42's registration
(PreRegistration_2026-10-12_Large_PAH_Size_Test.md) gives such a molecule one pyscf re-optimisation at the label settings.

1. The folder's geometry is displaced along its lowest B3LYP analytic mode when that mode is negative: a start on a symmetric saddle would
   otherwise stay there, because the gradient along an antisymmetric mode is zero.
2. geomeTRIC optimises at the labels' SCF (`labels_mol`, `labels_ks`), called as pyscf's own pyscf/geomopt/test/test_geometric_solver.py
   (test_optimize_with_hessian) calls `geometric_solver.kernel`; a run that does not converge raises.
3. A new folder receives job.json (copied), result.json (labels "analytic_only", the re-optimisation recorded) and geometry.json, written
   last, so its presence means the optimisation is complete. `analytic_hessians.py <out>` then adds the Hessians and the imaginary counts.
The source folder is only read.

    python probes/reoptimise_at_label_settings.py <source molecule dir> <out molecule dir> [--threads 8] [--max-memory 11704]
        [--grid 99,590] [--push-bohr 0.05] [--dry-run]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TextIO

import numpy as np

CORPUS_CODE = Path(__file__).resolve().parents[1] / "modules" / "05_support_predictor" / "corpus"
sys.path.insert(0, str(CORPUS_CODE))
from analytic_hessians import (  # noqa: E402  (the corpus code lives in the module's folder, not on the path)
    AMU2AU,
    AU2CM,
    FUNCTIONALS,
    MAX_MEMORY_MB,
    freqs_cm,
    labels_ks,
    labels_mol,
    software,
    vib_only,
)
from library_log import PYSCF_LOG_NAME  # noqa: E402
from pyscf import lib  # noqa: E402
from pyscf.geomopt import geometric_solver  # noqa: E402

LABEL_XC = dict(FUNCTIONALS)["b3lyp"]
LABEL_GRID = "99,590"                  # analytic_hessians.py's default grid: the labels are computed there
MAX_STEPS = 100
# tight: a soft mode of a few cm-1 decides the sign of the lowest frequency, so the minimum must be found well below geomeTRIC's defaults
CONVERGENCE = {"convergence_energy": 1e-7, "convergence_grms": 1e-5, "convergence_gmax": 2e-5, "convergence_drms": 1e-4,
               "convergence_dmax": 2e-4}
N_TRANS_ROT = 6
MODE_CHECK_TOL_CM = 1e-6               # the lowest frequency by the eigenvector route against freqs_cm's


@dataclass(frozen=True)
class Reoptimisation:
    """One re-optimisation's settings, checked before any SCF runs."""

    source: Path
    out: Path
    threads: int
    max_memory_mb: int
    grid: tuple[int, int]
    push_bohr: float
    dry_run: bool

    def __post_init__(self) -> None:
        for name in ("geometry.json", "result.json", "job.json", "hessian_b3lyp_analytic.npz"):
            if not (self.source / name).is_file():
                raise ValueError(f"{self.source} has no {name}")
        if self.out.resolve() == self.source.resolve():
            raise ValueError("the out folder is the source folder; the source is only read")
        if (self.out / "geometry.json").exists():
            raise ValueError(f"{self.out} already holds a geometry.json: the optimisation is done, not repeated")
        if self.threads < 1 or self.max_memory_mb < 500:
            raise ValueError(f"threads {self.threads} / max_memory {self.max_memory_mb} MB out of range")
        if len(self.grid) != 2 or min(self.grid) < 1:
            raise ValueError(f"grid {self.grid} is not two positive integers (radial, angular)")
        if not 0.0 <= self.push_bohr <= 0.5:
            raise ValueError(f"push {self.push_bohr} bohr outside [0, 0.5]")


def lowest_mode(H_projected: np.ndarray, masses: np.ndarray) -> tuple[float, np.ndarray]:
    """The lowest vibrational frequency (cm-1, negative when imaginary) and its Cartesian displacement (N, 3), scaled so the largest atom
    moves by 1 bohr. Cross-checked against `freqs_cm`/`vib_only`, the corpus's own frequency route."""
    sm = np.sqrt(np.repeat(masses, 3))
    w, V = np.linalg.eigh(H_projected / np.outer(sm, sm))
    vib = np.argsort(np.abs(w))[N_TRANS_ROT:]
    k = vib[np.argmin(w[vib])]
    freq = float(np.sign(w[k]) * np.sqrt(abs(w[k]) / AMU2AU) * AU2CM)
    reference = float(vib_only(freqs_cm(H_projected, masses))[0])
    if abs(freq - reference) > MODE_CHECK_TOL_CM:
        raise RuntimeError(f"lowest frequency {freq:.6f} by the eigenvectors, {reference:.6f} by freqs_cm")
    cart = (V[:, k] / sm).reshape(-1, 3)
    return freq, cart / np.linalg.norm(cart, axis=1).max()


def start_geometry(geometry: dict, H_projected: np.ndarray, push_bohr: float) -> tuple[dict, dict]:
    """The geometry the optimisation starts from and a record of the push (none when the lowest mode is not negative)."""
    masses = np.asarray(geometry["masses_amu"], dtype=float)
    freq, mode = lowest_mode(H_projected, masses)
    push = push_bohr if freq < 0 else 0.0
    start = dict(geometry, coords_bohr=(np.asarray(geometry["coords_bohr"], dtype=float) + push * mode).tolist())
    return start, {"lowest_mode_cm": freq, "push_bohr_largest_atom": push}


def optimise(start: dict, cfg: Reoptimisation, lib_log: TextIO) -> tuple[np.ndarray, float, int]:
    """geomeTRIC at the labels' SCF; returns the converged coordinates (bohr), the last energy and the number of gradient steps."""
    mol = labels_mol(start, lib_log, max_memory=cfg.max_memory_mb)
    mf = labels_ks(mol, LABEL_XC, cfg.grid)
    steps: list[float] = []

    def report(env: dict[str, Any]) -> None:
        steps.append(float(env["energy"]))
        gmax = float(np.abs(env["gradients"]).max())
        print(f"(RLS) step {len(steps)} E {steps[-1]:.10f} gmax {gmax:.2e} {time.strftime('%F %T')}", flush=True)

    # assert_convergence: an unconverged SCF at any step raises instead of feeding the optimiser a wrong gradient
    converged, mol_eq = geometric_solver.kernel(mf, assert_convergence=True, callback=report, maxsteps=MAX_STEPS, **CONVERGENCE)
    if not converged:
        raise RuntimeError(f"geomeTRIC did not converge in {len(steps)} steps (limit {MAX_STEPS})")
    return mol_eq.atom_coords(unit="Bohr"), steps[-1], len(steps)


def write_json(path: Path, record: dict) -> None:
    """A JSON record through a temp file in the same folder, moved over the target."""
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=1)
    os.replace(tmp, path)


def provenance(cfg: Reoptimisation, push: dict, energy: float, steps: int, seconds: float) -> dict:
    """The re-optimisation's record, stored in result.json and geometry.json."""
    return {"from": str(cfg.source), "why": "a negative mode at the label settings (chain 42's registration: one pyscf re-optimisation)",
            "settings": {"xc": LABEL_XC, "basis": "6-31G* (Cartesian d)", "grid": list(cfg.grid), "density_fitting": False,
                         "optimiser": "geomeTRIC via pyscf.geomopt.geometric_solver.kernel", **CONVERGENCE, "maxsteps": MAX_STEPS},
            **push, "energy": energy, "steps": steps, "seconds": round(seconds, 1),
            "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "software": software()}


def write_folder(cfg: Reoptimisation, geometry: dict, coords: np.ndarray, record: dict) -> None:
    """job.json and result.json first, geometry.json last: its presence marks a finished optimisation."""
    cfg.out.mkdir(parents=True, exist_ok=True)
    job = json.loads((cfg.source / "job.json").read_text(encoding="utf-8"))
    result = json.loads((cfg.source / "result.json").read_text(encoding="utf-8"))
    for stale in ("n_imaginary_b3lyp", "n_imaginary_wb97x", "peak_rss_gb", "timings_s"):
        result.pop(stale, None)
    result.update(status="done", labels="analytic_only", e_opt=record["energy"], reoptimised_at_label_settings=record)
    write_json(cfg.out / "job.json", job)
    write_json(cfg.out / "result.json", result)
    write_json(cfg.out / "geometry.json", dict(geometry, coords_bohr=coords.tolist(), optimised_at="B3LYP (pyscf, label settings)",
                                               reoptimised_at_label_settings=record))


def parse_args(argv: list[str] | None = None) -> Reoptimisation:
    """The command line as a checked Reoptimisation."""
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("source", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--threads", type=int, default=8)
    ap.add_argument("--max-memory", type=int, default=MAX_MEMORY_MB, help="pyscf's max_memory in MB (below a run's memory cap)")
    ap.add_argument("--grid", default=LABEL_GRID, help="radial,angular; the labels' grid unless a test runs small")
    ap.add_argument("--push-bohr", type=float, default=0.05, help="largest atom shift along a negative lowest mode before optimising")
    ap.add_argument("--dry-run", action="store_true", help="check the inputs, print the lowest mode and the basis size, run no SCF")
    a = ap.parse_args(argv)
    rad, ang = (int(v) for v in a.grid.split(","))
    return Reoptimisation(source=a.source, out=a.out, threads=a.threads, max_memory_mb=a.max_memory, grid=(rad, ang),
                          push_bohr=a.push_bohr, dry_run=a.dry_run)


def main(argv: list[str] | None = None) -> None:
    cfg = parse_args(argv)
    geometry = json.loads((cfg.source / "geometry.json").read_text(encoding="utf-8"))
    with np.load(cfg.source / "hessian_b3lyp_analytic.npz") as z:
        H_projected = z["H_projected"]
    start, push = start_geometry(geometry, H_projected, cfg.push_bohr)
    print(f"(RLS) {cfg.source.name}: {len(geometry['symbols'])} atoms, lowest B3LYP analytic mode {push['lowest_mode_cm']:.2f} cm-1, "
          f"push {push['push_bohr_largest_atom']} bohr; out {cfg.out}", flush=True)
    if cfg.dry_run:
        with open(os.devnull, "w", encoding="utf-8") as quiet:
            mol = labels_mol(start, quiet, max_memory=cfg.max_memory_mb)
        print(f"(RLS) dry run: {mol.nao} basis functions, grid {cfg.grid}, {cfg.threads} threads, max_memory {cfg.max_memory_mb} MB")
        return
    lib.num_threads(cfg.threads)
    cfg.out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    with open(cfg.out / PYSCF_LOG_NAME, "a", encoding="utf-8") as lib_log:
        coords, energy, steps = optimise(start, cfg, lib_log)
    record = provenance(cfg, push, energy, steps, time.time() - t0)
    write_folder(cfg, geometry, coords, record)
    print(f"(RLS) optimised: {steps} steps, E {energy:.10f}, {record['seconds']} s", flush=True)


if __name__ == "__main__":
    main()
