"""modules/05_support_predictor/corpus/grid_response_blocked.py: the blocked grid response gives pyscf's gradient (one block and many
blocks per atom, GGA hybrid and LDA), its weights and weight derivatives equal pyscf's per atom, the block size follows the memory, the
unsupported cases raise, and the swap is undone after the block. Needs pyscf, so it runs in WSL and is skipped elsewhere."""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "modules" / "05_support_predictor" / "corpus"))
pytest.importorskip("pyscf")
GRB = pytest.importorskip("grid_response_blocked")

from pyscf import dft, gto  # noqa: E402
from pyscf.dft import gen_grid  # noqa: E402
from pyscf.grad import rks as rks_grad  # noqa: E402

WATER = "O 0 0 0; H 0 -0.757 0.587; H 0 0.757 0.587"
GRID = (50, 194)
TOL = 1e-10


def _scf(xc: str, displaced: bool = True) -> dft.rks.RKS:
    atom = WATER.replace("0.587; H", "0.600; H") if displaced else WATER      # off equilibrium: the grid response is not zero there
    mol = gto.M(atom=atom, basis="6-31g*", verbose=0)
    mf = dft.RKS(mol, xc=xc)
    mf.grids.atom_grid = GRID
    mf.grids.prune = None
    mf.conv_tol = 1e-12
    mf.kernel()
    return mf


def _gradient(mf: dft.rks.RKS) -> np.ndarray:
    return mf.nuc_grad_method().set(grid_response=True).kernel()


@pytest.mark.parametrize("xc", ["b3lyp", "lda,vwn"])
def test_the_blocked_gradient_equals_pyscfs_with_one_and_many_blocks(xc, monkeypatch):
    mf = _scf(xc)
    reference = _gradient(mf)
    with GRB.blocked_grid_response():
        one_block = _gradient(mf)
    monkeypatch.setattr(GRB, "block_size", lambda *_: gen_grid.BLKSIZE)        # 9,700 points per atom in blocks of BLKSIZE
    with GRB.blocked_grid_response():
        many_blocks = _gradient(mf)
    assert np.abs(one_block - reference).max() < TOL
    assert np.abs(many_blocks - reference).max() < TOL
    assert np.abs(reference - mf.nuc_grad_method().set(grid_response=False).kernel()).max() > 1e-7   # the term is there to test


def test_the_blocked_weights_and_derivatives_equal_pyscfs_per_atom():
    mf = _scf("b3lyp")
    grids = mf.grids
    pieces = list(GRB.grids_response_blocked(grids, 1000))
    for atom_id, (coords, w0, w1) in enumerate(rks_grad.grids_response_cc(grids)):
        mine = [p for p in pieces if p[0] == atom_id]
        assert len(mine) == -(-len(w0) // 1000)
        assert np.array_equal(np.concatenate([p[1] for p in mine]), coords)
        assert np.allclose(np.concatenate([p[2] for p in mine]), w0, rtol=0, atol=1e-14)
        assert np.allclose(np.concatenate([p[3] for p in mine], axis=-1), w1, rtol=0, atol=1e-14)


def test_the_block_size_follows_the_memory():
    small, large = GRB.block_size(38, 388, 2000), GRB.block_size(38, 388, 8000)
    assert small % gen_grid.BLKSIZE == 0 and large % gen_grid.BLKSIZE == 0
    assert 3 * small < large <= 4 * (small + gen_grid.BLKSIZE)
    assert GRB.block_size(500, 5000, 1) == gen_grid.BLKSIZE


def test_unsupported_cases_raise():
    mf = _scf("b3lyp", displaced=False)
    ni, mol, grids = mf._numint, mf.mol, mf.grids
    dm = mf.make_rdm1()
    with pytest.raises(NotImplementedError):
        GRB.get_vxc_full_response_blocked(ni, mol, grids, "tpss", dm)
    with pytest.raises(NotImplementedError):
        GRB.get_vxc_full_response_blocked(ni, mol, grids, "b3lyp", np.array([dm / 2, dm / 2]))
    grids.becke_scheme = gen_grid.becke_lko
    with pytest.raises(NotImplementedError):
        next(GRB.grids_response_blocked(grids, 100))
    grids.becke_scheme = gen_grid.original_becke
    with pytest.raises(ValueError):
        next(GRB.grids_response_blocked(grids, 0))


def test_the_swap_is_undone_after_the_block_and_after_an_error():
    original = rks_grad.get_vxc_full_response
    with GRB.blocked_grid_response():
        assert rks_grad.get_vxc_full_response is GRB.get_vxc_full_response_blocked
    assert rks_grad.get_vxc_full_response is original
    with pytest.raises(RuntimeError), GRB.blocked_grid_response():
        raise RuntimeError("inside")
    assert rks_grad.get_vxc_full_response is original
