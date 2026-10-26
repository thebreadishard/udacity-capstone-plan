"""probes/t_density_kernel/uhf_t_blocked.py against pyscf's own `uccsd_t_lambda.make_intermediates`, element by element, on the open-shell
molecules of the design note of 23 Oct 2026: H₂O⁺ (doublet), NO (doublet) and triplet water, all-electron and frozen core, with block sizes
that do and do not divide the virtual counts (edge blocks and the one-block case). Runs where pyscf is installed (WSL ~/qc05)."""
import sys
from pathlib import Path

import numpy as np
import pytest

pyscf = pytest.importorskip("pyscf")
from pyscf import cc, gto, scf  # noqa: E402
from pyscf.cc import uccsd_t_lambda  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "probes" / "t_density_kernel"))
import uhf_t_blocked as U  # noqa: E402

TOL = 1e-12
FIELDS = ("l1a_t", "l1b_t", "l2aa_t", "l2ab_t", "l2bb_t")
MOLECULES = {
    "H2O+": dict(atom="O 0 0 0; H 0 -0.757 0.587; H 0 0.757 0.587", charge=1, spin=1),
    "NO": dict(atom="N 0 0 0; O 0 0 1.15", charge=0, spin=1),
    "triplet H2O": dict(atom="O 0 0 0; H 0 -0.757 0.587; H 0 0.757 0.587", charge=0, spin=2),
}


def converged(name: str, frozen: int):
    mol = gto.M(basis="6-31g", verbose=0, **MOLECULES[name])
    mf = scf.UHF(mol).run(conv_tol=1e-12)
    mycc = cc.UCCSD(mf, frozen=frozen).run(conv_tol=1e-10)
    return mycc, mycc.ao2mo()


@pytest.fixture(scope="module", params=[(m, f) for m in MOLECULES for f in (0, 1)], ids=lambda p: f"{p[0]}-frozen{p[1]}")
def case(request):
    mycc, eris = converged(*request.param)
    return mycc, eris, uccsd_t_lambda.make_intermediates(mycc, mycc.t1, mycc.t2, eris)


@pytest.mark.parametrize("block", [1, 3, 5, U.BLOCK])
def test_the_blocked_intermediates_equal_pyscf(case, block):
    mycc, eris, ref = case
    got = U.make_intermediates(mycc, mycc.t1, mycc.t2, eris, block=block)
    for f in FIELDS:
        r, g = getattr(ref, f), getattr(got, f)
        assert np.abs(r).max() > 1e-8, f"{f}: the reference is zero, so the comparison would prove nothing"
        assert np.abs(g - r).max() <= TOL * max(1.0, np.abs(r).max()), f"{f}: max |Δ| {np.abs(g - r).max():.3g}"


def test_a_block_below_one_is_refused(case):
    mycc, eris, _ = case
    with pytest.raises(ValueError, match="at least one virtual index"):
        U.make_intermediates(mycc, mycc.t1, mycc.t2, eris, block=0)
