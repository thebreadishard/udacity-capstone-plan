"""A prediction that moves a mode across the vibrational threshold (chain PX's distorted base, 21 Oct 2026): the intensity read-out names the
case, the trainer's per-molecule read and the proxy check record and count it, every other error still stops, and the proxy read reports
the intensity over the molecules that have one."""
import sys
from pathlib import Path

import numpy as np
import pytest

pytest.importorskip("torch")
PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "modules" / "05_support_predictor" / "m05"))
sys.path.insert(0, str(PLAN / "probes"))
import proxy_check_plan as X  # noqa: E402
import proxy_transfer_check as P  # noqa: E402
import rungC_intensities as RI  # noqa: E402
import rungC_train as RT  # noqa: E402


def test_the_case_has_its_own_error_class():
    assert issubclass(RI.ModeCountChanged, ValueError)


def test_aggregate_counts_the_molecules_without_a_read_out():
    ok = {k: 0.5 for k in ("spectrum_overlap", "spectrum_overlap_zero_rule", "intensity_rel_rms", "intensity_rel_rms_zero_rule",
                           RI.MATCHED, "intensity_rel_rms_zero_rule_matched")}
    assert "intensity_failed_n" not in RI.aggregate({"a": ok, "b": ok})                      # pinned records keep their keys
    agg = RI.aggregate({"a": ok, "b": {RI.FAILED: "mode counts differ"}})
    assert agg["intensity_failed_n"] == 1 and agg["intensity_n"] == 1


def _mols():
    return {i: {"H_low": np.eye(3), "dH_true": np.zeros((3, 3)), "B": np.eye(3), "masses": np.ones(1), "apt": np.zeros((3, 3)),
                "F_low": np.zeros((3, 3))} for i in ("a", "b")}


def _raise_for_b(H_low, dH_true, dH_pred, masses, apt):
    if dH_pred[0, 0] == 1.0:
        raise RI.ModeCountChanged("mode counts differ (3, 2, 3)")
    return {RI.MATCHED: 0.2}


def test_the_trainers_read_records_the_molecule(monkeypatch):
    monkeypatch.setattr(RT, "readouts", lambda mols, ids, tr, dF_of: {})
    monkeypatch.setattr(RT.RI, "intensity_readout", _raise_for_b)
    out = RT.per_molecule_readouts(_mols(), ["a", "b"], [], lambda i: np.eye(3) * (i == "b"))
    assert RI.FAILED not in out["a"] and out["b"][RI.FAILED] == "mode counts differ (3, 2, 3)"


def test_another_error_still_stops_the_trainers_read(monkeypatch):
    def broken(*args):
        raise ValueError("an APT of the wrong shape")
    monkeypatch.setattr(RT, "readouts", lambda mols, ids, tr, dF_of: {})
    monkeypatch.setattr(RT.RI, "intensity_readout", broken)
    with pytest.raises(ValueError, match="wrong shape"):
        RT.per_molecule_readouts(_mols(), ["a"], [], lambda i: np.zeros((3, 3)))


def test_the_proxy_read_counts_the_molecule(monkeypatch):
    monkeypatch.setattr(P, "family_freq_rms", lambda m, K: {"CH-oop": 1.0})
    monkeypatch.setattr(P.PH, "k_of", lambda m, dF: dF)
    monkeypatch.setattr(P, "readouts", lambda mols, ids, tr, dF_of: {})
    monkeypatch.setattr(P.RI, "intensity_readout", _raise_for_b)
    r = P.read_set(_mols(), ["a", "b"], [], lambda i: np.eye(3) * (i == "b"))
    assert r["n_intensity"] == 1 and r["n_intensity_failed"] == 1 and r["intensity_matched_mean"] == 0.2


def test_the_plan_read_reports_intensity_over_the_reads_that_have_one():
    assert X.intensity_column([0.2, None, 0.4])[::2] == (pytest.approx(0.3), 2)
    m, se, n = X.intensity_column([None, None])
    assert np.isnan(m) and np.isnan(se) and n == 0
    with pytest.raises(SystemExit, match="non-finite"):
        X.mean_se([1.0, None])                                    # a frequency value never goes missing silently
