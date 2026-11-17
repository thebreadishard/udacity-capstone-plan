"""probes/v14_search.py on synthetic records: the frozen list (deterministic, in range, every configuration a valid trainer command), the
plan's refusals, the score, the winner rule (no-worsening, two SE, the cap), plan → read1 → read2 → read3 end to end, the final chain's
whole-pool retraining of the winner with read3's refusals, the score on the selection set without the excluded core (the
evaluator stubbed), and the frozen stage-1 chain reproduced from the frozen list."""
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
import model_registry as MR  # noqa: E402
import promotion_read as P  # noqa: E402
import runspec as RUNSPEC  # noqa: E402
import v14_search as V  # noqa: E402
from rungC_config import config_from_argv  # noqa: E402

ON_LINES = {"diag_rms": {f: 3.0 for f in P.FAMILIES}, P.RATIO: 0.25}
FROZEN_STAGE1 = PLAN / "probes" / "runs" / "v14_stage1.json"                       # the chain the laptop runs since 15 Nov 2026
FROZEN_LIST = PLAN / "modules" / "05_support_predictor" / V.OUT / "configs.json"
FINAL_SEEDS = "0,1,2"


BIPHENYLENES = [f"A2_bph{k}" for k in range(8)]
SEL_IDS = [f"A2_sel{k:03d}" for k in range(161)] + BIPHENYLENES                    # the search's selection set: 169, 8 of the excluded core
NAMES = {"A_72b86c2331": "biphenylene", **{i: "pyrene+F" for i in SEL_IDS[:158]}, **{i: "fluoranthene+F" for i in SEL_IDS[158:161]},
         **{i: f"biphenylene+X{k}" for k, i in enumerate(BIPHENYLENES)}}


@pytest.fixture(autouse=True)
def registry(tmp_path, monkeypatch):
    """Every test's model registry is a file of its own. (The registry's own status files cover real checkpoint folders only, so a
    test's checkpoint could not reach them either: `model_registry.status_file_for` refuses a path outside those folders.)"""
    path = tmp_path / "registry" / "MODELS_STATUS.json"
    path.parent.mkdir()
    monkeypatch.setattr(V, "REGISTRY_STATUS_FILE", path)
    return path


class FakeEvaluator:
    """Stands in for `V.run_evaluator`: passes the model registry's real gate as the evaluator's first line does
    (`model_registry.require_carried`, here on the test's registry), then writes the record `rungC_eval_saved.py` would write for the
    command, with the trainer's own selection read on the whole set.
    `gain[configuration name]` lowers that configuration's read-outs on the scored set, as if the
    excluded core had carried that much of its error; `all_shift` makes the whole-set read differ from the trainer's."""

    def __init__(self) -> None:
        self.calls: list[list[str]] = []
        self.gain: dict[str, float] = {}
        self.all_shift = 0.0

    def __call__(self, argv: list[str], log: Path) -> None:
        self.calls.append(argv)
        model, out = argv[2], argv[3]
        MR.require_carried(V.M05 / model, allow="--allow-any-model" in argv, status_file=V.REGISTRY_STATUS_FILE)
        files = dict(a.split("=") for k, a in enumerate(argv) if argv[k - 1] == "--eval-ids-file")
        m = V.CHECKPOINT.fullmatch(Path(model).name)
        (entry,) = json.loads((V.M05 / Path(model).parent / f"{m['prefix']}.json").read_text(encoding="utf-8"))["curve"].values()
        sel = next(s["sel"] for s in entry["per_seed"] if s["seed"] == int(m["seed"]))
        gain = next((g for name, g in self.gain.items() if m["prefix"].endswith(name)), 0.0)

        def read(name: str, shift: float) -> dict:
            ids = (V.M05 / files[name]).read_text(encoding="utf-8").split()
            return {"diag_rms": {f: v - shift for f, v in sel["diag_rms"].items()}, P.RATIO: sel[P.RATIO] - shift / 30,
                    "per_molecule": {i: {"corrected_freq_rms": 2.0} for i in ids}, "dropped": [], "file": files[name]}
        rec = {"model": model, V.SEL_ALL: read(V.SEL_ALL, self.all_shift), V.SEL_SCORED: read(V.SEL_SCORED, gain)}
        (V.M05 / f"{out}.json").write_text(json.dumps(rec), encoding="utf-8")
        (V.M05 / f"{out}.md").write_text("# a saved model read\n", encoding="utf-8")


def make_module(root: Path, monkeypatch) -> list[str]:
    """Module 05 and the plan's probes folder inside `root`: the manifest, the carried checkpoints (returned)."""
    monkeypatch.setattr(V, "M05", root / "m05")
    monkeypatch.setattr(V, "PLAN", root)
    (root / "m05" / V.OUT).mkdir(parents=True)
    (root / "m05" / "corpus").mkdir()
    (root / "m05" / "corpus" / "manifest.csv").write_text("id,layer,name\n" + "".join(f"{i},A2,{n}\n" for i, n in NAMES.items()),
                                                         encoding="utf-8")
    carried = [f"out/carried_seed{s}.pt" for s in range(3)]
    for c in carried:
        (root / "m05" / c).write_bytes(b"x")
    return carried


