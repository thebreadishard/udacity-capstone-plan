"""Which corpus molecules carry a low or imaginary label mode, and which of them the low-mode repair covers (TASKS 201, 14 Nov 2026).

The repair (`probes/low_mode_patch.py`) selects a molecule when a projected vibrational mode of either analytic label falls inside
|omega| < LOW_MODE_CM, where the quadrature error of pyscf's CPU DFT Hessian reaches several cm-1. This reads every corpus folder's two
analytic labels, takes the lowest projected vibrational frequency of each, and bands them, so the selection's coverage and the molecules
outside it are a measurement rather than a count from memory. A molecule with any imaginary mode never reaches a release
(`m05/build_release.py` skips it), so the lowest frequency's sign decides whether its rows train at all.

    python probes/low_mode_coverage.py [--ids <selection>] [--out <folder>]
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from low_mode_patch import LOW_MODE_CM, read_label, vibrational_modes
from qc_common import write_atomic

PLAN = Path(__file__).resolve().parents[1]
CORPUS = PLAN / "modules" / "05_support_predictor" / "corpus" / "molecules"
LABEL_TAGS = ("b3lyp", "wb97x")
BANDS: tuple[tuple[str, float, float], ...] = (
    ("below -50", -np.inf, -50.0), ("-50 to -20", -50.0, -20.0), ("-20 to 0", -20.0, 0.0),
    ("0 to 20", 0.0, LOW_MODE_CM), ("20 to 30", LOW_MODE_CM, 30.0), ("above 30", 30.0, np.inf),
)


@dataclass(frozen=True)
class Lowest:
    """One corpus folder's lowest projected vibrational frequency in each analytic label (cm-1, negative = imaginary)."""

    mol_id: str
    b3lyp: float
    wb97x: float

    @property
    def lowest(self) -> float:
        return min(self.b3lyp, self.wb97x)


def lowest_modes(corpus: Path) -> list[Lowest]:
    """Every folder with both analytic labels, with the lowest vibrational frequency of each."""
    rows = []
    for folder in sorted(corpus.iterdir()):
        if not (folder.is_dir() and all((folder / f"hessian_{t}_analytic.npz").is_file() for t in LABEL_TAGS)):
            continue
        geometry, hessians = read_label(folder)
        masses = np.asarray(geometry["masses_amu"], float)
        coords = np.asarray(geometry["coords_bohr"], float)
        lowest = [float(vibrational_modes(H, masses, coords).omega_cm[0]) for H in hessians.values()]
        rows.append(Lowest(folder.name, *lowest))
    return rows


def read_selection(ids: Path) -> set[str]:
    """The molecule ids the repair selected, from the file `low_mode_patch.py select` wrote."""
    return {line.split()[0] for line in ids.read_text(encoding="utf-8").splitlines() if line and not line.startswith("#")}


def report(rows: list[Lowest], selected: set[str]) -> dict[str, object]:
    """The banded coverage: how many molecules sit in each band and how many of them the repair covers."""
    bands = [{"band": name, "molecules": len(inside), "selected": sum(r.mol_id in selected for r in inside),
              "ids": [r.mol_id for r in inside] if len(inside) <= 60 else []}
             for name, lo, hi in BANDS
             for inside in ([r for r in rows if lo <= r.lowest < hi],)]
    imaginary = [r for r in rows if r.lowest < 0]
    return {"folders": len(rows), "selected": len(selected), "bands": bands,
            "imaginary": {"molecules": len(imaginary), "selected": sum(r.mol_id in selected for r in imaginary),
                          "both_labels": len([r for r in rows if r.b3lyp < 0 and r.wb97x < 0]),
                          "note": "m05/build_release.py skips a molecule with any imaginary mode, so these rows never train"},
            "below_threshold_not_selected": [r.mol_id for r in rows if r.lowest < LOW_MODE_CM and r.mol_id not in selected],
            "selected_not_below_threshold": sorted(selected - {r.mol_id for r in rows if r.lowest < LOW_MODE_CM})}


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description="Band the corpus by its lowest label mode and read the low-mode repair's coverage.")
    ap.add_argument("--corpus", type=Path, default=CORPUS)
    ap.add_argument("--ids", type=Path, default=PLAN / "probes/results_m1/low_mode_patch_2026-11-13/ids_below20.txt")
    ap.add_argument("--out", type=Path, default=PLAN / "probes/results_m1/low_mode_coverage_2026-11-14")
    a = ap.parse_args(argv)
    rows = lowest_modes(a.corpus)
    if not rows:
        raise RuntimeError(f"no corpus folder under {a.corpus} carries both analytic labels")
    read = report(rows, read_selection(a.ids))
    a.out.mkdir(parents=True, exist_ok=True)
    write_atomic(a.out / "lowest_modes.json", json.dumps([r.__dict__ for r in rows], indent=1))
    write_atomic(a.out / "coverage.json", json.dumps(read, indent=1))
    print(f"folders {read['folders']}, selected by the repair {read['selected']}")
    for band in read["bands"]:
        print(f"  lowest label mode {band['band']:>10} cm-1: {band['molecules']:4d} molecules, selected {band['selected']}")
    im = read["imaginary"]
    print(f"imaginary in at least one label: {im['molecules']} molecules ({im['both_labels']} in both), "
          f"{im['selected']} of them in the repair -- none of these train")


if __name__ == "__main__":
    main()
