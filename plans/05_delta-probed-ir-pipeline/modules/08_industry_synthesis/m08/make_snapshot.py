"""Build the frozen snapshot a submitted module 08 reads (the standalone plan of 18 October 2026, TASKS 78, 20).

Module 08 reads the other modules' folders, the website export and the plan's evidence files. A submitted repository has none of
them, so it carries `snapshot/` with the same paths under it and `m08/paths.resolve` reads from there (see that module).

What goes in is not a list somebody keeps up to date: the builder runs the scenarios with Python's own audit hook watching every
file opened for reading, and copies exactly those that lie under the plan or the repository. A file the scenarios never open is a
file the submitted module does not need; a file they open is in the snapshot by construction, so the two cannot drift apart.

    python -m m08.make_snapshot --dry-run     # what would be copied, with its size
    python -m m08.make_snapshot               # copy, and write snapshot/MANIFEST.json

The manifest holds every path with its bytes and sha256, the plan's commit and the date, so a reader of the submitted repository
can tell which state of the project the module was frozen from.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

from . import paths

MODULE = paths.MODULE
OWN_FOLDERS = ("modules/08_industry_synthesis",)     # the module's own files travel with the repository, not in the snapshot
SKIP_SUFFIXES = (".pyc", ".pyo", ".log", ".exit", ".pid")
MANIFEST = "MANIFEST.json"


@dataclass
class Recorder:
    """Every file the scenarios open for reading, as plan-relative or repository-relative paths."""

    plan: set[str] = field(default_factory=set)
    repo: set[str] = field(default_factory=set)

    def note(self, opened: Path) -> None:
        """Keep the path when it lies under the plan or the repository and is not the module's own or a run's leavings."""
        if opened.suffix in SKIP_SUFFIXES or not opened.is_file():
            return
        if opened.is_relative_to(paths.PLAN):
            rel = opened.relative_to(paths.PLAN).as_posix()
            if not rel.startswith(OWN_FOLDERS):
                self.plan.add(rel)
        elif opened.is_relative_to(paths.REPO):
            self.repo.add(opened.relative_to(paths.REPO).as_posix())

    def hook(self, event: str, args: tuple) -> None:
        """Python's audit hook: 'open' fires for every file the interpreter opens, with its mode."""
        if event != "open" or len(args) < 2 or args[1] is None or "r" not in str(args[1]):
            return
        try:
            self.note(Path(args[0]).resolve())
        except (OSError, TypeError, ValueError):       # a file descriptor or an unreadable name: not a path we can copy
            return


def run_scenarios(recorder: Recorder) -> int:
    """Run module 08's scenarios in this process with the recorder watching; returns their exit code."""
    sys.path.insert(0, str(MODULE))
    import run_scenarios as scenarios  # imported here, after the path is set, so the hook sees everything it opens

    sys.addaudithook(recorder.hook)
    return scenarios.main(["--no-candidate"])


def copy_into(snapshot: Path, recorder: Recorder) -> list[dict]:
    """Copy every recorded file under `snapshot/`, keeping its spelling; returns one row per file for the manifest."""
    rows = []
    for prefix, relatives, root in (("", sorted(recorder.plan), paths.PLAN), (paths.REPO_PREFIX, sorted(recorder.repo), paths.REPO)):
        for rel in relatives:
            source = root / rel
            target = snapshot / prefix / rel if prefix else snapshot / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            rows.append(dict(path=f"{prefix}/{rel}" if prefix else rel, bytes=target.stat().st_size,
                             sha256=hashlib.sha256(target.read_bytes()).hexdigest()))
    return rows


def plan_commit() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=paths.PLAN, capture_output=True, text=True,
                              check=True).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Freeze what module 08's scenarios read into snapshot/.")
    ap.add_argument("--dry-run", action="store_true", help="list what would be copied, copy nothing")
    ap.add_argument("--snapshot", type=Path, default=paths.SNAPSHOT)
    a = ap.parse_args(argv)
    if paths.snapshot_mode():
        raise SystemExit("the builder runs in the plan repository; here the module already reads a snapshot")

    recorder = Recorder()
    code = run_scenarios(recorder)
    total = sum((paths.PLAN / r).stat().st_size for r in recorder.plan) + sum((paths.REPO / r).stat().st_size for r in recorder.repo)
    print(f"scenarios exit {code}; {len(recorder.plan)} plan files and {len(recorder.repo)} repository files, {total / 1e6:.1f} MB")
    if a.dry_run:
        for rel in sorted(recorder.plan)[:20]:
            print(f"  {rel}")
        return 0 if code == 0 else 1

    if code != 0:
        raise SystemExit(f"the scenarios exit {code}: a snapshot of a state the module reports as failing would freeze it. "
                         "The content rewrite under decision 63/65 comes first (TASKS 146, the standalone plan's step 1).")
    if a.snapshot.exists():
        shutil.rmtree(a.snapshot)
    rows = copy_into(a.snapshot, recorder)
    manifest = dict(about="module 08's frozen snapshot — m08/make_snapshot.py", built=time.strftime("%Y-%m-%d %H:%M"),
                    plan_commit=plan_commit(), scenarios_exit=code, files=rows,
                    bytes=sum(r["bytes"] for r in rows))
    (a.snapshot / MANIFEST).write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    print(f"snapshot: {len(rows)} files, {manifest['bytes'] / 1e6:.1f} MB, plan commit {manifest['plan_commit']}")
    return 0 if code == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
