"""probes/apt_l4_diag.py (L4 diagnosis D1, 16 Oct 2026), run on synthetic APTs before the field run at 2F: a pure F² error of the field
route, a refined APT that is off, a mixture, a field route noisier than the line, and a case with no entry over the line."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes"))
import apt_l4_diag as D

RNG = np.random.default_rng(0)
TRUTH = RNG.normal(size=(3, 63))
SHAPE = RNG.normal(size=(3, 63))
ERROR = 3e-4 * SHAPE / np.abs(SHAPE).max()            # an error pattern whose largest entry is 3e-4 e, as on B_1f3de8463a


def noise(scale: float) -> np.ndarray:
    return scale * RNG.normal(size=(3, 63))


def test_a_pure_f_squared_error_is_the_field_route():
    res = D.diagnose(TRUTH, TRUTH + ERROR + noise(1e-6), TRUTH + 4 * ERROR + noise(1e-6))
    assert res["verdict"] == "field-route truncation" and abs(res["slope"] - 4) < 0.1 and res["max_diff_richardson_e"] < 1e-5


def test_a_refined_apt_that_is_off_is_in_doubt():
    field_error = 1e-5 * SHAPE / np.abs(SHAPE).max()
    P = TRUTH - ERROR                                       # the refined APT off by the pattern, the field route nearly converged in F
    res = D.diagnose(P, TRUTH + field_error, TRUTH + 4 * field_error)
    assert res["verdict"] == "refined APT in doubt" and 0.9 < res["slope"] < 1.3


def test_half_and_half_is_unexplained():
    res = D.diagnose(TRUTH - ERROR / 2, TRUTH + ERROR / 2, TRUTH + 2 * ERROR)
    assert res["verdict"] == "unexplained" and 2 < res["slope"] < 3


def test_a_slope_of_four_with_a_noisy_field_route_is_not_enough():
    res = D.diagnose(TRUTH, TRUTH + ERROR + noise(1e-4), TRUTH + 4 * ERROR + noise(1e-4))
    assert res["max_diff_richardson_e"] > D.LINE_E and res["verdict"] == "unexplained"


def test_nothing_over_the_line_gives_no_slope():
    res = D.diagnose(TRUTH, TRUTH + noise(1e-6), TRUTH + noise(1e-6))
    assert res["entries_over_line"] == 0 and np.isnan(res["slope"]) and res["verdict"] == "unexplained"


def test_the_command_line_on_files(tmp_path):
    (tmp_path / "m").mkdir()
    np.savez(tmp_path / "m" / D.APT_FILE, apt=TRUTH)
    np.savez(tmp_path / "f1.npz", apt_no_grid_response=TRUTH + ERROR, apt_grid_response=TRUTH)
    np.savez(tmp_path / "f2.npz", apt_no_grid_response=TRUTH + 4 * ERROR, apt_grid_response=TRUTH)
    assert D.main(["--refined", str(tmp_path / "m"), "--field", str(tmp_path / "f1.npz"), "--field2", str(tmp_path / "f2.npz"),
                   "--out", str(tmp_path / "d1")]) == 0
    assert "field-route truncation" in (tmp_path / "d1.md").read_text(encoding="utf-8")
