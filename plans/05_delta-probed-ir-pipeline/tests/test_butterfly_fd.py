"""probes/butterfly_fd.py (TASKS 49, option 3): the registered verdict on synthetic rows (positive, negative, steps apart, grids apart, a
negative patched Hessian, the control), the settings refused before any geometry is read, the rigid basis, the patched Hessian, and water
end to end at a small grid: the control (gradients without the grid response) must give the analytic Hessian's curvature along its
lowest mode. Needs pyscf, so it runs in WSL and is skipped elsewhere."""
import sys
from pathlib import Path

import numpy as np
import pytest

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
sys.path.insert(0, str(PLAN / "modules" / "05_support_predictor" / "corpus"))
pytest.importorskip("pyscf")
BFD = pytest.importorskip("butterfly_fd")

COARSE, FINE = (50, 194), (75, 302)
STEPS = (0.01, 0.02)
WATER = {"symbols": ["O", "H", "H"], "masses_amu": [15.99491461956, 1.00782503207, 1.00782503207],
         "coords_bohr": [[0.0, 0.0, 0.0], [0.0, -1.4305, 1.1093], [0.0, 1.4305, 1.1093]]}


def _row(gradient: float, patched: float | None = None, control: float = -9.5) -> dict[str, float]:
    return {"gradient": gradient, "energy": gradient, "patched_lowest": gradient if patched is None else patched, "control": control}


def _rows(values: dict[tuple, dict]) -> dict:
    return {(g, h): r for (g, h), r in values.items()}


def test_verdict_positive_negative_and_unresolved():
    positive = _rows({(COARSE, 0.01): _row(14.0), (COARSE, 0.02): _row(15.0), (FINE, 0.01): _row(16.0), (FINE, 0.02): _row(17.0)})
    assert BFD.verdict(positive, -9.5) == ("POSITIVE", True)
    negative = _rows({(COARSE, 0.01): _row(-9.0), (COARSE, 0.02): _row(-9.4), (FINE, 0.01): _row(-8.0), (FINE, 0.02): _row(-8.5)})
    assert BFD.verdict(negative, -9.5)[0] == "NEGATIVE"
    steps_apart = _rows({(COARSE, 0.01): _row(14.0), (COARSE, 0.02): _row(15.0), (FINE, 0.01): _row(10.0), (FINE, 0.02): _row(16.0)})
    assert BFD.verdict(steps_apart, -9.5)[0] == "UNRESOLVED"
    grids_apart = _rows({(COARSE, 0.01): _row(-3.0), (COARSE, 0.02): _row(-2.0), (FINE, 0.01): _row(12.0), (FINE, 0.02): _row(12.5)})
    assert BFD.verdict(grids_apart, -9.5)[0] == "UNRESOLVED"
    patched_negative = _rows({(COARSE, 0.01): _row(14.0), (COARSE, 0.02): _row(15.0), (FINE, 0.01): _row(16.0, -1.0),
                              (FINE, 0.02): _row(17.0)})
    assert BFD.verdict(patched_negative, -9.5)[0] == "UNRESOLVED"


def test_the_control_must_match_the_analytic_frequency():
    rows = _rows({(COARSE, 0.01): _row(14.0, control=-9.0), (COARSE, 0.02): _row(15.0, control=-6.0),
                  (FINE, 0.01): _row(16.0), (FINE, 0.02): _row(17.0)})
    assert BFD.verdict(rows, -9.5) == ("POSITIVE", False)
    fine_only = _rows({(COARSE, 0.01): _row(14.0), (COARSE, 0.02): _row(15.0),
                       (FINE, 0.01): _row(16.0, control=-3.0), (FINE, 0.02): _row(17.0, control=-3.0)})
    assert BFD.verdict(fine_only, -9.5) == ("POSITIVE", True)              # the control is read at the analytic Hessian's grid only


@pytest.mark.parametrize("change", [{"xc_tag": "pbe"}, {"grids": (COARSE,)}, {"grids": (COARSE, COARSE)}, {"steps": (0.01,)},
                                    {"steps": (0.01, 0.01)}, {"steps": (0.0, 0.01)}, {"steps": (0.01, 0.1)}, {"threads": 0}])
def test_settings_are_refused_before_any_geometry_is_read(change, tmp_path):
    base = {"molecule": tmp_path, "out": tmp_path / "out", "xc_tag": "b3lyp", "grids": (COARSE, FINE), "steps": STEPS, "threads": 1,
            "max_memory_mb": 1000, "dry_run": False}
    with pytest.raises(ValueError):
        BFD.FdConfig(**{**base, **change})


def test_the_rigid_basis_is_orthonormal_and_holds_the_translations():
    coords = np.asarray(WATER["coords_bohr"])
    sqrt_m = np.sqrt(np.repeat(WATER["masses_amu"], 3) * BFD.AMU2AU)
    R = BFD.rigid_basis(coords, sqrt_m)
    assert np.allclose(R.T @ R, np.eye(6), atol=1e-12)
    t = np.zeros((3, 3))
    t[:, 0] = 1.0
    tmw = t.ravel() * sqrt_m
    assert np.linalg.norm(tmw - R @ (R.T @ tmw)) < 1e-12 * np.linalg.norm(tmw)


def test_the_patched_hessian_keeps_an_exact_column_and_moves_with_a_shifted_one():
    rng = np.random.default_rng(0)
    A = rng.normal(size=(5, 5))
    h = A @ A.T + np.diag([0.1, 2.0, 3.0, 4.0, 5.0])
    w, Y = np.linalg.eigh(h)
    mode = BFD.Mode(np.eye(5), h, Y[:, 0], Y[:, 0], np.ones(5))
    assert np.isclose(BFD.patched_lowest(mode, h @ Y[:, 0]), w[0])
    assert np.isclose(BFD.patched_lowest(mode, h @ Y[:, 0] - 0.05 * Y[:, 0]), w[0] - 0.05)


def test_water_control_reproduces_the_analytic_curvature(tmp_path):
    from analytic_hessians import labels_ks, labels_mol

    with open(tmp_path / "pyscf.log", "w", encoding="utf-8") as log:
        mf = labels_ks(labels_mol(WATER, log), "b3lyp", COARSE)
        mf.conv_tol = 1e-12
        mf.kernel()
        H = mf.Hessian().kernel().transpose(0, 2, 1, 3).reshape(9, 9)
    mode = BFD.lowest_mode(np.asarray(WATER["coords_bohr"]), np.asarray(WATER["masses_amu"]), H)
    cfg = BFD.FdConfig(tmp_path, tmp_path / "out", "b3lyp", (COARSE, FINE), STEPS, 1, 2000, False)
    cfg.out.mkdir()
    with open(cfg.out / "pyscf.log", "a", encoding="utf-8") as log:
        points = BFD.run_points(WATER, mode, cfg, log)
        assert BFD.run_points(WATER, mode, cfg, log).keys() == points.keys()      # a resume reads every point back
    record = BFD.report(cfg, mode, points)
    analytic = record["analytic_lowest_cm"]
    assert 1500 < analytic < 1800                                                  # the bend
    for r in record["rows"]:
        if tuple(r["grid"]) == COARSE:
            assert abs(r["control"] - analytic) < BFD.CONTROL_TOLERANCE_CM
        assert abs(r["gradient"] - r["energy"]) < 5.0                             # two routes on one curve
        assert abs(r["gradient"] - analytic) < 20.0
    assert record["verdict"] == "POSITIVE"
