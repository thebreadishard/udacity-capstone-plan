"""Input wiring of rung C (1 Oct 2026, the user: is 'the encoder ignores H_low / the rank-2 input' a finding or a bug?). An ablation cannot tell
"learned to ignore" from "never wired in"; a sensitivity test at initialisation can: a wired-in input changes the output and carries gradient
before any training. Three paths are checked: the encoder's H_low scalars, the rank-2 tensor messages, and the hybrid head's F_low inputs."""
import sys
from pathlib import Path

import pytest

torch = pytest.importorskip("torch")
M05 = Path(__file__).resolve().parents[1] / "modules" / "05_support_predictor" / "m05"
sys.path.insert(0, str(M05))
import rungC_equivariant as RC  # noqa: E402
import rungC_hybrid as RH  # noqa: E402

from test_rungC_hybrid import _hybrid_tensors  # noqa: E402

torch.set_num_threads(1)


def _rel(a, b):
    return float((a - b).abs().max() / a.abs().max())


def test_encoder_output_and_gradient_depend_on_h_low():
    torch.manual_seed(0)
    t = RC.to_torch(RC.water(), torch.float64)
    model = RC.DeltaHessianModel(aggregation="mean").double()
    H = t["H_low"].clone().requires_grad_(True)
    out = model(t["Z"], t["pos"], H)
    out_zero = model(t["Z"], t["pos"], torch.zeros_like(H))
    assert _rel(out, out_zero) > 1e-3                                              # the H_low scalars reach the output
    (g,) = torch.autograd.grad(out.pow(2).sum(), H)
    assert float(g.abs().max()) > 0                                                # and carry gradient at initialisation


def test_rank2_tensor_messages_are_live():
    """The tensor-input model's extra message channels (S·v_j, S·r̂) receive gradient, i.e. the rank-2 path contributes to the output."""
    torch.manual_seed(0)
    t = RC.to_torch(RC.water(), torch.float64)
    model = RC.DeltaHessianModel(aggregation="mean", tensor_input=True).double()
    out = model(t["Z"], t["pos"], t["H_low"])
    out.pow(2).sum().backward()
    blk = model.blocks[0]
    lo = blk.n_s + 2 * blk.n_v                                                     # rows of W feeding dvt and dvr
    g = blk.W.weight.grad[lo:lo + 2 * blk.n_v]
    assert g is not None and float(g.abs().max()) > 0
    plain = RC.DeltaHessianModel(aggregation="mean").double()
    assert plain.blocks[0].W.weight.shape[0] == lo                                 # without the option those rows do not exist


def test_hybrid_head_depends_on_f_low_and_on_the_encoder_h_low():
    torch.manual_seed(0)
    t = _hybrid_tensors(RC.water())
    model = RH.HybridDeltaFModel(aggregation="mean").double()
    out = model(t["Z"], t["pos"], t["H_low"], t)
    t2 = dict(t, F_int=2.0 * t["F_int"])
    assert _rel(out, model(t2["Z"], t2["pos"], t2["H_low"], t2)) > 1e-3            # the head's own F_low inputs
    assert _rel(out, model(t["Z"], t["pos"], torch.zeros_like(t["H_low"]), t)) > 1e-3   # the encoder's H_low, through the pooled features