@pytest.fixture
def evaluator(monkeypatch):
    fake = FakeEvaluator()
    monkeypatch.setattr(V, "run_evaluator", fake)
    return fake


@pytest.fixture
def sandbox(tmp_path, monkeypatch, evaluator):
    """Module 05 and the plan's probes folder inside tmp_path, with the carried checkpoints present and the evaluator stubbed."""
    return tmp_path, make_module(tmp_path, monkeypatch)


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
    late = V.SeedRead({}, {}, best_epoch=V.EPOCH_CAP - 1, cap=V.EPOCH_CAP, scored={})
    early = V.SeedRead({}, {}, best_epoch=100, cap=V.EPOCH_CAP, scored={})
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
    """A trainer record as `rungC_train.py` writes it, with its checkpoints: the selection split, the selection set and the selection
    read only when the split was used."""
    per_seed = [{"seed": s, "best_epoch": best_epoch, **({"sel": sel_read(sh)} if split else {})} for s, sh in seeds.items()]
    rec = {**({"selection_split": V.SELECTION, "holdout_sel": SEL_IDS} if split else {}), "epochs": V.EPOCH_CAP,
           "curve": {"1000": {"per_seed": per_seed}}}
    (root / "m05" / f"{pre}.json").write_text(json.dumps(rec), encoding="utf-8")
    for s in seeds:
        (root / "m05" / f"{pre}_model_n{913 if split else 1082}_seed{s}.pt").write_bytes(b"x")


def write_eval(root: Path, name: str, shift: float, seed: int, model: str | None, biphenylene: float = 2.0,   # noqa: PLR0913  a record's fields
               clean_shift: float | None = None) -> None:
    """An eval record as `rungC_eval_saved.py` writes it: `model` is the checkpoint it read, relative to module 05 (None: no such
    key), and every hold-out read carries its per-molecule read-outs. With `clean_shift` the record also holds hold-out (a)'s clean
    set, its read-outs that far below the lines."""
    fam = {f: 3.0 - shift + 0.01 * seed for f in P.FAMILIES}
    per_molecule = {V.PREDICTION_MOLECULE: {"corrected_freq_rms": biphenylene}}
    rec = {**({"model": model} if model else {}), "holdout_b_file": "corpus/" + P.FROZEN_B, "substituted_analytic": ["m1"],
           **{h: {"diag_rms": fam, P.RATIO: 0.2 - shift / 30 + 0.001 * seed, "corrected_freq_rms": 3.0 - shift + 0.01 * seed,
                  "per_molecule": per_molecule} for h in ("a", "b")}}
    if clean_shift is not None:
        rec[V.CLEAN_A] = {"diag_rms": {f: 3.0 - clean_shift + 0.01 * seed for f in P.FAMILIES}, P.RATIO: 0.2 - clean_shift / 30 + 0.001 * seed,
                          "corrected_freq_rms": 3.0 - clean_shift + 0.01 * seed, "per_molecule": per_molecule}
    (root / "m05" / V.OUT / f"eval_{name}_seed{seed}.json").write_text(json.dumps(rec), encoding="utf-8")


def full_checkpoint(w: V.Config, seed: int) -> str:
    return f"{V.prefix(w, V.FULL_TAG)}_model_n1082_seed{seed}.pt"


def patterns_the_runner_expands(root: Path, name: str) -> int:
    """A written chain walked through the runner's own `expand`: every argument with a '*' must be in a step the runner expands
    (17 Nov 2026: `expand` dropped glob_args and the patterns reached their programs as written). Returns the number of patterns."""
    spec = json.loads((root / "probes" / "runs" / f"{name}.json").read_text(encoding="utf-8"))
    steps = V.chain_runner.expand(spec, "py")
    literal = [(s["label"], a) for s in steps for a in s["argv"] if "*" in a and not s.get("glob_args")]
    assert not literal, f"{name}: patterns the runner would pass as written: {literal}"
    return sum("*" in a for s in steps for a in s["argv"])


