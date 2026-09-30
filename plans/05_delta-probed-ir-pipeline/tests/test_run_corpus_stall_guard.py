"""run_corpus stall guard (30 Sep 2026): a worker that stops writing is terminated and reported 'stalled'; one that keeps writing runs to its end;
the wall-clock cap reports 'timeout'; molecules with a triple bond get cartesian optimisation coordinates from the start. The fake workers are
tiny python one-liners, so the tests run anywhere in seconds (no psi4)."""
import sys
from pathlib import Path

import pytest

CORPUS = Path(__file__).resolve().parents[1] / "modules" / "05_support_predictor" / "corpus"
sys.path.insert(0, str(CORPUS))
import run_corpus as R  # noqa: E402

PY = sys.executable


def test_stalled_worker_is_terminated(tmp_path):
    cmd = [PY, "-c", "import time; time.sleep(60)"]                      # writes nothing
    out, err, guard = R.run_worker(cmd, tmp_path, stall_s=1.0, max_s=600.0, poll_s=0.5)
    assert guard == "stalled"
    assert not list(tmp_path.glob("*.raw"))                              # the raw capture files are removed after reading


def test_writing_worker_runs_to_the_end(tmp_path):
    code = ("import time, pathlib, sys; p = pathlib.Path(sys.argv[1]) / 'psi4.out'\n"
            "for i in range(6):\n    p.write_text(str(i)); time.sleep(0.4)\nprint('finished')")
    out, err, guard = R.run_worker([PY, "-c", code, str(tmp_path)], tmp_path, stall_s=1.5, max_s=600.0, poll_s=0.5)
    assert guard is None and "finished" in out


def test_wall_clock_cap_reports_timeout(tmp_path):
    code = ("import time, pathlib, sys; p = pathlib.Path(sys.argv[1]) / 'psi4.out'\n"
            "for i in range(100):\n    p.write_text(str(i)); time.sleep(0.2)")
    out, err, guard = R.run_worker([PY, "-c", code, str(tmp_path)], tmp_path, stall_s=600.0, max_s=1.0, poll_s=0.5)
    assert guard == "timeout"


@pytest.mark.parametrize("smiles, retry, expect", [
    ("C#Cc1ccc2ccccc2c1", False, True),       # ethynyl: linear bend → cartesian from the start
    ("N#Cc1ccccc1", False, True),             # nitrile
    ("Cc1ccccc1", False, False),              # no triple bond, first attempt: optking's default coordinates
    ("Cc1ccccc1", True, True),                # any retry of a failed row keeps the 20 Sep behaviour
])
def test_opt_options_for_triple_bonds_and_retries(smiles, retry, expect):
    o = R.opt_options_for({"smiles": smiles}, retry)
    assert (o is not None) == expect
    if o:
        assert o["opt_coordinates"] == "cartesian" and o is not R.RETRY_OPT_OPTIONS   # a copy, never the module constant
