"""probes/frame_proof_142a_read.py on synthetic records: the registered rule holds only when modes 5 and 11 move beyond their truncation
and the floor, mode 10 stays, and mode 5 moves more than mode 11."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes"))
import frame_proof_142a_read as R


def run(phi: dict[str, float], trunc: dict[str, float] | None = None) -> dict:
    trunc = trunc or {}
    return {"modes": {m: {"all_steps": {"omega": 400.0, "phi_iiii": p}, "one_fewer": {"phi_iiii": p + trunc.get(m, 0.2)}, "odd_max": 1e-6}
                      for m, p in phi.items()}}


LAB = {"5": 265.0, "10": 933.0, "11": 10.4}


@pytest.mark.parametrize(("charge", "trunc", "holds"), [
    ({"5": 850.0, "10": 933.3, "11": 75.0}, None, True),                       # the lead: big moves on 5 and 11, mode 10 still
    ({"5": 850.0, "10": 940.0, "11": 75.0}, None, False),                      # mode 10 moves too: not the turn
    ({"5": 280.0, "10": 933.0, "11": 175.0}, None, False),                     # mode 11 moves more than mode 5: not the turn's order
    ({"5": 850.0, "10": 933.0, "11": 75.0}, {"11": 30.0}, False),              # mode 11's move inside 5x its truncation
    ({"5": 268.0, "10": 933.0, "11": 12.0}, {"5": 0.1, "11": 0.1}, False),     # moves under the 5 cm⁻¹ floor
    ({"5": 1.0e10, "10": 933.0, "11": 75.0}, None, True),                      # a numerically wild value still reads, it does not crash
])
def test_rule(charge, trunc, holds):
    _, verdict = R.verdict(run(LAB, trunc), run(charge))
    assert verdict is holds
