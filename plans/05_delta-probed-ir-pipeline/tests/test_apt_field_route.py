"""probes/apt_field_route.py (12 Oct 2026): the APT from the analytic gradient in a small field. At HF it converges to the CPHF APT of route C
(both exact second derivatives, no exchange-correlation term) with an O(F²) field error — measured on water: 3.6e-5, 9.1e-6, 2.4e-6 e at
F = 2e-3, 1e-3, 5e-4; with grid response its translation sum rule is exact. Water, small grid, seconds;
needs pyscf, so it runs in WSL and is skipped elsewhere."""
import sys
from pathlib import Path

import numpy as np
import pytest

pytest.importorskip("pyscf")
from pyscf import gto

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
sys.path.insert(0, str(PLAN / "modules" / "05_support_predictor" / "corpus"))
from apt import apt_from_mo1, hessian_with_response, refine_response, solve_response, sum_rule  # noqa: E402
from apt_field_route import apt_field, save_checkpoint, scf_in_field  # noqa: E402

WATER = [("O", (0.0, 0.0, 0.2217)), ("H", (0.0, 1.4309, -0.8867)), ("H", (0.0, -1.4309, -0.8867))]


def _mol():
    return gto.M(atom=WATER, unit="Bohr", basis="6-31g*", cart=True, symmetry=False, verbose=0)


def test_field_route_equals_route_c_at_hf():
    mol = _mol()
    settings = {"xc": "hf", "grid": (50, 194)}
    mf = scf_in_field(mol, settings, np.zeros(3))
    P_c = apt_from_mo1(mf, hessian_with_response(mf.Hessian())[1])
    P_no, P_gr = apt_field(mol, settings, 1e-3, log=lambda *a, **k: None)
    e1 = np.abs(P_no - P_c).max()
    assert e1 < 3e-5 and np.abs(P_gr - P_no).max() < 1e-9                         # HF has no grid: both field variants are the same object
    e2 = np.abs(apt_field(mol, settings, 5e-4, log=lambda *a, **k: None)[0] - P_c).max()
    assert e2 < e1 / 3                                                             # O(F²): halving the field quarters the error


def test_grid_response_makes_the_sum_rule_exact_for_dft():
    mol = _mol()
    P_no, P_gr = apt_field(mol, {"xc": "b3lyp", "grid": (50, 194)}, 1e-3, log=lambda *a, **k: None)
    assert sum_rule(P_gr) < 1e-8 < sum_rule(P_no)


def test_the_refined_response_puts_route_c_on_the_field_route_for_dft():
    """TASKS 44 (a), 12 Oct 2026; premise refreshed 14 Nov 2026 (TASKS 213). When pyscf's Krylov CPHF stopped early for DFT
    (#2702, ours) route C's APT was 6e-5 e off the field route and the refined one 7.5e-6. pyscf 2.15.0 carries the fix, so
    the solver's own response is already inside the bound (5.7e-10): route C sits 7.31e-6 from the field route, inside the
    field error of about 9e-6 at F = 1e-3, and the refined response is the same array to 1.8e-15 (measured, ~/qc215). What is
    pinned is that both agree with the field route inside 2e-5 and that refining never makes it worse. Against the field
    route without grid response, the derivative the analytic Hessian takes."""
    mol = _mol()
    settings = {"xc": "b3lyp", "grid": (50, 194)}
    mf = scf_in_field(mol, settings, np.zeros(3))
    hobj = mf.Hessian()
    resp = solve_response(hobj)
    P_c = apt_from_mo1(mf, resp.mo1)
    P_r = apt_from_mo1(mf, refine_response(hobj, resp.mo1, resp.h1ao)[0])
    P_no = apt_field(mol, settings, 1e-3, log=lambda *a, **k: None)[0]
    off_c, off_r = np.abs(P_c - P_no).max(), np.abs(P_r - P_no).max()
    assert off_r < 2e-5 and off_c < 2e-5 and off_r <= off_c + 1e-12


def test_a_restart_resumes_from_the_checkpoint_and_refuses_another_field(tmp_path):
    mol = _mol()
    settings = {"xc": "hf", "grid": (50, 194)}
    quiet = lambda *a, **k: None  # noqa: E731  (a no-op log)
    full = apt_field(mol, settings, 1e-3, log=quiet)
    ck = str(tmp_path / "ck.npz")
    save_checkpoint(ck, 1e-3, 2, {False: full[0].copy(), True: full[1].copy()})       # two components done, as after an interruption
    lines = []
    resumed = apt_field(mol, settings, 1e-3, log=lambda s, **k: lines.append(s), checkpoint=ck)
    assert lines[0].startswith("  resuming after field component 2/3")
    assert sum("component 3/3 done" in s for s in lines) == 1 and not any("component 1/3" in s for s in lines)
    assert np.abs(resumed[0] - full[0]).max() < 1e-9 and np.abs(resumed[1] - full[1]).max() < 1e-9
    with pytest.raises(ValueError, match="another run"):
        apt_field(mol, settings, 2e-3, log=quiet, checkpoint=ck)
