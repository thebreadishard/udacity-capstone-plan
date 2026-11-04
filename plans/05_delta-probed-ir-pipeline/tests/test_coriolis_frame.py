"""The Coriolis term in the principal frame (TASKS 174, 4 Nov 2026): `coriolis_zeta` used to build ζ^a in the lab frame of the stored
geometry while `rotational_constants` returns the sorted principal constants, so `vpt2` paired them correctly only for a geometry that
already sat in its principal frame in that order (psi4's standard orientation, which is why `test_data_water.py` never saw it). On the
pyscf water of S1 the two stretch-bend fundamentals came out 23 cm⁻¹ high, against Psience 1.6.1 (TASKS 173's bridge)."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from conftest import PROBES, _need
from dpir.qff import HessianRecord, coriolis_zeta, load_results, qff_from_records, rotational_constants, vpt2

S1_WATER_G = PROBES / "results_m1" / "s1_anharmonic_benzene_2026-10-13" / "s1_smoke_water" / "G" / "hess"   # pyscf, lab frame, step 0.10
PSIENCE_WATER_G = PROBES / "results_m1" / "psience_bridge_2026-11-04" / "bridge_water_cart.json"         # Psience 1.6.1 on that set


def fundamentals(recs: list[HessianRecord], disp: float) -> np.ndarray:
    """VPT2 fundamentals (cm⁻¹) without resonance handling, the Coriolis term included."""
    qff, harm, ref, _ = qff_from_records(recs, disp, allow_noisy=True)
    B = rotational_constants(ref.geom, ref.symbols)
    zeta = coriolis_zeta(harm.q, ref.symbols, ref.geom)
    return vpt2(qff.omega_cm, qff.phi3, qff.phi4, B, zeta, fermi_window=0.0)[0]


def rotated(recs: list[HessianRecord], R: np.ndarray) -> list[HessianRecord]:
    """Every record turned rigidly by R: geometry x → R x per atom, Hessian H → R_big H R_bigᵀ."""
    out = []
    for r in recs:
        n = len(r.symbols)
        Rb = np.kron(np.eye(n), R)
        out.append(HessianRecord(r.file, (r.geom.reshape(n, 3) @ R.T).ravel(), Rb @ r.H @ Rb.T, list(r.symbols)))
    return out


@pytest.mark.parametrize("seed", [1, 2, 3])
def test_vpt2_does_not_depend_on_the_orientation_of_the_molecule(water_cache, seed):
    """A rigid rotation of the whole force field leaves every fundamental unchanged (before the fix: up to 23 cm⁻¹)."""
    recs = load_results(str(water_cache))
    q, _ = np.linalg.qr(np.random.default_rng(seed).normal(size=(3, 3)))
    R = q * np.sign(np.linalg.det(q))
    np.testing.assert_allclose(fundamentals(rotated(recs, R), 0.05), fundamentals(recs, 0.05), atol=1e-6)


def test_water_in_its_lab_frame_agrees_with_psience():
    """S1's pyscf water (lab frame): our fundamentals within 0.05 cm⁻¹ of Psience's on the same force field (measured 4 Nov 2026:
    0.003, 0.011, 0.011 after the fix; before it modes 0 and 2 were 23.0 cm⁻¹ high)."""
    recs = load_results(str(_need(S1_WATER_G)))
    psience = np.array(json.loads(Path(_need(PSIENCE_WATER_G)).read_text(encoding="utf-8"))["nu_psience_cm"], float)
    np.testing.assert_allclose(fundamentals(recs, 0.10), psience, atol=0.05)


def test_coriolis_zeta_requires_the_geometry(model_molecule):
    """The frame comes from the geometry: a call without it fails loudly rather than falling back to the lab frame."""
    symbols, _geom, _m, _rng = model_molecule
    q = np.linalg.qr(np.random.default_rng(0).normal(size=(3 * len(symbols), 3 * len(symbols) - 6)))[0]
    with pytest.raises(TypeError):
        coriolis_zeta(q, symbols)  # type: ignore[call-arg]
