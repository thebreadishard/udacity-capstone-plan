"""Rung C (weekend plan lever 4, 25/26 September 2026): the equivariant Δ-Hessian model must rotate, reflect and permute with its input to 1e-6,
obey the translational sum rule, and its loss must be trainable — checked on synthetic water only; nothing here touches the 175-molecule pool."""
import sys
from pathlib import Path

import numpy as np
import pytest

torch = pytest.importorskip("torch")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "modules" / "05_support_predictor" / "m05"))
import rungC_equivariant as RC  # noqa: E402

torch.set_num_threads(1)


@pytest.fixture(scope="module", params=[(agg, ti) for agg in RC.AGGREGATIONS for ti in (False, True)],
                ids=lambda p: f"{p[0]}-{'tensor' if p[1] else 'scalars'}")
def model(request):
    torch.manual_seed(0)
    agg, tensor_input = request.param
    return RC.DeltaHessianModel(aggregation=agg, tensor_input=tensor_input).double()


def test_equivariance_on_water(model):
    err = RC.equivariance_errors(model, RC.water(), seed=1)
    for k in ("rotation", "reflection", "permutation", "translation_sum_rule", "symmetry"):
        assert err[k] < 1e-6, (k, err[k])


def test_check_detects_a_broken_model(model):
    """Negative control: a model that adds a term built from absolute coordinates is not equivariant, and the check must say so."""

    class Broken(torch.nn.Module):
        def forward(self, Z, pos, H):
            n = pos.shape[0]
            bad = torch.einsum("ia,jb->iajb", pos, pos).reshape(3 * n, 3 * n) * 1e-3
            return model(Z, pos, H) + bad + bad.T

    err = RC.equivariance_errors(Broken(), RC.water(), seed=1)
    assert err["rotation"] > 1e-3 and err["translation_sum_rule"] > 1e-3


def test_pair_invariants_are_invariant():
    m = RC.water()
    R = RC.rotation(3)
    inv0, node0 = RC.pair_invariants(torch.tensor(m["H_low"]), torch.tensor(m["pos"]))
    inv1, node1 = RC.pair_invariants(torch.tensor(RC.transform_hessian(m["H_low"], R)), torch.tensor(m["pos"] @ R.T))
    assert torch.allclose(inv0, inv1, atol=1e-12) and torch.allclose(node0, node1, atol=1e-12)


def test_registered_input_is_only_the_three_pair_scalars(model):
    """Two low-level Hessians whose registered invariants (trace, r̂ᵀBr̂, ‖B‖_F per block; trace and norm per diagonal block) agree must give the
    same prediction: the H–H block is set to ε(e₁e₁ᵀ − e₂e₂ᵀ) with e₁, e₂ ⊥ r̂ in one and to its 90° rotation about r̂, −ε(e₁e₁ᵀ − e₂e₂ᵀ), in the other."""
    m = RC.water()
    r = m["pos"][2] - m["pos"][1]
    r = r / np.linalg.norm(r)
    e1 = np.cross(r, [1.0, 0.0, 0.0])
    e1 = e1 / np.linalg.norm(e1)
    e2 = np.cross(r, e1)
    P = 0.05 * (np.outer(e1, e1) - np.outer(e2, e2))
    variants = []
    for sign in (1.0, -1.0):
        H = m["H_low"].copy()
        H[3:6, 6:9] = sign * P
        H[6:9, 3:6] = sign * P.T
        variants.append(H)
    assert not np.allclose(variants[0], variants[1])
    inv0, _ = RC.pair_invariants(torch.tensor(variants[0]), torch.tensor(m["pos"]))
    inv1, _ = RC.pair_invariants(torch.tensor(variants[1]), torch.tensor(m["pos"]))
    assert torch.allclose(inv0, inv1, atol=1e-12)
    preds = []
    for H in variants:
        t = RC.to_torch(dict(m, H_low=H), torch.float64)
        with torch.no_grad():
            preds.append(model(t["Z"], t["pos"], t["H_low"]))
    if model.tensor_input:
        # rank 1 (30 Sep 2026): the rank-2 input carries the block's orientation, so the two variants must NOT give the same prediction
        assert not torch.allclose(preds[0], preds[1], atol=1e-8)
    else:
        assert torch.allclose(preds[0], preds[1], atol=1e-10)


def test_loss_is_trainable_on_water():
    """Gradient path: a few Adam steps on synthetic water lower the registered loss (main + 0.1 × aux). Not a training run."""
    torch.manual_seed(0)
    mdl = RC.DeltaHessianModel().double()
    t = RC.to_torch(RC.water(), torch.float64)
    B = torch.tensor(np.random.default_rng(0).normal(size=(3, 9)))          # any (n_ic, 3N) B matrix exercises the auxiliary term
    Bp = torch.linalg.pinv(B)
    opt = torch.optim.Adam(mdl.parameters(), lr=1e-3)
    losses = []
    for _ in range(15):
        opt.zero_grad()
        main, aux, _ = RC.loss_terms(mdl, t, Bp)
        loss = main + RC.AUX_WEIGHT * aux
        loss.backward()
        opt.step()
        losses.append(loss.item())
    assert losses[-1] < losses[0]
    assert all(np.isfinite(losses))


def test_pair_tensor_transforms_as_a_rank_two_tensor():
    """pair_tensor (rank-1 input, 30 Sep 2026): under x → R x every block goes to R S Rᵀ, the normalisation is invariant, and permutations permute."""
    m = RC.water()
    R = RC.rotation(5, reflect=True)
    S0 = RC.pair_tensor(torch.tensor(m["H_low"]), torch.tensor(m["pos"]))
    S1 = RC.pair_tensor(torch.tensor(RC.transform_hessian(m["H_low"], R)), torch.tensor(m["pos"] @ R.T))
    Rt = torch.tensor(R)
    assert torch.allclose(S1, torch.einsum("ab,ijbc,dc->ijad", Rt, S0, Rt), atol=1e-12)
    assert torch.allclose(S0, S0.transpose(-1, -2), atol=1e-14)                                    # symmetrised
    off = ~torch.eye(3, dtype=torch.bool)
    assert abs(float(torch.sqrt((S0[off] ** 2).sum((-1, -2)).mean())) - 1.0) < 1e-10             # unit RMS over the off-diagonal blocks
    perm = np.array([2, 0, 1])
    Sp = RC.pair_tensor(torch.tensor(RC.transform_hessian(m["H_low"], np.eye(3), perm)), torch.tensor(m["pos"][perm]))
    assert torch.allclose(Sp, S0[perm][:, perm], atol=1e-14)


def test_registered_model_is_unchanged_by_the_tensor_input_flag():
    """Default tensor_input=False builds the registered architecture: the parameter count of 30 Sep (171,554) plus the zero-initialised charge-state
    embedding of 3 Oct 2026 (4 × 64 = 256; test_rungC_charge_input shows the output unchanged to the bit) plus the hinge-class embedding of 7 Oct
    2026 (6 × 64 = 384, zero and frozen unless --hinge-feature; test_hinge_feature shows the output unchanged)."""
    assert sum(p.numel() for p in RC.DeltaHessianModel().parameters()) == 171_554 + 256 + 384
    assert RC.DeltaHessianModel().h_emb.weight.numel() == 384
    assert sum(p.numel() for p in RC.DeltaHessianModel(tensor_input=True).parameters()) > 171_554 + 256 + 384
