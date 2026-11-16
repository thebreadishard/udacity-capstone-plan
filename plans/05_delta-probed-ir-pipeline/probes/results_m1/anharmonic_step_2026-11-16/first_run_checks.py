"""The four checks of the anharmonic step's first real run (TASKS 211) — the run that decides whether the pipeline's default
time budget goes from 0 (off) to 120 minutes.

    python first_run_checks.py <pipeline result folder> [--reference <folder>] [--out <json>]

The run is `probes/runspecs/pipeline_benzene_anharmonic.json`: the pipeline on benzene with --anharmonic-minutes 120, its GFN2-xTB
force field computed by the pipeline itself from its own geometry. The reference is the certificate built from stored files
(stored_field_demo/benzene beside this script: S2's stored force field of benzene rotated onto the pipeline's geometry). Read
from the two folders' pipeline.json, band by band in ascending position:

1. Δ_anh of every band the reference steps lies within DELTA_TOL_CM of the reference's (the bands are the same bands: their
   harmonic positions within OMEGA_TOL_CM);
2. no band is lost: every band the reference steps is stepped (the stored case: 28 of 30);
3. the bands of a degenerate pair (harmonic positions within PAIR_TOL_CM) carry steps within PAIR_STEP_TOL_CM of each other;
4. the force field's seconds and peak memory are in the record.

Exit 0 when all four pass; the record names every band that fails one. Run on the reference itself, checks 1–3 pass by
construction and check 4 fails, because a stored field has no run to time: that is this script's own test
(tests/test_anharmonic_first_run_checks.py).
"""
from __future__ import annotations

import argparse
import json
import sys
from itertools import pairwise
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
REFERENCE = HERE / "stored_field_demo" / "benzene"
DELTA_TOL_CM = 1.0          # the coordinator's line: 'within about 1 cm⁻¹ of the stored-field certificate'
OMEGA_TOL_CM = 0.5          # the two results' harmonic positions: the same Hessian route, pyscf 2.14 against 2.15 moved 0.07 at most
PAIR_TOL_CM = 0.05          # the record rounds positions to 0.1: a degenerate pair prints the same ω
PAIR_STEP_TOL_CM = 0.1      # and the same Δ_anh, to the record's rounding


def sticks_of(folder: Path) -> tuple[list[dict], dict]:
    """A result's network sticks in ascending position and its anharmonic summary."""
    rec = json.loads((folder / "pipeline.json").read_text(encoding="utf-8"))
    spectra = rec["spectra"]
    if "anharmonic" not in spectra:
        raise SystemExit(f"{folder}: the record has no anharmonic step at all")
    return sorted(spectra["network"]["sticks"], key=lambda s: s["omega_cm"]), spectra["anharmonic"]


def delta(stick: dict) -> float | None:
    a = stick.get("anharmonic")
    return None if a is None else a["delta_anh_cm"]


def same_bands(run: list[dict], ref: list[dict]) -> None:
    worst = max((abs(a["omega_cm"] - b["omega_cm"]) for a, b in zip(run, ref, strict=False)), default=0.0)
    if len(run) != len(ref) or worst > OMEGA_TOL_CM:
        raise SystemExit(f"the run has {len(run)} bands and the reference {len(ref)}, harmonic positions up to {worst:.2f} cm-1 apart: "
                         "not the same molecule at the same level, so nothing can be compared")


def check_steps(run: list[dict], ref: list[dict]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Checks 1 and 2 over the bands the reference steps."""
    far, lost, worst = [], [], 0.0
    for a, b in zip(run, ref, strict=True):
        if delta(b) is None:
            continue
        if delta(a) is None:
            lost.append({"omega_cm": a["omega_cm"], "reason": (a.get("anharmonic") or {}).get("reason")})
            continue
        worst = max(worst, abs(delta(a) - delta(b)))
        if abs(delta(a) - delta(b)) > DELTA_TOL_CM:
            far.append({"omega_cm": a["omega_cm"], "run": delta(a), "reference": delta(b)})
    stepped = {"run": sum(delta(s) is not None for s in run), "reference": sum(delta(s) is not None for s in ref), "of": len(ref)}
    return ({"passed": not far, "tolerance_cm": DELTA_TOL_CM, "largest_difference_cm": round(worst, 2), "bands_beyond": far},
            {"passed": not lost, "stepped": stepped, "bands_lost": lost})


def check_pairs(run: list[dict]) -> dict[str, Any]:
    """Check 3: neighbours at the same harmonic position carry the same step (or both none)."""
    pairs, unequal = 0, []
    for a, b in pairwise(run):
        if abs(a["omega_cm"] - b["omega_cm"]) > PAIR_TOL_CM:
            continue
        pairs += 1
        da, db = delta(a), delta(b)
        if (da is None) != (db is None) or (da is not None and abs(da - db) > PAIR_STEP_TOL_CM):
            unequal.append({"omega_cm": a["omega_cm"], "steps": [da, db]})
    return {"passed": pairs > 0 and not unequal, "pairs": pairs, "unequal": unequal}


def check_cost(summary: dict) -> dict[str, Any]:
    """Check 4: the run's own force field was timed and its peak memory read."""
    field = summary.get("field") or {}
    return {"passed": field.get("seconds") is not None and field.get("peak_memory_mb") is not None, "seconds": field.get("seconds"),
            "peak_memory_mb": field.get("peak_memory_mb"), "unit": field.get("unit")}


def checks(run_folder: Path, reference: Path = REFERENCE) -> dict[str, Any]:
    run, summary = sticks_of(run_folder)
    ref, _ = sticks_of(reference)
    same_bands(run, ref)
    near, kept = check_steps(run, ref)
    out = {"run": str(run_folder), "reference": str(reference), "status": summary["status"], "reason": summary.get("reason"),
           "1_steps_within_tolerance": near, "2_no_band_lost": kept, "3_degenerate_pairs_equal": check_pairs(run),
           "4_time_and_memory_recorded": check_cost(summary)}
    out["passed"] = all(v["passed"] for k, v in out.items() if k[0].isdigit())
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("result", type=Path)
    ap.add_argument("--reference", type=Path, default=REFERENCE)
    ap.add_argument("--out", type=Path, help="where the record is written (default: first_run_checks.json in the result folder)")
    a = ap.parse_args(argv)
    res = checks(a.result.resolve(), a.reference.resolve())
    out = a.out or a.result / "first_run_checks.json"
    tmp = out.with_suffix(out.suffix + ".tmp")
    tmp.write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    tmp.replace(out)
    for key, value in res.items():
        if key[0].isdigit():
            print(f"{'pass' if value['passed'] else 'FAIL'}  {key}: { {k: v for k, v in value.items() if k != 'passed'} }", flush=True)
    print(f"{'ALL FOUR PASSED: the default may become 120' if res['passed'] else 'NOT PASSED: the default stays 0'} ({out})", flush=True)
    return 0 if res["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
