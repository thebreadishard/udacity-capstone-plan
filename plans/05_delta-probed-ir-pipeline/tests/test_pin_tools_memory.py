"""pin_tools' memory guard (20 Oct 2026): a pin that loads the corpus does not start when the jobs beside it need the memory."""
import pytest

import pin_tools


def test_the_free_commit_is_measured():
    free = pin_tools.free_commit_gb()
    assert free is None or free > 0


def test_a_pin_that_needs_more_than_is_free_is_skipped_with_the_numbers(monkeypatch):
    monkeypatch.setattr(pin_tools, "free_commit_gb", lambda: 3.2)
    with pytest.raises(pytest.skip.Exception, match=r"3\.2 GB can be committed, this pin needs about 6 GB"):
        pin_tools.require_free_memory()
    pin_tools.require_free_memory(3.0)                                  # enough: no skip


def test_an_unknown_free_memory_does_not_skip(monkeypatch):
    monkeypatch.setattr(pin_tools, "free_commit_gb", lambda: None)
    pin_tools.require_free_memory(1e9)
