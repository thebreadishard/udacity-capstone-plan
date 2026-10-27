"""The task board's two files: `TASKS.md` holds open work only, `TASKS_closed.md` the desk-queue rows that left it, verbatim, each with one
line saying when and why (the user, 27 Oct 2026: closed rows to an archive, and a check in the hooks; the board had grown to 396 KB because
closed rows were struck through instead of moved).

    python tools/tasks_board.py check                                   # exit 1 with every reason when a rule is broken
    python tools/tasks_board.py archive <reasons.json> --stamp "$(python tools/stamp.py --date)"
                                                                        # reasons.json: {"<number>": "<why it closed, with the pointer>"}

Rules of `check`: a row number appears once on the board and once in the archive, never in both; no board row is closed by its own words
(a struck title, or the phrase that promises removal at the next tidy). It prints the next free number for a new row.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import patch_file as pf

PLAN = Path(__file__).resolve().parents[1]
BOARD = PLAN / "TASKS.md"
ARCHIVE = PLAN / "TASKS_closed.md"
DESK_HEADING = "## Desk"
ARCHIVE_END = "<!-- tasks_board.py archive: new entries go above this line -->"
ROW_START = re.compile(r"^(\d+)\. ")
STAMP = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\dx$")
CLOSED_WORDS = ("Row removed at the next tidy", "Row closes with the next TASKS pass")


@dataclass(frozen=True)
class Row:
    number: int
    text: str              # the numbered line through the row's last non-blank line, newlines included


def desk_rows(text: str) -> list[Row]:
    """The desk queue's rows in file order: a row is its numbered line and the lines after it, up to the next numbered line or heading."""
    rows: list[Row] = []
    current: list[str] | None = None
    number, inside = 0, False

    def close() -> None:
        if current is not None:
            rows.append(Row(number, "\n".join(current).rstrip("\n")))

    for line in text.split("\n"):
        if line.startswith("## "):
            close()
            current, inside = None, line.startswith(DESK_HEADING)
            continue
        m = ROW_START.match(line)
        if m and inside:
            close()
            number, current = int(m.group(1)), [line]
        elif current is not None:
            current.append(line)
    close()
    return rows


def archived_numbers(text: str) -> list[int]:
    return [int(m.group(1)) for line in text.split("\n") if (m := ROW_START.match(line))]


def problems(board: str, archive: str) -> list[str]:
    """Every broken rule, one sentence each; empty when the board is sound."""
    rows = desk_rows(board)
    on_board = [r.number for r in rows]
    in_archive = archived_numbers(archive)
    out = [f"row {n} appears {on_board.count(n)} times on the board" for n in sorted(set(on_board)) if on_board.count(n) > 1]
    out += [f"row {n} appears {in_archive.count(n)} times in the archive" for n in sorted(set(in_archive)) if in_archive.count(n) > 1]
    out += [f"row {n} is both on the board and in the archive" for n in sorted(set(on_board) & set(in_archive))]
    for r in rows:
        body = ROW_START.sub("", r.text, count=1)
        if body.startswith("~~"):
            out.append(f"row {r.number} has a struck title: closed rows move to {ARCHIVE.name} (tools/tasks_board.py archive)")
        out += [f"row {r.number} says '{w}': archive it" for w in CLOSED_WORDS if w in r.text]
    return out


def next_number(board: str, archive: str) -> int:
    return max([0, *(r.number for r in desk_rows(board)), *archived_numbers(archive)]) + 1


def archive_plan(board: str, reasons: dict[int, str], stamp: str) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    """The edits that move the named rows: (board edits, archive edits). Refuses an unknown number, an empty reason or a bad stamp."""
    if not STAMP.match(stamp):
        raise SystemExit(f"stamp {stamp!r} is not tools/stamp.py --date's form (YYYY-MM-DD HH:Mx)")
    rows = {r.number: r for r in desk_rows(board)}
    unknown = sorted(set(reasons) - set(rows))
    if unknown:
        raise SystemExit(f"not on the board: {unknown}")
    empty = sorted(n for n, why in reasons.items() if not why.strip())
    if empty:
        raise SystemExit(f"no reason given for {empty}")
    entries = "".join(f"{rows[n].text}\n   → archived {stamp}: {reasons[n].strip()}\n\n" for n in sorted(reasons))
    board_edits = [(rows[n].text + "\n", "") for n in sorted(reasons)]
    return board_edits, [(ARCHIVE_END, f"## Archived {stamp}\n\n{entries}{ARCHIVE_END}")]


def archive(reasons_file: Path, stamp: str) -> int:
    reasons = {int(k): v for k, v in json.loads(reasons_file.read_text(encoding="utf-8")).items()}
    board_edits, archive_edits = archive_plan(BOARD.read_text(encoding="utf-8"), reasons, stamp)
    # the archive is written first: a failure between the two writes leaves a row in both files, which check reports, never in neither
    pf.patch_many({str(ARCHIVE): archive_edits, str(BOARD): board_edits})
    left = problems(BOARD.read_text(encoding="utf-8"), ARCHIVE.read_text(encoding="utf-8"))
    print(f"archived {len(reasons)} rows; board check: {'clean' if not left else '; '.join(left)}")
    return 1 if left else 0


def check() -> int:
    board, archive_text = BOARD.read_text(encoding="utf-8"), ARCHIVE.read_text(encoding="utf-8")
    found = problems(board, archive_text)
    for p in found:
        print(f"TASKS: {p}")
    print(f"TASKS: {len(desk_rows(board))} open desk rows, {len(archived_numbers(archive_text))} archived; next free number "
          f"{next_number(board, archive_text)}" + ("" if not found else f"; {len(found)} problem(s)"))
    return 1 if found else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check")
    a = sub.add_parser("archive")
    a.add_argument("reasons", type=Path)
    a.add_argument("--stamp", required=True, help="python tools/stamp.py --date")
    args = ap.parse_args(argv)
    return check() if args.cmd == "check" else archive(args.reasons, args.stamp)


if __name__ == "__main__":
    sys.exit(main())
