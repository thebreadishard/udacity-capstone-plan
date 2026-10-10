"""probes/fivering_laptop_1015.sh (10 Oct 2026): the main pass never repeats a molecule; after it, every failed molecule is retried once with the
corpus's retry rule (--retry-failed), a second failure is named in the end marker, and a relaunch does not retry again. psi4 is replaced by a stub."""
import os
import shutil
import subprocess
from pathlib import Path

import pytest

PLAN = Path(__file__).resolve().parents[1]
BASH = shutil.which("bash")
pytestmark = pytest.mark.skipif(BASH is None, reason="bash not available")

STUB = r"""#!/usr/bin/env bash
# stands in for the psi4 python: `run_corpus.py --ids ID [--retry-failed] …` writes molecules/ID/result.json and counts its calls
cat > /dev/null                      # like python under psi4, the stub reads stdin (10 Oct: the loop lost its list that way)
id=""; retry=0
while [ $# -gt 0 ]; do case "$1" in --ids) id=$2; shift ;; --retry-failed) retry=1 ;; esac; shift; done
mkdir -p "molecules/$id"; echo "$id $retry" >> calls.txt
status=done
case "$id" in bad) [ $retry = 1 ] || status=failed ;; worse) status=failed ;; esac
printf '{"id": "%s", "status": "%s"}\n' "$id" "$status" > "molecules/$id/result.json"
"""


def _run(tmp: Path) -> subprocess.CompletedProcess:
    d = tmp / "work"
    d.mkdir(exist_ok=True)
    (d / "manifest.csv").write_text("id\n", encoding="utf-8")            # present: the corpus copy step is skipped
    (tmp / "list.txt").write_text("good\nbad\nworse\n", encoding="utf-8", newline="\n")
    (tmp / "py_stub.sh").write_text(STUB, encoding="utf-8", newline="\n")
    env = dict(os.environ, P=PLAN.as_posix(), D=d.as_posix(), LIST=(tmp / "list.txt").as_posix(), PY=f"{(tmp / 'py_stub.sh').as_posix()}",
               PIDFILE=(tmp / "f5.pid").as_posix(), NO_WAIT="1")
    os.chmod(tmp / "py_stub.sh", 0o755)
    return subprocess.run([BASH, (PLAN / "probes" / "fivering_laptop_1015.sh").as_posix()], env=env, capture_output=True, text=True,
                          timeout=120, check=False)


def test_failed_molecules_are_retried_once(tmp_path):
    r = _run(tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "bad done on retry" in r.stdout and "worse FAILED AGAIN" in r.stdout
    assert "failed after one retry: worse" in r.stdout
    calls = (tmp_path / "work" / "calls.txt").read_text().split("\n")
    assert calls[:5] == ["good 0", "bad 0", "worse 0", "bad 1", "worse 1"]
    r2 = _run(tmp_path)                                                    # a relaunch repeats nothing and retries nothing
    assert "failed after one retry: worse" in r2.stdout
    assert (tmp_path / "work" / "calls.txt").read_text().split("\n")[:6] == calls[:5] + [""]
