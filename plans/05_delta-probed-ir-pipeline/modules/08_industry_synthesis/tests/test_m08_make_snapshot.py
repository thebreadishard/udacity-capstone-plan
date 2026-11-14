"""The snapshot builder's recorder (TASKS 20, 78; the standalone plan of 18 October 2026).

What the submitted module carries is decided by what the scenarios open, not by a list somebody maintains, so the part worth pinning
is the recorder: it keeps a plan file, keeps a repository file under its own prefix, and drops the module's own files, a run's
leavings and anything opened for writing. The build itself waits for the content rewrite (TASKS 146) and refuses meanwhile.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
MODULE = HERE.parent
sys.path.insert(0, str(MODULE))
from m08 import paths  # noqa: E402
from m08.make_snapshot import Recorder  # noqa: E402


def test_a_plan_file_is_kept() -> None:
    recorder = Recorder()
    recorder.note(paths.PLAN / "TASKS.md")
    assert recorder.plan == {"TASKS.md"} and not recorder.repo


def test_a_repository_file_keeps_its_own_root() -> None:
    recorder = Recorder()
    export = paths.REPO / "website" / "export" / "out" / "summary.json"
    if not export.is_file():
        pytest.skip("the website export is not built in this checkout")
    recorder.note(export)
    assert recorder.repo == {"website/export/out/summary.json"} and not recorder.plan


def test_the_modules_own_files_do_not_travel() -> None:
    """They are in the submitted repository already; copying them into the snapshot would duplicate the module."""
    recorder = Recorder()
    recorder.note(MODULE / "run_scenarios.py")
    assert not recorder.plan and not recorder.repo


def test_a_runs_leavings_are_not_evidence(tmp_path: Path) -> None:
    recorder = Recorder()
    for name in ("a.log", "b.pid", "c.exit", "d.pyc"):
        (tmp_path / name).write_text("x", encoding="utf-8")
        recorder.note(tmp_path / name)
    assert not recorder.plan and not recorder.repo


def test_only_reads_are_recorded() -> None:
    recorder = Recorder()
    recorder.hook("open", (str(paths.PLAN / "TASKS.md"), "w", None))
    recorder.hook("open", (str(paths.PLAN / "TASKS.md"), None, None))
    recorder.hook("exec", (None,))
    assert not recorder.plan
    recorder.hook("open", (str(paths.PLAN / "TASKS.md"), "r", None))
    assert recorder.plan == {"TASKS.md"}


def test_a_file_descriptor_does_not_break_the_hook() -> None:
    """The interpreter opens by descriptor too; the hook has to let that pass rather than fall over."""
    recorder = Recorder()
    recorder.hook("open", (3, "r", None))
    assert not recorder.plan and not recorder.repo
