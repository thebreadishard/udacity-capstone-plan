"""finish_by_newton's contract (TASKS 201, 14 Nov 2026): the second-order solver gets its own cycle budget and pyscf's own derived
gradient threshold -- never the caller's tight one -- and the verdict stays with the DIIS object the Hessian is built on.

The corpus repair's last molecule, T_76dfc434db (C42H18, 60 atoms), stopped at |g| 1.83e-8 after 50 macro iterations and 2.8 h against
the grid-response caller's conv_tol_grad of 1e-8, which `pyscf/soscf/newton_ah.py` (2.15.0, SecondOrderSCF.kernel) passes straight on as
`self.conv_tol_grad`. Left to itself the solver derives sqrt(conv_tol) (newton_ah.py:526-527), the ~3e-6 at which it stops stalling, and
the plain SCF then finishes to the caller's threshold from a good density.

The stubs stand in for pyscf's objects, so these tests pin the policy, not the physics; the module itself needs pyscf to import.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "modules" / "05_support_predictor" / "corpus"))
pytest.importorskip("pyscf")
AH = pytest.importorskip("analytic_hessians")

CALLER_TOL = 1e-8        # the grid-response FD path's CONV_TOL_GRAD: the value the solver must not inherit
STALLED_E = -1611.5
RESTARTED_E = -1611.6


class _Solver:
    """pyscf's second-order solver, as `mf.newton()` returns it: a copy of the caller's settings, tight threshold included."""

    def __init__(self, converged: bool) -> None:
        self.converged = converged
        self.conv_tol_grad: float | None = CALLER_TOL
        self.max_cycle = 0
        self.started_from: tuple[Any, Any] | None = None

    def kernel(self, mo_coeff: Any, mo_occ: Any) -> None:
        self.started_from = (mo_coeff, mo_occ)

    def make_rdm1(self) -> str:
        return "second-order density"


class _Stalled:
    """A DIIS run that stopped short of the caller's threshold, holding that threshold on itself."""

    def __init__(self, solver: _Solver) -> None:
        self.e_tot = STALLED_E
        self.converged = False
        self.conv_tol_grad = CALLER_TOL
        self.mo_coeff, self.mo_occ = "orbitals", "occupations"
        self.restarted_from: Any = None
        self._solver = solver

    def newton(self) -> _Solver:
        return self._solver

    def kernel(self, dm0: Any = None) -> float:
        self.restarted_from = dm0
        self.converged = True
        self.e_tot = RESTARTED_E
        return self.e_tot


def test_the_solver_gets_pyscfs_own_gradient_threshold_not_the_callers() -> None:
    solver = _Solver(converged=True)
    mf = _Stalled(solver)
    AH.finish_by_newton(mf)
    assert solver.conv_tol_grad is None
    assert mf.conv_tol_grad == CALLER_TOL


def test_the_solver_keeps_its_own_cycle_budget_and_starts_from_the_stalled_orbitals() -> None:
    solver = _Solver(converged=True)
    mf = _Stalled(solver)
    AH.finish_by_newton(mf)
    assert solver.max_cycle == AH.NEWTON_MAX_CYCLE
    assert solver.started_from == ("orbitals", "occupations")


def test_a_converged_solver_hands_its_density_to_the_plain_scf() -> None:
    mf = _Stalled(_Solver(converged=True))
    assert AH.finish_by_newton(mf) == RESTARTED_E
    assert mf.restarted_from == "second-order density"
    assert mf.converged


def test_a_solver_that_does_not_converge_leaves_the_stalled_verdict() -> None:
    mf = _Stalled(_Solver(converged=False))
    assert AH.finish_by_newton(mf) == STALLED_E
    assert mf.restarted_from is None
    assert not mf.converged
