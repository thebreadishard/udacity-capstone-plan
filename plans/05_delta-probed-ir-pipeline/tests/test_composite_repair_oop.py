"""Test 3 of the composite anchor level (6 Oct 2026): the out-of-plane repair. planeframe puts a tilted planar molecule flat (z = 0) and names the
representatives' z displacements; merge joins lane files; repair-oop leaves the anchor untouched when the MP2 step is zero, changes only the
out-of-plane block otherwise, and reports the frequencies. No quantum chemistry: synthetic Hessians on a planar formaldehyde-shaped molecule (C2v)."""
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

pytest.importorskip("torch")                     # repair-oop's frequencies use anchor_deck_rehearsal.project_tr (module 05's python)
PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
import cc_composite_full_check as C  # noqa: E402
import e8_symmetry as SYM  # noqa: E402

SYMS = ["C", "O", "H", "H"]
FLAT = np.array([[0.0, 0.0, 0.0], [0.0, 2.3, 0.0], [1.8, -1.1, 0.0], [-1.8, -1.1, 0.0]])
MASSES = np.array([12.0, 15.995, 1.008, 1.008])
N = 4
ZI = np.arange(2, 3 * N, 3)
IP = np.array([k for k in range(3 * N) if k % 3 != 2])


def _tilted(x, seed=3):
    rng = np.random.default_rng(seed)
    q, _ = np.linalg.qr(rng.normal(size=(3, 3)))
    if np.linalg.det(q) < 0:
        q[:, 0] *= -1
    return x @ q.T + np.array([0.7, -0.4, 2.0])


def _write_geometry(path, x):
    path.write_text(json.dumps(dict(symbols=SYMS, coords_bohr=np.asarray(x).tolist(), masses_amu=MASSES.tolist())), encoding="utf-8")


def _spd_hessian(rng, oop_scale=0.05):
    """A symmetric positive Hessian in the plane frame with no in-plane/out-of-plane coupling (what symmetry imposes on a planar molecule)."""
    A = rng.normal(size=(3 * N, 3 * N))
    H = A @ A.T + 3 * N * np.eye(3 * N)
    H[np.ix_(ZI, IP)] = 0.0
    H[np.ix_(IP, ZI)] = 0.0
    H[np.ix_(ZI, ZI)] *= oop_scale
    return H


def _rows_npz(path, H_r, reps, scale=1.0):
    rows = {f"row_{3 * i + 2:02d}": scale * H_r[3 * i + 2] for i in reps}
    np.savez(path, ks=np.array([3 * i + 2 for i in reps]), step=0.005, basis="x", **rows)


def test_planeframe_flattens_and_names_the_out_of_plane_displacements(tmp_path):
    g = tmp_path / "g.json"
    out = tmp_path / "pf.json"
    _write_geometry(g, _tilted(FLAT))
    assert C.planeframe(SimpleNamespace(geometry=str(g), out=str(out))) == 0
    pf = json.loads(out.read_text(encoding="utf-8"))
    xr = np.asarray(pf["coords_bohr"])
    V = np.asarray(pf["frame"])
    assert np.abs(xr[:, 2]).max() < 1e-9 and abs(np.linalg.det(V) - 1) < 1e-9
    reps = SYM.unique_displacements(SYM.point_group_ops(SYMS, xr), N)[1]
    assert pf["oop_ks"] == [3 * i + 2 for i in reps]
    assert all(k % 3 == 2 for k in pf["oop_ks"]) and len(pf["oop_ks"]) == 3    # three orbits: C, O, the H pair


def test_merge_joins_rows(tmp_path):
    a, b, out = tmp_path / "a.npz", tmp_path / "b.npz", tmp_path / "m.npz"
    np.savez(a, ks=np.array([2]), step=0.005, basis="x", row_02=np.ones(12))
    np.savez(b, ks=np.array([8]), step=0.005, basis="x", row_08=2 * np.ones(12))
    assert C.merge(SimpleNamespace(out=str(out), parts=[str(a), str(b)])) == 0
    z = np.load(out)
    assert list(z["ks"]) == [2, 8] and float(z["row_08"][0]) == 2.0 and str(z["basis"]) == "x"


def _setup(tmp_path, tz_scale):
    rng = np.random.default_rng(11)
    x_tilt = _tilted(FLAT)
    V, origin = C.plane_frame(x_tilt)
    xr = (x_tilt - origin) @ V
    ops = SYM.point_group_ops(SYMS, xr)
    _, reps = SYM.unique_displacements(ops, N)
    H_r = _spd_hessian(rng)
    H_r = SYM.reconstruct({i: H_r[3 * i:3 * i + 3] for i in reps}, ops, N)[0]      # symmetry-consistent
    H_r = 0.5 * (H_r + H_r.T)
    T = np.kron(np.eye(N), V)
    H = T @ H_r @ T.T
    anchor = tmp_path / "anchor"
    anchor.mkdir()
    np.savez(anchor / "hessian_ccsd_t_IMAGINARY.npz", H_raw=H, coords_bohr=x_tilt, freq_cm=np.zeros(6))
    pf = tmp_path / "pf.json"
    g = tmp_path / "g.json"
    _write_geometry(g, x_tilt)
    C.planeframe(SimpleNamespace(geometry=str(g), out=str(pf)))
    _rows_npz(tmp_path / "dz.npz", H_r, reps, 1.0)
    _rows_npz(tmp_path / "tz.npz", H_r, reps, tz_scale)
    args = SimpleNamespace(anchor_dir=str(anchor), mol_id="none", planeframe=str(pf), mp2_dz=str(tmp_path / "dz.npz"), mp2_tz=str(tmp_path / "tz.npz"),
                           out_prefix=str(tmp_path / "rep"))
    return args, H, H_r, V


