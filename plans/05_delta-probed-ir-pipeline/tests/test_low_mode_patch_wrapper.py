"""probes/low_mode_patch.sh: what it hands the runner (TASKS 218). The measurement of the threshold needs `--below` and `--step`, which
the wrapper used to drop; the three run specs of the repair must go on meaning what they meant. Every call here carries
`--show-command`, which prints the runner's arguments and starts nothing, so no test reaches WSL.
"""
from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
from pathlib import Path

import pytest

from conftest import SHELL_HANG_GUARD_S

PLAN = Path(__file__).resolve().parents[1]
BASH = shutil.which("bash")
pytestmark = pytest.mark.skipif(BASH is None, reason="bash not available")

IDS = "probes/results_m1/low_mode_patch_2026-11-13/ids_check.txt"    # a tracked ids file: the wrapper refuses a missing one
OUT = "probes/results_m1/somewhere_new"
REPAIR_SPECS = ("low_mode_patch_check", "low_mode_patch_corpus", "low_mode_patch_fd222")


def show(*args: str, **env: str) -> subprocess.CompletedProcess:
    """The wrapper with --show-command appended: it prints the runner's arguments and exits."""
    clean = {k: v for k, v in os.environ.items() if k not in ("THREADS", "CAP_MB", "PYSCF_MB")}
    return subprocess.run([BASH, (PLAN / "probes" / "low_mode_patch.sh").as_posix(), *args, "--show-command"], env=clean | env,
                          capture_output=True, text=True, encoding="utf-8", timeout=SHELL_HANG_GUARD_S, check=False)


def runner_args(*args: str, **env: str) -> list[str]:
    res = show(*args, **env)
    assert res.returncode == 0, res.stdout + res.stderr
    return res.stdout.split("python ", 1)[1].split()


def test_without_options_the_runner_gets_its_defaults() -> None:
    args = runner_args(IDS, OUT)
    assert args[0] == "probes/low_mode_patch_run.py"
    assert args[1].endswith("/modules/05_support_predictor/corpus/molecules") and args[2].endswith("/" + OUT)
    assert args[3:] == ["--ids", args[4], "--threads", "8", "--max-memory", "2048"] and args[4].endswith("/" + IDS)


def test_below_and_step_reach_the_runner_in_any_order_with_the_dry_run() -> None:
    assert runner_args(IDS, OUT, "--below", "60")[-2:] == ["--below", "60"]
    assert runner_args(IDS, OUT, "--step", "0.02", "--below", "100")[-4:] == ["--step", "0.02", "--below", "100"]
    assert runner_args(IDS, OUT, "--below", "60", "--dry-run")[-3:] == ["--below", "60", "--dry-run"]
    assert runner_args(IDS, OUT, "--dry-run")[-1] == "--dry-run"


def test_threads_and_cap_come_from_the_environment() -> None:
    args = runner_args(IDS, OUT, "--below", "60", THREADS="4", CAP_MB="6000")
    assert args[args.index("--threads") + 1] == "4" and args[args.index("--max-memory") + 1] == "3000"
    assert "cap 6000 MB" in show(IDS, OUT, THREADS="4", CAP_MB="6000").stdout


@pytest.mark.parametrize("extra", [("--bellow", "60"), ("--below",), ("--step",), ("60",)])
def test_an_argument_the_wrapper_does_not_know_is_refused(extra: tuple[str, ...]) -> None:
    res = subprocess.run([BASH, (PLAN / "probes" / "low_mode_patch.sh").as_posix(), IDS, OUT, "--show-command", *extra], capture_output=True,
                         text=True, encoding="utf-8", timeout=SHELL_HANG_GUARD_S, check=False)
    assert res.returncode == 2 and "usage:" in res.stdout


def test_a_missing_ids_file_stops_before_anything_starts() -> None:
    res = show("probes/results_m1/no_such_ids.txt", OUT)
    assert res.returncode == 1 and "STOPPED" in res.stdout


