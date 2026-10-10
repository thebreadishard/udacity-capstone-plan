"""One runner for the chains that until 10 Oct 2026 each got their own dated shell script (TASKS 41; a review the user showed: ≈ 1,200 lines of shell
against ≈ 1,270 of Python in four days, and three of five review points were bugs in such scripts). A run is data: a JSON spec in probes/runs/.

    python probes/chain_runner.py probes/runs/<name>.json [--dry-run]

Spec (paths relative to the plan folder unless absolute):
  name        short marker tag, e.g. "C40" — every marker line starts with "=== (C40) " (the watch's job table matches that)
  wait        list of conditions, all must hold, checked every `poll_s` (default 600) seconds:
                {"kind": "marker", "log": …, "regex": …}                 a line of a log matches
                {"kind": "results", "list": …, "first": N, "dir": …}     the first N ids of a list each have dir/<id>/result.json
  steps       run in order; the run stops at the first failing step:
                {"kind": "cmd", "argv": [...], "cwd": …, "log": …}       any command (stdin is /dev/null, always; "{python}" = the runner's python)
                {"kind": "rungc", …}                                      the standard rung C chain, expanded by `rungc_steps`
  outputs     files that must exist at the end (TASKS 43: declared outputs); a missing one fails the run
A standard rung C step: design check → every training (chain 34's recipe v1.1 plus each training's own arguments, models saved) → ONE
`model_registry --add-candidates` call for all checkpoints of the run (9 Oct: registering per training stopped the rebuild on the next training's
unregistered models) → `rungC_eval_saved` per checkpoint on the frozen hold-out (b) → `rungC_eval_means` per training. Its keys: "chain", "note",
"date", "trainings": [{"prefix": …, "args": [...]}], optional "seeds" (default 0,1,2), "threads" (8), "holdout_b_file", "recipe" (override).
Markers: "armed", "waiting", "<step> done", "run done"; failures: "RUN FAILED at <step>: …". Exit 0 done, 1 failed.
"""
from __future__ import annotations

import argparse
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
    raise ValueError(f"unknown wait kind {c['kind']!r}")


def rungc_steps(s: dict, python: str) -> list[dict]:
    """The standard rung C chain as plain command steps (cwd = module 05). Checkpoint names follow rungC_train's `<prefix>_model_n<N>_seed<s>.pt`;
    N is found after training, so the registry and eval steps carry a glob that `run_step` resolves."""
    seeds = s.get("seeds", [0, 1, 2]); threads = str(s.get("threads", 8)); recipe = s.get("recipe", RECIPE_V11)
    hb = s.get("holdout_b_file", HOLDOUT_B); date = s.get("date", datetime.now().strftime("%Y-%m-%d"))
    seed_arg = ",".join(str(x) for x in seeds)
    out = [dict(label="design check", argv=[python, "m05/design_check.py", "corpus/molecules", "--aggregation", "sum", "--out",
                                             f"out/design_check_{s['chain']}_{date}"], log=f"out/design_check_{s['chain']}_{date}.log")]
    for t in s["trainings"]:
        pre = t["prefix"]
        out.append(dict(label=f"train {Path(pre).name}", log=f"{pre}.log",
                        argv=[python, "m05/rungC_train.py", "corpus/molecules", pre, *BASE, "--seeds", seed_arg, "--threads", threads, *recipe,
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
                                  "--allow-any-model", "--holdout-b-file", hb]))
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


def run_step(st: dict, env: dict) -> None:
    cwd = _p(st.get("cwd", PLAN))
    argv = _resolve(st["argv"], cwd) if st.get("glob_args") else st["argv"]
    log = Path(st["log"])                                              # absolute: expand() resolves every log
    log.parent.mkdir(parents=True, exist_ok=True)
    with open(log, "a", encoding="utf-8") as fh:
        r = subprocess.run(argv, cwd=cwd, stdin=subprocess.DEVNULL, stdout=fh, stderr=subprocess.STDOUT, env=env, check=False)
    if r.returncode != 0:
        raise RuntimeError(f"exit {r.returncode} (log {log})")


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
    for st in steps:
        try:
            run_step(st, env)
        except (RuntimeError, OSError) as e:
            marker(name, f"RUN FAILED at {st['label']}: {e}")
            return 1
        print(f"({name}) {st['label']} done {stamp()}", flush=True)
    missing = [o for o in spec.get("outputs", []) if not _p(o).exists()]
    if missing:
        marker(name, f"RUN FAILED: declared outputs missing: {', '.join(missing)}")
        return 1
    marker(name, f"run done — {len(steps)} steps, {len(spec.get('outputs', []))} declared outputs present")
    return 0


if __name__ == "__main__":
    sys.exit(main())
