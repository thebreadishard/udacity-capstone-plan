"""probes/cation_oom_check.sh (TASKS 122): an OOM-killed scope is recognised from the kernel's line as well as from systemd's result, the
system journal is read on request, and a scope that ended normally is not called a kill. journalctl is a stand-in on PATH."""
import os
import shutil
import subprocess
from pathlib import Path

import pytest

PLAN = Path(__file__).resolve().parents[1]
BASH = shutil.which("bash")
pytestmark = pytest.mark.skipif(BASH is None, reason="bash not available")

STARTED = 'Started run-p78716-i80017.scope - [systemd-run] /usr/bin/time -f "({tag}) P3c_428228e5a5 max RSS %M kB, wall %e s" python x.py\n'


def _run(tmp_path, unit_lines: str, tag: str = "CA", journal: str = "--user", journal_tag: str | None = None) -> subprocess.CompletedProcess:
    """A journalctl that prints the whole journal, or the scope's own lines when called with -u; it records whether --user was given."""
    (tmp_path / "all.txt").write_text(STARTED.format(tag=journal_tag or tag), encoding="utf-8", newline="\n")
    (tmp_path / "unit.txt").write_text(unit_lines, encoding="utf-8", newline="\n")
    stub = tmp_path / "bin" / "journalctl"
    stub.parent.mkdir()
    stub.write_text("#!/usr/bin/env bash\n"
                    f'echo "$@" >> "{(tmp_path / "args.txt").as_posix()}"\n'
                    f'case " $* " in *" -u "*) cat "{(tmp_path / "unit.txt").as_posix()}" ;; *) cat "{(tmp_path / "all.txt").as_posix()}" ;; esac\n',
                    encoding="utf-8", newline="\n")
    stub.chmod(0o755)
    env = dict(os.environ, PATH=stub.parent.as_posix() + os.pathsep + os.environ["PATH"], OOM_TAG=tag, OOM_JOURNAL=journal, OOM_WAIT="1")
    return subprocess.run([BASH, (PLAN / "probes" / "cation_oom_check.sh").as_posix(), "P3c_428228e5a5"], env=env, capture_output=True,
                          text=True, timeout=60, check=False)


def test_the_kernel_line_alone_is_a_kill(tmp_path):
    """25 Oct 2026: the kernel's line was in the journal one second before systemd's result."""
    res = _run(tmp_path, "run-p78716-i80017.scope: The kernel OOM killer killed some processes in this unit.\n")
    assert res.returncode == 0 and "oom-kill" in res.stdout


def test_systemds_result_is_a_kill(tmp_path):
    assert _run(tmp_path, "run-p78716-i80017.scope: Failed with result 'oom-kill'.\n").returncode == 0


def test_a_normal_end_is_not_a_kill(tmp_path):
    res = _run(tmp_path, "run-p78716-i80017.scope: Deactivated successfully.\n")
    assert res.returncode == 1 and "not an oom-kill" in res.stdout


def test_the_system_journal_and_another_tag(tmp_path):
    res = _run(tmp_path, "run-p78716-i80017.scope: Failed with result 'oom-kill'.\n", tag="CX", journal="system")
    assert res.returncode == 0
    assert "--user" not in (tmp_path / "args.txt").read_text(encoding="utf-8")


def test_no_scope_for_the_molecule(tmp_path):
    res = _run(tmp_path, "", tag="CX", journal_tag="CA")       # the journal names the molecule with CA, the caller asks for CX
    assert res.returncode == 2 and "no scope found" in res.stdout
