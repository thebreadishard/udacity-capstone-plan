"""probes/v14_search.py on synthetic records: the frozen list (deterministic, in range, every configuration a valid trainer command), the
plan's refusals, the score, the winner rule (no-worsening, two SE, the cap), plan → read1 → read2 → read3 end to end, the final chain's
whole-pool retraining of the winner with read3's refusals, and the frozen stage-1 chain reproduced from the frozen list."""
import collections
import json
import sys
from pathlib import Path

import pytest

pytest.importorskip("torch")
PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
sys.path.insert(0, str(PLAN / "modules" / "05_support_predictor" / "m05"))
sys.path.insert(0, str(PLAN / "tools"))
import promotion_read as P  # noqa: E402
import runspec as RUNSPEC  # noqa: E402
import v14_search as V  # noqa: E402
from rungC_config import config_from_argv  # noqa: E402

ON_LINES = {"diag_rms": {f: 3.0 for f in P.FAMILIES}, P.RATIO: 0.25}
FROZEN_STAGE1 = PLAN / "probes" / "runs" / "v14_stage1.json"                       # the chain the laptop runs since 15 Nov 2026
FROZEN_LIST = PLAN / "modules" / "05_support_predictor" / V.OUT / "configs.json"
FINAL_SEEDS = "0,1,2"


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    """Module 05 and the plan's probes folder inside tmp_path, with the carried checkpoints present."""
    monkeypatch.setattr(V, "M05", tmp_path / "m05")
    monkeypatch.setattr(V, "PLAN", tmp_path)
    (tmp_path / "m05" / V.OUT).mkdir(parents=True)
    carried = [f"out/carried_seed{s}.pt" for s in range(3)]
    for c in carried:
        (tmp_path / "m05" / c).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / "m05" / c).write_bytes(b"x")
    return tmp_path, carried


def test_the_list_is_frozen_in_range_and_holds_both_variants():
    a, b = V.draw(), V.draw()
    assert a == b and len(a) == V.N_DRAWN and len({c.name for c in a}) == V.N_DRAWN
    for c in a:
        for name in V.LOG_RANGES:
            lo, hi = V.SPACE[name]
            assert lo <= getattr(c, name) <= hi
        assert c.body_width in V.SPACE["body_width"] and c.hybrid_hidden in V.SPACE["hybrid_hidden"]
    assert {c.parity for c in a} == {True, False}
    assert {c.target for c in a} == set(V.TARGETS)
    assert {c.schedule for c in a} == set(V.SCHEDULES)
    half = V.N_DRAWN // 2
    assert sum(c.parity for c in a) == half and sum(c.target == V.CARRIED_TARGET for c in a) == half
    assert sum(c.schedule == V.CARRIED_SCHEDULE for c in a) == half
    pairs = [(lambda c: (c.parity, c.target)), (lambda c: (c.parity, c.schedule)), (lambda c: (c.target, c.schedule))]
    for pair in pairs:                                           # every pair of two choices' values: three of the twelve
        assert sorted(collections.Counter(pair(c) for c in a).values()) == [3, 3, 3, 3]
    assert len({(c.parity, c.target, c.schedule) for c in a}) == 8
    assert {(c.kring_weight, c.kdiag_weight) for c in a} == {(V.control().kring_weight, V.control().kdiag_weight)}


def test_the_dealt_choices_leave_every_drawn_range_as_it_was():
    def without_choices(configs):
        return [V.replace(c, parity=False, target=V.CARRIED_TARGET, schedule=V.CARRIED_SCHEDULE) for c in configs]
    assert without_choices(V.draw(choices_seed=1)) == without_choices(V.draw(choices_seed=2))


def test_the_choices_are_dealt_as_one_design_in_a_seeded_order():
    assert V.dealt_choices(12, seed=1) == V.dealt_choices(12, seed=1) != V.dealt_choices(12, seed=2)
    assert len(set(V.dealt_choices(8, seed=1))) == 8                                  # the first eight: every combination once


