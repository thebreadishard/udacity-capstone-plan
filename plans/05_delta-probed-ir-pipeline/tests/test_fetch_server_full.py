"""tools/fetch_server_full.sh against a fake server (a local folder behind a fake ssh that answers the machine-id pin): a finished run is
copied, sha256-checked and recorded on both sides; an unfinished run, an existing target, an unset READY, a changed file and a missing
environment listing each give NOT FETCHED and no FETCHED line; VERIFY_ONLY re-checks a copy; NO_RECORD writes nothing; a wrong machine is
refused before any copy."""
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from conftest import SHELL_HANG_GUARD_S

TOOL = Path(__file__).resolve().parents[1] / "tools" / "fetch_server_full.sh"
BASH = shutil.which("bash")
pytestmark = pytest.mark.skipif(BASH is None or shutil.which("tar") is None, reason="needs bash and tar")
MACHINE_ID = "0123abcd"

FAKE_SSH = """#!/usr/bin/env bash
# drop the options up to root@host, answer the machine-id pin, run the rest as a local shell command (the 'server' is a local folder)
while [ $# -gt 0 ]; do case "$1" in root@*) shift; break ;; -i|-o) shift 2 ;; *) shift ;; esac; done
cmd="$*"
cmd="${cmd/cat \\/etc\\/machine-id;/echo $FAKE_MACHINE_ID;}"
bash -c "$cmd"
"""
FAKE_CONDA = '#!/usr/bin/env bash\necho "# packages in environment $3"\necho "pyscf 2.14.0"\n'


def setup(tmp_path: Path, served_id: str = MACHINE_ID) -> tuple[Path, Path, dict]:
    server = tmp_path / "server"
    (server / "run" / "mol").mkdir(parents=True)
    (server / "run" / "mol" / "hess.json").write_text('{"h": 1}', encoding="utf-8")
    (server / "run" / "run.log").write_text("=== all done\n", encoding="utf-8")
    (server / "code").mkdir()
    (server / "code" / "runner.sh").write_text("echo run\n", encoding="utf-8")
    (server / "miniforge3" / "envs" / "qc05").mkdir(parents=True)
    (server / "miniforge3" / "bin").mkdir(parents=True)
    (server / "miniforge3" / "bin" / "conda").write_text(FAKE_CONDA, encoding="utf-8", newline="\n")
    (server / "miniforge3" / "bin" / "conda").chmod(0o755)
    fake = tmp_path / "fake_ssh.sh"
    fake.write_text(FAKE_SSH, encoding="utf-8", newline="\n")
    hosts = tmp_path / "hosts.tsv"
    hosts.write_text(f"fake\t10.0.0.9\t{MACHINE_ID}\ta local folder\n", encoding="utf-8", newline="\n")
    # $HOSTS_SSH is word-split, so 'bash' by name: the full path of Git's bash holds a space
    env = {**os.environ, "HOSTS_FILE": hosts.as_posix(), "HOSTS_SSH": f"bash {fake.as_posix()}", "FAKE_MACHINE_ID": served_id,
           "REMOTE_ROOT": server.as_posix(), "READY": f"grep -q 'all done' {server.as_posix()}/run/run.log"}
    return server, tmp_path / "copy", env


def run(env: dict, dst: Path, *parts: str) -> subprocess.CompletedProcess:
    return subprocess.run([BASH, TOOL.as_posix(), "fake", "testrun", dst.as_posix(), *(parts or ("run", "code"))], env=env, capture_output=True,
                          text=True, encoding="utf-8", timeout=SHELL_HANG_GUARD_S, check=False)


def test_a_finished_run_is_fetched_and_recorded_on_both_sides(tmp_path):
    server, dst, env = setup(tmp_path)
    r = run(env, dst)
    assert r.returncode == 0, r.stdout + r.stderr
    assert r.stdout.strip().splitlines()[-1].startswith("FETCHED testrun 3 files")
    assert (dst / "run" / "mol" / "hess.json").read_text(encoding="utf-8") == '{"h": 1}'
    assert "pyscf 2.14.0" in (dst / "server" / "conda_lists.txt").read_text(encoding="utf-8")
    assert "(no fetched.log on the server)" in (dst / "server" / "fetched_log_at_fetch.txt").read_text(encoding="utf-8")
    assert (server / "fetched.log").read_text(encoding="utf-8").startswith("FETCHED testrun 3 files")
    assert (dst / "FETCHED.txt").read_text(encoding="utf-8").startswith("FETCHED testrun 3 files")


@pytest.mark.parametrize(("change", "says"), [
    ("unfinished", "not finished"),
    ("exists", "exists - refusing"),
    ("no_ready", "READY"),
])
def test_refusals_before_any_copy(tmp_path, change, says):
    server, dst, env = setup(tmp_path)
    if change == "unfinished":
        (server / "run" / "run.log").write_text("still running\n", encoding="utf-8")
    elif change == "exists":
        dst.mkdir()
    else:
        env.pop("READY")
    r = run(env, dst)
    assert r.returncode != 0 and says in r.stdout + r.stderr
    assert not (server / "fetched.log").exists() and not (dst / "FETCHED.txt").exists()


def test_a_wrong_machine_is_refused(tmp_path):
    _server, dst, env = setup(tmp_path, served_id="ffff0000")
    r = run(env, dst)
    assert r.returncode != 0 and "WRONG MACHINE" in r.stderr and not dst.exists()


def test_a_file_changed_after_the_copy_is_a_mismatch_and_verify_only_sees_it(tmp_path):
    server, dst, env = setup(tmp_path)
    assert run(env, dst).returncode == 0
    (server / "run" / "mol" / "hess.json").write_text('{"h": 2}', encoding="utf-8")
    r = run({**env, "VERIFY_ONLY": "1"}, dst)
    assert r.returncode == 1 and "MISMATCH" in r.stdout
    assert (dst / "FETCHED.txt").read_text(encoding="utf-8").count("FETCHED") == 1


def test_no_record_compares_and_writes_nothing(tmp_path):
    server, dst, env = setup(tmp_path)
    assert run(env, dst).returncode == 0
    r = run({**env, "VERIFY_ONLY": "1", "NO_RECORD": "1"}, dst)
    assert r.returncode == 0 and r.stdout.startswith("VERIFIED testrun 3 files")
    assert (server / "fetched.log").read_text(encoding="utf-8").count("FETCHED") == 1


def test_a_copy_without_an_environment_listing_is_not_fetched(tmp_path):
    server, dst, env = setup(tmp_path)
    shutil.rmtree(server / "miniforge3" / "envs")
    (server / "miniforge3" / "envs").mkdir()
    r = run(env, dst)
    assert r.returncode == 1 and "no environment listing" in r.stdout and not (server / "fetched.log").exists()