@pytest.mark.parametrize("name", REPAIR_SPECS)
def test_the_repair_run_specs_still_patch_at_the_runners_defaults(name: str) -> None:
    """Their commands name an ids file and an out dir and nothing else, so the runner's own threshold and step apply."""
    spec = json.loads((PLAN / "probes" / "runspecs" / f"{name}.json").read_text(encoding="utf-8"))
    words = shlex.split(spec["command"])
    assert words[:2] == ["bash", "../low_mode_patch.sh"] and len(words) == 4
    args = runner_args(*words[2:])
    assert "--below" not in args and "--step" not in args and args[-2:] == ["--max-memory", "2048"]
    assert runner_args(*words[2:], *shlex.split(spec["dry_run_args"]))[-1] == "--dry-run"


@pytest.mark.parametrize(("name", "extra"), [("low_mode_threshold_sample_2026-11-20", ["--below", "60"]),
                                             ("low_mode_threshold_step02_2026-11-20", ["--below", "60", "--step", "0.02"])])
def test_the_measurement_run_specs_patch_at_their_own_settings_into_their_own_folder(name: str, extra: list[str]) -> None:
    spec = json.loads((PLAN / "probes" / "runspecs" / f"{name}.json").read_text(encoding="utf-8"))
    words = shlex.split(spec["command"])
    assert words[:5] == ["env", "THREADS=4", "CAP_MB=4096", "bash", "../low_mode_patch.sh"] and words[7:] == extra
    assert words[6].startswith("probes/results_m1/low_mode_threshold_2026-11-20/patch_") and spec["threads"] == 4
    assert spec["progress"]["heartbeat_glob"] == words[6].removeprefix("probes/results_m1/") + "/pyscf.log"


def test_a_path_with_a_space_stays_one_argument() -> None:
    """Review finding 10: the runner's arguments are quoted one by one for the shell inside WSL."""
    res = show(IDS, "probes/results_m1/some where", "--below", "60")
    assert res.returncode == 0, res.stdout + res.stderr
    args = shlex.split(res.stdout.split("python ", 1)[1])
    assert args[2].endswith("/probes/results_m1/some where") and args[3] == "--ids" and args[-2:] == ["--below", "60"]


ON_WINDOWS = pytest.mark.skipif(os.name != "nt", reason="a drive path and an inherited Windows-style PWD exist under Git Bash only")


@ON_WINDOWS
def test_started_with_a_windows_style_pwd_the_wsl_path_is_still_a_mount() -> None:
    """The run door starts the wrapper from probes/results_m1 with PWD inherited in Windows form; the WSL path must not become
    '/mntC:/…' (20 Nov 2026: the step check's dry run stopped on it)."""
    workdir = PLAN / "probes" / "results_m1"
    clean = {k: v for k, v in os.environ.items() if not k.startswith("LMP_")}
    res = subprocess.run([BASH, "../low_mode_patch.sh", IDS, OUT, "--show-command"], cwd=workdir, capture_output=True, text=True,
                         encoding="utf-8", env=clean | {"PWD": workdir.as_posix()}, timeout=SHELL_HANG_GUARD_S, check=False)
    assert res.returncode == 0, res.stdout + res.stderr
    assert "/mnt/" in res.stdout and "/mntC:" not in res.stdout and "C:/" not in res.stdout


def test_only_git_bash_turns_a_drive_path_into_a_wsl_mount() -> None:
    """On Linux or inside WSL a path is its own, also one that starts with a one-letter folder such as /a/b."""
    plan = subprocess.run([BASH, "-c", 'cd "$1" && pwd', "_", PLAN.as_posix()], capture_output=True, text=True, encoding="utf-8",
                          timeout=SHELL_HANG_GUARD_S, check=True).stdout.strip()
    assert runner_args(IDS, OUT, LMP_HOST_KERNEL="Linux")[2] == f"{plan}/{OUT}"
    if os.name == "nt":                     # only there is the plan folder a drive path that the Git Bash branch can mount
        assert runner_args(IDS, OUT, LMP_HOST_KERNEL="MINGW64_NT-10.0-26200")[2] == f"/mnt{plan}/{OUT}"
