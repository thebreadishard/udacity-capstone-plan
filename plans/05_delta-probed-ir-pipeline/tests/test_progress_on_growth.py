"""probes/progress_on_growth.sh: a progress line only when the watched files grow, the command's output and exit code pass through."""
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from conftest import SHELL_HANG_GUARD_S

SCRIPT = Path(__file__).resolve().parent.parent / "probes" / "progress_on_growth.sh"
BASH = shutil.which("bash")
pytestmark = pytest.mark.skipif(BASH is None, reason="needs bash")


def _run(tmp_path: Path, body: str, *opts: str, timeout: float = SHELL_HANG_GUARD_S) -> subprocess.CompletedProcess:
    (tmp_path / "mols").mkdir(exist_ok=True)
    job = tmp_path / "job.sh"
    job.write_text(body, encoding="utf-8", newline="\n")
    args = [BASH, SCRIPT.as_posix(), "--tag", "T", "--dir", (tmp_path / "mols").as_posix(), "--name", "psi4.out", "--interval", "1", *opts,
            "--", BASH, job.as_posix()]
    env = {**os.environ, "M": (tmp_path / "mols").as_posix()}
    return subprocess.run(args, capture_output=True, text=True, encoding="utf-8", timeout=timeout, check=False, env=env)


def test_growth_gives_progress_and_the_end_line_carries_the_exit_code(tmp_path):
    body = ("mkdir -p $M/a; echo 'unit started'; sleep 2; echo 1234 >> $M/a/psi4.out; sleep 3; echo 5678 >> $M/a/psi4.out; echo junk >> $M/a/other.txt;"
            " sleep 8; echo 'unit done'; exit 4\n")
    r = _run(tmp_path, body)
    lines = r.stdout.splitlines()
    assert r.returncode == 4 and "unit started" in lines and "unit done" in lines
    progress = [line for line in lines if "progress:" in line]
    assert progress and "at 10 bytes" in progress[-1]          # 'other.txt' is not watched
    assert lines[-1].startswith("=== (T) command ended rc=4")


def test_the_end_of_a_short_job_is_seen_within_seconds_not_after_the_interval(tmp_path):
    """19 Oct 2026: with a 600 s interval a job that ended at once still held the wrapper for ten minutes (a dry run, a deploy smoke)."""
    r = _run(tmp_path, "exit 3\n", "--interval", "600", timeout=300)   # the later --interval wins; a timeout below it fails the old loop
    assert r.returncode == 3 and r.stdout.splitlines()[-1].startswith("=== (T) command ended rc=3")


def test_a_job_that_writes_nothing_prints_no_progress(tmp_path):
    r = _run(tmp_path, "sleep 4\n")
    assert r.returncode == 0 and "progress:" not in r.stdout


def test_missing_options_are_refused(tmp_path):
    r = subprocess.run([BASH, SCRIPT.as_posix(), "--tag", "T", "--", "true"], capture_output=True, text=True, timeout=SHELL_HANG_GUARD_S, check=False)
    assert r.returncode == 2 and "usage" in r.stderr
