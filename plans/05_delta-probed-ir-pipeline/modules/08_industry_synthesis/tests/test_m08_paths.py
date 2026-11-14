"""The one resolver module 08 reads through (TASKS 20, 78; the standalone plan of 18 October 2026).

What matters is the behaviour at the edges: inside the plan repository the live file, in a submitted repository the snapshot, a
missing snapshot path named in the error rather than quietly fetched from somewhere else, and an absolute path refused.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
MODULE = HERE.parent
sys.path.insert(0, str(MODULE))
from m08 import paths as P  # noqa: E402


def test_the_plan_repository_reads_the_live_file() -> None:
    assert not P.snapshot_mode()
    assert P.resolve("TASKS.md") == P.PLAN / "TASKS.md"
    assert P.resolve("TASKS.md").is_file()


def test_the_snapshot_is_read_when_the_environment_asks(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv(P.MODE_ENV, "1")
    monkeypatch.setattr(P, "SNAPSHOT", tmp_path)
    (tmp_path / "modules").mkdir()
    (tmp_path / "modules" / "x.json").write_text("{}", encoding="utf-8")
    assert P.snapshot_mode()
    assert P.resolve("modules/x.json") == tmp_path / "modules" / "x.json"


def test_a_path_missing_from_the_snapshot_is_named(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv(P.MODE_ENV, "1")
    monkeypatch.setattr(P, "SNAPSHOT", tmp_path)
    with pytest.raises(FileNotFoundError, match=r"modules/missing.json"):
        P.resolve("modules/missing.json")
    assert P.resolve("modules/missing.json", must_exist=False) == tmp_path / "modules" / "missing.json"


def test_an_unknown_mode_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(P.MODE_ENV, "yes")
    with pytest.raises(ValueError, match="M08_SNAPSHOT"):
        P.snapshot_mode()


def test_an_absolute_path_is_refused() -> None:
    with pytest.raises(ValueError, match="absolute"):
        P.resolve(P.PLAN / "TASKS.md")


def test_a_path_comes_back_plan_relative(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    assert P.relative_to_plan(P.PLAN / "modules" / "x.json") == "modules/x.json"
    monkeypatch.setattr(P, "SNAPSHOT", tmp_path)
    assert P.relative_to_plan(tmp_path / "modules" / "x.json") == "modules/x.json"
    # a path under neither root is the live pipeline's own working directory, and it is quoted as it stands
    outside = Path("C:/elsewhere/x.json") if sys.platform == "win32" else Path("/elsewhere/x.json")
    assert P.relative_to_plan(outside) == outside.as_posix()
