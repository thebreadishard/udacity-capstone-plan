"""C2 incident of 27 September 2026 (22:0x): the H_low channel during pretraining and the non-finite guard. The bond surrogate must be a
proper Hessian (symmetric, translationally invariant, finite, non-zero on bonded pairs); a run whose loss turns non-finite must abort at once."""
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


def test_bond_surrogate_is_a_hessian():
    w = RC.water()
    H = PT.bond_surrogate_hessian(w["Z"], w["pos"])
    assert H.shape == (9, 9) and np.isfinite(H).all() and np.allclose(H, H.T)
    assert np.allclose(H.reshape(3, 3, 3, 3).sum(axis=2), 0.0, atol=1e-12)        # translational sum rule
    assert np.abs(H[0:3, 3:6]).max() > 0 and np.allclose(H[3:6, 6:9], 0.0)          # O–H bonded, H–H not
    inv_pair, inv_node = RC.pair_invariants(torch.as_tensor(H, dtype=torch.float32), torch.as_tensor(w["pos"], dtype=torch.float32))
    assert torch.isfinite(inv_pair).all() and inv_node.abs().max() > 0.05         # the channel carries a realistic magnitude


def test_record_channel_switch():
    w = RC.water()
    row = {"label": "w", "atomic_numbers": [8, 1, 1], "positions": (w["pos"] * RC.BOHR2ANG).tolist(), "hessian": np.zeros((3, 3, 3, 3)).tolist()}
    assert not PT.record_to_molecule(row, "zero")["H_low"].any()
    assert PT.record_to_molecule(row, "bond")["H_low"].any()


def test_non_finite_loss_aborts():
    w = RC.water()
    t = RC.to_torch(w)
    t["Bp"] = torch.eye(9)
    t["dF_true"] = t["dH_true"].clone()
    t["dF_norm"] = torch.tensor(1.0)
    t["cls"] = RT.entry_classes(w)
    tensors = {"w": t}
    model_ok, _ = RT.train_one(["w"], tensors, seed=0, epochs=1, log=lambda s: None)
    assert model_ok is not None
    tensors["w"]["dH_true"] = t["dH_true"] * float("nan")                        # a NaN target makes the first loss NaN
    with pytest.raises(RuntimeError, match="non-finite loss"):
        RT.train_one(["w"], tensors, seed=0, epochs=1, log=lambda s: None)


def test_pretrained_transfer_preflight():
    """Second incident of 27 Sep (22:4x): a body that explodes on a training molecule must be refused before fine-tuning."""
    w = RC.water()
    t = RC.to_torch(w)
    tensors = {"w": t}
    torch.manual_seed(0)
    body = RC.DeltaHessianModel().eval()
    worst = RT.check_pretrained_transfer(body, tensors, ["w"], limit=1e3)          # a fresh body is finite and small
    assert 0 < worst < 1e3
    with pytest.raises(RuntimeError, match="does not transfer"):
        RT.check_pretrained_transfer(body, tensors, ["w"], limit=worst / 2)        # the same body against a limit below its output
