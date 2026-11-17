"""Decision 66 (17 Nov 2026) in the trainer: `--network-kind release` puts hold-outs (a) and (b) and their twins into the training pool
and reads no hold-out; every option that holds molecules back or reads one is refused with it, before any data is loaded; a
measurement training is what it was (pinned to the bit by `test_rungC_train_regression.py`, whose golden gained the field only).

The run at the end trains a release network on the frozen pin corpus at mechanics size (`--smoke`: 5 molecules, 2 epochs, one thread)
and reads its record and its checkpoint."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "modules" / "05_support_predictor" / "m05"))
sys.path.insert(0, str(PLAN / "probes"))
import network_kind as NK  # noqa: E402
from rungC_config import TrainConfig, config_from_argv  # noqa: E402

RELEASE = {"network_kind": "release", "sizes": "all"}
REFUSED = [
    ({"selection_split": "7:0.15"}, "--network-kind release with --selection-split"),
    ({"size_test_min_atoms": 30}, "--network-kind release with --size-test-min-atoms"),
    ({"pool_max_atoms": 30}, "--network-kind release with --pool-max-atoms"),
    ({"exclude_ids_file": "ids.txt"}, "--network-kind release with --exclude-ids-file"),
    ({"split": "layerB"}, "--network-kind release with --split layerB"),
    ({"overfit_one": "A_x"}, "--network-kind release with --overfit-one"),
    ({"sizes": "45,100,175"}, "--network-kind release needs --sizes all"),
    ({"sizes": "half"}, "--network-kind release needs --sizes all"),
    ({"pool_layers": "A,B"}, "--network-kind release needs layers A and A2"),
    ({"pool_layers": "A2,B"}, "--network-kind release needs layers A and A2"),
]


def config(**kw) -> TrainConfig:
    return TrainConfig(molecules="mol", out_prefix="out", **kw)


def test_the_default_is_a_measurement_network_and_the_flag_parses():
    assert config().network_kind == NK.MEASUREMENT == config_from_argv(["mol", "out"]).network_kind
    assert config_from_argv(["mol", "out", "--network-kind", "release", "--sizes", "all"]).network_kind == NK.RELEASE
    with pytest.raises(SystemExit):
        config_from_argv(["mol", "out", "--network-kind", "both", "--sizes", "all"])
    with pytest.raises(ValueError, match="network_kind"):
        config(network_kind="both")


@pytest.mark.parametrize(("kw", "reason"), REFUSED)
def test_what_holds_molecules_back_or_reads_a_hold_out_is_refused_with_release(kw, reason):
    with pytest.raises(ValueError, match=reason):
        config(**(RELEASE | kw))
    config(**kw)                                             # the same option without release is today's behaviour, not refused


def test_every_release_conflict_is_listed_at_once():
    with pytest.raises(ValueError) as e:
        config(network_kind="release", selection_split="7:0.15", size_test_min_atoms=30, exclude_ids_file="ids.txt")
    assert all(flag in str(e.value) for flag in ("--selection-split", "--size-test-min-atoms", "--exclude-ids-file", "--sizes all"))


def test_the_carried_recipe_with_the_kind_is_a_valid_release_command():
    """The release command is the measurement command with the kind: the carried recipe, its inner validation, early stopping and
    either --holdout-twins value (a release pool keeps the twins whatever it says) are all accepted; so is a smoke of it."""
    import chain_runner

    recipe = ["mol", "out", *chain_runner.BASE, *chain_runner.RECIPE_V11, "--sizes", "all", "--save-model"]
    measurement, release = config_from_argv(recipe), config_from_argv([*recipe, "--network-kind", "release"])
    assert release.model_dump(exclude={"network_kind"}) == measurement.model_dump(exclude={"network_kind"})
    assert release.inner_val == 0.15 and release.patience == 20
    assert config_from_argv([*recipe, "--network-kind", "release", "--holdout-twins", "keep"]).holdout_twins == "keep"
    assert config_from_argv([*recipe, "--network-kind", "release", "--smoke"]).smoke


@pytest.fixture
def corpus(tmp_path):
    """Five molecules beside a manifest: the pool holds toluene twice — once as hold-out (a)'s twin under a layer-B id."""
    rows = [("A_tol", "Cc1ccccc1", "A"), ("B_tol", "c1ccccc1C", "B"), ("B_xyl", "Cc1ccccc1C", "B"), ("A2_naph", "Cc1cccc2ccccc12", "A2"),
            ("A2_fd", "Oc1cccc2ccccc12", "A2")]
    (tmp_path / "manifest.csv").write_text("id,smiles,layer\n" + "".join(f"{i},{s},{layer}\n" for i, s, layer in rows), encoding="utf-8")
    return tmp_path / "molecules"


