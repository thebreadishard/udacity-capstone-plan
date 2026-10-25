"""probes/cation_ccx53.sh (TASKS 121): it waits for the four label lanes, shares the queue among its lanes, names a molecule killed at the
cap apart from one that failed otherwise, skips finished molecules, and --dry-run only counts. Stand-ins replace systemd, /usr/bin/time and
pyscf; the real analytic_hessians.py is never called."""
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
IDS = ["P3c_aaaaaaaaaa", "P3c_bbbbbbbbbb", "P3c_cccccccccc", "P3c_dddddddddd"]


def _stub(path: Path, body: str) -> str:
    path.write_text("#!/usr/bin/env bash\n" + body, encoding="utf-8", newline="\n")
    path.chmod(0o755)
    return path.as_posix()


def _setup(tmp_path, lanes_done: int = 4, fail: str = "", killed: str = "") -> dict:
    mol = tmp_path / "molecules"
    for i in IDS:
        (mol / i).mkdir(parents=True)
        (mol / i / "geometry.json").write_text("{}", encoding="utf-8")
    (tmp_path / "ids.tsv").write_text("# header\n" + "".join(f"{i}\t300\t28\n" for i in IDS), encoding="utf-8", newline="\n")
    labels = tmp_path / "labels"
    labels.mkdir()
    for n in range(4):
        (labels / f"lane_{n}.log").write_text(f"LANE {n} DONE: x\n" if n < lanes_done else "running\n", encoding="utf-8", newline="\n")
    # the cap wrapper drops '<cap> -- /usr/bin/time -f <fmt>' and runs the rest; the python stand-in writes both Hessians or fails
    capped = _stub(tmp_path / "capped.sh", 'shift 2; shift 3; "$@"\n')
    py = _stub(tmp_path / "py.sh", f'd=$2; id=$(basename "$d"); case "$id" in {fail or "none"}|{killed or "none"}) exit 1 ;; esac\n'
                                     'touch "$d/hessian_wb97x_analytic.npz" "$d/hessian_b3lyp_analytic.npz"\n')
    oom = _stub(tmp_path / "oom.sh", f'[ "$1" = "{killed or "none"}" ]\n')
    return dict(os.environ, MOL=mol.as_posix(), LABELS=labels.as_posix(), WORK=tmp_path.as_posix(), QC_TMP=(tmp_path / "qc").as_posix(),
                PY=py, CAPPED=capped, OOM_CHECK=oom, LANES="2", THREADS="1", WAIT_S="1", BEAT_S="3600")


def _run(tmp_path, env: dict, *extra: str) -> subprocess.CompletedProcess:
    return subprocess.run([BASH, (PLAN / "probes" / "cation_ccx53.sh").as_posix(), (tmp_path / "ids.tsv").as_posix(), *extra], env=env,
                          capture_output=True, text=True, timeout=120, check=False)


def test_all_molecules_are_shared_among_the_lanes_and_the_run_ends_clean(tmp_path):
    res = _run(tmp_path, _setup(tmp_path))
    assert res.returncode == 0, res.stdout + res.stderr
    assert all(f"(CX) {i} done" in res.stdout for i in IDS)
    assert "(CX) lane 0 finished" in res.stdout and "(CX) lane 1 finished" in res.stdout
    assert "=== (CX) run done: 4 of 4" in res.stdout


def test_a_kill_at_the_cap_and_a_plain_failure_are_told_apart(tmp_path):
    res = _run(tmp_path, _setup(tmp_path, fail=IDS[1], killed=IDS[2]))
    assert f"(CX) {IDS[2]} KILLED at the cap" in res.stdout and f"(CX) {IDS[1]} FAILED" in res.stdout
    assert f"(CX) {IDS[0]} done" in res.stdout and f"(CX) {IDS[3]} done" in res.stdout      # the lanes went on
    assert res.returncode != 0 and "=== (CX) run done: 2 of 4" in res.stdout


def test_finished_molecules_are_skipped(tmp_path):
    env = _setup(tmp_path)
    for name in ("hessian_wb97x_analytic.npz", "hessian_b3lyp_analytic.npz"):
        (tmp_path / "molecules" / IDS[0] / name).write_bytes(b"")
    res = _run(tmp_path, env)
    assert f"(CX) {IDS[0]} skipped" in res.stdout and res.returncode == 0


def test_it_waits_for_the_fourth_label_lane(tmp_path):
    env = _setup(tmp_path, lanes_done=3)
    lane3 = tmp_path / "labels" / "lane_3.log"
    threading.Thread(target=lambda: (time.sleep(2.5), lane3.write_text("LANE 3 DONE: x\n", encoding="utf-8")), daemon=True).start()
    res = _run(tmp_path, env)
    assert "=== (CX) waiting: 3 of 4 label lanes done" in res.stdout
    assert res.stdout.index("waiting") < res.stdout.index("=== (CX) start") and res.returncode == 0


def test_dry_run_counts_only(tmp_path):
    env = _setup(tmp_path, lanes_done=0)
    res = _run(tmp_path, env, "--dry-run")
    assert res.returncode == 0 and "4 cations listed, 4 to compute" in res.stdout
    assert not (tmp_path / "molecules" / IDS[0] / "hessian_wb97x_analytic.npz").exists()
