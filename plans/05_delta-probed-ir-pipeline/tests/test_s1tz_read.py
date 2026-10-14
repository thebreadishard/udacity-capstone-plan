"""probes/s1tz_read.py (14 Oct 2026): S1-TZ's branches, the curve of amendment 1, the transfer read, and — when S1's benzene results are on
this machine — the read reproducing S1's registered G-vs-R and R-vs-B numbers (0.19 / 0.35 and 3.16 / 7.51 cm⁻¹) through the same code."""
import sys
from pathlib import Path

import numpy as np
import pytest

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
sys.path.insert(0, str(PLAN / "src"))
import s1tz_read as T  # noqa: E402

S1 = PLAN / "probes/results_m1/s1_anharmonic_benzene_2026-10-13/s1_benzene"


def mol(d_oop, d_ring, n=4):
    """A synthetic molecule: n CH-oop and n ring-ip modes with the given shifts d."""
    return {"omega": np.r_[np.full(n, 800.0), np.full(n, 1400.0)], "d": np.r_[np.asarray(d_oop, float) * np.ones(n), np.asarray(d_ring, float) * np.ones(n)],
            "family": np.array(["CH-oop"] * n + ["ring-ip"] * n)}


def test_branches_follow_the_registered_lines():
    assert T.branch({"a": mol(1.0, 1.0), "b": mol(1.4, 0.5)})[0] == "a"
    assert T.branch({"a": mol(1.0, 1.0), "b": mol(2.0, 2.0)})[0] == "c"
    assert T.branch({"a": mol(1.0, 1.0), "b": mol(1.0, 4.5)})[0] == "b"           # one molecule over 3.0 (rms 3.26)
    assert T.branch({"a": mol(3.2, 0.0), "b": mol(3.2, 0.0)})[0] == "b"           # pooled CH-oop over 3.0 (each molecule's rms 2.26)


def test_the_curve_reads_still_learning_only_beyond_twice_the_combined_se():
    flat = {"a": mol(-2.0, -1.0), "b": mol(-2.1, -1.0), "c": mol(-1.9, -1.1)}
    assert not T.curve(flat)["still_learning"]
    learning = {"a": mol(-6.0, -3.0), "b": mol(0.0, 0.0), "c": mol(-3.0, -1.5)}
    c = T.curve(learning)
    assert c["1"]["subsets"] == 3 and c["2"]["subsets"] == 3
    assert c["2"]["e"] < c["1"]["e"]


def test_a_transfer_miss_reads_by_the_curve():
    dbar, overall = T.family_means([mol(-2.0, -1.0)])
    hit = T.transfer(dbar, overall, mol(-2.5, -0.5), learning=False)
    assert not hit["miss"] and hit["reading"].startswith("transfers")
    miss_learning = T.transfer(dbar, overall, mol(-4.0, -1.0), learning=True)
    assert miss_learning["miss"] and "data-limited" in miss_learning["reading"] and "biphenylene" in miss_learning["reading"]
    miss_flat = T.transfer(dbar, overall, mol(-4.0, -1.0), learning=False)
    assert "the search first" in miss_flat["reading"]


@pytest.mark.skipif(not (S1 / "B" / "qff_report.npz").exists(), reason="S1's benzene results are not on this machine")
def test_the_read_reproduces_s1s_registered_numbers():
    gr = T.stats(T.molecule_d(str(S1 / "G"), str(S1 / "R")))
    rb = T.stats(T.molecule_d(str(S1 / "R"), str(S1 / "B")))
    assert gr["rms"] == pytest.approx(0.19, abs=0.005) and gr["max"] == pytest.approx(0.35, abs=0.01)
    assert rb["rms"] == pytest.approx(3.16, abs=0.005) and rb["max"] == pytest.approx(7.51, abs=0.005)
    rr = T.reference_read(str(S1 / "G"))
    assert rr["n_modes"] == 14 and rr["rms"] == pytest.approx(7.16, abs=0.005)        # the hybrid check's registered G number


@pytest.mark.skipif(not (S1 / "R" / "ref.json").exists(), reason="S1's benzene results are not on this machine")
def test_the_grid_gate_reproduces_the_measured_033_and_fails_below_it():
    from s1_anharmonic_level import grid_gate
    g = grid_gate(str(S1 / "G" / "ref.json"), str(S1 / "R" / "ref.json"))
    assert g["passed"] and g["max_abs_domega_window"] == pytest.approx(0.33, abs=0.005) and g["n_window"] == 22
    assert not grid_gate(str(S1 / "G" / "ref.json"), str(S1 / "R" / "ref.json"), line=0.1)["passed"]
