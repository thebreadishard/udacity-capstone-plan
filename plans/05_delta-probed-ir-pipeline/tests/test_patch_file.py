"""tools/patch_file.py: anchors asserted before any write; a failed anchor leaves the file byte-identical; append and insert behave."""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import patch_file as pf  # noqa: E402


def test_patch_applies_and_keeps_lf(tmp_path):
    p = tmp_path / "a.md"
    p.write_text("alpha\nbeta\ngamma\n", encoding="utf-8", newline="\n")
    assert pf.patch(str(p), [("beta", "BETA"), ("gamma", "GAMMA")]) == 2
    assert p.read_bytes() == b"alpha\nBETA\nGAMMA\n"


def test_failed_anchor_writes_nothing(tmp_path):
    p = tmp_path / "a.md"
    p.write_text("alpha\nbeta\nbeta\n", encoding="utf-8", newline="\n")
    before = p.read_bytes()
    with pytest.raises(AssertionError):
        pf.patch(str(p), [("alpha", "A"), ("beta", "B")])  # beta occurs twice: the whole patch is refused
    assert p.read_bytes() == before
    assert not (tmp_path / "a.md.tmp").exists()


def test_append_and_insert(tmp_path):
    p = tmp_path / "a.md"
    p.write_text("one\ntwo\n\n\n", encoding="utf-8", newline="\n")
    pf.append(str(p), "three\n")
    assert p.read_text(encoding="utf-8") == "one\ntwo\nthree\n"
    pf.insert_after_line(str(p), "one", "one-and-a-half")
    assert p.read_text(encoding="utf-8").split("\n")[:3] == ["one", "one-and-a-half", "two"]
    with pytest.raises(AssertionError):
        pf.insert_after_line(str(p), "o", "x")  # the needle matches several lines


def test_control_characters_from_a_mangled_escape_are_refused(tmp_path):
    """11 Oct 2026: a heredoc turned the \\t of a Windows path into a tab ('claude<TAB>est_suites_task.log' in TASKS)."""
    p = tmp_path / "a.md"
    p.write_text("path: X\n", encoding="utf-8", newline="\n")
    before = p.read_bytes()
    for bad in ("C:\\Temp\tlog", "a\bb", "page\fbreak"):
        with pytest.raises(AssertionError):
            pf.patch(str(p), [("X", bad)])
        with pytest.raises(AssertionError):
            pf.append(str(p), bad)
        with pytest.raises(AssertionError):
            pf.insert_after_line(str(p), "path", bad)
    assert p.read_bytes() == before
    pf.patch(str(p), [("X", "C:\\Temp\\claude\\test.log")])                  # backslashes themselves are fine
    pf.patch(str(p), [("path:", "a\tb")], controls=True)                         # a TSV edit says so
    pf.patch(str(p), [("a\tb", "c\td")])                                       # a tab the anchor carries may stay
    assert p.read_text(encoding="utf-8") == "c\td C:\\Temp\\claude\\test.log\n"


def test_patch_many_writes_no_file_when_one_anchor_fails(tmp_path):
    """15 Oct 2026: a four-file patch wrote three files and stopped at the fourth; patch_many checks all before writing any."""
    a, b = tmp_path / "a.txt", tmp_path / "b.txt"
    a.write_text("alpha\n", encoding="utf-8")
    b.write_text("beta\n", encoding="utf-8")
    with pytest.raises(AssertionError, match="b.txt"):
        pf.patch_many({str(a): [("alpha", "ALPHA")], str(b): [("gamma", "GAMMA")]})
    assert a.read_text(encoding="utf-8") == "alpha\n" and b.read_text(encoding="utf-8") == "beta\n"
    assert pf.patch_many({str(a): [("alpha", "ALPHA")], str(b): [("beta", "BETA")]}) == 2
    assert a.read_text(encoding="utf-8") == "ALPHA\n" and b.read_text(encoding="utf-8") == "BETA\n"
