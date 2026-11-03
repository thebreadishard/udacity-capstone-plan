"""TASKS 169: probes/epoch_repeat_check.py passes a re-run that repeats the old epochs and fails one whose inputs moved."""
import subprocess
import sys
from pathlib import Path

PLAN = Path(__file__).resolve().parents[1]
SCRIPT = PLAN / "probes" / "epoch_repeat_check.py"


def write_log(path: Path, cap: int, vals: dict[int, float], seed: int = 2) -> Path:
    lines = [f"    seed {seed} epoch {e}/{cap}: loss main 1e-07 aux 0.01 val {v} ({e * 27} s)" for e, v in vals.items()]
    path.write_text("\n".join(["header line", *lines]) + "\n", encoding="utf-8")
    return path


def run(old: Path, new: Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), str(old), str(new), "--seed", "2"], capture_output=True, text=True, check=False)


OLD = {1: 0.4041, 10: 0.1319, 200: 0.0412}


def test_a_repeating_rerun_passes(tmp_path):
    old = write_log(tmp_path / "old.log", 200, OLD)
    new = write_log(tmp_path / "new.log", 300, {**OLD, 210: 0.0405, 300: 0.0399})
    r = run(old, new)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "REPEAT OK" in r.stdout


def test_moved_inputs_fail(tmp_path):
    old = write_log(tmp_path / "old.log", 200, OLD)
    new = write_log(tmp_path / "new.log", 300, {1: 0.4041, 10: 0.1400, 200: 0.0412, 300: 0.0399})
    r = run(old, new)
    assert r.returncode == 1
    assert "REPEAT FAILED" in r.stdout and "epoch 10" in r.stdout


def test_the_same_cap_is_refused(tmp_path):
    old = write_log(tmp_path / "old.log", 200, OLD)
    r = run(old, old)
    assert r.returncode != 0 and "not above the old cap" in r.stderr


def test_a_run_that_stopped_before_the_old_cap_fails(tmp_path):
    old = write_log(tmp_path / "old.log", 200, OLD)
    new = write_log(tmp_path / "new.log", 300, {1: 0.4041, 10: 0.1319})
    r = run(old, new)
    assert r.returncode != 0 and "skips epoch 200" in r.stderr