def test_the_frozen_list_holds_the_control_and_its_three_ablations():
    c, parity, target, schedule = V.frozen_list()[:4]
    assert c == V.control() and c.target == V.CARRIED_TARGET and not c.parity
    assert parity == V.replace(c, name="c01_control_parity", parity=True)
    assert target == V.replace(c, name="c02_control_target", target="ls")
    assert schedule == V.replace(c, name="c03_control_schedule", schedule="cosine")
    assert len(V.frozen_list()) == 4 + V.N_DRAWN and len({x.name for x in V.frozen_list()}) == 4 + V.N_DRAWN


def test_the_control_is_the_carried_recipe():
    c = V.control()
    assert (c.lr, c.weight_decay, c.body_width, c.body_blocks, c.hybrid_hidden, c.kring_weight, c.kdiag_weight, c.parity, c.schedule) == \
           (3e-4, 1e-4, 64, 3, 256, 0.3, 0.1, False, "constant")


def test_every_configuration_is_a_valid_trainer_command():
    for c in V.frozen_list():
        argv = V.trainer_argv(c, "out/x", "0")
        cfg = config_from_argv(argv[2:])                      # past '{python}' and the script; refusals raise here
        assert (cfg.lr, cfg.weight_decay, cfg.body_width, cfg.hybrid_hidden) == (c.lr, c.weight_decay, c.body_width, c.hybrid_hidden)
        assert cfg.parity_odd_mixed == c.parity and cfg.pair_features == (not c.parity)
        assert cfg.aux_target == c.target and cfg.lr_schedule == c.schedule and cfg.seeds == "0"
        assert cfg.patience == (V.EPOCH_CAP if c.schedule == "cosine" else 20)     # a cosine trains to its cap
        assert (cfg.kring_weight, cfg.kdiag_weight) == (0.3, 0.1)
        assert cfg.pool_layers == V.POOL_LAYERS and cfg.selection_split == V.SELECTION and cfg.epochs == V.EPOCH_CAP
        assert argv.count("--lr") == 1


def test_score_is_one_on_the_lines():
    assert V.score(ON_LINES) == pytest.approx(1.0)


def test_the_cap_rule_is_the_constant_rates_only():
    late = V.SeedRead({}, {}, best_epoch=V.EPOCH_CAP - 1, cap=V.EPOCH_CAP)
    early = V.SeedRead({}, {}, best_epoch=100, cap=V.EPOCH_CAP)
    assert V.at_cap(late, "constant") and not V.at_cap(early, "constant")
    assert not V.at_cap(late, "cosine")                        # the cosine ends at the cap by construction
    assert V.epoch_note(late, "constant").endswith("AT CAP") and V.epoch_note(late, "cosine").endswith("LATE")
    assert V.epoch_note(early, "cosine") == "100"


def stage2(name, scores, worse=(), cap=False):
    return V.Stage2(name, tuple(scores), tuple(worse), cap)


def test_the_winner_rule():
    ctrl = stage2("c00_control", (1.00, 1.02, 0.98))
    clear = stage2("c05", (0.80, 0.82, 0.78))
    assert V.winner([clear], ctrl)[0] == "c05"
    assert V.winner([stage2("c06", (0.99, 1.01, 0.97))], ctrl)[0] == "c00_control"                    # within two SE
    assert V.winner([stage2("c07", (0.5, 0.5, 0.5), worse=("(sel) CH-oop",)), clear], ctrl)[0] == "c05"  # the better one is ineligible
    assert V.winner([stage2("c07", (0.5, 0.5, 0.5), worse=("(sel) other",))], ctrl)[0] == "c00_control"


def test_plan_refuses_missing_checkpoints_and_overwrites(sandbox):
    _, carried = sandbox
    with pytest.raises(SystemExit, match="not found"):
        V.cmd_plan(["out/nope.pt", *carried[1:]])
    V.cmd_plan(carried)
    with pytest.raises(SystemExit, match="refusing to overwrite"):
        V.cmd_plan(carried)


