"""probes/upstream_dfmp2_grad/compare_grad.py: what the comparison of two gradient files refuses, and what it reports."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes" / "upstream_dfmp2_grad"))
import compare_grad as C
from pyscf_grad import level_text, save_npz

LEVEL = level_text("ANO-pVQZ", "cc-pVQZ-JKFIT", "cc-pVQZ-RI", 6)


def record(**changes: object) -> dict[str, np.ndarray]:
    """A gradient file's content for a three-atom molecule."""
    made = {"gradient": np.array([[0.0, 0.0, 0.01], [0.0, 0.02, -0.005], [0.0, -0.02, -0.005]]), "e_scf": np.array(-76.0),
            "e_tot": np.array(-76.2), "coords_bohr": np.arange(9.0).reshape(3, 3), "seconds": np.array([1.0, 2.0, 3.0]),
            "peak_gib": np.array(0.5), "level": np.array(LEVEL)}
    return made | {key: np.asarray(value) for key, value in changes.items()}


def test_level_text_is_the_same_for_any_spelling_of_the_names():
    assert LEVEL == "ano-pvqz / cc-pvqz-jkfit / cc-pvqz-ri / frozen 6"


def test_equal_files_report_zero_and_the_sum_of_the_stage_times():
    lines = C.compare(record(), record(seconds=40.0))
    assert lines[0] == f"level: {LEVEL}"
    assert "max |difference| 0.00e+00" in lines[3] and "sum 6" in lines[4] and "psi4 seconds (the whole gradient call) 40" in lines[4]


def test_the_largest_difference_of_any_element_is_reported():
    theirs = record()
    theirs["gradient"] = theirs["gradient"] + np.array([[0.0, 0.0, 0.0], [0.0, 3e-7, 0.0], [0.0, 0.0, -1e-7]])
    assert "max |difference| 3.00e-07" in C.compare(record(), theirs | {"seconds": np.array(1.0)})[3]


@pytest.mark.parametrize(("change", "said"), [
    ({"level": level_text("ano-pvqz", "cc-pvqz-jkfit", "cc-pvqz-ri", 10)}, "different levels"),
    ({"coords_bohr": np.arange(9.0).reshape(3, 3) + 1e-6}, "different geometries"),
    ({"e_scf": -76.0 + 2e-6}, "not the same calculation"),
    ({"e_tot": -76.2 - 2e-6}, "not the same calculation"),
])
def test_files_that_are_not_of_one_calculation_are_refused(change, said):
    with pytest.raises(SystemExit, match=said):
        C.compare(record(), record(seconds=1.0, **change))


def test_energies_at_the_line_are_still_compared():
    assert C.compare(record(), record(seconds=1.0, e_tot=-76.2 + 0.9e-6))


def test_main_reads_two_files_written_through_the_temp_file(tmp_path, capsys):
    save_npz(str(tmp_path / "a.npz"), **record())
    save_npz(str(tmp_path / "b.npz"), **record(seconds=5.0))
    assert C.main([str(tmp_path / "a.npz"), str(tmp_path / "b.npz")]) == 0
    assert "gradient: largest element 0.020000" in capsys.readouterr().out
    assert sorted(p.name for p in tmp_path.iterdir()) == ["a.npz", "b.npz"]
