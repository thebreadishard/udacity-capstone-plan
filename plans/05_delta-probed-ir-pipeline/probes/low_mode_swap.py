"""The repaired low-mode Hessians become the corpus's analytic labels (TASKS 201, 14 November 2026).

Registered first: `GoalGathering/notes/PreRegistration_2026-11-14_Low_Mode_Label_Swap.md`, which fixes what is swapped, the four
acceptance criteria and how the swap is undone. This script does only what that note registers. Per molecule it takes `H_raw`,
`H_projected` and `freq_cm` from the patch `probes/low_mode_patch_run.py` wrote, carries the label file's own `energy`, `grid`,
`charge`, `spin` and `reference` over unchanged, keeps both provenance strings, moves the original under `superseded_<date>/` and
replaces the label atomically. A molecule that fails a criterion is reported and left alone.

    python probes/low_mode_swap.py --dry-run     # decides and reports, writes nothing but the record
    python probes/low_mode_swap.py               # swaps, after the repair run has finished
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from low_mode_patch import LOW_MODE_CM
from qc_common import write_atomic

PLAN = Path(__file__).resolve().parents[1]
CORPUS = PLAN / "modules" / "05_support_predictor" / "corpus"
LABEL_TAGS = ("b3lyp", "wb97x")
PATCHED_KEYS = ("H_raw", "H_projected", "freq_cm")      # what the patch replaces
CARRIED_KEYS = ("energy", "grid", "charge", "spin", "reference")  # the label's own, untouched by a Hessian patch
COLLATERAL_CM = 0.5              # registration amendment 1a: the bound on the modes the patch does not target


@dataclass(frozen=True)
class SwapConfig:
    """Where the labels, the repair's output and the record live, and the lines a molecule has to clear to be swapped."""

    molecules: Path
    results: Path
    superseded: Path
    record: Path
    below_cm: float = LOW_MODE_CM
    collateral_cm: float = COLLATERAL_CM
    dry_run: bool = False

    def __post_init__(self) -> None:
        for name in ("molecules", "results"):
            if not getattr(self, name).is_dir():
                raise ValueError(f"{name} {getattr(self, name)} is not a directory")
        if not 0 < self.below_cm <= 50:
            raise ValueError(f"below_cm {self.below_cm}: the registered threshold is 20 cm-1, and nothing above 50 is quadrature noise")
        if not 0 < self.collateral_cm <= 2:
            raise ValueError(f"collateral_cm {self.collateral_cm}: the registration's bound on untargeted modes is 0.5 cm-1")


