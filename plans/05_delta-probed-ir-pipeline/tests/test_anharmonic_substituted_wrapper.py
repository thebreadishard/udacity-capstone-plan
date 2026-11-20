"""probes/anharmonic_substituted.sh and its two run specs (TASKS 211, the measurement on a substituted molecule): what the
wrapper hands the runners inside WSL, from wherever it is started. Every wrapper call carries `--show-command`, which prints
what would be started and starts nothing, so no test reaches WSL and none computes anything.
"""
from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import SHELL_HANG_GUARD_S

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
import g_label_tools_check as TC  # noqa: E402

BASH = shutil.which("bash")
pytestmark = pytest.mark.skipif(BASH is None, reason="bash not available")

FOLDER = "probes/results_m1/anharmonic_step_substituted_2026-11-20"
START_A = f"{FOLDER}/second_minimum/G"                                               # tracked: the wrapper refuses a missing start
START_B = "modules/05_support_predictor/corpus/molecules/B_3100da3761/geometry.json"
SPECS = {"benzonitrile_xtb_second_field_2026-11-20": ("second-field", START_A, f"{FOLDER}/second_field"),
         "benzonitrile_g_label_2026-11-20": ("g-label", START_B, f"{FOLDER}/g_label")}
ON_WINDOWS = pytest.mark.skipif(os.name != "nt", reason="a drive path and an inherited Windows-style PWD exist under Git Bash only")


def wrapper(*args: str, cwd: Path | None = None, script: str | None = None, **env: str) -> subprocess.CompletedProcess:
    clean = {k: v for k, v in os.environ.items() if k not in ("THREADS", "CAP_MB", "PLAN_HOST_KERNEL")}
    return subprocess.run([BASH, script or (PLAN / "probes" / "anharmonic_substituted.sh").as_posix(), *args], cwd=cwd, env=clean | env,
                          capture_output=True, text=True, encoding="utf-8", timeout=SHELL_HANG_GUARD_S, check=False)


def shown(*args: str, **env: str) -> str:
    res = wrapper(*args, "--show-command", **env)
    assert res.returncode == 0, res.stdout + res.stderr
    return res.stdout.strip()


def need_start(start: str) -> None:
    if not (PLAN / start).exists():
        pytest.skip(f"data not present: {start}")


def test_the_second_field_is_the_pipelines_runner_under_its_cap() -> None:
    out = shown("second-field", "benzonitrile", START_A, f"{FOLDER}/second_field")
    assert out.startswith("(ASM) cap 1536 MB: export PYTHONUNBUFFERED=1; cd ")
    assert out.endswith(f"bash probes/wsl_capped.sh 1536 -- bash probes/xtb_field_for_step.sh benzonitrile {START_A} {FOLDER}/second_field")
    assert "PYSCF_MAX_MEMORY" not in out


def test_the_g_label_is_its_runner_with_the_threads_and_half_the_cap_for_pyscf() -> None:
    need_start(START_B)
    out = shown("g-label", "benzonitrile", START_B, f"{FOLDER}/g_label")
    assert "cap 4096 MB" in out and "PYSCF_MAX_MEMORY=2048" in out
    assert out.endswith(f"bash probes/wsl_capped.sh 4096 -- bash probes/g_label_for_step.sh benzonitrile {START_B} {FOLDER}/g_label 4")
    out = shown("g-label", "benzonitrile", START_B, f"{FOLDER}/g_label", "--dry-run", CAP_MB="3000", THREADS="2")
    assert "PYSCF_MAX_MEMORY=1500" in out and out.endswith("/g_label 2 --dry-run") and "wsl_capped.sh 3000 --" in out


@pytest.mark.parametrize("args", [("third-field", "benzonitrile", START_A, "out"), ("second-field", "benzo nitrile", START_A, "out"),
                                  ("second-field", "benzonitrile", START_A, "out", "--dryrun"), ("second-field", "benzonitrile", START_A),
                                  ("second-field", "benzonitrile", "--dry-run", "out")])
def test_what_the_wrapper_does_not_know_is_refused_with_its_usage(args: tuple[str, ...]) -> None:
    """Also a path left out: the option that follows would be taken for the out dir, and the run would start."""
    res = wrapper(*args, "--show-command")
    assert res.returncode == 2 and "usage:" in res.stdout


def test_a_cap_that_is_not_a_number_is_refused() -> None:
    res = wrapper("second-field", "benzonitrile", START_A, "out", "--show-command", CAP_MB="1.5G")
    assert res.returncode == 2 and "whole numbers" in res.stdout


@pytest.mark.parametrize(("part", "start"), [("second-field", f"{FOLDER}/no_such_minimum"), ("g-label", "no_such_geometry.json")])
def test_a_missing_start_stops_before_anything_starts(part: str, start: str) -> None:
    res = wrapper(part, "benzonitrile", start, "out", "--show-command")
    assert res.returncode == 1 and "STOPPED" in res.stdout and "missing" in res.stdout


