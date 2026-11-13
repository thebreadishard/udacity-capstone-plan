"""dpir.qff.assemble_qff still gives, bit for bit, what it gave before the semi-diagonal quartic tensor was added beside it
(tests/qff_assemble_golden.py, 13 Nov 2026, TASKS 209 stage 2). A new array in the result is an addition; a changed one is a
regression, and every run's labels rest on these."""
import sys
from pathlib import Path

import numpy as np
import pytest

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "src"))
sys.path.insert(0, str(PLAN / "tests"))
from dpir.qff import assemble_qff  # noqa: E402
from qff_assemble_golden import DISP, GOLDEN, PAIRS, inputs, pinned  # noqa: E402


def test_every_pinned_array_comes_back_unchanged():
    if not GOLDEN.exists():
        pytest.skip(f"{GOLDEN} is missing; write it with python tests/qff_assemble_golden.py")
    got = pinned(assemble_qff(*inputs(), DISP, PAIRS))
    with np.load(GOLDEN) as golden:
        assert sorted(golden.files) == sorted(got)
        for name in golden.files:
            np.testing.assert_array_equal(got[name], golden[name], err_msg=f"{name} moved since the force field was pinned")
