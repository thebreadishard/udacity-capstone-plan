"""Rebuild-and-diff for REPRODUCE.md (weekend plan lever 3, 25 September 2026).

Reads the tables of REPRODUCE.md: every row names a command (first back-quoted span of the command column) and the files it writes (back-quoted
spans of the last column, `{a,b}` brace groups expanded, `*` globs allowed).

    python tools/rebuild_check.py                 # audit: does every output file exist, is it tracked by git, is the working copy clean?
    python tools/rebuild_check.py --run E11.4     # run the rows whose first column contains the text, then diff the outputs against HEAD
    python tools/rebuild_check.py --run all       # every desk row (machine rows, marked "hel1-" / "CCX53" / "(machine" in the command, are skipped)

A row passes the diff when every JSON number agrees with HEAD to 1 % or 1e-6 absolute and every other file is byte-identical. Nothing is
committed; the diff is printed for the human. Runs use the interpreter that runs this script, in the directory the row's command states
("(in `<dir>`)") or, by default, the plan directory."""
from __future__ import annotations

import argparse
import glob
import itertools
import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
PLAN = Path(__file__).resolve().parents[1]
_VENV = PLAN.parents[1] / ".venv" / "Scripts" / "python.exe"
PYTHON = str(_VENV) if _VENV.exists() else sys.executable  # the repository .venv (3.13) carries torch/rdkit for the module rows
DOC = PLAN / "REPRODUCE.md"
MACHINE = ("hel1-", "CCX53", "/root/", "chain", ".sh` (")


def brace_expand(s: str) -> list[str]:
    m = re.search(r"\{([^{}]*)\}", s)
    if not m:
        return [s]
    return list(itertools.chain.from_iterable(brace_expand(s[:m.start()] + alt + s[m.end():]) for alt in m.group(1).split(",")))


SECTION_DIRS = {"(module 05)": "modules/05_support_predictor", "Modules 06 and 07": None}
ROW_DIRS = {"module 06": "modules/06_generative_candidates", "module 07": "modules/07_agentic_workflows"}


def rows():
    section_dir = PLAN
    for line in DOC.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            hit = [d for k, d in SECTION_DIRS.items() if k in line]
            section_dir = PLAN / hit[0] if hit and hit[0] else PLAN
        if not line.startswith("|") or set(line.replace("|", "").strip()) <= {"-", " "}:
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) != 3 or cells[0] in ("number", "check"):
            continue
        name, cmd_cell, out_cell = cells
        cmds = re.findall(r"`([^`]+)`", cmd_cell)
        cwd = section_dir
        for k, d in ROW_DIRS.items():
            if name.lower().startswith(k):
                cwd = PLAN / d
        m = re.search(r"\(in `([^`]+)`\)", cmd_cell)
        if m:
            cwd = PLAN / m.group(1)
        machine = any(tag in cmd_cell or tag in name for tag in MACHINE)
        outs = [o for span in re.findall(r"`([^`]+)`", out_cell) for o in brace_expand(span) if "/" in o and not o.startswith("/root")]
        yield name, cmds, cwd, outs, machine


def tracked() -> set[str]:
    out = subprocess.run(["git", "ls-files"], cwd=PLAN, capture_output=True, text=True, check=True).stdout
    return set(out.split("\n"))


def dirty() -> set[str]:
    out = subprocess.run(["git", "status", "--porcelain", "."], cwd=PLAN, capture_output=True, text=True, check=True).stdout
    return {line[3:].strip() for line in out.splitlines()}


