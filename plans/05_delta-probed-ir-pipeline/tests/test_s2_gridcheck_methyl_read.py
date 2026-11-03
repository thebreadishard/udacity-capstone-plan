"""probes/s2_gridcheck_methyl_read.py on synthetic records: the control, the three readings and their boundaries."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes"))
import s2_gridcheck_methyl_read as R


def rec(coarse: float, fine: float) -> dict:
    return {"max_disagreement": {"coarse": coarse, "fine": fine}}


@pytest.mark.parametrize(("coarse", "fine", "reading"), [
    (5.63, 1.0, "GRID NOISE"),
    (5.63, 2.815, "GRID NOISE"),            # exactly half: noise
    (5.63, 3.5, "MIXED"),
    (5.63, 4.2225, "LARGE AMPLITUDE"),      # exactly three quarters: amplitude
    (5.63, 6.0, "LARGE AMPLITUDE"),         # the fine grid worse: amplitude, not noise
    (5.70, 1.0, "CONTROL FAILED"),          # the coarse Hessians do not reproduce S2
])
def test_readings(coarse, fine, reading):
    assert R.verdict(rec(coarse, fine))[0].startswith(reading)
