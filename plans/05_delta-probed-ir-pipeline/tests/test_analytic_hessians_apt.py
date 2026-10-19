"""The labels route's APT (11 Oct 2026, TASKS 44 route C): analytic_hessians.py writes dipole_b3lyp_cphf.npz from the response its B3LYP Hessian
solves (after refine_response, 12 Oct 2026: residual before/after in the file, a residual above the bound fails it); it keeps an existing
APT file, --no-apt turns it off, analytic_check.json keeps one entry per functional (the export reads it so), and a failed APT costs neither
Hessian but ends with exit status 3. Water at a small grid; needs pyscf, so it runs in WSL and is skipped elsewhere."""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "modules" / "05_support_predictor" / "corpus"))
pytest.importorskip("pyscf")
AH = pytest.importorskip("analytic_hessians")

WATER = {"symbols": ["O", "H", "H"], "coords_bohr": [[0.0, 0.0, 0.2217], [0.0, 1.4309, -0.8867], [0.0, -1.4309, -0.8867]],
         "masses_amu": [15.995, 1.008, 1.008]}


def _run(tmp_path, monkeypatch, *args):
    d = tmp_path / "water"
    d.mkdir(exist_ok=True)
    (d / "geometry.json").write_text(json.dumps(WATER))
    monkeypatch.setattr(sys, "argv", ["analytic_hessians.py", str(d), "--threads", "1", "--grid", "50,194", *args])
    AH.main()
    return d


def test_the_b3lyp_pass_writes_the_apt_and_the_check_file_keeps_its_shape(tmp_path, monkeypatch):
    d = _run(tmp_path, monkeypatch)
    z = np.load(d / AH.APT_FILE)
    assert str(z["route"]) == "hessian_response_refined" and bool(z["passed"]) and float(z["sum_rule_max"]) < AH.SUM_RULE_LIMIT
    assert float(z["cphf_residual_after"]) <= AH.CPHF_BOUND < float(z["cphf_residual_before"]) and int(z["cphf_refine_rounds"]) >= 1
    assert z["apt"].shape == (3, 9) and len(z["intensity_km_mol"]) == 3
    assert set(json.loads((d / "analytic_check.json").read_text())) == {"b3lyp", "wb97x"}


def test_every_file_names_the_software_that_made_it(tmp_path, monkeypatch):
    """TASKS 47 (11 Oct 2026): pyscf can publish a release during the project; a file that travels alone still says which version made it."""
    import pyscf
    d = _run(tmp_path, monkeypatch)
    stamps = [json.loads(str(np.load(d / f)["software"])) for f in (AH.APT_FILE, "hessian_b3lyp_analytic.npz", "hessian_wb97x_analytic.npz")]
    stamps += [v["software"] for v in json.loads((d / "analytic_check.json").read_text()).values()]
    assert all(s == stamps[0] for s in stamps) and stamps[0]["pyscf"] == pyscf.__version__
    assert set(stamps[0]["sha256"]) == {"analytic_hessians.py", "apt.py"} and "pyscf_git" in stamps[0]


def test_an_existing_apt_file_is_kept_and_no_apt_writes_none(tmp_path, monkeypatch):
    d = _run(tmp_path, monkeypatch)
    before = (d / AH.APT_FILE).read_bytes()
    _run(tmp_path, monkeypatch)
    assert (d / AH.APT_FILE).read_bytes() == before
    (d / AH.APT_FILE).unlink()
    _run(tmp_path, monkeypatch, "--no-apt")
    assert not (d / AH.APT_FILE).exists()


def test_a_failed_apt_keeps_both_hessians_and_exits_3(tmp_path, monkeypatch):
    monkeypatch.setattr(AH, "apt_from_mo1", lambda mf, mo1: np.ones((3, 9)))      # breaks the translation sum rule
    with pytest.raises(SystemExit) as e:
        _run(tmp_path, monkeypatch)
    assert e.value.code == 3
    d = tmp_path / "water"
    assert (d / "hessian_b3lyp_analytic.npz").exists() and (d / "hessian_wb97x_analytic.npz").exists()
    assert not bool(np.load(d / AH.APT_FILE)["passed"])


def test_a_residual_above_the_bound_fails_the_apt_and_exits_3(tmp_path, monkeypatch):
    """TASKS 44 (a), 12 Oct 2026: the bound is checked, not assumed: at a bound no solver reaches, the APT is written with passed=False and the
    molecule ends with exit status 3, its Hessians kept."""
    monkeypatch.setattr(AH, "CPHF_BOUND", 0.0)
    with pytest.raises(SystemExit) as e:
        _run(tmp_path, monkeypatch)
    assert e.value.code == 3
    d = tmp_path / "water"
    z = np.load(d / AH.APT_FILE)
    assert not bool(z["passed"]) and int(z["cphf_refine_rounds"]) == 3 and (d / "hessian_wb97x_analytic.npz").exists()


def test_an_analytic_only_folder_gets_its_imaginary_counts(tmp_path, monkeypatch):
    """Chain 42 (12 Oct 2026): psi4_worker without Hessians leaves result.json without n_imaginary; analytic_hessians.py writes them there for
    such a folder (the loader reads its imaginary flag from result.json), and leaves an ordinary folder's result.json alone."""
    d = tmp_path / "water"
    d.mkdir()
    (d / "result.json").write_text(json.dumps({"layer": "T", "labels": "analytic_only", "status": "done"}))
    _run(tmp_path, monkeypatch, "--no-apt")
    r = json.loads((d / "result.json").read_text())
    assert r["n_imaginary_b3lyp"] == 0 and r["n_imaginary_wb97x"] == 0 and r["layer"] == "T"
    (d / "result.json").write_text(json.dumps({"layer": "A"}))
    _run(tmp_path, monkeypatch, "--no-apt")
    assert json.loads((d / "result.json").read_text()) == {"layer": "A"}


def test_reuse_existing_recomputes_only_the_missing_functional(tmp_path, monkeypatch):
    d = _run(tmp_path, monkeypatch, "--no-apt")
    b3lyp = (d / "hessian_b3lyp_analytic.npz").read_bytes()
    (d / "hessian_wb97x_analytic.npz").unlink()
    _run(tmp_path, monkeypatch, "--no-apt", "--reuse-existing")
    assert (d / "hessian_b3lyp_analytic.npz").read_bytes() == b3lyp and (d / "hessian_wb97x_analytic.npz").exists()
    assert set(json.loads((d / "analytic_check.json").read_text())) == {"b3lyp", "wb97x"}


def test_reuse_existing_and_compare_only_do_not_combine(tmp_path, monkeypatch):
    with pytest.raises(ValueError, match="do not combine"):
        _run(tmp_path, monkeypatch, "--compare-only", "--reuse-existing")


def test_pyscfs_own_log_lands_in_the_molecule_folder(tmp_path, monkeypatch):
    d = _run(tmp_path, monkeypatch, "--no-apt")
    log = (d / AH.PYSCF_LOG_NAME).read_text(encoding="utf-8")
    first_cycles = [s for s in log.splitlines() if s.startswith("cycle= 1 ")]
    assert len(first_cycles) == 2 and log.count("CPU time for RHF hessian") == 2      # both functionals' SCF and Hessian timers (RKS logs as RHF)
