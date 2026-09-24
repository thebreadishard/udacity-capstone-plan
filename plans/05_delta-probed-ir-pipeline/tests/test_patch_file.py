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
