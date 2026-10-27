"""The task board's check and archive (`tools/tasks_board.py`, 27 Oct 2026) on synthetic boards: row parsing across wrapped lines and
blank lines, the rules, the archive's edits and its refusals."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import tasks_board as TB

BOARD = """# Task board

## Running (machines)

| run | state |
|---|---|
| 1. not a desk row | x |

## Desk work queue (quiet hours, in order)

1. ~~Done thing~~ **DONE 08:1x.**
2. **Open thing** wrapped
over two lines. Next: tomorrow.

3. **Another open thing.** Row removed at the next tidy.
4. **Last.**

## Guards on this file

Rule text.
"""
ARCHIVE = f"# closed\n\n{TB.ARCHIVE_END}\n"


def test_rows_are_the_desk_queue_only_and_keep_their_wrapped_lines():
    rows = TB.desk_rows(BOARD)
    assert [r.number for r in rows] == [1, 2, 3, 4]
    assert rows[1].text == "2. **Open thing** wrapped\nover two lines. Next: tomorrow."      # the blank line after it is not the row's
    assert rows[3].text == "4. **Last.**"


def test_the_check_names_struck_and_self_closed_rows_and_the_next_number():
    found = TB.problems(BOARD, ARCHIVE)
    assert any("row 1 has a struck title" in p for p in found)
    assert any("row 3 says 'Row removed at the next tidy'" in p for p in found)
    assert not any("row 2" in p or "row 4" in p for p in found)
    assert TB.next_number(BOARD, "7. archived\n") == 8 and TB.next_number(BOARD, ARCHIVE) == 5


def test_a_number_in_both_files_or_twice_is_refused():
    assert any("row 4 is both" in p for p in TB.problems(BOARD, "4. old\n"))
    assert any("appears 2 times in the archive" in p for p in TB.problems(BOARD, "9. a\n9. b\n"))
    assert any("appears 2 times on the board" in p for p in TB.problems(BOARD.replace("4. **Last.**", "2. **Last.**"), ARCHIVE))


def test_archive_moves_rows_verbatim_with_the_reason(tmp_path, monkeypatch):
    board, arch = tmp_path / "TASKS.md", tmp_path / "TASKS_closed.md"
    board.write_text(BOARD, encoding="utf-8")
    arch.write_text(ARCHIVE, encoding="utf-8")
    monkeypatch.setattr(TB, "BOARD", board)
    monkeypatch.setattr(TB, "ARCHIVE", arch)
    reasons = tmp_path / "r.json"
    reasons.write_text(json.dumps({"1": "done, ledger 1 Oct", "3": "done, ledger 2 Oct"}), encoding="utf-8")
    assert TB.archive(reasons, "2026-10-27 18:3x") == 0
    new_board, new_arch = board.read_text(encoding="utf-8"), arch.read_text(encoding="utf-8")
    assert [r.number for r in TB.desk_rows(new_board)] == [2, 4]
    assert "1. ~~Done thing~~ **DONE 08:1x.**\n   → archived 2026-10-27 18:3x: done, ledger 1 Oct\n" in new_arch
    assert new_arch.index("## Archived 2026-10-27 18:3x") < new_arch.index(TB.ARCHIVE_END)
    assert TB.problems(new_board, new_arch) == []


@pytest.mark.parametrize(("reasons", "stamp", "match"), [
    ({7: "x"}, "2026-10-27 18:3x", "not on the board"),
    ({2: " "}, "2026-10-27 18:3x", "no reason"),
    ({2: "x"}, "18:3x", "stamp"),
])
def test_archive_refuses_before_writing(reasons, stamp, match):
    with pytest.raises(SystemExit, match=match):
        TB.archive_plan(BOARD, reasons, stamp)
