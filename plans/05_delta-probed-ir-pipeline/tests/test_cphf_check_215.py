"""probes/cphf_check_215.py (TASKS 49): the registered verdict at its edges, option 3's controls read or refused, the frequency along a mode
and the comparison on synthetic Hessians. Needs pyscf (the module imports it), so it runs in WSL and is skipped elsewhere."""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes"))
pytest.importorskip("pyscf")
CC = pytest.importorskip("cphf_check_215")


def test_verdict_edges():
    tol = CC.CONTROL_TOLERANCE_CM
    assert CC.verdict(3.4 + tol, -9.46, [3.38, 3.56]) == "UNRESOLVED"   # beyond the first control by more than the tolerance
    assert CC.verdict(3.5, -9.46, [3.38, 3.56]) == "CPHF"
    assert CC.verdict(-9.46 + tol, -9.46, [3.38, 3.56]) == "NOT CPHF"
    assert CC.verdict(-2.0, -9.46, [3.38, 3.56]) == "UNRESOLVED"


def test_controls_read_and_refused():
    rows = [{"grid": [99, 590], "control": 3.38}, {"grid": [99, 590], "control": 3.56}, {"grid": [150, 974], "control": 4.33}]
    assert CC.controls_at_label_grid({"xc": "b3lyp", "rows": rows}) == [3.38, 3.56]
    with pytest.raises(ValueError, match="not b3lyp"):
        CC.controls_at_label_grid({"xc": "wb97x", "rows": rows})
    with pytest.raises(ValueError, match="two steps"):
        CC.controls_at_label_grid({"xc": "b3lyp", "rows": rows[1:]})


def _triatomic():
    coords = np.array([[0.0, 0.0, 0.0], [0.0, -1.43, 1.11], [0.0, 1.43, 1.11]])
    masses = np.array([15.995, 1.008, 1.008])
    rng = np.random.default_rng(0)
    A = rng.normal(size=(9, 9))
    return coords, masses, 0.1 * (A @ A.T)


def test_frequency_along_matches_lowest_mode():
    coords, masses, H = _triatomic()
    mode = CC.lowest_mode(coords, masses, H)
    assert CC.frequency_along(mode, H) == pytest.approx(CC.frequency_cm(mode.analytic_k), rel=1e-10)


def test_compare_same_hessian_is_not_cphf():
    coords, masses, H = _triatomic()
    record = CC.compare(H, H.copy(), masses, coords, [1e6, 1e6])
    assert record["verdict"] == "NOT CPHF"
    assert record["difference_215_minus_label"]["max_abs_cm"] == pytest.approx(0.0, abs=1e-9)
    assert record["along_v_cm"]["label"] == pytest.approx(record["along_v_cm"]["analytic_215"])


def test_settings_refused(tmp_path):
    with pytest.raises(ValueError, match="threads"):
        CC.CphfCheckConfig(tmp_path, tmp_path / "fd.json", tmp_path / "out", 0, 4000, False)
    with pytest.raises(FileNotFoundError, match=r"geometry\.json"):
        CC.CphfCheckConfig(tmp_path, tmp_path / "fd.json", tmp_path / "out", 8, 4000, False)
