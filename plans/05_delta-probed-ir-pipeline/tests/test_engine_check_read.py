"""The engine check's read (`probes/engine_check_read.py`, TASKS 73) on synthetic route files with the regime's edge cases: equal routes
pass, a family exactly on the line passes and one just beyond fails, a pyscf route better everywhere passes, and every inconsistency is
refused before a verdict — another route label, a missing family, a non-finite or missing seed value, other models or molecules, and a
psi4 route whose check 0 failed or is absent."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes"))
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
