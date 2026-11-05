"""probes/e8_cc_hessian_fd.py writes pyscf's own log when given a stream (TASKS 184): the CCSD(T) gradient is the same with and without it, the
stream receives pyscf's lines, and RunLog opens <out>/pyscf.log beside e8_fd.log and closes both."""
from __future__ import annotations

import io
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes"))
pytest.importorskip("pyscf")
E = pytest.importorskip("e8_cc_hessian_fd")

SYMBOLS = ["O", "H", "H"]
X = np.array([[0.0, 0.0, 0.2217], [0.0, 1.4309, -0.8867], [0.0, -1.4309, -0.8867]])
SETTINGS = E.CCSettings("sto-3g", 1, 0, 0, 2000)
# 'The same' to the noise of the iterative CCSD and lambda solves (OpenMP summation order): 2.1e-12 a.u. measured on this gradient; a finite-
# difference row divides it by 0.01 bohr, far below the Hessian's 1e-5 pair checks.
THREAD_NOISE = 1e-10


def test_the_log_stream_changes_nothing_in_the_gradient():
    quiet = E.gradient(SYMBOLS, X, SETTINGS, lambda s: None)
    stream = io.StringIO()
    logged = E.gradient(SYMBOLS, X, SETTINGS, lambda s: None, lib_log=stream)
    assert abs(logged[0] - quiet[0]) < THREAD_NOISE and np.abs(logged[1] - quiet[1]).max() < THREAD_NOISE
    assert "CCSD" in stream.getvalue()


def test_runlog_opens_and_closes_the_pyscf_log(tmp_path):
    with E.RunLog(str(tmp_path)) as log:
        log("a line")
        log.lib.write("pyscf\n")
    assert log.fh.closed and log.lib.closed
    assert (tmp_path / "pyscf.log").read_text(encoding="utf-8") == "pyscf\n"
    assert "a line" in (tmp_path / "e8_fd.log").read_text()
