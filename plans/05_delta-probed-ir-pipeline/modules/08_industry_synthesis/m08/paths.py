"""One root for every file module 08 reads (the standalone plan of 18 October 2026, TASKS 78, 20).

Module 08 is the integration module: inside the plan repository it reads the other modules' folders, the website export and the
plan's evidence files. A submitted module has none of those. It carries a frozen `snapshot/`, built by `m08/make_snapshot.py`, with
the same paths under it. `resolve` is the one place that knows which of the two repositories it is in, so that no reader has to.

A snapshot that lacks a path raises with that path's name: a half-snapshot that silently falls back to a live folder would pass its
tests in the plan repository and fail in the submitted one, which is the failure this module exists to avoid.
"""
from __future__ import annotations

import os
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1]
PLAN = MODULE.parents[1]
REPO = PLAN.parents[1]         # the website export and the other plans live beside the plan folder
SNAPSHOT = MODULE / "snapshot"
REPO_PREFIX = "repo"           # a repository-relative path is stored under snapshot/repo/, so the two roots cannot collide
PLAN_MARKER = "TASKS.md"       # the plan folder's own file; a submitted repository has no such parent
MODE_ENV = "M08_SNAPSHOT"      # "1" reads the snapshot inside the plan repository too (the snapshot-mode test)


def snapshot_mode() -> bool:
    """Whether the module must read its frozen snapshot: in a submitted repository, or when the environment asks for it."""
    asked = os.environ.get(MODE_ENV)
    if asked not in (None, "", "0", "1"):
        raise ValueError(f"{MODE_ENV}={asked!r}: '1' to read the snapshot, '0' or unset to read the plan")
    if asked == "1":
        return True
    return not (PLAN / PLAN_MARKER).is_file()


def resolve(relative: str | Path, *, must_exist: bool = True) -> Path:
    """The file for a plan-relative path: the live file in the plan repository, `snapshot/<path>` in the submitted one.

    must_exist=False is for the reads whose caller treats absence as an answer (an evidence page that was never written, say); the
    path comes back unchecked and the caller's own test decides.
    """
    rel = Path(relative)
    if rel.is_absolute():
        raise ValueError(f"{rel} is absolute; resolve takes a path relative to the plan folder")
    if not snapshot_mode():
        return PLAN / rel
    inside = SNAPSHOT / rel
    if must_exist and not inside.exists():
        raise FileNotFoundError(f"{rel.as_posix()} is not in {SNAPSHOT.name}/; rebuild it with m08/make_snapshot.py")
    return inside


def resolve_repo(relative: str | Path, *, must_exist: bool = True) -> Path:
    """The file for a path relative to the repository root (the website export): live, or `snapshot/repo/<path>`.

    The export is the catalogue module 08 answers from, and it lies outside the plan folder, so it cannot be addressed by a
    plan-relative path. It keeps its own prefix inside the snapshot for the same reason.
    """
    rel = Path(relative)
    if rel.is_absolute():
        raise ValueError(f"{rel} is absolute; resolve_repo takes a path relative to the repository root")
    if not snapshot_mode():
        return REPO / rel
    inside = SNAPSHOT / REPO_PREFIX / rel
    if must_exist and not inside.exists():
        raise FileNotFoundError(f"{REPO_PREFIX}/{rel.as_posix()} is not in {SNAPSHOT.name}/; rebuild it with m08/make_snapshot.py")
    return inside


def relative_to_plan(path: Path) -> str:
    """A path as a record should quote it: plan-relative when it lies under the plan or the snapshot, else the path itself.

    A path under neither is not a mistake — the live pipeline computes a molecule in a working directory of its own, and that
    directory belongs in the record as it stands.
    """
    for root in (SNAPSHOT, PLAN):
        if path.is_relative_to(root):
            return path.relative_to(root).as_posix()
    return path.as_posix()
