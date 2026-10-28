"""probes/qff_energy_route.py (28 Oct 2026): the even-part fit returns ω and φ_iiii of a known curve in dpir.qff's convention
(E = ½ ω q² + φ_iiii q⁴ / 24 + …), the cubic term stays out of it and shows in the odd part, and one step fewer shows the truncation."""
import sys
from pathlib import Path

import pytest

PLAN = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(PLAN / "probes"), str(PLAN / "src")]
import qff_energy_route as R  # noqa: E402

HARTREE_CM = R.HARTREE_CM
STEPS = [0.1, 0.2, 0.3, 0.4]


def curve(q: float, omega: float, phi3: float, phi4: float, c6: float, c8: float = 0.0) -> float:
    return -232.1 + (omega * q ** 2 / 2 + phi3 * q ** 3 / 6 + phi4 * q ** 4 / 24 + c6 * q ** 6 + c8 * q ** 8) / HARTREE_CM


def read(*args: float) -> dict:
    return R.read_curve(curve(0.0, *args), [curve(q, *args) for q in STEPS], [curve(-q, *args) for q in STEPS], STEPS)


@pytest.mark.parametrize("c6", [0.0, 40.0])
def test_known_curve_is_read_back(c6):
    r = read(992.0, 35.0, 907.0, c6)
    assert r["all_steps"]["omega"] == pytest.approx(992.0, abs=1e-4)
    assert r["all_steps"]["phi_iiii"] == pytest.approx(907.0, abs=1e-2)
    assert r["one_fewer"]["phi_iiii"] == pytest.approx(907.0, abs=1e-2)  # a q⁶ term is still exact with three steps
    assert r["odd_max"] == pytest.approx(2 * 35.0 * 0.4 ** 3 / 6, rel=1e-6)


def test_two_steps_are_refused():
    with pytest.raises(ValueError, match="at least 3"):
        R.read_curve(0.0, [1e-5, 4e-5], [1e-5, 4e-5], [0.1, 0.2])


def test_one_fewer_shows_truncation():
    r = read(992.0, 0.0, 907.0, 0.0, 500.0)                              # a q⁸ term: exact with four steps, aliased with three
    assert r["all_steps"]["phi_iiii"] == pytest.approx(907.0, abs=1e-2)
    assert abs(r["one_fewer"]["phi_iiii"] - 907.0) > 10
