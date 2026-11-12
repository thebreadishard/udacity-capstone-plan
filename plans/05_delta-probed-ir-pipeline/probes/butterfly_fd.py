"""The curvature along one normal mode from analytic gradients with the grid response (TASKS 49; the user's option 3, 12 Nov 2026).

pyscf's CPU DFT Hessian leaves out the derivative of the quadrature weights (pyscf#3437; software ledger row 56). D_ac28161d06's B3LYP
analytic Hessian puts its butterfly mode at -9.5 cm-1, while a rigid translation in the same file gets up to 10.9 cm-1. Here the curvature
along that mode comes from analytic gradients that do include the weight derivatives, on pyscf 2.15.0. pyscf's own Hessian tests use the
same reference: `mf.Gradients().set(grid_response=True)` in `pyscf/hessian/test/test_rks.py` (`finite_diff`).

v is the lowest vibrational eigenvector of the mass-weighted analytic Hessian, taken in the space orthogonal to the rigid motions. A step
q (bohr me^1/2) moves the atoms by q v / sqrt(m). For every grid and step h (the largest atomic displacement, bohr), the SCF is converged
at x0 and at x0 +- h, and the gradient is taken with and without the grid response. The mass-weighted column c = (g~(+) - g~(-)) / 2q,
with g~ = g / sqrt(m), gives the Rayleigh quotient k = v.c and the frequency sign(k) sqrt|k|. The energies give a second route,
(E+ + E- - 2 E0) / q^2. The analytic Hessian with its row and column along v replaced by c gives a third number: its lowest frequency,
exact when the analytic Hessian's error lies along v. The gradients without the grid response are the control: their curvature must
equal the analytic Hessian's own Rayleigh quotient, or the difference is not the weight term (the other candidate is pyscf 2.14.0's
Krylov CPHF, fixed in 2.15.0).

Verdict, registered here before the run (`verdict`), on the gradients with the grid response:
    POSITIVE    the gradient route's frequency is > 0 at every grid and step, the steps agree within STEP_AGREEMENT_CM at the finest grid,
                and the patched Hessian's lowest frequency at the finest grid is > 0
    NEGATIVE    the gradient route's frequency is < 0 at every grid and step
    UNRESOLVED  otherwise
Attribution: CONTROL MATCHES when the control's frequency at both steps of the first grid (the analytic Hessian's, the label grid) lies
within CONTROL_TOLERANCE_CM of the analytic one.
One json per point (a point already written is kept on a resume); fd.json, with the verdict, is written last.

    python probes/butterfly_fd.py <molecule dir> <out dir> [--xc b3lyp] [--grids 99,590 150,974] [--steps 0.01 0.02] [--threads 8]
        [--max-memory MB] [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
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
    finish_by_newton,
    labels_ks,
    labels_mol,
    software,
)
from butterfly_scan import FINE_GRID, LABEL_GRID, write_json  # noqa: E402
from library_log import PYSCF_LOG_NAME  # noqa: E402
from pyscf import lib  # noqa: E402

STEPS_BOHR = (0.01, 0.02)      # the largest atomic displacement; the scan's bend reaches 0.07 bohr
STEP_AGREEMENT_CM = 2.0
CONTROL_TOLERANCE_CM = 2.0
CONV_TOL = 1e-12               # tighter than the labels' 1e-11: a 15 cm-1 mode changes the projected gradient by ~3e-6 over the steps
CONV_TOL_GRAD = 1e-7


@dataclass(frozen=True)
class FdConfig:
    """One run's settings, checked before any geometry is read."""
    molecule: Path
    out: Path
    xc_tag: str
    grids: tuple[tuple[int, int], ...]
    steps: tuple[float, ...]
    threads: int
    max_memory_mb: int
    dry_run: bool

    def __post_init__(self) -> None:
        if self.xc_tag not in dict(FUNCTIONALS):
            raise ValueError(f"functional {self.xc_tag!r} is not one of the labels' {sorted(dict(FUNCTIONALS))}")
        if len(self.grids) < 2 or len(set(self.grids)) != len(self.grids):
            raise ValueError(f"the verdict needs at least two distinct grids, got {self.grids}")
        if len(self.steps) != 2 or len(set(self.steps)) != 2 or min(self.steps) <= 0 or max(self.steps) > 0.05:
            raise ValueError(f"two distinct steps in (0, 0.05] bohr are needed, got {self.steps}")
        if self.threads < 1 or self.max_memory_mb < 1:
            raise ValueError(f"threads {self.threads} and max_memory {self.max_memory_mb} MB must be positive")

    @property
    def hessian_file(self) -> Path:
        return self.molecule / f"hessian_{self.xc_tag}_analytic.npz"


