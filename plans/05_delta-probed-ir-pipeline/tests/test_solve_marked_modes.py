"""probes/solve_marked_modes.py (TASKS 209 stage 1) on synthetic labels: the block's constants are read from the force field, a block
that does not cover the breakdown gives no corrected fundamental, an unbounded block is refused with its reason, and a label written
before the domain check is refused outright."""
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "probes"))
sys.path.insert(0, str(ROOT / "src"))
import solve_marked_modes as S  # noqa: E402


def _report(n, cubic=None, quartic=None):
    p3, p4 = np.zeros((n, n, n)), np.zeros((n, n))
    for (i, j, k), v in (cubic or {}).items():
        p3[i, j, k] = v
    for (i, j), v in (quartic or {}).items():
        p4[i, j] = p4[j, i] = v
    return {"phi_ijk": p3, "phi_iijj_sym": p4}


def _label(omega, nu, marked, diagnostics=None):
    return {"id": "m", "omega": list(omega), "nu_gvpt2": list(nu),
            "vpt2_domain": {"marked": list(marked), "strain_max": 0.10, "partner_max": 0.10,
                            "diagnostics": diagnostics or [{"mode": i, "partner": 0, "partner_share": 0.02} for i in marked]}}


def test_the_block_reads_its_own_constants():
    report = _report(3, cubic={(1, 1, 1): 40.0}, quartic={(1, 1): 90.0, (0, 1): 7.0})
    assert S.block_constants(report, 1) == {3: 40.0, 4: 90.0}
    assert S.block_constants(report, 2) == {3: 0.0, 4: 0.0}


def test_a_covered_block_gives_a_corrected_fundamental():
    # omega 1000, quartic 80: the block's own second order is 1000 + 10 = 1010, and VPT2 puts only 4 cm-1 outside it
    report = _report(2, quartic={(1, 1): 80.0})
    res = S.solve_label(_label([500.0, 1000.0], [505.0, 1014.0], [1]), report)
    row = res["modes"][0]
    assert row["solved"] and row["covered"] and row["outside_cm"] == pytest.approx(4.0)
    assert row["block_exact_cm"] == pytest.approx(1010.0, abs=0.5) and row["correction_cm"] == pytest.approx(0.0, abs=0.5)
    assert row["nu_corrected_cm"] == pytest.approx(1014.0, abs=0.5)
    assert "1 of 1 marked mode(s) have a corrected fundamental" in "\n".join(S.report_lines(res))


def test_a_block_that_does_not_cover_the_breakdown_gives_no_number():
    # the quartic puts +203 cm-1 in the block while VPT2's fundamental sits far below: the two nearly cancel
    report = _report(2, quartic={(1, 1): 3254.9})
    res = S.solve_label(_label([500.0, 564.49], [505.0, 658.44], [1]), report)
    row = res["modes"][0]
    assert row["solved"] and not row["covered"] and "nu_corrected_cm" not in row
    assert row["outside_cm"] == pytest.approx(658.44 - (564.49 + 3254.9 / 8.0), abs=1e-6)
    assert "does not cover the breakdown" in row["reason"]
    assert "0 of 1 marked mode(s) have a corrected fundamental" in "\n".join(S.report_lines(res))


def test_an_unbounded_block_is_refused_with_its_reason():
    report = _report(2, quartic={(1, 1): -400.0})
    row = S.solve_label(_label([500.0, 900.0], [505.0, 880.0], [1]), report)["modes"][0]
    assert not row["solved"] and "unbounded below" in row["reason"] and "nu_corrected_cm" not in row


def test_a_label_from_before_the_domain_check_is_refused():
    with pytest.raises(ValueError, match="no vpt2_domain record"):
        S.solve_label({"id": "m", "omega": [500.0], "nu_gvpt2": [505.0]}, _report(1))


def test_a_label_with_nothing_marked_reads_as_an_empty_table():
    res = S.solve_label(_label([500.0], [505.0], []), _report(1))
    assert res["modes"] == [] and "0 of 0 marked mode(s)" in "\n".join(S.report_lines(res))
