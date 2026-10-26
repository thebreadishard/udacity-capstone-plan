"""probes/v14_search.py on synthetic records: the frozen list (deterministic, in range, every configuration a valid trainer command), the
plan's refusals, the score, the winner rule (no-worsening, two SE, the cap), and plan → read1 → read2 → read3 end to end."""
import json
import sys
from pathlib import Path

import pytest

pytest.importorskip("torch")
PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
sys.path.insert(0, str(PLAN / "modules" / "05_support_predictor" / "m05"))
import promotion_read as P  # noqa: E402
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
    a, b = V.draw("projected"), V.draw("projected")
    assert a == b and len(a) == V.N_DRAWN and len({c.name for c in a}) == V.N_DRAWN
    for c in a:
        for name in V.LOG_RANGES:
            lo, hi = V.SPACE[name]
            assert lo <= getattr(c, name) <= hi
        assert c.body_width in V.SPACE["body_width"] and c.hybrid_hidden in V.SPACE["hybrid_hidden"]
    assert {c.parity for c in a} == {True, False}


def test_the_control_is_the_carried_recipe():
    c = V.control("projected")
    assert (c.lr, c.weight_decay, c.body_width, c.body_blocks, c.hybrid_hidden, c.kring_weight, c.kdiag_weight, c.parity) == \
           (3e-4, 1e-4, 64, 3, 256, 0.3, 0.1, False)


@pytest.mark.parametrize("target", V.TARGETS)
def test_every_configuration_is_a_valid_trainer_command(target):
    for c in V.frozen_list(target):
        argv = V.trainer_argv(c, "out/x", "0")
        cfg = config_from_argv(argv[2:])                      # past '{python}' and the script; refusals raise here
        assert (cfg.lr, cfg.weight_decay, cfg.body_width, cfg.hybrid_hidden) == (c.lr, c.weight_decay, c.body_width, c.hybrid_hidden)
        assert cfg.parity_odd_mixed == c.parity and cfg.pair_features == (not c.parity) and cfg.aux_target == target
        assert cfg.pool_layers == V.POOL_LAYERS and cfg.selection_split == V.SELECTION and cfg.epochs == V.EPOCH_CAP
        assert argv.count("--lr") == 1


def test_score_is_one_on_the_lines():
    assert V.score(ON_LINES) == pytest.approx(1.0)


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
        V.cmd_plan("projected", ["out/nope.pt", *carried[1:]])
    V.cmd_plan("projected", carried)
    with pytest.raises(SystemExit, match="refusing to overwrite"):
        V.cmd_plan("projected", carried)


def test_an_edited_list_is_refused(sandbox):
    root, carried = sandbox
    V.cmd_plan("projected", carried)
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
    V.cmd_plan("projected", carried)
    configs, _ = V.load_list()
    stage1 = {c.name: 0.05 * k for k, c in enumerate(configs)}                      # the later the configuration, the better its score
    stage1["c00_control"] = 0.3
    for c in configs:
        write_record(root, V.prefix(c, "s1"), {0: stage1[c.name]})
    V.cmd_read1()
    chosen = json.loads((root / "m05" / V.OUT / "read1.json").read_text(encoding="utf-8"))["stage2"]
    assert chosen == [c.name for c in configs[::-1][:V.STAGE2_BEST]]
    assert json.loads((root / "probes" / "runs" / "v14_stage2.json").read_text(encoding="utf-8"))["steps"][-1]["argv"][-1] == "read2"
    for c in configs:
        if c.name in [*chosen, "c00_control"]:
            sh = stage1[c.name]
            write_record(root, V.prefix(c, "s2"), {1: sh + 0.01, 2: sh - 0.01})
    V.cmd_read2()
    best = json.loads((root / "m05" / V.OUT / "read2.json").read_text(encoding="utf-8"))["winner"]
    assert best == chosen[0]
    final = json.loads((root / "probes" / "runs" / "v14_final.json").read_text(encoding="utf-8"))
    assert final["steps"][0]["argv"].count("--aux-target") == 1 and any(s["argv"][2] == carried[0] for s in final["steps"][1:7])
    w = next(c for c in configs if c.name == best)
    other = V.replace(w, target="ls")
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
    V.cmd_plan("projected", carried)
    configs, _ = V.load_list()
    for k, c in enumerate(configs):
        write_record(root, V.prefix(c, "s1"), {0: 0.3 if k == 0 else 0.05 * k})
    V.cmd_read1()
    chosen = json.loads((root / "m05" / V.OUT / "read1.json").read_text(encoding="utf-8"))["stage2"]
    for k, c in enumerate(configs):
        if c.name in [*chosen, "c00_control"]:
            sh = 0.3 if k == 0 else 0.05 * k
            write_record(root, V.prefix(c, "s2"), {1: sh, 2: sh + 0.02}, best_epoch=V.EPOCH_CAP if c.name == chosen[0] else 100)
    with pytest.raises(SystemExit, match="within 10% of the cap"):
        V.cmd_read2()
