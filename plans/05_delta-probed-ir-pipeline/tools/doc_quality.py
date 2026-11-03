"""Mechanical quality checks on three living documents (the user, 3 Nov 2026: go through the task board, the software ledger and the
Uitleg on quality): what a script can decide, so that a reading pass is spent on what only reading finds.

    python tools/doc_quality.py tasks        # TASKS.md: file references that do not resolve, TASKS numbers that exist nowhere,
                                             # waiting rows whose named date has passed, the longest rows (history creeping in)
    python tools/doc_quality.py software     # the software ledger: register and sections agree, status words, every upstream
                                             # issue or pull request it names with its live state on GitHub (gh), file references
    python tools/doc_quality.py uitleg       # Uitleg/: links and file references that do not resolve, files the reading guide
                                             # does not list, each file's last commit date

Exit 1 when a finding needs a fix (an unresolved reference, a register/section mismatch, a pull request whose state contradicts its
status); the other lines are leads for reading.
"""
from __future__ import annotations

import argparse
import datetime as dt
import fnmatch
import functools
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

PLAN = Path(__file__).resolve().parents[1]
REPO = PLAN.parents[1]
BOARD = PLAN / "TASKS.md"
ARCHIVE = PLAN / "TASKS_closed.md"
SOFTWARE = PLAN / "GoalGathering" / "notes" / "Software_Changes_Ledger.md"
UITLEG = PLAN / "Uitleg"
GUIDE = UITLEG / "00_Leeswijzer.md"
# files git does not list but documents name: ignored build outputs (`out/...` in a module) and the nested manuscripts repository
DISK_ROOTS = (PLAN, REPO, *sorted(p for p in (PLAN / "modules").iterdir() if p.is_dir()),
              *sorted(p for p in (PLAN / "manuscripts").iterdir() if p.is_dir()))
FILE_REF = re.compile(r"`([\w./*-]+\.(?:py|md|sh|json|tsv|csv|ipynb|html|yml|yaml|toml|txt))`")
TASK_REF = re.compile(r"\bTASKS (\d+)\b")
ROW_START = re.compile(r"^(\d+)\. \*\*", re.M)
MONTHS = {"Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12, "Jan": 1, "Feb": 2, "Mar": 3}
WAITS_DATE = re.compile(r"\*Waits for:\*([^*]*?)\b(\d{1,2}) (" + "|".join(MONTHS) + r")\b")
LONG_ROW_CHARS = 2500
REGISTER_ROW = re.compile(r"^\| (\d+) \| [^|]+ \| [A-D] \| .* \| ([a-z-]+) \|$", re.M)
SECTION = re.compile(r"^### (\d+) — ", re.M)
STATUSES = ("done", "pr-open", "waiting-upstream", "pr-candidate", "planned")
SHORT_REPOS = {"pyscf": "pyscf/pyscf", "optking": "psi-rking/optking", "pyscf-forge": "pyscf/pyscf-forge", "dxtb": "grimme-lab/dxtb",
               "pyvpt2": "philipmnel/pyvpt2"}
UPSTREAM_REF = re.compile(r"(?:github\.com/([\w.-]+/[\w.-]+)/(?:pull|issues)/(\d+))|(?:\b([\w.-]+/[\w.-]+)#(\d+))|(?:\b("
                          + "|".join(map(re.escape, SHORT_REPOS)) + r")#(\d+))")
OWN_PREFIXES = ("probes/", "tools/", "modules/", "m05/", "m08/", "website/", "GoalGathering/")   # the software ledger's own files
MD_LINK = re.compile(r"\]\(([^)#\s]+)(?:#[^)]*)?\)")


@dataclass(frozen=True)
class Report:
    fixes: list[str]
    leads: list[str]


@functools.cache
def known_paths() -> tuple[str, ...]:
    """Every file git knows in the repository, tracked or untracked but not ignored, as '/'-joined paths from the repository root."""
    out = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"], capture_output=True, text=True, check=True,
                         cwd=REPO)
    return tuple("/" + p for p in out.stdout.splitlines())


def resolves(ref: str, near: Path) -> bool:
    """Whether a file reference names a file: beside the document, or as the end of a path git knows — documents write `show.py`,
    `m08/show.py` or `probes/x.py` for files deep in the tree (a glob may match)."""
    if "*" not in ref and any((root / ref).exists() for root in (near, *DISK_ROOTS)):
        return True
    tail = "/" + ref.lstrip("./")
    if "*" in ref:
        return any(fnmatch.fnmatch(p, "*" + tail) for p in known_paths())
    return any(p.endswith(tail) for p in known_paths())


def unresolved_refs(text: str, near: Path, where: str) -> list[str]:
    return [f"{where}: `{ref}` resolves nowhere" for ref in sorted(set(FILE_REF.findall(text))) if not resolves(ref, near)]


def board_rows(text: str) -> dict[int, str]:
    starts = [(int(m.group(1)), m.start()) for m in ROW_START.finditer(text)]
    ends = [s for _, s in starts[1:]] + [len(text)]
    return {n: text[s:e].split("\n\n", 1)[0] for (n, s), e in zip(starts, ends, strict=True)}


