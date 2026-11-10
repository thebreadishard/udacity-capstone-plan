"""probes/anchor_oop_check.py on synthetic records, before any TASKS 184 number is read: the rows from gradient files, the refusals (another
geometry, a non-planar Hessian), the truth anchor's round trip, the leave-one-out residual and the registered lines at their edges. The family
read itself is pinned on real data by `anchor_oop_check.py pin` (test 2 reproduced)."""
from __future__ import annotations

import json
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


def _rows_file(path: Path, basis: str, method: str | None, ks=(2, 20)) -> Path:
    extra = {} if method is None else {"method": method}
    np.savez(path, ks=np.array(ks), reps=np.array([0, 6]), step=0.005, basis=basis, frozen=6, cart=False, **extra)
    return path


def test_df_files_on_the_conventional_plan_pass_and_others_are_refused(tmp_path):
    conv = _rows_file(tmp_path / "conv.npz", "cc-pvtz", None)
    tz = _rows_file(tmp_path / "tz.npz", "cc-pvtz", "DF-MP2 psi4 1.10.2")
    qz = _rows_file(tmp_path / "qz.npz", "cc-pvqz", "DF-MP2 psi4 1.10.2")
    A.check_df_files(conv, tz, qz)
    for bad, match in ((_rows_file(tmp_path / "b1.npz", "cc-pvqz", None), "not a DF-MP2"),
                       (_rows_file(tmp_path / "b2.npz", "cc-pvtz", "DF-MP2 x"), "basis"),
                       (_rows_file(tmp_path / "b3.npz", "cc-pvqz", "DF-MP2 x", ks=(2, 5)), "ks differs")):
        with pytest.raises(SystemExit, match=match):
            A.check_df_files(conv, tz, bad)


def test_the_df_error_is_zero_for_equal_rows_and_refused_past_the_line():
    rng = np.random.default_rng(3)
    x0 = np.array([[0.0, 0.0, 0.0], [2.6, 0.0, 0.0], [0.0, 2.6, 0.0], [2.6, 2.6, 0.0]])
    masses = np.array([12.0, 1.0, 1.0, 12.0])
    H = _planar(4, rng)
    H = H @ H.T                                  # positive: real frequencies
    M = _planar(4, rng)
    assert A.df_error_cm(H, np.eye(3), M, M, masses, x0) == 0.0
    zi, _ = A.C.oop_indices(4)
    M_df = M.copy()
    M_df[np.ix_(zi, zi)] += 0.05
    err = A.df_error_cm(H, np.eye(3), M, M_df, masses, x0)
    assert err > A.DF_LINE_CM
    A.require_df_line(A.DF_LINE_CM)
    with pytest.raises(SystemExit, match="not read"):
        A.require_df_line(err)


def test_rows_of_unchecked_kernels_are_refused_until_the_check_passes(tmp_path):
    coords = np.zeros((2, 3))
    run = _run_dir(tmp_path, coords, {2: np.ones(6)})
    np.savez(run / "reference.npz", coords_bohr=coords, two_route_checked=False)
    with pytest.raises(SystemExit, match="unchecked"):
        A.write_cc_rows(run, [2], coords, tmp_path / "rows.npz")
    (run / A.HC.TWO_ROUTE_FILE).write_text(json.dumps({"passed": True}), encoding="utf-8")
    assert A.write_cc_rows(run, [2], coords, tmp_path / "rows.npz").exists()
