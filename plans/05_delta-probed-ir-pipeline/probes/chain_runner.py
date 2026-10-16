"""One runner for the chains that until 10 Oct 2026 each got their own dated shell script (TASKS 41; a review the user showed: ≈ 1,200 lines of shell
against ≈ 1,270 of Python in four days, and three of five review points were bugs in such scripts). A run is data: a JSON spec in probes/runs/.

    python probes/chain_runner.py probes/runs/<name>.json [--dry-run]

Spec (paths relative to the plan folder unless absolute):
  name        short marker tag, e.g. "C40" — every marker line starts with "=== (C40) " (the watch's job table matches that)
  wait        list of conditions, all must hold, checked every `poll_s` (default 600) seconds:
                {"kind": "marker", "log": …, "regex": …}                 a line of a log matches
                {"kind": "results", "list": …, "first": N, "dir": …}     the first N ids of a list each have dir/<id>/result.json
                {"kind": "cmd", "argv": [...], "cwd": …}                a command exits 0 (e.g. a check on a server; 120 s timeout)
  steps       run in order; the run stops at the first failing step:
                {"kind": "cmd", "argv": [...], "cwd": …, "log": …}       any command (stdin is /dev/null, always; "{python}" = the runner's python)
                {"kind": "rungc", …}                                      the standard rung C chain, expanded by `rungc_steps` (needs "date")
  outputs     files that must exist at the end (TASKS 43: declared outputs); a missing one fails the run
A standard rung C step: design check → every training (chain 34's recipe v1.1 plus each training's own arguments, models saved) → ONE
`model_registry --add-candidates` call for all checkpoints of the run (9 Oct: registering per training stopped the rebuild on the next training's
unregistered models) → `rungC_eval_saved` per checkpoint on the frozen hold-out (b) → `rungC_eval_means` per training. Its keys: "chain", "note",
"date", "trainings": [{"prefix": …, "args": [...], "labels": "analytic" (default) | "fd"}], optional "seeds" (default 0,1,2),
"threads" (8), "holdout_b_file", "recipe" (override), "eval_args" (extra arguments for every rungC_eval_saved call, e.g. chain 42's
`--eval-ids-file T=…`); a training's own "eval_args" replaces the spec's for that training's evaluations (chain 41: each control fold
reads its own test list, 13 Oct 2026). A training with "labels": "fd" trains without `--use-analytic` (chain 35's half read
compares the two on one pool, 11 Oct 2026); evaluation always uses the analytic labels, the one yardstick.
Markers: "armed", "waiting", "starting", "<step> done", "run done"; failures: "RUN FAILED at <step>: …". Exit 0 done, 1 failed.
While a step runs, "progress: <step> (i/N) running M min, its log +B bytes" every PROGRESS_S seconds in which the step's log grew (15 Oct 2026,
TASKS 63: the progress contract of tools/runspec.py; a step whose log stands still prints nothing, so the contract's gap catches a hang).
Resume (13 Oct 2026): every finished step is recorded in probes/watch_state/chains/<name>.json with a hash of the expanded steps; a relaunch
(after an app or Windows restart, tools/resume_laptop_jobs.sh) skips the recorded steps while the hash matches, and starts afresh, with a
marker saying so, when the spec changed. --fresh ignores and removes the record.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

PLAN = Path(__file__).resolve().parents[1]
M05 = PLAN / "modules" / "05_support_predictor"
RECIPE_V11 = ["--head", "hybrid", "--aux", "both", "--kring-weight", "0.3", "--kdiag-weight", "0.1", "--kdiag-mode", "family", "--sqm-scale",
              "--pair-features", "--aux-weight", "1.0", "--epochs", "200", "--patience", "20", "--lr", "3e-4", "--hybrid-hidden", "256", "--pattern", "f"]
BASE = ["--use-analytic", "--pool-layers", "A,A2,B", "--inner-val", "0.15", "--aggregation", "sum"]
HOLDOUT_B = "corpus/holdout_b_frozen_2026-10-08.txt"
STATE_DIR = PLAN / "probes" / "watch_state" / "chains"                 # resume records; tests point it at a temporary folder
PROGRESS_S = 600                                                       # seconds between progress checks of a running step; tests lower it


def _p(path: str | Path) -> Path:
    p = Path(path)
    return p if p.is_absolute() else PLAN / p


def stamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def marker(name: str, text: str) -> None:
    print(f"=== ({name}) {text} {stamp()}", flush=True)


def condition_holds(c: dict) -> bool:
    if c["kind"] == "marker":
        log = _p(c["log"])
        return log.exists() and re.search(c["regex"], log.read_text(encoding="utf-8", errors="replace"), re.M) is not None
    if c["kind"] == "results":
        ids = [s.strip() for s in _p(c["list"]).read_text(encoding="utf-8").split() if s.strip()][: int(c["first"])]
        return len(ids) == int(c["first"]) and all((_p(c["dir"]) / i / "result.json").exists() for i in ids)
    if c["kind"] == "cmd":
        try:
            r = subprocess.run(c["argv"], cwd=_p(c.get("cwd", PLAN)), stdin=subprocess.DEVNULL, capture_output=True, timeout=120, check=False)
        except (OSError, subprocess.TimeoutExpired):
            return False
        return r.returncode == 0
    raise ValueError(f"unknown wait kind {c['kind']!r}")


def rungc_steps(s: dict, python: str) -> list[dict]:
    """The standard rung C chain as plain command steps (cwd = module 05). Checkpoint names follow rungC_train's `<prefix>_model_n<N>_seed<s>.pt`;
    N is found after training, so the registry and eval steps carry a glob that `run_step` resolves."""
    seeds = s.get("seeds", [0, 1, 2]); threads = str(s.get("threads", 8)); recipe = s.get("recipe", RECIPE_V11)
    hb = s.get("holdout_b_file", HOLDOUT_B); date = s.get("date")
    if not date:   # 16 Oct 2026: a date taken from the clock named the logs by the day, so a relaunch on another day changed the resume hash
        raise ValueError(f"rungc step of chain {s.get('chain')}: no 'date' — a fixed date keeps the resume record valid across days")
    seed_arg = ",".join(str(x) for x in seeds)
    out = [dict(label="design check", argv=[python, "m05/design_check.py", "corpus/molecules", "--aggregation", "sum", "--out",
                                             f"out/design_check_{s['chain']}_{date}"], log=f"out/design_check_{s['chain']}_{date}.log")]
    for t in s["trainings"]:
        pre = t["prefix"]
        labels = t.get("labels", "analytic")
        if labels not in ("analytic", "fd"):
            raise ValueError(f"training {pre}: labels must be 'analytic' or 'fd', not {labels!r}")
        base = BASE if labels == "analytic" else [a for a in BASE if a != "--use-analytic"]
        out.append(dict(label=f"train {Path(pre).name}", log=f"{pre}.log",
                        argv=[python, "m05/rungC_train.py", "corpus/molecules", pre, *base, "--seeds", seed_arg, "--threads", threads, *recipe,
                              *t.get("args", []), "--save-model"]))
    ckpts = [f"{t['prefix']}_model_n*_seed{x}.pt" for t in s["trainings"] for x in seeds]
    out.append(dict(label="register candidates", log=f"out/registry_{s['chain']}_{date}.log", glob_args=True,
                    argv=[python, "m05/model_registry.py", "--add-candidates", *ckpts, "--chain", str(s["chain"]), "--note", s["note"]]))
    for t in s["trainings"]:
        pre = t["prefix"]
        evals = []
        for x in seeds:
            ev = f"{pre}_eval_frozenb_seed{x}"
            evals.append(f"{ev}.json")
            out.append(dict(label=f"eval {Path(pre).name} seed {x}", log=f"{ev}.log", glob_args=True,
                            argv=[python, "../../probes/rungC_eval_saved.py", f"{pre}_model_n*_seed{x}.pt", ev, "--use-analytic", "--threads", threads,
                                  "--allow-any-model", "--holdout-b-file", hb, *t.get("eval_args", s.get("eval_args", []))]))
        read = f"out/read_{Path(pre).name}"
        out.append(dict(label=f"seed means {Path(pre).name}", log=f"{read}.log",
                        argv=[python, "../../probes/rungC_eval_means.py", read, *evals, "--against", f"{pre}.json"]))
    for st in out:
        st["cwd"] = str(M05); st["log"] = str(M05 / st["log"])
    return out


def _resolve(argv: list[str], cwd: Path) -> list[str]:
    out = []
    for a in argv:
        if "*" in a:
            hits = sorted(cwd.glob(a))
            if len(hits) != 1:
                raise RuntimeError(f"{a!r} matches {len(hits)} files, expected 1")
            out.append(str(hits[0].relative_to(cwd)).replace("\\", "/"))
        else:
            out.append(a)
    return out


def run_step(st: dict, env: dict, name: str | None = None, position: str = "") -> None:
    """Run one step with its output appended to its log; with a name, a progress marker for every PROGRESS_S in which that log grew."""
    cwd = _p(st.get("cwd", PLAN))
    argv = _resolve(st["argv"], cwd) if st.get("glob_args") else st["argv"]
    log = Path(st["log"])                                              # absolute: expand() resolves every log
    log.parent.mkdir(parents=True, exist_ok=True)
    with open(log, "a", encoding="utf-8") as fh:
        proc = subprocess.Popen(argv, cwd=cwd, stdin=subprocess.DEVNULL, stdout=fh, stderr=subprocess.STDOUT, env=env)
        size, t0 = log.stat().st_size, time.time()
        while True:
            try:
                rc = proc.wait(timeout=PROGRESS_S)
                break
            except subprocess.TimeoutExpired:
                grown = log.stat().st_size - size
                if name and grown > 0:
                    size += grown
                    marker(name, f"progress: {st['label']} ({position}) running {(time.time() - t0) / 60:.0f} min, its log +{grown} bytes")
    if rc != 0:
        raise RuntimeError(f"exit {rc} (log {log})")


def steps_hash(steps: list[dict]) -> str:
    """What a record of finished steps is valid for: the labels, commands and folders of the expanded steps."""
    return hashlib.sha256(json.dumps([[st["label"], st["argv"], str(st["cwd"])] for st in steps]).encode()).hexdigest()[:16]


def load_done(name: str, h: str) -> tuple[set, bool]:
    """(labels finished in an earlier run of these very steps, whether a record for other steps was set aside)."""
    p = STATE_DIR / f"{name}.json"
    if not p.exists():
        return set(), False
    rec = json.load(open(p, encoding="utf-8"))
    return (set(rec["done"]), False) if rec.get("hash") == h else (set(), True)


def save_done(name: str, h: str, done: set) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    tmp = STATE_DIR / f"{name}.json.tmp"
    tmp.write_text(json.dumps({"hash": h, "done": sorted(done), "updated": stamp()}, indent=1), encoding="utf-8")
    os.replace(tmp, STATE_DIR / f"{name}.json")


def expand(spec: dict, python: str) -> list[dict]:
    steps = []
    for st in spec.get("steps", []):
        if st["kind"] == "rungc":
            steps += rungc_steps(st, python)
        elif st["kind"] == "cmd":
            argv = [python if a == "{python}" else a for a in st["argv"]]
            steps.append(dict(label=st.get("label", " ".join(argv)[:60]), argv=argv, cwd=str(_p(st.get("cwd", PLAN))),
                              log=str(_p(st["log"]))))
        else:
            raise ValueError(f"unknown step kind {st['kind']!r}")
    return steps


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("spec")
    ap.add_argument("--dry-run", action="store_true", help="print the expanded steps and the wait conditions' state; run nothing")
    ap.add_argument("--python", default=sys.executable)
    ap.add_argument("--fresh", action="store_true", help="ignore and remove the record of finished steps (13 Oct 2026: the default resumes)")
    a = ap.parse_args(argv)
    spec = json.load(open(_p(a.spec), encoding="utf-8"))
    name = spec["name"]
    steps = expand(spec, a.python)
    if a.dry_run:
        for c in spec.get("wait", []):
            print(f"wait {c['kind']}: {'holds' if condition_holds(c) else 'not yet'}")
        for st in steps:
            print(f"{st['label']}: (cwd {Path(st['cwd']).name}) {' '.join(st['argv'])}")
        print("outputs:", ", ".join(spec.get("outputs", [])) or "—")
        return 0
    env = dict(os.environ, PYTHONUTF8="1", PYTHONUNBUFFERED="1")
    marker(name, f"armed (pid {os.getpid()}), {len(steps)} steps")
    waits = spec.get("wait", [])
    if waits and not all(condition_holds(c) for c in waits):
        marker(name, "waiting")
        while not all(condition_holds(c) for c in waits):
            time.sleep(float(spec.get("poll_s", 600)))
    marker(name, f"starting: {len(steps)} steps")                     # the line a run spec's start_regex waits for (TASKS 63)
    h = steps_hash(steps)
    if a.fresh:
        (STATE_DIR / f"{name}.json").unlink(missing_ok=True)
    done, stale = load_done(name, h)
    if stale:
        marker(name, "resume record is for other steps (the spec changed) — starting from the first step")
    elif done:
        marker(name, f"resuming: {len(done)} of {len(steps)} steps finished in an earlier run are skipped")
    for n, st in enumerate(steps, 1):
        if st["label"] in done:
            print(f"({name}) {st['label']} skipped: done in an earlier run {stamp()}", flush=True)
            continue
        try:
            run_step(st, env, name, f"{n}/{len(steps)}")
        except (RuntimeError, OSError) as e:
            marker(name, f"RUN FAILED at {st['label']}: {e}")
            return 1
        done.add(st["label"])
        save_done(name, h, done)
        print(f"({name}) {st['label']} done {stamp()}", flush=True)
    missing = [o for o in spec.get("outputs", []) if not _p(o).exists()]
    if missing:
        marker(name, f"RUN FAILED: declared outputs missing: {', '.join(missing)}")
        return 1
    marker(name, f"run done — {len(steps)} steps, {len(spec.get('outputs', []))} declared outputs present")
    return 0


def utf8_stdout(stream: io.TextIOWrapper) -> None:
    """The chain log is the runner's redirected stdout, which Windows opens in the locale's code page: a marker's '—' became byte 0x97
    and grep read chain40.log as a binary file (17 Oct 2026)."""
    stream.reconfigure(encoding="utf-8")


if __name__ == "__main__":
    utf8_stdout(sys.stdout)
    sys.exit(main())
