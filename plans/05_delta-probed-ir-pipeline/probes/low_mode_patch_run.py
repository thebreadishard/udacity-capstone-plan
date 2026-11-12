"""Repair the corpus labels along their low modes with grid-response gradients (TASKS 201 step 3; the arithmetic in low_mode_patch.py).

Per molecule: the label modes below the threshold in either functional give one set of mass-weighted directions; per functional and
direction the SCF is converged at ± one step (the largest atomic displacement STEP_BOHR) from the label geometry, at the label grid, and the
grid-response gradient (our blocked implementation, software ledger 57) gives the true Hessian column along the direction. The repaired
Hessian is written beside the label as <out>/<id>/hessian_<xc>_analytic_grfpatch.npz (H_raw, H_projected, freq_cm as the labels write them,
with the directions, the columns and the frequencies before and after); the label files are only read. A molecule with no low mode gets
<out>/<id>/report.json saying so. Points are json files and are kept on a resume. Runs on pyscf 2.15.0 (~/qc215 in WSL).

    python probes/low_mode_patch_run.py <corpus molecules dir> <out dir> --ids FILE [--below 20] [--step 0.01] [--threads 8]
        [--max-memory MB] [--dry-run]
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

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "modules" / "05_support_predictor" / "corpus"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from analytic_hessians import FUNCTIONALS, freqs_cm, labels_mol, project_tr, software, vib_only
from butterfly_scan import LABEL_GRID, write_json
from hessian_grid_response_fd import FdHessianConfig, converged_scf, point_record
from library_log import PYSCF_LOG_NAME
from low_mode_patch import LABEL_TAGS, LOW_MODE_CM, STEP_BOHR, column, displacement, label_directions, patched_hessian, read_label
from pyscf import lib

if tuple(tag for tag, _ in FUNCTIONALS) != LABEL_TAGS:
    raise ImportError(f"the labels' functionals {FUNCTIONALS} are not low_mode_patch's {LABEL_TAGS}")
XC_TAGS = LABEL_TAGS


@dataclass(frozen=True)
class PatchConfig:
    """The run's settings, checked before any molecule is read."""

    molecules: Path
    out: Path
    ids: tuple[str, ...]
    below_cm: float
    step_bohr: float
    threads: int
    max_memory_mb: int
    dry_run: bool

    def __post_init__(self) -> None:
        if not self.ids or len(set(self.ids)) != len(self.ids):
            raise ValueError("the id list is empty or repeats an id")
        if not 0 < self.below_cm <= 100:
            raise ValueError(f"threshold {self.below_cm} cm⁻¹: in (0, 100]")
        if not 0 < self.step_bohr <= 0.05:
            raise ValueError(f"step {self.step_bohr} bohr: in (0, 0.05]")
        if self.threads < 1 or self.max_memory_mb < 1000:
            raise ValueError(f"threads {self.threads} (≥ 1), max memory {self.max_memory_mb} MB (≥ 1000)")
        missing = [i for i in self.ids if not all((self.molecules / i / f"hessian_{t}_analytic.npz").is_file() for t in XC_TAGS)]
        if missing:
            raise FileNotFoundError(f"{len(missing)} id(s) without both analytic labels, e.g. {missing[:3]}")

    def scf_config(self, molecule_dir: Path) -> FdHessianConfig:
        """The grid-response probe's settings for this molecule (its SCF and gradient functions are reused as they are)."""
        return FdHessianConfig(molecule_dir, self.out, XC_TAGS, LABEL_GRID, 0.005, self.threads, self.max_memory_mb, False)


@dataclass(frozen=True)
class Label:
    """One molecule's label: its id and folder, geometry and both Hessians."""

    mol_id: str
    folder: Path
    geometry: dict
    masses: np.ndarray
    coords: np.ndarray
    hessians: dict[str, np.ndarray]

    @classmethod
    def read(cls, molecule_dir: Path) -> Label:
        geometry, hessians = read_label(molecule_dir)
        return cls(molecule_dir.name, molecule_dir, geometry, np.asarray(geometry["masses_amu"], float),
                   np.asarray(geometry["coords_bohr"], float), hessians)

def gradient_at(label: Label, scf: FdHessianConfig, tag: str, point: tuple[Path, np.ndarray, Any], lib_log: TextIO) -> np.ndarray:
    """The grid-response gradient at one displaced geometry, read back from its json when present."""
    path, coords, dm0 = point
    if path.exists():
        return np.asarray(json.loads(path.read_text(encoding="utf-8"))["gradient"], float)
    t0 = time.time()
    rec, _ = point_record(label.geometry, coords, scf, tag, dm0, lib_log)
    rec["seconds"] = round(time.time() - t0, 1)
    write_json(path, rec)
    print(f"(LMP) point {label.mol_id} {tag} {path.stem}: E {rec['energy_hartree']:.10f} ({rec['seconds']:.0f} s)", flush=True)
    return np.asarray(rec["gradient"], float)


