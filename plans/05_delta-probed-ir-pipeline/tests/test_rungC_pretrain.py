"""Rung C, variant C2 (`m05/rungC_pretrain.py`, 27 September 2026): unit conversion of a Hessian QM9 record, the per-class scales, and the checkpoint
round trip with the head re-initialised — on fabricated records only; the QM9 shards are not touched."""
import sys
from pathlib import Path

import numpy as np
import pytest

torch = pytest.importorskip("torch")
M05 = Path(__file__).resolve().parents[1] / "modules" / "05_support_predictor" / "m05"
sys.path.insert(0, str(M05))
import rungC_equivariant as RC  # noqa: E402
import rungC_pretrain as PT  # noqa: E402
import rungC_train as RT  # noqa: E402

torch.set_num_threads(1)


def _fake_row(seed: int = 0) -> dict:
    """A water-like record in QM9's units: positions in Å, a symmetric Hessian in eV/Å²."""
    rng = np.random.default_rng(seed)
    pos_bohr = RC.water()["pos"]
    A = rng.normal(size=(9, 9))
    return {"label": f"fake_{seed}", "atomic_numbers": [8, 1, 1], "positions": (pos_bohr * RC.BOHR2ANG).tolist(),
            "hessian": (A + A.T).reshape(3, 3, 3, 3).tolist()}


def test_record_to_molecule_converts_units():
    row = _fake_row()
    m = PT.record_to_molecule(row, hlow_channel="zero")                             # the unit check on the zero channel; the bond channel has its own test
    assert np.allclose(m["pos"], RC.water()["pos"])                                 # Å → bohr round trip
    H_ev = np.asarray(row["hessian"]).reshape(9, 9)
    assert np.allclose(m["dH_true"], H_ev * RC.BOHR2ANG**2 / PT.HARTREE_EV)          # eV/Å² → hartree/bohr²
    assert np.allclose(m["dH_true"], m["dH_true"].T) and not m["H_low"].any()
    assert list(m["masses"].round(2)) == [15.99, 1.01, 1.01]


def test_class_scales_are_rms_per_class():
    t = PT.molecule_to_tensors(PT.record_to_molecule(_fake_row()))
    s = PT.class_scales([t])
    c = t["cls"].repeat_interleave(3, 0).repeat_interleave(3, 1).numpy()
    d2 = (t["dH_true"] ** 2).numpy()
    for k in range(3):
        assert s[k] == pytest.approx(float(np.sqrt(d2[c == k].mean())), rel=1e-6)


def test_checkpoint_round_trip_reinitialises_only_the_head(tmp_path):
    torch.manual_seed(0)
    model = RT.Scaled(RC.DeltaHessianModel(), 1.0, [1.0, 2.0, 3.0])
    path = tmp_path / "ck.pt"
    PT.save_checkpoint(path, model, {"note": "test"})
    body = RT.load_pretrained_body(path, reinit_head=True, seed=1)
    ref = model.model.state_dict()
    for name, p in body.state_dict().items():
        same = torch.equal(p, ref[name])
        assert same != name.startswith("head."), name                                 # body identical, head re-drawn
    kept = RT.load_pretrained_body(path, reinit_head=False)
    assert all(torch.equal(p, ref[n]) for n, p in kept.state_dict().items())
