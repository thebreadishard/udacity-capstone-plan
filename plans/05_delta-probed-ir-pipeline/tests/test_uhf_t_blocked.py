"""probes/t_density_kernel/uhf_t_blocked.py against pyscf's own UHF CCSD(T) code, element by element, on the open-shell molecules of the
design note of 23 Oct 2026: H₂O⁺ (doublet), NO (doublet) and triplet water, all-electron and frozen core, with block sizes that do and do not
divide the virtual counts (edge blocks and the one-block case). The (T) lambda against `uccsd_t_lambda.make_intermediates`, γ1 against
`uccsd_t_rdm._gamma1_intermediates` (for_grad both ways), γ2 against `uccsd_t_rdm._gamma2_intermediates` uncompressed, and compressed against
the same with the E8 probe's dvvVV fix (pyscf#3305/#3387); the out-of-core γ2 (`uccsd_gamma2_outcore`, v⁴ blocks in an HDF5 file, slabs of
one, three and all virtual indices) against pyscf's in-core UCCSD and (T) γ2. Runs where pyscf is installed (WSL ~/qc05)."""
import sys
from pathlib import Path

import numpy as np
import pytest

pyscf = pytest.importorskip("pyscf")
from pyscf import cc, gto, lib, scf  # noqa: E402
from pyscf.cc import uccsd_rdm, uccsd_t_lambda, uccsd_t_rdm  # noqa: E402

PROBES = Path(__file__).resolve().parent.parent / "probes"
sys.path.insert(0, str(PROBES / "t_density_kernel"))
sys.path.insert(0, str(PROBES))
import uccsd_gamma2_outcore as O  # noqa: E402
import uhf_t_blocked as U  # noqa: E402

TOL = 1e-12
BLOCKS = [1, 3, 5, U.BLOCK]
LAMBDA_FIELDS = ("l1a_t", "l1b_t", "l2aa_t", "l2ab_t", "l2bb_t")
MOLECULES = {
    "H2O+": dict(atom="O 0 0 0; H 0 -0.757 0.587; H 0 0.757 0.587", charge=1, spin=1),
    "NO": dict(atom="N 0 0 0; O 0 0 1.15", charge=0, spin=1),
    "triplet H2O": dict(atom="O 0 0 0; H 0 -0.757 0.587; H 0 0.757 0.587", charge=0, spin=2),
}


@pytest.fixture(scope="module", params=[(m, f) for m in MOLECULES for f in (0, 1)], ids=lambda p: f"{p[0]}-frozen{p[1]}")
def case(request):
    name, frozen = request.param
    mol = gto.M(basis="6-31g", verbose=0, **MOLECULES[name])
    mf = scf.UHF(mol).run(conv_tol=1e-12)
    mycc = cc.UCCSD(mf, frozen=frozen).run(conv_tol=1e-10)
    l1, l2 = mycc.solve_lambda()
    return mycc, mycc.ao2mo(), l1, l2


def close(ref, got, what: str) -> None:
    ref, got = np.asarray(ref), np.asarray(got)
    assert np.abs(ref).max() > 1e-8, f"{what}: the reference is zero, so the comparison would prove nothing"
    assert np.abs(got - ref).max() <= TOL * max(1.0, np.abs(ref).max()), f"{what}: max |Δ| {np.abs(got - ref).max():.3g}"


def nested_close(ref, got, what: str) -> None:
    """pyscf's tuples of tuples of arrays (None where a block is not formed), compared array by array."""
    for k, (r, g) in enumerate(zip(ref, got, strict=True)):
        if isinstance(r, tuple):
            nested_close(r, g, f"{what}[{k}]")
        elif r is None:
            assert g is None, f"{what}[{k}]: pyscf has no block here"
        else:
            close(r, g, f"{what}[{k}]")


@pytest.mark.parametrize("block", BLOCKS)
def test_the_lambda_intermediates_equal_pyscf(case, block):
    mycc, eris, _, _ = case
    ref = uccsd_t_lambda.make_intermediates(mycc, mycc.t1, mycc.t2, eris)
    got = U.make_intermediates(mycc, mycc.t1, mycc.t2, eris, block=block)
    for f in LAMBDA_FIELDS:
        close(getattr(ref, f), getattr(got, f), f)


