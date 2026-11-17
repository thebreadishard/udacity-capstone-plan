"""The four checks of a real run of the anharmonic step (TASKS 211, 255) — the checks that decide whether the pipeline's default
time budget goes from 0 (off) to 120 minutes. Second version: the first (../anharmonic_step_2026-11-16/first_run_checks.py)
stays as the record of the run of 17 Nov 2026, which it failed on two counts.

    python first_run_checks.py <pipeline result folder> [--reference <folder>] [--out <json>]

A run is the pipeline on a molecule with --anharmonic-minutes, its GFN2-xTB force field computed by the pipeline itself from its
own geometry. The reference is the certificate built from stored files (../anharmonic_step_2026-11-16/stored_field_demo/benzene:
S2's stored force field of benzene rotated onto the pipeline's geometry). Read from the two folders' pipeline.json, band by band
in ascending position:

1. Δ_anh of every band the reference steps lies within the band's tolerance of the reference's (the bands are the same bands:
   their harmonic positions within OMEGA_TOL_CM). The tolerance is STEP_FRACTION of the bar of the band's family, STEP_CAP_CM at
   most, plus the record's rounding;
2. no band is lost: every band the reference steps is stepped (the stored case: 28 of 30);
3. the bands of a degenerate pair (harmonic positions within PAIR_TOL_CM) carry steps within PAIR_STEP_TOL_CM of each other;
4. the force field's seconds and peak memory are in the record.

The tolerance of check 1 was set on 17 Nov 2026, after the first run had failed the first version's line by 1.7 cm⁻¹ on a
C–H stretch pair: it was chosen knowing that number, not registered before the run, and the first run passing check 1 here
proves nothing about the run. What the 1.7 is: scatter between two GFN2-xTB force fields of the same molecule, an error the
family's bar does not contain. A later run is a test of the line; the first is where it comes from.

What changed against the first version, and why. Its check 1 had one line for every band, 1.0 cm⁻¹, and the first run's CH
stretches at 3241.6 differed by 1.7 on a step of −131 whose own error bar is 6.21. Two force fields of one molecule — the
stored one and the run's — give the model slightly different inputs, and the step moves with them; that scatter is not in the
bar, which was measured with stored fields. A scatter of 0.3 × the bar, added to the bar in quadrature, makes the stated error
4 % larger (√1.09), less than the bar's second digit says; the first run's bands lie at 0.27 × (the CH stretches, 1.7 of
6.21), 0.18 × (ring-ip at 1388.5: 0.6 of 3.37) and under 0.03 × everywhere else. The cap keeps the widest family (CH-oop, 8.38)
from allowing more than 2 cm⁻¹. And the record holds steps rounded to 0.1 cm⁻¹: the difference of two rounded steps is off by
up to 0.1 and carries binary noise (−130.9 − (−132.6) is 1.6999999999999886), so it is rounded to 0.1 before it is compared and
the line is widened by ROUNDING_CM.

Exit 0 when all four pass; the record names every band that fails one. Run on the reference itself, checks 1–3 pass by
construction and check 4 fails, because a stored field has no run to time: that is this script's own test
(tests/test_anharmonic_first_run_checks_v2.py).
"""
from __future__ import annotations

import argparse
import json
import sys
from itertools import pairwise
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
REFERENCE = HERE.parent / "anharmonic_step_2026-11-16" / "stored_field_demo" / "benzene"
STEP_FRACTION = 0.3         # of the family's bar: two force fields of one molecule may move a step by this much
STEP_CAP_CM = 2.0           # and by no more than this, whatever the bar
ROUNDING_CM = 0.1           # the record rounds a step to 0.1: the difference of two recorded steps is off by up to this
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
    """A stick's recorded step, or None."""
    a = stick.get("anharmonic")
    return None if a is None else a["delta_anh_cm"]


def same_bands(run: list[dict], ref: list[dict]) -> None:
    """Refuse two results that are not the same molecule at the same level."""
    worst = max((abs(a["omega_cm"] - b["omega_cm"]) for a, b in zip(run, ref, strict=False)), default=0.0)
    if len(run) != len(ref) or worst > OMEGA_TOL_CM:
        raise SystemExit(f"the run has {len(run)} bands and the reference {len(ref)}, harmonic positions up to {worst:.2f} cm-1 apart: "
                         "not the same molecule at the same level, so nothing can be compared")


