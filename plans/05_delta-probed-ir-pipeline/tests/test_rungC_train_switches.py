"""Rung C driver, the switches of the fair-chance search registered on 27 September 2026 (`m05/rungC_train.py`): the entry-class mask, the
per-class output scale, the deterministic inner split, and that the defaults still run the registered recipe — on synthetic water only."""
import sys
from pathlib import Path

import numpy as np
import pytest

torch = pytest.importorskip("torch")
M05 = Path(__file__).resolve().parents[1] / "modules" / "05_support_predictor" / "m05"
sys.path.insert(0, str(M05))
import rungC_equivariant as RC  # noqa: E402
import rungC_train as RT  # noqa: E402

torch.set_num_threads(1)


def _water_tensors(n_copies: int = 3) -> dict:
    """n synthetic water molecules as the driver builds them (Cartesian tensors, B⁺ from a made-up but full-rank B, entry classes)."""
    out = {}
    for k in range(n_copies):
        m = RC.water()
        m["pos"] = m["pos"] + 0.01 * k                       # translated copies: different ids, identical physics
        t = RC.to_torch(m)
        rng = np.random.default_rng(k)
        B = rng.normal(size=(3, 9))                          # 3 internal coordinates for 9 Cartesians
        t["Bp"] = torch.as_tensor(np.linalg.pinv(B), dtype=torch.float32)
        t["dF_true"] = t["Bp"].T @ t["dH_true"] @ t["Bp"]
        t["dF_norm"] = (t["dF_true"] ** 2).mean().clamp_min(1e-30)
        t["cls"] = RT.entry_classes(m)
        out[f"w{k}"] = t
    return out


def test_entry_classes_on_water():
    cls = RT.entry_classes(RC.water()).numpy()
    assert cls.shape == (3, 3)
    assert (np.diag(cls) == 0).all()                         # own block
    assert cls[0, 1] == 1 and cls[0, 2] == 1                 # O–H bonded
    assert cls[1, 2] == 2                                    # H–H not bonded
    assert (cls == cls.T).all()


def test_class_scale_applies_per_block():
    t = _water_tensors(1)["w0"]
    torch.manual_seed(0)
    base = RC.DeltaHessianModel()
    plain = RT.Scaled(base, 2.0)
    per_class = RT.Scaled(base, 2.0, class_scale=[1.0, 10.0, 100.0])
    with torch.no_grad():
        p = plain(t["Z"], t["pos"], t["H_low"], t).numpy()
        c = per_class(t["Z"], t["pos"], t["H_low"], t).numpy()
    scale = np.array([1.0, 10.0, 100.0])[t["cls"].numpy()].repeat(3, 0).repeat(3, 1)   # the class scale replaces the scalar scale
    assert np.allclose(c, (p / 2.0) * scale, rtol=1e-5, atol=1e-7)
    assert scale[0, 0] == 1.0 and scale[0, 3] == 10.0 and scale[3, 6] == 100.0                # own block, O–H, H–H


def test_inner_split_is_deterministic_and_disjoint():
    ids = [f"m{i}" for i in range(20)]
    v1, f1 = RT.inner_split(ids, seed=0, fraction=0.15)
    v2, f2 = RT.inner_split(ids, seed=0, fraction=0.15)
    v3, _ = RT.inner_split(ids, seed=1, fraction=0.15)
    assert (v1, f1) == (v2, f2) and len(v1) == 3 and not set(v1) & set(f1) and sorted(v1 + f1) == sorted(ids)
    assert v3 != v1
    assert RT.inner_split(ids, seed=0, fraction=0.0) == ([], ids)


def test_defaults_are_the_registered_recipe_and_switches_run():
    tensors = _water_tensors(3)
    ids = list(tensors)
    model, hist = RT.train_one(ids, tensors, seed=0, epochs=2, log=lambda s: None)
    assert model.class_scale is None and model.best_epoch is None and len(hist) == 2 and "val_aux" not in hist[0]
    model2, hist2 = RT.train_one(ids[:2], tensors, seed=0, epochs=3, log=lambda s: None, loss_mode="internal", scale_mode="class",
                                 val_ids=ids[2:], patience=5)
    assert len(model2.class_scale_values) == 3 and isinstance(model2.best_epoch, int) and 1 <= model2.best_epoch <= 3
    assert all("val_aux" in h for h in hist2) and np.isfinite(RT.inner_val_aux(model2, tensors, ids[2:]))
