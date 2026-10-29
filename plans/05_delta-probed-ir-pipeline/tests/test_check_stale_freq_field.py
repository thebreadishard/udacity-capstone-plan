"""TASKS 147's check (`probes/check_stale_freq_field.py`): when a stale frequency field could move an imaginary-mode verdict."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes"))
import check_stale_freq_field as C


@pytest.mark.parametrize(("stored", "own", "gap", "expected"), [
    (58.66, 58.68, 0.73, []),                         # A2_13bafae8e0's B3LYP file: far from both bounds
    (10.3, 10.5, 0.5, ["10 cm⁻¹"]),                   # within the gap of the healed bound
    (9.9, 10.1, 0.05, ["10 cm⁻¹"]),                   # the two on either side of it, the gap smaller than the distance
    (-0.2, 0.3, 0.1, ["0 cm⁻¹"]),                     # imaginary stored, real recomputed
])
def test_a_bound_is_at_risk_within_the_gap_or_across_it(stored, own, gap, expected):
    assert C.at_risk(stored, own, gap) == expected
