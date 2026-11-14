"""The label route's own output, pinned before the low-mode repair moves into it (TASKS 216, 14 November 2026).

`Design_2026-11-14_Low_Mode_Repair_In_The_Label_Route.md` section 2: a molecule whose lowest vibration lies above the threshold must
come out of the route unchanged. `process_molecule` is what changes, so the pin goes through it: a water folder is written, the route
runs on it, and the two label files it writes are stored. Water's lowest vibration is near 1600 cm-1, far above the 20 cm-1 trigger,
so the repair must never touch it.

Thread order changes the last bits of a summed integral, so the comparison is to a stated tolerance rather than to the bit, and the
run is pinned to one thread. The tolerance is far below the quadrature error being corrected (TOL_H hartree/bohr**2, TOL_FREQ cm-1).

    python probes/label_route_pin.py write tests/fixtures/label_route_water.npz     # before the change
    python probes/label_route_pin.py check tests/fixtures/label_route_water.npz     # after it, and in the tests
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

import numpy as np

PLAN = Path(__file__).resolve().parents[1]
CORPUS_CODE = PLAN / "modules" / "05_support_predictor" / "corpus"
sys.path.insert(0, str(CORPUS_CODE))
sys.path.insert(0, str(PLAN / "probes"))

LABEL_TAGS = ("b3lyp", "wb97x")
PINNED_KEYS = ("H_raw", "H_projected", "freq_cm", "energy")
GRID = (99, 590)                 # the labels' own grid
THREADS = 1                      # one thread, so the summation order is the same on every run
TOL_H = 1e-10                    # hartree/bohr**2, against a quadrature error that reaches 1e-3 along a soft mode
TOL_FREQ = 1e-6                  # cm-1, against the 0.5 cm-1 the repair is allowed to move an untargeted mode
TOL_ENERGY = 1e-10               # hartree

WATER = {
    "symbols": ["O", "H", "H"],
    "coords_bohr": [[0.0, 0.0, 0.2217], [0.0, 1.4309, -0.8867], [0.0, -1.4309, -0.8867]],
    "masses_amu": [15.99491461957, 1.00782503207, 1.00782503207],
    "charge": 0,
    "multiplicity": 1,
    "optimised_at": "not optimised: a fixed geometry is enough to pin the route's arithmetic",
}


def label_record(geometry: dict[str, Any], grid: tuple[int, int] = GRID) -> dict[str, np.ndarray]:
    """Run the label route on one geometry in a temporary folder and return what it wrote, tag by tag."""
    import analytic_hessians as AH
    from library_log import PYSCF_LOG_NAME

    with tempfile.TemporaryDirectory() as tmp:
        folder = Path(tmp) / "PIN_water"
        folder.mkdir()
        (folder / "geometry.json").write_text(json.dumps(geometry), encoding="utf-8")
        run = AH.LabelsRun(grid=grid, charge=0, spin=0, compare_only=False, apt=False, stamp=AH.software())
        with (folder / PYSCF_LOG_NAME).open("a", encoding="utf-8") as lib_log:
            errors = AH.process_molecule(str(folder), run, lib_log)
        if errors:
            raise RuntimeError(f"the label route reported {errors}")
        out = {}
        for tag in LABEL_TAGS:
            with np.load(folder / f"hessian_{tag}_analytic.npz", allow_pickle=False) as z:
                out |= {f"{tag}_{key}": np.asarray(z[key]) for key in PINNED_KEYS}
    return out


def differences(pinned: dict[str, np.ndarray], fresh: dict[str, np.ndarray]) -> list[str]:
    """One line per entry that moved further than its tolerance; empty when the route still writes what it wrote."""
    tolerance = {"H_raw": TOL_H, "H_projected": TOL_H, "freq_cm": TOL_FREQ, "energy": TOL_ENERGY}
    out = []
    for name in sorted(set(pinned) | set(fresh)):
        if name not in pinned or name not in fresh:
            out.append(f"{name}: in {'the fixture' if name in pinned else 'the fresh record'} only")
            continue
        tol = tolerance[name.split("_", 1)[1]]
        worst = float(np.abs(np.asarray(fresh[name], float) - np.asarray(pinned[name], float)).max())
        if worst > tol:
            out.append(f"{name}: moved {worst:.3e}, over its tolerance {tol:.0e}")
    return out


def threads(n: int = THREADS) -> None:
    """Pin the thread count before pyscf is imported, so the integral summation order is reproducible."""
    import os
    for name in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
        os.environ[name] = str(n)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Write or check the label route's pinned output on water.")
    ap.add_argument("action", choices=("write", "check"))
    ap.add_argument("fixture", type=Path)
    a = ap.parse_args(argv)
    threads()
    fresh = label_record(WATER)
    if a.action == "write":
        a.fixture.parent.mkdir(parents=True, exist_ok=True)
        np.savez(a.fixture, **fresh)
        print(f"pinned {len(fresh)} entries to {a.fixture}; water's lowest vibration "
              f"{np.sort(np.asarray(fresh['b3lyp_freq_cm'], float))[6]:.1f} cm-1")
        return 0
    with np.load(a.fixture, allow_pickle=False) as z:
        pinned = {k: np.asarray(z[k]) for k in z.files}
    found = differences(pinned, fresh)
    for line in found:
        print(f"label_route_pin: {line}")
    print("label_route_pin: " + ("PASS, the route writes what it wrote" if not found else f"FAIL, {len(found)} entries moved"))
    return 1 if found else 0


if __name__ == "__main__":
    raise SystemExit(main())
