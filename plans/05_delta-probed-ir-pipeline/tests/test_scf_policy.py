"""The one SCF convergence policy both deployment units carry (TASKS 212, 14 November 2026).

The stubs stand in for pyscf's objects, so these tests pin the policy, not the physics: that the second-order solver gets the policy's
own gradient threshold and never the caller's tight one, that the plain SCF object is the one restarted and returned, and that a step
which fails says which step it was. The module itself imports nothing outside the standard library, so unlike the route that uses it
these tests need no pyscf.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "modules" / "05_support_predictor" / "corpus"))
import scf_policy as S

CALLER_TOL = 1e-8          # a displaced point's conv_tol_grad: the value the solver must not inherit
STALLED_E = -1611.5
RESTARTED_E = -1611.6
FIRST_E = -1611.4
POLICY = S.SCFPolicy(diis_cycles=7, newton_cycles=11, newton_conv_tol_grad=1e-6)


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


class _SCF:
    """A DIIS SCF that converges or stalls on its first kernel and converges on the restart, holding the caller's threshold."""

    def __init__(self, solver: _Solver | None = None, converges: bool = False, restart_converges: bool = True) -> None:
        self.converged = False
        self.conv_tol_grad = CALLER_TOL
        self.max_cycle = 999
        self.mo_coeff, self.mo_occ = "orbitals", "occupations"
        self.e_tot = STALLED_E
        self.started_from: Any = "not run"
        self.restarted_from: Any = None
        self._solver, self._converges, self._restart = solver, converges, restart_converges
        self._runs = 0

    def newton(self) -> _Solver:
        if self._solver is None:
            raise AssertionError("the solver was asked for although DIIS converged")
        return self._solver

    def kernel(self, dm0: Any = None) -> float:
        self._runs += 1
        if self._runs == 1:
            self.started_from = dm0
            self.converged = self._converges
            self.e_tot = FIRST_E if self._converges else STALLED_E
        else:
            self.restarted_from = dm0
            self.converged = self._restart
            self.e_tot = RESTARTED_E
        return self.e_tot


def quiet(_message: str) -> None:
    """The log the policy writes its fallback line to; silent in a test."""


def test_a_converged_diis_run_returns_at_once_and_never_asks_for_the_solver():
    mf = _SCF(solver=None, converges=True)
    assert S.converged_scf(mf, POLICY, quiet) == (mf, FIRST_E)
    assert mf.restarted_from is None and mf.max_cycle == POLICY.diis_cycles


def test_the_start_density_reaches_the_first_kernel_only():
    mf = _SCF(solver=None, converges=True)
    S.converged_scf(mf, POLICY, quiet, dm0="neighbour density")
    assert mf.started_from == "neighbour density"


def test_the_solver_gets_the_policys_threshold_and_budget_not_the_callers():
    solver = _Solver(converged=True)
    mf = _SCF(solver)
    S.converged_scf(mf, POLICY, quiet)
    assert solver.conv_tol_grad == POLICY.newton_conv_tol_grad
    assert solver.max_cycle == POLICY.newton_cycles
    assert solver.started_from == ("orbitals", "occupations")
    assert mf.conv_tol_grad == CALLER_TOL      # the caller's own threshold is the verdict, and it is untouched


def test_pyscfs_derived_threshold_is_asked_for_by_none():
    solver = _Solver(converged=True)
    S.converged_scf(_SCF(solver), S.LABEL_ROUTE, quiet)
    assert solver.conv_tol_grad is None


def test_the_plain_object_is_restarted_from_the_solvers_density_and_returned():
    mf = _SCF(_Solver(converged=True))
    returned, energy = S.converged_scf(mf, POLICY, quiet)
    assert returned is mf and energy == RESTARTED_E
    assert mf.restarted_from == "second-order density" and mf.converged


def test_a_solver_that_does_not_converge_names_the_step_that_failed():
    mf = _SCF(_Solver(converged=False))
    with pytest.raises(S.SCFNotConverged, match="second-order solver in 11 macro iterations"):
        S.converged_scf(mf, POLICY, quiet)
    assert mf.restarted_from is None


def test_a_restart_that_does_not_converge_names_its_own_step():
    mf = _SCF(_Solver(converged=True), restart_converges=False)
    with pytest.raises(S.SCFNotConverged, match="DIIS from the second-order solver's density"):
        S.converged_scf(mf, POLICY, quiet)


def test_a_policy_without_a_diis_budget_leaves_the_objects_own():
    mf = _SCF(solver=None, converges=True)
    S.converged_scf(mf, S.LABEL_ROUTE, quiet)
    assert mf.max_cycle == 999


@pytest.mark.parametrize(("field", "value"), [("diis_cycles", 0), ("newton_cycles", 0), ("newton_conv_tol_grad", 0.0),
                                              ("newton_conv_tol_grad", 1.0)])
def test_a_setting_outside_its_range_is_refused_when_the_policy_is_built(field, value):
    with pytest.raises(ValueError, match=field):
        S.SCFPolicy(**{"diis_cycles": 7, "newton_cycles": 11, "newton_conv_tol_grad": 1e-6, field: value})


def test_the_two_presets_carry_the_numbers_their_incidents_measured():
    labels, runners = S.LABEL_ROUTE, S.S1_S2_RUNNERS
    assert labels == S.SCFPolicy(diis_cycles=None, newton_cycles=50, newton_conv_tol_grad=None)
    assert runners == S.SCFPolicy(diis_cycles=200, newton_cycles=100, newton_conv_tol_grad=1e-6)
