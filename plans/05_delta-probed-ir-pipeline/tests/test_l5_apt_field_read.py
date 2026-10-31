"""The read of l5_apt_field (`probes/l5_apt_field_read.py`, TASKS 49) on synthetic records before any output of the run: both lines hold;
a field error that misses L4's line at F alone but not after Richardson; a response error in the labels-route APT (line B fails); a grid-
response APT off its sum rule (line A fails); a missing field file refused; the whole read on a folder."""
from __future__ import annotations

import json
import sys

import numpy as np
import pytest

from pin_tools import PLAN

sys.path.insert(0, str(PLAN / "probes"))
import l5_apt_field_read as R

N = 3
MASSES = np.array([12.0, 1.008, 1.008])


def exact_apt(seed: int) -> np.ndarray:
    """A random 3 × 3N APT whose translation sum rule is exact (a neutral molecule)."""
    P = np.random.default_rng(seed).normal(0, 0.3, (3, N, 3))
    return (P - P.mean(axis=1, keepdims=True)).reshape(3, 3 * N)


def hessian() -> np.ndarray:
    A = np.random.default_rng(7).normal(0, 0.05, (3 * N, 3 * N))
    return 0.5 * np.eye(3 * N) + A @ A.T


def field_runs(no_gr_limit: np.ndarray, gr_limit: np.ndarray, c: float = 2e2) -> dict:
    """Central differences at F and 2F with an F² error c·F² on every entry, in both grid modes."""
    out = {}
    for f in R.FIELDS:
        F = float(f)
        out[f] = {"no_gr": no_gr_limit + c * F**2, "gr": gr_limit + c * F**2}
    return out


def grid_offset() -> np.ndarray:
    """What a fixed grid adds: equal on every atom, so it breaks the sum rule (here by 7.5e-4 e, as ovalene's miss)."""
    return np.tile(np.full((3, 1, 3), 2.5e-4), (1, N, 1)).reshape(3, 3 * N)


def test_both_lines_hold_and_richardson_removes_a_field_error_that_misses_at_f_alone():
    P_true = exact_apt(1)
    P_labels = P_true + grid_offset()                                   # the labels route: fixed grid, sum rule missed
    field = field_runs(P_labels, P_true)
    assert np.abs(field["1e-3"]["no_gr"] - P_labels).max() > R.D.LINE_E   # F alone would miss L4's line (c·F² = 2e-4 e)
    res, apt = R.assess(P_labels, field, hessian(), MASSES)
    assert res["line_A"]["holds"] and res["line_B"]["holds"] and res["passed"]
    assert res["labels_sum_rule_e"] > R.SUM_RULE_LIMIT and res["line_A"]["sum_rule_e"] < 1e-12
    assert np.allclose(apt, P_true) and res["heights"]["strong_bands"] > 0


def test_a_response_error_in_the_labels_apt_fails_line_b():
    P_true = exact_apt(2)
    P_labels = P_true + grid_offset()
    off = P_labels.copy()
    off[0, 0] += 3e-4                                                   # the labels route's response off on one entry
    res, _ = R.assess(off, field_runs(P_labels, P_true), hessian(), MASSES)
    assert res["line_A"]["holds"] and not res["line_B"]["holds"] and not res["passed"]


def test_a_grid_response_apt_off_its_sum_rule_fails_line_a():
    P_true = exact_apt(3)
    P_labels = P_true + grid_offset()
    res, _ = R.assess(P_labels, field_runs(P_labels, P_true + 2 * grid_offset()), hessian(), MASSES)
    assert not res["line_A"]["holds"] and res["line_B"]["holds"] and not res["passed"]


def test_a_missing_field_output_is_refused(tmp_path):
    np.savez(tmp_path / "field_F1e-3.npz", apt_no_grid_response=exact_apt(4), apt_grid_response=exact_apt(4))
    with pytest.raises(SystemExit, match="2e-3"):
        R.load_field(tmp_path)


def test_the_whole_read_writes_the_apt_and_the_report(tmp_path):
    d = tmp_path / "T_x"
    d.mkdir()
    P_true = exact_apt(5)
    P_labels = P_true + grid_offset()
    for f, v in field_runs(P_labels, P_true).items():
        np.savez(d / f"field_F{f}.npz", apt_no_grid_response=v["no_gr"], apt_grid_response=v["gr"])
    np.savez(d / R.D.APT_FILE, apt=P_labels, passed=False)
    np.savez(d / "hessian_b3lyp_analytic.npz", H_projected=hessian())
    (d / "geometry.json").write_text(json.dumps({"masses_amu": MASSES.tolist()}), encoding="utf-8")
    (tmp_path / "ids.tsv").write_text("# test\nT_x\tx\n", encoding="utf-8")
    assert R.main(["--dir", str(tmp_path)]) == 0
    with np.load(d / R.OUT_APT) as z:
        assert bool(z["passed"]) and str(z["route"]) == "field_grid_response_richardson" and np.allclose(z["apt"], P_true)
    rows = json.loads((tmp_path / "l5_apt_field_read.json").read_text(encoding="utf-8"))
    assert rows["T_x"]["passed"] and "| T_x |" in (tmp_path / "l5_apt_field_read.md").read_text(encoding="utf-8")
