"""probes/watch.sh (10 Oct 2026): one parameterised watch instead of dated copies. A job's markers are reported once (seen file outside any session's
scratchpad); a job gone before its end marker is an anomaly; a host that answers with another machine-id (a re-used IP) is an anomaly, not a silent
read of the wrong machine."""
import os
import shutil
import subprocess
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
    env = dict(os.environ, WATCH_JOBS=str(tmp / "jobs.tsv"), WATCH_SEEN=str(tmp / "seen.txt"), WATCH_CYCLES="1", WATCH_SLEEP="0",
               HOSTS_FILE=str(tmp / "hosts.tsv"), HOSTS_SSH=f"bash {stub.as_posix()}")   # not BASH: its path may hold a space
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
