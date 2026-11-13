"""Does a QFF's diagonal quartic constant change with the DFT grid? Energies along a normal mode at two grids (TASKS 207).

Coronene's G force field (route A, B3LYP/6-31G*, grid 75/302) gives mode 36 (807 cm⁻¹) φ_iiii 711 cm⁻¹ and Δ_anh +179 cm⁻¹, while the
matching xtb mode has φ_iiii 5.9 cm⁻¹ and Δ_anh −7.5 cm⁻¹. A planar molecule displaced ± along a mode gives mirror images, so a quadrature
error that is the same at both appears as an even term — a spurious quartic constant — that both finite-difference routes share. Here the
SCF energy (route A's own SCF: `pyscf_hessians_for_qff.converged_at`) is taken at Q = 0, ±h, ±2h along each mode's reduced coordinate at
each grid, and

    ω   = (−E(2h) + 16 E(h) − 30 E(0) + 16 E(−h) − E(−2h)) / (12 h²),     φ_iiii = (E(2h) − 4 E(h) + 6 E(0) − 4 E(−h) + E(−2h)) / h⁴

(hartree, reported in cm⁻¹), beside the stored QFF's ω and φ_iiii. Two readings, each registered before its run:

    the grid (two grids at the first step), per mode with φ_QFF the stored value
        GRID       |φ_iiii| at the finer grid ≤ 0.1 |φ_QFF| and the coarse grid's within 30 % of φ_QFF: the constant is the coarse grid's
        POTENTIAL  the two grids' φ_iiii within 30 % of each other and of φ_QFF: the potential has it
        UNRESOLVED otherwise
    the step (two or more steps at the finest grid), the five-point stencil's leading error going as h² (its next term is the sixth
    derivative, so a step-dependent constant means the quartic truncation itself is the limit)
        CONVERGED       the two smallest steps' φ_iiii within 10 % of each other: the quartic constant is the potential's
        STEP_DEPENDENT  otherwise; `phi_extrapolated_cm` is then the h → 0 value of those two steps

A scan needs two grids or two steps, or it measures nothing. Every point is one json named by its displacement, so two steps that meet at
the same geometry share one SCF and a resume recomputes nothing; scan.json holds every measurement and the readings.

    python probes/mode_quartic_scan.py <setting dir: ref.json, qff_report.npz> <out dir> --modes 36 24 [--grids 75,302 99,590]
        [--steps 0.25 0.5 1.0] [--threads 8] [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TextIO

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from butterfly_scan import write_json
from library_log import PYSCF_LOG_NAME
from pyscf_hessians_for_qff import converged_at

from dpir.qff import HARTREE_CM, harmonic

QFF_CONV = 1e-11                 # route A's conv_tol (ref.json keywords)
RELATIVE = 0.3
FINE_FRACTION = 0.1
STEP_RELATIVE = 0.1              # the step reading's tolerance between the two smallest steps
STENCIL_OFFSETS = (0, 1, -1, 2, -2)   # multiples of a step; 0 first so every displaced SCF starts from the reference density
DISPLACEMENT_DIGITS = 6          # a displacement is a point's name and its key: both rounded here, so they never disagree


@dataclass(frozen=True)
class QuarticConfig:
    """The scan's settings, checked before any geometry is read."""

    setting: Path
    out: Path
    modes: tuple[int, ...]
    grids: tuple[str, ...]
    steps: tuple[float, ...]
    threads: int
    dry_run: bool

    def __post_init__(self) -> None:
        if not self.modes or len(set(self.modes)) != len(self.modes) or min(self.modes) < 0:
            raise ValueError(f"modes {self.modes}: distinct, non-negative")
        if not 1 <= len(self.grids) <= 2 or len(set(self.grids)) != len(self.grids):
            raise ValueError(f"one or two distinct grids (coarse, fine) are needed, got {self.grids}")
        if not self.steps or len({round(s, DISPLACEMENT_DIGITS) for s in self.steps}) != len(self.steps):
            raise ValueError(f"steps {self.steps}: distinct")
        if any(not 0 < s <= 2.0 for s in self.steps):
            raise ValueError(f"steps {self.steps} (reduced coordinate): each in (0, 2]")
        if len(self.grids) == 1 and len(self.steps) == 1:
            raise ValueError("one grid and one step measure nothing: a scan needs two grids (the grid reading) or two steps (the step reading)")
        if self.threads < 1:
            raise ValueError(f"threads {self.threads}: positive")
        for f in ("ref.json", "qff_report.npz"):
            if not (self.setting / f).is_file():
                raise FileNotFoundError(f"{self.setting / f} is missing")


def stencils(e: dict[int, float], h: float) -> tuple[float, float]:
    """(ω, φ_iiii) in cm⁻¹ from the energies (hartree) at offsets 0, ±1, ±2 of a reduced-coordinate step h."""
    omega = (-e[2] + 16 * e[1] - 30 * e[0] + 16 * e[-1] - e[-2]) / (12 * h**2)
    quartic = (e[2] - 4 * e[1] + 6 * e[0] - 4 * e[-1] + e[-2]) / h**4
    return float(omega * HARTREE_CM), float(quartic * HARTREE_CM)


