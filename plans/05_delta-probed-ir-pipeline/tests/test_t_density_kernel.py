"""(T) density C kernel (probes/t_density_kernel): the intermediates equal pyscf's Python functions element-wise, and the
CCSD(T) gradient computed through the installed replacement equals pyscf's. Water RHF/cc-pVDZ, frozen core, no symmetry
and with C2v symmetry (the kernel does not sort by irrep, so both must agree). Skipped where pyscf or the built library is missing."""
import os
import sys

import numpy as np
import pytest

PLAN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PLAN, "probes", "t_density_kernel"))
import t_density_fast as F  # noqa: E402

pyscf = pytest.importorskip("pyscf")
pytestmark = pytest.mark.skipif(not F.available(), reason="ccsd_t_rdm_kernel.so not built (bash probes/t_density_kernel/build.sh)")

WATER = "O 0 0 0.1173; H 0 0.7572 -0.4692; H 0 -0.7572 -0.4692"


def _ccsd_t(symmetry):
    from pyscf import cc, gto, scf
    mol = gto.M(atom=WATER, basis="cc-pvdz", symmetry=symmetry, verbose=0)
    mf = scf.RHF(mol).run(conv_tol=1e-12)
    mycc = cc.CCSD(mf, frozen=1)
    mycc.conv_tol = 1e-11
    mycc.conv_tol_normt = 1e-9
    eris = mycc.ao2mo()
    mycc.kernel(eris=eris)
    from pyscf.cc import ccsd_t_lambda
    conv, l1, l2 = ccsd_t_lambda.kernel(mycc, eris, mycc.t1, mycc.t2, tol=1e-10)
    assert conv
    return mycc, eris, l1, l2


@pytest.mark.parametrize("symmetry", [False, True])
def test_intermediates_match_pyscf_to_1e_10(symmetry):
    mycc, eris, l1, l2 = _ccsd_t(symmetry)
    F.uninstall()
    diffs = F.check_against_pyscf(mycc, mycc.t1, mycc.t2, l1, l2, eris)
    assert diffs, "no intermediates compared"
    worst = max(diffs, key=diffs.get)
    assert diffs[worst] < 1e-10, diffs


def test_kernel_terms_are_nonzero_and_cached():
    mycc, eris, l1, l2 = _ccsd_t(False)
    t = F.kernel(mycc.t1, mycc.t2, eris)
    assert all(np.max(np.abs(t[k])) > 1e-8 for k in ("goo", "gvv", "dvo", "dovov", "dooov", "dovvv")), {k: float(np.max(np.abs(v))) for k, v in t.items()}
    a = F._cached(mycc.t1, mycc.t2, eris)
    assert F._cached(mycc.t1, mycc.t2, eris) is a


def test_gradient_through_installed_replacement_matches_pyscf():
    from pyscf import cc, gto, scf
    mol = gto.M(atom=WATER, basis="cc-pvdz", symmetry=False, verbose=0)
    mf = scf.RHF(mol).run(conv_tol=1e-12)
    mycc = cc.CCSD(mf, frozen=1)
    mycc.conv_tol, mycc.conv_tol_normt = 1e-11, 1e-9
    mycc.kernel()
    mycc.ccsd_t()
    from pyscf.grad import ccsd_t as ccsd_t_grad
    F.uninstall()
    g_ref = ccsd_t_grad.Gradients(mycc).kernel()
    F.install()
    try:
        g_new = ccsd_t_grad.Gradients(mycc).kernel()
    finally:
        F.uninstall()
    assert np.max(np.abs(g_new - g_ref)) < 1e-8, np.max(np.abs(g_new - g_ref))
