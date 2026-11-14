"""The label route's low-mode measurement against the probe's, on a corpus folder the probe has already patched (TASKS 216, test 3).

`Design_2026-11-14_Low_Mode_Repair_In_The_Label_Route.md` section 4: the route's own repair and `probes/low_mode_patch_run.py`'s patch
must give the same thing, or the corpus will slowly hold two kinds of repaired label. The sharpest comparison is the measured column
itself, not the repaired Hessian: the patch file stores the directions it used and the columns it measured, so the route is asked for
the columns along *those* directions and the two are compared directly. That leaves out everything the two routes do not share — the
label Hessian they start from was written by pyscf 2.14.0, the route would recompute it with 2.15.0 — and tests what they do share:
the displacement, the SCF, the blocked grid response and the central difference.

    python probes/label_route_vs_probe.py --id D_ac28161d06
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "modules" / "05_support_predictor" / "corpus"))
sys.path.insert(0, str(PLAN / "probes"))

TOL_COLUMN = 1e-6        # hartree/bohr^2: a gradient threshold of 1e-8 over a step of 0.01 bohr leaves about 1e-8 in a column
LABEL_TAGS = ("b3lyp", "wb97x")


def compare(mol_dir: Path, patch_dir: Path, out: Path) -> int:
    """Ask the route for the columns the probe measured, and report the largest difference per functional."""
    import analytic_hessians as AH
    from label_route_pin import GRID, threads
    from library_log import PYSCF_LOG_NAME

    threads()
    geometry = json.loads((mol_dir / "geometry.json").read_text(encoding="utf-8"))
    run = AH.LabelsRun(grid=GRID, charge=int(geometry["charge"]), spin=int(geometry["multiplicity"]) - 1,
                       compare_only=False, apt=False, stamp=AH.software())
    out.mkdir(parents=True, exist_ok=True)
    worst, record = 0.0, {"id": mol_dir.name, "tolerance": TOL_COLUMN, "per_functional": {}}
    with (out / PYSCF_LOG_NAME).open("a", encoding="utf-8") as lib_log:
        for tag in LABEL_TAGS:
            with np.load(patch_dir / f"hessian_{tag}_analytic_grfpatch.npz", allow_pickle=False) as z:
                directions, probe_columns = np.asarray(z["directions"], float), np.asarray(z["columns"], float)
            route_columns = AH.measured_columns(geometry, directions, AH.XC_BY_TAG[tag], run, lib_log)
            difference = float(np.abs(route_columns - probe_columns).max())
            worst = max(worst, difference)
            record["per_functional"][tag] = {"directions": int(directions.shape[1]), "max_difference": difference,
                                             "column_norm": float(np.abs(probe_columns).max())}
            print(f"(LRVP) {tag}: {directions.shape[1]} direction(s), largest difference {difference:.3e} hartree/bohr^2", flush=True)
    record["worst"] = worst
    record["passed"] = worst <= TOL_COLUMN
    (out / "label_route_vs_probe.json").write_text(json.dumps(record, indent=1), encoding="utf-8")
    print(f"=== (LRVP) {'done' if record['passed'] else 'FAILED'}: worst {worst:.3e} against {TOL_COLUMN:.0e} hartree/bohr^2", flush=True)
    return 0 if record["passed"] else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Compare the label route's low-mode columns with the probe's on one corpus folder.")
    ap.add_argument("--id", default="D_ac28161d06", help="the corpus folder the probe has patched")
    ap.add_argument("--molecules", type=Path, default=PLAN / "modules/05_support_predictor/corpus/molecules")
    ap.add_argument("--patches", type=Path, default=PLAN / "probes/results_m1/low_mode_patch_2026-11-13/corpus")
    ap.add_argument("--out", type=Path, default=PLAN / "probes/results_m1/label_route_vs_probe_2026-11-14")
    a = ap.parse_args(argv)
    mol_dir, patch_dir = a.molecules / a.id, a.patches / a.id
    for path in (mol_dir / "geometry.json", patch_dir / "hessian_b3lyp_analytic_grfpatch.npz"):
        if not path.is_file():
            raise SystemExit(f"{path} is missing: the comparison needs a folder the probe has patched")
    return compare(mol_dir, patch_dir, a.out)


if __name__ == "__main__":
    raise SystemExit(main())