def assert_final_chain(root: Path, w: V.Config, other: V.Config, carried: list[str]) -> None:
    """The final chain and its run spec as read2 wrote them: the other target with the split, the winner on the whole pool, six evals."""
    spec = RUNSPEC.RunSpec.model_validate_json((root / "probes" / "runspecs" / "v14_final.json").read_text(encoding="utf-8"))
    final = json.loads((root / "probes" / "runs" / "v14_final.json").read_text(encoding="utf-8"))
    assert patterns_the_runner_expands(root, "v14_stage2") == 0 and patterns_the_runner_expands(root, "v14_final") == 3   # eval_winner_seed*
    assert spec.estimate.hours == pytest.approx(3 * V.HOURS[w.schedule] * (1 + 1080 / 911) + 1.0)   # the whole pool is 18.6 % larger
    assert spec.progress.max_gap_minutes == V.MAX_GAP_MINUTES and spec.memory.peak_gb == 7.7
    assert [s["label"].split(" (")[0] for s in final["steps"]] == [
        f"train {w.name}", f"train {w.name}", "v1.4 search register",
        *(f"eval eval_{who}_seed{s}" for who in ("winner", "carried") for s in range(3)), "v1.4 search read3"]
    assert final["steps"][2]["argv"] == ["{python}", "probes/v14_search.py", "register"]   # the registry entry before the evals
    other_step, full_step = final["steps"][:2]
    assert other_step == V.train_step(other, "s3other", FINAL_SEEDS)                # the target check's arm keeps the selection split
    assert other_step["argv"].count("--aux-target") == (other.target != V.CARRIED_TARGET)
    assert other_step["argv"].count("--selection-split") == 1
    split_twin = V.trainer_argv(w, V.prefix(w, V.FULL_TAG), FINAL_SEEDS)             # the winner's stage command at this prefix and seeds
    k = split_twin.index("--selection-split")
    assert full_step["argv"] == split_twin[:k] + split_twin[k + 2:]                 # the same command, the split alone taken out
    whole = config_from_argv(full_step["argv"][2:])
    assert whole.selection_split is None and whole.seeds == FINAL_SEEDS and whole.inner_val > 0   # early stopping keeps its inner split
    assert [s["argv"][2:4] for s in final["steps"][3:6]] == [
        [f"{V.OUT}/E7_rungC_v14s3full_{w.name}_model_n*_seed{s}.pt", f"{V.OUT}/eval_winner_seed{s}"] for s in range(3)]
    assert [s["argv"][2] for s in final["steps"][6:9]] == carried


def assert_both_scores_agree(root: Path, chosen: list[str]) -> None:
    """read1 and read2 where the stubbed evaluator gives the scored set the registered read-outs: both scores printed, one decision."""
    read1, read2 = (json.loads((root / "m05" / V.OUT / f"{name}.json").read_text(encoding="utf-8")) for name in ("read1", "read2"))
    report1, report2 = ((root / "m05" / V.OUT / f"{name}.md").read_text(encoding="utf-8") for name in ("read1", "read2"))
    assert read1["stage2_registered"] == chosen and read1["scores"] == pytest.approx(read1["registered_scores"])
    assert "It sends the same configurations to stage 2, in the same order." in report1
    assert read2["winner"] == read2["winner_registered"] and read2["rows"] == read2["rows_registered"]
    assert "all 169 (mean ± SE)" in report2
    assert ("Among these candidates, which stage 1 chose on the scored set, the winner rule on the registered score gives the same "
            "winner.") in report2


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
    assert_both_scores_agree(root, chosen)
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
    assert "the choice goes to the user" in report and "On the registered set (all 169):" in report and "the same decision." in report \
        and rec["target_check"] == rec["target_check_registered"] and rec["prediction"]["passed"]
    assert rec["expectation"]["b"] == {"winner": pytest.approx(2.51), "carried": pytest.approx(2.91), "held": True}
    assert "hold-out (b) winner 2.51 against carried 2.91 (expected below: held)" in report
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
    write_eval(root, "winner", 0.5, 1, None)                                        # a record without its model
    with pytest.raises(SystemExit, match="names no model"):
        V.cmd_read3()
    (root / "m05" / V.OUT / "eval_winner_seed1.json").unlink()                      # the eval step has not run
    with pytest.raises(SystemExit, match="no eval record"):
        V.cmd_read3()


def test_read3_applies_the_cap_rule_to_the_whole_pool_trainings(sandbox, tmp_path_factory, monkeypatch):
    root, carried = sandbox
    at_read3(root, carried, winner_index=0, full_epoch=V.EPOCH_CAP)                 # the control: a constant rate, stopped by the cap
    with pytest.raises(SystemExit, match="within 10% of the cap") as refusal:
        V.cmd_read3()
    assert "The way out" in str(refusal.value) and f"{V.RERUN_CAP} epochs" in str(refusal.value)
    other_root = tmp_path_factory.mktemp("cosine")                                  # c03: the cosine ends at the cap by construction
    carried = make_module(other_root, monkeypatch)
    w = at_read3(other_root, carried, winner_index=3, full_epoch=V.EPOCH_CAP)
    assert w.schedule == "cosine"
    V.cmd_read3()
    assert f"{V.EPOCH_CAP} LATE" in (other_root / "m05" / V.OUT / "read3.md").read_text(encoding="utf-8")


def test_read3_reads_the_prediction_on_biphenylene(sandbox):
    root, carried = sandbox
    w = at_read3(root, carried, winner_index=0)
    V.cmd_read3()
    rec = json.loads((root / "m05" / V.OUT / "read3.json").read_text(encoding="utf-8"))
    assert rec["prediction"] == {"molecule": "A_72b86c2331", "winner": [2.0] * 3, "carried": [2.0] * 3, "line": 4.7, "passed": True}
    assert "**PASS**" in (root / "m05" / V.OUT / "read3.md").read_text(encoding="utf-8")
    for s in range(3):
        write_eval(root, "winner", 0.5, s, full_checkpoint(w, s), biphenylene=6.0 + s)
    V.cmd_read3()
    rec = json.loads((root / "m05" / V.OUT / "read3.json").read_text(encoding="utf-8"))
    report = (root / "m05" / V.OUT / "read3.md").read_text(encoding="utf-8")
    assert not rec["prediction"]["passed"] and rec["promotion"]["promoted"]         # a failed prediction leaves the promotion as read
    assert "winner 6.00, 7.00, 8.00 (mean 7.00), carried 2.00, 2.00, 2.00 (mean 2.00)" in report and "**FAIL**" in report
    rec_path = root / "m05" / V.OUT / "eval_carried_seed1.json"
    stripped = json.loads(rec_path.read_text(encoding="utf-8"))
    del stripped["a"]["per_molecule"]
    rec_path.write_text(json.dumps(stripped), encoding="utf-8")
    with pytest.raises(SystemExit, match="no corrected_freq_rms of A_72b86c2331"):
        V.cmd_read3()


