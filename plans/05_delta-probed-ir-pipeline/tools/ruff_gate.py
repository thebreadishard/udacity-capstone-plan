"""The one ruff check of plan 05 (CLAUDE.md 'Python code', the user 27 Oct 2026): pyproject.toml's ruff set on the lines a change writes, and on
the whole function around such a line for the rules that judge a function. A new file is all written lines, so it is checked whole.

    python tools/ruff_gate.py --staged                 pre-commit: the staged changes
    python tools/ruff_gate.py --range BASE..HEAD       CI: the commits pushed
    python tools/ruff_gate.py FILE[:START-END] ...     by hand (a file without a span is checked whole)

The edit hook (tools/hooks/guard.py) calls findings() with the span the edit wrote. Exit 1 with the findings listed when there are any.
Lines nobody touched are not judged here: the old code's findings are TASKS 139, cleaned where no run depends on the file.
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
from pathlib import Path

PLAN = Path(__file__).resolve().parents[1]
REPO = PLAN.parents[1]
CONFIG = PLAN / "pyproject.toml"
# reported at the def line, about the whole function: a change anywhere in the function makes it the change's finding
FUNCTION_RULES = frozenset({"C901", "PLR0911", "PLR0912", "PLR0913", "PLR0915", "PLR0917"})
HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")


def parse_diff(text: str, root: Path, within: Path) -> dict[Path, set[int]]:
    """The added or changed line numbers per file of a `git diff -U0` text, for the files under `within`."""
    lines: dict[Path, set[int]] = {}
    current: Path | None = None
    for line in text.splitlines():
        if line.startswith("+++ "):
            name = line[4:].strip()
            path = None if name == "/dev/null" else (root / name.removeprefix("b/")).resolve()
            current = path if path is not None and within.resolve() in path.parents else None
            if current is not None:
                lines.setdefault(current, set())
        elif current is not None and (m := HUNK.match(line)):
            start = int(m.group(1))
            count = 1 if m.group(2) is None else int(m.group(2))
            lines[current].update(range(start, start + count))
    return lines


def changed_lines(diff_args: list[str]) -> dict[Path, set[int]]:
    """parse_diff of `git diff -U0 <diff_args>` over the plan's .py files (added or modified)."""
    out = subprocess.run(["git", "diff", "-U0", "--no-color", "--no-ext-diff", "--diff-filter=AM", *diff_args, "--", "*.py"],
                         cwd=REPO, capture_output=True, text=True, encoding="utf-8", check=True).stdout
    return parse_diff(out, REPO, PLAN)


def function_spans(path: Path) -> dict[int, range]:
    """Every function's lines, keyed by its def line."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, ValueError):
        return {}
    return {n.lineno: range(n.lineno, n.end_lineno + 1) for n in ast.walk(tree) if isinstance(n, ast.FunctionDef | ast.AsyncFunctionDef)}


def _ruff(files: list[Path]) -> list[dict]:
    r = subprocess.run([sys.executable, "-m", "ruff", "check", "--config", str(CONFIG), "--force-exclude", "--no-fix", "--output-format", "json",
                        *map(str, files)], cwd=PLAN, capture_output=True, text=True, encoding="utf-8", check=False)
    if r.returncode not in (0, 1):
        raise RuntimeError(f"ruff did not run (exit {r.returncode}): {r.stderr.strip()[:400]}")
    return json.loads(r.stdout or "[]")


def findings(spans: dict[Path, set[int] | None]) -> list[str]:
    """Ruff's findings on the given lines of each file (None: the whole file), as 'path:row:col: CODE message'."""
    spans = {p.resolve(): lines for p, lines in spans.items() if p.suffix == ".py" and p.exists()}
    if not spans:
        return []
    kept = []
    for f in _ruff(list(spans)):
        path, row = Path(f["filename"]).resolve(), f["location"]["row"]
        code = f.get("code") or "syntax"
        lines = spans.get(path)
        if lines is not None:
            touched = {row}
            if code in FUNCTION_RULES and row in (fn := function_spans(path)):
                touched = set(fn[row])
            if not touched & lines:
                continue
        name = path.relative_to(REPO).as_posix() if REPO in path.parents else str(path)
        kept.append(f"{name}:{row}:{f['location']['column']}: {code} {f['message']}")
    return kept


def parse_span(arg: str) -> tuple[Path, set[int] | None]:
    """'file' (whole) or 'file:START-END' (inclusive)."""
    m = re.fullmatch(r"(.+?):(\d+)-(\d+)", arg)
    if m is None:
        return Path(arg), None
    return Path(m.group(1)), set(range(int(m.group(2)), int(m.group(3)) + 1))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--staged", action="store_true", help="the staged changes (pre-commit)")
    ap.add_argument("--range", metavar="BASE..HEAD", help="the changes of a commit range (CI)")
    ap.add_argument("files", nargs="*", metavar="FILE[:START-END]")
    a = ap.parse_args(argv)
    if sum((a.staged, a.range is not None, bool(a.files))) != 1:
        ap.error("give exactly one of --staged, --range BASE..HEAD or files")
    if a.staged:
        spans: dict[Path, set[int] | None] = dict(changed_lines(["--cached"]))
    elif a.range:
        spans = dict(changed_lines([a.range]))
    else:
        spans = dict(parse_span(x) for x in a.files)
    found = findings(spans)
    for line in found:
        print(line)
    if found:
        print(f"ruff_gate: {len(found)} finding(s) on changed lines - fix them or add '# noqa: <rule>  <reason>' (CLAUDE.md 'Python code')")
    return 1 if found else 0


if __name__ == "__main__":
    raise SystemExit(main())
