"""Module 05's notebook builder: `--check-only` compiles every code cell and leaves the executed notebook alone, so a queued
re-execution can be dry-run beside the stored outputs (TASKS 20)."""
import os
import subprocess
import sys
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "modules" / "05_support_predictor"
NOTEBOOK = MODULE / "notebook" / "deep_learning.ipynb"


def test_check_only_writes_nothing():
    before = NOTEBOOK.stat().st_mtime_ns
    env = {**os.environ, "PYTHONUTF8": "1"}
    done = subprocess.run([sys.executable, "notebook/make_notebook.py", "--check-only"], cwd=MODULE, env=env,
                          capture_output=True, text=True, check=False, timeout=300)
    assert done.returncode == 0, done.stderr
    assert "every code cell compiles; nothing written" in done.stdout
    assert NOTEBOOK.stat().st_mtime_ns == before
    assert not (MODULE / "notebook" / "deep_learning.building.ipynb").exists()
