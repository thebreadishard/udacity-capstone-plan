"""The physical constants the label route and the vibrational arithmetic share, defined once (TASKS 216, 14 November 2026).

Both numbers were written out in some twenty files, and three of them carried 219474.6313632 for the hartree in cm-1 instead of the
219474.6313705 the rest carried. The sweep of TASKS 221 made every file read from here.

Where the two numbers come from, checked against NIST's table on 14 November 2026 (physics.nist.gov/cuu/Constants/Table/allascii.txt,
the 2022 CODATA adjustment) rather than quoted from memory:

  carried                        CODATA 2022                              relative   at 3000 cm-1
  AMU2AU     1822.888486209      1822.888486278 = 1 / 5.485799090441e-4   3.8e-11    --
  HARTREE2CM 219474.6313705      219474.6313631 = 2.1947463136314e7 m-1   3.4e-11    1.0e-7 cm-1

So what we carry is one adjustment behind, and the 219474.6313632 that three files held was in fact the better value - it sits
2.7e-13 from the 2022 one. The error either way is a ten-thousandth of a thousandth of the 3 cm-1 we license, so no number we have
printed moves; adopting the 2022 values is still the right thing, and it waits for the next regeneration of the rung C pin, which
reproduces a training run to the bit and would have to be rewritten with it (TASKS 224).

tests/test_constants.py pins both values and their distance from the CODATA table, so neither can drift unnoticed and the gap above
cannot grow silently.
"""
from __future__ import annotations

AMU2AU = 1822.888486209          # electron masses per atomic mass unit
HARTREE2CM = 219474.6313705      # cm-1 per hartree
