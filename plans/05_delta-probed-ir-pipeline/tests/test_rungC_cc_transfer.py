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
    g = json.loads((d / "geometry.json").read_text(encoding="utf-8"))
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
    assert CT.build_parser().parse_args(["m", "x.pt", "out", "--anchor", "a=b", "--head-l2", "0.1"]).head_l2 == 0.1
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
    mid = [k for k, layer in enumerate(m.head) if isinstance(layer, torch.nn.Linear)][1]
    before = m.head[mid](x).detach().clone()
    params = CT.attach_lora(m, 3)
    assert torch.allclose(m.head[mid](x), before)                      # A = 0: the adapted layer equals the proxy layer at the start
    assert sum(p.numel() for p in params) == 2 * 3 * 32
    assert not any(p.requires_grad for p in m.head[mid].base.parameters())


def test_the_lora_start_is_reproducible_and_leaves_the_global_generator_alone():
    """16 Oct 2026: the adapter's B drew from torch's default generator, which this torch seeds from the clock (the same fold gave 14.44
    and 14.05 cm⁻¹ in two runs); it now has its own seeded generator."""
    import rungC_cc_transfer as CT
    torch.manual_seed(1)
    starts = []
    for _ in range(2):
        m = RH.HybridDeltaFModel(aggregation="sum", sqm_scale=True, hidden=32)
        state = torch.get_rng_state()
        starts.append(CT.attach_lora(m, 3)[1].detach().clone())
        assert torch.equal(torch.get_rng_state(), state)
    assert torch.equal(starts[0], starts[1])
    assert not torch.equal(CT.LowRankLinear(torch.nn.Linear(32, 32), 3, seed=1).B, starts[0])


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
    """TASKS 45 (10 Oct 2026): one writer for --predict and --save-fold-predictions; a fold file names its held-out anchor. The switch's
    use (the standard mode's fold files) is pinned by test_rungC_cc_transfer_regression."""
    pred = RT_T.Prediction(np.eye(3), 2 * np.eye(3), "hessian_b3lyp_analytic.npz", "head_l2", ["B", "C"], "m.pt", None, held="A")
    with np.load(pred.save(tmp_path / "x_fold_A.npz")) as z:
        assert z["held"].item() == "A" and list(z["anchors"]) == ["B", "C"] and z["mode"].item() == "head_l2" and np.isnan(z["final_loss"])
        assert np.allclose(z["dH_pred"] + z["H_low"], 3 * np.eye(3))


def test_fit_mode_follows_the_tz_tier_standard():
    """TASKS 36 (8 Oct 2026): the fit on all anchors uses the head-tuned column with the L2 pull when it is set (amendment (A))."""
    assert RT_T.fit_mode(1.0) == "head_l2" and RT_T.fit_mode(0.0) == "head"


def test_an_exclude_file_s_comment_lines_are_not_ids(tmp_path):
    """13 Oct 2026: chain 41's exclude files carry a '#' header; it must not count as an id."""
    import rungC_train as RT
    f = tmp_path / "ex.txt"
    f.write_text("# header\nb\n", encoding="utf-8")
    assert RT.exclude_pool_ids(["a", "b"], str(f)) == (["a"], ["b"])


def test_anchor_subsets_take_all_when_few_and_a_fixed_draw_when_many():
    """Anchor set three (amendment of 14 Oct 2026): five subsets per size below 'all', numpy seed 0, all of them when no more exist."""
    five = ["e", "d", "c", "b", "a"]
    assert RT_T.anchor_subsets(five, 4) == [("a", "b", "c", "d"), ("a", "b", "c", "e"), ("a", "b", "d", "e"), ("a", "c", "d", "e"),
                                            ("b", "c", "d", "e")]
    assert RT_T.anchor_subsets(five, 5) == [("a", "b", "c", "d", "e")]
    ten = [f"m{i}" for i in range(10)]
    drawn = RT_T.anchor_subsets(ten, 4)
    assert len(drawn) == 5 and len(set(drawn)) == 5 and all(len(s) == 4 and set(s) <= set(ten) for s in drawn)
    assert RT_T.anchor_subsets(list(reversed(ten)), 4) == drawn                  # the pool's order does not change the draw
    assert len(RT_T.anchor_subsets(five, 2)) == 5 and len(set(RT_T.anchor_subsets(five, 2))) == 5     # C(5, 2) = 10 > 5
    for bad in (0, 6):
        with pytest.raises(ValueError):
            RT_T.anchor_subsets(five, bad)


@pytest.mark.parametrize(("extra", "says"), [
    (["--held", "z"], "not among the anchors"),
    (["--held", "a", "--skip-folds"], "--skip-folds runs none"),
    (["--oop-fit-sizes", "1"], "give both"),
    (["--oop-diagonal-model", "--oop-fit-sizes", "1,2"], "every size must be smaller"),
])
def test_switches_that_do_not_combine_are_refused_before_loading(extra, says):
    argv = ["m", "x.pt", "out", "--anchor", "a=1", "--anchor", "b=2", "--anchor", "c=3", *extra]
    a = RT_T.build_parser().parse_args(argv)
    with pytest.raises(SystemExit, match=says):
        RT_T.check_switches(a, dict(s.split("=", 1) for s in a.anchor))