def test_an_edited_list_is_refused(sandbox):
    root, carried = sandbox
    V.cmd_plan(carried)
    path = root / "m05" / V.OUT / "configs.json"
    rec = json.loads(path.read_text(encoding="utf-8"))
    rec["configs"][3]["lr"] = 0.5
    path.write_text(json.dumps(rec), encoding="utf-8")
    with pytest.raises(SystemExit, match="was edited"):
        V.load_list()


def sel_read(shift: float) -> dict:
    """A selection read 'shift' below the lines on every read-out, with two per-molecule entries (one cation)."""
    return {"diag_rms": {f: 3.0 - shift for f in P.FAMILIES}, P.RATIO: 0.25 - shift / 30,
            "per_molecule": {"P3c_x": {"corrected_freq_rms": 4.0}, "A_y": {"corrected_freq_rms": 2.0}}}


def write_record(root: Path, pre: str, seeds: dict[int, float], best_epoch: int = 100, split: bool = True) -> None:
    """A trainer record as `rungC_train.py` writes it: the selection split and the selection read only when the split was used."""
    per_seed = [{"seed": s, "best_epoch": best_epoch, **({"sel": sel_read(sh)} if split else {})} for s, sh in seeds.items()]
    rec = {**({"selection_split": V.SELECTION} if split else {}), "epochs": V.EPOCH_CAP, "curve": {"1000": {"per_seed": per_seed}}}
    (root / "m05" / f"{pre}.json").write_text(json.dumps(rec), encoding="utf-8")


def write_eval(root: Path, name: str, shift: float, seed: int, model: str) -> None:
    """An eval record as `rungC_eval_saved.py` writes it: `model` is the checkpoint it read, relative to module 05."""
    fam = {f: 3.0 - shift + 0.01 * seed for f in P.FAMILIES}
    rec = {"model": model, "holdout_b_file": "corpus/" + P.FROZEN_B, "substituted_analytic": ["m1"],
           **{h: {"diag_rms": fam, P.RATIO: 0.2 - shift / 30 + 0.001 * seed} for h in ("a", "b")}}
    (root / "m05" / V.OUT / f"eval_{name}_seed{seed}.json").write_text(json.dumps(rec), encoding="utf-8")


def full_checkpoint(w: V.Config, seed: int) -> str:
    return f"{V.prefix(w, V.FULL_TAG)}_model_n1082_seed{seed}.pt"


def assert_final_chain(root: Path, w: V.Config, other: V.Config, carried: list[str]) -> None:
    """The final chain and its run spec as read2 wrote them: the other target with the split, the winner on the whole pool, six evals."""
    spec = RUNSPEC.RunSpec.model_validate_json((root / "probes" / "runspecs" / "v14_final.json").read_text(encoding="utf-8"))
    final = json.loads((root / "probes" / "runs" / "v14_final.json").read_text(encoding="utf-8"))
    assert spec.estimate.hours == 6 * V.HOURS[w.schedule] + 1.0                     # six trainings and the evals
    assert spec.progress.max_gap_minutes == V.MAX_GAP_MINUTES and spec.memory.peak_gb == 7.7
    assert [s["label"].split(" (")[0] for s in final["steps"]] == [
        f"train {w.name}", f"train {w.name}", *(f"eval eval_{who}_seed{s}" for who in ("winner", "carried") for s in range(3)), "v1.4 search read3"]
    other_step, full_step = final["steps"][:2]
    assert other_step == V.train_step(other, "s3other", FINAL_SEEDS)                # the target check's arm keeps the selection split
    assert other_step["argv"].count("--aux-target") == (other.target != V.CARRIED_TARGET)
    assert other_step["argv"].count("--selection-split") == 1
    split_twin = V.trainer_argv(w, V.prefix(w, V.FULL_TAG), FINAL_SEEDS)             # the winner's stage command at this prefix and seeds
    k = split_twin.index("--selection-split")
    assert full_step["argv"] == split_twin[:k] + split_twin[k + 2:]                 # the same command, the split alone taken out
    whole = config_from_argv(full_step["argv"][2:])
    assert whole.selection_split is None and whole.seeds == FINAL_SEEDS and whole.inner_val > 0   # early stopping keeps its inner split
    assert [s["argv"][2:4] for s in final["steps"][2:5]] == [
        [f"{V.OUT}/E7_rungC_v14s3full_{w.name}_model_n*_seed{s}.pt", f"{V.OUT}/eval_winner_seed{s}"] for s in range(3)]
    assert [s["argv"][2] for s in final["steps"][5:8]] == carried


