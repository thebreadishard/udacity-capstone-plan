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

### PROOF

1. ~~Done thing~~ **DONE 08:1x.** *Next:* none.
2. **[PROOF][Accuracy][Now] Open thing** wrapped
over two lines. *Next:* tomorrow.

### PRODUCT

3. **[PRODUCT][Pipeline][Now] Another open thing.** Row removed at the next tidy. *Next:* x.
4. **[OPS][Operations][Event] Last.** *Waits for:* a run. *Next:* y.

## Guards on this file

Rule text.
"""
ARCHIVE = f"# closed\n\n{TB.ARCHIVE_END}\n"


def test_rows_are_the_desk_queue_only_and_keep_their_wrapped_lines():
    rows = TB.desk_rows(BOARD)
    assert [r.number for r in rows] == [1, 2, 3, 4]
    # the blank line and the heading after a row are not the row's
    assert rows[1].text == "2. **[PROOF][Accuracy][Now] Open thing** wrapped\nover two lines. *Next:* tomorrow."
    assert rows[3].text == "4. **[OPS][Operations][Event] Last.** *Waits for:* a run. *Next:* y."


def test_the_check_names_struck_and_self_closed_rows_and_the_next_number():
    found = TB.problems(BOARD, ARCHIVE)
    assert any("row 1 has a struck title" in p for p in found)
    assert any("row 3 says 'Row removed at the next tidy'" in p for p in found)
    assert not any("row 2" in p or "row 4" in p for p in found)
    assert any("row 1 opens without its class" in p for p in found)


def test_an_open_row_needs_its_class_and_its_next_check():
    board = BOARD.replace("4. **[OPS][Operations][Event] Last.** *Waits for:* a run. *Next:* y.", "4. **Last.** Soon.")
    found = TB.problems(board, ARCHIVE)
    assert any("row 4 opens without its class" in p for p in found) and any("row 4 names no next check" in p for p in found)
    assert any("opens without its class" in p for p in TB.problems(BOARD.replace("[OPS]", "[MISC]"), ARCHIVE))
    assert any("row 4 opens without its class, topic and state" in p for p in TB.problems(BOARD.replace("[Operations]", ""), ARCHIVE))
    assert any("row 4 opens without" in p for p in TB.problems(BOARD.replace("[Event]", "[Later]"), ARCHIVE))
    assert any("row 4 opens without" in p for p in TB.problems(BOARD.replace("[Operations]", "[Misc]"), ARCHIVE))
    assert TB.next_number(BOARD, "7. archived\n") == 8 and TB.next_number(BOARD, ARCHIVE) == 5


def test_a_number_in_both_files_or_twice_is_refused():
    assert any("row 4 is both" in p for p in TB.problems(BOARD, "4. old\n"))
    assert any("appears 2 times in the archive" in p for p in TB.problems(BOARD, "9. a\n9. b\n"))
    twice = BOARD.replace("4. **[OPS][Operations][Event] Last.**", "2. **[OPS][Operations][Event] Last.**")
    assert any("appears 2 times on the board" in p for p in TB.problems(twice, ARCHIVE))


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
    assert "1. ~~Done thing~~ **DONE 08:1x.** *Next:* none.\n   → archived 2026-10-27 18:3x: done, ledger 1 Oct\n" in new_arch
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


def test_view_lists_the_open_rows_by_state_and_by_topic():
    board = BOARD.replace("1. ~~Done thing~~ **DONE 08:1x.** *Next:* none.\n", "")
    by_topic = TB.grouped(board, "topic")
    assert by_topic["Accuracy"] == ["2 [PROOF][Now] Open thing — tomorrow."]
    assert by_topic["Operations"] == ["4 [OPS][Event] Last. — a run."]
    assert list(by_topic) == list(TB.TOPICS) and by_topic["Udacity"] == []
    by_state = TB.grouped(board, "state")
    assert [n.split()[0] for n in by_state["Now"]] == ["2", "3"] and by_state["User"] == []
    with pytest.raises(SystemExit, match="row 1 opens without"):
        TB.grouped(BOARD, "state")


def test_a_waiting_row_names_what_it_waits_for_and_a_now_row_does_not():
    found = TB.problems(BOARD.replace(" *Waits for:* a run.", ""), ARCHIVE)
    assert any(p.startswith("row 4: a Now row names nothing") for p in found)
    found = TB.problems(BOARD.replace("over two lines. *Next:*", "over two lines. *Waits for:* x. *Next:*"), ARCHIVE)
    assert any(p.startswith("row 2: a Now row names nothing") for p in found)
    assert not any("a Now row" in p for p in TB.problems(BOARD, ARCHIVE))
