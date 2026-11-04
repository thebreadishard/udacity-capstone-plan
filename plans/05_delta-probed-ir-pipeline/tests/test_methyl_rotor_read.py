"""probes/methyl_rotor_read.py on synthetic records, before any of its data exists (PreRegistration_2026-11-04_Methyl_Rotor_Variational.md):
a pure cosine recovers V3/V6, a free rotor gives F m², a separable harmonic surface gives ω exactly and no coupling shift, a coupled
surface moves the bend (against its value at τ₀), and the scan read stops a non-periodic scan."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes"))
import methyl_rotor_read as R


def test_a_pure_cosine_recovers_v3_and_v6():
    tau = np.radians(np.arange(12) * 10.0)
    e = 7.0 + 300.0 / 2 * (1 - np.cos(3 * tau)) - 12.0 / 2 * (1 - np.cos(6 * tau))
    v3, v6, c = R.fit_v3_v6(tau, e)
    assert v3 == pytest.approx(300.0, abs=1e-9) and v6 == pytest.approx(-12.0, abs=1e-9) and c == pytest.approx(7.0, abs=1e-9)


def test_a_free_rotor_has_levels_F_m_squared():
    lv = R.torsion_levels(5.0, 0.0, 0.0, m_max=10)
    np.testing.assert_allclose(lv[:5], [0.0, 5.0, 5.0, 20.0, 20.0], atol=1e-9)


def test_the_periodic_dvr_gives_free_rotor_levels():
    lv = np.linalg.eigvalsh(R.fourier_dvr_kinetic(24))
    np.testing.assert_allclose(lv[:9], [0, 1, 1, 4, 4, 9, 9, 16, 16], atol=1e-9)


def separable_surface(nt: int, nq: int, omega: tuple[float, float], v3: float) -> np.ndarray:
    tau = 2 * np.pi * np.arange(nt) / nt
    q = R.ho_dvr(nq, 1.0)[0]
    return (v3 / 2 * (1 - np.cos(3 * tau)))[:, None, None] + (omega[0] / 2 * q**2)[None, :, None] + (omega[1] / 2 * q**2)[None, None, :]


def test_a_separable_harmonic_surface_gives_omega_and_no_coupling_shift():
    omega = (1507.5, 1521.1)
    V = separable_surface(24, 11, omega, 300.0)
    s = R.coupling_shifts(V, 5.5, omega)
    assert s["full"]["nu20"] == pytest.approx(omega[0], abs=1e-6) and s["full"]["nu21"] == pytest.approx(omega[1], abs=1e-6)
    assert s["delta20"] == pytest.approx(0.0, abs=1e-9) and s["delta21"] == pytest.approx(0.0, abs=1e-9)


@pytest.mark.parametrize("c", [0.02, -0.02])
def test_a_torsion_bend_coupling_moves_the_bend_against_its_value_at_tau0(c):
    """V_nt cuts the bend at τ₀, where this coupling is largest; the torsion's zero-point motion samples it weaker, so the coupled bend
    lies on the other side: Δ_var < 0 for a bend stiffer at τ₀ (c > 0). This is what the registered Δ measures, and what removing the
    torsion from VPT2 (the bend at a frozen τ₀) compares against."""
    omega = (1507.5, 1521.1)
    nt, nq = 24, 11
    V = separable_surface(nt, nq, omega, 300.0)
    tau = 2 * np.pi * np.arange(nt) / nt
    q = R.ho_dvr(nq, 1.0)[0]
    V = V + (c * omega[0] / 2 * np.cos(3 * tau))[:, None, None] * (q**2)[None, :, None]   # the bend stiffer near τ₀ for c > 0
    s = R.coupling_shifts(V, 5.5, omega)
    assert np.sign(s["delta20"]) == -np.sign(c) and abs(s["delta20"]) > 1.0
    assert abs(s["delta21"]) < 1e-6


@pytest.mark.skipif(not (R.BRIDGE / "bridge_4mi_zmat_dec.json").exists(), reason="TASKS 173's Psience runs not here")
def test_the_grid_read_on_a_separable_surface_finds_no_coupling_and_reads_vpt2_as_spurious(tmp_path):
    """The whole grid read on files: no torsion–bend coupling on the surface, while the stored full-dimensional VPT2 Δ is ≥ 3 cm⁻¹ for
    mode 20 in both coordinate sets — branch (iii) of amendment 1."""
    omega, nt, nq = (1507.5, 1521.1), 8, 5
    V = separable_surface(nt, nq, omega, 300.0)
    points, energies = [], {}
    for t in range(nt):
        for a in range(nq):
            for b in range(nq):
                idx = (t * nq + a) * nq + b
                points.append({"index": idx, "k_tau": t, "i20": a, "i21": b})
                energies[str(idx)] = float(V[t, a, b] / R.HARTREE_CM)
    (tmp_path / "grid.json").write_text(json.dumps({"n_tau": nt, "n_q": nq, "bends": [20, 21], "omega_cm": list(omega), "points": points}),
                                        encoding="utf-8")
    (tmp_path / "energies_lane00.json").write_text(json.dumps(energies), encoding="utf-8")
    r = R.read_grid(tmp_path, {"F_cm": 5.5})
    assert abs(r["variational"]["delta20"]) < 1e-9 and r["convergence_cm"] < 1e-9
    assert r["delta_vpt2_full_dimension"]["cart"]["20"] == pytest.approx(6.50, abs=0.01)
    assert r["verdict"].startswith("VPT2's torsion–bend coupling is spurious")


def write_scan(tmp_path, e_end_offset_cm: float) -> None:
    for k in range(13):
        tau = np.radians(10.0 * k)
        e = (310.0 / 2 * (1 - np.cos(3 * tau))) / R.HARTREE_CM + (e_end_offset_cm / R.HARTREE_CM if k == 12 else 0.0)
        geom = [[0.0, 0.0, 0.0], [2.8, 0.0, 0.0], [3.8, 2.0, 0.0], [-0.7, 1.7, 0.4], [-0.7, -1.2, 1.3], [-0.7, -0.5, -1.7], [5.0, -1.0, 0.0],
                [3.0, 3.6, 0.0], [5.5, 1.4, 0.0], [-0.7, 1.0, 1.4], [2.0, -2.0, 0.0], [6.0, 2.0, 0.0]]
        sym = ["C", "C", "C", "H", "H", "H", "N", "H", "C", "H", "N", "H"]
        # the read takes the top from atoms 6–8 and the axis 1→0: put the methyl H there
        sym[6:9], sym[3:6] = ["H", "H", "H"], ["N", "C", "N"]
        geom[6:9], geom[3:6] = geom[3:6], geom[6:9]
        (tmp_path / f"scan_k{k:02d}.json").write_text(json.dumps({"k": k, "tau0_deg": 0.0, "achieved_deg": 10.0 * k, "energy": e,
                                                                  "symbols": sym, "geometry_bohr": geom}), encoding="utf-8")


def test_the_scan_read_recovers_its_barrier_and_judges_it(tmp_path):
    write_scan(tmp_path, 0.0)
    r = R.read_scan(tmp_path)
    assert r["V3_cm"] == pytest.approx(310.0, abs=1e-6) and r["periodicity_cm"] < 1e-9
    assert r["verdict"].startswith("B3LYP's barrier within 15 %") and r["F_cm"] > 0


def test_the_scan_read_stops_a_scan_that_is_not_periodic(tmp_path):
    write_scan(tmp_path, 0.8)
    assert R.read_scan(tmp_path)["verdict"].startswith("scan not converged")
