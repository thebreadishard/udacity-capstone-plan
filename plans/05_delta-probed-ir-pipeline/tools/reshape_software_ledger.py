"""Reshape Software_Changes_Ledger.md (3 Oct 2026, the user: 'Doe maar, via een patchscript met controle'): the four long tables become one register with
short cells (#, date, group, software, title, status) and one numbered section per row that carries every original cell verbatim. No text is dropped:
the script asserts that each original cell appears in the new document, that every row number occurs once in the register and once as a section, and
it writes through a temporary file. `--dry` prints the derived titles and statuses without writing.

Status words (fixed vocabulary): done = complete, no action required; pr-open = submitted upstream, waiting for the maintainers; waiting-upstream =
nothing to do until an upstream release, then a small action; pr-candidate = a pull request or report could be drafted, waits for the user's word;
planned = decided, not started.

    python tools/reshape_software_ledger.py [--dry]
"""
import os
import re
import sys
import tempfile

PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "GoalGathering", "notes", "Software_Changes_Ledger.md")
GROUPS = {"A": "patch to third-party code", "B": "own layer around third-party code", "C": "finding about third-party software", "D": "Lean 4 / Mathlib"}
STATUS_PHRASES = ("not changed", "adopted, not changed", "built and tested", "decided", "two upstream reports", "not sent", "submitted")
# Reviewed row by row on 3 Oct 2026 (the user: a PR we have not submitted is pr-candidate, not done). Every row needs an entry; the NOTE says why where the
# cell text and the status differ.
STATUS = {1: "done", 2: "done", 3: "pr-candidate", 4: "done", 5: "done", 6: "pr-candidate", 7: "done", 8: "pr-candidate", 9: "done", 10: "pr-candidate",
          11: "pr-candidate", 12: "pr-candidate", 13: "planned", 14: "pr-candidate", 15: "done", 16: "done", 17: "done", 18: "done", 19: "done",
          20: "waiting-upstream", 21: "pr-open", 22: "pr-open", 23: "done", 24: "done", 25: "done", 26: "pr-candidate", 27: "pr-candidate", 28: "done",
          29: "pr-candidate", 30: "pr-candidate", 31: "pr-open", 32: "pr-open"}
NOTE = {1: "the cell still says 'PR candidate: yes'; it was merged upstream as pyscf-forge #212 on 30 Sep 2026 (row 22) — nothing left to do",
        2: "the cell still says 'PR candidate: yes'; merged upstream as pyscf-forge #212 on 30 Sep 2026 (row 22) — nothing left to do",
        3: "a proposal upstream (a `chkfile` attribute on the LNO kernel) is possible and was never sent; it waits for the user's word",
        5: "no pull request intended; a paper or example later — nothing pending in this ledger",
        6: "a question to the PAHdb maintainers is still to be asked (item on the user's list)",
        9: "adopted as is; nothing to send unless our use needs a patch",
        13: "decided (decision 41) and not started; once built and passing it becomes a pr-candidate",
        20: "the fix exists upstream (pyscf #3387); our wrapper is dropped when a release carries it — the only action left, and it waits for upstream",
        22: "the state row: #212 merged, #213 (reworked 3 Oct, replied), pyscf #3469 and #3470, optking #116 open — all waiting for maintainers",
        29: "a report to pyscf-properties ('no infrared module') was not filed; the CPHF APT of row 26 is our own answer — the report waits for the user's word",
        30: "the same lookup pattern in pyscf-core's CMakeLists would be a second pull request once forge #213 is merged"}


def parse(text):
    lines = text.split("\n")
    head, rows, tail, group, headers = [], [], [], None, {}
    i = 0
    while i < len(lines):
        s = lines[i]
        m = re.match(r"^## ([ABCD])\. ", s)
        if m:
            group = m.group(1)
            i += 1
            continue
        if s.startswith("## How to use this ledger"):
            tail = lines[i:]
            break
        if group is None:
            head.append(s)
        elif s.startswith("| # |"):
            headers[group] = [c.strip() for c in s.strip("|").split("|")]
        elif re.match(r"^\| \d+ \|", s):
            cells = [c.strip() for c in s.strip().strip("|").split("|")]
            rows.append((int(cells[0]), group, cells))
        i += 1
    return head, headers, rows, tail


