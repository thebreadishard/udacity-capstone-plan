"""The engine check's read (TASKS 73; `GoalGathering/notes/PreRegistration_2026-11-01_Engine_Check.md`): is the network as accurate on
pyscf + geomeTRIC geometries as on the corpus's psi4 geometries, each route scored against the analytic ωB97X Hessian at its own geometry?

Each route file holds, for the same models and the same molecules, the network's error per mode family and seed (cm⁻¹, the licence's
read-out). The psi4 route also carries check 0: its errors recomputed by the run's own evaluation against the models' recorded read
(`max_abs_difference`), which must be ≤ CHECK0_TOLERANCE before anything is read. The line: in no family is the pyscf route's seed-mean
error more than ENGINE_LINE_CM above the psi4 route's. Differences between the routes themselves (geometry, B3LYP frequencies, corrected
bands) are passed through as information and do not decide.

    python probes/engine_check_read.py <psi4 route.json> <pyscf route.json> [--out <read.json>]
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from promotion_read import FAMILIES

ENGINE_LINE_CM = 0.3          # a tenth of decision 53's 3 cm⁻¹ (the user, 1 Nov 2026: above it the new value must be the less true one)
CHECK0_TOLERANCE = 1e-9       # cm⁻¹: the run's evaluation must reproduce the models' recorded read on the corpus folders
ROUTES = ("psi4", "pyscf")


def load_route(path: Path, expected: str) -> dict:
    with open(path, encoding="utf-8") as f:
        rec = json.load(f)
    if rec.get("route") != expected:
        raise ValueError(f"{path}: route {rec.get('route')!r}, expected {expected!r}")
    missing = [f for f in FAMILIES if f not in rec.get("family_errors", {})]
    if missing:
        raise ValueError(f"{path}: no errors for {missing}")
    for family in FAMILIES:
        values = rec["family_errors"][family]
        if not values or not all(isinstance(v, (int, float)) and math.isfinite(v) for v in values):
            raise ValueError(f"{path}: {family}'s errors are empty or not finite numbers: {values}")
        if len(values) != len(rec["models"]):
            raise ValueError(f"{path}: {family} has {len(values)} seed values for {len(rec['models'])} models")
    return rec


def check_pairing(psi4: dict, pyscf: dict) -> None:
    if psi4["models"] != pyscf["models"]:
        raise ValueError(f"the routes were read with different models: {psi4['models']} against {pyscf['models']}")
    if sorted(psi4["molecules"]) != sorted(pyscf["molecules"]):
        raise ValueError(f"the routes cover different molecules: {sorted(set(psi4['molecules']) ^ set(pyscf['molecules']))}")
    check0 = psi4.get("check0", {}).get("max_abs_difference")
    if check0 is None or not math.isfinite(check0) or check0 > CHECK0_TOLERANCE:
        raise ValueError(f"check 0 not passed on the psi4 route (max |difference| {check0}, needs ≤ {CHECK0_TOLERANCE:g}): the evaluation "
                         "does not reproduce the models' recorded read, so its pyscf numbers cannot be compared with it")


def read(psi4: dict, pyscf: dict) -> dict:
    """Per family the two seed means and their difference (pyscf − psi4), and the verdict against ENGINE_LINE_CM."""
    check_pairing(psi4, pyscf)
    rows = {}
    for family in FAMILIES:
        a = sum(psi4["family_errors"][family]) / len(psi4["family_errors"][family])
        b = sum(pyscf["family_errors"][family]) / len(pyscf["family_errors"][family])
        rows[family] = {"psi4": a, "pyscf": b, "difference": b - a, "within_line": b - a <= ENGINE_LINE_CM}
    passed = all(r["within_line"] for r in rows.values())
    return {"verdict": "PASS" if passed else "FAIL", "line_cm": ENGINE_LINE_CM, "families": rows, "models": psi4["models"],
            "molecules": sorted(psi4["molecules"]), "information": {r: rec.get("information", {}) for r, rec in zip(ROUTES, (psi4, pyscf),
                                                                                                                  strict=True)}}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("psi4", type=Path)
    ap.add_argument("pyscf", type=Path)
    ap.add_argument("--out", type=Path)
    a = ap.parse_args()
    result = read(load_route(a.psi4, "psi4"), load_route(a.pyscf, "pyscf"))
    for family, r in result["families"].items():
        print(f"{family:11s} psi4 {r['psi4']:.3f}  pyscf {r['pyscf']:.3f}  difference {r['difference']:+.3f}  "
              f"{'within' if r['within_line'] else 'BEYOND'} {ENGINE_LINE_CM:g}", flush=True)
    print(f"verdict: {result['verdict']}", flush=True)
    if a.out:
        tmp = a.out.with_suffix(".tmp")
        tmp.write_text(json.dumps(result, indent=1), encoding="utf-8")
        tmp.replace(a.out)


if __name__ == "__main__":
    main()
