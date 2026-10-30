"""The cation fill's manifest rows (`probes/cation_fill_manifest.py`, TASKS 121): the checks that stop a fill, the cations held until their
parent is merged, a second run that skips what is written, and the written manifest on a synthetic one — old rows unchanged, the line
ending kept, a copy beside it."""
from __future__ import annotations

import csv
import sys

import pytest

from pin_tools import PLAN

sys.path.insert(0, str(PLAN / "probes"))
import cation_fill_manifest as CF

NAPH = "c1ccc2ccccc2c1"
PARENT_ID = "A_" + CF.P3.sha(NAPH)[:10]


@pytest.fixture(autouse=True)
def merged(monkeypatch):
    """Every parent counts as merged unless a test says otherwise (the real corpus/molecules is not read)."""
    held: set[str] = set()
    monkeypatch.setattr(CF, "_merged", lambda row: row["id"] not in held)
    return held


def _parent(status: str = "done") -> dict:
    return {**{k: "" for k in CF.BM.FIELDS}, "id": PARENT_ID, "layer": "A", "name": "naphthalene", "smiles": NAPH, "n_atoms": "18",
            "status": status}


def _candidate(**over) -> dict:
    c = {"id": "P3c_" + CF.P3.sha(NAPH)[:10], "parent_id": PARENT_ID, "name": "naphthalene+", "parent_smiles": NAPH, "charge": "1",
         "multiplicity": "2", "n_atoms": "18"}
    return {**c, **over}


def test_a_checked_candidate_becomes_a_pending_cation_row():
    f = CF.fill([_candidate()], [_parent()], {PARENT_ID})
    (row,) = f.rows
    assert (row["layer"], row["status"], row["smiles"], row["n_atoms"], row["n_heavy"]) == ("P3c", "pending", NAPH, 18, 10)
    assert f"parent {PARENT_ID};" in row["note"] and "charge 1 mult 2" in row["note"]
    assert CF.RC.cation_parent(row) == PARENT_ID                  # the runner finds the parent in the note


def test_a_parent_in_a_shard_only_holds_its_cation(merged):
    merged.add(_candidate()["id"])
    f = CF.fill([_candidate()], [_parent("pending")], {PARENT_ID})
    assert (f.rows, f.held) == ([], [_candidate()["id"]])


@pytest.mark.parametrize(("parents", "computed", "over", "reason"), [
    ([], {PARENT_ID}, {}, "neither done"),
    ([_parent("pending")], set(), {}, "neither done"),
    ([_parent()], {PARENT_ID}, {"id": "P3c_0000000000"}, "parent's hash"),
    ([_parent()], {PARENT_ID}, {"n_atoms": "17"}, "by RDKit"),
    ([_parent()], {PARENT_ID}, {"parent_smiles": "c1ccccc1"}, "parent SMILES differs"),
])
def test_a_wrong_candidate_stops_the_fill(parents, computed, over, reason):
    with pytest.raises(ValueError, match=reason):
        CF.fill([_candidate(**over)], parents, computed)


def test_a_second_run_skips_the_written_row_and_refuses_a_changed_one():
    (row,) = CF.fill([_candidate()], [_parent()], {PARENT_ID}).rows
    there = {k: str(v) for k, v in row.items()}
    f = CF.fill([_candidate()], [_parent(), there], {PARENT_ID})
    assert (f.rows, f.written) == ([], [row["id"]])
    with pytest.raises(ValueError, match="other values"):
        CF.fill([_candidate()], [_parent(), {**there, "name": "other"}], {PARENT_ID})
    with pytest.raises(ValueError, match="twice"):
        CF.fill([_candidate(), _candidate()], [_parent()], {PARENT_ID})


def test_the_written_manifest_keeps_its_rows_its_line_ending_and_a_copy(tmp_path):
    path = tmp_path / "manifest.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CF.BM.FIELDS, lineterminator="\r\n")
        w.writeheader()
        w.writerow(_parent())
    before = path.read_bytes()
    backup = CF.write(CF.fill([_candidate()], [_parent()], {PARENT_ID}).rows, path)
    assert backup.read_bytes() == before
    after = path.read_bytes()
    assert after.startswith(before) and after.count(b"\r\n") == 3
    with path.open(newline="", encoding="utf-8") as f:
        assert [r["layer"] for r in csv.DictReader(f)] == ["A", "P3c"]