def test_a_release_pool_takes_the_hold_outs_in_and_keeps_the_twins(corpus):
    pytest.importorskip("torch")
    pytest.importorskip("rdkit")
    import e6_learning_curve as E6
    import rungC_train as RT

    cfg = TrainConfig(molecules=str(corpus), out_prefix="out", use_analytic=True, **RELEASE)
    held = {"a": ["A_tol"], "b": ["A2_naph", "A2_fd"]}
    lines: list[str] = []
    pool, a, b, release = RT.kind_split(cfg, ["B_tol", "B_xyl"], held, ["A_tol", "A2_naph", "B_tol", "B_xyl"], lines.append)
    assert (a, b) == ([], []) and pool == sorted(["B_tol", "B_xyl", "A_tol", "A2_naph"], key=E6.sha)
    assert release == {"a": ["A_tol"], "b": ["A2_naph"], "twins": ["B_tol"], "left_out": ["A2_fd"]}     # no analytic labels: not trained on
    assert "pool 4" in lines[0] and "1 hold-out molecules without analytic labels" in lines[0] and "no hold-out is read" in lines[0]
    assert RT.drop_twins(cfg, pool, [], lines.append) == (pool, [])
    without_analytic = cfg.model_copy(update={"use_analytic": False})
    assert RT.kind_split(without_analytic, ["B_tol", "B_xyl"], held, [], lines.append)[3]["left_out"] == []   # one kind of label: all enter


def test_a_measurement_split_is_returned_as_it_came(corpus):
    pytest.importorskip("torch")
    import rungC_train as RT

    cfg = TrainConfig(molecules=str(corpus), out_prefix="out")
    pool, held = ["B_tol", "B_xyl"], {"a": ["A_tol"], "b": ["A2_naph"]}
    assert RT.kind_split(cfg, pool, held, [], None) == (pool, ["A_tol"], ["A2_naph"], {})
    assert RT.drop_twins(cfg, pool, ["A_tol"], lambda s: None) == (["B_xyl"], ["B_tol"])                # and the twin still leaves its pool


@pytest.fixture(scope="module")
def release_run(tmp_path_factory):
    """A release training on the frozen corpus at mechanics size, and the golden's measurement record of the same corpus."""
    pytest.importorskip("torch")
    pytest.importorskip("geometric")
    import chain_runner

    from pin_tools import DATA, M05, PIN_CORPUS, require_frozen_corpus, single_thread_env

    require_frozen_corpus()
    work = tmp_path_factory.mktemp("release")
    argv = [str(PIN_CORPUS / "molecules"), str(work / "release"), *chain_runner.BASE, *chain_runner.RECIPE_V11, "--smoke", "--threads", "1",
            "--seeds", "0", "--save-model", "--epochs", "2", "--no-event-log", "--sizes", "all", "--network-kind", "release"]
    done = subprocess.run([sys.executable, str(M05 / "rungC_train.py"), *argv], env=single_thread_env(), stdin=subprocess.DEVNULL,
                          capture_output=True, text=True, encoding="utf-8", check=False)
    assert done.returncode == 0, done.stderr[-2000:]
    golden = json.loads((DATA / "rungC_train_golden.json").read_text(encoding="utf-8"))["carried"]["record"]
    return work, json.loads((work / "release.json").read_text(encoding="utf-8")), golden, done.stdout


