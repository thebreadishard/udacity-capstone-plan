"""probes/run_in_scope.sh on stand-in process trees in WSL (TASKS 211, review round two, finding 2): the run is stopped by
ownership — its systemd scope — and not by a pattern on command lines. A grandchild that ignores SIGTERM, with a command line
that names nothing of the run, is gone when the script returns; a command that ends by itself keeps its exit code; and the
budget's exit is 124. Light: a few `sleep` processes under a 256 MB cap for a few seconds. Skipped where there is no WSL with a
systemd user manager (CI)."""
from __future__ import annotations

import shutil
import subprocess
import uuid
from pathlib import Path, PureWindowsPath

import pytest

PLAN = Path(__file__).resolve().parents[1]
SCRIPT = PLAN / "probes" / "run_in_scope.sh"
WSL = shutil.which("wsl.exe")
# the grandchild ignores SIGTERM and is renamed, so that nothing in its command line names the run
STUBBORN = "bash -c 'trap \"\" TERM; (trap \"\" TERM; exec -a quiet-worker sleep 300) & wait'"


def wsl(inner: str) -> subprocess.CompletedProcess:
    return subprocess.run([WSL, "-e", "bash", "-lc", inner], capture_output=True, text=True, timeout=120, check=False)


def script() -> str:
    w = PureWindowsPath(SCRIPT)
    return "/mnt/" + w.drive[0].lower() + "/" + "/".join(w.parts[1:])


def can_scope() -> bool:
    return WSL is not None and wsl(f"bash {script()} --check").returncode == 0


pytestmark = pytest.mark.skipif(not can_scope(), reason="no WSL with a systemd user manager on this machine")


def unit() -> str:
    return f"m08-scope-test-{uuid.uuid4().hex[:10]}"


def processes_of(name: str) -> str:
    """The unit's cgroup path as systemd reports it now: empty when the scope is gone."""
    return wsl(f"systemctl --user show {name}.scope -p ControlGroup --value").stdout.strip()


def test_a_grandchild_that_ignores_sigterm_is_gone_at_the_budget():
    name = unit()
    r = wsl(f"bash {script()} {name} 256 2 1 -- {STUBBORN}")
    assert r.returncode == 124, r.stdout + r.stderr
    assert f"process(es) left in {name} were killed; none is left" in r.stdout and "stopped at the budget of 2 s" in r.stdout
    assert processes_of(name) == ""
    assert wsl("pgrep -fc quiet-worker").stdout.strip() == "0"


def test_a_command_that_ends_by_itself_keeps_its_exit_code_and_leaves_nothing():
    name = unit()
    r = wsl(f"bash {script()} {name} 256 30 1 -- bash -c 'echo unit $SCOPE_UNIT; (exec -a quiet-orphan sleep 300) & exit 5'")
    assert r.returncode == 5 and f"unit {name}" in r.stdout, r.stdout + r.stderr
    assert "1 process(es) left" in r.stdout and "stopped at the budget" not in r.stdout       # the orphan it left was the unit's
    assert processes_of(name) == "" and wsl("pgrep -fc quiet-orphan").stdout.strip() == "0"


@pytest.mark.parametrize(("args", "match"), [("bad/name 256 2 1 -- true", "characters outside"), ("u 256 x 1 -- true", "not a whole number"),
                                             ("u 256 2 1 --", "no command")])
def test_usage_errors_are_refused_before_anything_runs(args: str, match: str):
    r = wsl(f"bash {script()} {args}")
    assert r.returncode == 2 and match in r.stdout
