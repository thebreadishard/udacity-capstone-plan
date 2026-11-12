"""probes/low_mode_patch_run.py (TASKS 201 step 3): settings refused before any molecule is read; a molecule without low modes gets a
report and no patch; and water end to end as a second route — with every vibrational direction patched, the repaired Hessian's
frequencies equal those of probes/hessian_grid_response_fd.py's full central-difference Hessian of the same grid-response gradients
(another step and another displacement pattern). Needs pyscf, so it runs in WSL and is skipped elsewhere."""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes"))
pytest.importorskip("pyscf")
RUN = pytest.importorskip("low_mode_patch_run")
GRF = pytest.importorskip("hessian_grid_response_fd")

WATER = {"symbols": ["O", "H", "H"], "masses_amu": [15.99491461956, 1.00782503207, 1.00782503207],
         "coords_bohr": [[0.0, 0.0, 0.0], [0.0, -1.4305, 1.1093], [0.0, 1.4305, 1.1093]]}


def _label(root: Path, H: np.ndarray) -> Path:
    d = root / "W_water"
    d.mkdir(parents=True)
    (d / "geometry.json").write_text(json.dumps(WATER), encoding="utf-8")
    for tag in RUN.XC_TAGS:
        np.savez(d / f"hessian_{tag}_analytic.npz", H_raw=H, H_projected=H)
    return d


def _cfg(tmp_path, **change):
    base = {"molecules": tmp_path / "mol", "out": tmp_path / "out", "ids": ("W_water",), "below_cm": 20.0, "step_bohr": 0.01, "threads": 1,
            "max_memory_mb": 2000, "dry_run": False}
    return RUN.PatchConfig(**{**base, **change})


def test_settings_are_refused(tmp_path):
    _label(tmp_path / "mol", np.eye(9) * 0.5)
    with pytest.raises(ValueError, match="empty or repeats"):
        _cfg(tmp_path, ids=())
    with pytest.raises(ValueError, match="threshold"):
        _cfg(tmp_path, below_cm=0.0)
    with pytest.raises(ValueError, match="step"):
        _cfg(tmp_path, step_bohr=0.5)
    with pytest.raises(FileNotFoundError, match="without both analytic labels"):
        _cfg(tmp_path, ids=("W_water", "missing"))


def test_a_molecule_without_low_modes_gets_a_report_and_no_patch(tmp_path):
    d = _label(tmp_path / "mol", np.eye(9) * 0.5)        # every vibrational frequency far above 20 cm⁻¹
    cfg = _cfg(tmp_path)
    with open(tmp_path / "pyscf.log", "w", encoding="utf-8") as log:
        rec = RUN.patch_molecule(d, cfg, log)
    assert rec["directions"] == 0
    assert not list((tmp_path / "out" / "W_water").glob("*grfpatch.npz"))


def test_water_fully_patched_equals_the_full_fd_hessian(tmp_path):
    d = _label(tmp_path / "mol", np.zeros((9, 9)))       # every mode below the threshold: the label's vibrational block is replaced whole
    cfg = _cfg(tmp_path)
    with open(tmp_path / "pyscf.log", "w", encoding="utf-8") as log:
        rec = RUN.patch_molecule(d, cfg, log)
        assert rec["directions"] == 3
        fd_cfg = GRF.FdHessianConfig(d, tmp_path / "fd", ("b3lyp",), RUN.LABEL_GRID, 0.005, 1, 2000, False)
        mol = GRF.labels_mol(WATER, log, max_memory=2000)
        dm0 = GRF.converged_scf(mol, "b3lyp", RUN.LABEL_GRID, None).make_rdm1()
        H_fd = GRF.fd_hessian(WATER, fd_cfg, "b3lyp", dm0, log)
    with np.load(tmp_path / "out" / "W_water" / "hessian_b3lyp_analytic_grfpatch.npz") as z:
        patched = np.asarray(z["freq_patched_vib_cm"])
    fd = GRF.frequencies(H_fd, np.asarray(WATER["masses_amu"]), np.asarray(WATER["coords_bohr"]))
    np.testing.assert_allclose(patched, fd, atol=1.0)
