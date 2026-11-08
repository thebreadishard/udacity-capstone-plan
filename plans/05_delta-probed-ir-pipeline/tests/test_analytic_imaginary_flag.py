"""TASKS 188 (8 Nov 2026): on analytic labels the imaginary-mode flag follows the analytic frequencies, every negative mode counting (pyscf's
own count), and the trainer's substitution sets it — until then it kept the finite-difference counts of result.json."""
import shutil
import sys
from pathlib import Path

import numpy as np
import pytest

PLAN = Path(__file__).resolve().parents[1]
pytest.importorskip("torch")                                              # module 05's loaders import torch
sys.path.insert(0, str(PLAN / "modules" / "05_support_predictor" / "m05"))
import learning_curve_layerA as LA  # noqa: E402

MOLECULES = PLAN / "modules" / "05_support_predictor" / "corpus" / "molecules"
FD_ONLY = MOLECULES / "P3_2a090cd77b"                 # ωB97X FD −39.8 cm⁻¹ (a methyl torsion); both analytic Hessians real
needs_corpus = pytest.mark.skipif(not (FD_ONLY / "hessian_wb97x_analytic.npz").exists(), reason="the analytic corpus folder is not present")


@pytest.mark.parametrize(("freq", "expected"), [
    ([0.0, -0.0, 0.0, 0.0, -0.0, 0.0, 30.1, 76.9], 0),          # the six trans/rot entries, signed zeros included, never count
    ([0.0, -0.0, 0.0, 0.0, -0.0, 0.0, -4.6, 48.2], 1),          # a soft analytic mode counts however small
    ([0.1, -0.2, 0.0, 0.3, -0.1, 0.0, -52.4, -27.3, 33.7], 2),
])
def test_every_negative_vibrational_mode_counts(freq, expected):
    assert LA.n_imaginary(np.array(freq)) == expected


def _with_lowest_b3lyp(folder: Path, value: float) -> None:
    """Rewrite the analytic B3LYP file's lowest vibrational frequency (the flag reads freq_cm; the Hessian itself is left alone)."""
    path = folder / "hessian_b3lyp_analytic.npz"
    z = dict(np.load(path))
    f = z["freq_cm"].copy()
    vib = np.argsort(np.abs(f))[6:]
    f[vib[np.argmin(f[vib])]] = value
    z["freq_cm"] = f
    np.savez(path, **z)


@pytest.mark.data
@needs_corpus
def test_the_substitution_takes_the_flag_from_the_analytic_frequencies(tmp_path):
    import e7_rungB_reread_analytic as RR
    import e7_t2_sqm as T2
    shutil.copytree(FD_ONLY, tmp_path / FD_ONLY.name)
    m = T2.load(tmp_path)[FD_ONLY.name]
    assert m["imaginary"]                                                 # the FD counts flag it
    assert not RR.substitute(m, tmp_path / FD_ONLY.name)["imaginary"]     # real on both analytic Hessians
    _with_lowest_b3lyp(tmp_path / FD_ONLY.name, -4.6)
    assert RR.substitute(T2.load(tmp_path)[FD_ONLY.name], tmp_path / FD_ONLY.name)["imaginary"]