def test_a_release_record_says_its_kind_and_holds_no_hold_out(release_run):
    _, record, golden, _ = release_run
    assert record["network_kind"] == NK.RELEASE and golden["network_kind"] == NK.MEASUREMENT
    assert not {"holdout_a", "holdout_b", "holdout_s", "holdout_sel"} & set(record) and record["zero_rule"] == {}
    seeds = [s for row in record["curve"].values() for s in row["per_seed"]]
    assert len(seeds) == 1 and not {"a", "b", "s", "sel", "c"} & set(seeds[0])
    assert seeds[0]["inner_val_ids"] and seeds[0]["best_epoch"] is not None                             # inner validation as always
    assert record["holdout_twins_dropped"] == []


def test_a_release_pool_is_the_measurement_pool_and_its_hold_outs(release_run):
    """Against the measurement record of the same corpus: every hold-out molecule is in the pool or named as left out; the pool is
    the measurement pool, the twins it dropped and the hold-outs that entered — and nothing else."""
    _, record, golden, stdout = release_run
    took = record["release_pool"]
    for h in ("a", "b"):                                    # the golden's hold-outs are --smoke's first three; the release takes every one
        assert set(golden[f"holdout_{h}"]) <= set(took[h]) | set(took["left_out"])
    from pin_tools import PIN_CORPUS

    def analytic(i: str) -> bool:
        return (PIN_CORPUS / "molecules" / i / "hessian_wb97x_analytic.npz").is_file()

    entered = set(took["a"]) | set(took["b"])
    # the recipe reads analytic labels: the frozen corpus's hold-out (b) has none and is named, not trained on (as (b+) on the real one)
    assert took["a"] and took["left_out"] and all(analytic(i) for i in entered) and not any(analytic(i) for i in took["left_out"])
    assert set(took["twins"]) >= set(golden["holdout_twins_dropped"])
    assert entered <= set(record["pool_ids"]) and not set(took["left_out"]) & set(record["pool_ids"])
    assert set(record["pool_ids"]) == set(golden["pool_ids"]) | set(golden["holdout_twins_dropped"]) | entered
    assert record["pool"] == len(record["pool_ids"]) and "release networks (decision 66): pool" in stdout


def test_a_release_checkpoint_carries_its_kind(release_run):
    import torch

    work, record, _, _ = release_run
    saved = sorted(work.glob("release_model_n*_seed0.pt"))
    assert len(saved) == 1
    ck = torch.load(saved[0], map_location="cpu", weights_only=False)
    assert NK.kind_of_checkpoint(ck) == NK.RELEASE == ck["args"]["network_kind"]
    assert set(ck["train_ids"]) <= set(record["pool_ids"]) and len(ck["train_ids"]) == ck["n"]
    assert "no hold-out read (release networks, decision 66)" in (work / "release.md").read_text(encoding="utf-8")


def test_the_kind_of_what_predates_the_decision_is_measurement():
    assert NK.stated_kind({}, "an old record") == NK.MEASUREMENT == NK.kind_of_checkpoint({"args": {"lr": 1e-3}})
    assert NK.kind_of_checkpoint({"body_state": {}}) == NK.MEASUREMENT == NK.kind_of_checkpoint(None)
    assert NK.kind_of_checkpoint({"args": {"network_kind": "release"}}) == NK.RELEASE
    with pytest.raises(ValueError, match="one of"):
        NK.stated_kind({"network_kind": "shipping"}, "a record")
    NK.refuse_release(NK.MEASUREMENT, "m.pt", "its error on hold-out (a)")
    with pytest.raises(NK.ReleaseNetworkError, match=r"m\.pt is a release network \(decision 66\).*its error on hold-out \(a\)"):
        NK.refuse_release(NK.RELEASE, "m.pt", "its error on hold-out (a)")
