"""Single-point energies along the out-of-plane bend of a nearly planar molecule (TASKS 49; the user's choice A of 11 Nov 2026).

D_ac28161d06 re-optimised at the label settings is bent by up to 0.07 bohr along a butterfly mode whose B3LYP analytic frequency is
-9.5 cm-1. The scan tells a planar minimum hidden by numerical noise from a genuine shallow double well. The planar geometry P is the input
geometry with every atom's height above the heavy atoms' best plane removed; d is that removed out-of-plane part. The energy is taken at
P + s d for every s in SCALES at each grid, with the labels route's own SCF (`analytic_hessians.labels_mol` / `labels_ks`, the RKS call of
pyscf's dft/test/test_rks.py). s = 1 is the input geometry and s = -1 its mirror image, equal to it by symmetry: their difference is one
measure of the numerical noise, the change between the grids the other.

The verdict is registered here, before the run (`verdict`). With dE(s) = E(s) - E(0) and noise = the largest of |E(1) - E(-1)| at each
grid and the change of dE(1) between the grids:
    PLANAR       at the finest grid dE(0.5) > noise and dE(1) > noise: the bent geometry lies above the planar one
    DOUBLE WELL  dE(1) < -noise at every grid: the bent geometry lies below the planar one beyond the noise
    UNDECIDED    otherwise
One json per point (a point already written is skipped on a resume); scan.json, with the verdict, is written last.

    python probes/butterfly_scan.py <molecule dir> <out dir> [--xc b3lyp] [--grids 99,590 150,974] [--threads 8] [--max-memory MB]
        [--dry-run]
"""
from __future__ import annotations

import argparse
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
    FUNCTIONALS,
    MAX_MEMORY_MB,
    labels_ks,
    labels_mol,
    software,
)
from constants import HARTREE2CM  # noqa: E402
from library_log import PYSCF_LOG_NAME  # noqa: E402
from pyscf import lib  # noqa: E402
from vibrations import signed_cm  # noqa: E402

SCALES = (0.0, 0.5, 1.0, 1.5, 2.0, -1.0)   # multiples of the input geometry's out-of-plane part; 0 = planar, -1 = the mirror image
LABEL_GRID = (99, 590)                     # analytic_hessians.py's grid: the labels are computed there
FINE_GRID = (150, 974)


@dataclass(frozen=True)
class ScanConfig:
    """One scan's settings, checked before any geometry is read."""
    molecule: Path
    out: Path
    xc_tag: str
    grids: tuple[tuple[int, int], ...]
    threads: int
    max_memory_mb: int
    dry_run: bool

    def __post_init__(self) -> None:
        known = dict(FUNCTIONALS)
        if self.xc_tag not in known:
            raise ValueError(f"functional {self.xc_tag!r} is not one of the labels' {sorted(known)}")
        if len(self.grids) < 2 or len(set(self.grids)) != len(self.grids):
            raise ValueError(f"the verdict needs at least two distinct grids, got {self.grids}")
        if self.threads < 1 or self.max_memory_mb < 1:
            raise ValueError(f"threads {self.threads} and max_memory {self.max_memory_mb} MB must be positive")

    @property
    def hessian_file(self) -> Path:
        return self.molecule / f"hessian_{self.xc_tag}_analytic.npz"


def plane_split(coords: np.ndarray, heavy: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """The planar geometry and the out-of-plane part (both (N, 3), bohr) relative to the heavy atoms' best plane."""
    centre = coords[heavy].mean(axis=0)
    normal = np.linalg.svd(coords[heavy] - centre)[2][2]
    heights = (coords - centre) @ normal
    out_of_plane = np.outer(heights, normal)
    return coords - out_of_plane, out_of_plane


def mode_overlap(out_of_plane: np.ndarray, H_projected: np.ndarray, masses: np.ndarray) -> tuple[float, float, float]:
    """The lowest mode's frequency (cm-1), the cosine between it and the mass-weighted out-of-plane part, and the harmonic energy change
    1/2 d^T H d (hartree) that the Hessian predicts for the whole out-of-plane part."""
    sm = np.sqrt(np.repeat(masses, 3) * AMU2AU)
    w, V = np.linalg.eigh(H_projected / np.outer(sm, sm))
    vib = np.argsort(np.abs(w))[6:]
    k = vib[np.argmin(w[vib])]
    freq = float(signed_cm(w[k]))
    q = out_of_plane.ravel() * sm
    cosine = float(abs(q @ V[:, k]) / np.linalg.norm(q))
    d = out_of_plane.ravel()
    return freq, cosine, float(0.5 * d @ H_projected @ d)


def verdict(energies: dict[tuple[int, int], dict[float, float]]) -> tuple[str, float]:
    """PLANAR, DOUBLE WELL or UNDECIDED (the module docstring's rule) and the noise in hartree, from energies[grid][s]; the last grid in
    the dict is the finest."""
    grids = list(energies)
    dE = {g: {s: e - energies[g][0.0] for s, e in energies[g].items()} for g in grids}
    mirror = max(abs(energies[g][1.0] - energies[g][-1.0]) for g in grids)
    grid_change = max(abs(dE[g][1.0] - dE[grids[0]][1.0]) for g in grids)
    noise = max(mirror, grid_change)
    fine = dE[grids[-1]]
    if fine[0.5] > noise and fine[1.0] > noise:
        return "PLANAR", noise
    if all(dE[g][1.0] < -noise for g in grids):
        return "DOUBLE WELL", noise
    return "UNDECIDED", noise


def write_json(path: Path, record: dict) -> None:
    """A JSON record through a temp file in the same folder, moved over the target."""
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=1)
    os.replace(tmp, path)


