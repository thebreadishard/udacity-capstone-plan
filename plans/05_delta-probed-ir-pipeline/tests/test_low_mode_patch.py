"""probes/low_mode_patch.py — what the probe owns once the arithmetic lives in the corpus (TASKS 201, 216).

The formulas moved to `modules/05_support_predictor/corpus/vibrations.py` on 14 November 2026, where `tests/test_vibrations.py`
pins them; what stays here is the probe's own job: reading a corpus folder's two analytic labels, finding the molecules whose
labels carry a soft mode, and counting the directions. That job had no test before the move. numpy only.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
sys.path.insert(0, str(PLAN / "modules" / "05_support_predictor" / "corpus"))
import low_mode_patch as L  # noqa: E402
import vibrations as V  # noqa: E402
from constants import AMU2AU, HARTREE2CM  # noqa: E402

MASSES = [15.99491461956, 1.00782503207, 1.00782503207]
COORDS = [[0.0, 0.0, 0.0], [0.0, -1.4305, 1.1093], [0.0, 1.4305, 1.1093]]


def hessian_with(omega_cm: list[float]) -> np.ndarray:
    """A water Hessian whose three vibrational frequencies are the ones given (cm⁻¹), on a fixed vibrational basis."""
    masses, coords = np.array(MASSES), np.array(COORDS)
    basis = V.vibrational_modes(np.diag(np.arange(1.0, 10.0)), masses, coords).vectors
    curvature = np.sign(omega_cm) * (np.asarray(omega_cm, float) / HARTREE2CM) ** 2 * AMU2AU
    sm = np.sqrt(np.repeat(np.asarray(masses) * AMU2AU, 3))
    return (basis @ np.diag(curvature / AMU2AU) @ basis.T) * np.outer(sm, sm)


def write_molecule(folder: Path, omega_by_tag: dict[str, list[float]]) -> None:
    """A corpus folder as the probe expects it: a geometry and one analytic label file per functional."""
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "geometry.json").write_text(json.dumps(dict(symbols=["O", "H", "H"], coords_bohr=COORDS, masses_amu=MASSES,
                                                          charge=0, multiplicity=1)), encoding="utf-8")
    for tag, omega in omega_by_tag.items():
        np.savez(folder / f"hessian_{tag}_analytic.npz", H_raw=hessian_with(omega), freq_cm=np.zeros(9))


def test_read_label_gives_the_geometry_and_both_hessians(tmp_path: Path) -> None:
    write_molecule(tmp_path / "A_1", {tag: [12.0, 1600.0, 3700.0] for tag in V.LABEL_TAGS})
    geometry, hessians = L.read_label(tmp_path / "A_1")
    assert geometry["symbols"] == ["O", "H", "H"]
    assert set(hessians) == set(V.LABEL_TAGS)
    assert all(h.shape == (9, 9) for h in hessians.values())


def test_label_directions_find_the_soft_mode_and_only_that(tmp_path: Path) -> None:
    write_molecule(tmp_path / "A_1", {tag: [12.0, 1600.0, 3700.0] for tag in V.LABEL_TAGS})
    assert L.label_directions(tmp_path / "A_1").shape == (9, 1)
    write_molecule(tmp_path / "A_2", {tag: [120.0, 1600.0, 3700.0] for tag in V.LABEL_TAGS})
    assert L.label_directions(tmp_path / "A_2").shape[1] == 0


def test_one_functional_below_the_threshold_is_enough(tmp_path: Path) -> None:
    """The directions are merged over both labels, so a mode soft in one of them is repaired in both."""
    write_molecule(tmp_path / "A_3", {"b3lyp": [9.0, 1600.0, 3700.0], "wb97x": [120.0, 1600.0, 3700.0]})
    assert L.label_directions(tmp_path / "A_3").shape[1] == 1


def test_select_keeps_the_folders_with_a_soft_mode(tmp_path: Path) -> None:
    molecules = tmp_path / "molecules"
    write_molecule(molecules / "A_low", {tag: [12.0, 1600.0, 3700.0] for tag in V.LABEL_TAGS})
    write_molecule(molecules / "A_stiff", {tag: [120.0, 1600.0, 3700.0] for tag in V.LABEL_TAGS})
    (molecules / "A_unlabelled").mkdir()
    assert L.select(molecules) == {"A_low": 1}


def test_select_reads_the_threshold_it_is_given(tmp_path: Path) -> None:
    molecules = tmp_path / "molecules"
    write_molecule(molecules / "A_mid", {tag: [60.0, 1600.0, 3700.0] for tag in V.LABEL_TAGS})
    assert L.select(molecules) == {}
    assert L.select(molecules, below_cm=100.0) == {"A_mid": 1}


def test_a_folder_without_both_labels_is_left_out(tmp_path: Path) -> None:
    molecules = tmp_path / "molecules"
    write_molecule(molecules / "A_half", {"b3lyp": [12.0, 1600.0, 3700.0]})
    assert L.select(molecules) == {}
    with pytest.raises(FileNotFoundError):
        L.read_label(molecules / "A_half")


def test_the_probe_takes_its_arithmetic_from_the_corpus_module() -> None:
    """One implementation: the names the probe uses are the corpus module's own objects, not copies of them."""
    assert L.vibrational_modes is V.vibrational_modes
    assert L.low_mode_directions is V.low_mode_directions
    assert L.LOW_MODE_CM == V.LOW_MODE_CM


WANTED = {"below_cm": 60.0, "step_bohr": 0.02, "grid": [99, 590]}


def test_a_fresh_out_folder_and_one_made_with_the_same_settings_may_be_used() -> None:
    assert L.settings_conflict(None, WANTED, has_results=False) is None
    assert L.settings_conflict(dict(WANTED), WANTED, has_results=True) is None
    assert L.settings_conflict(dict(WANTED), WANTED, has_results=False) is None


def test_an_out_folder_made_with_another_step_or_threshold_is_refused() -> None:
    """20 Nov 2026 review: the runner kept any dir_j_±.json it found, so a folder reused at another --step or --below mixed two
    measurements in one Hessian."""
    other_step = L.settings_conflict(WANTED | {"step_bohr": 0.01}, WANTED, has_results=True)
    assert other_step is not None and "step_bohr: 0.01 there, 0.02 asked" in other_step
    other_below = L.settings_conflict(WANTED | {"below_cm": 20.0}, WANTED, has_results=False)
    assert other_below is not None and "below_cm: 20.0 there, 60.0 asked" in other_below
    assert "grid" in L.settings_conflict({"below_cm": 60.0, "step_bohr": 0.02}, WANTED, has_results=True)


def test_an_out_folder_with_results_and_no_record_of_its_settings_is_refused() -> None:
    problem = L.settings_conflict(None, WANTED, has_results=True)
    assert problem is not None and L.RUN_SETTINGS_NAME in problem and "fresh out folder" in problem
