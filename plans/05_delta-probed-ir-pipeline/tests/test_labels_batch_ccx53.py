"""probes/labels_batch_ccx53.sh: waits for its condition, optimises what has no finished result, labels what lacks either analytic Hessian,
names a failure and goes on, and --dry-run only reports. Stand-ins replace psi4 and pyscf; the real workers are never called."""
import os
import shutil
import subprocess
import threading
import time
from pathlib import Path

import pytest

PLAN = Path(__file__).resolve().parents[1]
BASH = shutil.which("bash")
pytestmark = pytest.mark.skipif(BASH is None, reason="bash not available")
A, B = "X_aaaaaaaaaa", "X_bbbbbbbbbb"


def _stub(path: Path, body: str) -> str:
    path.write_text("#!/usr/bin/env bash\n" + body, encoding="utf-8", newline="\n")
    path.chmod(0o755)
    return path.as_posix()


def _setup(tmp_path, ids=(A, B), optimised=(B,), fail: str = "", ready: bool = True) -> dict:
    batch = tmp_path / "batch"
    for i in ids:
        (batch / "molecules" / i).mkdir(parents=True)
        (batch / "molecules" / i / "job.json").write_text("{}", encoding="utf-8")
        if i in optimised:
            (batch / "molecules" / i / "result.json").write_text('{"status": "done"}', encoding="utf-8")
            (batch / "molecules" / i / "geometry.json").write_text("{}", encoding="utf-8")
    (batch / "ids.txt").write_text("# header\n" + "".join(f"{i}\n" for i in ids), encoding="utf-8", newline="\n")
    code = tmp_path / "code"
    code.mkdir()
    for name in ("psi4_worker.py", "analytic_hessians.py"):
        (code / name).write_text("", encoding="utf-8")
    # psi4 stand-in: '<worker> molecules/<id>/job.json' -> a finished result and an optimised geometry
    qc = _stub(tmp_path / "qc.sh", 'd=$(dirname "$2"); echo \'{"status": "done"}\' > "$d/result.json"; echo "{}" > "$d/geometry.json"\n')
    # pyscf stand-in: 'analytic_hessians.py <dir> ...' -> both Hessians, or a failure for the named id
    qc05 = _stub(tmp_path / "qc05.sh", f'echo "$*" >> "{(tmp_path / "qc05_args.log").as_posix()}"\n'
                                       f'd=$2; case "$(basename "$d")" in {fail or "none"}) exit 1 ;; esac\n'
                                       'touch "$d/hessian_b3lyp_analytic.npz" "$d/hessian_wb97x_analytic.npz"\n')
    (tmp_path / "wait.log").write_text("READY\n" if ready else "busy\n", encoding="utf-8", newline="\n")
    return dict(os.environ, QC=qc, QC05=qc05, CODE=code.as_posix(), QC_TMP=(tmp_path / "qc_tmp").as_posix(), WAIT_S="1")


def _run(tmp_path, env: dict, *extra: str, wait_log: str = "", wait_re: str = "^READY") -> subprocess.CompletedProcess:
    args = [(tmp_path / "batch").as_posix(), "T", wait_log or (tmp_path / "wait.log").as_posix(), wait_re, *extra]
    return subprocess.run([BASH, (PLAN / "probes" / "labels_batch_ccx53.sh").as_posix(), *args], env=env,
                          capture_output=True, encoding="utf-8", timeout=120, check=False)


def test_optimises_what_is_not_done_and_labels_both(tmp_path):
    res = _run(tmp_path, _setup(tmp_path))
    assert res.returncode == 0, res.stdout + res.stderr
    assert "=== (T) armed: 2 molecules (0 without a job file)" in res.stdout and "=== (T) start: the wait condition is met" in res.stdout
    assert f"  {A} optimised " in res.stdout and f"  {B} optimised already" in res.stdout
    assert f"  {A} labelled " in res.stdout and f"  {B} labelled " in res.stdout
    assert res.stdout.index("=== (T) optimisations") < res.stdout.index("=== (T) labels") < res.stdout.index("=== (T) all done")