@pytest.mark.parametrize("for_grad", [False, True])
@pytest.mark.parametrize("block", BLOCKS)
def test_gamma1_equals_pyscf(case, block, for_grad):
    mycc, eris, l1, l2 = case
    ref = uccsd_t_rdm._gamma1_intermediates(mycc, mycc.t1, mycc.t2, l1, l2, eris, for_grad=for_grad)
    got = U.gamma1_intermediates(mycc, mycc.t1, mycc.t2, l1, l2, eris, for_grad=for_grad, block=block)
    nested_close(ref, got, "d1")


@pytest.mark.parametrize("block", BLOCKS)
def test_gamma2_equals_pyscf_uncompressed(case, block):
    mycc, eris, l1, l2 = case
    ref = uccsd_t_rdm._gamma2_intermediates(mycc, mycc.t1, mycc.t2, l1, l2, eris, compress_vvvv=False)
    got = U.gamma2_intermediates(mycc, mycc.t1, mycc.t2, l1, l2, eris, compress_vvvv=False, block=block)
    nested_close(ref, got, "d2")


def test_gamma2_compressed_equals_pyscf_with_the_dvvvv_fix(case, monkeypatch):
    import e8_cc_hessian_fd as E8
    mycc, eris, l1, l2 = case
    monkeypatch.setattr(uccsd_t_rdm, "_gamma2_intermediates", uccsd_t_rdm._gamma2_intermediates)   # undone after the test
    E8.install_uccsd_t_dvvvv_fix()
    ref = uccsd_t_rdm._gamma2_intermediates(mycc, mycc.t1, mycc.t2, l1, l2, eris, compress_vvvv=True)
    got = U.gamma2_intermediates(mycc, mycc.t1, mycc.t2, l1, l2, eris, compress_vvvv=True)
    nested_close(ref, got, "d2")


def test_a_block_below_one_is_refused(case):
    mycc, eris, l1, l2 = case
    for call in (lambda: U.make_intermediates(mycc, mycc.t1, mycc.t2, eris, block=0),
                 lambda: U.gamma1_intermediates(mycc, mycc.t1, mycc.t2, l1, l2, eris, block=0),
                 lambda: U.gamma2_intermediates(mycc, mycc.t1, mycc.t2, l1, l2, eris, block=0)):
        with pytest.raises(ValueError, match="at least one virtual index"):
            call()


def slab_mb(nvir: int, per_slab: int) -> float:
    """The memory that gives `per_slab` virtual indices per slab for a molecule with nvir α virtuals (O._slab's inverse)."""
    return per_slab * 2 * 8 * nvir ** 3 / 1e6 * 1.0001


def read_back(d2):
    """The out-of-core d2 with its HDF5 datasets read into arrays."""
    return tuple(tuple(None if x is None else np.asarray(x[:]) for x in group) for group in d2)


@pytest.mark.parametrize("per_slab", [1, 3, None])
def test_uccsd_gamma2_outcore_equals_pyscf(case, per_slab):
    mycc, _, l1, l2 = case
    nvira = mycc.t2[1].shape[2]
    mb = O.V4_SLAB_MB if per_slab is None else slab_mb(nvira, per_slab)
    h5 = lib.H5TmpFile()                                       # held: the datasets live in it
    got = read_back(O.gamma2_outcore(mycc, mycc.t1, mycc.t2, l1, l2, h5, True, mb))
    nested_close(uccsd_rdm._gamma2_intermediates(mycc, mycc.t1, mycc.t2, l1, l2, compress_vvvv=True), got, "d2")


def test_t_gamma2_outcore_equals_pyscf_with_the_dvvvv_fix(case, monkeypatch):
    import e8_cc_hessian_fd as E8
    mycc, eris, l1, l2 = case
    monkeypatch.setattr(uccsd_t_rdm, "_gamma2_intermediates", uccsd_t_rdm._gamma2_intermediates)
    E8.install_uccsd_t_dvvvv_fix()
    ref = uccsd_t_rdm._gamma2_intermediates(mycc, mycc.t1, mycc.t2, l1, l2, eris, compress_vvvv=True)
    h5 = lib.H5TmpFile()
    got = read_back(U.gamma2_outcore(mycc, mycc.t1, mycc.t2, l1, l2, eris, h5, True, block=3,
                                     slab_mb=slab_mb(mycc.t2[1].shape[2], 2)))
    nested_close(ref, got, "d2")


def test_the_outcore_path_refuses_the_uncompressed_form(case):
    mycc, _, l1, l2 = case
    with pytest.raises(ValueError, match="compress_vvvv=False is the in-core path"):
        O.gamma2_outcore(mycc, mycc.t1, mycc.t2, l1, l2, lib.H5TmpFile(), False)