def test_zero_step_leaves_the_anchor_unchanged(tmp_path):
    args, H, _, _ = _setup(tmp_path, tz_scale=1.0)
    assert C.repair_oop(args) == 0
    z = np.load(tmp_path / "rep.npz")
    assert np.abs(z["H_raw"] - H).max() < 1e-10 and str(z["status"]) == "VALID"
    rec = json.loads((tmp_path / "rep.json").read_text(encoding="utf-8"))
    assert rec["coupling"]["anchor"] < 1e-10 and rec["coupling"]["step"] < 1e-12
    assert np.allclose(rec["freq_dz"], rec["freq_composite"])


def test_step_changes_only_the_out_of_plane_block(tmp_path):
    args, H, H_r, V = _setup(tmp_path, tz_scale=3.0)
    C.repair_oop(args)
    z = np.load(tmp_path / "rep.npz")
    T = np.kron(np.eye(N), V)
    D = T.T @ (z["H_raw"] - H) @ T                                      # the change, back in the plane frame
    assert np.abs(D[np.ix_(IP, IP)]).max() < 1e-10 and np.abs(D[np.ix_(ZI, IP)]).max() < 1e-10
    assert np.abs(D[np.ix_(ZI, ZI)] - 2.0 * H_r[np.ix_(ZI, ZI)]).max() < 1e-8   # step = (3 − 1) × the DZ out-of-plane block
    rec = json.loads((tmp_path / "rep.json").read_text(encoding="utf-8"))
    assert "repaired" in rec["verdict"]                                  # no corpus DFT values for mol_id 'none' → 'repaired but flagged'


def test_build_full_composite_in_the_plane_frame(tmp_path, monkeypatch):
    """The full composite: zero step reproduces the anchor; a step of (s − 1) × the DZ rows adds exactly that, rotated back from the plane frame."""
    rng = np.random.default_rng(5)
    x_tilt = _tilted(FLAT)
    V, origin = C.plane_frame(x_tilt)
    xr = (x_tilt - origin) @ V
    ops = SYM.point_group_ops(SYMS, xr)
    ks, reps = SYM.unique_displacements(ops, N)
    H_r = _spd_hessian(rng)
    H_r = SYM.reconstruct({i: H_r[3 * i:3 * i + 3] for i in reps}, ops, N)[0]
    H_r = 0.5 * (H_r + H_r.T)
    T = np.kron(np.eye(N), V)
    H = T @ H_r @ T.T
    plan = tmp_path / "plan"
    mol = plan / "modules" / "05_support_predictor" / "corpus" / "molecules" / "M_test"
    mol.mkdir(parents=True)
    _write_geometry(mol / "geometry.json", x_tilt)
    monkeypatch.setattr(C, "PLAN", plan)
    anchor = tmp_path / "anchor.npz"
    np.savez(anchor, H_raw=H, coords_bohr=x_tilt)
    pf = tmp_path / "pf.json"
    C.planeframe(SimpleNamespace(geometry=str(mol / "geometry.json"), out=str(pf)))
    for name, s in (("dz", 1.0), ("tz", 2.5)):
        np.savez(tmp_path / f"{name}.npz", ks=np.array(ks), coords_bohr=xr, step=0.005, basis=name, **{f"row_{k:02d}": s * H_r[k] for k in ks})
    args = SimpleNamespace(anchor=str(anchor), mol_id="M_test", mp2_dz=str(tmp_path / "dz.npz"), mp2_tz=str(tmp_path / "tz.npz"),
                           out_prefix=str(tmp_path / "comp"), planeframe=str(pf))
    assert C.build(args) == 0
    z = np.load(tmp_path / "comp.npz")
    assert np.abs(z["H_raw"] - (H + 1.5 * H)).max() < 1e-8 and str(z["status"]) == "VALID" and "H_projected" in z.files
    np.savez(tmp_path / "far.npz", ks=np.array(ks), coords_bohr=xr + 0.1, step=0.005, basis="x", **{f"row_{k:02d}": H_r[k] for k in ks})
    with pytest.raises(SystemExit, match="other coordinates"):
        C.build(SimpleNamespace(**{**vars(args), "mp2_tz": str(tmp_path / "far.npz")}))