def reading(phi_coarse: float, phi_fine: float, phi_qff: float) -> str:
    """GRID, POTENTIAL or UNRESOLVED by the module docstring's grid rule."""
    if abs(phi_fine) <= FINE_FRACTION * abs(phi_qff) and abs(phi_coarse - phi_qff) <= RELATIVE * abs(phi_qff):
        return "GRID"
    if abs(phi_fine - phi_coarse) <= RELATIVE * abs(phi_coarse) and abs(phi_coarse - phi_qff) <= RELATIVE * abs(phi_qff):
        return "POTENTIAL"
    return "UNRESOLVED"


def step_reading(phi_small: float, phi_large: float) -> str:
    """CONVERGED or STEP_DEPENDENT by the module docstring's step rule, from the two smallest steps' quartic constants."""
    if abs(phi_small - phi_large) <= STEP_RELATIVE * max(abs(phi_small), abs(phi_large)):
        return "CONVERGED"
    return "STEP_DEPENDENT"


def richardson(h_small: float, phi_small: float, h_large: float, phi_large: float) -> float:
    """The h → 0 quartic constant of two steps, the five-point stencil's leading error going as h²."""
    if not 0 < h_small < h_large:
        raise ValueError(f"steps {h_small} and {h_large}: positive, the first the smaller")
    return float((h_large**2 * phi_small - h_small**2 * phi_large) / (h_large**2 - h_small**2))


def displacements(steps: tuple[float, ...]) -> list[float]:
    """Every reduced-coordinate displacement the stencils of those steps need, each once, 0 first."""
    out = [0.0]
    for s in steps:
        for d in (s, -s, 2 * s, -2 * s):
            if round(d, DISPLACEMENT_DIGITS) not in [round(x, DISPLACEMENT_DIGITS) for x in out]:
                out.append(round(d, DISPLACEMENT_DIGITS))
    return out


def point_name(mode: int, displacement: float) -> str:
    """The json of one point. Its displacement is in the name, so two steps meeting at one geometry share the SCF."""
    if round(displacement, DISPLACEMENT_DIGITS) == 0.0:
        return "Q0.json"
    return f"mode{mode}_{displacement:+.{DISPLACEMENT_DIGITS}f}.json"


def energy_at(ref: dict, coords: np.ndarray, grid: str, point: tuple[Path, Any], displacement: float,
              lib_log: TextIO) -> tuple[float, Any]:
    """The SCF energy at coords and grid (read back from its json when present) and the density for the next start."""
    path, dm0 = point
    if path.exists():
        return float(json.loads(path.read_text(encoding="utf-8"))["energy_hartree"]), dm0
    t0 = time.time()
    d = {"molecule": {**ref["molecule"], "geometry": coords.ravel().tolist()}}
    a = argparse.Namespace(basis=ref["model"]["basis"], xc=ref["model"]["method"].split()[-1], grid=grid, conv=QFF_CONV)
    mf, energy = converged_at(d, a, lib_log, dm0)
    write_json(path, {"energy_hartree": float(energy), "grid": grid, "displacement": displacement, "seconds": round(time.time() - t0, 1)})
    print(f"(MQS) point {path.stem}: E {float(energy):.12f} ({time.time() - t0:.0f} s)", flush=True)
    return float(energy), mf.make_rdm1()


def grid_energies(cfg: QuarticConfig, ref: dict, modes_a: np.ndarray, grid: str, lib_log: TextIO) -> dict[int, dict[float, float]]:
    """{mode: {displacement: energy}} at one grid, every point computed once and cached under its displacement."""
    x0 = np.asarray(ref["molecule"]["geometry"], float)
    folder = cfg.out / grid.replace(",", "_")
    folder.mkdir(parents=True, exist_ok=True)
    e0, dm0 = energy_at(ref, x0, grid, (folder / "Q0.json", None), 0.0, lib_log)
    table: dict[int, dict[float, float]] = {}
    for i in cfg.modes:
        table[i] = {0.0: e0}
        for d in displacements(cfg.steps)[1:]:
            table[i][d], _ = energy_at(ref, x0 + d * modes_a[:, i], grid, (folder / point_name(i, d), dm0), d, lib_log)
    return table


def summarise(cfg: QuarticConfig, measured: list[dict[str, Any]], omega_qff: np.ndarray, phi_qff: np.ndarray) -> dict[str, Any]:
    """Each mode's stored QFF values and the readings its grids and steps allow."""

    def phi(mode: int, grid: str, step: float) -> float:
        return next(m["phi_cm"] for m in measured if m["mode"] == mode and m["grid"] == grid and m["step"] == step)

    first_step, finest_grid = cfg.steps[0], cfg.grids[-1]
    small, large = sorted(cfg.steps)[:2] if len(cfg.steps) >= 2 else (0.0, 0.0)
    out: dict[str, Any] = {}
    for i in cfg.modes:
        row = {"omega_qff_cm": float(omega_qff[i]), "phi_qff_cm": float(phi_qff[i])}
        if len(cfg.grids) == 2:
            row["reading"] = reading(phi(i, cfg.grids[0], first_step), phi(i, cfg.grids[1], first_step), float(phi_qff[i]))
        if len(cfg.steps) >= 2:
            row["step_reading"] = step_reading(phi(i, finest_grid, small), phi(i, finest_grid, large))
            row["phi_extrapolated_cm"] = richardson(small, phi(i, finest_grid, small), large, phi(i, finest_grid, large))
        out[str(i)] = row
    return out