def measured_columns(label: Label, U: np.ndarray, cfg: PatchConfig, tag: str, lib_log: TextIO) -> np.ndarray:
    """The true mass-weighted Hessian columns along every direction, from ± one step of grid-response gradients."""
    scf = cfg.scf_config(label.folder)
    folder = cfg.out / label.mol_id / tag
    folder.mkdir(parents=True, exist_ok=True)
    mol = labels_mol(label.geometry, lib_log, max_memory=cfg.max_memory_mb)
    dm0 = converged_scf(mol, tag, LABEL_GRID, None).make_rdm1()
    columns = []
    for j in range(U.shape[1]):
        step, q = displacement(U[:, j], label.masses, cfg.step_bohr)
        g = [gradient_at(label, scf, tag, (folder / f"dir_{j}_{s}.json", label.coords + sign * step, dm0), lib_log)
             for s, sign in (("plus", 1.0), ("minus", -1.0))]
        columns.append(column(g[0], g[1], q, label.masses))
    return np.stack(columns, axis=1)


def write_patch(label: Label, tag: str, U: np.ndarray, C: np.ndarray, cfg: PatchConfig) -> dict[str, float]:
    """The repaired Hessian beside the label, in the labels' fields; returns the lowest frequency before and after."""
    H = patched_hessian(label.hessians[tag], label.masses, U, C)
    Hp = project_tr(H, label.masses, label.coords)
    before = vib_only(freqs_cm(project_tr(label.hessians[tag], label.masses, label.coords), label.masses))
    after = vib_only(freqs_cm(Hp, label.masses))
    np.savez_compressed(cfg.out / label.mol_id / f"hessian_{tag}_analytic_grfpatch.npz", H_raw=H, H_projected=Hp,
                        freq_cm=freqs_cm(Hp, label.masses), directions=U, columns=C, freq_label_vib_cm=before, freq_patched_vib_cm=after,
                        below_cm=cfg.below_cm, step_bohr=cfg.step_bohr, grid=np.array(LABEL_GRID), software=json.dumps(software(), sort_keys=True))
    return {"lowest_label_cm": float(before[0]), "lowest_patched_cm": float(after[0]),
            "max_abs_change_cm": float(np.abs(after - before).max())}


def patch_molecule(molecule_dir: Path, cfg: PatchConfig, lib_log: TextIO) -> dict[str, Any]:
    """One molecule: its directions, and per functional the measured columns and the repaired Hessian."""
    label = Label.read(molecule_dir)
    U = label_directions(label.folder, cfg.below_cm)
    record: dict[str, Any] = {"id": label.mol_id, "directions": int(U.shape[1]), "below_cm": cfg.below_cm}
    (cfg.out / label.mol_id).mkdir(parents=True, exist_ok=True)
    if U.shape[1]:
        record["functionals"] = {tag: write_patch(label, tag, U, measured_columns(label, U, cfg, tag, lib_log), cfg) for tag in XC_TAGS}
    write_json(cfg.out / label.mol_id / "report.json", record)
    return record


def parse_args(argv: list[str] | None = None) -> PatchConfig:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("molecules", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--ids", type=Path, required=True, help="one molecule id per line ('#' starts a comment)")
    ap.add_argument("--below", type=float, default=LOW_MODE_CM)
    ap.add_argument("--step", type=float, default=STEP_BOHR)
    ap.add_argument("--threads", type=int, default=8)
    ap.add_argument("--max-memory", type=int, default=4096)
    ap.add_argument("--dry-run", action="store_true", help="read every label and count its directions; compute nothing")
    a = ap.parse_args(argv)
    ids = tuple(line.split()[0] for line in a.ids.read_text(encoding="utf-8").splitlines() if line.strip() and not line.startswith("#"))
    return PatchConfig(a.molecules, a.out, ids, a.below, a.step, a.threads, a.max_memory, a.dry_run)


def main(argv: list[str] | None = None) -> None:
    cfg = parse_args(argv)
    if cfg.dry_run:
        counts = {i: int(label_directions(cfg.molecules / i, cfg.below_cm).shape[1]) for i in cfg.ids}
        print(f"(LMP) dry run: {len(counts)} molecules, {sum(1 for c in counts.values() if c)} with low modes, "
              f"{sum(counts.values())} directions below {cfg.below_cm} cm⁻¹ → {4 * sum(counts.values())} gradient points", flush=True)
        return
    lib.num_threads(cfg.threads)
    cfg.out.mkdir(parents=True, exist_ok=True)
    with open(cfg.out / PYSCF_LOG_NAME, "a", encoding="utf-8") as lib_log:
        for k, mol_id in enumerate(cfg.ids, 1):
            done = cfg.out / mol_id / "report.json"
            if done.exists():
                print(f"(LMP) {k}/{len(cfg.ids)} {mol_id}: kept", flush=True)
                continue
            rec = patch_molecule(cfg.molecules / mol_id, cfg, lib_log)
            summary = {t: f"{r['lowest_label_cm']:.2f} → {r['lowest_patched_cm']:.2f}" for t, r in rec.get("functionals", {}).items()}
            print(f"(LMP) {k}/{len(cfg.ids)} {mol_id}: {rec['directions']} direction(s) {summary}", flush=True)


if __name__ == "__main__":
    main()
