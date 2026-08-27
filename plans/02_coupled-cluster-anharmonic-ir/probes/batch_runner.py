"""Unattended batch runner: the machine works while nobody is watching.

The laptop is idle roughly 168 hours a week and human attention is roughly 8. That
asymmetry is recorded in GoalGathering/Compute_Budget_2026-08-27.md, and this is the
tool that spends the large budget without drawing on the small one.

It exists because a run launched from an interactive terminal died when that terminal
was cleaned up, taking an hour of phenanthrene with it. Rule 7 of the compute budget
says nothing waits for a human; a process that dies when a human closes a window is
the same failure wearing a different hat.

WHAT IT GUARANTEES

  1. Each job writes its result the moment it finishes.
  2. A job is skipped only when its COMPLETE artefact set exists, never on a partial.
  3. A failing job is recorded as a failure and the queue continues.
  4. Expensive intermediates are stored, so re-analysis never re-computes.
  5. Every start, finish and failure appends a timestamped line to run.log.
  6. STATUS.md is regenerated after every job: one glance, no log reading.
  7. Nothing ever waits for input.

USAGE

  Queue is jobs.json, next to this file, and is meant to be edited by hand.
  Launch detached so it survives the shell that started it:

      pwsh> Start-Process -WindowStyle Hidden -FilePath "$env:USERPROFILE\\.conda\\envs\\qc\\python.exe" `
              -ArgumentList "batch_runner.py" -WorkingDirectory (Get-Location)

  Then close everything. Read STATUS.md whenever you next sit down.
"""

from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
JOBS = HERE / "jobs.json"
OUT = HERE / "batch_results"
LOG = OUT / "run.log"
STATUS = OUT / "STATUS.md"
HEARTBEAT = OUT / "heartbeat.json"


# ------------------------------------------------------------------- bookkeeping

def now():
    return datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S")


def log(message):
    OUT.mkdir(exist_ok=True)
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(f"{now()}  {message}\n")


def beat(state, job_id=None, started=None):
    HEARTBEAT.write_text(json.dumps({
        "written": now(),
        "pid": os.getpid(),
        "state": state,
        "current_job": job_id,
        "current_started": started,
    }, indent=2), encoding="utf-8")


def artefacts(job):
    """Every file a job must produce to count as finished."""
    base = OUT / job["id"]
    names = [base.with_suffix(".json")]
    if job["kind"] == "freq":
        names.append(base.with_suffix(".npz"))
    return names


def is_done(job):
    return all(p.exists() for p in artefacts(job))


# ------------------------------------------------------------------- the jobs

def job_freq(params):
    """B3LYP frequency job: geometry, Hessian, IR intensities."""
    import importlib.util

    import psi4

    spec = importlib.util.spec_from_file_location(
        "dft", HERE / "dft_locality_2026-08-26.py")
    dft = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(dft)

    # Importing the module does not configure psi4; only its main() did, and the
    # runner never calls that. Without this every job dies on "Unable to find a
    # basis set", which is a two-second failure that looks exactly like a real one.
    psi4.set_output_file(str(OUT / f"{params['name']}_freq.log"), False)
    psi4.set_memory(f"{params.get('memory_gb', 12)} GB")
    psi4.set_num_threads(params.get("threads", 8))
    psi4.set_options({"scf_type": "df", "basis": dft.BASIS,
                      "g_convergence": "gau", "geom_maxiter": 200})

    data, arrays = dft.run_molecule(
        params["name"], params["smiles"],
        tuple(params["formula"]), params.get("bays", 0))
    return data, arrays


def job_cc_timing(params):
    """Time a coupled-cluster single point. The missing number in the whole plan.

    A failure here is a measurement: "this does not fit in this machine" is exactly
    what gate G1a needs to know, and it is recorded rather than retried.
    """
    import psi4

    psi4.set_output_file(str(OUT / f"{params['name']}_cc.log"), False)
    psi4.set_memory(f"{params.get('memory_gb', 24)} GB")
    psi4.set_num_threads(params.get("threads", 8))
    psi4.set_options({"freeze_core": True, "scf_type": "df", "cc_type": "df"})

    mol = psi4.geometry(params["geometry"] + "\nsymmetry c1\nno_reorient\nno_com\n")
    n_bf = psi4.core.BasisSet.build(mol, "BASIS", params["basis"]).nbf()

    started = time.perf_counter()
    energy = psi4.energy(params["method"] + "/" + params["basis"], molecule=mol)
    seconds = time.perf_counter() - started
    psi4.core.clean()

    return dict(
        name=params["name"], method=params["method"], basis=params["basis"],
        n_atoms=mol.natom(), n_basis_functions=int(n_bf),
        energy_hartree=float(energy), seconds=seconds,
        threads=params.get("threads", 8), memory_gb=params.get("memory_gb", 24),
    ), None


