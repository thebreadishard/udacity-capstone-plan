"""Rung C hybrid head (30 Sep 2026, rank 3 of the external reviews): ΔH = Bᵀ ΔF B is symmetric, translation- and rotation-annihilated, and rotates
with the frame when B is rebuilt for the rotated geometry; the pooling matrix averages the right atoms; the SQM α term adds α_c F_low,pq; input
scales come from the given ids. Water through geomeTRIC (skipped where it is missing)."""
import sys
from pathlib import Path

import numpy as np
import pytest

torch = pytest.importorskip("torch")
M05 = Path(__file__).resolve().parents[1] / "modules" / "05_support_predictor" / "m05"
sys.path.insert(0, str(M05))
import rungC_equivariant as RC  # noqa: E402
import rungC_hybrid as RH  # noqa: E402

torch.set_num_threads(1)


def _hybrid_tensors(m, R=None):
    """Water tensors with the pattern from e7_rungB_pairs on the (optionally rotated) geometry; F_int = a fixed synthetic internal force-constant matrix."""
    geometric = pytest.importorskip("geometric")  # noqa: F841
    import e7_rungB_pairs as RB
    pos = m["pos"] if R is None else m["pos"] @ R.T
    H = m["H_low"] if R is None else RC.transform_hessian(m["H_low"], R)
    symbols = m["symbols"]
    pairs, feat, pcls, B, atoms = RB.molecule_pairs(symbols, pos, np.eye(3), return_atoms=True)
    K = B.shape[0]
    F_int = np.diag(np.linspace(0.3, 0.9, K)) + 0.02
    t = RC.to_torch(dict(m, pos=pos, H_low=H), torch.float64)
    t.update(pairs=torch.as_tensor(pairs, dtype=torch.long), pcls=torch.as_tensor(pcls, dtype=torch.long), pfeat=torch.as_tensor(feat, dtype=torch.float64),
             prim_pool=RH.primitive_pool_matrix(atoms, len(symbols), torch.float64), F_int=torch.as_tensor(F_int), B=torch.as_tensor(B))
    return t


@pytest.mark.parametrize("tensor_input", [False, True])
def test_hybrid_output_is_symmetric_rigid_body_free_and_equivariant(tensor_input):
    m = RC.water()
    torch.manual_seed(0)
    model = RH.HybridDeltaFModel(aggregation="mean", tensor_input=tensor_input, class_scale=torch.tensor([1e-2] * RH.N_PAIR_CLASSES)).double()
    t0 = _hybrid_tensors(m)
    with torch.no_grad():
        dH = model(t0["Z"], t0["pos"], t0["H_low"], t0).numpy()
    n = len(m["Z"])
    scale = np.abs(dH).max() + 1e-30
    assert np.abs(dH - dH.T).max() / scale < 1e-12
    assert np.abs(dH.reshape(n, 3, n, 3).sum(2)).max() / scale < 1e-10                 # translations
    x = m["pos"] - m["pos"].mean(0)
    for k in range(3):                                                                  # infinitesimal rotations about the three axes
        e = np.zeros(3)
        e[k] = 1.0
        rot = np.cross(np.tile(e, (n, 1)), x).reshape(-1)
        assert np.abs(dH @ rot).max() / scale < 1e-8
    R = RC.rotation(3, reflect=True)
    t1 = _hybrid_tensors(m, R)
    with torch.no_grad():
        dH1 = model(t1["Z"], t1["pos"], t1["H_low"], t1).numpy()
    assert np.abs(dH1 - RC.transform_hessian(dH, R)).max() / scale < 1e-6


def test_pool_matrix_and_input_scales():
    M = RH.primitive_pool_matrix([{0, 1}, {2}, {0, 1, 2}], 3)
    assert torch.allclose(M.sum(1), torch.ones(3)) and M[0, 0] == 0.5 and M[1, 2] == 1.0 and abs(float(M[2, 0]) - 1 / 3) < 1e-6   # float32 third
    t = dict(F_int=torch.tensor([[2., 1.], [1., 4.]]), pairs=torch.tensor([[0, 0], [0, 1], [1, 1]]))
    x = RH.hybrid_inputs(t)
    assert torch.equal(x, torch.tensor([[2., 2., 2.], [1., 2., 4.], [4., 4., 4.]]))
    s = RH.input_scales({"a": t}, ["a"])
    assert torch.allclose(s, torch.sqrt(torch.tensor([(4. + 1. + 16.) / 3, (4. + 4. + 16.) / 3, (4. + 16. + 16.) / 3])))


