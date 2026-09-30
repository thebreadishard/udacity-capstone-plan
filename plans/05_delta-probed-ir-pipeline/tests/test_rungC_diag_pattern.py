"""rungC_train switches of 30 Sep 2026 (after the external reviews): the pattern internal term, its class scales, the zeroed-H_low diagnostic and the
overfit-one diagnostic. Synthetic tensors for the term and the scales (no torch model needed beyond a stub); the pattern builder on the corpus benzene
when geomeTRIC and the corpus are present; the CLI flags from the source."""
import re
import sys
from pathlib import Path

import numpy as np
import pytest

torch = pytest.importorskip("torch")
PLAN = Path(__file__).resolve().parents[1]
M05 = PLAN / "modules" / "05_support_predictor" / "m05"
sys.path.insert(0, str(M05))
import rungC_train as R  # noqa: E402

CORPUS = PLAN / "modules" / "05_support_predictor" / "corpus" / "molecules"


def _tensors():
    """Two fake molecules with 4 internal coordinates: pattern classes on a few entries, −1 elsewhere."""
    cls = torch.full((4, 4), -1, dtype=torch.long)
    cls[0, 0], cls[1, 1], cls[2, 2], cls[3, 3] = 0, 1, 2, 3      # diagonal classes
    cls[0, 1] = cls[1, 0] = 4                                    # bond–bond
    cls[2, 3] = cls[3, 2] = 5                                    # other coupling
    t1 = dict(dF_true=torch.tensor([[2., 1., 0, 0], [1., 4., 0, 0], [0, 0, 6., 3.], [0, 0, 3., 8.]]), pat_cls=cls)
    t2 = dict(dF_true=torch.tensor([[4., 3., 0, 0], [3., 0., 0, 0], [0, 0, 0., 1.], [0, 0, 1., 0.]]), pat_cls=cls)
    return {"m1": t1, "m2": t2}


def test_pattern_class_scales_are_rms_per_class_over_fit_ids_only():
    T = _tensors()
    s = R.pattern_class_scales(T, ["m1", "m2"])
    assert torch.allclose(s[0], torch.tensor((2. ** 2 + 4. ** 2) / 2).sqrt())            # diag_bond: entries (0,0) of both molecules
    assert torch.allclose(s[4], torch.tensor((1. + 1. + 9. + 9.) / 4).sqrt())              # off_bondbond: both triangles of both molecules
    s1 = R.pattern_class_scales(T, ["m1"])
    assert torch.allclose(s1[5], torch.tensor(3.))                                          # from m1 alone
    assert s.shape == (len(R.PAIR_CLASS_NAMES),) and (s > 0).all()


def test_pattern_term_equals_manual_standardised_mse_and_ignores_off_pattern_entries():
    T = _tensors()
    t = dict(T["m1"], Z=None, pos=None, H_low=None, mw=torch.ones(4, 4), dH_true=torch.zeros(4, 4), Bp=torch.eye(4), dF_norm=torch.tensor(1.))

    class Stub:
        aux_mode = "pattern"
        aux_class_scale = torch.tensor([2., 1., 1., 1., 0.5, 3.])

        def __call__(self, Z, pos, H_low, tt):
            out = torch.zeros(4, 4)
            out[0, 0] = 3.0      # class 0: error (3−2)/2 = 0.5
            out[0, 1] = out[1, 0] = 0.0   # class 4: error (0−1)/0.5 = −2 twice
            out[1, 3] = out[3, 1] = 100.  # off-pattern: must not count
            return out

    main, aux, _ = R._terms(Stub(), t)
    on = (t["pat_cls"] >= 0).sum().item()                       # 4 diagonal + 4 off-diagonal entries
    expected = (0.5 ** 2 + 2 * 2.0 ** 2 + (4. / 1) ** 2 + (6. / 1) ** 2 + (8. / 1) ** 2 + 2 * (3. / 3) ** 2) / on
    assert on == 8 and abs(float(aux) - expected) < 1e-6


@pytest.mark.skipif(not (CORPUS / "A_8448043181" / "geometry.json").exists(), reason="corpus benzene not on this machine")
def test_pattern_classes_on_benzene_match_the_loader_and_are_symmetric():
    pytest.importorskip("geometric")
    import json

    import e7_t2_sqm as T2
    d = CORPUS / "A_8448043181"
    g = json.load(open(d / "geometry.json"))
    B, _types = T2.internals(g["symbols"], np.asarray(g["coords_bohr"], float))
    K = B.shape[0]
    m = dict(B=B, F_low=np.eye(K))
    cls = R.pattern_classes(d, m)
    assert cls.shape == (K, K) and torch.equal(cls, cls.T)
    assert (cls.diagonal() >= 0).all() and (cls.diagonal() <= 3).all()               # every primitive's diagonal entry is in the pattern
    off = cls[~torch.eye(K, dtype=torch.bool)]
    assert set(off[off >= 0].tolist()) <= {4, 5} and (off == -1).sum() > 0             # off-diagonal classes 4/5, and entries outside the pattern exist


def test_cli_switches_present_and_recipe_unchanged_by_default():
    text = (M05 / "rungC_train.py").read_text(encoding="utf-8")
    assert re.search(r'add_argument\("--aux", default="all", choices=\["all", "pattern"\]', text)
    assert re.search(r'add_argument\("--zero-hlow", action="store_true"', text)
    assert re.search(r'add_argument\("--overfit-one", default=None', text)
    assert 'aux_mode: str = "all"' in text                                            # default keeps the registered internal term
    assert "pattern_class_scales(tensors, train_ids)" in text                          # scales from the fit molecules of the seed, nothing else