def test_plan_to_read3_end_to_end(sandbox):
    root, carried = sandbox
    V.cmd_plan(carried)
    configs, _ = V.load_list()
    stage1 = {c.name: 0.05 * k for k, c in enumerate(configs)}                      # the later the configuration, the better its score
    stage1["c00_control"] = 0.3
    for c in configs:
        write_record(root, V.prefix(c, "s1a"), {0: stage1[c.name] + 0.01})
        write_record(root, V.prefix(c, "s1b"), {1: stage1[c.name] - 0.01})
    RUNSPEC.RunSpec.model_validate_json((root / "probes" / "runspecs" / "v14_stage1.json").read_text(encoding="utf-8"))
    stage1_chain = json.loads((root / "probes" / "runs" / "v14_stage1.json").read_text(encoding="utf-8"))
    trainings = [s for s in stage1_chain["steps"] if s["label"].startswith("train ")]
    assert [s["argv"][s["argv"].index("--seeds") + 1] for s in trainings] == ["0"] * len(configs) + ["1"] * len(configs)
    V.cmd_read1()
    read1 = json.loads((root / "m05" / V.OUT / "read1.json").read_text(encoding="utf-8"))
    chosen = read1["stage2"]
    assert chosen == [c.name for c in configs[::-1][:V.STAGE2_BEST]]
    assert all(len(v) == len(V.STAGE1_SEEDS) for v in read1["seed_scores"].values())
    stage2_chain = json.loads((root / "probes" / "runs" / "v14_stage2.json").read_text(encoding="utf-8"))
    assert all(s["argv"][s["argv"].index("--seeds") + 1] == str(V.STAGE2_SEED) for s in stage2_chain["steps"][:-1])
    by_name = {c.name: c for c in configs}
    assert stage2_chain["steps"][:-1] == [V.train_step(by_name[n], "s2", str(V.STAGE2_SEED)) for n in ["c00_control", *chosen]]
    assert json.loads((root / "probes" / "runs" / "v14_stage2.json").read_text(encoding="utf-8"))["steps"][-1]["argv"][-1] == "read2"
    for c in configs:
        if c.name in [*chosen, "c00_control"]:
            write_record(root, V.prefix(c, "s2"), {V.STAGE2_SEED: stage1[c.name]})
    RUNSPEC.RunSpec.model_validate_json((root / "probes" / "runspecs" / "v14_stage2.json").read_text(encoding="utf-8"))
    V.cmd_read2()
    best = json.loads((root / "m05" / V.OUT / "read2.json").read_text(encoding="utf-8"))["winner"]
    assert best == chosen[0]
    w = next(c for c in configs if c.name == best)
    other = V.replace(w, target=next(t for t in V.TARGETS if t != w.target))
    assert_final_chain(root, w, other, carried)
    write_record(root, V.prefix(other, "s3other"), {0: stage1[best] + 0.2, 1: stage1[best] + 0.21, 2: stage1[best] + 0.19})  # larger shift = better
    stage_checkpoints = [f"{V.prefix(w, tag)}_model_n913_seed{s}.pt" for s, tag in enumerate(("s1a", "s1b", "s2"))]
    for s in range(3):
        write_eval(root, "winner", 0.5, s, stage_checkpoints[s])                    # what the final chain evaluated before 16 Nov
        write_eval(root, "carried", 0.1, s, carried[s])
    with pytest.raises(SystemExit, match="trained with --selection-split"):
        V.cmd_read3()
    assert not (root / "m05" / V.OUT / "read3.json").exists()
    write_record(root, V.prefix(w, V.FULL_TAG), dict.fromkeys(range(3), 0.0), split=False)
    for s in range(3):
        write_eval(root, "winner", 0.5, s, full_checkpoint(w, s))
    V.cmd_read3()
    rec = json.loads((root / "m05" / V.OUT / "read3.json").read_text(encoding="utf-8"))
    assert rec["promotion"]["promoted"] and rec["target_check"]["promoted"]          # the other target is better: the choice goes to the user
    assert rec["winner_trained_on"] == "whole pool" and rec["winner_best_epochs"] == [100, 100, 100]
    report = (root / "m05" / V.OUT / "read3.md").read_text(encoding="utf-8")
    assert "the choice goes to the user" in report
    (retrained,) = [line for line in report.splitlines() if "retrained on the whole pool" in line]
    assert "selection-set scores are not shown" in retrained and "biphenylene" in retrained