def test_the_set_three_switches_parse_and_combine():
    a = RT_T.build_parser().parse_args(["m", "x.pt", "out", "--anchor", "a=1", "--anchor", "b=2", "--anchor", "c=3", "--anchor", "d=4",
                                        "--held", "b", "--held", "a", "--oop-diagonal-model", "--oop-fit-sizes", "2,1,2"])
    assert a.held == ["b", "a"] and a.oop_fit_sizes == [1, 2]
    RT_T.check_switches(a, dict(s.split("=", 1) for s in a.anchor))           # passes
    for bad in ("0", "x", ""):
        with pytest.raises(SystemExit):
            RT_T.build_parser().parse_args(["m", "x.pt", "out", "--anchor", "a=1", "--oop-fit-sizes", bad])


def test_oop_subset_reads_fit_on_each_subset_and_keep_the_fold_s_training_anchors(monkeypatch):
    """The wiring of arm M along the anchor count: one fit per subset, from that subset's anchors only; the read sees the fold's full
    training list and the network's predictor."""
    fits, reads = [], []
    monkeypatch.setattr(RT_T, "oop_shift_coefficients", lambda an, ids: fits.append(tuple(ids)) or np.array([len(fits), 0.0, 0.0]))
    monkeypatch.setattr(RT_T, "oop_model_predictor", lambda an, dF_of, coef: (dF_of, float(coef[0])))
    monkeypatch.setattr(RT_T, "read", lambda an, held, tr, pred: reads.append((held, tuple(tr), pred)) or {"n": pred[1]})
    train = ["t1", "t2", "t3", "t4"]
    out = RT_T.oop_subset_reads(None, "h", train, "network", [1, 3])
    assert sorted(out) == ["1", "3"] and len(out["1"]) == 4 and len(out["3"]) == 4          # C(4, 1) = C(4, 3) = 4 ≤ 5: all of them
    assert fits == [tuple(r["train"]) for k in ("1", "3") for r in out[k]]
    assert all(r == ("h", tuple(train), ("network", r[2][1])) for r in reads)
    assert [r["read"]["n"] for r in out["1"]] == [1.0, 2.0, 3.0, 4.0]


def test_modes_narrow_the_enabled_ones_and_unknown_modes_are_refused():
    base = ["m", "x.pt", "out", "--anchor", "a=1", "--anchor", "b=2", "--anchor", "c=3"]
    a = RT_T.build_parser().parse_args([*base, "--head-l2", "1", "--head-all", "--modes", "head_l2,head_all"])
    assert RT_T.enabled_modes(a) == ("none", "alpha", "head", "head_l2", "head_all") and RT_T.fold_modes(a) == ("head_l2", "head_all")
    RT_T.check_switches(a, dict(s.split("=", 1) for s in a.anchor))
    plain = RT_T.build_parser().parse_args(base)
    assert RT_T.fold_modes(plain) == ("none", "alpha", "head")
    bad = RT_T.build_parser().parse_args([*base, "--modes", "head_l2"])                  # not enabled without --head-l2
    with pytest.raises(SystemExit, match="not enabled"):
        RT_T.check_switches(bad, dict(s.split("=", 1) for s in bad.anchor))


def test_init_scale_multiplies_the_last_layer_only():
    m = RH.HybridDeltaFModel(aggregation="sum", sqm_scale=True)
    before = {n: p.detach().clone() for n, p in m.named_parameters()}
    RT_T.scale_last_layer(m, -0.5)
    for n, p in m.named_parameters():
        expected = before[n] * -0.5 if n.startswith("head.4.") else before[n]
        assert torch.equal(p, expected), n
    assert RT_T.build_parser().parse_args(["m", "x.pt", "out", "--anchor", "a=1"]).init_scale == 1.0


def test_in_sample_keeps_the_held_out_anchor_in_the_pool():
    assert RT_T.training_anchors(["a", "b", "c"], "b", in_sample=False) == ["a", "c"]
    assert RT_T.training_anchors(["a", "b", "c"], "b", in_sample=True) == ["a", "b", "c"]


def test_head_all_trains_every_head_layer_and_alpha_and_nothing_else():
    m = RH.HybridDeltaFModel(aggregation="sum", sqm_scale=True)
    params = RT_T._trainable(m, "head_all", RT_T.FinetuneSettings(1, 1e-3, 1.0))
    trainable = {n for n, p in m.named_parameters() if p.requires_grad}
    assert trainable == {n for n, _ in m.named_parameters() if n.startswith("head.")} | {"alpha"}
    assert sum(p.numel() for p in params) == sum(p.numel() for n, p in m.named_parameters() if n in trainable)
    assert not any(p.requires_grad for p in m.body.parameters())


def test_the_out_of_plane_switches_add_their_table_columns():
    """TASKS 51 (13 Oct 2026): the arms of R-A's fail branch are columns of the same read, for both head-tuned modes; that the model's
    coefficients come from the training anchors only is the signature of oop_shift_coefficients (an, train_ids), and the columns' values
    are pinned by test_rungC_cc_transfer_regression."""
    import rungC_cc_transfer as CT
    a = CT.build_parser().parse_args(["m", "x.pt", "out", "--anchor", "a=b", "--head-l2", "0.1", "--oop-couplings-low", "--oop-diagonal-model"])
    keys = [k for k, _ in CT.table_columns(a)]
    assert {"network_head_ooplow", "network_head_l2_ooplow", "oop_model_only", "network_head_oopmodel", "network_head_l2_oopmodel"} <= set(keys)
    plain = CT.build_parser().parse_args(["m", "x.pt", "out", "--anchor", "a=b"])
    assert [k for k, _ in CT.table_columns(plain)] == ["zero_rule", "alpha_scaling", "network_none", "network_alpha", "network_head"]