def sha256(path: Path) -> str:
    """The file's digest, so the record can name what was replaced and what replaced it."""
    with path.open("rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def split_by_change(label_cm: np.ndarray, patched_cm: np.ndarray, directions: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(|change| per mode, the indices of the `directions` largest, the rest), both lists sorted ascending as the patch wrote them.

    The repair targets `directions` modes and may move them by any amount; everything else is collateral and is bounded (registration
    amendment 1a/1b). Same-index rather than nearest-neighbour: if a patched mode crosses a neighbour, two modes show a large change,
    the count exceeds `directions`, and the file is refused rather than quietly accepted.
    """
    if label_cm.shape != patched_cm.shape:
        raise ValueError(f"the patch lists {patched_cm.size} vibrational modes against the label's {label_cm.size}")
    if not 0 < directions < label_cm.size:
        raise ValueError(f"directions {directions}: between 1 and the {label_cm.size} vibrational modes")
    change = np.abs(label_cm - patched_cm)
    order = np.argsort(change)[::-1]
    return change, np.sort(order[:directions]), np.sort(order[directions:])


def structural_reason(label: dict[str, Any], patch: dict[str, Any], cfg: SwapConfig) -> str:
    """Why the patch does not describe the same calculation as the label (criteria 3 and 4); empty when it does."""
    if not np.array_equal(np.asarray(label["grid"]), np.asarray(patch["grid"])):
        return f"grid {np.asarray(patch['grid']).tolist()} is not the label's {np.asarray(label['grid']).tolist()}"
    if np.asarray(label["freq_cm"]).shape != np.asarray(patch["freq_cm"]).shape:
        return "the patch has a different number of frequencies"
    if np.asarray(label["H_projected"]).shape != np.asarray(patch["H_projected"]).shape:
        return "the patch has a different Hessian shape"
    if float(patch["below_cm"]) != cfg.below_cm:
        return f"the patch used below_cm {float(patch['below_cm'])}, not the registered {cfg.below_cm}"
    return ""


def verdict(label: dict[str, Any], patch: dict[str, Any], cfg: SwapConfig) -> tuple[bool, str, dict[str, float]]:
    """The registration's criteria on one label file and its patch: (swap it, the reason when not, the numbers for the record)."""
    label_vib = np.asarray(patch["freq_label_vib_cm"], float)
    patched_vib = np.asarray(patch["freq_patched_vib_cm"], float)
    k = int(np.asarray(patch["directions"]).shape[1])
    change, targeted, collateral = split_by_change(label_vib, patched_vib, k)
    numbers = {"lowest_label_cm": float(label_vib.min()), "lowest_patched_cm": float(patched_vib.min()), "directions": k,
               "targeted_change_cm": [round(float(change[i]), 4) for i in targeted],
               "max_collateral_cm": round(float(change[collateral].max()), 4),
               "targeted_turned_imaginary": int(((label_vib[targeted] > 0) & (patched_vib[targeted] < 0)).sum())}
    reason = structural_reason(label, patch, cfg)
    if not reason and numbers["max_collateral_cm"] > cfg.collateral_cm:
        reason = (f"a mode the patch does not target moved {numbers['max_collateral_cm']:.2f} cm-1, over the registered "
                  f"{cfg.collateral_cm:g}: more than its {k} direction(s) moved")
    turned = int(((label_vib[collateral] > 0) & (patched_vib[collateral] < 0)).sum())
    if not reason and turned:
        reason = f"{turned} untargeted real mode(s) turned imaginary"
    return not reason, reason, numbers


def swapped_arrays(label: dict[str, Any], patch: dict[str, Any], results: Path) -> dict[str, Any]:
    """The new label file's contents: the patch's Hessian and frequencies, the label's own settings, both provenance strings."""
    carried = [k for k in CARRIED_KEYS if k in label]   # the older corpus folders do not all carry every one
    out: dict[str, Any] = {k: np.asarray(patch[k]) for k in PATCHED_KEYS}
    out |= {k: np.asarray(label[k]) for k in carried}
    out["software"] = np.asarray(str(patch["software"]))
    out["low_mode_patch"] = np.asarray(json.dumps({
        "registration": "GoalGathering/notes/PreRegistration_2026-11-14_Low_Mode_Label_Swap.md",
        "results": results.name, "below_cm": float(patch["below_cm"]), "step_bohr": float(patch["step_bohr"]),
        "directions": int(np.asarray(patch["directions"]).shape[1]), "carried": carried,
        "label_software": str(label["software"]) if "software" in label else ""}))
    return out


def write_label(path: Path, arrays: dict[str, Any]) -> None:
    """Write the new label beside the old one and move it over: a reader never sees a half-written file."""
    tmp = path.with_suffix(".npz.tmp")
    with tmp.open("wb") as fh:
        np.savez(fh, **arrays)
    os.replace(tmp, path)


def decide(mol_id: str, tag: str, cfg: SwapConfig) -> dict[str, Any]:
    """One molecule's one functional, read only: the verdict, its reason and the numbers the record keeps."""
    label_path = cfg.molecules / mol_id / f"hessian_{tag}_analytic.npz"
    patch_path = cfg.results / mol_id / f"hessian_{tag}_analytic_grfpatch.npz"
    if not (label_path.is_file() and patch_path.is_file()):
        return {"id": mol_id, "tag": tag, "swapped": False, "reason": "label or patch file missing"}
    with np.load(label_path, allow_pickle=False) as label, np.load(patch_path, allow_pickle=False) as patch:
        ok, reason, numbers = verdict({k: label[k] for k in label.files}, {k: patch[k] for k in patch.files}, cfg)
    return {"id": mol_id, "tag": tag, "swapped": False, "reason": reason, **numbers,
            "sha256_before": sha256(label_path), "sha256_patch": sha256(patch_path), "ok": ok}


def apply_one(row: dict[str, Any], cfg: SwapConfig) -> None:
    """Keep the original under `superseded_<date>/` and move the new label over it; `row` gains the digest and the kept path."""
    label_path = cfg.molecules / row["id"] / f"hessian_{row['tag']}_analytic.npz"
    patch_path = cfg.results / row["id"] / f"hessian_{row['tag']}_analytic_grfpatch.npz"
    with np.load(label_path, allow_pickle=False) as label, np.load(patch_path, allow_pickle=False) as patch:
        arrays = swapped_arrays({k: label[k] for k in label.files}, {k: patch[k] for k in patch.files}, cfg.results)
    kept = cfg.superseded / row["id"]
    kept.mkdir(parents=True, exist_ok=True)
    shutil.copy2(label_path, kept / label_path.name)
    write_label(label_path, arrays)
    row["swapped"] = True
    row["sha256_after"] = sha256(label_path)
    saved = kept / label_path.name
    row["kept"] = str(saved.relative_to(PLAN) if saved.is_relative_to(PLAN) else saved)   # absolute under a test's tmp_path


def read_ids(ids: Path) -> list[str]:
    """The molecule ids the repair selected, from the file `low_mode_patch.py select` wrote."""
    return [line.split()[0] for line in ids.read_text(encoding="utf-8").splitlines() if line and not line.startswith("#")]


def swap_molecule(mol_id: str, cfg: SwapConfig) -> list[dict[str, Any]]:
    """Both labels of one molecule, together or not at all: a mixed pair would make dH the difference of two different treatments."""
    rows = [decide(mol_id, tag, cfg) for tag in LABEL_TAGS]
    if all(r.get("ok") for r in rows) and not cfg.dry_run:
        for row in rows:
            apply_one(row, cfg)
    elif not all(r.get("ok") for r in rows):
        for row in rows:
            if row.get("ok"):
                row["reason"] = "the molecule's other label was refused, and a mixed pair would make dH mix two treatments"
    return rows


def imaginary_after(rows: list[dict[str, Any]]) -> bool:
    """Whether the molecule still carries an imaginary mode once both labels are patched (the trainer's drop rule)."""
    return any(r.get("lowest_patched_cm", 0.0) < 0 for r in rows)


def run(ids: list[str], cfg: SwapConfig) -> dict[str, Any]:
    """Every selected molecule's two labels, with the summary the record and the console both use."""
    per_molecule = {mol_id: swap_molecule(mol_id, cfg) for mol_id in ids}
    rows = [r for mol_rows in per_molecule.values() for r in mol_rows]
    refused = [r for r in rows if r["reason"]]
    clean = {i: rs for i, rs in per_molecule.items() if all(not r["reason"] for r in rs)}
    cleared = sorted(i for i, rs in clean.items() if any(r["lowest_label_cm"] < 0 for r in rs) and not imaginary_after(rs))
    gained = sorted(i for i, rs in clean.items() if all(r["lowest_label_cm"] >= 0 for r in rs) and imaginary_after(rs))
    return {"registration": "PreRegistration_2026-11-14_Low_Mode_Label_Swap.md", "dry_run": cfg.dry_run,
            "molecules": len(ids), "files": len(rows), "swapped": sum(bool(r["swapped"]) for r in rows),
            "refused": [{"id": r["id"], "tag": r["tag"], "reason": r["reason"]} for r in refused],
            "imaginary_cleared": cleared, "imaginary_gained": gained,
            "max_collateral_cm": max((r.get("max_collateral_cm", 0.0) for r in rows), default=0.0), "rows": rows}


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description="Swap the repaired low-mode Hessians into the corpus's analytic labels.")
    ap.add_argument("--molecules", type=Path, default=CORPUS / "molecules")
    ap.add_argument("--results", type=Path, default=PLAN / "probes/results_m1/low_mode_patch_2026-11-13/corpus")
    ap.add_argument("--ids", type=Path, default=PLAN / "probes/results_m1/low_mode_patch_2026-11-13/ids_below20.txt")
    ap.add_argument("--superseded", type=Path, default=CORPUS / "superseded_2026-11-14")
    ap.add_argument("--record", type=Path, default=PLAN / "probes/results_m1/low_mode_swap_2026-11-14")
    ap.add_argument("--dry-run", action="store_true", help="decide and record, write no label and move no file")
    a = ap.parse_args(argv)
    cfg = SwapConfig(a.molecules, a.results, a.superseded, a.record, dry_run=a.dry_run)
    read = run(read_ids(a.ids), cfg)
    a.record.mkdir(parents=True, exist_ok=True)
    name = "swap_dry_run.json" if cfg.dry_run else "swap.json"
    write_atomic(a.record / name, json.dumps(read, indent=1))
    print(f"{'would swap' if cfg.dry_run else 'swapped'} {read['swapped'] if not cfg.dry_run else read['files'] - len(read['refused'])}"
          f" of {read['files']} label files over {read['molecules']} molecules")
    print(f"  largest untargeted change: {read['max_collateral_cm']:.3f} cm-1 (line {cfg.collateral_cm:g})")
    print(f"  molecules whose imaginary mode clears: {len(read['imaginary_cleared'])}, that gain one: {len(read['imaginary_gained'])}")
    for refusal in read["refused"]:
        print(f"  refused {refusal['id']} {refusal['tag']}: {refusal['reason']}")


if __name__ == "__main__":
    main()
