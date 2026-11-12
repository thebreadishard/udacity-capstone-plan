"""TASKS 201 step 2: the vibrational error of our analytic label Hessians from the missing XC grid response, measured.

pyscf's CPU DFT Hessian leaves out the derivative of the quadrature weights (software ledger 56). The Hessian of the energy as actually
integrated is the finite difference of gradients with `grid_response=True` on a grid that moves with the atoms (pyscf's own reference in
`hessian/test/test_rks.py`, `finite_diff`). Per functional this probe computes, at the label settings (6-31G* Cartesian, unpruned label
grid) on pyscf 2.15.0: the central-difference Hessian of grid-response gradients (our blocked implementation, software ledger 57), and
pyscf's analytic Hessian at the same reference SCF; it compares both with the corpus label (H_raw, pyscf 2.14.0) by the projected
harmonic frequencies and by the rigid-translation residual, which is zero for the exact Hessian of a translation-invariant energy.

    python probes/hessian_grid_response_fd.py <molecule dir> <out dir> [--xc b3lyp wb97x] [--step 0.005] [--threads 8] [--max-memory MB]

Writes `<out>/<xc>/point_<atom>_<xyz>_<sign>.json` (resumable), `<out>/fd_hessian_<xc>.npz`, `<out>/report.json` and `report.md`.
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
    FUNCTIONALS,
    MAX_MEMORY_MB,
    finish_by_newton,
    freqs_cm,
    labels_ks,
    labels_mol,
    project_tr,
    vib_only,
)
from butterfly_scan import LABEL_GRID, write_json  # noqa: E402
from grid_response_blocked import blocked_grid_response  # noqa: E402
from library_log import PYSCF_LOG_NAME  # noqa: E402
from pyscf import __version__ as pyscf_version  # noqa: E402
from pyscf import lib  # noqa: E402
from qc_common import translation_residual, write_atomic  # noqa: E402

STEP_BOHR = 0.005              # the frozen-grid check's step (probes/hessian_fixed_grid_fd.py: 0.06 cm-1 from the analytic on benzene)
CONV_TOL_GRAD = 1e-8           # a gradient error of 1e-8 over 2h = 0.01 bohr is 1e-6 Eh/bohr², against translation residuals ≈ 1e-4
LOW_MODE_CM = 100.0            # 'low' modes for the summary: the family 'other' holds them
XYZ = "xyz"


@dataclass(frozen=True)
class FdHessianConfig:
    """The probe's settings, checked before any geometry is read."""

    molecule: Path
    out: Path
    xc_tags: tuple[str, ...]
    grid: tuple[int, int]
    step: float
    threads: int
    max_memory_mb: int
    dry_run: bool

    def __post_init__(self) -> None:
        known = dict(FUNCTIONALS)
        if not self.xc_tags or len(set(self.xc_tags)) != len(self.xc_tags) or any(t not in known for t in self.xc_tags):
            raise ValueError(f"xc tags {self.xc_tags}: one or more distinct of {sorted(known)}")
        if len(self.grid) != 2 or min(self.grid) < 1:
            raise ValueError(f"grid {self.grid}: (radial, angular), both positive")
        if not 0 < self.step <= 0.02:
            raise ValueError(f"step {self.step} bohr: in (0, 0.02]")
        if self.threads < 1 or self.max_memory_mb < 1000:
            raise ValueError(f"threads {self.threads} (≥ 1), max memory {self.max_memory_mb} MB (≥ 1000)")


def converged_scf(mol: Any, xc_tag: str, grid: tuple[int, int], dm0: Any) -> Any:
    """The labels route's KS object at grid, converged (second-order finish when DIIS stalls); raises when it does not converge."""
    mf = labels_ks(mol, dict(FUNCTIONALS)[xc_tag], grid)
    mf.conv_tol_grad = CONV_TOL_GRAD
    mf.kernel(dm0=dm0)
    if not mf.converged:
        finish_by_newton(mf)
    if not mf.converged:
        raise RuntimeError(f"{xc_tag} SCF not converged")
    return mf


def point_record(geometry: dict, coords: np.ndarray, cfg: FdHessianConfig, xc_tag: str, dm0: Any, lib_log: TextIO) -> tuple[dict, Any]:
    """Energy and grid-response gradient at coords (the grid built at coords, so it moves with the atoms)."""
    mol = labels_mol({**geometry, "coords_bohr": coords.tolist()}, lib_log, max_memory=cfg.max_memory_mb)
    mf = converged_scf(mol, xc_tag, cfg.grid, dm0)
    with blocked_grid_response():
        gradient = mf.nuc_grad_method().set(grid_response=True).kernel()
    return {"energy_hartree": float(mf.e_tot), "gradient": np.asarray(gradient).tolist()}, mf.make_rdm1()