@dataclass(frozen=True)
class Mode:
    """The probed mode: the vibrational basis B (mass-weighted, orthogonal to the rigid motions), the analytic Hessian in it, the mode's
    coordinates y in B and its full mass-weighted vector v = B y, and sqrt(m) per Cartesian coordinate (me^1/2)."""
    basis: np.ndarray
    hessian_vib: np.ndarray
    y: np.ndarray
    v: np.ndarray
    sqrt_m: np.ndarray

    @property
    def analytic_k(self) -> float:
        return float(self.y @ self.hessian_vib @ self.y)


def frequency_cm(k: float) -> float:
    """A mass-weighted curvature (hartree / (bohr^2 me)) as a signed frequency in cm-1."""
    return float(np.sign(k) * np.sqrt(abs(k)) * AU2CM)


def rigid_basis(coords: np.ndarray, sqrt_m: np.ndarray) -> np.ndarray:
    """An orthonormal basis (3N, 6) of the mass-weighted translations and rotations about the centre of mass."""
    m = sqrt_m[::3] ** 2
    r = coords - (m[:, None] * coords).sum(0) / m.sum()
    cols = []
    for ax in range(3):
        t = np.zeros_like(coords)
        t[:, ax] = 1.0
        cols.append(t.ravel())
        cols.append(np.cross(np.eye(3)[ax], r).ravel())
    q, _ = np.linalg.qr(np.stack(cols, 1) * sqrt_m[:, None])
    return q


def lowest_mode(coords: np.ndarray, masses_amu: np.ndarray, H: np.ndarray) -> Mode:
    """The analytic Hessian's lowest vibrational mode, with the vibrational basis and the Hessian in it."""
    sqrt_m = np.sqrt(np.repeat(masses_amu, 3) * AMU2AU)
    rigid = rigid_basis(coords, sqrt_m)
    full, _ = np.linalg.qr(np.hstack([rigid, np.eye(len(sqrt_m))]))
    basis = full[:, 6:]
    Hmw = 0.5 * (H + H.T) / np.outer(sqrt_m, sqrt_m)
    hv = basis.T @ Hmw @ basis
    _eigenvalues, Y = np.linalg.eigh(hv)
    return Mode(basis, hv, Y[:, 0], basis @ Y[:, 0], sqrt_m)


def displacement_unit(mode: Mode) -> tuple[np.ndarray, float]:
    """The Cartesian displacement per unit q, (N, 3) bohr / (bohr me^1/2), and the q per bohr of largest atomic displacement."""
    d = (mode.v / mode.sqrt_m).reshape(-1, 3)
    return d, 1.0 / float(np.linalg.norm(d, axis=1).max())


def patched_lowest(mode: Mode, c_vib: np.ndarray) -> float:
    """The lowest eigenvalue of the vibrational Hessian with its row and column along the mode replaced by c (in the basis B)."""
    y, h = mode.y, mode.hessian_vib
    P = np.eye(len(y)) - np.outer(y, y)
    patched = P @ h @ P + np.outer(c_vib, y) + np.outer(y, c_vib) - (y @ c_vib) * np.outer(y, y)
    return float(np.linalg.eigvalsh(0.5 * (patched + patched.T))[0])


def point_record(geometry: dict, coords: np.ndarray, cfg: FdConfig, grid: tuple[int, int], dm0: Any, lib_log: TextIO) -> tuple[dict, Any]:
    """The converged SCF energy and the gradients with and without the grid response at coords; raises when the SCF does not converge."""
    mol = labels_mol({**geometry, "coords_bohr": coords.tolist()}, lib_log, max_memory=cfg.max_memory_mb)
    mf = labels_ks(mol, dict(FUNCTIONALS)[cfg.xc_tag], grid)
    mf.conv_tol, mf.conv_tol_grad = CONV_TOL, CONV_TOL_GRAD
    energy = mf.kernel(dm0=dm0)
    if not mf.converged:
        energy = finish_by_newton(mf)
    if not mf.converged:
        raise RuntimeError(f"SCF not converged at grid {grid}")
    with_response = mf.Gradients().set(grid_response=True).kernel()
    without = mf.Gradients().set(grid_response=False).kernel()
    return {"energy_hartree": float(energy), "gradient": np.asarray(with_response).tolist(),
            "gradient_no_grid_response": np.asarray(without).tolist()}, mf.make_rdm1()


