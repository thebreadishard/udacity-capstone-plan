"""The two physical constants the whole plan reads, pinned against their source (TASKS 221, 14 November 2026).

Until today they were written out in some twenty files and one of the copies differed in the eleventh digit, which nobody would have
noticed drifting further. Now there is one definition, and this is the test that says what it is: the exact values we carry, and how
far they sit from NIST's CODATA 2022 table, so that gap cannot grow in silence either.

The CODATA numbers below were read from physics.nist.gov/cuu/Constants/Table/allascii.txt on 14 November 2026 — "electron mass in u"
5.485 799 090 441(97)e-4 and "hartree-inverse meter relationship" 2.194 746 313 6314(24)e7 m^-1.
"""
from __future__ import annotations

import sys
from pathlib import Path

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "modules" / "05_support_predictor" / "corpus"))
import constants as C  # noqa: E402  the path line above must run first

CODATA22_ELECTRON_MASS_IN_U = 5.485799090441e-4
CODATA22_HARTREE_INVERSE_METRE = 2.1947463136314e7
# the carried values are one adjustment behind; the gap costs 1.0e-7 cm-1 at 3000 cm-1, against the 3 cm-1 we license (TASKS 224)
BEHIND_BY = 1e-10


def test_the_carried_values_are_exactly_these():
    assert C.AMU2AU == 1822.888486209
    assert C.HARTREE2CM == 219474.6313705


def test_they_stay_within_a_known_distance_of_the_codata_table():
    amu2au = 1.0 / CODATA22_ELECTRON_MASS_IN_U
    hartree2cm = CODATA22_HARTREE_INVERSE_METRE / 100.0
    assert abs(C.AMU2AU - amu2au) / amu2au < BEHIND_BY
    assert abs(C.HARTREE2CM - hartree2cm) / hartree2cm < BEHIND_BY


def test_the_gap_is_far_below_anything_we_report():
    """A frequency we license to 3 cm-1 cannot feel a constant that is right to the eleventh digit."""
    hartree2cm = CODATA22_HARTREE_INVERSE_METRE / 100.0
    at_3000 = abs(C.HARTREE2CM - hartree2cm) / hartree2cm * 3000.0
    assert at_3000 < 1e-6