def test_sqm_alpha_adds_a_per_class_scale_of_f_low():
    m = RC.water()
    t = _hybrid_tensors(m)
    torch.manual_seed(1)
    base = RH.HybridDeltaFModel(aggregation="mean", sqm_scale=False).double()
    sqm = RH.HybridDeltaFModel(aggregation="mean", sqm_scale=True).double()
    sqm.load_state_dict(base.state_dict(), strict=False)
    with torch.no_grad():
        r0 = base.delta_f(t["Z"], t["pos"], t["H_low"], t)
        sqm.alpha.fill_(0.0)
        r1 = sqm.delta_f(t["Z"], t["pos"], t["H_low"], t)
        sqm.alpha.fill_(0.5)
        r2 = sqm.delta_f(t["Z"], t["pos"], t["H_low"], t)
    p, q = t["pairs"][:, 0], t["pairs"][:, 1]
    assert torch.allclose(r0, r1)
    assert torch.allclose(r2 - r1, 0.5 * t["F_int"][p, q])


def test_pair_features_path_is_invariant_and_off_by_default():
    """With rung B's pair vector in the head the output stays equivariant (the features are invariants of the geometry), the stats come from the given
    ids, and n_pair_features=0 keeps the 00:4x model (no pfeat tensor needed)."""
    m = RC.water()
    t0 = _hybrid_tensors(m)
    mu, sd = RH.pair_feature_stats({"w": t0}, ["w"])
    assert mu.shape == (t0["pfeat"].shape[1],) and (sd > 0).all()
    torch.manual_seed(2)
    model = RH.HybridDeltaFModel(aggregation="mean", n_pair_features=int(t0["pfeat"].shape[1])).double()
    model.set_pair_feature_stats(mu, sd)
    with torch.no_grad():
        dH = model(t0["Z"], t0["pos"], t0["H_low"], t0).numpy()
        R = RC.rotation(7)
        t1 = _hybrid_tensors(m, R)
        dH1 = model(t1["Z"], t1["pos"], t1["H_low"], t1).numpy()
    assert np.abs(dH1 - RC.transform_hessian(dH, R)).max() / (np.abs(dH).max() + 1e-30) < 1e-6
    plain = RH.HybridDeltaFModel(aggregation="mean").double()
    assert plain.pfeat_in is None
    t_no = {k: v for k, v in t0.items() if k != "pfeat"}
    with torch.no_grad():
        plain(t_no["Z"], t_no["pos"], t_no["H_low"], t_no)                          # runs without a pfeat tensor


def test_hybrid_hidden_width_changes_the_head_only():
    small = RH.HybridDeltaFModel(aggregation="mean", hidden=128)
    wide = RH.HybridDeltaFModel(aggregation="mean", hidden=256)
    n_body = sum(p.numel() for p in small.body.parameters())
    assert sum(p.numel() for p in wide.body.parameters()) == n_body
    assert sum(p.numel() for p in wide.parameters()) > sum(p.numel() for p in small.parameters())


def test_hybrid_class_count_matches_the_trainer():
    import rungC_train as RT
    assert RH.N_PAIR_CLASSES == len(RT.PAIR_CLASS_NAMES) == 9 and RT.PAIR_CLASS_NAMES[6:] == ("off_twobond", "off_dist2", "off_dist3")


def test_body_size_switches_change_the_body_and_the_head_input():
    """Lever 2c (1 Oct 2026): blocks and width reach the body; the head's first layer follows the width; defaults keep the 171,554-parameter body."""
    default = RH.HybridDeltaFModel(aggregation="mean")
    deeper = RH.HybridDeltaFModel(aggregation="mean", n_blocks=5)
    wider = RH.HybridDeltaFModel(aggregation="mean", n_s=128, n_v=128)
    assert len(default.body.blocks) == 3 and len(deeper.body.blocks) == 5
    assert sum(p.numel() for p in default.body.parameters()) == 171_554 + 256 + 384    # + charge-state (3 Oct) and hinge (7 Oct) embeddings, zero rows
    assert sum(p.numel() for p in deeper.body.parameters()) > sum(p.numel() for p in default.body.parameters())
    assert wider.head[0].in_features > default.head[0].in_features and wider.body.blocks[0].n_s == 128