def stored_qff(cfg: QuarticConfig) -> tuple[dict, np.ndarray, np.ndarray, np.ndarray]:
    """The reference record, its mass-weighted mode columns, and the QFF's ω and φ_iiii, refused unless the modes are the QFF's."""
    ref = json.loads((cfg.setting / "ref.json").read_text(encoding="utf-8"))
    symbols, x0 = ref["molecule"]["symbols"], np.asarray(ref["molecule"]["geometry"], float)
    harm = harmonic(np.asarray(ref["return_result"], float).reshape(len(x0), len(x0)), symbols, x0)
    with np.load(cfg.setting / "qff_report.npz") as z:
        omega_qff, phi_qff = np.asarray(z["omega_cm"]), np.diag(np.asarray(z["phi_iijj"]))
    if not np.allclose(harm.omega_cm, omega_qff, atol=1e-6):
        raise ValueError("the reference record's modes are not the QFF's")
    if max(cfg.modes) >= len(omega_qff):
        raise ValueError(f"mode {max(cfg.modes)} of {len(omega_qff)}")
    return ref, harm.A, omega_qff, phi_qff


def scan(cfg: QuarticConfig, lib_log: TextIO) -> dict[str, Any]:
    """Every mode's ω and φ_iiii at each grid and step, beside the stored QFF's, with the readings."""
    ref, modes_a, omega_qff, phi_qff = stored_qff(cfg)
    measured: list[dict[str, Any]] = []
    for grid in cfg.grids:
        table = grid_energies(cfg, ref, modes_a, grid, lib_log)
        for i, row in table.items():
            for s in cfg.steps:
                w, phi = stencils({k: row[round(k * s, DISPLACEMENT_DIGITS)] for k in STENCIL_OFFSETS}, s)
                measured.append({"mode": i, "grid": grid, "step": s, "omega_cm": w, "phi_cm": phi})
    return {"setting": str(cfg.setting), "steps": list(cfg.steps), "grids": list(cfg.grids), "measured": measured,
            "modes": summarise(cfg, measured, omega_qff, phi_qff)}


def parse_args(argv: list[str] | None = None) -> QuarticConfig:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("setting", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--modes", type=int, nargs="+", required=True)
    ap.add_argument("--grids", nargs="+", default=["75,302", "99,590"], help="one, or coarse and fine (radial,angular)")
    ap.add_argument("--steps", type=float, nargs="+", default=[0.5], help="the steps in the QFF's reduced normal coordinate")
    ap.add_argument("--threads", type=int, default=8)
    ap.add_argument("--dry-run", action="store_true", help="read the setting and check the modes; compute nothing")
    a = ap.parse_args(argv)
    return QuarticConfig(a.setting, a.out, tuple(a.modes), tuple(a.grids), tuple(a.steps), a.threads, a.dry_run)


def main(argv: list[str] | None = None) -> None:
    cfg = parse_args(argv)
    if cfg.dry_run:
        with np.load(cfg.setting / "qff_report.npz") as z:
            w, p = np.asarray(z["omega_cm"]), np.diag(np.asarray(z["phi_iijj"]))
        print("(MQS) dry run: " + ", ".join(f"mode {i} ω {w[i]:.1f} φ_iiii {p[i]:.1f} cm⁻¹" for i in cfg.modes)
              + f"; steps {list(cfg.steps)}; {len(cfg.grids) * (1 + (len(displacements(cfg.steps)) - 1) * len(cfg.modes))} SCFs",
              flush=True)
        return
    from pyscf import lib
    lib.num_threads(cfg.threads)
    cfg.out.mkdir(parents=True, exist_ok=True)
    with open(cfg.out / PYSCF_LOG_NAME, "a", encoding="utf-8") as lib_log:
        record = scan(cfg, lib_log)
    write_json(cfg.out / "scan.json", record)
    for i, r in record["modes"].items():
        measured = "; ".join(f"{m['grid']} h {m['step']:g}: ω {m['omega_cm']:.1f} φ {m['phi_cm']:.1f}"
                             for m in record["measured"] if str(m["mode"]) == i)
        verdicts = " ".join(f"{k} {r[k]}" for k in ("reading", "step_reading") if k in r)
        print(f"(MQS) mode {i}: QFF ω {r['omega_qff_cm']:.1f} φ {r['phi_qff_cm']:.1f}; {measured} → {verdicts}", flush=True)


if __name__ == "__main__":
    main()
