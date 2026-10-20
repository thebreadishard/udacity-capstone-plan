"""probes/fetch_labels_ccx53.sh against a fake server (a local folder behind a fake ssh): FETCHED only when every server file is in the corpus,
a failed copy or a missing file gives NOT FETCHED and exit 1 (17 Oct 2026: the rsync version said FETCHED with 44 of 538), files the corpus
already holds are kept."""
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from conftest import SHELL_HANG_GUARD_S

SCRIPT = Path(__file__).resolve().parent.parent / "probes" / "fetch_labels_ccx53.sh"
BASH = shutil.which("bash")
pytestmark = pytest.mark.skipif(BASH is None or shutil.which("tar") is None, reason="needs bash and tar")

FAKE_SSH = """#!/usr/bin/env bash
# drop the options up to user@host, run the rest as a local shell command (the 'server' is a local folder)
while [ $# -gt 0 ]; do case "$1" in root@*) shift; break ;; -i|-o) shift 2 ;; *) shift ;; esac; done
[ -n "${FAIL_SSH_ON:-}" ] && [[ "$*" == *"$FAIL_SSH_ON"* ]] && exit 255
bash -c "$*"; rc=$?
# a server file the copy did not bring: listed, never sent
[ -n "${EXTRA_LISTED:-}" ] && [[ "$*" == "cd "*"&& ls "* ]] && echo "$EXTRA_LISTED"
exit $rc
"""


def _setup(tmp_path: Path) -> tuple[Path, Path, dict]:
    server = tmp_path / "server"
    for mol in ("A_1", "A_2"):
        d = server / "molecules" / mol
        d.mkdir(parents=True)
        for name in ("hessian_b3lyp_analytic.npz", "hessian_wb97x_analytic.npz", "analytic_check.json"):
            (d / name).write_text(f"server {mol} {name}", encoding="utf-8")
    (server / "molecules" / "A_1" / "dipole_b3lyp_cphf.npz").write_text("server apt", encoding="utf-8")
    (server / "lane1.log").write_text("lane log", encoding="utf-8")
    (server / "gate").mkdir()
    (server / "gate" / "gate.log").write_text("gate ok", encoding="utf-8")
    plan = tmp_path / "plan"
    (plan / "modules" / "05_support_predictor" / "corpus" / "molecules").mkdir(parents=True)
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    (fake_bin / "ssh").write_text(FAKE_SSH, encoding="utf-8", newline="\n")
    (fake_bin / "ssh").chmod(0o755)
    env = {**os.environ, "P": plan.as_posix(), "REMOTE": server.as_posix(), "KEY": "none", "ENV_CMD": "echo env", "LANES_CMD": "echo 0",
           "PATH": fake_bin.as_posix() + os.pathsep + os.environ["PATH"]}
    return server, plan / "modules" / "05_support_predictor" / "corpus" / "molecules", env


def _run(env: dict) -> subprocess.CompletedProcess:
    return subprocess.run([BASH, SCRIPT.as_posix(), "10.0.0.1"], env=env, capture_output=True, text=True, encoding="utf-8", timeout=SHELL_HANG_GUARD_S,
                          check=False)


def test_a_complete_fetch_says_fetched_and_keeps_existing_files(tmp_path):
    _, corpus, env = _setup(tmp_path)
    (corpus / "A_1").mkdir()
    (corpus / "A_1" / "dipole_b3lyp_cphf.npz").write_text("route B apt", encoding="utf-8")
    r = _run(env)
    assert r.returncode == 0, r.stdout + r.stderr
    assert r.stdout.splitlines()[-1].startswith("FETCHED") and "server 2 ωB97X" in r.stdout
    assert (corpus / "A_2" / "hessian_wb97x_analytic.npz").read_text(encoding="utf-8") == "server A_2 hessian_wb97x_analytic.npz"
    assert (corpus / "A_1" / "dipole_b3lyp_cphf.npz").read_text(encoding="utf-8") == "route B apt"


def test_a_complete_copy_while_lanes_run_is_a_snapshot(tmp_path):
    _, _, env = _setup(tmp_path)
    r = _run({**env, "LANES_CMD": "echo 3"})
    assert r.returncode == 0 and r.stdout.splitlines()[-1].startswith("SNAPSHOT") and "3 label lanes still run" in r.stdout


def test_a_failed_copy_is_not_fetched(tmp_path):
    _, _, env = _setup(tmp_path)
    r = _run({**env, "FAIL_SSH_ON": "hessian_b3lyp_analytic"})
    assert r.returncode == 1 and r.stdout.splitlines()[-1].startswith("NOT FETCHED")
    assert "Hessians (ssh 255" in r.stdout


def test_a_file_missing_from_the_corpus_is_not_fetched(tmp_path):
    _, _, env = _setup(tmp_path)
    r = _run({**env, "EXTRA_LISTED": "A_9/hessian_wb97x_analytic.npz"})
    assert r.returncode == 1 and "1 server files not in the corpus" in r.stdout


def test_an_empty_server_is_not_fetched(tmp_path):
    server, _, env = _setup(tmp_path)
    shutil.rmtree(server / "molecules")
    (server / "molecules").mkdir()
    r = _run(env)
    assert r.returncode == 1 and "lists no analytic Hessian" in r.stdout
