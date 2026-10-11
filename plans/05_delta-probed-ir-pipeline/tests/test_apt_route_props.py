"""TASKS 44 third route (11 Oct 2026): pyscf-properties' infrared module (pinned checkout, `probes/upstream_infrared.py`) against our APT on water
(route C), and our finite-difference route's new open-shell branch (`dipole_derivs_fd.py --spin`) against upstream's UKS module on H2O⁺ — small
basis and grid, so the test takes seconds. Needs pyscf and the checkout, so it runs in WSL (like test_apt_route_c.py) and is skipped elsewhere;
a checkout at another commit fails rather than skips."""
import os
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
from apt_route_props_probe import apt_from_upstream, band_groups, compare_heights, richardson, upstream_route  # noqa: E402
from dipole_derivs_fd import apt_fd  # noqa: E402
from upstream_infrared import CHECKOUT, load  # noqa: E402

if not os.path.isdir(CHECKOUT):
    pytest.skip(f"no pyscf-properties checkout at {CHECKOUT}", allow_module_level=True)
INFRARED, _ = load()

WATER = [("O", (0.0, 0.0, 0.2217)), ("H", (0.0, 1.4309, -0.8867)), ("H", (0.0, -1.4309, -0.8867))]
MASSES = np.array([15.99491461957, 1.00782503223, 1.00782503223])
GRID = (50, 194)


def converged(charge=0, spin=0, basis="6-31g*"):
    mol = gto.M(atom=WATER, unit="Bohr", basis=basis, cart=True, symmetry=False, verbose=0, charge=charge, spin=spin)
    mf = dft.UKS(mol) if spin else dft.RKS(mol)
    mf.xc = "b3lyp"
    mf.grids.atom_grid = GRID
    mf.conv_tol = 1e-11
    mf.kernel()
    assert mf.converged
    return mf


def test_apt_from_upstream_reorders_atom_axis_dipole_to_dipole_column():
    de = np.arange(2 * 3 * 3, dtype=float).reshape(2, 3, 3)                              # de[A, x, t]
    P = apt_from_upstream(de)
    assert P.shape == (3, 6) and all(P[t, 3 * A + x] == de[A, x, t] for A in range(2) for x in range(3) for t in range(3))


def test_richardson_removes_a_pure_second_order_step_error():
    P = np.ones((3, 6))
    err = np.full((3, 6), 1e-3)                                                           # FD error c·h² at h; a quarter at h/2
    r = richardson(P, P + err, P + err / 4)
    assert abs(r["g_h"] - 1e-3) < 1e-15 and abs(r["g_h2"] - 2.5e-4) < 1e-15 and r["g_richardson"] < 1e-15
    assert abs(r["fd_pair"] - 7.5e-4) < 1e-15


def test_band_groups_sum_degenerate_modes_and_compare_heights_ignores_their_split():
    f = np.array([100.0, 500.0, 500.4, 900.0])
    assert band_groups(f, [1.0, 2.0, 3.0, 4.0]) == [(100.0, 1.0), (500.2, 5.0), (900.0, 4.0)]
    df, rel = compare_heights(f, [1.0, 2.0, 3.0, 4.0], f, [1.0, 4.5, 0.5, 4.0])            # the pair's split differs, its sum does not
    assert df == 0.0 and rel == 0.0


def test_upstream_rks_apt_and_hessian_equal_route_c_on_water():
    mf = converged()
    H_c, mo1 = hessian_with_response(mf.Hessian())
    P_c = apt_from_mo1(mf, mo1)
    P_u, H_u, freq, km, _, (freq_s, km_s) = upstream_route(mf, MASSES, INFRARED)
    assert np.abs(P_u - P_c).max() < 1e-6 and np.abs(H_u - H_c).max() < 1e-8
    assert len(freq) == len(km) == 3 and (km > 0).all()
    assert compare_heights(freq_s, km_s, freq, km)[1] < 1e-3                               # water's Hessian is near symmetric


def test_fd_open_shell_branch_matches_upstream_uks_on_water_cation():
    mf = converged(charge=1, spin=1, basis="6-31g")
    P_u = upstream_route(mf, MASSES, INFRARED)[0]
    x0 = mf.mol.atom_coords(unit="Bohr")
    P_fd = apt_fd(mf.mol, "b3lyp", GRID, x0, 0.005, log=lambda *_: None)                  # mol.spin = 1 → UKS at every displaced geometry
    assert sum_rule(P_u, charge=1) < 5e-4 and sum_rule(P_fd, charge=1) < 5e-4
    assert np.abs(P_u - P_fd).max() < 1e-4
