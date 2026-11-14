"""The label route's low-mode repair, checked where the analytic Hessian is already right (TASKS 216, 14 November 2026).

The repair replaces a Hessian's columns along its soft modes with central differences of grid-response gradients. On a soft mode
there is no reference to check it against — that is the point of the repair. So the check runs it where there *is* one: water's
bending mode at 1679 cm-1, by lowering the threshold so the route treats it as low. The quadrature error pyscf's Hessian leaves on a
stiff mode is small, so the measured column must reproduce the analytic one, and the repaired frequency must come back within
TOL_CM of the analytic frequency. The displacement, the SCF, the blocked grid response, the central difference and the column
replacement all run exactly as they do in production.

The second half of the check reads what the route wrote: the label is the repaired Hessian, the analytic one stays beside it as
H_raw_unrepaired, and low_mode_patch records the threshold, the step, the directions and what moved.

    python probes/label_route_repair_check.py      -> prints the numbers and PASS or FAIL
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import numpy as np

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "modules" / "05_support_predictor" / "corpus"))
sys.path.insert(0, str(PLAN / "probes"))

BELOW_CM = 2000.0        # water's bend (1679 cm-1) and nothing stiffer; its stretches are near 3900
TOL_CM = 0.5             # the repaired frequency against the analytic one, where the quadrature error is negligible
TOL_COLUMN = 1e-6        # hartree/bohr^2 on the measured column against the analytic one; 50 times the 2e-8 observed on water


def check() -> int:
    import analytic_hessians as AH
    from label_route_pin import GRID, WATER, threads
    from library_log import PYSCF_LOG_NAME
    from vibrations import low_mode_directions, vibrational_modes

    threads()
    with tempfile.TemporaryDirectory() as tmp:
        folder = Path(tmp) / "CHECK_water"
        folder.mkdir()
        (folder / "geometry.json").write_text(json.dumps(WATER), encoding="utf-8")
        run = AH.LabelsRun(grid=GRID, charge=0, spin=0, compare_only=False, apt=False, stamp=AH.software())
        masses = np.array(WATER["masses_amu"])
        coords = np.array(WATER["coords_bohr"])
        with (folder / PYSCF_LOG_NAME).open("a", encoding="utf-8") as lib_log:
            mol = AH.labels_mol(WATER, lib_log, run.charge, run.spin, run.max_memory_mb)
            analytic = {tag: AH.compute_hessian(str(folder), mol, tag, xc, run)[0] for tag, xc in AH.FUNCTIONALS}
            repaired, record = AH.repair_low_modes(WATER, analytic, run, lib_log, below_cm=BELOW_CM)
    if not repaired:
        print(f"label_route_repair_check: FAIL, no direction below {BELOW_CM:g} cm-1 was found")
        return 1
    worst_freq, worst_column = 0.0, 0.0
    for tag, H in analytic.items():
        U = low_mode_directions([vibrational_modes(H, masses, coords)], BELOW_CM)
        sm = np.sqrt(np.repeat(masses * AH.AMU2AU, 3))
        analytic_columns = (H / np.outer(sm, sm)) @ U
        measured = (repaired[tag] / np.outer(sm, sm)) @ U
        worst_column = max(worst_column, float(np.abs(measured - analytic_columns).max()))
        before = np.sort(vibrational_modes(H, masses, coords).omega_cm)
        after = np.sort(vibrational_modes(repaired[tag], masses, coords).omega_cm)
        worst_freq = max(worst_freq, float(np.abs(after - before).max()))
        print(f"  {tag}: {U.shape[1]} direction(s); frequencies {before.round(2).tolist()} -> {after.round(2).tolist()} cm-1")
    print(f"  record: {json.dumps(record, sort_keys=True)}")
    print(f"  worst frequency change {worst_freq:.3f} cm-1 (tolerance {TOL_CM}), worst column difference {worst_column:.2e} "
          f"(tolerance {TOL_COLUMN:.0e})")
    ok = worst_freq <= TOL_CM and worst_column <= TOL_COLUMN
    print("label_route_repair_check: " + ("PASS, the measured columns reproduce the analytic ones" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(check())
