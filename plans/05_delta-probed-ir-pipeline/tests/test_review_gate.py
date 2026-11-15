"""The gate that refuses a commit whose diff has no independent review (the user, 14 November 2026).

The reviewing itself is nobody's code; what is tested here is the bookkeeping, because that is what can go quietly wrong: the digest
must be of the staged diff with the review record itself left out, a record must match the diff it was written for, and a diff
nobody has reviewed must be refused with a reason that says what to do.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "tools"))
import review_gate as R  # noqa: E402  the path line above must run first


@pytest.fixture
def staged(monkeypatch):
    """What would land, an empty record file, and HEAD on the trunk - all of this test's own."""
    def set_diff(text: str, records_path: Path, on_trunk: bool = True):
        monkeypatch.setattr(R, "landing_diff", lambda _incoming=None: text)
        monkeypatch.setattr(R, "files_landing", lambda _incoming=None: ["probes/x.py"] if text else [])
        monkeypatch.setattr(R, "on_trunk", lambda: on_trunk)
        monkeypatch.setattr(R, "RECORDS", records_path)
    return set_diff


def test_the_digest_is_of_the_diff_and_nothing_else():
    first, second = R.digest_of("diff --git a/x b/x\n+one\n"), R.digest_of("diff --git a/x b/x\n+two\n")
    assert first != second and len(first) == 16
    assert R.digest_of("diff --git a/x b/x\n+one\n") == first


def test_the_record_itself_is_left_out_of_the_digest():
    """Writing the record happens between the review and the commit; counting it would make every review stale at once."""
    assert any("tools/reviews.jsonl" in pattern for pattern in R.EXCLUDED)
    assert all(pattern.startswith(":(exclude)") for pattern in R.EXCLUDED)


def test_a_diff_with_no_review_is_refused_and_says_what_to_do(tmp_path, staged, capsys):
    staged("diff --git a/x b/x\n+one\n", tmp_path / "none.jsonl")
    assert R.check(None) == 1
    out = capsys.readouterr().out
    assert "no independent review" in out and "review_gate.py record" in out


def test_a_diff_with_a_review_passes_and_names_the_reviewer(tmp_path, staged, capsys):
    path = tmp_path / "reviews.jsonl"
    diff = "diff --git a/x b/x\n+one\n"
    staged(diff, path)
    path.write_text(json.dumps({"digest": R.digest_of(diff), "reviewer": "agent-7", "findings": 2,
                                "verdict": "both fixed"}) + "\n", encoding="utf-8")
    assert R.check(None) == 0
    assert "agent-7" in capsys.readouterr().out


def test_a_review_of_another_diff_does_not_count(tmp_path, staged):
    path = tmp_path / "reviews.jsonl"
    staged("diff --git a/x b/x\n+one\n", path)
    path.write_text(json.dumps({"digest": R.digest_of("something else"), "reviewer": "agent-7", "findings": 0,
                                "verdict": "nothing"}) + "\n", encoding="utf-8")
    assert R.check(None) == 1


def test_the_last_review_of_a_diff_is_the_one_that_counts(tmp_path, staged, capsys):
    path = tmp_path / "reviews.jsonl"
    diff = "diff --git a/x b/x\n+one\n"
    staged(diff, path)
    lines = [json.dumps({"digest": R.digest_of(diff), "reviewer": "first", "findings": 1, "verdict": "one left"}),
             json.dumps({"digest": R.digest_of(diff), "reviewer": "second", "findings": 0, "verdict": "clean"})]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    assert R.check(None) == 0
    assert "second" in capsys.readouterr().out


def test_nothing_staged_needs_no_review(tmp_path, staged):
    staged("", tmp_path / "none.jsonl")
    assert R.check(None) == 0


def test_a_commit_off_the_trunk_lands_nothing_and_is_not_checked(tmp_path, staged, capsys):
    """The rule's own shape: work on a branch is free, and the branch is reviewed when it comes home."""
    staged("diff --git a/x b/x\n+one\n", tmp_path / "none.jsonl", on_trunk=False)
    assert R.check(None) == 0
    assert "lands nothing" in capsys.readouterr().out


def test_a_merge_off_the_trunk_lands_nothing_either(tmp_path, staged, capsys):
    """Keeping a feature branch current by merging the trunk into it is not a landing (14 Nov 2026, the review's B4)."""
    staged("diff --git a/x b/x\n+one\n", tmp_path / "none.jsonl", on_trunk=False)
    assert R.check("master") == 0
    assert "lands nothing" in capsys.readouterr().out


def test_a_merge_onto_the_trunk_is_checked(tmp_path, staged):
    staged("diff --git a/x b/x\n+one\n", tmp_path / "none.jsonl", on_trunk=True)
    assert R.check("my-branch") == 1


def test_a_review_of_nothing_is_refused(tmp_path, staged):
    staged("", tmp_path / "reviews.jsonl")
    with pytest.raises(SystemExit, match="is empty: there is no change"):
        R.record("agent-7", 0, "clean", None, None)


def test_a_negative_finding_count_is_refused(tmp_path, staged):
    staged("diff --git a/x b/x\n+one\n", tmp_path / "reviews.jsonl")
    with pytest.raises(SystemExit, match="never negative"):
        R.record("agent-7", -1, "clean", None, None)


def test_a_recorded_review_is_found_again(tmp_path, staged):
    path = tmp_path / "reviews.jsonl"
    staged("diff --git a/x b/x\n+one\n", path)
    assert R.record("agent-7", 3, "two fixed, one noted", "a note", None) == 0
    assert R.check(None) == 0
    entry = json.loads(path.read_text(encoding="utf-8").splitlines()[-1])
    assert entry["reviewer"] == "agent-7" and entry["findings"] == 3 and entry["note"] == "a note"
    assert entry["files"] == ["probes/x.py"] and entry["date"]


def test_every_path_is_reviewed_until_someone_narrows_it():
    """The rule as the user set it: every diff. REVIEWED is the one place it could be narrowed."""
    assert R.REVIEWED == ("*",)
