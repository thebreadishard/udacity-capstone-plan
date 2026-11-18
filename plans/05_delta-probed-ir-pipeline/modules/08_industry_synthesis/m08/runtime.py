"""How long the pipeline will take on the laptop, known before it runs (TASKS 151: the demo's live molecule must finish within half an hour).
A power law in the 6-31G* basis functions, fitted on the pipeline's own finished runs on the laptop at the same thread count and on the
same pyscf version in step 3 (pipeline 0.10 moved step 3 from 2.14.0 to 2.15.0, whose CPHF can fall back to a per-root solve:
probes/runspecs/pipeline_softmode_minimum.json) — the
analytic B3LYP Hessian and APT are nearly all of a run's time (module 06's candidate: 12,871 of 13,354 s) and grow as about the third power
of the functions. Basis functions and the fit are module 05's probes' (`anchor_plan.basis_functions`, `anchor_plan.fit_power_law`)."""
from __future__ import annotations

import json
import math
from pathlib import Path

from . import paths
from . import pipeline as P  # noqa: F401  imported for its side effect: it puts probes/ (anchor_plan) on the path
from .prices import host_class

# isort: split
# probes/, on the path through m08.pipeline
import anchor_plan as AP

RESULTS = paths.resolve("probes/results_m1", must_exist=False)
HALF_HOUR_S = 1800.0                   # the demo's live run (the user's demo plan, 30 Oct 2026)


def timed_runs(threads: int, results: Path = RESULTS) -> list[tuple[int, float, str, str | None]]:
    """(basis functions, total seconds, folder, step 3's pyscf version) of every finished pipeline run on the laptop at this thread count
    that computed its Hessian (a run that reused the corpus's took seconds, TASKS 150). The version is the record's (None where it names
    none): step 3 is nearly all of a run's time, and pyscf 2.15.0's runs are not 2.14.0's."""
    out = []
    for p in sorted(results.glob("pipeline_*/*/pipeline.json")):
        rec = json.loads(p.read_text(encoding="utf-8"))
        reused = "reuse" in rec and rec["reuse"]["reused"]          # records before 0.5 have no reuse entry: they computed
        if reused or host_class(rec["provenance"]["host"]) != "laptop" or rec["settings"]["threads"] != threads:
            continue
        n = AP.basis_functions(rec["input"]["smiles"], AP.BASIS_FUNCTIONS_631GS)   # the given SMILES: 0.1 records lack the canonical one
        out.append((n, float(sum(rec["seconds"].values())), p.parent.relative_to(results).as_posix(), pyscf_of(rec)))
    return out


def pyscf_of(rec: dict) -> str | None:
    """Step 3's pyscf version as a computed run's record names it."""
    return ((rec.get("low_level") or {}).get("b3lyp", {}).get("software") or {}).get("pyscf")


def estimate(smiles: str, threads: int, pyscf: str, results: Path = RESULTS) -> dict:
    """The laptop time of a run on this molecule with step 3 on this pyscf version, the fit it comes from (that version's runs alone),
    and the largest molecule (in basis functions) that fits half an hour. Refused with fewer than three distinct sizes: a power law
    through two points is a guess."""
    runs = [r for r in timed_runs(threads, results) if r[3] == pyscf]
    if len({n for n, *_ in runs}) < 3:
        raise ValueError(f"{len(runs)} timed laptop runs at {threads} threads on pyscf {pyscf} cover fewer than three sizes: no estimate "
                         "(the fit is per pyscf version)")
    a, b = AP.fit_power_law([(n, s) for n, s, *_ in runs])
    n = AP.basis_functions(smiles, AP.BASIS_FUNCTIONS_631GS)
    seconds = math.exp(a) * n ** b
    return {"basis_functions": n, "seconds": round(seconds), "within_half_hour": seconds <= HALF_HOUR_S,
            "half_hour_functions": int((HALF_HOUR_S / math.exp(a)) ** (1 / b)), "exponent": round(b, 2), "runs": len(runs),
            "sizes": sorted({n for n, *_ in runs}), "pyscf": pyscf}


def fitted_versions(threads: int, results: Path = RESULTS) -> list[str]:
    """The pyscf versions whose timed runs at this thread count cover three sizes or more."""
    runs = timed_runs(threads, results)
    return sorted(v for v in {r[3] for r in runs} if v is not None and len({n for n, _, _, w in runs if w == v}) >= 3)


def estimate_or_other(smiles: str, threads: int, pyscf: str, results: Path = RESULTS) -> dict | None:
    """The estimate on `pyscf` (`other_version` False); where that version has no fit, the newest fitted other version's
    (`other_version` True, its own version under `pyscf`); None where no version has one."""
    try:
        return estimate(smiles, threads, pyscf, results) | {"other_version": False}
    except ValueError:
        others = [v for v in fitted_versions(threads, results) if v != pyscf]
        return estimate(smiles, threads, others[-1], results) | {"other_version": True} if others else None


def announce(smiles: str | None, threads: int, pyscf: str | None, results: Path = RESULTS) -> str:
    """The pipeline's line about the expected time: the estimate for step 3's pyscf version, or why there is none (an xyz input, an
    interpreter whose version is not known before the run, too few timed runs on that version) — with, in the last case, what the
    versions that have a fit give, each named as another version's time."""
    if smiles is None:
        return "no time estimate for an xyz input (the estimate counts basis functions from a SMILES)"
    if pyscf is None:
        return ("no time estimate: step 3 runs an interpreter given with --pyscf-python, whose pyscf version is not known before the run, "
                "and the estimate is fitted per pyscf version")
    try:
        return sentence(estimate(smiles, threads, pyscf, results))
    except ValueError as e:
        others = [sentence(estimate(smiles, threads, v, results)) for v in fitted_versions(threads, results) if v != pyscf]
        said = "".join(f"; another version's time, not this run's: {s}" for s in others)
        return f"no time estimate: {e}{said}"


def sentence(e: dict) -> str:
    """The estimate as one line; past the demo's half hour it opens with a warning (the run is not refused)."""
    minutes = e["seconds"] / 60
    warning = "" if e["within_half_hour"] else f"WARNING: the estimate passes the demo's half hour ({HALF_HOUR_S / 60:.0f} min) — "
    return (f"{warning}estimated laptop time ≈ {minutes:.0f} min for {e['basis_functions']} basis functions on pyscf {e['pyscf']} "
            f"({'within' if e['within_half_hour'] else 'beyond'} half an hour, whose line lies at ≈ {e['half_hour_functions']}); "
            f"fit seconds ∝ n^{e['exponent']} over {e['runs']} laptop runs on pyscf {e['pyscf']} of sizes {e['sizes']}")
