"""How long the pipeline will take on the laptop, known before it runs (TASKS 151: the demo's live molecule must finish within half an hour).
A power law in the 6-31G* basis functions, fitted on the pipeline's own finished runs on the laptop at the same thread count — the
analytic B3LYP Hessian and APT are nearly all of a run's time (module 06's candidate: 12,871 of 13,354 s) and grow as about the third power
of the functions. Basis functions and the fit are module 05's probes' (`anchor_plan.basis_functions`, `anchor_plan.fit_power_law`)."""
from __future__ import annotations

import json
import math
from pathlib import Path

from . import pipeline as P
from .prices import host_class

# isort: split
# probes/, on the path through m08.pipeline
import anchor_plan as AP

RESULTS = P.PLAN / "probes" / "results_m1"
HALF_HOUR_S = 1800.0                   # the demo's live run (the user's demo plan, 30 Oct 2026)


def timed_runs(threads: int, results: Path = RESULTS) -> list[tuple[int, float, str]]:
    """(basis functions, total seconds, folder) of every finished pipeline run on the laptop at this thread count that computed its
    Hessian (a run that reused the corpus's took seconds, TASKS 150)."""
    out = []
    for p in sorted(results.glob("pipeline_*/*/pipeline.json")):
        rec = json.loads(p.read_text(encoding="utf-8"))
        reused = "reuse" in rec and rec["reuse"]["reused"]          # records before 0.5 have no reuse entry: they computed
        if reused or host_class(rec["provenance"]["host"]) != "laptop" or rec["settings"]["threads"] != threads:
            continue
        n = AP.basis_functions(rec["input"]["smiles"], AP.BASIS_FUNCTIONS_631GS)   # the given SMILES: 0.1 records lack the canonical one
        out.append((n, float(sum(rec["seconds"].values())), p.parent.relative_to(results).as_posix()))
    return out


def estimate(smiles: str, threads: int, results: Path = RESULTS) -> dict:
    """The laptop time of a run on this molecule, the fit it comes from, and the largest molecule (in basis functions) that fits half an
    hour. Refused with fewer than three distinct sizes: a power law through two points is a guess."""
    runs = timed_runs(threads, results)
    if len({n for n, _, _ in runs}) < 3:
        raise ValueError(f"{len(runs)} timed laptop runs at {threads} threads cover fewer than three sizes: no estimate")
    a, b = AP.fit_power_law([(n, s) for n, s, _ in runs])
    n = AP.basis_functions(smiles, AP.BASIS_FUNCTIONS_631GS)
    seconds = math.exp(a) * n ** b
    return {"basis_functions": n, "seconds": round(seconds), "within_half_hour": seconds <= HALF_HOUR_S,
            "half_hour_functions": int((HALF_HOUR_S / math.exp(a)) ** (1 / b)), "exponent": round(b, 2), "runs": len(runs),
            "sizes": sorted({n for n, _, _ in runs})}


def announce(smiles: str | None, threads: int) -> str:
    """The pipeline's line about the expected time: the estimate, or why there is none (an xyz input, too few timed runs)."""
    if smiles is None:
        return "no time estimate for an xyz input (the estimate counts basis functions from a SMILES)"
    try:
        return sentence(estimate(smiles, threads))
    except ValueError as e:
        return f"no time estimate: {e}"


def sentence(e: dict) -> str:
    minutes = e["seconds"] / 60
    return (f"estimated laptop time ≈ {minutes:.0f} min for {e['basis_functions']} basis functions "
            f"({'within' if e['within_half_hour'] else 'beyond'} half an hour, whose line lies at ≈ {e['half_hour_functions']}); "
            f"fit seconds ∝ n^{e['exponent']} over {e['runs']} laptop runs of sizes {e['sizes']}")
