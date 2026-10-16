"""The rung-C trainer's settings (TASKS 72, 16 Oct 2026): every option that would do nothing in a combination is refused before any data is
loaded, the defaults are the registered recipe C1, and every trainer command a chain spec builds still parses — a new refusal must not break
a queued chain."""
import json
import sys
from pathlib import Path

import pytest

pytest.importorskip("torch")
PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "modules" / "05_support_predictor" / "m05"))
sys.path.insert(0, str(PLAN / "probes"))
import chain_runner  # noqa: E402
import rungC_train as RT  # noqa: E402
from rungC_config import AUX_WEIGHT, EPOCHS, SMOKE_EPOCHS, TrainConfig, config_from_argv, parse_config  # noqa: E402
from rungC_equivariant import N_BLOCKS, N_S  # noqa: E402
from rungC_targets import LAM_REL  # noqa: E402

RUNS = PLAN / "probes" / "runs"


def config(**kw) -> TrainConfig:
    return TrainConfig(molecules="mol", out_prefix="out", **kw)


def test_defaults_are_the_registered_recipe_c1():
    cfg = parse_config(["mol", "out"])
    assert (cfg.head, cfg.aux, cfg.pattern, cfg.aux_target, cfg.lr, cfg.aux_weight) == ("cartesian", "all", "c", "projected", 1e-3, AUX_WEIGHT)
    assert (cfg.inner_val, cfg.patience, cfg.body_blocks, cfg.body_width, cfg.ls_lam) == (0.0, 0, N_BLOCKS, N_S, LAM_REL)
    assert cfg.epochs is None and cfg.resolved().epochs == EPOCHS
    assert parse_config(["mol", "out", "--smoke"]).resolved().epochs == SMOKE_EPOCHS
    assert parse_config(["mol", "out", "--smoke", "--epochs", "3"]).resolved().epochs == 3


def test_the_carried_recipe_parses():
    cfg = parse_config(["mol", "out", *chain_runner.BASE, *chain_runner.RECIPE_V11, "--save-model"])
    assert (cfg.head, cfg.pattern, cfg.aux, cfg.patience, cfg.inner_val, cfg.save_model) == ("hybrid", "f", "both", 20, 0.15, True)


def chain_trainer_commands() -> list[tuple[str, list[str]]]:
    """(chain spec, trainer arguments) for every rung-C training any chain spec in probes/runs builds."""
    out = []
    for spec_path in sorted(RUNS.glob("*.json")):
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
        for step in spec.get("steps", []):
            if step.get("kind") != "rungc":
                continue
            for built in chain_runner.rungc_steps(step, "python"):
                argv = built["argv"]
                if "m05/rungC_train.py" in argv:
                    out.append((f"{spec_path.name}: {built['label']}", argv[argv.index("m05/rungC_train.py") + 1:]))
    return out


def test_chain_specs_exist_with_trainings():
    assert len(chain_trainer_commands()) >= 5


@pytest.mark.parametrize(("where", "argv"), chain_trainer_commands(), ids=lambda x: x if isinstance(x, str) else "")
def test_every_queued_chain_training_still_parses(where, argv):
    """Combinations only: a chain's input files resolve in its step's folder, and an earlier step may write them."""
    config_from_argv(argv)