def test_the_excluded_core_is_eight_of_the_selection_set():
    sets = V.selection_sets(SEL_IDS, NAMES)
    assert sets.all_ids == tuple(SEL_IDS) and sets.scored_ids == tuple(SEL_IDS[:161])
    assert len(sets.scored_ids) == V.N_SELECTION - V.N_EXCLUDED == 161
    assert sum(NAMES[i].startswith("fluoranthene") for i in sets.scored_ids) == 3   # only the named core leaves the score
    with pytest.raises(SystemExit, match="7 molecules of biphenylene among 168"):
        V.selection_sets(SEL_IDS[:-1], NAMES)                                       # another split
    with pytest.raises(SystemExit, match="9 molecules of biphenylene among 169"):
        V.selection_sets(SEL_IDS, {**NAMES, SEL_IDS[0]: "biphenylene+F"})           # another corpus
    with pytest.raises(SystemExit, match="8 molecules of biphenylene among 170"):
        V.selection_sets([*SEL_IDS, SEL_IDS[0]], NAMES)                             # an id twice
    with pytest.raises(SystemExit, match="without a manifest row"):
        V.selection_sets(SEL_IDS, {i: n for i, n in NAMES.items() if i != SEL_IDS[5]})


def test_a_selection_eval_is_made_once_checked_and_reused(sandbox, evaluator, monkeypatch):
    root, carried = sandbox
    V.cmd_plan(carried)
    pre = V.prefix(V.load_list()[0][0], "s1a")
    write_record(root, pre, {0: 0.1})
    first = V.seed_reads(pre)
    (argv,) = evaluator.calls
    assert argv[0] == sys.executable and argv[2:4] == [f"{pre}_model_n913_seed0.pt", f"{pre}_seleval_seed0.tmp"]
    assert [a for k, a in enumerate(argv) if argv[k - 1] == "--eval-ids-file"] == [
        f"{name}={V.OUT}/selection_{name}.ids" for name in (V.SEL_ALL, V.SEL_SCORED)]
    assert [len((root / "m05" / V.ids_file(name)).read_text(encoding="utf-8").split()) for name in (V.SEL_ALL, V.SEL_SCORED)] == [169, 161]
    record = root / "m05" / f"{pre}_seleval_seed0.json"
    assert record.is_file() and record.with_suffix(".md").is_file() and not list(record.parent.glob("*.tmp.*"))
    assert first[0].scored == json.loads(record.read_text(encoding="utf-8"))[V.SEL_SCORED] and first[0].sel == sel_read(0.1)
    assert V.seed_reads(pre) == first and len(evaluator.calls) == 1                 # the record is reused
    good = json.loads(record.read_text(encoding="utf-8"))
    off = {**good, V.SEL_ALL: {**good[V.SEL_ALL], P.RATIO: good[V.SEL_ALL][P.RATIO] + 0.01}}
    for bad, reason in ((off, "does not reproduce the trainer's selection score"),
                        ({**good, "model": f"{pre}_model_n913_seed1.pt"}, "not seed 0 of"),
                        ({**good, V.SEL_SCORED: good[V.SEL_ALL]}, f"its set {V.SEL_SCORED} is not the 161 molecules")):
        record.write_text(json.dumps(bad), encoding="utf-8")
        with pytest.raises(SystemExit, match=reason):
            V.seed_reads(pre)
    record.unlink()

    def failing(argv: list[str], log: Path) -> None:
        (root / "m05" / f"{argv[3]}.md").write_text("half a report", encoding="utf-8")
        raise SystemExit("the selection eval ended with exit 1")
    monkeypatch.setattr(V, "run_evaluator", failing)
    with pytest.raises(SystemExit, match="exit 1"):
        V.seed_reads(pre)
    assert not record.exists()                                                      # a failed evaluation leaves no record to reuse
    monkeypatch.setattr(V, "run_evaluator", evaluator)
    assert V.seed_reads(pre) == first and len(evaluator.calls) == 2                 # the next read makes it


def test_another_selection_set_in_a_record_is_refused(sandbox):
    root, carried = sandbox
    V.cmd_plan(carried)
    a, b = (V.prefix(c, "s1a") for c in V.load_list()[0][:2])
    write_record(root, a, {0: 0.1})
    write_record(root, b, {0: 0.1})
    V.seed_reads(a)
    rec = json.loads((root / "m05" / f"{b}.json").read_text(encoding="utf-8"))
    rec["holdout_sel"] = rec["holdout_sel"][::-1]
    (root / "m05" / f"{b}.json").write_text(json.dumps(rec), encoding="utf-8")
    with pytest.raises(SystemExit, match="do not share one split"):
        V.seed_reads(b)


