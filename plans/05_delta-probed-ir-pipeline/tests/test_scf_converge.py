"""probes/scf_converge.py (19 Oct 2026): one DIIS → second-order → DIIS convergence for the S1/S2 pyscf paths. On water at B3LYP/6-31G*
(grid 75,302) the fallback, forced by cutting DIIS to 3 cycles, reaches the energy of a plain DIIS run to 1e-10 E_h and says so in its log;
a run that converges under DIIS returns the same object without a fallback line. Needs pyscf, so it runs in WSL and is skipped elsewhere."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes"))
pytest.importorskip("pyscf")
S = pytest.importorskip("scf_converge")

WATER = [("O", (0.0, 0.0, 0.2217)), ("H", (0.0, 1.4309, -0.8867)), ("H", (0.0, -1.4309, -0.8867))]


def _rks():
    from pyscf import dft, gto
    mf = dft.RKS(gto.M(atom=WATER, unit="Bohr", basis="6-31g*", verbose=0))
    mf.xc, mf.grids.atom_grid, mf.grids.prune, mf.conv_tol, mf.conv_tol_grad = "b3lyp", (75, 302), None, 1e-11, 1e-8
    return mf


def test_a_converging_diis_needs_no_fallback():
    lines = []
    mf = _rks()
    out, _ = S.converged_scf(mf, log=lines.append)
    assert out is mf and out.converged and lines == []


def test_the_fallback_reaches_the_plain_energy_and_says_so():
    lines = []
    _, e_ref = S.converged_scf(_rks(), log=lines.append)
    out, e_fb = S.converged_scf(_rks(), diis_cycles=3, log=lines.append)
    assert out.converged and abs(e_fb - e_ref) < 1e-10
    assert lines == ["  SCF: DIIS not converged in 3 cycles; second-order solver"]


def test_a_budget_that_cannot_run_is_refused():
    with pytest.raises(ValueError, match="positive"):
        S.converged_scf(object(), diis_cycles=0)