def point_energy(geometry: dict, coords: np.ndarray, cfg: ScanConfig, grid: tuple[int, int], dm0: Any, lib_log: TextIO) -> tuple[float, Any]:
    """The labels route's converged SCF energy (hartree) at coords, started from dm0; raises when it does not converge."""
    mol = labels_mol({**geometry, "coords_bohr": coords.tolist()}, lib_log, max_memory=cfg.max_memory_mb)
    mf = labels_ks(mol, dict(FUNCTIONALS)[cfg.xc_tag], grid)
    energy = mf.kernel(dm0=dm0)
    if not mf.converged:
        raise RuntimeError(f"SCF not converged at grid {grid}")
    return float(energy), mf.make_rdm1()


def scan_grid(geometry: dict, planar: np.ndarray, out_of_plane: np.ndarray, cfg: ScanConfig, grid: tuple[int, int],
              lib_log: TextIO) -> dict[float, float]:
    """The energies at every scale for one grid, each written to its own json; points already written are read back."""
    energies, dm0 = {}, None
    for s in SCALES:
        path = cfg.out / f"point_{grid[0]}_{grid[1]}_s{s:+.1f}.json"
        if path.exists():
            energies[s] = json.loads(path.read_text(encoding="utf-8"))["energy_hartree"]
            print(f"(BFS) grid {grid} s {s:+.1f}: kept {energies[s]:.12f}", flush=True)
            continue
        t0 = time.time()
        energies[s], dm0 = point_energy(geometry, planar + s * out_of_plane, cfg, grid, dm0, lib_log)
        write_json(path, {"grid": list(grid), "scale": s, "energy_hartree": energies[s], "seconds": round(time.time() - t0, 1)})
        print(f"(BFS) grid {grid} s {s:+.1f}: E {energies[s]:.12f} ({time.time() - t0:.0f} s)", flush=True)
    return energies


def parse_args(argv: list[str] | None = None) -> ScanConfig:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("molecule", type=Path, help="folder with geometry.json and hessian_<xc>_analytic.npz")
    ap.add_argument("out", type=Path)
    ap.add_argument("--xc", default="b3lyp", help="the labels' functional tag")
    ap.add_argument("--grids", nargs="+", default=[f"{r},{a}" for r, a in (LABEL_GRID, FINE_GRID)], help="radial,angular; finest last")
    ap.add_argument("--threads", type=int, default=8)
    ap.add_argument("--max-memory", type=int, default=MAX_MEMORY_MB)
    ap.add_argument("--dry-run", action="store_true", help="build the geometries and the molecule, compute nothing")
    a = ap.parse_args(argv)
    grids = tuple(tuple(int(x) for x in g.split(",")) for g in a.grids)
    return ScanConfig(a.molecule, a.out, a.xc, grids, a.threads, a.max_memory, a.dry_run)


def main(argv: list[str] | None = None) -> None:
    cfg = parse_args(argv)
    geometry = json.loads((cfg.molecule / "geometry.json").read_text(encoding="utf-8"))
    coords = np.asarray(geometry["coords_bohr"], dtype=float)
    heavy = np.array([s.upper() != "H" for s in geometry["symbols"]])
    planar, out_of_plane = plane_split(coords, heavy)
    with np.load(cfg.hessian_file) as z:
        freq, cosine, harmonic = mode_overlap(out_of_plane, z["H_projected"], np.asarray(geometry["masses_amu"], dtype=float))
    print(f"(BFS) {cfg.molecule.name}: largest height {np.abs(out_of_plane).max():.4f} bohr; lowest {cfg.xc_tag} mode {freq:.3f} cm-1, "
          f"cosine with the out-of-plane part {cosine:.3f}; harmonic dE(1) {harmonic * HARTREE2CM:+.4f} cm-1", flush=True)
    if cfg.dry_run:
        with open(os.devnull, "w", encoding="utf-8") as quiet:
            mol = labels_mol({**geometry, "coords_bohr": planar.tolist()}, quiet, max_memory=cfg.max_memory_mb)
        print(f"(BFS) dry run: {mol.nao} basis functions, grids {cfg.grids}, scales {SCALES}, {cfg.threads} threads")
        return
    lib.num_threads(cfg.threads)
    cfg.out.mkdir(parents=True, exist_ok=True)
    with open(cfg.out / PYSCF_LOG_NAME, "a", encoding="utf-8") as lib_log:
        energies = {g: scan_grid(geometry, planar, out_of_plane, cfg, g, lib_log) for g in cfg.grids}
    call, noise = verdict(energies)
    record = {"molecule": cfg.molecule.name, "xc": cfg.xc_tag, "scales": list(SCALES), "lowest_mode_cm": freq, "cosine": cosine,
              "harmonic_dE1_cm": harmonic * HARTREE2CM, "noise_cm": noise * HARTREE2CM, "verdict": call, "software": software(),
              "dE_cm": {f"{g[0]},{g[1]}": {f"{s:+.1f}": (e - en[0.0]) * HARTREE2CM for s, e in en.items()} for g, en in energies.items()}}
    write_json(cfg.out / "scan.json", record)
    for g, row in record["dE_cm"].items():
        print(f"(BFS) dE (cm-1) at {g}: " + "  ".join(f"{s} {v:+.4f}" for s, v in row.items()), flush=True)
    print(f"(BFS) verdict {call}, noise {noise * HARTREE2CM:.4f} cm-1", flush=True)


if __name__ == "__main__":
    main()
