"""probes/hessian_grid_response_fd.py (TASKS 201 step 2): settings refused before any input is read, the comparison and the target change
on synthetic Hessians, and water end to end at a coarse grid: the grid-response FD Hessian has a far smaller translation residual than the
analytic one and the same frequencies within the quadrature error. Needs pyscf, so it runs in WSL and is skipped elsewhere."""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
pytest.importorskip("pyscf")
GRF = pytest.importorskip("hessian_grid_response_fd")

WATER = {"symbols": ["O", "H", "H"], "masses_amu": [15.99491461956, 1.00782503207, 1.00782503207],
         "coords_bohr": [[0.0, 0.0, 0.0], [0.0, -1.4305, 1.1093], [0.0, 1.4305, 1.1093]]}
COARSE = (40, 110)


def _cfg(tmp_path, **change):
    base = {"molecule": tmp_path, "out": tmp_path / "out", "xc_tags": ("b3lyp",), "grid": COARSE, "step": 0.005, "threads": 1,
            "max_memory_mb": 2000, "dry_run": False}
    return GRF.FdHessianConfig(**{**base, **change})


@pytest.mark.parametrize("change", [{"xc_tags": ()}, {"xc_tags": ("pbe",)}, {"xc_tags": ("b3lyp", "b3lyp")}, {"grid": (0, 110)},
                                    {"grid": (40,)}, {"step": 0.0}, {"step": 0.05}, {"threads": 0}, {"max_memory_mb": 10}])
def test_settings_are_refused(change, tmp_path):
    with pytest.raises(ValueError):
        _cfg(tmp_path, **change)


def _spring(coords: np.ndarray, k: float = 0.4) -> np.ndarray:
    n = len(coords)
    H = np.zeros((3 * n, 3 * n))
    for i in range(n):
        for j in range(i + 1, n):
            e = coords[j] - coords[i]
            block = k * np.outer(e, e) / (e @ e)
            for a, b, s in ((i, i, 1), (j, j, 1), (i, j, -1), (j, i, -1)):
                H[3 * a:3 * a + 3, 3 * b:3 * b + 3] += s * block
    return H


def test_the_comparison_reads_a_known_error_and_the_target_change():
    coords = np.array([[0.0, 0.0, 0.0], [1.4, 0.2, 0.0], [-0.3, 1.1, 0.4], [0.5, -0.9, 1.2]])
    masses = np.array([12.0, 1.008, 15.995, 14.003])
    exact = _spring(coords)
    noisy = exact + 1e-4 * np.eye(12)
    r = GRF.compare({"label": noisy, "analytic_215": noisy, "fd_grid_response": exact}, masses, coords)
    assert r["translation"]["fd_grid_response"]["max_Ht"] < 1e-12 < r["translation"]["label"]["max_Ht"]
    assert r["fd_minus_label"]["max_abs_cm"] > 0 and r["fd_minus_label"] == r["fd_minus_analytic_215"]
    same = GRF.compare({"label": exact, "analytic_215": exact, "fd_grid_response": exact}, masses, coords)
    assert GRF.target_change({"b3lyp": same}) is None
    assert GRF.target_change({"b3lyp": same, "wb97x": same})["max_abs_cm"] == 0.0


def test_water_end_to_end(tmp_path):
    mol_dir = tmp_path / "water"
    mol_dir.mkdir()
    (mol_dir / "geometry.json").write_text(json.dumps(WATER), encoding="utf-8")
    cfg = _cfg(tmp_path, molecule=mol_dir)
    cfg.out.mkdir()
    with open(cfg.out / "pyscf.log", "a", encoding="utf-8") as log:
        dm0, H_an = GRF.reference(WATER, cfg, "b3lyp", log)
        H_fd = GRF.fd_hessian(WATER, cfg, "b3lyp", dm0, log)
        assert np.array_equal(GRF.fd_hessian(WATER, cfg, "b3lyp", dm0, log), H_fd)          # a resume reads every point back
    assert len(list((cfg.out / "b3lyp").glob("point_*.json"))) == 18
    masses, coords = np.asarray(WATER["masses_amu"]), np.asarray(WATER["coords_bohr"])
    r = GRF.compare({"label": H_an, "analytic_215": H_an, "fd_grid_response": H_fd}, masses, coords)
    t_fd, t_an = r["translation"]["fd_grid_response"]["max_Ht"], r["translation"]["label"]["max_Ht"]
    assert t_fd < t_an / 10, (t_fd, t_an)
    assert r["fd_minus_label"]["max_abs_cm"] < 20.0
    assert np.abs(H_fd - H_fd.T).max() < 1e-4