def test_read1_ranks_on_the_scored_set_and_prints_the_registered_score(sandbox, evaluator):
    root, carried = sandbox
    V.cmd_plan(carried)
    configs, _ = V.load_list()
    shift = {c.name: 0.05 * k for k, c in enumerate(configs)}                       # the registered score: the later, the better
    lifted = configs[4].name                                                        # far from the registered leaders
    evaluator.gain = {lifted: 1.5}                                                  # … and the best once the excluded core is out
    for c in configs:
        write_record(root, V.prefix(c, "s1a"), {0: shift[c.name]})
        write_record(root, V.prefix(c, "s1b"), {1: shift[c.name]})
    V.cmd_read1()
    rec = json.loads((root / "m05" / V.OUT / "read1.json").read_text(encoding="utf-8"))
    registered_leaders = [c.name for c in configs[::-1][:V.STAGE2_BEST]]
    assert rec["stage2_registered"] == registered_leaders and rec["stage2"] == [lifted, *registered_leaders[:-1]]
    assert rec["scores"][lifted] < rec["registered_scores"][lifted] - 0.4
    assert all(rec["scores"][n] == pytest.approx(v) for n, v in rec["registered_scores"].items() if n != lifted)
    assert rec["registered_scores"][lifted] == pytest.approx(V.score(sel_read(shift[lifted])))
    report = (root / "m05" / V.OUT / "read1.md").read_text(encoding="utf-8")
    assert "| registered score (all 169) |" in report and "without biphenylene (161 of 169 molecules, §13)" in report
    assert f"**It would send other configurations to stage 2: {', '.join(registered_leaders)}.**" in report
    assert report.splitlines()[4].startswith(f"| 1 | {lifted} |")
    stage2_chain = json.loads((root / "probes" / "runs" / "v14_stage2.json").read_text(encoding="utf-8"))
    assert [s["argv"][3] for s in stage2_chain["steps"][:-1]] == [f"{V.OUT}/E7_rungC_v14s2_{n}" for n in ["c00_control", *rec["stage2"]]]
    assert len(evaluator.calls) == 2 * len(configs)                                 # one evaluation per stage checkpoint


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


def test_a_checkpoint_enters_the_registry_before_its_eval(sandbox, registry):
    """The real gate (`model_registry.require_carried`, the evaluator's first line) on a registry file of the test's own."""
    root, carried = sandbox
    V.cmd_plan(carried)
    pre = V.prefix(V.load_list()[0][0], "s1a")
    write_record(root, pre, {0: 0.1})
    model = f"{pre}_model_n913_seed0.pt"
    with pytest.raises(SystemExit, match="is not in the model registry"):           # unregistered: refused also with the exception
        MR.require_carried(root / "m05" / model, allow=True, status_file=registry)
    V.seed_reads(pre)                                                               # the stub's gate passed: the read registered it
    entry = MR.require_carried(root / "m05" / model, allow=True, status_file=registry)
    assert (entry["status"], entry["chain"], entry["network"]) == ("candidate", V.REGISTRY_CHAIN, MR.NETWORK_NAMES[0])
    with pytest.raises(SystemExit, match="has status 'candidate'"):                 # and it is no base for a read without the exception
        MR.require_carried(root / "m05" / model, status_file=registry)
    reviewed = json.loads(registry.read_text(encoding="utf-8"))
    reviewed[Path(model).name] = {**entry, "status": "invalid", "note": "reviewed"}
    registry.write_text(json.dumps(reviewed), encoding="utf-8")
    assert V.register_candidates([model]) == []                                     # a model with a status keeps it
    assert MR.status_of(root / "m05" / model, registry)["status"] == "invalid"


def test_register_enters_the_final_chains_six_checkpoints(sandbox, registry):
    root, carried = sandbox
    w = at_read3(root, carried, winner_index=0)
    other = V.replace(w, target="ls")
    for s in range(3):
        (root / "m05" / f"{V.prefix(other, 's3other')}_model_n913_seed{s}.pt").write_bytes(b"x")
    assert V.main(["register"]) == 0
    names = [Path(full_checkpoint(w, s)).name for s in range(3)] + [f"E7_rungC_v14s3other_{w.name}_model_n913_seed{s}.pt" for s in range(3)]
    assert sorted(json.loads(registry.read_text(encoding="utf-8"))) == sorted(names)
    assert MR.require_carried(root / "m05" / full_checkpoint(w, 1), allow=True, status_file=registry)["status"] == "candidate"
    assert V.main(["register"]) == 0                                                # a second run enters nothing and refuses nothing
    (root / "m05" / full_checkpoint(w, 2)).unlink()
    with pytest.raises(RuntimeError, match="matches 0 files"):                      # a training that saved no checkpoint stops the chain here
        V.main(["register"])


