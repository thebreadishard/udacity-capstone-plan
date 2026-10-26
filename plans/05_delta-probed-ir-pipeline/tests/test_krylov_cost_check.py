"""probes/krylov_cost_check.py and krylov_cost_compare.py (TASKS 133): the residual of solve_nos1's equation on a synthetic system (zero at
the exact solution, the known size off it) and on water's RHF CPHF through the recording wrapper; the comparison's threshold both ways and
its refusals. Runs where pyscf is installed (WSL ~/qc05)."""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

pyscf = pytest.importorskip("pyscf")
from pyscf import gto, lib, scf  # noqa: E402
from pyscf.scf import cphf  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "probes"))
import krylov_cost_check as K  # noqa: E402
import krylov_cost_compare as C  # noqa: E402

NOCC, NVIR = 2, 3


def synthetic():
    rng = np.random.default_rng(7)
    mo_energy = np.array([-1.0, -0.5, 0.3, 0.7, 1.2])
    mo_occ = np.array([2, 2, 0, 0, 0])
    a = rng.normal(size=(NVIR * NOCC, NVIR * NOCC)) * 0.1
    h1 = rng.normal(size=(NVIR, NOCC))
    e_ai = 1 / (mo_energy[NOCC:, None] - mo_energy[:NOCC])

    def fvind(x):
        return (a @ x.reshape(-1, NVIR * NOCC).T).T.reshape(-1, NVIR, NOCC)

    b = (-e_ai * h1).ravel()
    exact = np.linalg.solve(np.eye(NVIR * NOCC) + e_ai.ravel()[:, None] * a, b).reshape(NVIR, NOCC)
    return fvind, mo_energy, mo_occ, h1, exact, b


def test_the_residual_is_zero_at_the_exact_solution_and_the_known_size_off_it():
    fvind, mo_energy, mo_occ, h1, exact, b = synthetic()
    assert K.relative_residual(fvind, mo_energy, mo_occ, h1, exact) < 1e-14
    e_ai = 1 / (mo_energy[NOCC:, None] - mo_energy[:NOCC])
    delta = np.zeros_like(exact)
    delta[1, 0] = 1e-3
    expected = np.linalg.norm(delta + e_ai * fvind(delta)[0]) / np.linalg.norm(b)
    assert K.relative_residual(fvind, mo_energy, mo_occ, h1, exact + delta) == pytest.approx(expected, rel=1e-10)


def water_cphf():
    """(fvind, mo_energy, mo_occ, h1) of water's RHF response to a z field, the operator as grad/ccsd.py builds it."""
    mol = gto.M(atom="O 0 0 0; H 0 -0.757 0.587; H 0 0.757 0.587", basis="6-31g", verbose=0)
    mf = scf.RHF(mol).run(conv_tol=1e-12)
    occ, vir = mf.mo_occ > 0, mf.mo_occ == 0
    co, cv = mf.mo_coeff[:, occ], mf.mo_coeff[:, vir]

    def fvind(x):
        x = x.reshape(-1, cv.shape[1], co.shape[1])
        dm = np.einsum("pa,xai,qi->xpq", cv, x, co)
        v = mf.get_veff(mol, dm + dm.transpose(0, 2, 1))
        return np.einsum("pa,xpq,qi->xai", cv, v, co) * 2

    return fvind, mf.mo_energy, mf.mo_occ, np.einsum("pa,pq,qi->ai", cv, mol.intor("int1e_r")[2], co)


def test_the_wrapper_records_water_s_cphf_and_returns_pyscf_s_solution():
    fvind, mo_energy, mo_occ, h1 = water_cphf()
    records: list[dict] = []
    got = K.recording(cphf.solve, records)(fvind, mo_energy, mo_occ, h1, max_cycle=30)[0]
    ref = cphf.solve(fvind, mo_energy, mo_occ, h1, max_cycle=30)[0]
    np.testing.assert_allclose(got, ref, atol=1e-10)      # two solves differ in the last bits: threaded J/K sums
    assert len(records) == 1 and records[0]["max_cycle"] == 30
    assert 0 < records[0]["residual"] < 1e-6, records


MASTER = Path.home() / "pyscf-wt-base"


@pytest.mark.skipif(not (MASTER / "pyscf" / "scf" / "cphf.py").exists(), reason="no pyscf master checkout at ~/pyscf-wt-base")
def test_the_upstream_cphf_solves_water_with_lindep_and_restores_the_release_s_krylov():
    fvind, mo_energy, mo_occ, h1 = water_cphf()
    solve, module = K.upstream_solve(MASTER)
    released = lib.krylov
    x = solve(fvind, mo_energy, mo_occ, h1, max_cycle=30)[0]
    assert lib.krylov is released
    assert K.passes_lindep(module) and not K.passes_lindep(cphf)
    assert K.relative_residual(fvind, mo_energy, mo_occ, h1, x) < 1e-6


def test_a_solve_with_s1_is_recorded_as_not_measured():
    records: list[dict] = []
    K.recording(lambda *a, **k: (np.zeros(1), None), records)(None, None, None, None, s1=np.zeros(1))
    assert records == [{"residual": None, "why": "s1 or a level shift: not solve_nos1's equation"}]


def test_without_only_reference_the_check_refuses():
    with pytest.raises(SystemExit, match="--only-reference"):
        K.main(["geometry.json", "out"])


def write_run(run: Path, g: np.ndarray, lindep: bool, residual: float) -> Path:
    run.mkdir()
    np.savez(run / "reference.npz", gradient=g, energy=0.0)
    (run / "krylov_residuals.json").write_text(json.dumps({"solve_nos1_passes_lindep": lindep, "solves": [{"residual": residual}]}),
                                               encoding="utf-8")
    return run


@pytest.mark.parametrize(("shift", "beyond"), [(5e-7, False), (2e-6, True)])
def test_the_comparison_reads_the_threshold_both_ways(tmp_path, shift, beyond):
    g = np.arange(6.0).reshape(2, 3) * 1e-2
    released = write_run(tmp_path / "released", g + shift, False, 3e-5)
    master = write_run(tmp_path / "master", g, True, 2e-10)
    record = C.compare(released, master)
    assert record["beyond_threshold"] is beyond
    assert record["max_abs_dg"] == pytest.approx(shift)
    assert record["residuals_released"] == [3e-5] and record["residuals_master"] == [2e-10]


def test_the_comparison_refuses_runs_in_the_wrong_order(tmp_path):
    g = np.zeros((2, 3))
    released = write_run(tmp_path / "released", g, True, 1e-9)
    master = write_run(tmp_path / "master", g, True, 1e-9)
    with pytest.raises(SystemExit, match="release without lindep"):
        C.compare(released, master)


def test_the_comparison_refuses_an_unfinished_run(tmp_path):
    master = write_run(tmp_path / "master", np.zeros((2, 3)), True, 1e-9)
    (tmp_path / "released").mkdir()
    with pytest.raises(SystemExit, match="did not finish"):
        C.compare(tmp_path / "released", master)
