"""The engine check's read (`probes/engine_check_read.py`, TASKS 73) on synthetic route files with the regime's edge cases: equal routes
pass, a family exactly on the line passes and one just beyond fails, a pyscf route better everywhere passes, and every inconsistency is
refused before a verdict — another route label, a missing family, a non-finite or missing seed value, other models or molecules, and a
psi4 route whose check 0 failed or is absent."""
from __future__ import annotations

import json
import sys
import types
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes"))
import engine_check as EC
import engine_check_read as E

MODELS = ["v15_seed0.pt", "v15_seed1.pt", "v15_seed2.pt"]
MOLECULES = ["A_08dde334d8", "A_428228e5a5", "A_541c53d1a5", "A_72b86c2331", "A_8448043181", "A_bce5bae234", "A_e72997e726", "A_fdc27f1bd1"]
BASE = {"ring-ip": [1.7, 1.8, 1.8], "CH-stretch": [1.2, 1.2, 1.2], "CH-oop": [2.1, 2.2, 2.2], "other": [3.6, 3.6, 3.7]}


def route(name: str, errors: dict | None = None, **extra) -> dict:
    rec = {"route": name, "models": list(MODELS), "molecules": list(MOLECULES), "family_errors": errors or {k: list(v) for k, v in BASE.items()}}
    if name == "psi4":
        rec["check0"] = {"max_abs_difference": 0.0}
    return rec | extra


def shifted(by: dict) -> dict:
    return {k: [x + by.get(k, 0.0) for x in v] for k, v in BASE.items()}


def written(tmp_path: Path, rec: dict) -> Path:
    p = tmp_path / f"{rec['route']}_{len(list(tmp_path.iterdir()))}.json"
    p.write_text(json.dumps(rec), encoding="utf-8")
    return p


def test_equal_routes_pass() -> None:
    result = E.read(route("psi4"), route("pyscf"))
    assert result["verdict"] == "PASS" and all(r["difference"] == 0 for r in result["families"].values())


def test_a_family_on_the_line_passes_and_just_beyond_fails() -> None:
    assert E.read(route("psi4"), route("pyscf", shifted({"other": 0.3 - 1e-12})))["verdict"] == "PASS"
    result = E.read(route("psi4"), route("pyscf", shifted({"CH-oop": 0.31})))
    assert result["verdict"] == "FAIL" and not result["families"]["CH-oop"]["within_line"] and result["families"]["other"]["within_line"]


def test_a_better_pyscf_route_passes() -> None:
    assert E.read(route("psi4"), route("pyscf", shifted(dict.fromkeys(BASE, -0.5))))["verdict"] == "PASS"


def test_the_information_is_passed_through_and_does_not_decide() -> None:
    info = {"max_band_shift_cm": 4.2, "max_coordinate_difference_bohr": 3e-3}
    result = E.read(route("psi4"), route("pyscf", information=info))
    assert result["verdict"] == "PASS" and result["information"]["pyscf"] == info


@pytest.mark.parametrize("break_it, message", [
    (lambda r: r.update(route="psi4"), "route"),
    (lambda r: r["family_errors"].pop("CH-oop"), "no errors"),
    (lambda r: r["family_errors"].update({"other": [3.6, float("nan"), 3.7]}), "not finite"),
    (lambda r: r["family_errors"].update({"other": [3.6, 3.7]}), "seed values"),
])
def test_a_broken_route_file_is_refused(tmp_path, break_it, message) -> None:
    rec = route("pyscf")
    break_it(rec)
    with pytest.raises(ValueError, match=message):
        E.load_route(written(tmp_path, rec), "pyscf")


@pytest.mark.parametrize("pyscf_extra, psi4_extra, message", [
    ({"models": ["v14_seed0.pt", "v14_seed1.pt", "v14_seed2.pt"]}, {}, "different models"),
    ({"molecules": [*MOLECULES[:-1], "B_0da4a5aea1"]}, {}, "different molecules"),
    ({}, {"check0": {"max_abs_difference": 2e-6}}, "check 0"),
    ({}, {"check0": {}}, "check 0"),
])
def test_routes_that_do_not_pair_are_refused(pyscf_extra, psi4_extra, message) -> None:
    with pytest.raises(ValueError, match=message):
        E.read(route("psi4", **psi4_extra), route("pyscf", **pyscf_extra))


