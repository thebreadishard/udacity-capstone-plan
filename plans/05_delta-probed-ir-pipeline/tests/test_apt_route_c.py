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
from apt import CPHF_BOUND, apt_from_mo1, hessian_with_response, refine_response, solve_response, sum_rule  # noqa: E402
from dipole_derivs_cphf import apt_cphf  # noqa: E402

WATER = [("O", (0.0, 0.0, 0.2217)), ("H", (0.0, 1.4309, -0.8867)), ("H", (0.0, -1.4309, -0.8867))]


def _water_b3lyp():
    mol = gto.M(atom=WATER, unit="Bohr", basis="6-31g*", cart=True, symmetry=False, verbose=0)
    m = dft.RKS(mol)
    m.xc = "b3lyp"
    m.grids.atom_grid = (50, 194)
    m.conv_tol = 1e-11
    m.kernel()
    assert m.converged
    return m


@pytest.fixture(scope="module")
def mf():
    return _water_b3lyp()


def test_the_kept_response_gives_route_b_apt_and_the_same_hessian(mf):
    hobj = mf.Hessian()
    H, mo1 = hessian_with_response(hobj)
    P_c = apt_from_mo1(mf, mo1)
    P_b = apt_cphf(mf, log=lambda *_: None)
    assert np.abs(P_c - P_b).max() < 1e-6
    assert sum_rule(P_c) < 5e-4                                                          # translation sum rule, neutral molecule
    assert np.abs(H - mf.Hessian().kernel()).max() < 1e-8 and hobj.de is H                   # the same Hessian as kernel(), stored as kernel() stores it


def test_a_kept_response_gives_the_same_hessian():
    """hessian_with_response(hobj, solve_response(hobj)) is the Hessian of kernel(): the caller can keep h1ao for refine_response."""
    m = _water_b3lyp()
    hobj = m.Hessian()
    H, mo1 = hessian_with_response(hobj, solve_response(hobj))
    assert np.abs(H - m.Hessian().kernel()).max() < 1e-12


def test_refine_response_repairs_a_perturbed_response(mf):
    """TASKS 44 (a), 12 Oct 2026: a response pushed 1e-4 off in the virtual space (residual 3.8e-4, APT 9.6e-4 e off) is brought back below the
    bound in one round, to the APT of the refined unperturbed response within 1.6e-7 e (measured); pyscf's own water response, 3.0e-5 off its
    system, goes to 1.4e-7. A bound of zero stops after max_rounds."""
    hobj = mf.Hessian()
    resp = solve_response(hobj)
    mo1, info = refine_response(hobj, resp.mo1, resp.h1ao)
    assert info["residual_after"] <= CPHF_BOUND < info["residual_before"] and info["rounds"] == 1
    o, v = mf.mo_occ > 0, mf.mo_occ == 0
    rng = np.random.default_rng(0)
    noise = [np.einsum("pa,xai->xpi", mf.mo_coeff[:, v], 1e-4 * rng.standard_normal((3, int(v.sum()), int(o.sum())))) for _ in resp.mo1]
    bad = [m + n for m, n in zip(resp.mo1, noise, strict=True)]
    fixed, info_bad = refine_response(hobj, bad, resp.h1ao)
    P = apt_from_mo1(mf, mo1)
    assert np.abs(apt_from_mo1(mf, bad) - P).max() > 1e-4
    assert info_bad["residual_after"] <= CPHF_BOUND and np.abs(apt_from_mo1(mf, fixed) - P).max() < 1e-6
    assert refine_response(hobj, resp.mo1, resp.h1ao, bound=0.0, max_rounds=2)[1]["rounds"] == 2