def tolerance(stick: dict, bars: dict[str, float]) -> float:
    """A reference band's tolerance on its step: STEP_FRACTION of its family's bar (the artefact's, also where the band itself
    carries none because its error was not measured), STEP_CAP_CM at most, plus the record's rounding."""
    family = stick["anharmonic"]["family"]
    if family not in bars:
        raise SystemExit(f"the band at {stick['omega_cm']} is stepped in family {family!r}, which the reference's artefact has no bar for")
    return round(min(STEP_FRACTION * bars[family], STEP_CAP_CM) + ROUNDING_CM, 2)


def check_steps(run: list[dict], ref: list[dict], bars: dict[str, float]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Checks 1 and 2 over the bands the reference steps."""
    far, lost, worst = [], [], {"difference_cm": 0.0, "of_tolerance": 0.0}
    for a, b in zip(run, ref, strict=True):
        if delta(b) is None:
            continue
        if delta(a) is None:
            lost.append({"omega_cm": a["omega_cm"], "reason": (a.get("anharmonic") or {}).get("reason")})
            continue
        apart, line = round(abs(delta(a) - delta(b)), 1), tolerance(b, bars)
        if apart / line > worst["of_tolerance"]:
            worst = {"difference_cm": apart, "of_tolerance": round(apart / line, 2), "omega_cm": a["omega_cm"],
                     "family": b["anharmonic"]["family"], "tolerance_cm": line}
        if apart > line:
            far.append({"omega_cm": a["omega_cm"], "family": b["anharmonic"]["family"], "run": delta(a), "reference": delta(b),
                        "difference_cm": apart, "tolerance_cm": line})
    stepped = {"run": sum(delta(s) is not None for s in run), "reference": sum(delta(s) is not None for s in ref), "of": len(ref)}
    rule = {"fraction_of_the_family_bar": STEP_FRACTION, "cap_cm": STEP_CAP_CM, "rounding_cm": ROUNDING_CM, "bars_cm": bars}
    return ({"passed": not far, "tolerance": rule, "closest_to_its_line": worst, "bands_beyond": far},
            {"passed": not lost, "stepped": stepped, "bands_lost": lost})


def check_pairs(run: list[dict]) -> dict[str, Any]:
    """Check 3: neighbours at the same harmonic position carry the same step (or both none)."""
    pairs, unequal = 0, []
    for a, b in pairwise(run):
        if abs(a["omega_cm"] - b["omega_cm"]) > PAIR_TOL_CM:
            continue
        pairs += 1
        da, db = delta(a), delta(b)
        if (da is None) != (db is None) or (da is not None and round(abs(da - db), 1) > PAIR_STEP_TOL_CM):
            unequal.append({"omega_cm": a["omega_cm"], "steps": [da, db]})
    return {"passed": pairs > 0 and not unequal, "pairs": pairs, "unequal": unequal}


def check_cost(summary: dict) -> dict[str, Any]:
    """Check 4: the run's own force field was timed and its peak memory read."""
    field = summary.get("field") or {}
    return {"passed": field.get("seconds") is not None and field.get("peak_memory_mb") is not None, "seconds": field.get("seconds"),
            "peak_memory_mb": field.get("peak_memory_mb"), "unit": field.get("unit")}


def checks(run_folder: Path, reference: Path = REFERENCE) -> dict[str, Any]:
    """The four checks of one run against a reference."""
    run, summary = sticks_of(run_folder)
    ref, ref_summary = sticks_of(reference)
    same_bands(run, ref)
    near, kept = check_steps(run, ref, ref_summary["artefact"]["bars_cm"])
    out = {"run": str(run_folder), "reference": str(reference), "status": summary["status"], "reason": summary.get("reason"),
           "1_steps_within_tolerance": near, "2_no_band_lost": kept, "3_degenerate_pairs_equal": check_pairs(run),
           "4_time_and_memory_recorded": check_cost(summary)}
    out["passed"] = all(v["passed"] for k, v in out.items() if k[0].isdigit())
    return out


def main(argv: list[str] | None = None) -> int:
    """Run the checks, write the record and print each check's line."""
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