@pytest.mark.parametrize(("kw", "reason"), [
    ({"head": "hybrid"}, "--head hybrid needs --aux pattern, kring or both"),
    ({"sqm_scale": True}, "--sqm-scale works only with --head hybrid"),
    ({"pair_features": True}, "--pair-features works only with --head hybrid"),
    ({"parity_odd_mixed": True}, "--parity-odd-mixed works only with --head hybrid"),
    ({"hinge_feature": True}, "--hinge-feature works only with --head hybrid"),
    ({"save_model": True}, "--save-model works only with --head hybrid"),
    ({"hybrid_hidden": 256}, "--hybrid-hidden sets the width of the hybrid head"),
    ({"head": "hybrid", "aux": "both", "pair_features": True, "parity_odd_mixed": True}, "--parity-odd-mixed with --pair-features"),
    ({"head": "hybrid", "aux": "both", "scale": "class"}, "--scale class sets the Cartesian head's output scale"),
    ({"aux": "pattern", "kdiag_weight": 0.1}, "inside --aux both only"),
    ({"aux": "kring", "kring_weight": 0.3}, "inside --aux both only"),
    ({"aux": "both", "kdiag_mode": "family"}, "--kdiag-mode chooses the form"),
    ({"aux": "kring", "aux_target": "ls"}, "--aux-target replaces the pattern term's target"),
    ({"ls_lam": 0.01}, "--ls-lam is the ridge of the ls/kfit targets"),
    ({"loss": "internal", "aux_weight": 1.0}, "--loss internal trains on the internal term alone"),
    ({"patience": 20}, "--inner-val 0 has none"),
    ({"pretrained": "x.pt", "tensor_input": True}, "--tensor-input is a fresh-body variant"),
    ({"pretrained": "x.pt", "body_width": 32}, "do not fit a pretrained body"),
    ({"pretrained_elements": [1, 6]}, "--pretrained-elements describes a --pretrained checkpoint"),
    ({"split": "layerB", "size_test_min_atoms": 30}, "--split layerB builds its own pool"),
    ({"split": "layerB", "exclude_ids_file": "ex.txt"}, "--split layerB builds its own pool"),
    ({"smoke": True, "overfit_one": "A_1"}, "--smoke and --overfit-one"),
])
def test_a_combination_that_would_do_nothing_is_refused(kw, reason):
    with pytest.raises(ValueError, match=reason.replace("(", r"\(").replace(")", r"\)")):
        config(**kw)


def test_every_conflict_is_listed_at_once():
    with pytest.raises(ValueError) as e:
        config(save_model=True, patience=5, ls_lam=0.01)
    assert all(s in str(e.value) for s in ("--save-model", "--patience", "--ls-lam"))


def test_values_are_checked():
    for kw in ({"sizes": "45,ten"}, {"sizes": "0"}, {"seeds": "0,a"}, {"aggregation": "max"}, {"split": "layerC"}, {"inner_val": 1.0},
               {"lr": 0.0}, {"no_such_option": 1}):
        with pytest.raises(ValueError):
            config(**kw)
    assert config(sizes="45,half,all").sizes == "45,half,all"


def test_config_is_frozen():
    cfg = config()
    with pytest.raises(ValueError):
        cfg.aux = "pattern"


def test_missing_input_files_are_refused_before_loading(tmp_path, capsys):
    with pytest.raises(SystemExit):
        parse_config(["mol", "out", "--head", "hybrid", "--aux", "both", "--pretrained", str(tmp_path / "none.pt")])
    assert "--pretrained" in capsys.readouterr().err
    ok = tmp_path / "ex.txt"
    ok.write_text("A_1\n", encoding="utf-8")
    assert parse_config(["mol", "out", "--exclude-ids-file", str(ok)]).missing_files() == []


def test_overfit_one_resolves_to_its_diagnostic_recipe():
    cfg = config(overfit_one="A_1", inner_val=0.15, patience=20).resolved()
    assert (cfg.inner_val, cfg.patience, cfg.epochs) == (0.0, 0, EPOCHS)


def test_pretrained_elements_are_parsed_to_integers():
    assert parse_config(["mol", "out", "--pretrained", __file__, "--pretrained-elements", "1,6,7"]).pretrained_elements == [1, 6, 7]


def test_train_one_needs_a_resolved_config():
    with pytest.raises(ValueError, match="resolved"):
        RT.train_one(["w"], {}, 0, config())


def test_loss_settings_refuse_a_pattern_term_without_scales():
    with pytest.raises(ValueError, match="class_scale is required"):
        RT.LossSettings(mode="both")
    with pytest.raises(ValueError, match="aux mode"):
        RT.LossSettings(mode="ring")