KINDS = {"freq": job_freq, "cc_timing": job_cc_timing}


# ------------------------------------------------------------------- the status

def write_status(jobs):
    lines = [
        "# Batch status",
        "",
        f"Regenerated {now()} by `batch_runner.py` (pid {os.getpid()}).",
        f"Machine: {platform.node()}, {os.cpu_count()} logical cores.",
        "",
        "| # | job | kind | state | wall time | result |",
        "|---|---|---|---|---|---|",
    ]
    done = failed = 0
    for i, job in enumerate(jobs, 1):
        path = OUT / f"{job['id']}.json"
        state, wall, summary = "queued", "", ""
        if path.exists():
            payload = json.loads(path.read_text(encoding="utf-8"))
            if payload.get("_failed"):
                state, failed = "FAILED", failed + 1
                summary = payload.get("_error", "")[:70]
            else:
                state, done = "done", done + 1
                secs = payload.get("seconds") or payload.get("seconds_hessian", 0)
                wall = f"{secs/60:.1f} min" if secs else ""
                if "strongest_oop_cm" in payload:
                    summary = f"band {payload['strongest_oop_cm']:.1f} cm-1"
                elif "n_basis_functions" in payload:
                    summary = f"{payload['n_basis_functions']} basis fn"
        lines.append(f"| {i} | `{job['id']}` | {job['kind']} | {state} | {wall} | {summary} |")

    lines[3:3] = [f"**{done} done, {failed} failed, {len(jobs)-done-failed} queued.**", ""]
    lines += [
        "",
        "`heartbeat.json` carries the pid and the job in flight. If its timestamp is",
        "stale and the pid is gone, the runner died and can simply be started again:",
        "finished jobs are skipped, so nothing is repeated.",
        "",
    ]
    STATUS.write_text("\n".join(lines), encoding="utf-8")


# -------------------------------------------------------------------------- main

def run_single(job_id):
    """Execute exactly one job and exit. Invoked as a subprocess by the queue.

    Isolation is the whole point. Psi4 keeps global state - timers, scratch,
    options - and a job that dies mid-calculation leaves it inconsistent: the
    first attempt at this queue produced a spurious 'Timer FNOCC: CC energy is
    already on' failure in the job AFTER a genuine out-of-memory one. Chasing
    that overnight would have cost a night and produced a fictitious result.
    """
    jobs = json.loads(JOBS.read_text(encoding="utf-8"))
    job = next(j for j in jobs if j["id"] == job_id)

    data, arrays = KINDS[job["kind"]](job["params"])
    (OUT / f"{job_id}.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
    if arrays is not None:
        np.savez_compressed(OUT / f"{job_id}.npz", **arrays)


def main():
    OUT.mkdir(exist_ok=True)
    log(f"runner starting, pid {os.getpid()}")
    beat("starting")

    attempted = set()
    while True:
        # Re-read every pass, so jobs can be appended to the queue while it runs.
        # A runner you have to restart to extend is a runner that waits for a human.
        jobs = json.loads(JOBS.read_text(encoding="utf-8"))
        write_status(jobs)

        pending = [j for j in jobs if not is_done(j) and j["id"] not in attempted]
        if not pending:
            break
        job = pending[0]
        attempted.add(job["id"])

        started = now()
        beat("running", job["id"], started)
        log(f"start    {job['id']} ({job['kind']})")
        t0 = time.perf_counter()

        proc = subprocess.run(
            [sys.executable, str(Path(__file__).name), "--job", job["id"]],
            cwd=str(HERE), capture_output=True, text=True)
        elapsed = time.perf_counter() - t0

        if proc.returncode == 0 and is_done(job):
            log(f"finish   {job['id']} in {elapsed/60:.1f} min")
        else:
            for stale in artefacts(job):
                stale.unlink(missing_ok=True)
            tail = (proc.stderr or proc.stdout or "").strip().splitlines()
            reason = next((ln.strip() for ln in reversed(tail) if ln.strip()), "no output")
            (OUT / f"{job['id']}.json").write_text(json.dumps({
                "_failed": True,
                "_error": reason[:400],
                "_returncode": proc.returncode,
                "_stderr_tail": "\n".join(tail[-40:]),
                "seconds": elapsed,
                "started": started,
            }, indent=2), encoding="utf-8")
            log(f"FAILED   {job['id']} after {elapsed/60:.1f} min: {reason[:160]}")

    beat("idle")
    log("queue empty, runner exiting")
    write_status(json.loads(JOBS.read_text(encoding="utf-8")))


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--job":
        run_single(sys.argv[2])
    else:
        main()
