"""The second route for TASKS 201 step 3: a repaired label against step 2's full finite-difference Hessian of grid-response gradients.

Registered before the run (13 Nov 2026): PASS when, for both functionals, every vibrational frequency of the repaired Hessian lies within
TOLERANCE_CM of the full FD Hessian's (step 2: the label's modes above 20 cm⁻¹ already lie within 0.43 cm⁻¹ of it, so the repair must bring
the low mode in without moving the rest); else FAIL with the worst mode named. Both Hessians are read by low_mode_patch.vibrational_modes.

    python probes/low_mode_patch_check.py <patch dir of one molecule> <step 2 dir of the same molecule> <its corpus folder>
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from low_mode_patch import LABEL_TAGS, vibrational_modes

TOLERANCE_CM = 0.5


def compare(patch_dir: Path, fd_dir: Path, geometry: dict) -> dict[str, dict[str, float]]:
    """Per functional: the lowest frequency of the label, the repair and the FD Hessian, and the largest |repair − FD| over the modes."""
    masses, coords = np.asarray(geometry["masses_amu"], float), np.asarray(geometry["coords_bohr"], float)
    out = {}
    for tag in LABEL_TAGS:
        with np.load(patch_dir / f"hessian_{tag}_analytic_grfpatch.npz") as z:
            patched = vibrational_modes(np.asarray(z["H_raw"], float), masses, coords).omega_cm
            label_lowest = float(np.asarray(z["freq_label_vib_cm"])[0])
        with np.load(fd_dir / f"fd_hessian_{tag}.npz") as z:
            fd = vibrational_modes(np.asarray(z["H_fd"], float), masses, coords).omega_cm
        worst = int(np.argmax(np.abs(patched - fd)))
        out[tag] = {"lowest_label_cm": label_lowest, "lowest_patched_cm": float(patched[0]), "lowest_fd_cm": float(fd[0]),
                    "max_abs_diff_cm": float(abs(patched[worst] - fd[worst])), "worst_mode_fd_cm": float(fd[worst])}
    return out


def verdict(rows: dict[str, dict[str, float]]) -> str:
    """PASS or FAIL by the module docstring's rule."""
    return "PASS" if all(r["max_abs_diff_cm"] <= TOLERANCE_CM for r in rows.values()) else "FAIL"


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("patch_dir", type=Path)
    ap.add_argument("fd_dir", type=Path)
    ap.add_argument("molecule_dir", type=Path)
    a = ap.parse_args(argv)
    mol_id = a.molecule_dir.name
    if a.patch_dir.name != mol_id:
        raise SystemExit(f"the patch folder {a.patch_dir.name} is not the corpus folder's molecule {mol_id}")
    geometry = json.loads((a.molecule_dir / "geometry.json").read_text(encoding="utf-8"))
    rows = compare(a.patch_dir, a.fd_dir, geometry)
    for tag, r in rows.items():
        print(f"{mol_id} {tag}: lowest label {r['lowest_label_cm']:.2f} → repaired {r['lowest_patched_cm']:.2f}, FD {r['lowest_fd_cm']:.2f}; "
              f"max |repaired − FD| {r['max_abs_diff_cm']:.3f} cm⁻¹ (at {r['worst_mode_fd_cm']:.1f})")
    print(f"verdict {verdict(rows)} (tolerance {TOLERANCE_CM} cm⁻¹)")


if __name__ == "__main__":
    main()