# The run's own optimisation (`probes/engine_check.py optimise`, TASKS 228) with the solver and the SCF stubbed: a converged optimisation is
# written with its convergence numbers, an unconverged one raises and writes nothing.

FINAL_GRADIENT = np.array([[3e-6, 4e-6, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 1.2e-5]])   # per-atom norms 5e-6, 0, 1.2e-5
STEP_ENERGIES = (-76.40, -76.41, -76.4100004)


class StubMol:
    def __init__(self, coords_bohr: list) -> None:
        self.coords = np.asarray(coords_bohr, float)

    def atom_coords(self) -> np.ndarray:
        return self.coords


class StubScf:
    def __init__(self, mol: StubMol) -> None:
        self.mol = mol

    def nuc_grad_method(self) -> types.SimpleNamespace:
        return types.SimpleNamespace(kernel=lambda: FINAL_GRADIENT)


def stub_solver(monkeypatch: pytest.MonkeyPatch, converged: bool) -> list[dict]:
    """pyscf, its geomeTRIC solver and the labels' SCF replaced by stubs; returns the list the solver's calls are recorded in."""
    calls: list[dict] = []

    def kernel(mf: StubScf, **kwargs: object) -> tuple[bool, StubMol]:
        calls.append(kwargs)
        for energy in STEP_ENERGIES:
            kwargs["callback"]({"energy": energy})
        return converged, StubMol(mf.mol.coords + 0.01)

    solver = types.SimpleNamespace(kernel=kernel)
    labels = types.SimpleNamespace(labels_mol=lambda geometry, log, max_memory: StubMol(geometry["coords_bohr"]),
                                   labels_scf=lambda mol, functional, grid: (StubScf(mol), -76.41))
    for name, module in (("pyscf", types.SimpleNamespace(lib=types.SimpleNamespace(num_threads=lambda n: None))),
                         ("pyscf.geomopt", types.SimpleNamespace(geometric_solver=solver)), ("analytic_hessians", labels)):
        monkeypatch.setitem(sys.modules, name, module)
    return calls


def start_folder(tmp_path: Path) -> Path:
    folder = tmp_path / "water"
    folder.mkdir()
    (folder / "start.json").write_text(json.dumps({"id": "water", "layer": "smoke", **EC.WATER, "source": "the test"}), encoding="utf-8")
    return folder


def test_optimise_records_a_converged_geometry(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    calls = stub_solver(monkeypatch, converged=True)
    folder = start_folder(tmp_path)
    EC.optimise(folder, threads=1, max_memory=500)
    assert calls[0]["assert_convergence"] is True and {k: calls[0][k] for k in EC.CONVERGENCE} == EC.CONVERGENCE
    rec = json.loads((folder / "result.json").read_text(encoding="utf-8"))["optimisation"]
    assert rec["converged"] is True and rec["steps"] == len(STEP_ENERGIES)
    assert rec["engine"].endswith("geometric_solver.kernel")
    assert rec["grad_max_au"] == pytest.approx(1.2e-5) and rec["grad_rms_au"] == pytest.approx((169e-12 / 3) ** 0.5)
    assert rec["max_force_au"] == pytest.approx(1.2e-5)
    assert rec["last_energy_change_au"] == pytest.approx(STEP_ENERGIES[-1] - STEP_ENERGIES[-2])
    assert (folder / "geometry.json").is_file()


def test_optimise_refuses_an_unconverged_geometry(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    stub_solver(monkeypatch, converged=False)
    folder = start_folder(tmp_path)
    with pytest.raises(RuntimeError, match="geomeTRIC did not converge to GAU_TIGHT within 100 steps"):
        EC.optimise(folder, threads=1, max_memory=500)
    assert not (folder / "geometry.json").exists() and not (folder / "result.json").exists()


def test_convergence_record_after_a_single_gradient_call() -> None:
    assert EC.convergence_record(FINAL_GRADIENT, [-76.4])["last_energy_change_au"] is None
