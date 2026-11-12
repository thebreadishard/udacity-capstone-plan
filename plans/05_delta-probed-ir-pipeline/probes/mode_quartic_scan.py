"""Does a QFF's diagonal quartic constant change with the DFT grid? Energies along a normal mode at two grids (TASKS 207).

Coronene's G force field (route A, B3LYP/6-31G*, grid 75/302) gives mode 36 (807 cm⁻¹) φ_iiii 711 cm⁻¹ and Δ_anh +179 cm⁻¹, while the
matching xtb mode has φ_iiii 5.9 cm⁻¹ and Δ_anh −7.5 cm⁻¹. A planar molecule displaced ± along a mode gives mirror images, so a quadrature
error that is the same at both appears as an even term — a spurious quartic constant — that both finite-difference routes share. Here the
SCF energy (route A's own SCF: `pyscf_hessians_for_qff.converged_at`) is taken at Q = 0, ±h, ±2h along each mode's reduced coordinate at
each grid, and

    ω   = (−E(2h) + 16 E(h) − 30 E(0) + 16 E(−h) − E(−2h)) / (12 h²),     φ_iiii = (E(2h) − 4 E(h) + 6 E(0) − 4 E(−h) + E(−2h)) / h⁴

(hartree, reported in cm⁻¹), beside the stored QFF's ω and φ_iiii. Reading, registered before the run, per mode with φ_QFF the stored value:
    GRID       |φ_iiii| at the finer grid ≤ 0.1 |φ_QFF| and the coarse grid's within 30 % of φ_QFF: the constant is the coarse grid's
    POTENTIAL  the two grids' φ_iiii within 30 % of each other and of φ_QFF: the potential has it
    UNRESOLVED otherwise
One json per point (kept on a resume); scan.json with the reading last.

    python probes/mode_quartic_scan.py <setting dir: ref.json, qff_report.npz> <out dir> --modes 36 24 [--grids 75,302 99,590] [--h 0.5]
        [--threads 8] [--dry-run]
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
OFFSETS = (0, 1, -1, 2, -2)      # multiples of h; 0 first so every displaced SCF starts from its density


@dataclass(frozen=True)
class QuarticConfig:
    """The scan's settings, checked before any geometry is read."""

    setting: Path
    out: Path
    modes: tuple[int, ...]
    grids: tuple[str, ...]
    h: float
    threads: int
    dry_run: bool

    def __post_init__(self) -> None:
        if not self.modes or len(set(self.modes)) != len(self.modes) or min(self.modes) < 0:
            raise ValueError(f"modes {self.modes}: distinct, non-negative")
        if len(self.grids) != 2 or len(set(self.grids)) != 2:
            raise ValueError(f"two distinct grids (coarse, fine) are needed, got {self.grids}")
        if not 0 < self.h <= 2.0:
            raise ValueError(f"step {self.h} (reduced coordinate): in (0, 2]")
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
    """GRID, POTENTIAL or UNRESOLVED by the module docstring's rule."""
    if abs(phi_fine) <= FINE_FRACTION * abs(phi_qff) and abs(phi_coarse - phi_qff) <= RELATIVE * abs(phi_qff):
        return "GRID"
    if abs(phi_fine - phi_coarse) <= RELATIVE * abs(phi_coarse) and abs(phi_coarse - phi_qff) <= RELATIVE * abs(phi_qff):
        return "POTENTIAL"
    return "UNRESOLVED"


def energy_at(ref: dict, coords: np.ndarray, grid: str, point: tuple[Path, Any], lib_log: TextIO) -> tuple[float, Any]:
    """The SCF energy at coords and grid (read back from its json when present) and the density for the next start."""
    path, dm0 = point
    if path.exists():
        return float(json.loads(path.read_text(encoding="utf-8"))["energy_hartree"]), dm0
    t0 = time.time()
    d = {"molecule": {**ref["molecule"], "geometry": coords.ravel().tolist()}}
    a = argparse.Namespace(basis=ref["model"]["basis"], xc=ref["model"]["method"].split()[-1], grid=grid, conv=QFF_CONV)
    mf, energy = converged_at(d, a, lib_log, dm0)
    write_json(path, {"energy_hartree": float(energy), "grid": grid, "seconds": round(time.time() - t0, 1)})
    print(f"(MQS) point {path.stem}: E {float(energy):.12f} ({time.time() - t0:.0f} s)", flush=True)
    return float(energy), mf.make_rdm1()


