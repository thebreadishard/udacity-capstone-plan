"""probes/anchor_oop_check.py on synthetic records, before any TASKS 184 number is read: the rows from gradient files, the refusals (another
geometry, a non-planar Hessian), the truth anchor's round trip, the leave-one-out residual and the registered lines at their edges. The family
read itself is pinned on real data by `anchor_oop_check.py pin` (test 2 reproduced)."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes"))
A = pytest.importorskip("anchor_oop_check")


def _planar(n: int, rng: np.random.Generator) -> np.ndarray:
    """A symmetric Hessian with no out-of-plane–in-plane coupling in the frame where z is the normal."""
    H = rng.normal(size=(3 * n, 3 * n))
    H = H + H.T
    zi, ip = A.C.oop_indices(n)
    H[np.ix_(zi, ip)] = 0.0
    H[np.ix_(ip, zi)] = 0.0
    return H


def _run_dir(tmp_path: Path, coords: np.ndarray, rows: dict[int, np.ndarray]) -> Path:
    np.savez(tmp_path / "reference.npz", coords_bohr=coords)
    for k, row in rows.items():
        np.save(tmp_path / f"grad_{k:02d}_p.npy", row * A.STEP_BOHR)
        np.save(tmp_path / f"grad_{k:02d}_m.npy", -row * A.STEP_BOHR)
    return tmp_path


def test_rows_are_central_differences_of_the_gradients(tmp_path):
    coords = np.zeros((2, 3))
    rows = {2: np.arange(6.0), 5: -np.arange(6.0)}
    out = A.write_cc_rows(_run_dir(tmp_path, coords, rows), [2, 5], coords, tmp_path / "rows.npz")
    with np.load(out) as z:
        assert np.allclose(z["row_02"], rows[2]) and np.allclose(z["row_05"], rows[5]) and list(z["ks"]) == [2, 5]


def test_a_run_at_another_geometry_is_refused(tmp_path):
    run = _run_dir(tmp_path, np.zeros((2, 3)), {2: np.ones(6)})
    with pytest.raises(SystemExit, match="not the plane-frame geometry"):
        A.write_cc_rows(run, [2], np.full((2, 3), 0.1), tmp_path / "rows.npz")


def test_a_coupled_composite_is_refused(tmp_path):
    rng = np.random.default_rng(0)
    H = _planar(2, rng)
    H[2, 0] = H[0, 2] = 1e-3
    pf = A.C.PlaneFrame(["H", "H"], np.array([[0.0, 0.0, 0.0], [1.4, 0.0, 0.0]]), np.ones(2), np.eye(3), np.zeros(3))
    with pytest.raises(SystemExit, match="not a planar Hessian"):
        A.oop_truth(pf, H, tmp_path / "rows.npz")


def test_the_truth_anchor_reads_back_as_an_anchor(tmp_path):
    rng = np.random.default_rng(1)
    H = _planar(2, rng)
    x0, masses = np.array([[0.0, 0.0, 0.0], [1.4, 0.0, 0.0]]), np.ones(2)
    np.savez(tmp_path / "comp.npz", mp2_dz="dz.npz", mp2_tz="tz.npz", planeframe="")
    path = A.save_truth_anchor(tmp_path / "truth.npz", H, x0, masses, tmp_path / "comp.npz")
    assert np.allclose(A.M.projected(path), A.project_tr(H, masses, x0)[0])
    assert A.M.mp2_sources("A_x", str(path))[:2] == ("dz.npz", "tz.npz")


def _record(mol_id: str, truth: list[float], **cands: list[float]) -> dict:
    return {"mol_id": mol_id, "families": ["CH-oop"] * len(truth), "truth": truth, **cands}


def test_the_residual_scales_with_the_other_anchors_only():
    others = [_record("A1", [2.0, 4.0], c=[1.0, 2.0]), _record("A2", [-2.0, 6.0], c=[-1.0, 3.0])]     # s = 2 on the others
    rec = _record("P", [2.0, 2.0], c=[1.0, 2.0])
    assert A.loo_residual(others, rec, "c") == pytest.approx(np.sqrt(np.mean(np.array([0.0, -2.0]) ** 2)))


@pytest.mark.parametrize(("rms", "verdict"), [(10.0, "holds"), (10.01, "weaker"), (20.0, "weaker"), (20.01, "fails")])
def test_line_a_at_its_edges(rms, verdict):
    assert A.verdict_a(rms) == verdict


@pytest.mark.parametrize(("rms", "verdict"), [(3.0, "converged"), (3.01, "basis error"), (10.0, "basis error"), (10.01, "not the truth")])
def test_line_b_at_its_edges(rms, verdict):
    assert A.verdict_b(rms) == verdict
