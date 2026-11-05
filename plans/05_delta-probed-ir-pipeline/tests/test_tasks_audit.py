"""tools/tasks_audit.py on a synthetic board: each of the four findings fires on its case and stays quiet on the sound one."""
import datetime as dt
import sys
from pathlib import Path

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "tools"))
import tasks_audit as TA  # noqa: E402

TODAY = dt.date(2026, 11, 5)
BOARD = """# Open tasks

## Running (machines)

| run | what | where | next check |
|---|---|---|---|
| **run a** | waits for TASKS 3 | laptop | ≈ 4 Nov |
| **run b** | fine | laptop | ≈ 9 Nov |

## Waiting on the user

| decision | why | what I bring | by |
|---|---|---|---|
| **choice x** (TASKS 2, 5 and 6) | matters | a plan | before 30 Nov |

## Desk work queue

### PROOF

1. **[PROOF][Accuracy][Event] Row one (1 Oct).** From 1 Oct; TASKS 3. *Waits for:* the run (≈ 3–4 Nov). *Next:* read it ≈ 9 Nov (asked 2 Nov 10:1x). | `x` |
2. **[PROOF][Accuracy][User] Row two.** *Waits for:* the user's word. *Next:* build it after TASKS 3. | `y` |
4. **[OPS][Operations][User] Row four.** *Waits for:* the user. *Next:* ask on 2 Jan. | `z` |
5. **[OPS][Operations][User] Row five.** *Waits for:* the user. *Next:* ask. | `w` |
"""
ARCHIVE = "3. **[OPS][Operations][Now] Closed row.**\n   → archived 2026-11-01 08:0x: done\n"


def test_plan_dates_cross_the_new_year():
    assert TA.plan_date(4, "Nov") == dt.date(2026, 11, 4)
    assert TA.plan_date(2, "Jan") == dt.date(2027, 1, 2)


def test_a_range_counts_by_its_last_day():
    assert TA.passed("≈ 3–4 Nov", TODAY) == ["3–4 Nov"]
    assert TA.passed("≈ 4–6 Nov", TODAY) == []


def test_passed_dates_in_forward_clauses_and_last_columns_only():
    found = TA.date_findings(BOARD, TODAY)
    assert "row 1: *Waits for:* names 3–4 Nov, which has passed" in found
    assert "Running (machines): 'run a' names 4 Nov in its last column, which has passed" in found
    assert not any("1 Oct" in f for f in found)          # the title's and the history's dates are not forward-looking
    assert not any("2 Nov" in f for f in found)          # a stamped date is a moment, not a deadline
    assert not any("run b" in f or "row 4" in f for f in found)


def test_pointers_to_closed_rows():
    found = TA.pointer_findings(BOARD, ARCHIVE)
    assert found == ["row 2: *Next:* points to TASKS 3, which is closed",          # row 1's pointer is provenance, outside its clauses
                     "Running (machines): 'run a' points to TASKS 3, which is closed"]


def test_pointer_lists_name_every_number():
    assert TA.pointed("TASKS 74, 49, 171 and 183; TASKS 2") == {2, 49, 74, 171, 183}


def test_long_rows(monkeypatch):
    row1 = next(r for r in TA.desk_rows(BOARD) if r.number == 1)
    monkeypatch.setattr(TA, "LONG_ROW", len(row1.text) - 1)    # row 1 is the longest: only it crosses the line
    assert TA.length_findings(BOARD) == [f"row 1 is {len(row1.text)} characters (over {len(row1.text) - 1}): history belongs in the ledger"]


def test_user_rows_missing_from_the_waiting_table():
    assert TA.waiting_findings(BOARD) == ["row 4 waits for the user but 'Waiting on the user' does not name it"]


def test_main_exits_1_on_findings(monkeypatch, tmp_path, capsys):
    (tmp_path / "TASKS.md").write_text(BOARD, encoding="utf-8")
    (tmp_path / "TASKS_closed.md").write_text(ARCHIVE, encoding="utf-8")
    monkeypatch.setattr(TA, "BOARD", tmp_path / "TASKS.md")
    monkeypatch.setattr(TA, "ARCHIVE", tmp_path / "TASKS_closed.md")
    assert TA.main(["--today", "2026-11-05"]) == 1
    assert "finding(s) on 2026-11-05" in capsys.readouterr().out
