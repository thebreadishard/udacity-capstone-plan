"""probes/wait_then_run.sh waits for its line and then runs the command, but runs a trailing --dry-run at once; probes/run_with_mem_watch.sh
starts its sampler only after the start line, retries it until a sample finds the process, and returns the command's status. Stand-ins
replace the server's jobs and the sampler."""
import shutil
import subprocess
import threading
import time
from pathlib import Path

import pytest

PLAN = Path(__file__).resolve().parents[1]
BASH = shutil.which("bash")
pytestmark = pytest.mark.skipif(BASH is None, reason="bash not available")


def _stub(path: Path, body: str) -> str:
    path.write_text("#!/usr/bin/env bash\n" + body, encoding="utf-8", newline="\n")
    path.chmod(0o755)
    return path.as_posix()


def _append_later(path: Path, line: str, delay: float) -> threading.Thread:
    def write() -> None:
        time.sleep(delay)
        with path.open("a", encoding="utf-8", newline="\n") as fh:
            fh.write(line + "\n")
    t = threading.Thread(target=write)
    t.start()
    return t


def test_wait_then_run_runs_only_after_the_line(tmp_path):
    log, out = tmp_path / "other.log", tmp_path / "ran.txt"
    log.write_text("=== (X) start\n", encoding="utf-8", newline="\n")
    job = _stub(tmp_path / "job.sh", f'date +%s.%N > "{out.as_posix()}"\n')
    t0 = time.time()
    writer = _append_later(log, "=== (X) all done: 0 failures", 2.0)
    r = subprocess.run([BASH, (PLAN / "probes" / "wait_then_run.sh").as_posix(), log.as_posix(), r"^=== \(X\) all done", "--", BASH, job],
                       env={"PATH": "/usr/bin:/bin", "WAIT_S": "0.2"}, capture_output=True, text=True, check=False, timeout=60)
    writer.join()
    assert r.returncode == 0 and "condition met" in r.stdout
    assert out.exists() and time.time() - t0 >= 2.0


def test_wait_then_run_passes_a_dry_run_through_at_once(tmp_path):
    args = tmp_path / "args.txt"
    job = _stub(tmp_path / "job.sh", f'echo "$*" > "{args.as_posix()}"\n')
    r = subprocess.run([BASH, (PLAN / "probes" / "wait_then_run.sh").as_posix(), (tmp_path / "absent.log").as_posix(), "never", "--", BASH,
                        job, "--dry-run"], env={"PATH": "/usr/bin:/bin", "WAIT_S": "60"}, capture_output=True, text=True, check=False, timeout=20)
    assert r.returncode == 0 and args.read_text().strip() == "--dry-run" and "waiting" not in r.stdout


def test_run_with_mem_watch_samples_after_the_start_and_returns_the_status(tmp_path):
    log, mem, calls = tmp_path / "run.log", tmp_path / "mem.log", tmp_path / "sampler_calls.txt"
    job = _stub(tmp_path / "job.sh", f'sleep 1; echo "  M labels started" >> "{log.as_posix()}"; sleep 3; exit 7\n')
    # the sampler stand-in finds no process on its first call and the process on its second, as mem_watch_wsl.sh logs them
    sampler = _stub(tmp_path / "sampler.sh", f'echo "$1 $2" >> "{calls.as_posix()}"\n'
                    f'if [ -s "{calls.as_posix()}" ] && [ $(wc -l < "{calls.as_posix()}") -ge 2 ]; then echo "t pid 42 rss_MB 1" >> "$2"; '
                    'else echo "t pid none rss_MB 0" >> "$2"; fi\n')
    r = subprocess.run([BASH, (PLAN / "probes" / "run_with_mem_watch.sh").as_posix(), log.as_posix(), "labels started", "molecules/M",
                        mem.as_posix(), "--", BASH, job], env={"PATH": "/usr/bin:/bin", "WAIT_S": "0.3", "MEM_WATCH": sampler},
                       capture_output=True, text=True, check=False, timeout=60)
    assert r.returncode == 7
    lines = calls.read_text().splitlines()
    assert len(lines) == 2 and lines[0] == f"molecules/M {mem.as_posix()}"
    assert "pid 42" in mem.read_text()


def test_run_with_mem_watch_without_the_start_line_never_samples(tmp_path):
    calls = tmp_path / "sampler_calls.txt"
    job = _stub(tmp_path / "job.sh", "exit 0\n")
    sampler = _stub(tmp_path / "sampler.sh", f'echo called >> "{calls.as_posix()}"\n')
    r = subprocess.run([BASH, (PLAN / "probes" / "run_with_mem_watch.sh").as_posix(), (tmp_path / "run.log").as_posix(), "labels started",
                        "molecules/M", (tmp_path / "mem.log").as_posix(), "--", BASH, job],
                       env={"PATH": "/usr/bin:/bin", "WAIT_S": "0.2", "MEM_WATCH": sampler}, capture_output=True, text=True, check=False, timeout=30)
    assert r.returncode == 0 and not calls.exists()
