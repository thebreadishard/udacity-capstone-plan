"""probes/pahdb_anharmonic_match.py on synthetic values, before any library number is read against ours (S3 amendment 5): the library parse,
the threshold and window, the IR-active selection, and the one-to-one pairing with its cap."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes"))
M = pytest.importorskip("pahdb_anharmonic_match")

XML = """<?xml version="1.0"?>
<pahdatabase xmlns="http://www.astrochemistry.org/pahdb/anharmonic"><species>
<specie uid="7"><transitions>
<mode><frequency>700.0</frequency><intensity>3.0</intensity></mode>
<mode><frequency>1400.0</frequency><intensity>0.2</intensity></mode>
</transitions></specie>
<specie uid="8"><transitions><mode><frequency>900.0</frequency><intensity>1.0</intensity></mode></transitions></specie>
</species></pahdatabase>"""


def test_the_library_parse(tmp_path):
    p = tmp_path / "lib.xml"
    p.write_text(XML, encoding="utf-8")
    np.testing.assert_array_equal(M.pahdb_transitions(p, "7"), [[700.0, 3.0], [1400.0, 0.2]])
    with pytest.raises(SystemExit):
        M.pahdb_transitions(p, "9")


def test_threshold_and_widened_window():
    t = np.array([[530.0, 1.0], [520.0, 1.0], [800.0, 0.4], [800.5, 0.5], [2020.0, 9.0], [2030.0, 9.0]])
    np.testing.assert_array_equal(M.candidates(t, 0.5), [530.0, 800.5, 2020.0])


def test_only_ir_active_fundamentals_in_the_window():
    nu = np.array([600.0, 610.0, 3050.0, 1500.0, 540.0])
    labels = ["b3u", "ag", "b2u", "b1u", "b3u"]
    np.testing.assert_array_equal(M.ours_in_window(nu, labels), [600.0, 1500.0])


def test_pairing_is_one_to_one_least_total_and_capped():
    ours = np.array([700.0, 710.0, 1200.0])
    theirs = np.array([705.0, 1290.0])
    m = M.match(ours, theirs)
    assert len(m["pairs"]) == 1 and m["pairs"][0][1] == 705.0       # one of 700/710 pairs, 1200–1290 is beyond the cap
    assert 1200.0 in m["unpaired_ours"] and m["unpaired_theirs"] == [1290.0]
    m2 = M.match(np.array([700.0, 704.0]), np.array([703.0, 712.0]))
    assert sorted(m2["pairs"]) == [(700.0, 703.0), (704.0, 712.0)]    # least total (11), not greedy nearest (704–703, then 700–712: 13)
    s = M.summary(m2)
    assert s["mean_cm"] == pytest.approx(-5.5) and s["rms_about_mean_cm"] == pytest.approx(2.5)


def test_empty_sides():
    assert M.summary(M.match(np.array([]), np.array([700.0])))["n_pairs"] == 0
