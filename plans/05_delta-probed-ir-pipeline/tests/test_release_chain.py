"""`probes/release_chain.py` (decision 66; review of 17 Nov 2026): the release chain as explicit command steps, built from the
measurement checkpoints' own saved arguments — on made-up checkpoint files; nothing is trained or launched. And
`rungC_config.argv_of`, the command line a config parses back from."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

torch = pytest.importorskip("torch")
PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
sys.path.insert(0, str(PLAN / "tools"))
import chain_runner  # noqa: E402
import release_chain as RL  # noqa: E402
import release_checks as RC  # noqa: E402
import runspec  # noqa: E402
from rungC_config import TrainConfig, argv_of, config_from_argv  # noqa: E402

NK = RL.NK
PREFIX = "out/v14/E7_carried"
CARRIED = ["corpus/molecules", PREFIX, *chain_runner.BASE, *chain_runner.RECIPE_V11, "--sizes", "all", "--save-model", "--pool-layers", "A,A2,B,P3,P3c"]


def measurement(m05: Path, prefix: str = PREFIX, seeds: tuple[int, ...] = (0, 1, 2), n: int = 1080, pool: int = 1080, **changed) -> None:
    """A measurement training as the generator finds it: one checkpoint per seed with the carried recipe's saved arguments, and the
    record beside them. `changed` alters the saved arguments (None removes one, as a checkpoint older than the setting)."""
    args = config_from_argv(CARRIED).resolved().model_dump(exclude={"event_log", "family_scale", "distortion_file", "selection_split"})
    args = {k: v for k, v in (args | {"out_prefix": prefix} | changed).items() if not (k in changed and v is None)}
    (m05 / Path(prefix).parent).mkdir(parents=True, exist_ok=True)
    for s in seeds:
        torch.save({"args": args, "n": n, "seed": s, "train_ids": ["A_x"]}, m05 / f"{prefix}_model_n{n}_seed{s}.pt")
    (m05 / f"{prefix}.json").write_text(json.dumps({"pool": pool}), encoding="utf-8")


def written(tmp_path: Path, *extra: str, prefixes: tuple[str, ...] = (PREFIX,)) -> tuple[dict, dict]:
    assert RL.main([*prefixes, "--m05", str(tmp_path / "m05"), "--out-dir", str(tmp_path), *extra]) == 0
    name = extra[extra.index("--name") + 1] if "--name" in extra else "release_E7_carried"
    return tuple(json.loads((tmp_path / "probes" / folder / f"{name}.json").read_text(encoding="utf-8")) for folder in ("runs", "runspecs"))


def test_a_config_is_written_back_as_the_command_that_gives_it():
    carried = config_from_argv(CARRIED)
    assert config_from_argv(argv_of(carried)) == carried and argv_of(carried)[:2] == ["corpus/molecules", PREFIX]
    assert argv_of(TrainConfig(molecules="m", out_prefix="o")) == ["m", "o"]                     # every default: no option
    odd = TrainConfig(molecules="m", out_prefix="o", head="hybrid", aux="both", save_model=True, event_log=False, lr=3e-5, sizes="all",
                      pretrained="b.pt", pretrained_elements=[1, 6, 7], selection_split="26:0.15", network_kind="measurement")
    line = argv_of(odd)
    assert config_from_argv(line) == odd and "--no-event-log" in line and line[line.index("--pretrained-elements") + 1] == "1,6,7"
    assert "--network-kind" not in line and "--save-model" in line


def test_the_chain_is_the_four_kinds_of_step_in_order(tmp_path):
    measurement(tmp_path / "m05")
    chain, _ = written(tmp_path)
    assert [s["label"] for s in chain["steps"]] == ["train release E7_carried_release", "register release candidates", "in-sample read seed 0",
                                                    "in-sample read seed 1", "in-sample read seed 2", "release checks"]
    assert all(s["kind"] == "cmd" and s["cwd"] == RL.M05_REL for s in chain["steps"]) and chain["name"] == RL.TAG
    assert chain["outputs"][-1] == f"{RL.M05_REL}/{PREFIX}_release_release_checks.json" and len(chain["outputs"]) == 5
    expanded = chain_runner.expand(chain, "python")                              # the runner takes it, and every pattern is expanded by it
    assert len(expanded) == 6 and all(bool(st.get("glob_args")) == any("*" in a for a in st["argv"]) for st in expanded)


def test_the_training_is_the_measurement_command_with_the_kind(tmp_path):
    measurement(tmp_path / "m05")
    train = written(tmp_path)[0]["steps"][0]
    assert train["argv"][:2] == ["{python}", "m05/rungC_train.py"] and "glob_args" not in train
    cfg, measured = config_from_argv(train["argv"][2:]), config_from_argv(CARRIED)
    differ = {k for k, v in cfg.model_dump().items() if v != measured.model_dump()[k]}
    assert differ == {"network_kind", "out_prefix"} and cfg.network_kind == NK.RELEASE
    assert (cfg.out_prefix, cfg.seeds, cfg.sizes, cfg.epochs, cfg.save_model) == (f"{PREFIX}_release", "0,1,2", "all", 200, True)
    # and release check 1 finds the two checkpoints' arguments the same recipe
    saved = torch.load(tmp_path / "m05" / f"{PREFIX}_model_n1080_seed0.pt", weights_only=False)["args"]
    kw = {"train_ids": frozenset(), "record": {NK.FIELD: None, "pool": 1080}}
    nets = [RC.Net(Path(f"{kind}_model_n1_seed{s}.pt"), kind, s, 1080, args, kw["train_ids"], {"pool": 1080} | ({NK.FIELD: kind} if kind == NK.RELEASE else {}))
            for kind, args in ((NK.RELEASE, cfg.resolved().model_dump(exclude={"event_log"})), (NK.MEASUREMENT, saved)) for s in (0, 1)]
    assert RC.same_recipe(tuple(nets[:2]), tuple(nets[2:])).refusal is None


def test_registration_and_reads_name_the_release_kind(tmp_path):
    measurement(tmp_path / "m05")
    steps = written(tmp_path)[0]["steps"]
    register, reads, checks = steps[1], steps[2:5], steps[5]
    release = [f"{PREFIX}_release_model_n*_seed{s}.pt" for s in (0, 1, 2)]
    assert register["glob_args"] and register["argv"][2:6] == ["--add-candidates", *release]
    assert register["argv"][register["argv"].index("--network-kind") + 1] == NK.RELEASE
    for s, read in enumerate(reads):
        argv = read["argv"]
        assert read["glob_args"] and argv[1:4] == ["../../probes/rungC_eval_saved.py", release[s], f"{PREFIX}_release_insample_seed{s}"]
        assert "--insample-read" in argv and "--use-analytic" in argv and "--allow-any-model" in argv
        assert argv[argv.index("--holdout-b-file") + 1] == chain_runner.HOLDOUT_B and argv[argv.index("--eval-ids-file") + 1] == f"a8={RL.CLEAN_A}"
        assert "_eval_" not in argv[3]                                           # the accuracy's glob for evaluation records must not find it
    measured = [f"{PREFIX}_model_n1080_seed{s}.pt" for s in (0, 1, 2)]
    assert checks["glob_args"] and checks["argv"][1:] == ["../../probes/release_checks.py", *release, "--measurement", *measured, "--threads", "2"]


def test_the_run_spec_is_valid_and_names_the_chain(tmp_path):
    measurement(tmp_path / "m05")
    _, spec = written(tmp_path, "--name", "release_v14")
    checked = runspec.RunSpec.model_validate(spec)
    assert checked.command == "python ../chain_runner.py probes/runs/release_v14.json" and checked.resumable and checked.dry_run_args == "--dry-run"
    assert checked.memory.peak_gb == RL.PEAK_GB and checked.estimate.hours == RL.HOURS and f"({RL.TAG})" in spec["end_regex"].replace("\\", "")


def test_an_older_checkpoints_absent_settings_are_written_out(tmp_path):
    """Seeds trained in two runs, by a trainer older than --holdout-twins and --lr-schedule: the release command says what they trained with."""
    measurement(tmp_path / "m05", seeds=(0, 1), holdout_twins=None, lr_schedule=None, network_kind=None)
    measurement(tmp_path / "m05", prefix="out/v14/E7_more", seeds=(2,), holdout_twins=None, lr_schedule=None, network_kind=None)
    train = written(tmp_path, prefixes=(PREFIX, "out/v14/E7_more"))[0]["steps"][0]["argv"]
    assert train[train.index("--holdout-twins") + 1] == "keep" and config_from_argv(train[2:]).seeds == "0,1,2"
    measurement(tmp_path / "m05", prefix="out/v14/E7_two", seeds=(0, 2))
    two = written(tmp_path, "--name", "release_two", prefixes=("out/v14/E7_two",))[0]["steps"]
    assert two[0]["argv"][two[0]["argv"].index("--seeds") + 1] == "0,2" and [s["label"] for s in two[2:4]] == ["in-sample read seed 0",
                                                                                                             "in-sample read seed 2"]


@pytest.mark.parametrize(("kw", "reason"), [
    ({"n": 750, "pool": 1080}, "trained on 750 of its pool's 1080 molecules"),
    ({"network_kind": "release"}, "is a release network; the chain is built from a version's measurement networks"),
    ({"selection_split": "26:0.15"}, "(?s)cannot be trained as release networks.*--selection-split"),
    ({"pool_layers": "A,B"}, "(?s)cannot be trained as release networks.*layers A and A2"),
])
def test_what_cannot_be_a_release_is_refused_and_nothing_is_written(tmp_path, kw, reason):
    measurement(tmp_path / "m05", **kw)
    with pytest.raises(SystemExit, match=reason):
        RL.main([PREFIX, "--m05", str(tmp_path / "m05"), "--out-dir", str(tmp_path)])
    assert not (tmp_path / "probes").exists()


def test_seeds_of_different_recipes_a_missing_prefix_and_an_existing_chain_are_refused(tmp_path):
    measurement(tmp_path / "m05", seeds=(0, 1))
    measurement(tmp_path / "m05", prefix="out/v14/E7_more", seeds=(2,), lr=1e-3)
    with pytest.raises(SystemExit, match=r"not one recipe.*settings that differ \['lr'\]"):
        RL.main([PREFIX, "out/v14/E7_more", "--m05", str(tmp_path / "m05"), "--out-dir", str(tmp_path)])
    with pytest.raises(SystemExit, match="no checkpoint"):
        RL.main([PREFIX, "out/v14/E7_none", "--m05", str(tmp_path / "m05"), "--out-dir", str(tmp_path)])
    written(tmp_path)
    with pytest.raises(SystemExit, match="exists, not overwritten"):
        RL.main([PREFIX, "--m05", str(tmp_path / "m05"), "--out-dir", str(tmp_path)])


def test_an_earlier_release_of_the_recipe_is_refused_by_name_and_nothing_is_written(tmp_path):
    measurement(tmp_path / "m05")
    (tmp_path / "m05" / f"{PREFIX}_release_model_n1082_seed0.pt").write_bytes(b"")
    with pytest.raises(SystemExit, match=r"a release of this recipe exists .*out/v14/E7_carried_release_model_n1082_seed0\.pt"):
        RL.main([PREFIX, "--m05", str(tmp_path / "m05"), "--out-dir", str(tmp_path)])
    assert not (tmp_path / "probes").exists()


def test_a_pool_that_lost_its_hold_out_twins_was_trained_on_whole(tmp_path):
    """`--sizes all` is read against the pool before the twins leave it: v1.4's n1082 on a pool of 1080 is the whole pool."""
    measurement(tmp_path / "m05", n=1082, pool=1080)
    assert written(tmp_path)[0]["steps"][0]["label"] == "train release E7_carried_release"
    assert NK.trained_on_whole_pool({"pool": 972}, 972) and not NK.trained_on_whole_pool({"pool": 972}, 750)    # v1.3: 750 of 972
    with pytest.raises(ValueError, match="states no pool size"):
        NK.trained_on_whole_pool({}, 750)


