"""probes/watch.sh (10 Oct 2026): one parameterised watch instead of dated copies. A job's markers are reported once (seen file outside any session's
scratchpad); a job gone before its end marker is an anomaly; a host that answers with another machine-id (a re-used IP) is an anomaly, not a silent
read of the wrong machine."""
import os
import shutil
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest

PLAN = Path(__file__).resolve().parents[1]
BASH = shutil.which("bash")
pytestmark = pytest.mark.skipif(BASH is None, reason="bash not available")


def _run(tmp: Path, jobs: str, hosts: str = "", ssh_out: str = "") -> subprocess.CompletedProcess:
    (tmp / "jobs.tsv").write_text(jobs, encoding="utf-8", newline="\n")
    (tmp / "hosts.tsv").write_text(hosts, encoding="utf-8", newline="\n")
    (tmp / "ssh_out.txt").write_text(ssh_out + "\n", encoding="utf-8", newline="\n")
    stub = tmp / "ssh_stub.sh"                                        # stands in for ssh: prints a machine-id line and the remote output
    stub.write_text(f"#!/usr/bin/env bash\ncat '{(tmp / 'ssh_out.txt').as_posix()}'\n", encoding="utf-8", newline="\n")
    fake_bin = tmp / "bin"                                            # 17 Oct 2026: the real gh made these tests fail while the live CI was red
    fake_bin.mkdir(exist_ok=True)
    (fake_bin / "gh").write_text("#!/usr/bin/env bash\nexit 1\n", encoding="utf-8", newline="\n")
    (fake_bin / "gh").chmod(0o755)
    env = dict(os.environ, WATCH_JOBS=str(tmp / "jobs.tsv"), WATCH_SEEN=str(tmp / "seen.txt"), WATCH_CYCLES="1", WATCH_SLEEP="0",
               WATCH_BEAT=str(tmp / "watch_heartbeat"),                   # never the live heartbeat: a test would make a stopped watch look alive
               PATH=fake_bin.as_posix() + os.pathsep + os.environ["PATH"],
               HOSTS_FILE=str(tmp / "hosts.tsv"), HOSTS_SSH=f"bash {stub.as_posix()}",   # not BASH: its path may hold a space
               RUNSPEC_ROOT=str(tmp), RUNSPEC_DIR=str(tmp / "specs"), RUNSPEC_STATE=str(tmp / "runstate"), RUNSPEC_PYTHON=sys.executable)
    return subprocess.run([BASH, (PLAN / "probes" / "watch.sh").as_posix()], env=env, capture_output=True, text=True, timeout=120, check=False)


def _job(tmp: Path, lines: list[str]) -> str:
    log = tmp / "job.log"
    log.write_text("".join(s + "\n" for s in lines), encoding="utf-8", newline="\n")
    rel = os.path.relpath(log, PLAN).replace("\\", "/")
    return f"X\t{rel}\t^=== \\(X\\) \t^=== \\(X\\) finished\t[n]o_such_process_xyz\n"


def test_marker_once_then_anomaly_then_quiet(tmp_path):
    jobs = _job(tmp_path, ["=== (X) armed (pid 1)", "=== (X) step done"])
    r = _run(tmp_path, jobs)
    assert r.returncode == 2 and "MARKER" in r.stdout and "step done" in r.stdout and "armed" not in r.stdout
    r = _run(tmp_path, jobs)                                         # seen; the process is gone before the end marker
    assert r.returncode == 1 and "job X gone" in r.stdout
    jobs = _job(tmp_path, ["=== (X) step done", "=== (X) finished"])
    assert _run(tmp_path, jobs).returncode == 2                       # the end marker is reported once
    r = _run(tmp_path, jobs)
    assert r.returncode == 0 and "quiet cycle" in r.stdout


def test_reused_ip_is_an_anomaly(tmp_path):
    hosts = "labels\t192.0.2.1\taaaa\tthe labels server\n"
    r = _run(tmp_path, "", hosts, ssh_out="bbbb\nlanes 4 ok 1 failed 0 done 0")
    assert r.returncode == 1 and "another machine" in r.stdout
    r = _run(tmp_path, "", hosts, ssh_out="aaaa\nlanes 4 ok 1 failed 0 done 0")
    assert r.returncode == 0 and "lanes 4 ok 1" in r.stdout


