"""`probes/deploy_opt_batch.sh --list-files` names a closed, tracked deploy set (21 Nov 2026): a runner that gains an import must not reach
a server without it. The deploy checks the same at run time; this catches it before any server is rented."""
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

PLAN = Path(__file__).resolve().parents[1]
BASH = shutil.which("bash")


@pytest.mark.skipif(BASH is None, reason="needs bash")
def test_opt_batch_deploy_list_is_closed_and_tracked():
    listed = subprocess.run([BASH, "probes/deploy_opt_batch.sh", "--list-files"], cwd=PLAN, capture_output=True, text=True, check=True)
    files = listed.stdout.split()
    assert "probes/labels_batch_ccx53.sh" in files and "modules/05_support_predictor/corpus/psi4_worker.py" in files
    closure = subprocess.run([sys.executable, "tools/deploy_closure.py", *files], cwd=PLAN, capture_output=True, text=True, check=False)
    assert closure.returncode == 0, closure.stdout + closure.stderr
    tracked = subprocess.run(["git", "ls-files", "--error-unmatch", *files], cwd=PLAN, capture_output=True, text=True, check=False)
    assert tracked.returncode == 0, tracked.stderr