def audit() -> int:
    trk, drt = tracked(), dirty()
    problems = 0
    for name, _cmds, cwd, outs, machine in rows():
        if not outs:
            continue
        for pat in outs:
            hits = glob.glob(str(cwd / pat)) if "*" in pat else ([str(cwd / pat)] if (cwd / pat).exists() else [])
            if not hits:
                if machine:
                    print(f"remote    {pat:70s} <- {name[:60]} (machine row; fetched by hand)")
                    continue
                print(f"MISSING   {pat:70s} <- {name[:60]}")
                problems += 1
                continue
            for h in hits:
                rel = Path(h).resolve().relative_to(PLAN).as_posix()
                if rel not in trk:
                    print(f"UNTRACKED {rel:70s} <- {name[:60]}")
                    problems += 1
                elif rel in drt:
                    print(f"MODIFIED  {rel:70s} <- {name[:60]}")
                    problems += 1
    print(f"audit: {problems} problem(s) over {sum(1 for r in rows() if r[3])} rows with outputs")
    return 1 if problems else 0


VOLATILE_KEYS = {"date", "seconds", "wall_s", "elapsed_s", "time"}  # a rebuild legitimately changes these
STAMP = re.compile(r"20\d\d-\d\d-\d\d[ T]\d\d:\d\d")


def numbers_close(a, b, rel=0.01, abs_=1e-6) -> bool:
    if isinstance(a, bool) or isinstance(b, bool):
        return a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(a - b) <= max(abs_, rel * max(abs(a), abs(b)))
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(numbers_close(a[k], b[k]) for k in a if k not in VOLATILE_KEYS)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(numbers_close(x, y) for x, y in zip(a, b, strict=True))
    return a == b


def diff_against_head(rel: str) -> str:
    head = subprocess.run(["git", "show", f"HEAD:./{rel}"], cwd=PLAN, capture_output=True)
    if head.returncode:
        return "not in HEAD"
    old_text = head.stdout.decode("utf-8").replace("\r\n", "\n")  # bytes, not text=True: the console code page is not UTF-8 and autocrlf adds \r
    new = (PLAN / rel).read_text(encoding="utf-8").replace("\r\n", "\n")
    if rel.endswith(".json"):
        try:
            return "same numbers (1 %, time stamps ignored)" if numbers_close(json.loads(new), json.loads(old_text)) else "NUMBERS DIFFER"
        except json.JSONDecodeError as e:
            return f"json error: {e}"
    return "identical (time stamps ignored)" if STAMP.sub("<stamp>", new) == STAMP.sub("<stamp>", old_text) else f"TEXT DIFFERS (git diff -- {rel})"


def restore(rel: str) -> None:
    """Put the committed file back so an equivalent rebuild leaves no noise in the working copy."""
    subprocess.run(["git", "checkout", "--", rel], cwd=PLAN, check=False)


def run(select: str, keep: bool = False) -> int:
    failures = 0
    env = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}  # the module scripts print ≤ and → ; the console code page is cp1252
    for name, cmds, cwd, outs, machine in rows():
        if select != "all" and select not in name:
            continue
        if not cmds or machine:
            print(f"skip (machine run): {name[:70]}")
            continue
        for c in cmds:
            print(f"$ ({cwd.relative_to(PLAN) if cwd != PLAN else '.'}) {c}")
            c = re.sub(r"^python ", lambda _m: f'"{PYTHON}" ', c)
            r = subprocess.run(c, cwd=cwd, shell=True, env=env)
            if r.returncode:
                print(f"  exit {r.returncode}")
                failures += 1
        for pat in outs:
            for h in glob.glob(str(cwd / pat)) or [str(cwd / pat)]:
                rel = Path(h).resolve().relative_to(PLAN).as_posix()
                verdict = diff_against_head(rel) if Path(h).exists() else "MISSING after run"
                print(f"  {rel}: {verdict}")
                failures += verdict.split()[0] in ("NUMBERS", "TEXT", "MISSING")
                if not keep and verdict.split()[0] in ("same", "identical"):
                    restore(rel)
    print(f"run: {failures} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--run", metavar="SELECT", help="run the rows whose first column contains SELECT ('all' = every desk row) and diff against HEAD")
    ap.add_argument("--keep", action="store_true", help="leave rebuilt files in place (default: equivalent rebuilds are restored from HEAD)")
    a = ap.parse_args()
    sys.exit(run(a.run, a.keep) if a.run else audit())
