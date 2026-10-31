"""The geometry-term read (`probes/geometry_term_check.py`, TASKS 156 (d)) on synthetic records, before any run: a water-like molecule whose
higher level's Hessian at its own minimum is built so that every band moves by exactly ½ Σ_k φ_iik Δq_k — the read must find the term,
equal through the true displacement and the Newton step — and the cases it must fail or refuse: the cubic constants of the wrong sign, a
missing run, a run made on another force field, a reference whose ω are not the force field's."""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import numpy as np
import pytest

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
import geometry_term_check as G  # noqa: E402

from dpir.qff import HARTREE_CM, atomic_masses_me, harmonic, translation_rotation_projector  # noqa: E402

SYM = ["O", "H", "H"]
X0 = np.array([[0.0, 0.0, 0.2216], [0.0, 1.4304, -0.8865], [0.0, -1.4304, -0.8865]])
OMEGA_CM = np.array([1650.0, 3800.0, 3900.0])
PHI_DIAG = np.array([[-120.0, 300.0, 40.0], [60.0, -900.0, 150.0], [30.0, 200.0, -950.0]])   # φ_iik, cm⁻¹
DQ = np.array([0.04, -0.03, 0.02])


def hessian(x: np.ndarray, omega_cm: np.ndarray, q: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray]:
    """A Cartesian Hessian with these frequencies; its mass-weighted modes q (the internal space's at x unless given)."""
    m = atomic_masses_me(SYM)
    if q is None:
        P = translation_rotation_projector(x, m)
        w, v = np.linalg.eigh(P)
        q = v[:, w > 0.5]
    F = q @ np.diag((omega_cm / HARTREE_CM) ** 2) @ q.T
    mh = np.repeat(np.sqrt(m), 3)
    return mh[:, None] * F * mh[None, :], q


def write_molecule(s2: Path, runs: Path, mol_id: str, sign: float = 1.0) -> None:
    H_g, _ = hessian(X0, OMEGA_CM)
    hg = harmonic(H_g, SYM, X0)
    phi = np.zeros((3, 3, 3))
    for i in range(3):
        phi[i, i, :] = sign * PHI_DIAG[i]
    g_dir = s2 / mol_id / "G"
    g_dir.mkdir(parents=True)
    (g_dir / "ref.json").write_text(json.dumps({"molecule": {"symbols": SYM, "geometry": X0.reshape(-1).tolist()},
                                                "return_result": H_g.reshape(-1).tolist()}), encoding="utf-8")
    np.savez(g_dir / "qff_report.npz", omega_cm=hg.omega_cm, phi_ijk=phi)
    dx = (hg.A @ DQ).reshape(3, 3)
    x_t = X0 + dx
    moved = hg.omega_cm + 0.5 * PHI_DIAG @ DQ               # the true cubics: the sign test's report lies about them
    H_t, _ = hessian(x_t, moved, q=hg.q)
    run_dir = runs / mol_id
    run_dir.mkdir(parents=True)
    np.savez(run_dir / G.RUN_FILE, x0=X0, g0=-(H_g @ dx.reshape(-1)).reshape(3, 3), H0=H_g, x_t=x_t, H_t=H_t,
             ref_sha256=G.sha256(g_dir / "ref.json"), qff_sha256=G.sha256(g_dir / "qff_report.npz"))


def test_the_term_is_found_through_the_true_displacement_and_the_newton_step(tmp_path):
    write_molecule(tmp_path / "s2", tmp_path / "runs", "M")
    m = G.molecule("M", tmp_path / "s2" / "M" / "G", tmp_path / "runs" / "M" / G.RUN_FILE)
    assert np.abs(m.measured).min() > G.MIN_SHIFT_CM
    assert np.allclose(m.predicted_true, m.measured, atol=0.05) and np.allclose(m.predicted_newton, m.predicted_true, atol=1e-6)
    assert m.min_overlap > 0.99


def molecules(tmp_path: Path, n: int, sign: float = 1.0) -> tuple[Path, Path]:
    for k in range(n):
        write_molecule(tmp_path / "s2", tmp_path / "runs", f"M{k:02d}", sign)
    return tmp_path / "s2", tmp_path / "runs"


def test_eighteen_molecules_pass_every_line_and_the_report_is_written(tmp_path):
    s2, runs = molecules(tmp_path, 18)
    s = G.read(s2, runs, tmp_path / "out")
    assert s["passed"] and s["molecules_helped"] == 18 and s["rms_residual_true"] < 0.01 * s["rms_shift"]
    assert {k for k, v in s["windows"].items() if v["read"]} == {"1000-1900", "X-H stretch"}
    assert (tmp_path / "out" / "geometry_term_read.md").read_text(encoding="utf-8").count("holds") == 4


def test_cubic_constants_of_the_wrong_sign_fail(tmp_path):
    s2, runs = molecules(tmp_path, 18, sign=-1.0)
    s = G.read(s2, runs, tmp_path / "out")
    assert not s["lines"]["A"] and not s["lines"]["C"] and not s["passed"]


def test_a_force_field_without_its_run_is_refused(tmp_path):
    s2, runs = molecules(tmp_path, 2)
    shutil.rmtree(runs / "M01")
    with pytest.raises(SystemExit, match="no run for M01"):
        G.read(s2, runs, tmp_path / "out")


def test_a_run_on_another_force_field_is_refused(tmp_path):
    s2, runs = molecules(tmp_path, 1)
    with np.load(s2 / "M00" / "G" / "qff_report.npz") as z:
        np.savez(s2 / "M00" / "G" / "qff_report.npz", omega_cm=z["omega_cm"], phi_ijk=z["phi_ijk"] * 1.01)
    with pytest.raises(SystemExit, match="another force field"):
        G.read(s2, runs, tmp_path / "out")


def test_a_reference_whose_frequencies_are_not_the_force_fields_is_refused(tmp_path):
    s2, runs = molecules(tmp_path, 1)
    g = s2 / "M00" / "G"
    with np.load(g / "qff_report.npz") as z:
        np.savez(g / "qff_report.npz", omega_cm=z["omega_cm"] + 1.0, phi_ijk=z["phi_ijk"])
    with np.load(runs / "M00" / G.RUN_FILE) as z:
        np.savez(runs / "M00" / G.RUN_FILE, **{k: z[k] for k in z.files} | {"qff_sha256": G.sha256(g / "qff_report.npz")})
    with pytest.raises(SystemExit, match="differ from the force field's"):
        G.read(s2, runs, tmp_path / "out")