def test_a_specced_run_that_vanished_wakes_once(tmp_path):
    """15 Oct 2026 (TASKS 63): a run of tools/runspec.py whose process is gone without an exit file is one ANOMALY through the watch, then
    quiet while nothing changes; the quiet line names the run. (The progress gap itself is tested in test_runspec.py.)"""
    pytest.importorskip("pydantic")
    sys.path.insert(0, str(PLAN / "tools"))
    import runspec as R
    work = tmp_path / "w"
    work.mkdir()
    (work / "demo.log").write_text("  progress 1\n", encoding="utf-8", newline="\n")
    spec = R.RunSpec.model_validate(dict(name="demo", purpose="TASKS 63 watch test", host="laptop", workdir="w", command="true",
                                         sources=[{"local": "tools/stamp.py"}], progress={"regex": "^  progress ", "max_gap_minutes": 30}))
    (tmp_path / "specs").mkdir()
    (tmp_path / "specs" / "demo.json").write_text(spec.model_dump_json(), encoding="utf-8")
    long_ago = datetime.now().astimezone() - timedelta(hours=2)
    R.save_state("demo", R.RunState(started_at=long_ago, phase_started_at=long_ago, progress_count=1, progress_seen_at=long_ago),
                 tmp_path / "runstate")
    (work / "demo.pid").write_text("999999\n", encoding="utf-8")       # no such process: gone without an exit file
    r = _run(tmp_path, "")
    assert r.returncode == 1 and "run demo gone without an exit file" in r.stdout
    r = _run(tmp_path, "")
    assert r.returncode == 0 and "runs demo 1 lines" in r.stdout


def test_every_new_line_of_one_check_is_reported(tmp_path):
    """19 Oct 2026: the watch stopped at the first new line of a runspec check, and the check had saved the states already, so a second
    run's news in the same check was never reported. Two runs with news in one check: both lines, and the anomaly's exit code."""
    pytest.importorskip("pydantic")
    sys.path.insert(0, str(PLAN / "tools"))
    import runspec as R
    (tmp_path / "specs").mkdir()
    long_ago = datetime.now().astimezone() - timedelta(hours=2)
    for name in ("ended", "gone"):
        work = tmp_path / name
        work.mkdir()
        (work / f"{name}.log").write_text("  progress 1\n", encoding="utf-8", newline="\n")
        spec = R.RunSpec.model_validate(dict(name=name, purpose="watch test, two runs", host="laptop", workdir=name, command="true",
                                             sources=[{"local": "tools/stamp.py"}], progress={"regex": "^  progress ", "max_gap_minutes": 30}))
        (tmp_path / "specs" / f"{name}.json").write_text(spec.model_dump_json(), encoding="utf-8")
        R.save_state(name, R.RunState(started_at=long_ago, phase_started_at=long_ago, progress_count=1, progress_seen_at=long_ago),
                     tmp_path / "runstate")
    (tmp_path / "ended" / "ended.exit").write_text("0\n", encoding="utf-8")
    (tmp_path / "gone" / "gone.pid").write_text("999999\n", encoding="utf-8")
    r = _run(tmp_path, "")
    assert r.returncode == 1 and "run ended ended (exit 0)" in r.stdout and "run gone gone without an exit file" in r.stdout
    assert _run(tmp_path, "").returncode == 0


def test_every_check_stamps_the_heartbeat(tmp_path):
    """19 Oct 2026: on 18 Oct no watch ran for hours and nothing said so; state.sh reads this stamp's age."""
    _run(tmp_path, "")
    stamp = (tmp_path / "watch_heartbeat").read_text(encoding="utf-8").strip()
    assert abs(datetime.now() - datetime.strptime(stamp, "%Y-%m-%d %H:%M:%S")) < timedelta(minutes=2)
