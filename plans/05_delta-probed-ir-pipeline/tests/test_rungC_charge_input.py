"""P3-1 (decision 54, 3 Oct 2026): the charge-state input of the rung-C body. Zero-initialised, so a neutral prediction is unchanged to the bit;
a trained row changes the output and keeps the equivariance; a checkpoint without the embedding loads through load_state_compat with the rows
left at zero (any other mismatch refused); charge_index reads geometry.json's charge/multiplicity and refuses unknown states; design_check's
charge_rows refuses unlabelled cation rows."""
import sys
from pathlib import Path

import numpy as np
import pytest

torch = pytest.importorskip("torch")
M05 = Path(__file__).resolve().parents[1] / "modules" / "05_support_predictor" / "m05"
sys.path.insert(0, str(M05))
import design_check as DC  # noqa: E402
import rungC_equivariant as RC  # noqa: E402

torch.set_num_threads(1)


def _molecule(seed=0):
    rng = np.random.default_rng(seed)
    Z = torch.tensor([8, 1, 1, 6, 1])
    pos = torch.tensor([[0.0, 0.0, 0.0], [0.0, -1.43, 1.11], [0.0, 1.43, 1.11], [2.6, 0.0, 0.0], [2.6, 0.0, 2.0]], dtype=torch.float64)
    A = rng.normal(size=(15, 15))
    H = torch.tensor(A + A.T) * 0.05
    return Z, pos, H


def _body(seed=0):
    torch.manual_seed(seed)
    return RC.DeltaHessianModel(aggregation="mean").double()


def test_zero_rows_keep_the_neutral_output_bit_identical():
    Z, pos, H = _molecule()
    body = _body()
    assert torch.count_nonzero(body.q_emb.weight) == 0
    out_none = body(Z, pos, H)
    out_zero = body(Z, pos, H, qidx=torch.tensor(0))
    out_cat = body(Z, pos, H, qidx=torch.tensor(1))
    assert torch.equal(out_none, out_zero)
    assert torch.equal(out_none, out_cat)                         # the cation row is zero too until it is trained


def test_a_trained_row_changes_the_output_and_stays_equivariant():
    Z, pos, H = _molecule()
    body = _body()
    with torch.no_grad():
        body.q_emb.weight[1] = 0.3
    out0 = body(Z, pos, H, qidx=torch.tensor(0))
    out1 = body(Z, pos, H, qidx=torch.tensor(1))
    assert not torch.allclose(out0, out1)
    R = torch.tensor([[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], dtype=torch.float64)     # a proper rotation (cyclic axes)
    H_rot = torch.as_tensor(RC.transform_hessian(H.numpy(), R.numpy()))
    out1_rot = body(Z, pos @ R.T, H_rot, qidx=torch.tensor(1))
    assert torch.allclose(out1_rot, torch.as_tensor(RC.transform_hessian(out1.detach().numpy(), R.numpy())), atol=1e-10)


def test_compat_loader_accepts_only_the_missing_charge_rows():
    Z, pos, H = _molecule()
    body = _body(1)
    state = {k: v.clone() for k, v in body.state_dict().items() if k != "q_emb.weight"}      # a checkpoint from before 3 Oct 2026
    fresh = _body(2)
    left = RC.load_state_compat(fresh, state)
    assert left == ["q_emb.weight"]
    assert torch.equal(fresh(Z, pos, H), body(Z, pos, H))
    bad = dict(state, stray=torch.zeros(1))
    with pytest.raises(RuntimeError):
        RC.load_state_compat(_body(3), bad)
    short = {k: v for k, v in state.items() if k != "node_in.bias"}
    with pytest.raises(RuntimeError):
        RC.load_state_compat(_body(4), short)


def test_charge_index_reads_geometry_fields():
    assert RC.charge_index({}) == 0
    assert RC.charge_index({"charge": 1, "multiplicity": 2}) == 1
    assert RC.charge_index({"charge": -1, "multiplicity": 2}) == 2
    with pytest.raises(ValueError):
        RC.charge_index({"charge": 2, "multiplicity": 1})


def test_design_check_refuses_unlabelled_cation_rows():
    body = _body()
    mols = {"C_abc": {"charge": 1, "qidx": 0}, "A_xyz": {"qidx": 0}}
    assert DC.charge_rows(mols, body)["pass"] is False
    mols["C_abc"]["qidx"] = 1
    assert DC.charge_rows(mols, body)["pass"] is True
    assert DC.charge_rows({"A_xyz": {"qidx": 0}}, torch.nn.Linear(1, 1))["pass"] is True          # no cations: an old body is fine
    assert DC.charge_rows(mols, torch.nn.Linear(1, 1))["pass"] is False                            # cations but no charge input
