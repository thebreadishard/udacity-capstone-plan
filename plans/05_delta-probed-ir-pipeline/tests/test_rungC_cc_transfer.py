"""Lever 1 / T3 (2 Oct 2026): the trainer's save/load round trip rebuilds the hybrid model exactly; the transfer freeze leaves only the head's last layer and
α trainable; the CC substitution builds K from the CC Hessian with the loader's formula; the α-scaling baseline is the per-class least squares."""
import sys
from pathlib import Path

import numpy as np
import pytest

torch = pytest.importorskip("torch")
PLAN = Path(__file__).resolve().parents[1]
M05 = PLAN / "modules" / "05_support_predictor" / "m05"
sys.path.insert(0, str(M05))
import rungC_hybrid as RH  # noqa: E402
import rungC_train as RT  # noqa: E402

torch.set_num_threads(1)


def test_save_and_load_round_trip(tmp_path):
    torch.manual_seed(0)
    m = RH.HybridDeltaFModel(aggregation="sum", sqm_scale=True, n_pair_features=66, hidden=256)
    m.aux_mode, m.kring_weight, m.kdiag_weight = "both", 0.3, 0.1
    m.aux_class_scale = torch.rand(RH.N_PAIR_CLASSES)
    args = dict(aggregation="sum", tensor_input=False, sqm_scale=True, pattern="f", aux_target="projected", ls_lam=1e-3, head="hybrid")
    p = tmp_path / "m.pt"
    RT.save_hybrid_model(m, p, args, n=750, seed=0)
    m2, ck = RT.load_hybrid_model(p)
    for k, v in m.state_dict().items():
        assert torch.equal(m2.state_dict()[k], v)
    assert (m2.aux_mode, m2.kring_weight, m2.kdiag_weight) == ("both", 0.3, 0.1) and torch.equal(m2.aux_class_scale, m.aux_class_scale)
    assert ck["pattern"] == "f" and ck["n"] == 750 and m2.head[0].out_features == 256 and m2.n_pair_features == 66


def test_freeze_for_transfer_leaves_only_last_layer_and_alpha():
    m = RH.HybridDeltaFModel(aggregation="sum", sqm_scale=True)
    train = RT.freeze_for_transfer(m)
    trainable = {n for n, p in m.named_parameters() if p.requires_grad}
    assert trainable == {"head.4.weight", "head.4.bias", "alpha"}
    assert sum(p.numel() for p in train) == sum(p.numel() for n, p in m.named_parameters() if n in trainable)
    assert not any(p.requires_grad for p in m.body.parameters())


def test_exclude_pool_ids(tmp_path):
    f = tmp_path / "ex.txt"
    f.write_text("m2\n\nm9\n", encoding="utf-8")
    pool, dropped = RT.exclude_pool_ids(["m1", "m2", "m3"], str(f))
    assert pool == ["m1", "m3"] and dropped == ["m2"]
    assert RT.exclude_pool_ids(["m1"], None) == (["m1"], [])
    with pytest.raises(SystemExit):
        RT.exclude_pool_ids(["m1"], str(f))                      # nothing in common: refuse rather than run the full pool
    text = (M05 / "rungC_train.py").read_text(encoding="utf-8")
    assert 'add_argument("--exclude-ids-file"' in text and "pool, excluded = exclude_pool_ids(pool, a.exclude_ids_file)" in text


def test_record_paths_keep_a_dotted_prefix():
    j, m = RT.record_paths("out/T3b_l20.01_seed0_2026-10-02")
    assert j.name == "T3b_l20.01_seed0_2026-10-02.json" and m.name == "T3b_l20.01_seed0_2026-10-02.md"
    for src in ("rungC_cc_transfer.py",):
        assert "with_suffix" not in (M05 / src).read_text(encoding="utf-8")
    assert "with_suffix" not in (PLAN / "probes" / "rungC_eval_saved.py").read_text(encoding="utf-8")


def test_trainer_switch_present():
    import re
    text = (M05 / "rungC_train.py").read_text(encoding="utf-8")
    assert re.search(r'add_argument\("--save-model", action="store_true"', text)
    assert "tensors[i] = molecule_tensors(i, m, mols[i]" in text


@pytest.mark.skipif(not (PLAN / "modules" / "05_support_predictor" / "corpus" / "molecules" / "A_8448043181" / "hessian_b3lyp_analytic.npz").exists(),
                    reason="corpus benzene with the analytic route not on this machine")
