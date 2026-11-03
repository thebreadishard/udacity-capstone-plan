"""TASKS 169: probes/epoch_repeat_check.py passes a re-run on the same inputs (later epochs may drift) and fails one whose inputs moved."""
import json
import subprocess
import sys
from pathlib import Path

PLAN = Path(__file__).resolve().parents[1]
SCRIPT = PLAN / "probes" / "epoch_repeat_check.py"
OLD_VALS = {1: 0.4041, 10: 0.1319, 200: 0.0412}


def record(epochs: int, **change) -> dict:
    rec = {"pool_ids": ["B_1", "A_2", "A2_3"], "holdout_a": ["A_9"], "holdout_b": ["B_8"], "holdout_s": [], "excluded_ids": [],
           "scaffold_cores": ["fluorene"], "substituted_analytic": ["B_1"], "pair_class_names": ["cc"], "sizes": [750], "seeds": [0, 1, 2],
           "epochs": epochs, "lr": 0.0003, "patience": 20, "date": "x", "seconds": 1.0,
           "curve": {"750": {"n": 750, "per_seed": [{"seed": 2, "inner_val_ids": ["A_2"]}]}}}
    if epochs > 200:
        rec |= {"holdout_twins": "keep", "holdout_twins_dropped": [], "seeds": [2], "weight_decay": 1e-4}   # recorded since chain 35
    return rec | change


def write_run(tmp: Path, name: str, cap: int, vals: dict[int, float], rec: dict) -> Path:
    log = tmp / f"{name}.log"
    lines = [f"    seed 2 epoch {e}/{cap}: loss main 1e-07 aux 0.01 val {v} ({e * 27} s)" for e, v in vals.items()]
    log.write_text("\n".join(["header line", *lines]) + "\n", encoding="utf-8")
    log.with_suffix(".json").write_text(json.dumps(rec), encoding="utf-8")
    return log


def run(old: Path, new: Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), str(old), str(new), "--seed", "2"], capture_output=True, text=True, check=False,
                          encoding="utf-8")


def test_same_inputs_pass_although_later_epochs_drift(tmp_path):
    old = write_run(tmp_path, "old", 200, OLD_VALS, record(200))
    new = write_run(tmp_path, "new", 500, {1: 0.4041, 10: 0.1321, 200: 0.0420, 260: 0.0401}, record(500))
    r = run(old, new)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "REPEAT OK" in r.stdout and "epoch 10: old 0.1319 new 0.1321" in r.stdout


def test_a_moved_pool_fails(tmp_path):
    old = write_run(tmp_path, "old", 200, OLD_VALS, record(200))
    new = write_run(tmp_path, "new", 500, OLD_VALS, record(500, pool_ids=["A_2", "B_1", "A2_3"]))
    r = run(old, new)
    assert r.returncode == 1 and "pool_ids differs" in r.stdout


def test_a_changed_setting_fails(tmp_path):
    old = write_run(tmp_path, "old", 200, OLD_VALS, record(200))
    new = write_run(tmp_path, "new", 500, OLD_VALS, record(500, lr=0.001))
    r = run(old, new)
    assert r.returncode == 1 and "setting lr" in r.stdout


def test_dropped_twins_fail(tmp_path):
    old = write_run(tmp_path, "old", 200, OLD_VALS, record(200))
    new = write_run(tmp_path, "new", 500, OLD_VALS, record(500, holdout_twins="drop", holdout_twins_dropped=["B_1"]))
    r = run(old, new)
    assert r.returncode == 1 and "dropped hold-out twins" in r.stdout


def test_other_inner_validation_fails(tmp_path):
    old = write_run(tmp_path, "old", 200, OLD_VALS, record(200))
    moved = record(500)
    moved["curve"]["750"]["per_seed"][0]["inner_val_ids"] = ["B_1"]
    new = write_run(tmp_path, "new", 500, OLD_VALS, moved)
    r = run(old, new)
    assert r.returncode == 1 and "inner-validation molecules differ" in r.stdout


def test_a_different_first_epoch_fails(tmp_path):
    old = write_run(tmp_path, "old", 200, OLD_VALS, record(200))
    new = write_run(tmp_path, "new", 500, {**OLD_VALS, 1: 0.4100}, record(500))
    r = run(old, new)
    assert r.returncode == 1 and "REPEAT FAILED" in r.stdout


def test_the_same_cap_is_refused(tmp_path):
    old = write_run(tmp_path, "old", 200, OLD_VALS, record(200))
    r = run(old, old)
    assert r.returncode != 0 and "not above the old cap" in r.stderr