def test_read2_refuses_a_winner_at_the_cap(sandbox):
    root, carried = sandbox
    V.cmd_plan(carried)
    configs, _ = V.load_list()
    constant = [c.name for c in configs[4:] if c.schedule == "constant"][-1]        # the cap rule is the constant rate's
    shift = {c.name: 0.3 if k == 0 else 0.05 * k for k, c in enumerate(configs)}
    shift[constant] = 0.05 * len(configs) + 0.1                                     # the clear best of stage 1
    for c in configs:
        write_record(root, V.prefix(c, "s1a"), {0: shift[c.name]})
        write_record(root, V.prefix(c, "s1b"), {1: shift[c.name] + 0.02})
    V.cmd_read1()
    chosen = json.loads((root / "m05" / V.OUT / "read1.json").read_text(encoding="utf-8"))["stage2"]
    assert chosen[0] == constant
    for c in configs:
        if c.name in [*chosen, "c00_control"]:
            write_record(root, V.prefix(c, "s2"), {V.STAGE2_SEED: shift[c.name] + 0.01},
                         best_epoch=V.EPOCH_CAP if c.name == constant else 100)
    with pytest.raises(SystemExit, match="within 10% of the cap"):
        V.cmd_read2()


def at_read3(root: Path, carried: list[str], winner_index: int, full_epoch: int = 100) -> V.Config:
    """Every file read3 reads, written directly: the winner is the frozen list's configuration at `winner_index`."""
    V.cmd_plan(carried)
    w = V.load_list()[0][winner_index]
    other = V.replace(w, target=next(t for t in V.TARGETS if t != w.target))
    (root / "m05" / V.OUT / "read2.json").write_text(json.dumps({"winner": w.name}), encoding="utf-8")
    for tag, seed in (("s1a", 0), ("s1b", 1), ("s2", V.STAGE2_SEED)):
        write_record(root, V.prefix(w, tag), {seed: 0.3})
    write_record(root, V.prefix(other, "s3other"), dict.fromkeys(range(3), 0.1))
    write_record(root, V.prefix(w, V.FULL_TAG), dict.fromkeys(range(3), 0.0), best_epoch=full_epoch, split=False)
    for s in range(3):
        write_eval(root, "winner", 0.5, s, full_checkpoint(w, s))
        write_eval(root, "carried", 0.1, s, carried[s])
    return w


def test_read3_refuses_winner_evals_of_any_other_checkpoint(sandbox):
    root, carried = sandbox
    w = at_read3(root, carried, winner_index=0)
    V.cmd_read3()                                                                   # the whole-pool checkpoints: read
    write_eval(root, "winner", 0.5, 1, full_checkpoint(w, 2))                       # a whole-pool model, the wrong seed
    with pytest.raises(SystemExit, match="not seed 1 of"):
        V.cmd_read3()
    write_eval(root, "winner", 0.5, 1, carried[1])                                  # no trainer checkpoint's name
    with pytest.raises(SystemExit, match="not a trainer checkpoint"):
        V.cmd_read3()
    write_eval(root, "winner", 0.5, 1, "out/elsewhere_model_n1082_seed1.pt")        # a checkpoint without its training's record
    with pytest.raises(SystemExit, match="no trainer record"):
        V.cmd_read3()
    write_eval(root, "winner", 0.5, 1, f"{V.prefix(w, 's1b')}_model_n913_seed1.pt")  # one stage checkpoint among whole-pool ones
    with pytest.raises(SystemExit, match="trained with --selection-split"):
        V.cmd_read3()