def test_labelled_molecules_are_skipped(tmp_path):
    env = _setup(tmp_path)
    for name in ("hessian_b3lyp_analytic.npz", "hessian_wb97x_analytic.npz"):
        (tmp_path / "batch" / "molecules" / B / name).write_bytes(b"")
    res = _run(tmp_path, env)
    assert f"  {B} labelled already" in res.stdout


def test_a_failed_label_is_named_and_the_others_go_on(tmp_path):
    res = _run(tmp_path, _setup(tmp_path, fail=A))
    assert f"  {A} LABELS FAILED " in res.stdout and f"  {B} labelled " in res.stdout


def test_a_missing_job_file_stops_before_any_work(tmp_path):
    env = _setup(tmp_path)
    (tmp_path / "batch" / "molecules" / A / "job.json").unlink()
    res = _run(tmp_path, env)
    assert res.returncode != 0 and "=== (T) STOPPED: 1 job files missing" in res.stdout and "optimisations" not in res.stdout


def test_it_waits_for_its_condition(tmp_path):
    env = _setup(tmp_path, ready=False)
    log = tmp_path / "wait.log"
    threading.Thread(target=lambda: (time.sleep(2.5), log.write_text("READY\n", encoding="utf-8")), daemon=True).start()
    t0 = time.monotonic()
    res = _run(tmp_path, env)
    assert res.returncode == 0 and time.monotonic() - t0 > 2 and "=== (T) start" in res.stdout


def test_dry_run_reports_only(tmp_path):
    env = _setup(tmp_path, ready=False)
    res = _run(tmp_path, env, "--dry-run")
    assert res.returncode == 0 and "=== (T) dry run: wait condition not met yet" in res.stdout
    assert not (tmp_path / "batch" / "molecules" / A / "result.json").exists()


def _capped(tmp_path, killed: str) -> dict:
    """The cap wrapper stand-in drops '<cap> -- /usr/bin/time -f <fmt>' (systemd is not here) and records the cap; the oom check names
    the given id killed."""
    capped = _stub(tmp_path / "capped.sh", f'echo "$1" >> "{(tmp_path / "caps.log").as_posix()}"; shift 5; "$@"\n')
    oom = _stub(tmp_path / "oom.sh", f'[ "$OOM_TAG" = T ] && [ "$OOM_JOURNAL" = system ] && [ "$1" = "{killed}" ]\n')
    return {"CAPPED": capped, "OOM_CHECK": oom, "CAP_MB": "64"}


def test_ids_come_from_the_first_column_of_a_tsv_with_crlf(tmp_path):
    env = _setup(tmp_path)
    (tmp_path / "batch" / "ids.txt").write_bytes(f"# id\tnbas\r\n{A}\t303\t28\r\n{B}\t260\t26\r\n".encode())
    res = _run(tmp_path, env)
    assert res.returncode == 0, res.stdout + res.stderr
    assert f"  {A} labelled " in res.stdout and f"  {B} labelled " in res.stdout


def test_lanes_threads_and_label_arguments_reach_the_worker(tmp_path):
    env = _setup(tmp_path) | {"LANES": "2", "THREADS": "3", "LABEL_ARGS": "--charge 1 --spin 1 --reuse-existing"}
    res = _run(tmp_path, env)
    assert "2 lanes × 3 threads" in res.stdout and "label arguments '--charge 1 --spin 1 --reuse-existing'" in res.stdout
    calls = (tmp_path / "qc05_args.log").read_text(encoding="utf-8").splitlines()
    assert len(calls) == 2 and all(c.endswith("--threads 3 --charge 1 --spin 1 --reuse-existing") for c in calls)


