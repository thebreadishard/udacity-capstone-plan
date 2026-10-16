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
import rungC_cc_transfer as RT_T  # noqa: E402
import rungC_hybrid as RH  # noqa: E402
import rungC_train as RT  # noqa: E402
from rungC_config import TrainConfig, parse_config  # noqa: E402

torch.set_num_threads(1)


def test_save_and_load_round_trip(tmp_path):
    torch.manual_seed(0)
    m = RH.HybridDeltaFModel(aggregation="sum", sqm_scale=True, n_pair_features=66, hidden=256)
    loss = RT.LossSettings(mode="both", kring_weight=0.3, kdiag_weight=0.1, kdiag_mode="family", class_scale=torch.rand(RH.N_PAIR_CLASSES))
    args = dict(aggregation="sum", tensor_input=False, sqm_scale=True, pattern="f", aux_target="projected", ls_lam=1e-3, head="hybrid")
    p = tmp_path / "m.pt"
    RT.save_hybrid_model(m, loss, p, args, n=750, seed=0, train_ids=["a", "b"])
    m2, ck = RT.load_hybrid_model(p)
    assert ck["train_ids"] == ["a", "b"]                                   # 8 Oct 2026: the training pool travels with the model
    for k, v in m.state_dict().items():
        assert torch.equal(m2.state_dict()[k], v)
    back = RT.loss_settings(ck)
    assert (back.mode, back.kring_weight, back.kdiag_weight, back.kdiag_mode) == ("both", 0.3, 0.1, "family")
    assert torch.equal(back.class_scale, loss.class_scale)
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
    assert parse_config(["mol", "out", "--exclude-ids-file", str(f)]).exclude_ids_file == str(f)
    with pytest.raises(SystemExit):
        parse_config(["mol", "out", "--exclude-ids-file", str(tmp_path / "missing.txt")])   # refused before the corpus is loaded


def test_record_paths_keep_a_dotted_prefix():
    j, m = RT.record_paths("out/T3b_l20.01_seed0_2026-10-02")
    assert j.name == "T3b_l20.01_seed0_2026-10-02.json" and m.name == "T3b_l20.01_seed0_2026-10-02.md"
    for src in ("rungC_cc_transfer.py",):
        assert "with_suffix" not in (M05 / src).read_text(encoding="utf-8")
    assert "with_suffix" not in (PLAN / "probes" / "rungC_eval_saved.py").read_text(encoding="utf-8")


def test_trainer_switch_present():
    assert parse_config(["mol", "out", "--head", "hybrid", "--aux", "both", "--save-model"]).save_model
    with pytest.raises(ValueError, match="--save-model works only with --head hybrid"):
        TrainConfig(molecules="mol", out_prefix="out", save_model=True)       # refused before training, not after the first seed


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


def test_load_cc_apt_refuses_an_apt_from_another_geometry(tmp_path):
    """TASKS 32 (8 Oct 2026): the intensity read-out takes a CC APT only if it was computed at the corpus geometry of the molecule."""
    import json
    x = np.arange(9.0).reshape(3, 3)
    (tmp_path / "geometry.json").write_text(json.dumps({"coords_bohr": x.tolist()}), encoding="utf-8")
    np.savez(tmp_path / "ok.npz", apt=np.ones((3, 9)), coords_bohr=x)
    np.savez(tmp_path / "far.npz", apt=np.ones((3, 9)), coords_bohr=x + 1e-3)
    assert RT_T.load_cc_apt(tmp_path / "ok.npz", tmp_path).shape == (3, 9)
    with pytest.raises(SystemExit):
        RT_T.load_cc_apt(tmp_path / "far.npz", tmp_path)


def test_save_prediction_round_trip(tmp_path):
    """TASKS 45 (10 Oct 2026): one writer for --predict and --save-fold-predictions; a fold file names its held-out anchor."""
    p = RT_T.save_prediction(tmp_path / "x_fold_A.npz", np.eye(3), 2 * np.eye(3), "hessian_b3lyp_analytic.npz", "head_l2", ["B", "C"], "m.pt", None, held="A")
    z = np.load(p)
    assert z["held"].item() == "A" and list(z["anchors"]) == ["B", "C"] and z["mode"].item() == "head_l2" and np.isnan(z["final_loss"])
    assert np.allclose(z["dH_pred"] + z["H_low"], 3 * np.eye(3))
    text = (Path(RT_T.__file__)).read_text(encoding="utf-8")
    assert "--save-fold-predictions" in text and "mode == fit_mode(a.head_l2)" in text


def test_fit_mode_follows_the_tz_tier_standard():
    """TASKS 36 (8 Oct 2026): the fit on all anchors uses the head-tuned column with the L2 pull when it is set (amendment (A))."""
    assert RT_T.fit_mode(1.0) == "head_l2" and RT_T.fit_mode(0.0) == "head"


def test_an_exclude_file_s_comment_lines_are_not_ids(tmp_path):
    """13 Oct 2026: chain 41's exclude files carry a '#' header; it must not count as an id."""
    import rungC_train as RT
    f = tmp_path / "ex.txt"
    f.write_text("# header\nb\n", encoding="utf-8")
    assert RT.exclude_pool_ids(["a", "b"], str(f)) == (["a"], ["b"])


def test_oop_couplings_low_switch_adds_its_columns():
    """TASKS 51 (13 Oct 2026): the arm of R-A's fail branch is a column of the same read, for both head-tuned modes."""
    text = (M05 / "rungC_cc_transfer.py").read_text(encoding="utf-8")
    assert 'add_argument("--oop-couplings-low"' in text and 'f"network_{mode}_ooplow"' in text
    assert '"network_head_ooplow"' in text and '"network_head_l2_ooplow"' in text and 'mode in ("head", "head_l2")' in text


def test_oop_diagonal_model_switch_fits_per_fold_on_the_training_anchors_only():
    """TASKS 51: the model's coefficients come from `tr` (never the held-out anchor) and its columns sit in the same read."""
    text = (M05 / "rungC_cc_transfer.py").read_text(encoding="utf-8")
    assert 'add_argument("--oop-diagonal-model"' in text and "coef = oop_coef(tr)" in text
    assert '"oop_model_only"' in text and 'f"network_{mode}_oopmodel"' in text and '"network_head_l2_oopmodel"' in text
