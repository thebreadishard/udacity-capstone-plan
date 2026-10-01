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
    assert (s >= R.PATTERN_SCALE_FLOOR * s.max() - 1e-7).all()                              # 1 Oct floor: no class far below the largest


def test_pattern_class_scale_floor_lifts_tiny_classes():
    cls = torch.full((2, 2), -1, dtype=torch.long)
    cls[0, 0], cls[1, 1] = 0, 3
    T = {"m": dict(dF_true=torch.tensor([[10., 0.], [0., 1e-4]]), pat_cls=cls)}
    s = R.pattern_class_scales(T, ["m"])
    assert abs(float(s[0]) - 10.0) < 1e-6 and abs(float(s[3]) - 1.0) < 1e-6              # 1e-4 lifted to 0.1 × 10


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
    assert re.search(r'add_argument\("--aux", default="all", choices=\["all", "pattern", "kring"\]', text)   # kring added 1 Oct (lever 3)
    assert re.search(r'add_argument\("--zero-hlow", action="store_true"', text)
    assert re.search(r'add_argument\("--overfit-one", default=None', text)
    assert 'aux_mode: str = "all"' in text                                            # default keeps the registered internal term
    assert re.search(r'add_argument\("--hybrid-hidden", type=int, default=128', text)  # search stage H1 (1 Oct): width of the hybrid head
    assert "pattern_class_scales(tensors, train_ids)" in text                          # scales from the fit molecules of the seed, nothing else


@pytest.mark.skipif(not (CORPUS / "A_8448043181" / "geometry.json").exists(), reason="corpus benzene not on this machine")
def test_pattern_d_extends_c_with_two_bonds_apart_pairs_of_class_6():
    """Lever 1 (1 Oct 2026): pattern d contains every pair of c with the same classes, plus pairs of class 6 whose atom sets are disjoint and joined by
    exactly one bond; the default call is pattern c, unchanged."""
    pytest.importorskip("geometric")
    import json

    import e7_rungB_pairs as RB
    import e7_t2_sqm as T2
    from learning_curve_layerA_v2_descriptors import bond_graph
    d = CORPUS / "A_8448043181"
    g = json.load(open(d / "geometry.json"))
    coords = np.asarray(g["coords_bohr"], float)
    K = T2.internals(g["symbols"], coords)[0].shape[0]
    F = np.eye(K)                                                                    # F_low enters the features only; the identity will do
    pairs_c, _fc, cls_c, _Bc = RB.molecule_pairs(g["symbols"], coords, F)
    pairs_default, _fd, cls_default, _Bd = RB.molecule_pairs(g["symbols"], coords, F, pattern="c")
    pairs_d, _fe, cls_d, _Be, atoms = RB.molecule_pairs(g["symbols"], coords, F, return_atoms=True, pattern="d")
    assert np.array_equal(pairs_c, pairs_default) and np.array_equal(cls_c, cls_default)   # default = c
    set_c = {(int(i), int(j)): int(c) for (i, j), c in zip(pairs_c, cls_c, strict=True)}
    set_d = {(int(i), int(j)): int(c) for (i, j), c in zip(pairs_d, cls_d, strict=True)}
    assert set(set_c) <= set(set_d) and all(set_d[k] == v for k, v in set_c.items())       # d ⊇ c with the same classes
    extra = {k: v for k, v in set_d.items() if k not in set_c}
    assert extra and set(extra.values()) == {6}
    adj = bond_graph([s.capitalize() for s in g["symbols"]], coords)
    for (i, j) in extra:
        assert not (atoms[i] & atoms[j])                                                    # disjoint atom sets
        assert any(b in adj[a] for a in atoms[i] for b in atoms[j])                         # joined by one bond
    with pytest.raises(ValueError):
        RB.molecule_pairs(g["symbols"], coords, F, pattern="e")


def test_per_molecule_readouts_keep_the_registered_keys_and_nan_as_none(monkeypatch):
    """H7 (1 Oct 2026): one read-out call per hold-out molecule; NaN (no two ring modes) becomes None so the record stays JSON."""
    import rungC_train as RT
    calls = []

    def fake_readouts(mols, ids, tr, dF_of):
        calls.append(tuple(ids))
        return {"coupling_ratio": float("nan") if ids == ["m2"] else 0.4, "coupling_rms": 1.0, "coupling_zero_rms": 2.5, "corrected_freq_rms": 4.0,
                "dH_residual_ratio": 0.2, "block_rms": 9.0}
    monkeypatch.setattr(RT, "readouts", fake_readouts)
    out = RT.per_molecule_readouts({}, ["m1", "m2"], ["m1"], lambda i: None)
    assert calls == [("m1",), ("m2",)]
    assert set(out["m1"]) == set(RT.PER_MOLECULE_KEYS) and "block_rms" not in out["m1"]
    assert out["m1"]["coupling_ratio"] == 0.4 and out["m2"]["coupling_ratio"] is None


@pytest.mark.skipif(not (CORPUS / "A_8448043181" / "geometry.json").exists(), reason="corpus benzene not on this machine")
def test_kring_tensors_reproduce_k_of_and_vanish_on_the_truth():
    """Lever 3 / H8 (1 Oct 2026): the torch read-out map equals e7_t2_posthoc.k_of on the same ΔH (up to the B reconstruction), and the kring term is
    zero when the prediction is the truth."""
    pytest.importorskip("geometric")
    import json

    import e7_t2_posthoc as PH
    import e7_t2_sqm as T2
    import rungC_train as RT
    d = CORPUS / "A_8448043181"
    g = json.load(open(d / "geometry.json"))
    masses, coords = np.asarray(g["masses_amu"]), np.asarray(g["coords_bohr"], float)
    lo = np.load(d / "hessian_b3lyp.npz")["H_projected"]
    hi = np.load(d / "hessian_wb97x.npz")["H_projected"]
    w, _f, V, _ = T2.normal_modes(lo, masses)
    B, _types = T2.internals(g["symbols"], coords)
    dH = hi - lo
    fam = [RT.E6.RING] * V.shape[1]                                                     # every mode 'ring': the block is the whole matrix
    t = RT.kring_tensors(masses, V, w, fam, dH, dtype=torch.float64)
    K_t = ((t["Cm"] @ torch.as_tensor(dH) @ t["Cm"].T) * t["kscale"]).numpy()
    Bp = np.linalg.pinv(B)
    K_ref = PH.k_of(dict(masses=masses, w=w, V=V, B=B), Bp.T @ dH @ Bp)
    assert np.abs(K_t - K_ref).max() < 2e-3 * np.abs(K_ref).max()
    assert torch.allclose(t["K_true"], torch.as_tensor(K_t))

    class Truth(torch.nn.Module):
        aux_mode = "kring"

        def forward(self, Z, pos, H_low, t):
            return t["dH_true"]
    t.update(dH_true=torch.as_tensor(dH), mw=torch.ones_like(torch.as_tensor(dH)), Bp=torch.as_tensor(Bp), dF_true=torch.as_tensor(Bp.T @ dH @ Bp),
             dF_norm=torch.tensor(1.0, dtype=torch.float64), Z=None, pos=None, H_low=None)
    main, aux, _pred = RT._terms(Truth(), t)
    assert float(main) == 0.0 and float(aux) < 1e-20
    text = (M05 / "rungC_train.py").read_text(encoding="utf-8")
    assert re.search(r'add_argument\("--aux", default="all", choices=\["all", "pattern", "kring"\]', text)
