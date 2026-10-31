"""A reused answer against a computed one (TASKS 150): for molecules the pipeline computed itself (the 0.4 reruns of 30 Oct 2026), the
carried network's corrected frequencies (unrounded) on the corpus folder written in the canonical order (`reuse.write_reused`) against
those on the computed run's folder — as built, and with every near-π dihedral on one side of the wrap (`network_dihedral_wrap_check`):
v1.3's pair features carry the raw angle, so geometry noise of 1e-6 bohr can flip a planar molecule's dihedral by 2π and move a band by
1.2 cm⁻¹ between two computed runs as well (TASKS 149, fixed in v1.5); the line is read on the one-sided values. And the corrected
frequencies unchanged by a rotation of the reused folder's frame.

Benzene's and phenanthrene's corpus APTs predate the residual check, so the pipeline computes them (`reuse.apt_refusals`); band positions
need the Hessian alone, so their positions are compared here and their heights are not.

    python probes/pipeline_reuse_check.py --corpus <corpus> --reruns <pipeline_demo_v04 folder> --models <seed.pt> ... --out <folder>
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

import numpy as np

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "modules" / "08_industry_synthesis"))
from m08 import pipeline as P  # noqa: E402
from m08 import reuse as R  # noqa: E402
from network_dihedral_wrap_check import one_sided_dihedrals  # noqa: E402

LIMIT_CM = 0.01            # TASKS 150's test line: a reused answer equals a computed one to 0.01 cm⁻¹ (one side of the wrap)
ROTATION_LIMIT_CM = 1e-3
PAIRS = (("benzene", "c1ccccc1"), ("phenanthrene", "c1ccc2c(c1)ccc1ccccc12"))
BYPASSED = ("APT", "predates the charge")   # the refusals that do not touch the positions (benzene's Hessian file is of 4 Oct's format)


def positions(d: Path, models: tuple[Path, ...]) -> np.ndarray:
    """The seed-mean corrected frequencies (cm⁻¹, sorted, unrounded) of a folder."""
    dH, _ = P.correction(models, d)
    masses = np.asarray(json.loads((d / R.GEOMETRY).read_text(encoding="utf-8"))["masses_amu"], float)
    with np.load(d / R.HESSIAN) as z:
        H = z["H_projected"] + dH
    freq, _ = P.mode_intensities(H, masses, np.zeros((3, H.shape[0])))
    return np.sort(freq)


def reused_folder(smiles: str, corpus: Path, dst: Path) -> dict:
    """The corpus folder written in the canonical order, its APT check bypassed (positions only); the folder and its fit."""
    canonical = P.canonical_smiles(smiles)
    found = R.corpus_folders(canonical, corpus)
    src, written = next((f, s) for f, s in found.folders
                        if not [w for w in R.settings_refusals(f, P.REUSE_SETTINGS) if not any(b in w for b in BYPASSED)])
    xyz, _ = P.RC.start_geometry({"layer": "A", "smiles": canonical})
    start = R.Start(np.asarray([row[1:] for row in xyz], float), P.RC.opt_options_for({"smiles": canonical}))
    fit = R.same_start(src, written, canonical, start)
    if "why" in fit:
        raise SystemExit(f"{smiles}: {fit['why']}")
    R.write_reused(src, dst, np.asarray(fit["order"], int))
    return {"source": src.name, "start_rmsd_angstrom": fit["start_rmsd_angstrom"], "apt_refusals": R.apt_refusals(src, P.REUSE_SETTINGS)}


def rotated(src: Path, dst: Path, angle: float) -> None:
    c, s = np.cos(angle), np.sin(angle)
    rot = np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]]) @ np.array([[1.0, 0.0, 0.0], [0.0, c, -s], [0.0, s, c]])
    shutil.copytree(src, dst)
    g = json.loads((src / R.GEOMETRY).read_text(encoding="utf-8"))
    g["coords_bohr"] = (np.asarray(g["coords_bohr"]) @ rot.T).tolist()
    (dst / R.GEOMETRY).write_text(json.dumps(g), encoding="utf-8")
    big = np.kron(np.eye(len(g["symbols"])), rot)
    with np.load(src / R.HESSIAN) as z:
        h = {k: z[k] for k in z.files}
    h["H_projected"], h["H_raw"] = big @ h["H_projected"] @ big.T, big @ h["H_raw"] @ big.T
    np.savez(dst / R.HESSIAN, **h)
    with np.load(src / R.APT) as z:
        a = {k: z[k] for k in z.files}
    a["apt"] = rot @ a["apt"] @ big.T
    np.savez(dst / R.APT, **a)


def check(corpus: Path, reruns: Path, models: tuple[Path, ...], work: Path) -> dict:
    out = {}
    for name, smiles in PAIRS:
        d = work / name
        d.mkdir()
        rec = reused_folder(smiles, corpus, d)
        built = float(np.abs(positions(d, models) - positions(reruns / name, models)).max())
        with one_sided_dihedrals():
            mine = positions(d, models)
            one_sided = float(np.abs(mine - positions(reruns / name, models)).max())
            rot = float(np.abs(positions_rotated(d, work / f"{name}_rot", models) - mine).max())
        out[name] = rec | {"modes": len(mine), "max_diff_to_computed_cm_as_built": built, "max_diff_to_computed_cm_one_sided": one_sided,
                           "passed": one_sided <= LIMIT_CM, "max_diff_rotated_cm": rot, "rotation_passed": rot <= ROTATION_LIMIT_CM}
    return out


def positions_rotated(d: Path, dst: Path, models: tuple[Path, ...]) -> np.ndarray:
    rotated(d, dst, 0.7)
    return positions(dst, models)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--reruns", type=Path, required=True)
    ap.add_argument("--models", type=Path, nargs="+", required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    with tempfile.TemporaryDirectory() as tmp:
        res = check(a.corpus, a.reruns, tuple(a.models), Path(tmp))
    rec = {"limit_cm": LIMIT_CM, "rotation_limit_cm": ROTATION_LIMIT_CM, "models": [m.name for m in a.models], "molecules": res,
           "passed": all(r["passed"] and r["rotation_passed"] for r in res.values())}
    a.out.mkdir(parents=True, exist_ok=True)
    tmp_file = a.out / "pipeline_reuse_check.json.tmp"
    tmp_file.write_text(json.dumps(rec, indent=1), encoding="utf-8")
    os.replace(tmp_file, a.out / "pipeline_reuse_check.json")
    print(json.dumps(rec, indent=1))
    return 0 if rec["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
