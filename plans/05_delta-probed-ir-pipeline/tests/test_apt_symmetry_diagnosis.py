"""probes/apt_symmetry_diagnosis.py (14 Oct 2026): on a synthetic C2v-symmetric APT the deviations are zero and symmetrising changes nothing;
on the fetched anchors it reproduces the numbers azulene's decision rests on (geometry 2.6e-3 bohr, field APT 3.4e-3 off C2v, FD-dipole sum
rule 1.7e-3, 2.39e-3 stored and 1.09e-3 symmetrised) and quinoxaline's (1.6e-4)."""
import sys
from pathlib import Path

import numpy as np
import pytest

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
import apt_symmetry_diagnosis as A  # noqa: E402

RES = PLAN / "probes" / "results_m1"
AZ, QX = RES / "e8_azulene_ccpvdz_2026-10-14", RES / "e8_quinoxaline_ccpvdz_2026-10-13"


def test_a_symmetric_apt_has_no_deviation(tmp_path):
    # water in the yz plane (C2v about z); an APT built as the group average of a random tensor is symmetric by construction
    sym = np.array(["O", "H", "H"])
    x = np.array([[0.0, 0.0, 0.2217], [0.0, 1.4309, -0.8867], [0.0, -1.4309, -0.8867]])
    ops = A.point_group_ops(list(sym), x)
    reps = [(R, A.rep(R, p, 3)) for R, p in ops]
    P = np.random.default_rng(0).normal(size=(3, 9))
    P = sum(R.T @ P @ D for R, D in reps) / len(reps)
    P = (P.reshape(3, 3, 3) - P.reshape(3, 3, 3).mean(1, keepdims=True)).reshape(3, 9)      # translation sum rule
    for name in ("f.npz", "r.npz"):
        np.savez(tmp_path / name, apt=P, coords_bohr=x, symbols=sym)
    d = A.diagnose(str(tmp_path / "f.npz"), str(tmp_path / "r.npz"))
    assert len(ops) == 4 and d["geometry_symmetry_residual_bohr"] < 1e-12
    assert max(d["symmetry_deviation"].values()) < 1e-12 and max(d["translation_sum_rule"].values()) < 1e-12 and d["max_abs_diff"] == 0


@pytest.mark.skipif(not (AZ / "apt_ccsd_t_field.npz").exists() or not (QX / "apt_ccsd_t_field.npz").exists(), reason="anchor results not here")
def test_the_numbers_of_the_azulene_decision():
    az = A.diagnose(str(AZ / "apt_ccsd_t_field.npz"), str(AZ / "apt_ccsd_t.npz"))
    assert az["geometry_symmetry_residual_bohr"] == pytest.approx(2.6e-3, abs=5e-5)
    assert az["symmetry_deviation"]["field"] == pytest.approx(3.44e-3, abs=5e-5)
    assert az["translation_sum_rule"]["fd_dipole"] == pytest.approx(1.74e-3, abs=5e-5)
    assert az["max_abs_diff"] == pytest.approx(2.39e-3, abs=5e-5) and az["max_abs_diff_both_symmetrised"] == pytest.approx(1.09e-3, abs=5e-5)
    qx = A.diagnose(str(QX / "apt_ccsd_t_field.npz"), str(QX / "apt_ccsd_t.npz"))
    assert qx["max_abs_diff"] == pytest.approx(1.6e-4, abs=5e-6) and qx["geometry_symmetry_residual_bohr"] < 1e-4


MOL = PLAN / "modules" / "05_support_predictor" / "corpus" / "molecules"


@pytest.mark.skipif(not (MOL / "A_d9139359ab" / "hessian_b3lyp_analytic.npz").exists(), reason="corpus molecules not here")
def test_geometry_survey_on_azulene_and_benzene():
    """probes/geometry_symmetry_survey.py: azulene's corpus geometry is C2v to 2.6e-3 bohr and forcing the symmetry moves its B3LYP
    frequencies by 0.056 cm⁻¹; benzene (D6h, 24 operations, rotations beyond C2 — the convention test) holds to 1.4e-4 bohr."""
    import geometry_symmetry_survey as G
    az = G.survey_one(str(MOL / "A_d9139359ab"))
    assert az["n_ops"] == 4 and az["geometry_residual_bohr"] == pytest.approx(2.6e-3, abs=5e-5)
    assert az["max_abs_dfreq_symmetrised_cm"] == pytest.approx(0.056, abs=2e-3)
    bz = G.survey_one(str(MOL / "A_8448043181"))
    assert bz["n_ops"] == 24 and bz["geometry_residual_bohr"] < 2e-4