def point_plan(cfg: FdConfig) -> list[tuple[tuple[int, int], float, int]]:
    """Every point in run order: per grid, x0 and then +- each step (sign 0 is x0)."""
    return [(g, h, s) for g in cfg.grids for h, s in [(0.0, 0), *((h, s) for h in cfg.steps for s in (1, -1))]]


def run_points(geometry: dict, mode: Mode, cfg: FdConfig, lib_log: TextIO) -> dict[tuple, dict]:
    """Every point's record, computed or read back, keyed (grid, step, sign)."""
    x0 = np.asarray(geometry["coords_bohr"], dtype=float)
    unit, q_per_bohr = displacement_unit(mode)
    out, dm0, last_grid = {}, None, None
    for grid, h, sign in point_plan(cfg):
        path = cfg.out / f"point_{grid[0]}_{grid[1]}_h{h:.3f}_{'+' if sign >= 0 else '-'}{abs(sign)}.json"
        if path.exists():
            out[(grid, h, sign)] = json.loads(path.read_text(encoding="utf-8"))
            print(f"(BFD) point {grid} h {h:.3f} sign {sign:+d}: kept", flush=True)
            continue
        if grid != last_grid:
            dm0, last_grid = None, grid
        t0 = time.time()
        q = sign * h * q_per_bohr
        rec, dm0 = point_record(geometry, x0 + q * unit, cfg, grid, dm0, lib_log)
        rec.update(grid=list(grid), step_bohr=h, sign=sign, q=q, seconds=round(time.time() - t0, 1))
        write_json(path, rec)
        out[(grid, h, sign)] = rec
        print(f"(BFD) point {grid} h {h:.3f} sign {sign:+d}: E {rec['energy_hartree']:.12f} ({rec['seconds']:.0f} s)", flush=True)
    return out


def curvatures(points: dict[tuple, dict], mode: Mode, grid: tuple[int, int], h: float) -> dict[str, float]:
    """The three routes' frequencies (cm-1) at one grid and step, and the control's."""
    plus, minus, zero = points[(grid, h, 1)], points[(grid, h, -1)], points[(grid, 0.0, 0)]
    q = plus["q"]

    def column(key: str) -> np.ndarray:
        g = (np.ravel(plus[key]) - np.ravel(minus[key])) / mode.sqrt_m
        return g / (2 * q)

    c, c_ctrl = column("gradient"), column("gradient_no_grid_response")
    k_energy = (plus["energy_hartree"] + minus["energy_hartree"] - 2 * zero["energy_hartree"]) / q**2
    return {"gradient": frequency_cm(float(mode.v @ c)), "energy": frequency_cm(k_energy),
            "patched_lowest": frequency_cm(patched_lowest(mode, mode.basis.T @ c)), "control": frequency_cm(float(mode.v @ c_ctrl)),
            "stationarity_dE_dq": float(np.ravel(zero["gradient"]) @ (mode.v / mode.sqrt_m)), "q": q}


def verdict(rows: dict[tuple[tuple[int, int], float], dict[str, float]], analytic_cm: float) -> tuple[str, bool]:
    """POSITIVE, NEGATIVE or UNRESOLVED (the module docstring's rule) and whether the control matches; rows keyed (grid, step), the last
    grid in the dict the finest."""
    grids = list(dict.fromkeys(g for g, _ in rows))
    finest = [r for (g, _), r in rows.items() if g == grids[-1]]
    freqs = [r["gradient"] for r in rows.values()]
    control = all(abs(r["control"] - analytic_cm) <= CONTROL_TOLERANCE_CM for (g, _), r in rows.items() if g == grids[0])
    if (all(f > 0 for f in freqs) and abs(finest[0]["gradient"] - finest[-1]["gradient"]) <= STEP_AGREEMENT_CM
            and all(r["patched_lowest"] > 0 for r in finest)):
        return "POSITIVE", control
    if all(f < 0 for f in freqs):
        return "NEGATIVE", control
    return "UNRESOLVED", control