def test_substitute_cc_builds_k_from_the_cc_hessian():
    pytest.importorskip("geometric")
    import json

    import e7_t2_sqm as T2
    import rungC_cc_transfer as CT
    from learning_curve_layerA import AMU2AU, HARTREE2CM, normal_modes
    d = PLAN / "modules" / "05_support_predictor" / "corpus" / "molecules" / "A_8448043181"
    cc = PLAN / "probes" / "results_m1" / "e8_benzene_ccpvdz_tlambda" / "hessian_ccsd_t.npz"
    if not cc.exists():
        pytest.skip("benzene CC anchor not on this machine")
    g = json.load(open(d / "geometry.json"))
    masses, coords = np.asarray(g["masses_amu"]), np.asarray(g["coords_bohr"], float)
    B, _ = T2.internals(g["symbols"], coords)
    m = dict(masses=masses, B=B, family=["ring-ip"] * 30)
    CT.substitute_cc(m, d / "hessian_b3lyp_analytic.npz", cc)
    lo = np.load(d / "hessian_b3lyp_analytic.npz")["H_projected"]
    hi = np.load(cc)["H_projected"]
    assert np.allclose(m["dH_true"], hi - lo) and m["high_level"] == "ccsd_t"
    w, _, V, _ = normal_modes(lo, masses)
    mm = np.repeat(masses * AMU2AU, 3)
    Km = V.T @ ((hi - lo) / np.sqrt(np.outer(mm, mm))) @ V
    om = np.sqrt(np.abs(w))
    assert np.allclose(m["K"], Km / (2 * np.sqrt(np.outer(om, om))) * HARTREE2CM, rtol=1e-5, atol=1e-3)


def test_family_freq_rms_is_zero_on_the_truth_and_split_by_family():
    import rungC_cc_transfer as CT
    rng = np.random.default_rng(0)
    n = 6
    K = rng.normal(size=(n, n)) * 0.01
    K = 0.5 * (K + K.T)
    m = {"freq": np.array([800.0, 1000.0, 1200.0, 1400.0, 3000.0, 3100.0]), "K": K,
         "family": ["CH-oop", "ring-ip", "ring-ip", "ring-ip", "CH-stretch", "CH-stretch"]}
    z = CT.family_freq_rms(m, K)
    assert set(z) == {"CH-oop", "ring-ip", "CH-stretch"} and all(v == 0.0 for v in z.values())
    Kp = K.copy()
    Kp[1, 1] += 20.0                                         # a ring-ip diagonal shift (cm⁻¹ units of K) moves the ring-ip modes only
    e = CT.family_freq_rms(m, Kp)
    assert e["ring-ip"] > 1.0 and e["CH-stretch"] < 1e-6 and e["CH-oop"] < 1e-6


def test_head_l2_switch_present_and_penalty_keeps_the_proxy_weights():
    import rungC_cc_transfer as CT
    text = (M05 / "rungC_cc_transfer.py").read_text(encoding="utf-8")
    assert 'add_argument("--head-l2"' in text and '"network_head_l2"' in text
    # the penalty term: with the weights at W0 it is zero and its gradient vanishes — checked on a tiny stand-in head
    lin = torch.nn.Linear(4, 1)
    w0 = [p.detach().clone() for p in lin.parameters()]
    pen = 10.0 * sum(((p - q) ** 2).sum() for p, q in zip(lin.parameters(), w0, strict=True))
    assert float(pen) == 0.0
    with torch.no_grad():
        lin.weight += 0.5
    pen = 10.0 * sum(((p - q) ** 2).sum() for p, q in zip(lin.parameters(), w0, strict=True))
    assert float(pen) == pytest.approx(10.0 * 4 * 0.25)
    assert "head_l2" in CT.finetune.__doc__


def test_lora_adapter_starts_as_identity_and_counts_parameters():
    import rungC_cc_transfer as CT
    torch.manual_seed(0)
    m = RH.HybridDeltaFModel(aggregation="sum", sqm_scale=True, hidden=32)
    x = torch.randn(5, 32)
    mid = [k for k, l in enumerate(m.head) if isinstance(l, torch.nn.Linear)][1]
    before = m.head[mid](x).detach().clone()
    params = CT.attach_lora(m, 3)
    assert torch.allclose(m.head[mid](x), before)                      # A = 0: the adapted layer equals the proxy layer at the start
    assert sum(p.numel() for p in params) == 2 * 3 * 32
    assert not any(p.requires_grad for p in m.head[mid].base.parameters())
    text = (M05 / "rungC_cc_transfer.py").read_text(encoding="utf-8")
    assert 'add_argument("--lora-rank"' in text and '"network_lora"' in text


def test_alpha_scaling_baseline_recovers_a_per_class_factor():
    import rungC_cc_transfer as CT
    K = 5
    F = np.arange(1, K * K + 1, dtype=float).reshape(K, K)
    cls = torch.tensor([[0, 1, -1, -1, -1], [1, 0, 2, -1, -1], [-1, 2, 0, -1, -1], [-1, -1, -1, 3, -1], [-1, -1, -1, -1, 3]])
    alpha = {0: 2.0, 1: -0.5, 2: 0.25, 3: 1.5}
    dF = np.zeros((K, K))
    for c, a in alpha.items():
        dF[cls.numpy() == c] = a * F[cls.numpy() == c]
    mols = {"m1": {"F_low": F}, "m2": {"F_low": 2 * F}, "held": {"F_low": 3 * F}}
    tensors = {"m1": {"pat_cls": cls, "dF_true": torch.tensor(dF)}, "m2": {"pat_cls": cls, "dF_true": torch.tensor(2 * dF)}, "held": {"pat_cls": cls}}
    pred = CT.alpha_scaling_baseline(mols, tensors, ["m1", "m2"], "held")
    assert np.allclose(pred, 3 * dF)