def scan(cfg: QuarticConfig, lib_log: TextIO) -> dict[str, Any]:
    """Every mode's ω and φ_iiii at both grids, beside the stored QFF's, with the reading."""
    ref = json.loads((cfg.setting / "ref.json").read_text(encoding="utf-8"))
    symbols, x0 = ref["molecule"]["symbols"], np.asarray(ref["molecule"]["geometry"], float)
    harm = harmonic(np.asarray(ref["return_result"], float).reshape(len(x0), len(x0)), symbols, x0)
    with np.load(cfg.setting / "qff_report.npz") as z:
        omega_qff, phi_qff = np.asarray(z["omega_cm"]), np.diag(np.asarray(z["phi_iijj"]))
    if not np.allclose(harm.omega_cm, omega_qff, atol=1e-6):
        raise ValueError("the reference record's modes are not the QFF's")
    rows: dict[str, Any] = {}
    for grid in cfg.grids:
        folder = cfg.out / grid.replace(",", "_")
        folder.mkdir(parents=True, exist_ok=True)
        e0, dm0 = energy_at(ref, x0, grid, (folder / "Q0.json", None), lib_log)
        for i in cfg.modes:
            e = {0: e0}
            for k in OFFSETS[1:]:
                e[k], _ = energy_at(ref, x0 + k * cfg.h * harm.A[:, i], grid, (folder / f"mode{i}_{k:+d}.json", dm0), lib_log)
            w, phi = stencils(e, cfg.h)
            rows.setdefault(str(i), {"omega_qff_cm": float(omega_qff[i]), "phi_qff_cm": float(phi_qff[i])})[grid] = {"omega_cm": w, "phi_cm": phi}
    for r in rows.values():
        r["reading"] = reading(r[cfg.grids[0]]["phi_cm"], r[cfg.grids[1]]["phi_cm"], r["phi_qff_cm"])
    return {"setting": str(cfg.setting), "h": cfg.h, "grids": list(cfg.grids), "modes": rows}


def parse_args(argv: list[str] | None = None) -> QuarticConfig:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("setting", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--modes", type=int, nargs="+", required=True)
    ap.add_argument("--grids", nargs=2, default=["75,302", "99,590"], help="coarse, fine (radial,angular)")
    ap.add_argument("--h", type=float, default=0.5, help="the step in the QFF's reduced normal coordinate")
    ap.add_argument("--threads", type=int, default=8)
    ap.add_argument("--dry-run", action="store_true", help="read the setting and check the modes; compute nothing")
    a = ap.parse_args(argv)
    return QuarticConfig(a.setting, a.out, tuple(a.modes), tuple(a.grids), a.h, a.threads, a.dry_run)


def main(argv: list[str] | None = None) -> None:
    cfg = parse_args(argv)
    if cfg.dry_run:
        with np.load(cfg.setting / "qff_report.npz") as z:
            w, p = np.asarray(z["omega_cm"]), np.diag(np.asarray(z["phi_iijj"]))
        print("(MQS) dry run: " + ", ".join(f"mode {i} ω {w[i]:.1f} φ_iiii {p[i]:.1f} cm⁻¹" for i in cfg.modes)
              + f"; {len(cfg.grids) * (1 + 4 * len(cfg.modes))} SCFs", flush=True)
        return
    from pyscf import lib
    lib.num_threads(cfg.threads)
    cfg.out.mkdir(parents=True, exist_ok=True)
    with open(cfg.out / PYSCF_LOG_NAME, "a", encoding="utf-8") as lib_log:
        record = scan(cfg, lib_log)
    write_json(cfg.out / "scan.json", record)
    for i, r in record["modes"].items():
        print(f"(MQS) mode {i}: QFF ω {r['omega_qff_cm']:.1f} φ {r['phi_qff_cm']:.1f}; "
              + "; ".join(f"{g}: ω {r[g]['omega_cm']:.1f} φ {r[g]['phi_cm']:.1f}" for g in record["grids"]) + f" → {r['reading']}", flush=True)


if __name__ == "__main__":
    main()
