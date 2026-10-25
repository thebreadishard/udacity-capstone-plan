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
    qc05 = _stub(tmp_path / "qc05.sh", f'd=$2; case "$(basename "$d")" in {fail or "none"}) exit 1 ;; esac\n'
                                       'touch "$d/hessian_b3lyp_analytic.npz" "$d/hessian_wb97x_analytic.npz"\n')
    (tmp_path / "wait.log").write_text("READY\n" if ready else "busy\n", encoding="utf-8", newline="\n")
    return dict(os.environ, QC=qc, QC05=qc05, CODE=code.as_posix(), QC_TMP=(tmp_path / "qc_tmp").as_posix(), WAIT_S="1")


def _run(tmp_path, env: dict, *extra: str) -> subprocess.CompletedProcess:
    args = [(tmp_path / "batch").as_posix(), "T", (tmp_path / "wait.log").as_posix(), "^READY", *extra]
    return subprocess.run([BASH, (PLAN / "probes" / "labels_batch_ccx53.sh").as_posix(), *args], env=env,
                          capture_output=True, text=True, timeout=120, check=False)


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