def parse_args(argv: list[str] | None = None) -> FdConfig:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("molecule", type=Path, help="folder with geometry.json and hessian_<xc>_analytic.npz")
    ap.add_argument("out", type=Path)
    ap.add_argument("--xc", default="b3lyp", help="the labels' functional tag")
    ap.add_argument("--grids", nargs="+", default=[f"{r},{a}" for r, a in (LABEL_GRID, FINE_GRID)], help="radial,angular; finest last")
    ap.add_argument("--steps", nargs="+", type=float, default=list(STEPS_BOHR), help="largest atomic displacement, bohr")
    ap.add_argument("--threads", type=int, default=8)
    ap.add_argument("--max-memory", type=int, default=MAX_MEMORY_MB)
    ap.add_argument("--dry-run", action="store_true", help="find the mode and build the molecule, compute nothing")
    a = ap.parse_args(argv)
    grids = tuple(tuple(int(x) for x in g.split(",")) for g in a.grids)
    return FdConfig(a.molecule, a.out, a.xc, grids, tuple(a.steps), a.threads, a.max_memory, a.dry_run)


def report(cfg: FdConfig, mode: Mode, points: dict[tuple, dict]) -> dict:
    """fd.json's record: every grid's and step's routes, the analytic frequency, the verdict and the attribution."""
    analytic = frequency_cm(mode.analytic_k)
    rows = {(g, h): curvatures(points, mode, g, h) for g in cfg.grids for h in cfg.steps}
    call, control = verdict(rows, analytic)
    return {"molecule": cfg.molecule.name, "xc": cfg.xc_tag, "analytic_lowest_cm": analytic, "verdict": call,
            "control_matches": control, "steps_bohr": list(cfg.steps), "software": software(),
            "rows": [{"grid": list(g), "step_bohr": h, **r} for (g, h), r in rows.items()]}


def main(argv: list[str] | None = None) -> None:
    cfg = parse_args(argv)
    geometry = json.loads((cfg.molecule / "geometry.json").read_text(encoding="utf-8"))
    coords = np.asarray(geometry["coords_bohr"], dtype=float)
    with np.load(cfg.hessian_file) as z:
        mode = lowest_mode(coords, np.asarray(geometry["masses_amu"], dtype=float), np.asarray(z["H_raw"], dtype=float))
    q_per_bohr = displacement_unit(mode)[1]
    print(f"(BFD) {cfg.molecule.name}: lowest {cfg.xc_tag} mode {frequency_cm(mode.analytic_k):.3f} cm-1 (analytic, rigid motions removed); "
          f"q per bohr of largest displacement {q_per_bohr:.2f}", flush=True)
    if cfg.dry_run:
        with open(os.devnull, "w", encoding="utf-8") as quiet:
            mol = labels_mol(geometry, quiet, max_memory=cfg.max_memory_mb)
        print(f"(BFD) dry run: {mol.nao} basis functions, {len(point_plan(cfg))} points, grids {cfg.grids}, steps {cfg.steps}")
        return
    lib.num_threads(cfg.threads)
    cfg.out.mkdir(parents=True, exist_ok=True)
    with open(cfg.out / PYSCF_LOG_NAME, "a", encoding="utf-8") as lib_log:
        points = run_points(geometry, mode, cfg, lib_log)
    record = report(cfg, mode, points)
    write_json(cfg.out / "fd.json", record)
    for r in record["rows"]:
        print(f"(BFD) grid {tuple(r['grid'])} step {r['step_bohr']:.3f}: gradient {r['gradient']:+.2f}, energy {r['energy']:+.2f}, "
              f"patched lowest {r['patched_lowest']:+.2f}, control {r['control']:+.2f} cm-1", flush=True)
    print(f"(BFD) verdict {record['verdict']}; control matches the analytic {record['analytic_lowest_cm']:+.2f} cm-1: "
          f"{record['control_matches']}", flush=True)


if __name__ == "__main__":
    main()