def reference(geometry: dict, cfg: FdHessianConfig, xc_tag: str, lib_log: TextIO) -> tuple[Any, np.ndarray]:
    """The reference density and pyscf 2.15.0's analytic Hessian (no grid response) at the label geometry, (3N, 3N) symmetrised."""
    mol = labels_mol(geometry, lib_log, max_memory=cfg.max_memory_mb)
    mf = converged_scf(mol, xc_tag, cfg.grid, None)
    n3 = 3 * mol.natm
    H = mf.Hessian().kernel().transpose(0, 2, 1, 3).reshape(n3, n3)
    return mf.make_rdm1(), 0.5 * (H + H.T)


def fd_hessian(geometry: dict, cfg: FdHessianConfig, xc_tag: str, dm0: Any, lib_log: TextIO) -> np.ndarray:
    """Central differences of the grid-response gradient, one json per displaced point (kept on a resume); the raw (unsymmetrised) matrix."""
    x0 = np.asarray(geometry["coords_bohr"], dtype=float)
    natm = len(x0)
    folder = cfg.out / xc_tag
    folder.mkdir(parents=True, exist_ok=True)
    H = np.zeros((3 * natm, 3 * natm))
    for atom in range(natm):
        for d in range(3):
            pair = []
            for sign in (1, -1):
                path = folder / f"point_{atom}_{XYZ[d]}_{'+' if sign > 0 else '-'}.json"
                if path.exists():
                    pair.append(json.loads(path.read_text(encoding="utf-8")))
                    continue
                t0 = time.time()
                x = x0.copy()
                x[atom, d] += sign * cfg.step
                rec, _ = point_record(geometry, x, cfg, xc_tag, dm0, lib_log)
                rec.update(atom=atom, coordinate=XYZ[d], sign=sign, step_bohr=cfg.step, seconds=round(time.time() - t0, 1))
                write_json(path, rec)
                pair.append(rec)
                print(f"(GRF) point {xc_tag} atom {atom + 1}/{natm} {XYZ[d]} {sign:+d}: E {rec['energy_hartree']:.10f} "
                      f"({rec['seconds']:.0f} s)", flush=True)
            H[3 * atom + d] = (np.ravel(pair[0]["gradient"]) - np.ravel(pair[1]["gradient"])) / (2 * cfg.step)
    return H


def frequencies(H: np.ndarray, masses: np.ndarray, coords: np.ndarray) -> np.ndarray:
    """The 3N-6 projected harmonic frequencies (cm-1, sorted, imaginary negative), the corpus convention."""
    return vib_only(freqs_cm(project_tr(0.5 * (H + H.T), masses, coords), masses))


def compare(hessians: dict[str, np.ndarray], masses: np.ndarray, coords: np.ndarray) -> dict[str, Any]:
    """Frequencies and translation residuals of the label, the 2.15.0 analytic and the FD Hessian; the FD's differences from each."""
    freq = {name: frequencies(H, masses, coords) for name, H in hessians.items()}
    residual = {name: translation_residual(H, masses) for name, H in hessians.items()}
    out: dict[str, Any] = {"frequencies_cm": {k: v.tolist() for k, v in freq.items()},
                           "translation": {k: {"max_Ht": r[0], "frequencies_cm": r[1]} for k, r in residual.items()}}
    low = freq["label"] < LOW_MODE_CM
    for name in ("label", "analytic_215"):
        delta = freq["fd_grid_response"] - freq[name]
        out[f"fd_minus_{name}"] = {"max_abs_cm": float(np.abs(delta).max()), "rms_cm": float(np.sqrt(np.mean(delta**2))),
                                   "rms_below_100_cm": float(np.sqrt(np.mean(delta[low] ** 2))) if low.any() else None,
                                   "modes_below_100": int(low.sum()), "lowest_mode_cm": float(delta[0]), "per_mode_cm": delta.tolist()}
    return out


def target_change(per_xc: dict[str, dict]) -> dict[str, float] | None:
    """When both functionals ran: how the sorted per-mode correction ω(ωB97X) − ω(B3LYP) changes from the labels to the FD Hessians."""
    if set(per_xc) != {"b3lyp", "wb97x"}:
        return None
    f = {xc: {k: np.asarray(v) for k, v in r["frequencies_cm"].items()} for xc, r in per_xc.items()}
    change = (f["wb97x"]["fd_grid_response"] - f["b3lyp"]["fd_grid_response"]) - (f["wb97x"]["label"] - f["b3lyp"]["label"])
    low = f["b3lyp"]["label"] < LOW_MODE_CM
    return {"rms_cm": float(np.sqrt(np.mean(change**2))), "max_abs_cm": float(np.abs(change).max()),
            "rms_below_100_cm": float(np.sqrt(np.mean(change[low] ** 2))) if low.any() else float("nan")}


