"""Frozen LNO spaces (probes/lno_frozen_spaces.py, 3 Oct 2026). Fast part: the linear algebra (orthonormalisation, complement, semi-canonical
rotation) on random matrices. Slow part (pyscf, marked slow, run under the WSL `qc05` environment): on water, (1) a replay at the reference geometry
reproduces the fresh LNO-CCSD(T) composite energy — the spaces are the same, so the energy must be, to the solver's tolerance; (2) a replay at a
displaced geometry runs, carries the same number of active orbitals per fragment, and lands within 2e-5 E_h of the fresh energy at that geometry
(a 0.005-bohr displacement changes the domains very little; the difference is what cell (b) measures on naphthalene)."""
import os
import sys
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE / "probes"))
import lno_frozen_spaces as FS  # noqa: E402

rng = np.random.default_rng(0)


def test_lowdin_columns_orthonormal_and_span_preserved():
    u = rng.normal(size=(9, 4))
    q = FS._lowdin_columns(u)
    assert np.allclose(q.T @ q, np.eye(4), atol=1e-12)
    # same column space: projector equality
    p_u = u @ np.linalg.pinv(u)
    p_q = q @ q.T
    assert np.allclose(p_u, p_q, atol=1e-10)
    with pytest.raises(ValueError):
        FS._lowdin_columns(np.hstack((u[:, :1], u[:, :1])))               # rank-deficient block is refused


def test_complement_is_orthonormal_and_orthogonal():
    u = FS._lowdin_columns(rng.normal(size=(9, 4)))
    c = FS._complement(u, 9)
    assert c.shape == (9, 5) and np.allclose(c.T @ c, np.eye(5), atol=1e-12) and np.allclose(c.T @ u, 0, atol=1e-12)


def test_semicanonical_diagonalises_fock_in_block():
    e = np.sort(rng.normal(size=9))
    u = FS._lowdin_columns(rng.normal(size=(9, 4)))
    v = FS._semicanonical(u, e)
    f = v.T @ np.diag(e) @ v
    assert np.allclose(f - np.diag(np.diag(f)), 0, atol=1e-12) and np.allclose(v.T @ v, np.eye(4), atol=1e-12)
    assert np.allclose(v @ v.T, u @ u.T, atol=1e-12)                      # a rotation inside the block, the space unchanged


def test_store_roundtrip(tmp_path):
    frags = [{"orbfrag": rng.normal(size=(7, 7)), "frzfrag": np.array([0, 6]), "uloc": rng.normal(size=(2, 1))} for _ in range(3)]
    store = {"lo_coeff": rng.normal(size=(7, 3)), "frags": frags}
    p = str(tmp_path / "s.npz")
    FS.save_store(p, store)
    back = FS.load_store(p)
    assert len(back["frags"]) == 3 and np.allclose(back["lo_coeff"], store["lo_coeff"]) and np.array_equal(back["frags"][1]["frzfrag"], np.array([0, 6]))


@pytest.mark.slow
def test_water_replay_reproduces_reference_and_runs_displaced():
    pytest.importorskip("pyscf")
    pytest.importorskip("pyscf.lno")
    import l2_lno_price as L2
    from pyscf import lib
    lib.num_threads(int(os.environ.get("OMP_NUM_THREADS", "2")))
    L2.TIER = "t0"
    sym = ["O", "H", "H"]
    x0 = np.array([[0.0, 0.0, 0.2217], [0.0, 1.4309, -0.8867], [0.0, -1.4309, -0.8867]])   # bohr, the water of the gate-1 acceptance test
    out = str(HERE / "probes" / "results_m1" / "lno_frozen_spaces_water_test")
    os.makedirs(out, exist_ok=True)
    store = {}
    ref = L2.point(sym, x0, "cc-pvdz", "tight", 1, 2000, out, "ref_capture", spaces={"mode": "capture", "store": store})
    assert len(store["frags"]) == 4 and store["lo_coeff"].shape[1] == 4
    same = L2.point(sym, x0, "cc-pvdz", "tight", 1, 2000, out, "ref_replay", spaces={"mode": "replay", "store": store})
    assert abs(same["e_tot_composite"] - ref["e_tot_composite"]) < 1e-8, (same["e_tot_composite"], ref["e_tot_composite"])
    x1 = x0.copy()
    x1[0, 2] += 0.005
    fresh = L2.point(sym, x1, "cc-pvdz", "tight", 1, 2000, out, "disp_fresh")
    reused = L2.point(sym, x1, "cc-pvdz", "tight", 1, 2000, out, "disp_replay", spaces={"mode": "replay", "store": store})
    d = reused["e_tot_composite"] - fresh["e_tot_composite"]
    print(f"water: ref {ref['e_tot_composite']:.9f} replay-at-ref Δ {same['e_tot_composite'] - ref['e_tot_composite']:+.2e}; "
          f"displaced fresh {fresh['e_tot_composite']:.9f} reused Δ {d:+.2e}")
    assert abs(d) < 2e-5, d