def test_seleval_makes_the_finished_trainings_evals_and_skips_the_rest(sandbox, evaluator, capsys):
    root, carried = sandbox
    V.cmd_plan(carried)
    configs, _ = V.load_list()
    for c in configs[:3]:
        write_record(root, V.prefix(c, "s1a"), {0: 0.1})
    write_record(root, V.prefix(configs[0], "s1b"), {1: 0.1})
    assert V.main(["seleval", "--only", configs[1].name]) == 0 and len(evaluator.calls) == 1
    out = capsys.readouterr().out
    assert f"selection eval E7_rungC_v14s1a_{configs[1].name}_seleval_seed0 made in " in out
    own = f"{V.score(sel_read(0.1)):.4f}"
    assert f"score on all 169 {own}, the trainer's {own}, difference 0.0e+00" in out
    assert "selection evals: 1 finished trainings read, 0 failed, 3 without a record" in out
    assert V.main(["seleval"]) == 0 and len(evaluator.calls) == 4                   # the three others; the first is reused
    assert f"{len(configs) * 4 - 4} without a record" in capsys.readouterr().out
    assert V.main(["seleval"]) == 0 and len(evaluator.calls) == 4
    with pytest.raises(SystemExit, match="not a configuration of the frozen list"):
        V.main(["seleval", "--only", "c99"])
    evaluator.all_shift = 0.1                                                       # an eval that does not reproduce the trainer's score
    write_record(root, V.prefix(configs[3], "s1a"), {0: 0.1})
    assert V.main(["seleval"]) == 1
    out = capsys.readouterr().out
    assert f"FAILED E7_rungC_v14s1a_{configs[3].name}: " in out and "The way out (§13)" in out and "5 finished trainings read, 1 failed" in out
    with pytest.raises(SystemExit, match="the tolerance is not loosened"):          # and read1 refuses the same record
        V.stage1_seeds(configs[3])


def test_the_registered_score_note_says_what_differs():
    assert V.registered_note(["a", "b"], ["a", "b"]) == " It sends the same configurations to stage 2, in the same order."
    assert V.registered_note(["a", "b"], ["b", "a"]) == " It sends the same configurations to stage 2, in another order: b, a."
    assert V.registered_note(["a", "b"], ["a", "c"]) == " **It would send other configurations to stage 2: a, c.**"


def test_read3_says_whether_the_expectation_of_more_data_held(sandbox):
    root, carried = sandbox
    w = at_read3(root, carried, winner_index=0)                                     # the winner's evals 0.4 below the carried ones'
    V.cmd_read3()
    rec = json.loads((root / "m05" / V.OUT / "read3.json").read_text(encoding="utf-8"))
    assert rec["expectation"]["a"]["held"] and rec["expectation"]["b"]["held"]
    for s in range(3):
        write_eval(root, "winner", 0.05, s, full_checkpoint(w, s))                  # now above the carried version on both
    V.cmd_read3()
    rec = json.loads((root / "m05" / V.OUT / "read3.json").read_text(encoding="utf-8"))
    report = (root / "m05" / V.OUT / "read3.md").read_text(encoding="utf-8")
    assert not rec["expectation"]["a"]["held"] and not rec["expectation"]["b"]["held"] and not rec["promotion"]["promoted"]
    assert "(expected below: **did not hold**)" in report and "(a) is looked at per molecule before the promotion is decided" in report
    assert "The expectation decides nothing; the no-worsening rule does." in report


def at_read_data(root: Path, carried: list[str], shift: float = 0.5, full_epoch: int = 100) -> V.Config:
    """Every file read-data reads (chain v14_data's): the control's whole-pool record and the six evals; the new models' read-outs lie
    `shift` below the lines, the carried version's 0.1."""
    V.cmd_plan(carried)
    w = V.load_list()[0][0]
    write_record(root, V.prefix(w, V.FULL_TAG), dict.fromkeys(range(3), 0.0), best_epoch=full_epoch, split=False)
    for s in range(3):
        write_eval(root, "data", shift, s, full_checkpoint(w, s), clean_shift=shift)
        write_eval(root, "carried_data", 0.1, s, carried[s], clean_shift=0.1)
    return w


def read_data_outputs(root: Path) -> tuple[dict, str]:
    base = root / "m05" / V.OUT / "read_data"
    return json.loads(base.with_suffix(".json").read_text(encoding="utf-8")), base.with_suffix(".md").read_text(encoding="utf-8")


