"""`probes/geomopt_verdict.py` (TASKS 239) with pyscf's geomeTRIC solver stubbed: a converged optimisation returns the solver's geometry
and passes the run's settings through; an unconverged one raises with the criteria and the number of gradient calls; and no probe calls
pyscf's `optimize`, which drops the verdict."""
from __future__ import annotations

import re
import sys
import types
from pathlib import Path

import pytest

PROBES = Path(__file__).resolve().parents[1] / "probes"
sys.path.insert(0, str(PROBES))
import geomopt_verdict as GV  # noqa: E402  the probes folder goes on sys.path first

ROUTE2_THRESHOLDS = {"convergence_energy": 1e-7, "convergence_grms": 1e-5, "convergence_gmax": 2e-5, "convergence_drms": 1e-4,
                     "convergence_dmax": 2e-4}


def stub_solver(monkeypatch: pytest.MonkeyPatch, converged: bool, gradient_calls: int = 3) -> list[dict]:
    """pyscf.geomopt replaced by a solver whose kernel calls back `gradient_calls` times; returns the list its calls are recorded in."""
    calls: list[dict] = []

    def kernel(mf: object, **kwargs: object) -> tuple[bool, str]:
        calls.append({"mf": mf, **kwargs})
        for n in range(gradient_calls):
            kwargs["callback"]({"energy": -1.0 - n})
        return converged, "the last geometry"

    monkeypatch.setitem(sys.modules, "pyscf", types.SimpleNamespace())
    monkeypatch.setitem(sys.modules, "pyscf.geomopt", types.SimpleNamespace(geometric_solver=types.SimpleNamespace(kernel=kernel)))
    return calls


def test_a_converged_optimisation_returns_the_geometry_and_passes_the_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = stub_solver(monkeypatch, converged=True)
    seen: list[dict] = []
    got = GV.converged_geometry("mf", "water", maxsteps=200, callback=seen.append, convergence_set="GAU_TIGHT", constraints="c.txt")
    assert got == "the last geometry" and len(seen) == 3
    kw = calls[0]
    assert kw["mf"] == "mf" and kw["assert_convergence"] is True and kw["maxsteps"] == 200
    assert kw["convergence_set"] == "GAU_TIGHT" and kw["constraints"] == "c.txt"


def test_without_a_callback_the_calls_are_still_counted(monkeypatch: pytest.MonkeyPatch) -> None:
    stub_solver(monkeypatch, converged=False, gradient_calls=7)
    with pytest.raises(RuntimeError, match=r"\(7 gradient calls\)"):
        GV.converged_geometry("mf", "water", maxsteps=100, convergence_set="GAU_TIGHT")


def test_an_unconverged_named_set_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    stub_solver(monkeypatch, converged=False)
    with pytest.raises(RuntimeError, match=r"^water: geomeTRIC did not converge to GAU_TIGHT within 200 steps \(3 gradient calls\); "
                                           r"no geometry is written$"):
        GV.converged_geometry("mf", "water", maxsteps=200, callback=lambda env: None, convergence_set="GAU_TIGHT")


def test_unconverged_explicit_thresholds_are_named_in_the_refusal(monkeypatch: pytest.MonkeyPatch) -> None:
    stub_solver(monkeypatch, converged=False)
    with pytest.raises(RuntimeError, match=re.escape("did not converge to (dmax 0.0002, drms 0.0001, energy 1e-07, gmax 2e-05, "
                                                     "grms 1e-05) within 100 steps")):
        GV.converged_geometry("mf", "stageA.json", maxsteps=100, **ROUTE2_THRESHOLDS)


def test_no_criteria_given_names_geometric_defaults() -> None:
    assert GV.criteria_text({"constraints": "c.txt"}) == "geomeTRIC's default criteria"


def test_no_probe_calls_optimize() -> None:
    callers = [p.name for p in sorted(PROBES.glob("*.py"))
               if re.search(r"geometric_solver\.optimize\(|geometric_solver import[^\n]*\boptimize\b", p.read_text(encoding="utf-8"))]
    assert callers == []