def ignored_record(rel: str) -> Path:
    """A training record under module 05's out/ with its (ignored) checkpoints beside it: this checkout's, or in a worktree the
    main checkout's (git's common directory)."""
    import subprocess

    common = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"], cwd=PLAN, capture_output=True, text=True,
                            check=True).stdout.strip()
    for root in (PLAN, Path(common).parent / PLAN.relative_to(PLAN.parents[1])):
        path = root / RL.M05_REL / rel
        if path.is_file() and any(path.parent.glob(f"{path.stem}_model_n*_seed*.pt")):
            return path
    pytest.skip(f"{rel}: no such record with its checkpoints in this checkout or the main one (they are ignored files)")


@pytest.mark.parametrize(("record", "n"), [("out/v14/E7_rungC_v14s3full_c00_control.json", 1082), ("out/E7_rungC_chain42_arm0.json", 978)])
def test_the_real_records_that_dropped_two_twins_trained_on_their_whole_pool(record, n):
    path = ignored_record(record)
    rec = json.loads(path.read_text(encoding="utf-8"))
    names = sorted(p.name for p in path.parent.glob(f"{path.stem}_model_n*_seed*.pt"))
    assert rec["sizes"] == [n] and names and all(f"_model_n{n}_seed" in name for name in names)
    assert rec["pool"] == n - len(rec["holdout_twins_dropped"]) == n - 2 and NK.trained_on_whole_pool(rec, n)