def test_it_waits_for_every_log_of_the_glob(tmp_path):
    env = _setup(tmp_path) | {"WAIT_COUNT": "3"}
    for n in range(3):
        (tmp_path / f"lane_{n}.log").write_text(f"LANE {n} DONE\n" if n < 2 else "running\n", encoding="utf-8", newline="\n")
    last = tmp_path / "lane_2.log"
    threading.Thread(target=lambda: (time.sleep(2.5), last.write_text("LANE 2 DONE\n", encoding="utf-8")), daemon=True).start()
    t0 = time.monotonic()
    res = _run(tmp_path, env, wait_log="../lane_[0-2].log", wait_re="LANE [0-2] DONE")      # the runner works from the batch folder
    assert res.returncode == 0 and time.monotonic() - t0 > 2 and "=== (T) start" in res.stdout


def test_a_kill_at_the_cap_and_a_plain_failure_are_told_apart_and_counted(tmp_path):
    ids = (A, B, "X_cccccccccc")
    env = _setup(tmp_path, ids=ids, optimised=ids, fail=f"{A}|{B}") | _capped(tmp_path, killed=A)
    res = _run(tmp_path, env)
    assert f"  {A} KILLED at the cap of 64 MB " in res.stdout and f"  {B} LABELS FAILED " in res.stdout
    assert "  X_cccccccccc labelled " in res.stdout and "cap 64 MB" in res.stdout
    assert (tmp_path / "caps.log").read_text(encoding="utf-8").split() == ["64"] * 3
    assert "=== (T) all done: 2 failures or skips" in res.stdout and res.returncode != 0


def test_a_failure_without_a_cap_is_counted_and_fails_the_run(tmp_path):
    res = _run(tmp_path, _setup(tmp_path, fail=B))
    assert "=== (T) all done: 1 failures or skips" in res.stdout and res.returncode != 0


def test_a_clean_run_counts_zero_and_exits_zero(tmp_path):
    res = _run(tmp_path, _setup(tmp_path))
    assert "=== (T) all done: 0 failures or skips" in res.stdout and res.returncode == 0


@pytest.mark.parametrize(("setting", "value", "reason"), [
    ("LANES", "0", "LANES must be a positive integer"),
    ("THREADS", "x", "THREADS must be a positive integer"),
    ("CAP_MB", "26g", "CAP_MB must be a positive integer"),
])
def test_a_bad_setting_is_refused_before_the_wait(tmp_path, setting, value, reason):
    res = _run(tmp_path, _setup(tmp_path, ready=False) | {setting: value})
    assert res.returncode != 0 and f"=== (T) STOPPED: {reason}" in res.stdout and "armed" not in res.stdout


def test_a_cap_without_its_wrapper_is_refused(tmp_path):
    env = _setup(tmp_path) | {"CAP_MB": "64", "CAPPED": (tmp_path / "nowhere.sh").as_posix()}
    res = _run(tmp_path, env)
    assert res.returncode != 0 and "nowhere.sh missing (CAP_MB is set)" in res.stdout


def test_no_psi4_is_needed_when_every_molecule_is_optimised(tmp_path):
    env = _setup(tmp_path, optimised=(A, B)) | {"QC": (tmp_path / "no_psi4").as_posix()}
    (tmp_path / "code" / "psi4_worker.py").unlink()
    res = _run(tmp_path, env)
    assert res.returncode == 0, res.stdout + res.stderr
    assert "0 to optimise, 2 to label" in res.stdout and f"  {A} optimised already" in res.stdout


def test_an_ids_file_picks_its_molecules_from_a_shared_folder(tmp_path):
    env = _setup(tmp_path, optimised=(A, B)) | {"IDS_FILE": "ids_b.txt"}
    (tmp_path / "batch" / "ids_b.txt").write_text(f"{B}\n", encoding="utf-8", newline="\n")
    res = _run(tmp_path, env)
    assert res.returncode == 0, res.stdout + res.stderr
    assert "armed: 1 molecules" in res.stdout and "ids from ids_b.txt" in res.stdout
    assert f"  {B} labelled " in res.stdout and A not in res.stdout


def test_a_missing_ids_file_is_refused(tmp_path):
    res = _run(tmp_path, _setup(tmp_path) | {"IDS_FILE": "nowhere.txt"})
    assert res.returncode != 0 and "=== (T) STOPPED: no ids file nowhere.txt" in res.stdout
