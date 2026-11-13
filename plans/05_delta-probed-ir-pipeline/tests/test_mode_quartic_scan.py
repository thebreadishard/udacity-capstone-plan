"""probes/mode_quartic_scan.py (TASKS 207): the five-point stencils are exact on a quartic polynomial, the registered reading at its edges,
and settings refused before any geometry is read. Needs pyscf (the module imports route A's SCF), so it runs in WSL and is skipped elsewhere."""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes"))
pytest.importorskip("pyscf")
MQS = pytest.importorskip("mode_quartic_scan")


def test_stencils_are_exact_on_a_quartic():
    w, phi, h = 807.0, 711.0, 0.5
    energy = {k: (0.5 * w * (k * h) ** 2 + phi * (k * h) ** 4 / 24 + 3.0 * (k * h) ** 3) / MQS.HARTREE_CM for k in (0, 1, -1, 2, -2)}
    omega, quartic = MQS.stencils(energy, h)
    assert omega == pytest.approx(w, rel=1e-10) and quartic == pytest.approx(phi, rel=1e-10)


def test_reading_edges():
    assert MQS.reading(711.0, 50.0, 711.0) == "GRID"
    assert MQS.reading(711.0, 72.0, 711.0) == "UNRESOLVED"          # fine above a tenth, and not within 30 % of the coarse
    assert MQS.reading(700.0, 650.0, 711.0) == "POTENTIAL"
    assert MQS.reading(400.0, 380.0, 711.0) == "UNRESOLVED"          # the coarse grid does not reproduce the stored constant


def test_step_reading_edges():
    assert MQS.step_reading(456.6, 460.0) == "CONVERGED"
    assert MQS.step_reading(456.6, 711.1) == "STEP_DEPENDENT"
    assert MQS.step_reading(100.0, 110.0) == "CONVERGED"            # a tenth of the larger, the edge
    assert MQS.step_reading(100.0, 112.0) == "STEP_DEPENDENT"


def test_richardson_removes_an_h_squared_error():
    true_phi, c = 457.0, 1016.0                                      # phi(h) = true + c h^2
    for small, large in ((0.25, 0.5), (0.5, 1.0)):
        got = MQS.richardson(small, true_phi + c * small**2, large, true_phi + c * large**2)
        assert got == pytest.approx(true_phi, rel=1e-10)
    with pytest.raises(ValueError, match="the smaller"):
        MQS.richardson(1.0, 1.0, 0.5, 1.0)


def test_two_steps_share_the_points_that_meet():
    assert MQS.displacements((0.5,)) == [0.0, 0.5, -0.5, 1.0, -1.0]
    assert MQS.displacements((0.25, 0.5, 1.0)) == [0.0, 0.25, -0.25, 0.5, -0.5, 1.0, -1.0, 2.0, -2.0]
    assert MQS.point_name(36, 0.0) == "Q0.json" and MQS.point_name(36, -0.5) == "mode36_-0.500000.json"
    assert MQS.point_name(36, 2 * 0.25) == MQS.point_name(36, 0.5)   # the same geometry is the same file, whatever step asked for it


def test_settings_are_refused(tmp_path):
    (tmp_path / "ref.json").write_text("{}", encoding="utf-8")
    np.savez(tmp_path / "qff_report.npz", omega_cm=np.zeros(3))
    base = {"setting": tmp_path, "out": tmp_path / "out", "modes": (1,), "grids": ("75,302", "99,590"), "steps": (0.5,),
            "threads": 1, "dry_run": True}
    MQS.QuarticConfig(**base)
    MQS.QuarticConfig(**{**base, "grids": ("99,590",), "steps": (0.25, 0.5)})
    with pytest.raises(ValueError, match="distinct"):
        MQS.QuarticConfig(**{**base, "modes": (1, 1)})
    with pytest.raises(ValueError, match="one or two distinct grids"):
        MQS.QuarticConfig(**{**base, "grids": ("75,302", "75,302")})
    with pytest.raises(ValueError, match="steps"):
        MQS.QuarticConfig(**{**base, "steps": (3.0,)})
    with pytest.raises(ValueError, match="measure nothing"):
        MQS.QuarticConfig(**{**base, "grids": ("99,590",)})
    with pytest.raises(FileNotFoundError, match="missing"):
        MQS.QuarticConfig(**{**base, "setting": tmp_path / "nowhere"})