def check_tasks(today: dt.date) -> Report:
    board, archive = BOARD.read_text(encoding="utf-8"), ARCHIVE.read_text(encoding="utf-8")
    rows, closed = board_rows(board), {int(n) for n in re.findall(r"^(\d+)\. ", archive, re.M)}
    fixes = unresolved_refs(board, PLAN, "TASKS.md")
    fixes += [f"TASKS {n} is named but is neither on the board nor in the archive" for n in sorted({int(x) for x in TASK_REF.findall(board)})
              if n not in rows and n not in closed]
    leads = []
    for n, row in rows.items():
        for m in WAITS_DATE.finditer(row):
            month = MONTHS[m.group(3)]
            year = today.year + (1 if month < 6 and today.month > 6 else 0)
            when = dt.date(year, month, int(m.group(2)))
            if when < today:
                leads.append(f"row {n} waits for a date that has passed: '{m.group(0)[:90]}'")
        pointers = sorted({int(x) for x in TASK_REF.findall(row)} & closed)
        if pointers:
            leads.append(f"row {n} points at closed rows {pointers}")
    leads += [f"row {n} is {len(r):,} characters (over {LONG_ROW_CHARS:,}: history may have crept in)"
              for n, r in sorted(rows.items(), key=lambda kv: -len(kv[1])) if len(r) > LONG_ROW_CHARS]
    return Report(fixes, leads)


def gh_state(repo: str, number: int) -> str:
    """'open', 'closed' or 'merged', from GitHub's issues endpoint (a pull request is an issue there)."""
    out = subprocess.run(["gh", "api", f"repos/{repo}/issues/{number}"], capture_output=True, text=True, check=False)
    if out.returncode != 0:
        raise RuntimeError(f"gh api repos/{repo}/issues/{number}: {out.stderr.strip()[:200]}")
    issue = json.loads(out.stdout)
    if issue.get("pull_request", {}).get("merged_at"):
        return "merged"
    return issue["state"]


def upstream_refs(text: str) -> set[tuple[str, int]]:
    refs = set()
    for m in UPSTREAM_REF.finditer(text):
        if m.group(1):
            refs.add((m.group(1), int(m.group(2))))
        elif m.group(3) and "/" in m.group(3) and not m.group(3).startswith(("probes/", "tools/", "modules/")):
            refs.add((m.group(3), int(m.group(4))))
        elif m.group(5):
            refs.add((SHORT_REPOS[m.group(5)], int(m.group(6))))
    return refs


def check_software() -> Report:
    text = SOFTWARE.read_text(encoding="utf-8")
    register = {int(n): s for n, s in REGISTER_ROW.findall(text)}
    starts = [(int(m.group(1)), m.start()) for m in SECTION.finditer(text)]
    sections = {n: text[s:e] for (n, s), e in zip(starts, [s for _, s in starts[1:]] + [len(text)], strict=True)}
    fixes = [f"register line {n} has no section" for n in sorted(set(register) - set(sections))]
    fixes += [f"section {n} has no register line" for n in sorted(set(sections) - set(register))]
    fixes += [f"register line {n}: status '{s}' is not one of {STATUSES}" for n, s in register.items() if s not in STATUSES]
    fixes += [line for line in unresolved_refs(text, SOFTWARE.parent, SOFTWARE.name)
              if line.split("`")[1].startswith(OWN_PREFIXES)]
    leads = []
    states: dict[tuple[str, int], str] = {}
    for n, body in sorted(sections.items()):
        for ref in sorted(upstream_refs(body)):
            states.setdefault(ref, gh_state(*ref))
            state, status = states[ref], register.get(n, "?")
            line = f"line {n} ({status}): {ref[0]}#{ref[1]} is {state}"
            if status == "pr-open" and state != "open":
                fixes.append(line + " — the status says pr-open")
            elif status in ("waiting-upstream", "pr-candidate") and state in ("merged", "closed"):
                leads.append(line + " — does the status still hold?")
    return Report(fixes, leads)


def last_commit(path: Path) -> str:
    out = subprocess.run(["git", "log", "-1", "--format=%cs", "--", str(path)], capture_output=True, text=True, check=True, cwd=REPO)
    return out.stdout.strip()


def check_uitleg() -> Report:
    files = sorted(UITLEG.glob("*.md"))
    fixes, guide = [], GUIDE.read_text(encoding="utf-8")
    for f in files:
        text = f.read_text(encoding="utf-8")
        fixes += [f"{f.name}: link '{link}' resolves nowhere" for link in sorted(set(MD_LINK.findall(text)))
                  if not link.startswith(("http://", "https://", "mailto:")) and not (f.parent / link).exists()]
        fixes += unresolved_refs(text, f.parent, f.name)
    fixes += [f"{f.name} is not in {GUIDE.name}" for f in files if f != GUIDE and f.name not in guide and f.stem not in guide]
    leads = [f"{last_commit(f)} {f.name}" for f in files]
    return Report(fixes, leads)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("document", choices=("tasks", "software", "uitleg"))
    a = ap.parse_args(argv)
    report = {"tasks": lambda: check_tasks(dt.date.today()), "software": check_software, "uitleg": check_uitleg}[a.document]()
    for line in report.fixes:
        print("FIX ", line)
    for line in report.leads:
        print("LEAD", line)
    print(f"{len(report.fixes)} to fix, {len(report.leads)} leads")
    return 1 if report.fixes else 0


if __name__ == "__main__":
    sys.exit(main())