def test_read3_applies_the_cap_rule_to_the_whole_pool_trainings(sandbox, tmp_path_factory, monkeypatch):
    root, carried = sandbox
    at_read3(root, carried, winner_index=0, full_epoch=V.EPOCH_CAP)                 # the control: a constant rate, stopped by the cap
    with pytest.raises(SystemExit, match="within 10% of the cap"):
        V.cmd_read3()
    other_root = tmp_path_factory.mktemp("cosine")                                  # c03: the cosine ends at the cap by construction
    monkeypatch.setattr(V, "M05", other_root / "m05")
    monkeypatch.setattr(V, "PLAN", other_root)
    for c in carried:
        (other_root / "m05" / c).parent.mkdir(parents=True, exist_ok=True)
        (other_root / "m05" / c).write_bytes(b"x")
    w = at_read3(other_root, carried, winner_index=3, full_epoch=V.EPOCH_CAP)
    assert w.schedule == "cosine"
    V.cmd_read3()
    assert f"{V.EPOCH_CAP} LATE" in (other_root / "m05" / V.OUT / "read3.md").read_text(encoding="utf-8")


def test_the_frozen_stage1_chain_comes_out_byte_identical(sandbox):
    """The chain in use was written by `plan` on 15 Nov 2026; the same inputs must give the same bytes after any change to the search."""
    root, _ = sandbox
    carried = json.loads(FROZEN_LIST.read_text(encoding="utf-8"))["carried_models"]
    for c in carried:
        (root / "m05" / c).parent.mkdir(parents=True, exist_ok=True)
        (root / "m05" / c).write_bytes(b"x")
    V.cmd_plan(carried)
    # the repository stores both files with LF; `write_text` on Windows writes CRLF
    written = {name: path.read_bytes().replace(b"\r\n", b"\n") for name, path in (
        ("chain", root / "probes" / "runs" / "v14_stage1.json"), ("list", root / "m05" / V.OUT / "configs.json"))}
    assert written["chain"] == FROZEN_STAGE1.read_bytes().replace(b"\r\n", b"\n")
    assert written["list"] == FROZEN_LIST.read_bytes().replace(b"\r\n", b"\n")


def test_a_stage2_training_is_the_frozen_stage1_command_at_the_third_seed():
    steps = json.loads(FROZEN_STAGE1.read_text(encoding="utf-8"))["steps"]
    frozen = {s["argv"][3]: s["argv"] for s in steps if s["label"].startswith("train ")}
    for c in V.frozen_list():
        was = frozen[V.prefix(c, "s1a")]
        k = was.index("--seeds")
        assert was[k + 1] == "0"
        assert V.train_step(c, "s2", str(V.STAGE2_SEED))["argv"] == [*was[:3], V.prefix(c, "s2"), *was[4:k + 1], str(V.STAGE2_SEED), *was[k + 2:]]


def test_the_selection_split_is_an_explicit_switch_of_the_trainer_command():
    c = V.control()
    default, kept, whole = (V.trainer_argv(c, "out/x", "0"), V.trainer_argv(c, "out/x", "0", selection_split=True),
                            V.trainer_argv(c, "out/x", "0", selection_split=False))
    assert default == kept and "--selection-split" in kept and "--selection-split" not in whole
    assert [x for x in kept if x not in ("--selection-split", V.SELECTION)] == whole
    with pytest.raises(TypeError):
        V.trainer_argv(c, "out/x", "0", False)                                      # keyword-only: no positional switch
