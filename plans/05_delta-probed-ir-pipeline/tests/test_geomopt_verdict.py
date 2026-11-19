"""`probes/geomopt_verdict.py` (TASKS 239) with pyscf's geomeTRIC solver stubbed: a converged optimisation returns the solver's geometry
and passes the run's settings through; an unconverged one raises with the criteria and the number of gradient calls; the
re-optimisation at the label settings goes through it; and no probe calls pyscf's solver (`optimize` drops the verdict) outside the helper."""
from __future__ import annotations

import importlib.util
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


SOLVER_CALL = re.compile(r"geometric_solver\.(optimize|kernel)\(|geometric_solver import[^\n]*\b(optimize|kernel)\b")
OWN_SOLVER_CALL = {"geomopt_verdict.py": "the helper itself"}


def test_no_probe_calls_the_solver_outside_the_helper() -> None:
    callers = {p.name for p in PROBES.glob("*.py") if SOLVER_CALL.search(p.read_text(encoding="utf-8"))}
    assert callers == set(OWN_SOLVER_CALL)


def load_reoptimise(monkeypatch: pytest.MonkeyPatch) -> types.ModuleType:
    """probes/reoptimise_at_label_settings.py loaded under a private name with its pyscf-side imports stubbed; nothing stays in
    sys.modules, so its own pyscf test (WSL) still imports the real module."""
    corpus = types.SimpleNamespace(AMU2AU=1822.888, FUNCTIONALS=[("b3lyp", "b3lyp")], MAX_MEMORY_MB=4000, freqs_cm=None,
                                   labels_ks=lambda mol, xc, grid: types.SimpleNamespace(mol=mol),
                                   labels_mol=lambda start, log, max_memory: start, software=lambda: {}, vib_only=None)
    monkeypatch.setitem(sys.modules, "analytic_hessians", corpus)
    monkeypatch.setitem(sys.modules, "vibrations", types.SimpleNamespace(signed_cm=None))
    spec = importlib.util.spec_from_file_location("reoptimise_stubbed", PROBES / "reoptimise_at_label_settings.py")
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, "reoptimise_stubbed", module)   # dataclasses looks its module up there; removed after the test
    spec.loader.exec_module(module)
    return module


def reoptimise_solver(monkeypatch: pytest.MonkeyPatch, converged: bool) -> list[dict]:
    """A solver for the re-optimisation: two gradient calls with energies and gradients, then the verdict."""
    calls: list[dict] = []

    def kernel(mf: object, **kwargs: object) -> tuple[bool, types.SimpleNamespace]:
        calls.append(kwargs)
        for energy in (-76.40, -76.41):
            kwargs["callback"]({"energy": energy, "gradients": [[0.0, 0.0, 1e-5]]})
        return converged, types.SimpleNamespace(atom_coords=lambda unit: [[0.0, 0.0, 0.1]])

    monkeypatch.setitem(sys.modules, "pyscf", types.SimpleNamespace(lib=types.SimpleNamespace(num_threads=lambda n: None)))
    monkeypatch.setitem(sys.modules, "pyscf.geomopt", types.SimpleNamespace(geometric_solver=types.SimpleNamespace(kernel=kernel)))
    return calls


def test_the_reoptimisation_returns_coordinates_energy_and_steps(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = reoptimise_solver(monkeypatch, converged=True)
    rls = load_reoptimise(monkeypatch)
    cfg = types.SimpleNamespace(max_memory_mb=500, grid=(99, 590), source=Path("D_x"))
    coords, energy, steps = rls.optimise({"symbols": ["O"]}, cfg, lib_log=None)
    assert coords == [[0.0, 0.0, 0.1]] and energy == -76.41 and steps == 2
    assert calls[0]["assert_convergence"] is True and calls[0]["maxsteps"] == rls.MAX_STEPS
    assert {k: calls[0][k] for k in rls.CONVERGENCE} == rls.CONVERGENCE


def test_the_reoptimisation_refuses_an_unconverged_run(monkeypatch: pytest.MonkeyPatch) -> None:
    reoptimise_solver(monkeypatch, converged=False)
    rls = load_reoptimise(monkeypatch)
    cfg = types.SimpleNamespace(max_memory_mb=500, grid=(99, 590), source=Path("D_x"))
    with pytest.raises(RuntimeError, match=r"^D_x: geomeTRIC did not converge to \(dmax 0\.0002, .*\) within 100 steps \(2 gradient calls\)"):
        rls.optimise({"symbols": ["O"]}, cfg, lib_log=None)