def markdown(record: dict[str, Any]) -> str:
    """The report's table: per functional, the FD Hessian against the label and against the 2.15.0 analytic Hessian."""
    lines = [f"# Grid-response FD Hessian against the labels — {record['molecule']} ({record['n_atoms']} atoms)", "",
             f"Grid {tuple(record['grid'])}, step {record['step_bohr']} bohr, pyscf {record['pyscf']}.", "",
             "| functional | against | max |Δω| | rms Δω | rms Δω < 100 cm⁻¹ (modes) | lowest mode Δω | translation |ω| label / FD |",
             "|---|---|---|---|---|---|---|"]
    for xc, r in record["functionals"].items():
        t = r["translation"]
        for name in ("label", "analytic_215"):
            d = r[f"fd_minus_{name}"]
            low = "—" if d["rms_below_100_cm"] is None else f"{d['rms_below_100_cm']:.2f} ({d['modes_below_100']})"
            lines.append(f"| {xc} | {name} | {d['max_abs_cm']:.2f} | {d['rms_cm']:.2f} | {low} | {d['lowest_mode_cm']:+.2f} | "
                         f"{max(abs(v) for v in t['label']['frequencies_cm']):.2f} / "
                         f"{max(abs(v) for v in t['fd_grid_response']['frequencies_cm']):.2f} |")
    if record["target_change"]:
        tc = record["target_change"]
        lines += ["", f"The per-mode correction ω(ωB97X) − ω(B3LYP), sorted modes: FD against labels rms {tc['rms_cm']:.2f}, max "
                  f"{tc['max_abs_cm']:.2f}, rms below 100 cm⁻¹ {tc['rms_below_100_cm']:.2f} cm⁻¹."]
    return "\n".join(lines) + "\n"


def parse_args(argv: list[str] | None = None) -> FdHessianConfig:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("molecule", type=Path, help="folder with geometry.json and hessian_<xc>_analytic.npz")
    ap.add_argument("out", type=Path)
    ap.add_argument("--xc", nargs="+", default=[t for t, _ in FUNCTIONALS])
    ap.add_argument("--grid", default=f"{LABEL_GRID[0]},{LABEL_GRID[1]}", help="radial,angular")
    ap.add_argument("--step", type=float, default=STEP_BOHR)
    ap.add_argument("--threads", type=int, default=8)
    ap.add_argument("--max-memory", type=int, default=MAX_MEMORY_MB)
    ap.add_argument("--dry-run", action="store_true", help="read the inputs and build the molecule, compute nothing")
    a = ap.parse_args(argv)
    return FdHessianConfig(a.molecule, a.out, tuple(a.xc), tuple(int(v) for v in a.grid.split(",")), a.step, a.threads, a.max_memory,
                           a.dry_run)


def main(argv: list[str] | None = None) -> None:
    cfg = parse_args(argv)
    geometry = json.loads((cfg.molecule / "geometry.json").read_text(encoding="utf-8"))
    coords, masses = np.asarray(geometry["coords_bohr"], dtype=float), np.asarray(geometry["masses_amu"], dtype=float)
    labels = {}
    for xc in cfg.xc_tags:
        with np.load(cfg.molecule / f"hessian_{xc}_analytic.npz") as z:
            labels[xc] = np.asarray(z["H_raw"], dtype=float)
    if cfg.dry_run:
        with open(os.devnull, "w", encoding="utf-8") as quiet:
            mol = labels_mol(geometry, quiet, max_memory=cfg.max_memory_mb)
        print(f"(GRF) dry run: {cfg.molecule.name}, {mol.natm} atoms, {mol.nao} basis functions, {6 * mol.natm} points per functional "
              f"{cfg.xc_tags}, grid {cfg.grid}, step {cfg.step}", flush=True)
        return
    lib.num_threads(cfg.threads)
    cfg.out.mkdir(parents=True, exist_ok=True)
    per_xc = {}
    with open(cfg.out / PYSCF_LOG_NAME, "a", encoding="utf-8") as lib_log:
        for xc in cfg.xc_tags:
            dm0, H_215 = reference(geometry, cfg, xc, lib_log)
            print(f"(GRF) reference {xc}: SCF and analytic Hessian done", flush=True)
            H_fd = fd_hessian(geometry, cfg, xc, dm0, lib_log)
            np.savez_compressed(cfg.out / f"fd_hessian_{xc}.npz", H_fd=H_fd, H_analytic_215=H_215, step=cfg.step, grid=np.array(cfg.grid))
            per_xc[xc] = compare({"label": labels[xc], "analytic_215": H_215, "fd_grid_response": H_fd}, masses, coords)
    record = {"molecule": cfg.molecule.name, "n_atoms": len(coords), "grid": list(cfg.grid), "step_bohr": cfg.step, "pyscf": pyscf_version,
              "functionals": per_xc, "target_change": target_change(per_xc)}
    write_json(cfg.out / "report.json", record)
    write_atomic(cfg.out / "report.md", markdown(record))
    print(markdown(record), flush=True)


if __name__ == "__main__":
    main()
