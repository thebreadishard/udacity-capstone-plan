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


@pytest.fixture(scope="module")
def model():
    torch.manual_seed(0)
    return RC.DeltaHessianModel().double()


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
