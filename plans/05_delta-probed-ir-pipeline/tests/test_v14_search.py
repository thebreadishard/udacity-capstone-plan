"""probes/v14_search.py on synthetic records: the frozen list (deterministic, in range, every configuration a valid trainer command), the
plan's refusals, the score, the winner rule (no-worsening, two SE, the cap), and plan → read1 → read2 → read3 end to end."""
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


def write_record(root: Path, pre: str, seeds: dict[int, float], best_epoch: int = 100) -> None:
    rec = {"selection_split": V.SELECTION, "epochs": V.EPOCH_CAP,
           "curve": {"1000": {"per_seed": [{"seed": s, "sel": sel_read(sh), "best_epoch": best_epoch} for s, sh in seeds.items()]}}}
    (root / "m05" / f"{pre}.json").write_text(json.dumps(rec), encoding="utf-8")


def write_eval(root: Path, name: str, shift: float, seed: int) -> None:
    fam = {f: 3.0 - shift + 0.01 * seed for f in P.FAMILIES}
    rec = {"holdout_b_file": "corpus/" + P.FROZEN_B, "substituted_analytic": ["m1"],
           **{h: {"diag_rms": fam, P.RATIO: 0.2 - shift / 30 + 0.001 * seed} for h in ("a", "b")}}
    (root / "m05" / V.OUT / f"eval_{name}_seed{seed}.json").write_text(json.dumps(rec), encoding="utf-8")


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
    assert json.loads((root / "probes" / "runs" / "v14_stage2.json").read_text(encoding="utf-8"))["steps"][-1]["argv"][-1] == "read2"
    for c in configs:
        if c.name in [*chosen, "c00_control"]:
            write_record(root, V.prefix(c, "s2"), {V.STAGE2_SEED: stage1[c.name]})
    RUNSPEC.RunSpec.model_validate_json((root / "probes" / "runspecs" / "v14_stage2.json").read_text(encoding="utf-8"))
    V.cmd_read2()
    RUNSPEC.RunSpec.model_validate_json((root / "probes" / "runspecs" / "v14_final.json").read_text(encoding="utf-8"))
    best = json.loads((root / "m05" / V.OUT / "read2.json").read_text(encoding="utf-8"))["winner"]
    assert best == chosen[0]
    final = json.loads((root / "probes" / "runs" / "v14_final.json").read_text(encoding="utf-8"))
    w = next(c for c in configs if c.name == best)
    other = V.replace(w, target=next(t for t in V.TARGETS if t != w.target))
    assert final["steps"][0]["argv"].count("--aux-target") == (other.target != V.CARRIED_TARGET)
    assert any(s["argv"][2] == carried[0] for s in final["steps"][1:7])
    write_record(root, V.prefix(other, "s3other"), {0: stage1[best] + 0.2, 1: stage1[best] + 0.21, 2: stage1[best] + 0.19})  # larger shift = better
    for s in range(3):
        write_eval(root, "winner", 0.5, s)
        write_eval(root, "carried", 0.1, s)
    V.cmd_read3()
    rec = json.loads((root / "m05" / V.OUT / "read3.json").read_text(encoding="utf-8"))
    assert rec["promotion"]["promoted"] and rec["target_check"]["promoted"]          # the other target is better: the choice goes to the user
    assert "the choice goes to the user" in (root / "m05" / V.OUT / "read3.md").read_text(encoding="utf-8")


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
