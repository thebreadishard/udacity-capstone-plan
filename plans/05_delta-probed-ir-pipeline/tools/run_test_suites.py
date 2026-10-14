"""Every test suite of the repository, each with the interpreter it needs, as one regular local check (11 Oct 2026).

Why: CI runs only `plans/05_delta-probed-ir-pipeline/tests` without pyscf (pyproject `testpaths = ["tests"]`), so the module suites (06, 07, 08),
the website export's tests and the pyscf tests that only run in WSL were checked by hand or not at all; module 08's scenario test once failed
unnoticed for days. This script runs them all, writes the result to `probes/watch_state/test_suites.json` (git-ignored) and prints one line per
suite. `probes/state.sh` shows the last result (`--summary`); the nightly scheduled task runs it after the data backup (`tools/backup_task.cmd`).

Cost ≈ 4 min on the laptop. It must not slow a running job: Windows suites run at idle priority with two threads, the WSL suite at nice 19
with one thread.

    python tools/run_test_suites.py             # run every suite; exit 1 when one fails
    python tools/run_test_suites.py --summary   # print the last result (for state.sh); no tests run
"""
import argparse
import datetime
import glob
import json
import os
import re
import shlex
import subprocess
import sys
import time

PLAN = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
ROOT = os.path.abspath(os.path.join(PLAN, "..", ".."))
STATE = os.path.join(PLAN, "probes", "watch_state", "test_suites.json")
SYSTEM_PY = r"C:\Users\thebr\AppData\Local\Programs\Python\Python314\python.exe"   # torch, rdkit (memory 'Python interpreters on the laptop')
VENV_PY = os.path.join(ROOT, ".venv", "Scripts", "python.exe")                     # LangGraph, no torch: module 07
WSL_PY = "~/qc05/bin/python"                                                        # pyscf
STALE_HOURS = 48
TIMEOUT_S = 1800

# name, interpreter, working directory (relative to the repository root), pytest arguments
SUITES = [
    ("plan 05", SYSTEM_PY, "plans/05_delta-probed-ir-pipeline", ["tests"]),
    ("module 06", SYSTEM_PY, "plans/05_delta-probed-ir-pipeline/modules/06_generative_candidates", ["m06/tests"]),
    ("module 07", VENV_PY, "plans/05_delta-probed-ir-pipeline/modules/07_agentic_workflows", ["tests"]),
    ("module 08", SYSTEM_PY, "plans/05_delta-probed-ir-pipeline/modules/08_industry_synthesis", ["tests"]),
    ("website export", SYSTEM_PY, "website/export", ["tests"]),
]


def pyscf_tests(plan=PLAN):
    """The plan's test files that skip without pyscf: they run only in WSL (relative paths, sorted)."""
    pat = re.compile(r"importorskip\(\s*[\"']pyscf[\"']\s*\)")
    return sorted(os.path.relpath(p, plan).replace(os.sep, "/") for p in glob.glob(os.path.join(plan, "tests", "*.py"))
                  if pat.search(open(p, encoding="utf-8").read()))


def counts(text):
    """pytest's closing counts ('3 failed, 327 passed, 7 skipped in 118s') as a dict; {} when the line is missing."""
    out = {}
    for n, word in re.findall(r"(\d+) (passed|failed|errors?|skipped|deselected|xfailed|xpassed)", text):
        out["error" if word.startswith("error") else word] = out.get("error" if word.startswith("error") else word, 0) + int(n)
    return out


def failures(text):
    """pytest's short-summary lines for failed and erroring tests (its default -r fE), at most 20, each cut to 300 characters."""
    return [ln[:300] for ln in text.splitlines() if ln.startswith(("FAILED ", "ERROR "))][:20]


def verdict(rc, c):
    """'pass' only for exit 0 with at least one test passed; pytest exit 5 (nothing collected) is a failure of the check itself."""
    return "pass" if rc == 0 and c.get("passed", 0) > 0 and not c.get("failed") and not c.get("error") else "FAIL"


