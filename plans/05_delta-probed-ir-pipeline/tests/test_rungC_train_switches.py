"""Rung C driver, the switches of the fair-chance search registered on 27 September 2026 (`m05/rungC_train.py`): the entry-class mask, the
per-class output scale, the deterministic inner split, and that the defaults still run the registered recipe — on synthetic water only."""
import sys
from pathlib import Path

import numpy as np
import pytest

torch = pytest.importorskip("torch")
M05 = Path(__file__).resolve().parents[1] / "modules" / "05_support_predictor" / "m05"
sys.path.insert(0, str(M05))
import rungC_config as RC_CONFIG  # noqa: E402
import rungC_equivariant as RC  # noqa: E402
import rungC_history as RH  # noqa: E402
import rungC_train as RT  # noqa: E402
from rungC_config import TrainConfig  # noqa: E402

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


def test_the_cosine_schedule_sets_each_epochs_rate(monkeypatch):
    """The optimiser steps at the epoch's rate under 'cosine' and at --lr throughout under 'constant'."""
    tensors = _water_tensors(3)
    seen = []
    step = torch.optim.AdamW.step

    def recording_step(self, *args, **kwargs):
        seen.append(self.param_groups[0]["lr"])
        return step(self, *args, **kwargs)

    monkeypatch.setattr(torch.optim.AdamW, "step", recording_step)
    epochs = RC_CONFIG.LR_WARMUP_EPOCHS + 3
    for schedule in RC_CONFIG.LR_SCHEDULES:
        seen.clear()
        cfg = TrainConfig(molecules="-", out_prefix="-", epochs=epochs, lr=1e-3, lr_schedule=schedule)
        RT.train_one(list(tensors), tensors, 0, cfg, log=lambda s: None)
        per_epoch = seen[::len(tensors)]
        assert len(seen) == epochs * len(tensors)
        assert per_epoch == pytest.approx([RC_CONFIG.learning_rate(1e-3, schedule, ep, epochs) for ep in range(epochs)])
    assert per_epoch[0] < per_epoch[RC_CONFIG.LR_WARMUP_EPOCHS - 1] and per_epoch[-1] == pytest.approx(1e-3 * RC_CONFIG.LR_FLOOR)


def test_defaults_are_the_registered_recipe_and_switches_run():
    tensors = _water_tensors(3)
    ids = list(tensors)
    first = RT.train_one(ids, tensors, 0, TrainConfig(molecules="-", out_prefix="-", epochs=2), log=lambda s: None)
    assert first.model.class_scale is None and first.class_scale is None and first.best_epoch is None
    assert len(first.history) == 2 and not {"val_aux", "val_main"} & set(first.history[0])
    cfg = TrainConfig(molecules="-", out_prefix="-", epochs=3, loss="internal", scale="class", inner_val=0.3, patience=5)
    second = RT.train_one(ids[:2], tensors, 0, cfg, val_ids=ids[2:], log=lambda s: None)
    assert len(second.class_scale) == 3 and isinstance(second.best_epoch, int) and 1 <= second.best_epoch <= 3
    assert all(np.isfinite(h["val_aux"]) and np.isfinite(h["val_main"]) for h in second.history)
    assert all(np.isfinite(RT.inner_val_terms(second.model, tensors, ids[2:], second.loss)))


VAL_CFG = dict(molecules="-", out_prefix="-", epochs=4, inner_val=0.3, patience=2)


def test_the_validation_main_term_is_the_mean_of_the_molecules_own_terms():
    """`val_main` averages as the training `main` does (one value per molecule, then the mean), and the last epoch's entry is the model's
    own read when no better state was restored (patience 0)."""
    tensors = _water_tensors(4)
    ids = list(tensors)
    trained = RT.train_one(ids[:2], tensors, 0, TrainConfig(**{**VAL_CFG, "patience": 0}), val_ids=ids[2:], log=lambda s: None)
    val_main, val_aux = RT.inner_val_terms(trained.model, tensors, ids[2:], trained.loss)
    with torch.no_grad():
        per_molecule = [[float(x) for x in RT._terms(trained.model, tensors[i], trained.loss)[:2]] for i in ids[2:]]
    assert [val_main, val_aux] == [float(np.mean(col)) for col in zip(*per_molecule, strict=True)]
    assert (trained.history[-1]["val_main"], trained.history[-1]["val_aux"]) == (val_main, val_aux)
    assert all(np.isnan(RT.inner_val_terms(trained.model, tensors, [], trained.loss)))


def test_recording_the_validation_main_term_leaves_the_training_unchanged(monkeypatch):
    """Against the validation read as it stood before 17 Nov 2026 (the auxiliary term only): the same weights to the bit, the same best
    epoch and the same numbers in every entry of the history that existed then."""
    tensors = _water_tensors(4)
    ids = list(tensors)
    cfg = TrainConfig(**VAL_CFG)
    new = RT.train_one(ids[:2], tensors, 0, cfg, val_ids=ids[2:], log=lambda s: None)

    def aux_only(model, tensors, ids, loss):
        model.eval()
        with torch.no_grad():
            return float("nan"), float(np.mean([float(RT._terms(model, tensors[i], loss)[1]) for i in ids])) if ids else float("nan")

    monkeypatch.setattr(RT, "inner_val_terms", aux_only)
    old = RT.train_one(ids[:2], tensors, 0, cfg, val_ids=ids[2:], log=lambda s: None)
    new_state, old_state = new.model.state_dict(), old.model.state_dict()
    assert list(new_state) == list(old_state) and all(torch.equal(new_state[k], old_state[k]) for k in new_state)
    assert new.best_epoch == old.best_epoch and len(new.history) == len(old.history)
    assert [{k: h[k] for k in ("epoch", "main", "aux", "val_aux")} for h in new.history] == [
        {k: h[k] for k in ("epoch", "main", "aux", "val_aux")} for h in old.history]


def test_the_epoch_line_still_gives_the_repeat_check_its_validation_term():
    """`probes/epoch_repeat_check.py` reads the auxiliary validation term from the epoch lines of old and new logs."""
    sys.path.insert(0, str(M05.parents[2] / "probes"))
    from epoch_repeat_check import EPOCH_LINE

    tensors = _water_tensors(4)
    ids, lines = list(tensors), []
    trained = RT.train_one(ids[:2], tensors, 0, TrainConfig(**VAL_CFG), val_ids=ids[2:], log=lines.append)
    first = EPOCH_LINE.search(next(line for line in lines if " epoch 1/" in line))
    assert first is not None and float(first.group(4)) == float(f"{trained.history[0]['val_aux']:.4g}")
    assert f" val_main {trained.history[0]['val_main']:.4g} (" in first.string


def test_a_history_reader_names_why_a_series_is_missing():
    now = [dict(epoch=1, main=2.0, aux=1.0, val_main=3.0, val_aux=1.5)]
    before = [dict(epoch=1, main=2.0, aux=1.0, val_aux=1.5)]
    no_validation = [dict(epoch=1, main=2.0, aux=1.0)]
    assert RH.history_series(now, "val_main") == [3.0] and RH.history_series(before, "val_aux") == [1.5]
    assert RH.history_series(no_validation, "main") == [2.0]
    with pytest.raises(ValueError, match="not recorded before 17 Nov 2026"):
        RH.history_series(before, "val_main")
    for key in ("val_main", "val_aux"):
        with pytest.raises(ValueError, match="no inner-validation set"):
            RH.history_series(no_validation, key)
    with pytest.raises(ValueError, match="no series"):
        RH.history_series(now, "validation")
