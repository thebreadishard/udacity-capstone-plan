"""probes/qff_pm_saving.py on exactly symmetric data: staggered ethane under a Morse pair potential (D3d, no integration grid), so every
image Hessian must equal the directly computed one, and the force field assembled with images must equal the direct one."""
import itertools
import json
import os
import sys

import numpy as np
import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(ROOT, "probes"))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.dirname(__file__))
import qff_pm_saving as P  # noqa: E402

from dpir.qff import harmonic, load_results, qff_from_records  # noqa: E402
from test_qff_symmetry_rebuild import _ethane, _hessian, _write  # noqa: E402

DISP = 0.10


def _load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _pairs(x0):
    n = len(x0)
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    return pairs, [np.linalg.norm(x0[i] - x0[j]) for i, j in pairs]


def _stubs(tmp_path):
    """The reference record and every ±d stub, as make_qff_displacements.py names them."""
    sym, x0 = _ethane()
    pairs, r0 = _pairs(x0)
    H0 = _hessian(x0, pairs, r0)
    harm = harmonic(H0, sym, x0.ravel())
    stubs = tmp_path / "stubs"
    stubs.mkdir()
    _write(tmp_path / "ref.json", sym, x0, H0)
    _write(stubs / "ref.json", sym, x0, H0)
    for k in range(harm.A.shape[1]):
        for s, tag in ((1, "p"), (-1, "m")):
            _write(stubs / f"mode{k:02d}_{tag}.json", sym, x0 + s * DISP * harm.A[:, k].reshape(-1, 3), np.zeros((3 * len(sym),) * 2))
    return sym, x0, pairs, r0, stubs


def _compute(src_dir, hess_dir, sym, pairs, r0):
    hess_dir.mkdir(exist_ok=True)
    for name in sorted(os.listdir(src_dir)):
        x = np.array(_load(src_dir / name)["molecule"]["geometry"]).reshape(-1, 3)
        _write(hess_dir / name, sym, x, _hessian(x, pairs, r0))


def test_images_equal_the_direct_hessians_and_the_force_field(tmp_path):
    sym, _x0, pairs, r0, stubs = _stubs(tmp_path)
    summary = P.write_plan(str(tmp_path / "ref.json"), str(stubs), str(tmp_path / "compute"))
    assert summary["images"] > 0 and summary["computed"] + summary["images"] == summary["stubs"]
    _compute(tmp_path / "compute", tmp_path / "hess", sym, pairs, r0)
    assert P.fill_images(str(tmp_path / "hess"), str(stubs), str(tmp_path / P.IMAGES_NAME)) == summary["images"]
    assert P.fill_images(str(tmp_path / "hess"), str(stubs), str(tmp_path / P.IMAGES_NAME)) == 0      # resumed: nothing rewritten
    _compute(stubs, tmp_path / "direct", sym, pairs, r0)
    for name in _load(tmp_path / P.IMAGES_NAME)["images"]:
        a = np.array(_load(tmp_path / "hess" / name)["return_result"])
        b = np.array(_load(tmp_path / "direct" / name)["return_result"])
        assert np.abs(a - b).max() < 1e-10 * np.abs(b).max()
    q_i = qff_from_records(load_results(str(tmp_path / "hess")), DISP, allow_noisy=True)[0]
    q_d = qff_from_records(load_results(str(tmp_path / "direct")), DISP, allow_noisy=True)[0]
    assert np.abs(q_i.phi4 - q_d.phi4).max() < 1e-8 * np.abs(q_d.phi4).max()


def test_totally_symmetric_modes_are_computed_both_ways(tmp_path):
    sym, x0, pairs, r0, stubs = _stubs(tmp_path)
    images = P.plan_images(str(tmp_path / "ref.json"), str(stubs))
    harm = harmonic(_hessian(x0, pairs, r0), sym, x0.ravel())
    d = harm.A.T.reshape(harm.A.shape[1], -1, 3)
    ops = P.point_group_ops(sym, x0, tol=P.OPS_TOL)
    symmetric = [k for k in range(len(d)) if all(np.allclose(P.image_geometry(d[k], np.zeros(3), R, p), d[k], atol=1e-8) for R, p in ops)]
    assert symmetric and all(f"mode{k:02d}_m.json" not in images for k in symmetric)
    assert all(v["grid_compatible"] or v["residual"] < P.REL_TOL for v in images.values())


def test_the_lanes_hold_every_stub_once_and_a_resplit_must_agree(tmp_path):
    src = tmp_path / "compute"
    src.mkdir()
    for k in range(7):
        (src / f"mode{k:02d}_p.json").write_text("{}", encoding="utf-8")
    lanes = P.split_lanes(str(src), str(tmp_path / "lanes"), 3)
    assert sorted(itertools.chain(*lanes)) == sorted(os.listdir(src)) and [len(x) for x in lanes] == [3, 2, 2]
    assert P.split_lanes(str(src), str(tmp_path / "lanes"), 3) == lanes
    with pytest.raises(ValueError, match="another split"):
        P.split_lanes(str(src), str(tmp_path / "lanes"), 2)


def test_symmetrize_restores_the_group_once_and_refuses_a_large_move(tmp_path):
    sym, x0 = _ethane()
    x = x0 + np.random.default_rng(0).normal(scale=1e-4, size=x0.shape)
    _write(tmp_path / "s.json", sym, x, np.zeros((3 * len(sym),) * 2))
    info = P.symmetrize_stub(str(tmp_path / "s.json"))
    assert info["group_order"] == 12 and info["max_move_bohr"] < 1e-3                   # D3d
    before = (tmp_path / "s.json").read_bytes()
    assert P.symmetrize_stub(str(tmp_path / "s.json")) == info and (tmp_path / "s.json").read_bytes() == before
    x = x0.copy()
    x[2, 0] += 0.015
    _write(tmp_path / "far.json", sym, x, np.zeros((3 * len(sym),) * 2))
    with pytest.raises(ValueError, match="moves an atom"):
        P.symmetrize_stub(str(tmp_path / "far.json"))