def run(cmd, cwd, env, windows_idle):
    t0 = time.time()
    flags = getattr(subprocess, "IDLE_PRIORITY_CLASS", 0) if windows_idle else 0
    try:
        p = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=TIMEOUT_S,
                           creationflags=flags, check=False)
        rc, text = p.returncode, p.stdout + p.stderr
    except subprocess.TimeoutExpired:
        rc, text = -1, f"timeout after {TIMEOUT_S} s"
    except OSError as e:
        rc, text = -1, f"could not start: {e}"
    return rc, text, round(time.time() - t0)


def run_all():
    env = dict(os.environ, PYTHONUTF8="1", OMP_NUM_THREADS="2", MKL_NUM_THREADS="2")
    pytest = ["-m", "pytest", "-q", "-p", "no:cacheprovider", "-m", "not slow"]
    rows = []
    for name, py, rel, args in SUITES:
        rc, text, s = run([py, *pytest, *args], os.path.join(ROOT, rel), env, windows_idle=True)
        rows.append(dict(suite=name, rc=rc, seconds=s, counts=counts(text), tail=text.strip().splitlines()[-1:] or [""], failures=failures(text)))
    wsl_plan = "/mnt/" + PLAN[0].lower() + PLAN[2:].replace("\\", "/")
    args = " ".join(shlex.quote(x) for x in [*pytest, *pyscf_tests()])               # bash -lc reads one string: quote every word
    cmd = f"cd {shlex.quote(wsl_plan)} && OMP_NUM_THREADS=1 nice -n 19 {WSL_PY} {args}"
    rc, text, s = run(["wsl.exe", "-e", "bash", "-lc", cmd], ROOT, env, windows_idle=False)
    rows.append(dict(suite="plan 05 pyscf (WSL)", rc=rc, seconds=s, counts=counts(text), tail=text.strip().splitlines()[-1:] or [""],
                     failures=failures(text)))
    for r in rows:
        r["verdict"] = verdict(r["rc"], r["counts"])
    return rows


def summary(state, now=None):
    """One line for state.sh from the saved result."""
    if not state:
        return "  test suites: never run — python tools/run_test_suites.py"
    now = now or datetime.datetime.now()
    age = (now - datetime.datetime.fromisoformat(state["finished"])).total_seconds() / 3600
    failed = [r["suite"] for r in state["suites"] if r["verdict"] != "pass"]
    passed = sum(r["counts"].get("passed", 0) for r in state["suites"])
    line = (f"  test suites (last run {state['finished'][:16].replace('T', ' ')}, {age:.0f} h ago): "
            f"{len(state['suites']) - len(failed)}/{len(state['suites'])} pass, {passed} tests")
    if failed:
        line += " — FAILED: " + ", ".join(failed)
    if age > STALE_HOURS:
        line += f" — STALE (> {STALE_HOURS} h): check the scheduled task CapstoneDataBackup"
    return line


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--summary", action="store_true", help="print the last result for state.sh; run nothing")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")                                    # Git Bash reads UTF-8; Windows Python writes cp1252
    if a.summary:
        print(summary(json.load(open(STATE, encoding="utf-8")) if os.path.exists(STATE) else None))
        return 0
    started = datetime.datetime.now().isoformat(timespec="seconds")
    rows = run_all()
    state = dict(started=started, finished=datetime.datetime.now().isoformat(timespec="seconds"), suites=rows)
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    tmp = STATE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=1)
    os.replace(tmp, STATE)
    for r in rows:
        print(f"{r['suite']}: {r['verdict']} {r['counts']} ({r['seconds']} s){'' if r['verdict'] == 'pass' else ' — ' + r['tail'][0]}", flush=True)
        for ln in r.get("failures", []):
            print(f"    {ln}", flush=True)
    return 0 if all(r["verdict"] == "pass" for r in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
