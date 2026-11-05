"""Quality audit of the task board beyond `tasks_board.py check`: what a rule check cannot refuse but a reader trips over.

    python tools/tasks_audit.py [--today 2026-11-05]    # one line per finding; exit 1 when there is any

Four findings, each pointing at text to rewrite, never edited here:
- a date that has passed in a desk row's *Waits for:* or *Next:*, or in the last cell of a table row (the 'next check' or 'by' column);
- a pointer `TASKS N` (or `TASKS N, M and K`) in a *Waits for:*, a *Next:* or a table row to a row that is closed; elsewhere in a row it
  is provenance and stays;
- a desk row longer than LONG_ROW characters: the board says where things stand, the history belongs in the ledger and git;
- a [User] desk row that the 'Waiting on the user' table does not name.
Dates are read as 'D Mon' or 'D–D Mon' (the range's last day); September–December are 2026, January–August 2027, the plan's calendar. A
date followed by a time ('1 Nov 15:5x') is the moment something happened, not a deadline, and is not read.
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from collections.abc import Iterator

from tasks_board import ARCHIVE, BOARD, NEXT_MARK, ROW_TAGS, WAIT_MARK, archived_numbers, desk_rows

LONG_ROW = 2500
MONTHS = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6, "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}
DATE = re.compile(r"\b(?:\d{1,2}[–-])?(\d{1,2}) (" + "|".join(MONTHS) + r")\b(?! \d{2}:\d[0-9x])")
POINTER = re.compile(r"\bTASKS (\d+(?:(?:, | and )\d+)*)\b")
WAITING_HEADING = "## Waiting on the user"


def plan_date(day: int, month: str) -> dt.date:
    m = MONTHS[month]
    return dt.date(2026 if m >= 9 else 2027, m, day)


def pointed(text: str) -> set[int]:
    """Every row number a `TASKS …` pointer names, lists included."""
    return {int(n) for m in POINTER.finditer(text) for n in re.findall(r"\d+", m.group(1))}


def passed(text: str, today: dt.date) -> list[str]:
    """The dates in the text that lie before today, as written."""
    return [m.group(0) for m in DATE.finditer(text) if plan_date(int(m.group(1)), m.group(2)) < today]


def forward_parts(row_text: str) -> Iterator[tuple[str, str]]:
    """(mark, text) of a row's *Waits for:* and *Next:* clauses; a clause ends at the next mark or at the row's file column (' | ')."""
    for mark in (WAIT_MARK, NEXT_MARK):
        if mark in row_text:
            rest = row_text.split(mark, 1)[1]
            for end in (WAIT_MARK, NEXT_MARK, " | "):
                rest = rest.split(end, 1)[0]
            yield mark, rest


def table_rows(board: str) -> Iterator[tuple[str, str]]:
    """(section heading, row line) of every table body row outside the desk queue."""
    heading = ""
    for line in board.split("\n"):
        if line.startswith("## "):
            heading = line
        elif line.startswith("| ") and not line.startswith("|---") and heading and not heading.startswith("## Desk"):
            yield heading, line


def date_findings(board: str, today: dt.date) -> list[str]:
    out = []
    for r in desk_rows(board):
        for mark, text in forward_parts(r.text):
            out += [f"row {r.number}: {mark} names {d}, which has passed" for d in passed(text, today)]
    headers = set(_header_lines(board))
    for heading, line in table_rows(board):
        if line in headers:
            continue
        last = line.rstrip().rstrip("|").rsplit("|", 1)[-1]
        out += [f"{heading[3:]}: '{_label(line)}' names {d} in its last column, which has passed" for d in passed(last, today)]
    return out


def _header_lines(board: str) -> list[str]:
    """A table's header is the line just above its |---| separator."""
    lines = board.split("\n")
    return [lines[i - 1] for i, ln in enumerate(lines) if ln.startswith("|---") and i > 0]


def _label(line: str) -> str:
    first = line.strip("| ").split("|", 1)[0].replace("**", "").strip()
    return first[:70]


def pointer_findings(board: str, archive: str) -> list[str]:
    open_rows = {r.number for r in desk_rows(board)}
    closed = set(archived_numbers(archive)) - open_rows
    out = []
    for r in desk_rows(board):
        for mark, text in forward_parts(r.text):
            out += [f"row {r.number}: {mark} points to TASKS {n}, which is closed" for n in sorted(pointed(text) & closed)]
    for heading, line in table_rows(board):
        out += [f"{heading[3:]}: '{_label(line)}' points to TASKS {n}, which is closed" for n in sorted(pointed(line) & closed)]
    return out


def length_findings(board: str) -> list[str]:
    return [f"row {r.number} is {len(r.text):,} characters (over {LONG_ROW:,}): history belongs in the ledger"
            for r in desk_rows(board) if len(r.text) > LONG_ROW]


def waiting_findings(board: str) -> list[str]:
    waiting = " ".join(line for heading, line in table_rows(board) if heading == WAITING_HEADING)
    named = pointed(waiting)
    out = []
    for r in desk_rows(board):
        tags = ROW_TAGS.match(r.text)
        if tags and tags.group(3) == "User" and r.number not in named:
            out.append(f"row {r.number} waits for the user but '{WAITING_HEADING[3:]}' does not name it")
    return out


def audit(board: str, archive: str, today: dt.date) -> list[str]:
    return [*date_findings(board, today), *pointer_findings(board, archive), *length_findings(board), *waiting_findings(board)]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--today", type=dt.date.fromisoformat, default=dt.date.today())
    a = ap.parse_args(argv)
    found = audit(BOARD.read_text(encoding="utf-8"), ARCHIVE.read_text(encoding="utf-8"), a.today)
    for f in found:
        print(f"AUDIT: {f}")
    print(f"AUDIT: {len(found)} finding(s) on {a.today}")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