@ON_WINDOWS
def test_started_with_a_windows_style_pwd_the_wsl_path_is_still_a_mount() -> None:
    """tools/runspec.py starts the wrapper from the spec's workdir with PWD inherited in Windows form; the WSL path must not
    become '/mntC:/…' (20 Nov 2026: probes/low_mode_patch.sh's dry run stopped on it)."""
    workdir = PLAN / FOLDER
    res = wrapper("second-field", "benzonitrile", START_A, f"{FOLDER}/second_field", "--show-command", cwd=workdir,
                  script="../../anharmonic_substituted.sh", PWD=workdir.as_posix())
    assert res.returncode == 0, res.stdout + res.stderr
    assert "cd /mnt/" in res.stdout and "/mntC:" not in res.stdout and "C:/" not in res.stdout


def test_only_git_bash_turns_a_drive_path_into_a_wsl_mount() -> None:
    plan = subprocess.run([BASH, "-c", 'cd -P "$1" && pwd -P', "_", PLAN.as_posix()], capture_output=True, text=True, encoding="utf-8",
                          timeout=SHELL_HANG_GUARD_S, check=True).stdout.strip()
    args = ("second-field", "benzonitrile", START_A, "out")
    assert f"; cd {plan} && " in shown(*args, PLAN_HOST_KERNEL="Linux")
    if os.name == "nt":                     # only there is the plan folder a drive path that the Git Bash branch can mount
        assert f"; cd /mnt{plan} && " in shown(*args, PLAN_HOST_KERNEL="MINGW64_NT-10.0-26200")


@pytest.mark.parametrize("name", sorted(SPECS))
def test_the_run_specs_start_the_wrapper_as_registered(name: str) -> None:
    part, start, out = SPECS[name]
    need_start(start)
    spec = json.loads((PLAN / "probes" / "runspecs" / f"{name}.json").read_text(encoding="utf-8"))
    words = shlex.split(spec["command"])
    cap = words[1].removeprefix("CAP_MB=")
    assert spec["name"] == name and spec["workdir"] == FOLDER and spec["host"] == "laptop" and spec["threads"] == 4
    assert words[0] == "env" and words[1].startswith("CAP_MB=") and words[-6:] == ["bash", "../../anharmonic_substituted.sh", part, "benzonitrile", start, out]
    assert spec["memory"]["peak_gb"] == pytest.approx(int(cap) / 1024, abs=0.1) and spec["memory"]["peak_gb"] <= 5.0
    assert not ("m08.pipeline" in spec["command"] or "--anharmonic-minutes" in spec["command"])       # neither starts the pipeline
    env = dict(w.split("=", 1) for w in words[1:-6])
    said = shown(*words[-4:], *shlex.split(spec["dry_run_args"]), **env)
    assert f"wsl_capped.sh {cap} --" in said and said.endswith("--dry-run")
    if spec["progress"].get("heartbeat_glob"):
        assert spec["progress"]["heartbeat_glob"] == out.removeprefix(FOLDER + "/") + "/g/benzonitrile/G/*/pyscf.log"


# --- the runner inside WSL: what it refuses before it starts anything, and its dry run's check ------------------------------------


@pytest.mark.parametrize("args", [("benzonitrile", "geometry.json", "out"), ("benzonitrile", "geometry.json", "out", "four"),
                                  ("benzonitrile", "geometry.json", "out", "4", "--dryrun")])
def test_the_label_runner_refuses_a_wrong_call_with_its_usage(args: tuple[str, ...]) -> None:
    res = wrapper(*args, script=(PLAN / "probes" / "g_label_for_step.sh").as_posix())
    assert res.returncode == 2 and "usage:" in res.stdout


def test_the_dry_runs_check_counts_the_hessians_of_a_start_geometry(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    geometry = tmp_path / "geometry.json"
    geometry.write_text(json.dumps({"symbols": ["O", "H", "H"], "coords_bohr": [[0, 0, 0], [0, 1.4, 1.1], [0, -1.4, 1.1]]}), encoding="utf-8")
    assert TC.atoms_of(geometry) == 3
    geometry.write_text(json.dumps({"symbols": ["O", "H", "H"], "geometry": [0.0] * 9}), encoding="utf-8")
    with pytest.raises(SystemExit, match="no coords_bohr"):
        TC.atoms_of(geometry)
    geometry.write_text(json.dumps({"symbols": ["O", "H", "H"], "coords_bohr": [0.0] * 8}), encoding="utf-8")
    with pytest.raises(SystemExit, match="3 symbols and 8 coordinate entries"):
        TC.atoms_of(geometry)
    assert TC.versions(("json", "numpy")).startswith("json ")
    with pytest.raises(SystemExit):
        TC.main([])
    capsys.readouterr()
