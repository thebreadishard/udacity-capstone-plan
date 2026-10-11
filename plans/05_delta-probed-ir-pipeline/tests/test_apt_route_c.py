"""TASKS 44 route C (11 Oct 2026): the APT from the response the analytic Hessian solves equals the APT from a second CPHF solve (route B), on
water at a small grid; and the capture leaves the Hessian unchanged. Needs pyscf, so it runs in WSL (like test_acceptance_water.py) and is
skipped elsewhere."""
import sys
from pathlib import Path

import numpy as np
import pytest

pytest.importorskip("pyscf")
from pyscf import dft, gto  # noqa: E402

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
sys.path.insert(0, str(PLAN / "modules" / "05_support_predictor" / "corpus"))
from apt import apt_from_mo1, hessian_with_response, sum_rule  # noqa: E402
from dipole_derivs_cphf import apt_cphf  # noqa: E402

WATER = [("O", (0.0, 0.0, 0.2217)), ("H", (0.0, 1.4309, -0.8867)), ("H", (0.0, -1.4309, -0.8867))]


@pytest.fixture(scope="module")
def mf():
    mol = gto.M(atom=WATER, unit="Bohr", basis="6-31g*", cart=True, symmetry=False, verbose=0)
    m = dft.RKS(mol)
    m.xc = "b3lyp"
    m.grids.atom_grid = (50, 194)
    m.conv_tol = 1e-11
    m.kernel()
    assert m.converged
    return m


def test_the_kept_response_gives_route_b_apt_and_the_same_hessian(mf):
    hobj = mf.Hessian()
    H, mo1 = hessian_with_response(hobj)
    P_c = apt_from_mo1(mf, mo1)
    P_b = apt_cphf(mf, log=lambda *_: None)
    assert np.abs(P_c - P_b).max() < 1e-6
    assert sum_rule(P_c) < 5e-4                                                          # translation sum rule, neutral molecule
    assert np.abs(H - mf.Hessian().kernel()).max() < 1e-8 and hobj.de is H                   # the same Hessian as kernel(), stored as kernel() stores it
