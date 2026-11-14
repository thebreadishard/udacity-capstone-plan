"""Did the log keep everything the smoke wrote (TASKS 214)?

    python probes/log_append_check.py <log> [--lines 2000]

Counts the three writers' lines, checks that each run of numbers is complete and in order, and refuses a file whose first line is not
the start marker - the damage of 14 November was exactly that: the marker, then the lines written last, then the file continuing
mid-word where the overwrite stopped. Exit 0 when the log is whole, 1 with the first thing missing otherwise.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

START = "=== (LAS) start:"
DONE = "=== (LAS) done"
PATTERNS = {"win-after": re.compile(r"^win-after (\d+):"), "wsl": re.compile(r"^wsl (\d+):")}
SHELL_AFTER = 3   # the lines the shell writes after the child, where the two offsets part company


def numbers(lines: list[str], kind: str) -> list[int]:
    pattern = PATTERNS[kind]
    return [int(m.group(1)) for line in lines if (m := pattern.match(line))]


def problems(log: Path, expected_wsl: int) -> list[str]:
    lines = log.read_text(encoding="utf-8", errors="replace").splitlines()
    out = []
    if not lines or not lines[0].startswith(START):
        out.append(f"the first line is not the start marker but {lines[0][:60]!r}" if lines else "the log is empty")
    if not any(line.startswith(DONE) for line in lines):
        out.append("the done marker is missing")
    for kind, expected in (("wsl", expected_wsl), ("win-after", SHELL_AFTER)):
        got = numbers(lines, kind)
        if got != list(range(1, expected + 1)):
            missing = sorted(set(range(1, expected + 1)) - set(got))
            out.append(f"{kind}: {len(got)} of {expected} lines, first missing {missing[0] if missing else 'none'} "
                       f"(out of order or duplicated otherwise)")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("log", type=Path)
    ap.add_argument("--lines", type=int, default=2000, help="how many lines the WSL child wrote (the smoke's N)")
    a = ap.parse_args(argv)
    found = problems(a.log, a.lines)
    print(f"{a.log}: " + ("whole" if not found else "; ".join(found)))
    return 0 if not found else 1


if __name__ == "__main__":
    sys.exit(main())
