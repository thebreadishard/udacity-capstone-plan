"""probes/low_mode_patch_check.py and low_mode_patch.select (TASKS 201 step 3): the registered verdict at its edge, the comparison on
synthetic files, and the selection of folders by their label modes. numpy only."""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes"))
import low_mode_patch as L
import low_mode_patch_check as C
from qc_common import HARTREE2CM

MASSES = [15.99491461956, 1.00782503207, 1.00782503207]
COORDS = [[0.0, 0.0, 0.0], [0.0, -1.4305, 1.1093], [0.0, 1.4305, 1.1093]]


def _hessian_with(omega_cm):
    """A water Hessian with the given vibrational frequencies (cm⁻¹) along a fixed vibrational basis."""
    base = L.vibrational_modes(np.diag(np.arange(1.0, 10.0)), np.array(MASSES), np.array(COORDS)).vectors
    k = (np.asarray(omega_cm) / HARTREE2CM) ** 2
    sm = L.mass_weights(np.array(MASSES))
    return (base @ np.diag(k) @ base.T) * np.outer(sm, sm)


def _folder(root, name, omega_label, omega_patched, omega_fd):
    for sub in ("patch", "fd", "mol"):
        (root / sub / name).mkdir(parents=True)
    (root / "mol" / name / "geometry.json").write_text(json.dumps({"masses_amu": MASSES, "coords_bohr": COORDS}), encoding="utf-8")
    for tag in L.LABEL_TAGS:
        np.savez(root / "patch" / name / f"hessian_{tag}_analytic_grfpatch.npz", H_raw=_hessian_with(omega_patched),
                 freq_label_vib_cm=np.array(omega_label))
        np.savez(root / "fd" / name / f"fd_hessian_{tag}.npz", H_fd=_hessian_with(omega_fd))
        np.savez(root / "mol" / name / f"hessian_{tag}_analytic.npz", H_raw=_hessian_with(omega_label))


def test_verdict_edges():
    assert C.verdict({"b3lyp": {"max_abs_diff_cm": C.TOLERANCE_CM}, "wb97x": {"max_abs_diff_cm": 0.1}}) == "PASS"
    assert C.verdict({"b3lyp": {"max_abs_diff_cm": C.TOLERANCE_CM + 1e-9}, "wb97x": {"max_abs_diff_cm": 0.1}}) == "FAIL"


def test_compare_reads_the_repair_against_the_fd_hessian(tmp_path):
    _folder(tmp_path, "X_1", [9.5, 1600.0, 3700.0], [15.6, 1600.2, 3700.1], [15.7, 1600.0, 3700.0])
    rows = C.compare(tmp_path / "patch" / "X_1", tmp_path / "fd" / "X_1",
                     json.loads((tmp_path / "mol" / "X_1" / "geometry.json").read_text(encoding="utf-8")))
    r = rows["b3lyp"]
    assert r["lowest_patched_cm"] == pytest.approx(15.6, abs=1e-6) and r["lowest_fd_cm"] == pytest.approx(15.7, abs=1e-6)
    assert r["max_abs_diff_cm"] == pytest.approx(0.2, abs=1e-6) and C.verdict(rows) == "PASS"


def test_select_keeps_only_folders_with_low_modes(tmp_path):
    _folder(tmp_path, "X_low", [9.5, 1600.0, 3700.0], [9.5, 1600.0, 3700.0], [9.5, 1600.0, 3700.0])
    _folder(tmp_path, "X_high", [600.0, 1600.0, 3700.0], [600.0, 1600.0, 3700.0], [600.0, 1600.0, 3700.0])
    assert L.select(tmp_path / "mol") == {"X_low": 1}