def test_read_data_promotes_by_the_registered_rule_and_carries_nothing(sandbox, registry):
    root, carried = sandbox
    w = at_read_data(root, carried)
    assert w.name == "c00_control" and V.main(["read-data"]) == 0
    rec, report = read_data_outputs(root)
    new, old = (P.load_eval_arm([root / "m05" / V.OUT / f"eval_{who}_seed{s}.json" for s in range(3)], holdouts=("a8", "b"))
                for who in ("data", "carried_data"))
    assert rec["decided_on"] == ["a8", "b"] and "| (a8) | ring-ip |" in report and "| (a) | ring-ip |" in report
    registered = json.loads(json.dumps(V.asdict(P.promotion(P.compare(new, old)))))   # read3's calls, no other rule
    assert rec["promotion"] == registered and rec["promotion"]["promoted"]
    assert "\n".join(P.comparison_table(new, old, P.compare(new, old), "v1.4 candidate", "carried")) in report
    assert "**Promotion: promoted** — worse on none" in report and "By §14 these three models are version 1.4." in report
    assert "carries nothing itself and changes no registry entry" in report and not registry.exists()
    assert "- hold-out (b) below the carried version on the mean of three seeds: 2.51 against 2.91 — **PASS**" in report
    assert "- hold-out (a) not above the carried version on the mean of three seeds: 2.51 against 2.91 — **PASS**" in report
    assert ("- biphenylene (A_72b86c2331) on hold-out (a) at most 4.7 on the mean of three seeds: the new models 2.00, 2.00, 2.00 "
            "(mean 2.00), the carried version 2.00, 2.00, 2.00 (mean 2.00) — **PASS**") in report
    assert report.rstrip().endswith("`probes/product_error_read.py` and is not in this read.") and "the licence's quantity" in report
    with pytest.raises(SystemExit, match="the read is on record"):                  # never overwritten silently
        V.main(["read-data"])
    assert V.main(["read-data", "--replace"]) == 0 and read_data_outputs(root) == (rec, report)


def test_read_data_does_not_promote_a_model_worse_on_one_read_out(sandbox):
    root, carried = sandbox
    w = at_read_data(root, carried)
    for s in range(3):
        write_eval(root, "data", 0.5, s, full_checkpoint(w, s), biphenylene=6.0, clean_shift=0.5)
        path = root / "m05" / V.OUT / f"eval_data_seed{s}.json"
        rec = json.loads(path.read_text(encoding="utf-8"))
        rec["a8"] = {**rec["a8"], "diag_rms": {**rec["a8"]["diag_rms"], "CH-oop": 4.0}, "corrected_freq_rms": 3.5}
        path.write_text(json.dumps(rec), encoding="utf-8")
    V.cmd_read_data(replace_record=False)
    rec, report = read_data_outputs(root)
    (worse,) = rec["promotion"]["worse"]
    assert not rec["promotion"]["promoted"] and "CH-oop" in worse and "(a8)" in worse
    assert rec["on_the_ten_deciding_nothing"]["promotion"]["promoted"]              # the ten would have promoted: they do not decide
    assert f"**Promotion: not promoted** — worse on {worse}" in report
    assert "By §14 nothing is carried, and the cause is looked at per molecule before anything else is decided." in report
    assert "against 2.91 — **PASS**" in report                                      # (b) still below
    assert "three seeds: 3.50 against 2.91 — **FAIL**" in report                    # (a) above the carried version
    assert "the new models 6.00, 6.00, 6.00 (mean 6.00)" in report and report.count("**FAIL**") == 2


def test_read_data_refuses_the_wrong_models_and_missing_evals(sandbox):
    root, carried = sandbox
    w = at_read_data(root, carried)
    write_record(root, V.prefix(w, "s1a"), {0: 0.3})
    write_eval(root, "data", 0.5, 0, f"{V.prefix(w, 's1a')}_model_n913_seed0.pt")    # a stage checkpoint: trained with the split
    with pytest.raises(SystemExit, match="trained with --selection-split"):
        V.cmd_read_data(replace_record=False)
    write_eval(root, "data", 0.5, 0, full_checkpoint(w, 0))                          # an older record: the ten only
    with pytest.raises(SystemExit, match=r"eval_data_seed0\.json holds no set a8"):
        V.cmd_read_data(replace_record=False)
    write_eval(root, "data", 0.5, 0, full_checkpoint(w, 0), clean_shift=0.5)
    write_eval(root, "carried_data", 0.1, 2, carried[0], clean_shift=0.1)           # not the carried checkpoint of that seed
    with pytest.raises(SystemExit, match=r"not the carried version's out/carried_seed2\.pt"):
        V.cmd_read_data(replace_record=False)
    for name in ("eval_carried_data_seed2.json", "eval_data_seed1.json"):
        (root / "m05" / V.OUT / name).unlink()
        with pytest.raises(SystemExit, match=f"{name}: no eval record"):
            V.cmd_read_data(replace_record=False)
        write_eval(root, name[5:-11], 0.1, int(name[-6]), carried[2] if "carried" in name else None, clean_shift=0.1)
    assert not (root / "m05" / V.OUT / "read_data.json").exists()                   # no refusal left a report


def at_read_clean(root: Path, carried: list[str], twins: str = "drop-any-charge") -> V.Config:
    """read-data --arm clean's files: the control's whole-pool record at the clean tag, trained with `twins`, its three evals and the
    carried version's three."""
    V.cmd_plan(carried)
    w = V.load_list()[0][0]
    pre = V.prefix(w, V.CLEAN_TAG)
    write_record(root, pre, dict.fromkeys(range(3), 0.0), split=False)
    path = root / "m05" / f"{pre}.json"
    path.write_text(json.dumps(json.loads(path.read_text(encoding="utf-8")) | {"holdout_twins": twins}), encoding="utf-8")
    for s in range(3):
        write_eval(root, "clean", 0.5, s, f"{pre}_model_n1082_seed{s}.pt", clean_shift=0.5)
        write_eval(root, "carried_data", 0.1, s, carried[s], clean_shift=0.1)
    return w


