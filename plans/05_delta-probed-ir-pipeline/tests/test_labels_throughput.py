"""The labels server's first-day read (probes/labels_throughput.py): the log parser reads the lane log's line format, the exponent fit recovers a known
power and refuses a narrow size span, and the projection counts only what is still to run."""
import sys
from pathlib import Path

import pytest

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
import labels_throughput as L  # noqa: E402


def test_parse_molecule_log_reads_both_line_kinds():
    text = ("molecules/A2_02c8833bd5 b3lyp: 6003 s; |H_analytic − H_corpus| max 4.54e-03 rms 5.23e-04; max |Δfreq| 6 cm-1\n"
            "WARN: Input vhf is not found.\n"
            "molecules/A2_02c8833bd5 wb97x: 9120.5 s; no corpus psi4 file to compare with; lowest vib [50.1] cm-1\n")
    assert L.parse_molecule_log(text) == {"A2_02c8833bd5": {"b3lyp": 6003.0, "wb97x": 9120.5}}


def test_fit_exponent_recovers_power_and_refuses_narrow_span():
    ns = [12, 18, 24, 30]
    assert L.fit_exponent(ns, [2.0 * n ** 3.4 for n in ns]) == pytest.approx(3.4)
    assert L.fit_exponent([27, 28, 30], [1.0, 1.1, 1.3]) is None


def test_project_counts_only_what_remains():
    atoms = {"a": 30, "b": 15, "c": 30}
    done = {"a": {"b3lyp": 1000.0, "wb97x": 2000.0}, "c": {"b3lyp": 1000.0}}
    rem = L.project({0: ["a", "b"], 1: ["c"]}, done, atoms, p=3.0, wratio=9.0)
    # lane 0: b at 15 atoms = 1/8 of the 30-atom times (b3lyp 125 s, wb97x 250 s from the measured wb97x, not the ratio)
    assert rem[0] == pytest.approx((125 + 250) / 3600)
    assert rem[1] == pytest.approx(2000 / 3600)        # c's wb97x from a's measured wb97x
    with pytest.raises(ValueError):
        L.project({0: ["b"]}, {}, atoms, 3.0, 1.5)


def test_ids_of_includes_molecules_timed_before_a_list_switch():
    assert L.ids_of({0: ["b", "c"]}, {"a": {"b3lyp": 1.0}, "b": {}}) == {"a", "b", "c"}
