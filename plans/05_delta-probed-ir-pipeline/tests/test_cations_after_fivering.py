"""probes/cations_after_fivering.sh (10 Oct 2026): the resume chain does not wait silently for ever — a five-ring runner gone without its end marker
gives a (CA) marker once per pid, the chain gives up with a marker after MAX_DAYS, and with the end marker present it hands over to the cation route."""
import os
import shutil
import subprocess
from pathlib import Path

import pytest

PLAN = Path(__file__).resolve().parents[1]
BASH = shutil.which("bash")
pytestmark = pytest.mark.skipif(BASH is None, reason="bash not available")


def _run(tmp: Path, log_lines: list[str], pid: str) -> subprocess.CompletedProcess:
    (tmp / "f5.log").write_text("".join(s + "\n" for s in log_lines), encoding="utf-8", newline="\n")
    (tmp / "f5.pid").write_text(pid + "\n", encoding="utf-8", newline="\n")
    env = dict(os.environ, F5LOG=str(tmp / "f5.log"), F5PID=str(tmp / "f5.pid"), SLEEP_S="0", MAX_DAYS="0", CA_CMD="echo CATIONS-RESUMED")
    return subprocess.run([BASH, (PLAN / "probes" / "cations_after_fivering.sh").as_posix()], env=env, capture_output=True, text=True,
                          timeout=60, check=False)


def test_gone_runner_is_reported_and_the_chain_gives_up(tmp_path):
    r = _run(tmp_path, ["=== (F5) armed (pid 999999), priority 1"], "999999")      # no such process
    assert "RESUME CHAIN WAITING" in r.stdout and "pid 999999" in r.stdout
    assert "GAVE UP" in r.stdout and r.returncode == 1 and "CATIONS-RESUMED" not in r.stdout


def test_end_marker_hands_over_to_the_cation_route(tmp_path):
    r = _run(tmp_path, ["=== (F5) laptop runner finished: 181 molecules with a folder"], "999999")
    assert r.returncode == 0 and "resumed after the five-ring pool" in r.stdout and "CATIONS-RESUMED" in r.stdout