def test_read_data_clean_arm_reads_the_any_charge_trainings_into_its_own_report(sandbox):
    """TASKS 253: the clean arm's prefix, evals and report are its own; the data arm's files are neither read nor written."""
    root, carried = sandbox
    w = at_read_clean(root, carried)
    assert V.prefix(w, V.CLEAN_TAG) == "out/v14/E7_rungC_v14s3clean_c00_control"
    assert V.main(["read-data", "--arm", "clean"]) == 0
    base = root / "m05" / V.OUT / "read_clean"
    rec, report = json.loads(base.with_suffix(".json").read_text(encoding="utf-8")), base.with_suffix(".md").read_text(encoding="utf-8")
    assert rec["arm"] == "clean" and rec["holdout_twins"] == "drop-any-charge" and rec["promotion"]["promoted"]
    assert report.startswith("# v1.4 on the data, clean arm (no hold-out twin of any charge) — the promotion read (design note §14)")
    assert "trained on the whole pool without any hold-out molecule's twin of any charge (--holdout-twins drop-any-charge" in report
    assert not (root / "m05" / V.OUT / "read_data.json").exists()
    with pytest.raises(SystemExit, match="the read is on record"):
        V.main(["read-data", "--arm", "clean"])


@pytest.mark.parametrize("twins", ["drop", "keep", None])
def test_read_data_clean_arm_refuses_trainings_without_drop_any_charge(sandbox, twins):
    root, carried = sandbox
    at_read_clean(root, carried, twins=twins)
    with pytest.raises(SystemExit, match=rf"v14s3clean_c00_control\.json was trained with holdout_twins {twins!r}, not 'drop-any-charge'"):
        V.cmd_read_data(replace_record=False, arm_name="clean")
    assert not (root / "m05" / V.OUT / "read_clean.json").exists()


def test_read_data_clean_arm_refuses_the_data_arms_evals(sandbox):
    root, carried = sandbox
    w = at_read_clean(root, carried)
    write_record(root, V.prefix(w, V.FULL_TAG), dict.fromkeys(range(3), 0.0), split=False)
    write_eval(root, "clean", 0.5, 0, full_checkpoint(w, 0), clean_shift=0.5)       # an s3full checkpoint under the clean arm's name
    with pytest.raises(SystemExit, match=r"eval_clean_seed0\.json evaluated .*v14s3full.*, not seed 0 of .*v14s3clean_c00_control"):
        V.cmd_read_data(replace_record=False, arm_name="clean")


def test_read_data_applies_the_cap_rule(sandbox):
    root, carried = sandbox
    at_read_data(root, carried, full_epoch=V.EPOCH_CAP)
    with pytest.raises(SystemExit, match="within 10% of the cap"):
        V.cmd_read_data(replace_record=False)


def test_read_data_decides_on_the_eight_clean_molecules_and_prints_the_ten(sandbox):
    root, carried = sandbox
    w = at_read_data(root, carried)
    for s in range(3):                                                              # worse on the ten (the twins), better on the eight
        path = root / "m05" / V.OUT / f"eval_data_seed{s}.json"
        rec = json.loads(path.read_text(encoding="utf-8"))
        rec["a"] = {**rec["a"], "diag_rms": {**rec["a"]["diag_rms"], "other": 4.0}, "corrected_freq_rms": 3.5}
        path.write_text(json.dumps(rec), encoding="utf-8")
    V.cmd_read_data(replace_record=False)
    rec, report = read_data_outputs(root)
    assert rec["promotion"]["promoted"] and rec["decided_on"] == [V.CLEAN_A, "b"]
    ten = rec["on_the_ten_deciding_nothing"]["promotion"]
    assert not ten["promoted"] and ten["worse"] == ["(a) other"]
    decides, beside = report.index("## The promotion: hold-out (a) on its eight clean molecules (a8)"), report.index("## Beside it, deciding nothing")
    assert decides < report.index("**Promotion: promoted**") < beside < report.index("| (a) | other | 4.00")
    assert "The eight decide (§14's addition of 16 Nov): the carried version trained on twins of two of the ten" in report
    assert "On the ten the same rule would read: not promoted, worse on (a) other" in report
    assert "By §14 these three models are version 1.4." in report
    assert "three seeds: 2.51 against 2.91 — **PASS**" in report and "3.50 against" not in report   # the expectation reads the eight
    assert w.name in report


def test_the_clean_sets_name_is_the_certificates():
    sys.path.insert(0, str(PLAN / "modules" / "08_industry_synthesis"))
    from m08 import accuracy
    assert V.CLEAN_A == accuracy.CLEAN_SET
    chain = json.loads((PLAN / "probes" / "runs" / "v14_data.json").read_text(encoding="utf-8"))
    evals = [s["argv"] for s in chain["steps"] if s["label"].startswith("eval ")]
    assert len(evals) == 6 and all(any(a.startswith(f"{V.CLEAN_A}=") for a in argv) for argv in evals)
