"""probes/anchor_wave_progress.sh: a progress line only when result files appear, the wave's exit code reported, a dry run that checks inputs."""
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from conftest import SHELL_HANG_GUARD_S

SCRIPT = Path(__file__).resolve().parent.parent / "probes" / "anchor_wave_progress.sh"
BASH = shutil.which("bash")
pytestmark = pytest.mark.skipif(BASH is None, reason="needs bash")


def _setup(tmp_path: Path, wave_body: str) -> tuple[Path, dict]:
    root = tmp_path / "probes"
    (root / "results").mkdir(parents=True)
    geom = tmp_path / "geometry.json"
    geom.write_text("{}", encoding="utf-8")
    (tmp_path / "wave.txt").write_text(f"quinoline|{geom.as_posix()}|2|8|10000\n", encoding="utf-8", newline="\n")
    (root / "anchor_wave.sh").write_text("#!/usr/bin/env bash\n" + wave_body, encoding="utf-8", newline="\n")
    python = shutil.which("python") or shutil.which("python3")
    env = {**os.environ, "ROOT": root.as_posix(), "PY": Path(python).as_posix(), "INTERVAL_S": "1"}
    return tmp_path / "wave.txt", env


def _run(list_file: Path, env: dict, *extra: str) -> subprocess.CompletedProcess:
    return subprocess.run([BASH, SCRIPT.as_posix(), list_file.as_posix(), *extra], env=env, capture_output=True, text=True, timeout=SHELL_HANG_GUARD_S,
                          check=False)


def test_progress_lines_follow_new_files_and_the_end_is_reported(tmp_path):
    body = ("out=$ROOT/results/quinoline_ccpvdz; mkdir -p $out/apt_ccsd_t_field.npz.fields\n"
            "sleep 2; touch $out/grad_00_m.npy $out/grad_00_p.npy; sleep 2; touch $out/apt_ccsd_t_field.npz.fields/x_p.npz; sleep 8\n")
    # the long last sleep: the wrapper counts only while the wave runs, and a loaded laptop (the 03:41 nightly suite, 17 Oct) polls slowly
    list_file, env = _setup(tmp_path, body)
    r = _run(list_file, env)
    assert r.returncode == 0, r.stdout + r.stderr
    counts = [int(line.split("progress: ")[1].split()[0]) for line in r.stdout.splitlines() if "progress:" in line]
    # how many lines appear depends on the machine's speed against the 1 s interval; each one must carry a new count, the last all three files
    assert counts and counts[-1] == 3 and counts == sorted(set(counts))
    assert r.stdout.splitlines()[-1].startswith("=== (AS3W) wave done")


def test_a_stalled_wave_prints_no_progress(tmp_path):
    list_file, env = _setup(tmp_path, "sleep 4\n")
    r = _run(list_file, env)
    assert r.returncode == 0 and "progress:" not in r.stdout


def test_a_failed_wave_reports_its_exit_code(tmp_path):
    list_file, env = _setup(tmp_path, "exit 3\n")
    r = _run(list_file, env)
    assert r.returncode == 3 and "wave FAILED rc=3" in r.stdout


def test_dry_run_checks_inputs_and_runs_nothing(tmp_path):
    list_file, env = _setup(tmp_path, "touch $ROOT/ran\n")
    r = _run(list_file, env, "--dry-run")
    assert r.returncode == 0 and "dry run ok: quinoline" in r.stdout
    assert not (tmp_path / "probes" / "ran").exists()
    list_file.write_text("quinoline|/no/such/geometry.json|2|8|10000\n", encoding="utf-8", newline="\n")
    r = _run(list_file, env, "--dry-run")
    assert r.returncode == 2 and "has no geometry" in r.stdout
