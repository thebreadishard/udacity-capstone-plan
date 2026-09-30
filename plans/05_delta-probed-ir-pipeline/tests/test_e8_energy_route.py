"""Negative control for the energy route of the Hessian self-check (30 Sep 2026): on water, H_kk from gradients built with the CCSD lambda
(the 29 Sep incident) must disagree with the energy second difference beyond ENERGY_DIAG_LIMIT, and the correct (T)-lambda gradients must
agree well inside it. Needs pyscf (WSL / servers); slow (~1 min)."""
import sys
from pathlib import Path

import numpy as np
import pytest

pytest.importorskip("pyscf")
PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
import e8_hessian_checks as HC  # noqa: E402

pytestmark = pytest.mark.slow
X = np.array([[0.0, 0.0, 0.229980], [0.0, 1.418995, -0.919730], [0.0, -1.418995, -0.919730]])
H_STEP = 0.005


def _e_and_g(x, t_lambda):
    from pyscf import cc, gto, scf
    from pyscf.cc import ccsd_t_lambda
    from pyscf.grad import ccsd_t as ccsd_t_grad
    mol = gto.M(atom=[(s, tuple(c)) for s, c in zip("OHH", np.asarray(x).reshape(3, 3), strict=True)], unit="Bohr", basis="cc-pvdz", verbose=0)
    mf = scf.RHF(mol).run(conv_tol=1e-12)
    mycc = cc.CCSD(mf, frozen=1)
    mycc.conv_tol, mycc.conv_tol_normt = 1e-11, 1e-9
    eris = mycc.ao2mo()
    mycc.kernel(eris=eris)
    e = mycc.e_tot + mycc.ccsd_t(eris=eris)
    if t_lambda:
        _, l1, l2 = ccsd_t_lambda.kernel(mycc, eris, mycc.t1, mycc.t2, tol=1e-10)
    else:
        l1, l2 = mycc.solve_lambda(eris=eris)          # the incident: CCSD lambda handed to the (T) gradient
    return e, np.asarray(ccsd_t_grad.Gradients(mycc).kernel(mycc.t1, mycc.t2, l1, l2, eris)).ravel()


@pytest.mark.parametrize("t_lambda", [True, False])
def test_energy_route_separates_correct_and_ccsd_lambda_gradients(t_lambda):
    e0, _ = _e_and_g(X.ravel(), t_lambda)
    worst = 0.0
    for k in (2, 4, 5):                                 # O z, H1 y, H1 z
        xp, xm = X.ravel().copy(), X.ravel().copy()
        xp[k] += H_STEP
        xm[k] -= H_STEP
        ep, gp = _e_and_g(xp, t_lambda)
        em, gm = _e_and_g(xm, t_lambda)
        worst = max(worst, abs((gp[k] - gm[k]) / (2 * H_STEP) - (ep + em - 2 * e0) / H_STEP ** 2))
    if t_lambda:
        assert worst < HC.ENERGY_DIAG_LIMIT / 10, worst
    else:
        assert worst > HC.ENERGY_DIAG_LIMIT, worst
    print(f"t_lambda={t_lambda}: max |H_kk(gradients) - d2E(energies)| = {worst:.2e} E_h/bohr^2")
