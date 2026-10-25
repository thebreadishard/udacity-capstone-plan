"""A psi4_worker job for a smoke molecule (25 Oct 2026, TASKS 49): lever 5's job (`probes/large_pah_jobs.py`: the corpus deck's
optimisation without FD Hessians) for a geometry.json (symbols, coords_bohr), so a deploy's smoke runs the batch runner's psi4 step and
leaves the analytic-only result.json that chain 42's wait reads. The job's id is the folder's name, which the batch runner's ids file uses.
out_dir is written as given and must be absolute: a job for a server is built on the laptop too (bootstrap_psi4_ccx53.sh).

    python probes/smoke_job.py <geometry.json> <out_dir> [--deck …/deck_v1.json] [--job-file <path>]   → <out_dir>/job.json or <path>
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "modules", "05_support_predictor", "corpus"))
from large_pah_jobs import DECK, job  # noqa: E402
from saddle_restarts import BOHR  # noqa: E402

SMOKE_THREADS = 2
SMOKE_MEMORY_GB = 2


def smoke_job(geometry: dict, out_dir: str, deck: dict) -> dict:
    """lever 5's job for this geometry, written to out_dir and named after it."""
    sp = {"skeleton": "smoke", "uid": 0, "formula": "smoke", "symbols": geometry["symbols"],
          "xyz": [[c * BOHR for c in xyz] for xyz in geometry["coords_bohr"]]}
    smoke_deck = dict(deck, threads=SMOKE_THREADS, memory_gb=SMOKE_MEMORY_GB)
    return job(sp, "S", os.path.dirname(out_dir), smoke_deck) | {"id": os.path.basename(out_dir), "out_dir": out_dir}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("geometry")
    ap.add_argument("out_dir")
    ap.add_argument("--deck", default=DECK)
    ap.add_argument("--job-file", help="where the job goes (default <out_dir>/job.json)")
    a = ap.parse_args()
    if not (a.out_dir.startswith("/") or os.path.isabs(a.out_dir)):
        raise SystemExit(f"out_dir must be absolute (psi4_worker writes there from any working folder): {a.out_dir}")
    with open(a.geometry, encoding="utf-8") as fh:
        geometry = json.load(fh)
    with open(a.deck, encoding="utf-8") as fh:
        deck = json.load(fh)
    target = a.job_file or os.path.join(a.out_dir, "job.json")
    os.makedirs(os.path.dirname(os.path.abspath(target)), exist_ok=True)
    with open(target + ".tmp", "w", encoding="utf-8") as fh:
        json.dump(smoke_job(geometry, a.out_dir, deck), fh, indent=1)
    os.replace(target + ".tmp", target)


if __name__ == "__main__":
    main()
