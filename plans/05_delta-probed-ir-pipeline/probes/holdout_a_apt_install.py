"""Puts the clean hold-out (a)'s refined APTs (and benzene's new B3LYP Hessian) from `probes/holdout_a_apt_run.sh` into the corpus (1 Nov
2026, TASKS 146: the eight join the pipeline show by reuse).

    python probes/holdout_a_apt_install.py <run dir> <corpus molecules dir> [--apply]

Every row of <run dir>/ids.tsv is checked before anything changes, and nothing changes unless all pass. The check is the pipeline's own:
`m08.reuse.settings_refusals` with the pipeline's settings, on a staged copy of the corpus folder with the new files in place; a new
Hessian must also lie within HESSIAN_TOL of the corpus's old one. Without --apply the plan is printed. With it, each replaced file is first
copied to <corpus>/../superseded_2026-11-01/<id>/ (a copy already there is kept: it is the original), the new file goes in by a temporary
copy and os.replace, the folder is checked again in place, and <run dir>/install.json records what went in.
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
from m08 import reuse as R  # noqa: E402
from m08.pipeline import REUSE_SETTINGS  # noqa: E402

SUPERSEDED = "superseded_2026-11-01"
# Eh/bohr²: the same method, geometry and grid, so only the SCF's convergence separates the two Hessians; far below a 0.1 cm⁻¹ shift
HESSIAN_TOL = 1e-5
NEW_FILES = {"apt": (R.APT,), "hessian": (R.HESSIAN, R.APT)}


def rows(run_dir: Path) -> list[tuple[str, str]]:
    """(id, step) of every row of ids.tsv; a step other than apt or hessian is refused."""
    out = []
    for line in (run_dir / "ids.tsv").read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.startswith("#"):
            mol_id, step = line.split("\t")[:2]
            if step not in NEW_FILES:
                raise ValueError(f"{mol_id}: step '{step}' is neither apt nor hessian")
            out.append((mol_id, step))
    return out


def hessian_deviation(new: Path, old: Path) -> float:
    """The largest element of the difference of the two projected B3LYP Hessians."""
    with np.load(new / R.HESSIAN) as a, np.load(old / R.HESSIAN) as b:
        return float(np.abs(a["H_projected"] - b["H_projected"]).max())


def refusals(run_dir: Path, corpus: Path, mol_id: str, step: str) -> list[str]:
    """Every reason the molecule's new files may not go in; empty when they may."""
    new, old = run_dir / mol_id, corpus / mol_id
    missing = [f for f in NEW_FILES[step] if not (new / f).is_file()]
    if missing:
        return [f"{mol_id}: no new {', '.join(missing)}"]
    reasons = []
    if step == "hessian" and (dev := hessian_deviation(new, old)) > HESSIAN_TOL:
        reasons.append(f"{mol_id}: the new Hessian differs from the corpus's by {dev:.1e} > {HESSIAN_TOL:g}")
    with tempfile.TemporaryDirectory() as tmp:
        staged = Path(tmp) / mol_id
        staged.mkdir()
        for f in R.SOURCE_FILES:
            src = new / f if f in NEW_FILES[step] else old / f
            if src.is_file():
                shutil.copy2(src, staged / f)
        reasons += R.settings_refusals(staged, REUSE_SETTINGS)
    return reasons


def install(run_dir: Path, corpus: Path, mol_id: str, step: str) -> dict:
    """The new files of one checked molecule into its corpus folder, the originals kept; raises when the folder then fails the check."""
    target, backup = corpus / mol_id, corpus.parent / SUPERSEDED / mol_id
    backup.mkdir(parents=True, exist_ok=True)
    for f in NEW_FILES[step]:
        if not (backup / f).exists():
            shutil.copy2(target / f, backup / f)
        tmp = target / f"{f}.new"
        shutil.copy2(run_dir / mol_id / f, tmp)
        os.replace(tmp, target / f)
    after = R.settings_refusals(target, REUSE_SETTINGS)
    if after:
        raise RuntimeError(f"{mol_id}: installed but refused in place: {after}; the originals are in {backup}")
    return {"id": mol_id, "step": step, "files": list(NEW_FILES[step]), "superseded": str(backup)}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("run_dir", type=Path)
    ap.add_argument("corpus", type=Path, help="the corpus's molecules directory")
    ap.add_argument("--apply", action="store_true", help="install; without it the checks and the plan only")
    a = ap.parse_args()
    plan = rows(a.run_dir)
    reasons = [r for mol_id, step in plan for r in refusals(a.run_dir, a.corpus, mol_id, step)]
    if reasons:
        raise SystemExit("nothing installed:\n  " + "\n  ".join(reasons))
    for mol_id, step in plan:
        print(f"{mol_id}: {', '.join(NEW_FILES[step])} pass the pipeline's reuse check{'' if a.apply else ' (dry: not installed)'}")
    if not a.apply:
        return
    record = [install(a.run_dir, a.corpus, mol_id, step) for mol_id, step in plan]
    tmp = a.run_dir / "install.json.tmp"
    tmp.write_text(json.dumps(record, indent=1), encoding="utf-8")
    os.replace(tmp, a.run_dir / "install.json")
    print(f"installed {len(record)} molecules; originals in {a.corpus.parent / SUPERSEDED}")


if __name__ == "__main__":
    main()