def title_of(change):
    """A short title from the change cell: a leading bold status phrase is skipped (or, when it holds a colon, the part after the colon is taken);
    the text is cut at the first ':', ';', '—' or sentence end; status-like lead pieces are skipped; never cut inside '(T)'."""
    m = re.match(r"^\*\*([^*]+)\*\*(.*)$", change, flags=re.S)
    if m and ":" in m.group(1):
        src = m.group(1).split(":", 1)[1] + " " + m.group(2)
    elif m:
        src = m.group(1) + " " + m.group(2)
    else:
        src = change
    src = re.sub(r"\s+", " ", re.sub(r"\*\*", "", src).replace("`", ""))
    pieces = [p.strip(" —:;.-") for p in re.split(r"[:;—]|\. ", src)]
    pieces = [p for p in pieces if p]
    t = pieces[0] if pieces else src.strip()
    for p in pieces:
        if p.lower() in STATUS_PHRASES or p.lower().startswith("decided ("):
            continue
        t = p
        break
    return (t[:88] + "…") if len(t) > 90 else t


def status_of(n, cells):
    """The reviewed status of row n (STATUS); a row without an entry stops the reshape — a new row must be reviewed, not guessed."""
    if n not in STATUS:
        raise SystemExit(f"row {n} has no reviewed status in STATUS — add it (and a NOTE if the cell text differs)")
    return STATUS[n]


def build(head, headers, rows, tail):
    rows = sorted(rows, key=lambda r: r[0])
    out = list(head)
    out += ["## Register", "",
            "One line per change; the numbered section below the register carries every original cell. Status words: **done** = complete, no action required; "
            "**pr-open** = submitted upstream, waiting for the maintainers; **waiting-upstream** = nothing to do until an upstream release, then a small action; "
            "**pr-candidate** = a pull request or report could be drafted, waits for the user's word; **planned** = decided, not started. "
            "Groups: A patch to third-party code · B own layer · C finding · D Lean 4 / Mathlib. (Reshaped 3 October 2026 by `tools/reshape_software_ledger.py`; "
            "every original cell is in the sections, verbatim.)", "",
            "| # | date | group | software | title | status |", "|---|---|---|---|---|---|"]
    sections = []
    for n, g, cells in rows:
        hdr = headers[g]
        status = status_of(n, cells)
        out.append(f"| {n} | {cells[1]} | {g} | {cells[2][:70]}{'…' if len(cells[2]) > 70 else ''} | {title_of(cells[3])} | {status} |")
        sec = [f"### {n} — {title_of(cells[3])}", "", f"**Group:** {g}, {GROUPS[g]}. **Date:** {cells[1]}. **Status:** {status}."
               + (f" *Status note (3 Oct 2026):* {NOTE[n]}." if n in NOTE else ""), "", f"**Software:** {cells[2]}", ""]
        names = list(hdr[3:])
        if len(names) != len(cells) - 3:                       # rows 10–11 of table C were written with the four-column layout of A/B
            names = ["what", "why", "files / where", "action"][: len(cells) - 3]
        assert len(names) == len(cells) - 3, f"row {n}: {len(cells)} cells"
        for name, val in zip(names, cells[3:], strict=True):
            sec += [f"**{name[0].upper() + name[1:]}:** {val}", ""]
        sections += sec
    out += ["", "## Sections", ""] + sections + tail
    return "\n".join(out).rstrip("\n") + "\n"


def main():
    dry = "--dry" in sys.argv
    text = open(PATH, encoding="utf-8").read()
    head, headers, rows, tail = parse(text)
    assert rows and tail, "unexpected layout"
    nums = [r[0] for r in rows]
    assert len(nums) == len(set(nums)), f"duplicate row numbers: {sorted(n for n in nums if nums.count(n) > 1)}"
    new = build(head, headers, rows, tail)
    # controls: every original cell survives verbatim; every number once in the register and once as a section
    for n, _g, cells in rows:
        for c in cells[1:]:
            assert c in new, f"row {n}: a cell was lost: {c[:60]}"
        assert new.count(f"\n| {n} | ") == 1, f"row {n}: register count"
        assert new.count(f"\n### {n} — ") == 1, f"row {n}: section count"
    if dry:
        for n, g, cells in sorted(rows, key=lambda r: r[0]):
            print(f"{n:3d} {g} {status_of(n, cells):16s} {title_of(cells[3])[:80]}")
        print(f"{len(rows)} rows; new document {len(new.splitlines())} lines (old {len(text.splitlines())})")
        return 0
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(PATH), suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
        f.write(new)
    os.replace(tmp, PATH)
    print(f"reshaped: {len(rows)} rows → register + sections; {len(new.splitlines())} lines")
    return 0


if __name__ == "__main__":
    sys.exit(main())
