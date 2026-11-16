"""Of the 58 molecules the low-mode repair swapped on 14 Nov 2026, which carried a soft mode (|omega| < LOW_MODE_CM) in which label
before the repair (TASKS 73's open count). Before: the kept originals under corpus/superseded_2026-11-14; after: the corpus now.

    python soft_mode_by_label.py <worktree plan folder (code)> <main checkout plan folder (data, read only)>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

CODE, DATA = Path(sys.argv[1]), Path(sys.argv[2])
sys.path.insert(0, str(CODE / "modules" / "05_support_predictor" / "corpus"))
from vibrations import LOW_MODE_CM, vibrational_modes  # noqa: E402  the corpus code is not a package

CORPUS = DATA / "modules" / "05_support_predictor" / "corpus"
TAGS = ("b3lyp", "wb97x")
swap = json.loads((DATA / "probes/results_m1/low_mode_swap_2026-11-14/swap.json").read_text(encoding="utf-8"))
fd222 = json.loads((DATA / "probes/results_m1/low_mode_swap_fd222_2026-11-15/swap.json").read_text(encoding="utf-8"))
recorded = {(r["id"], r["tag"]): r for r in swap["rows"]}
ids = sorted({r["id"] for r in swap["rows"]})
reswapped = sorted({r["id"] for r in fd222["rows"]})


def low(path: Path, masses: np.ndarray, coords: np.ndarray) -> np.ndarray:
    with np.load(path) as z:
        omega = vibrational_modes(np.asarray(z["H_raw"], float), masses, coords).omega_cm
    return np.sort(omega)[:3]


groups: dict[str, list[str]] = {"b3lyp": [], "wb97x": [], "both": [], "wb97x only": [], "b3lyp only": [], "neither": []}
lines = []
worst_mismatch = 0.0
for i in ids:
    geometry = json.loads((CORPUS / "molecules" / i / "geometry.json").read_text(encoding="utf-8"))
    masses, coords = np.asarray(geometry["masses_amu"], float), np.asarray(geometry["coords_bohr"], float)
    before = {t: low(CORPUS / "superseded_2026-11-14" / i / f"hessian_{t}_analytic.npz", masses, coords) for t in TAGS}
    after = {t: low(CORPUS / "molecules" / i / f"hessian_{t}_analytic.npz", masses, coords) for t in TAGS}
    for t in TAGS:
        worst_mismatch = max(worst_mismatch, abs(before[t][0] - recorded[(i, t)]["lowest_label_cm"]))
    soft = {t: bool((np.abs(before[t]) < LOW_MODE_CM).any()) for t in TAGS}
    for t in TAGS:
        if soft[t]:
            groups[t].append(i)
    key = "both" if all(soft.values()) else "wb97x only" if soft["wb97x"] else "b3lyp only" if soft["b3lyp"] else "neither"
    groups[key].append(i)
    lines.append(f"{i:16s} {key:11s} before b3lyp {np.round(before['b3lyp'], 2).tolist()} wb97x {np.round(before['wb97x'], 2).tolist()}"
                 f" | now b3lyp {np.round(after['b3lyp'], 2).tolist()} wb97x {np.round(after['wb97x'], 2).tolist()}"
                 f" | swap.json patched b3lyp {recorded[(i, 'b3lyp')]['lowest_patched_cm']:.2f} wb97x {recorded[(i, 'wb97x')]['lowest_patched_cm']:.2f}"
                 + ("  [re-swapped 15 Nov, fd222]" if i in reswapped else ""))

print(f"molecules {len(ids)}; window |omega| < {LOW_MODE_CM} cm-1; three lowest projected modes per label (cm-1, negative = imaginary)")
print(f"largest |lowest before - swap.json lowest_label_cm| = {worst_mismatch:.2e} cm-1")
for k, v in groups.items():
    print(f"{k:11s} {len(v)}")
for k in ("wb97x only", "neither"):
    print(f"--- {k}")
    print("\n".join(s for s in lines if s[17:28].strip() == k))
print("--- all")
print("\n".join(lines))
