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


def test_settings_are_refused(tmp_path):
    (tmp_path / "ref.json").write_text("{}", encoding="utf-8")
    np.savez(tmp_path / "qff_report.npz", omega_cm=np.zeros(3))
    base = {"setting": tmp_path, "out": tmp_path / "out", "modes": (1,), "grids": ("75,302", "99,590"), "h": 0.5, "threads": 1, "dry_run": True}
    MQS.QuarticConfig(**base)
    with pytest.raises(ValueError, match="distinct"):
        MQS.QuarticConfig(**{**base, "modes": (1, 1)})
    with pytest.raises(ValueError, match="two distinct grids"):
        MQS.QuarticConfig(**{**base, "grids": ("75,302", "75,302")})
    with pytest.raises(ValueError, match="step"):
        MQS.QuarticConfig(**{**base, "h": 3.0})
    with pytest.raises(FileNotFoundError, match="missing"):
        MQS.QuarticConfig(**{**base, "setting": tmp_path / "nowhere"})
