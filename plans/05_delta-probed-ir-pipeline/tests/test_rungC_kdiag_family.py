"""Chain 34 (3 Oct 2026, decision 53): the family-balanced K-diagonal term of rungC_train. Synthetic tensors: two families whose true diagonals differ
20× in size; an error on the small family alone barely moves the 'all' term and moves the 'family' term by half its size; with one family the two modes
agree; kring_tensors carries one code per family label; the CLI flag and the train_one parameter exist; the loader defaults old records to 'all'."""
import inspect
import re
import sys
from pathlib import Path

import numpy as np
import pytest

torch = pytest.importorskip("torch")
PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "modules" / "05_support_predictor" / "m05"))
import rungC_train as RT  # noqa: E402


def _tensors(d_true, fam):
    n = len(d_true)
    return dict(Cm=torch.eye(n), kscale=torch.ones(n, n), K_true=torch.diag(torch.tensor(d_true, dtype=torch.float32)),
                fam_code=torch.tensor(fam, dtype=torch.long))


def test_family_mode_weighs_the_small_family():
    t = _tensors([100.0, 100.0, 5.0, 5.0], [0, 0, 1, 1])
    pred = torch.diag(torch.tensor([100.0, 100.0, 0.0, 0.0]))        # the big family exact, the small one entirely missing
    assert float(RT._kdiag_term(t, pred, "all")) == pytest.approx(12.5 / 5012.5, rel=1e-4)
    assert float(RT._kdiag_term(t, pred, "family")) == pytest.approx(0.5, rel=1e-5)
    assert float(RT._kdiag_term(t, pred)) == float(RT._kdiag_term(t, pred, "all"))


def test_one_family_makes_the_modes_equal():
    t = _tensors([3.0, -2.0, 7.0], [0, 0, 0])
    pred = torch.diag(torch.tensor([2.0, -2.5, 8.0]))
    assert float(RT._kdiag_term(t, pred, "family")) == pytest.approx(float(RT._kdiag_term(t, pred, "all")), rel=1e-6)


def test_unknown_mode_refused():
    t = _tensors([1.0, 2.0], [0, 1])
    with pytest.raises(ValueError):
        RT._kdiag_term(t, torch.zeros(2, 2), "ring")


def test_kring_tensors_family_codes():
    fam = ["ring-ip", "CH-oop", "other", "ring-ip", "CH-stretch", "other"]
    t = RT.kring_tensors(np.ones(2), np.eye(6), np.ones(6), fam, np.zeros((6, 6)))
    codes = t["fam_code"].tolist()
    assert len(codes) == 6 and len(set(codes)) == 4
    assert codes[0] == codes[3] and codes[2] == codes[5] and codes[1] != codes[4]


def test_flag_parameter_and_loader_default():
    src = (PLAN / "modules" / "05_support_predictor" / "m05" / "rungC_train.py").read_text(encoding="utf-8")
    assert re.search(r'add_argument\("--kdiag-mode", default="all", choices=\["all", "family", "family-low"\]', src)
    assert "kdiag_mode" in inspect.signature(RT.train_one).parameters
    assert 'ck.get("kdiag_mode", "all")' in src


def test_family_low_splits_other_at_700():
    """Chain 34c (4 Oct 2026): kring_tensors carries a second code array with 'other' split at LOW_CM; the 'family-low' term uses it and equals
    'family' when no 'other' mode lies below the line."""
    masses = np.array([12.0, 1.0])
    V = np.eye(6)
    dH = np.eye(6) * 1e-3
    w_cm = np.array([300.0, 1200.0, 1500.0, 3000.0, 500.0, 900.0])
    w = (w_cm / RT.PH.HARTREE2CM) ** 2
    fam = ["other", "ring-ip", "ring-ip", "CH-stretch", "other", "other"]
    t = RT.kring_tensors(masses, V, w, fam, dH)
    low = t["fam_code_low"].numpy()
    plain = t["fam_code"].numpy()
    assert len(set(plain)) == 3 and len(set(low)) == 4                      # other split into low (300, 500) and mid (900)
    assert low[0] == low[4] and low[0] != low[5] and plain[0] == plain[5]
    pred = torch.as_tensor(dH * 0.9, dtype=torch.float32)                      # a Cartesian ΔH at 90 % of the truth: relative error 0.01 in every family
    assert float(RT._kdiag_term(t, pred, "family-low")) == pytest.approx(0.01, rel=1e-4)
    t2 = RT.kring_tensors(masses, V, (np.array([900.0, 1200.0, 1500.0, 3000.0, 800.0, 950.0]) / RT.PH.HARTREE2CM) ** 2, fam, dH)
    assert float(RT._kdiag_term(t2, pred, "family-low")) == pytest.approx(float(RT._kdiag_term(t2, pred, "family")), rel=1e-6)
    with pytest.raises(ValueError):
        RT._kdiag_term(t, pred, "family-lo")
