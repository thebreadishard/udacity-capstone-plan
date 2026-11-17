"""Decision 66, review of 17 Nov 2026: a carried release network passed `require_carried`, and five scripts that read an error or
fine-tune a base were gated on that alone or on nothing. Each now asks the checkpoint itself (`model_registry.require_measurement`)
before it reads a molecule; and the two comparisons of an old training with a new one share one table of settings added since
(`m05/rungC_settings_added.py`), so that the new `network_kind` — and any setting in the table — is read, by name, as what the old
training did."""
from __future__ import annotations

import inspect
import json
import subprocess
import sys
from pathlib import Path

import pytest

torch = pytest.importorskip("torch")
PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "modules" / "08_industry_synthesis"))
sys.path.insert(0, str(PLAN / "probes"))
sys.path.insert(0, str(PLAN / "modules" / "05_support_predictor" / "m05"))
import network_kind as NK  # noqa: E402
from rungC_settings_added import SETTINGS_ADDED, with_absent_settings  # noqa: E402

REFUSAL = r"r\.pt is a release network \(decision 66\)"


@pytest.fixture
def release(tmp_path) -> Path:
    path = tmp_path / "r.pt"
    torch.save({"args": {NK.FIELD: NK.RELEASE}, "train_ids": ["A_x"]}, path)
    return path


def test_the_engine_check_refuses_a_release_network_before_the_corpus(release, tmp_path):
    import engine_check as EC

    with pytest.raises(SystemExit, match=f"{REFUSAL}.*its error on the check's hold-out molecules"):
        EC.family_errors(tmp_path / "no_corpus", ["A_x"], [release])


def test_the_pipeline_against_the_corpus_refuses_a_release_runs_models(release, tmp_path):
    import pipeline_vs_corpus as PVC

    (tmp_path / "pipeline.json").write_text(json.dumps({"admission": {"models": [{"path": str(release)}]}}), encoding="utf-8")
    with pytest.raises(SystemExit, match=f"{REFUSAL}.*against the corpus's labels"):
        PVC.compare(tmp_path, tmp_path / "no_corpus")


def test_the_low_modes_read_refuses_a_release_network_before_the_corpus(release, tmp_path, monkeypatch):
    import rungC_low_modes_noise as LM

    def no_corpus(*args, **kwargs):
        raise AssertionError("the corpus was loaded before the network's kind was asked")

    monkeypatch.setattr(LM, "load_corpus", no_corpus)
    monkeypatch.setattr(sys, "argv", ["rungC_low_modes_noise.py", str(tmp_path / "out"), str(release)])
    with pytest.raises(SystemExit, match=rf"{REFUSAL}.*its error on hold-out \(a\)"):
        LM.main()


@pytest.mark.parametrize("module", ["rungC_cc_transfer", "proxy_transfer_check"])
def test_a_fine_tune_asks_its_bases_kind_before_it_loads_the_base(module):
    """The two fine-tune scripts' `main`: the registry gate, then the checkpoint's own kind, then anything else is read."""
    main = inspect.getsource(__import__(module).main)
    gate, kind = main.index("MR.require_carried("), main.index("MR.require_measurement(")
    assert gate < kind and all(kind < main.index(later) for later in ("load_hybrid_model(", "load_inputs(") if later in main)
    assert "load_hybrid_model(" in main or "load_inputs(" in main


def test_the_table_of_settings_added_is_one_and_names_what_it_fills():
    import epoch_repeat_check as ER
    import release_checks as RC

    assert ER.SETTINGS_ADDED is SETTINGS_ADDED and RC.with_absent_settings is with_absent_settings
    assert SETTINGS_ADDED == {"weight_decay": 1e-4, "holdout_twins": "keep", "lr_schedule": "constant", "network_kind": "measurement"}
    assert with_absent_settings({"lr": 1.0, "weight_decay": 3e-5}) == (
        {"lr": 1.0, "weight_decay": 3e-5, "holdout_twins": "keep", "lr_schedule": "constant", "network_kind": "measurement"},
        {"holdout_twins": "keep", "lr_schedule": "constant", "network_kind": "measurement"})


def repeat_run(tmp: Path, name: str, cap: int, rec: dict) -> Path:
    log = tmp / f"{name}.log"
    log.write_text(f"    seed 2 epoch 1/{cap}: loss main 1e-07 aux 0.01 val 0.4041 (27 s)\n", encoding="utf-8")
    log.with_suffix(".json").write_text(json.dumps(rec), encoding="utf-8")
    return log


def test_a_re_run_under_todays_trainer_is_not_a_changed_setting(tmp_path):
    """Finding B: the record gained `network_kind` (and `lr_schedule` two days earlier); an old run against its re-run reported
    `setting network_kind: '<absent>' -> 'measurement'`. A release re-run of a measurement run is still a changed setting."""
    old = {"pool_ids": ["B_1"], "holdout_a": ["A_9"], "holdout_b": ["B_8"], "sizes": [750], "seeds": [0, 1, 2], "epochs": 200, "lr": 3e-4,
           "curve": {"750": {"per_seed": [{"seed": 2, "inner_val_ids": ["B_1"]}]}}}
    new = old | {"epochs": 500, "seeds": [2], "holdout_twins": "keep", "holdout_twins_dropped": [], "weight_decay": 1e-4,
                 "lr_schedule": "constant", "network_kind": "measurement"}
    script = PLAN / "probes" / "epoch_repeat_check.py"

    def run(record: dict) -> subprocess.CompletedProcess:
        logs = [str(repeat_run(tmp_path, "old", 200, old)), str(repeat_run(tmp_path, "new", 500, record))]
        return subprocess.run([sys.executable, str(script), *logs, "--seed", "2"], capture_output=True, text=True, check=False, encoding="utf-8")

    same = run(new)
    assert same.returncode == 0 and "REPEAT OK" in same.stdout, same.stdout + same.stderr
    released = run(new | {"network_kind": "release"})
    assert released.returncode == 1 and "setting network_kind: 'measurement' -> 'release'" in released.stdout
    cosine = run(new | {"lr_schedule": "cosine"})
    assert cosine.returncode == 1 and "setting lr_schedule: 'constant' -> 'cosine'" in cosine.stdout


def test_check_1_reads_an_absent_setting_by_the_table_and_says_so():
    """An older measurement checkpoint holds no `lr_schedule` or `weight_decay`: read as the table's values, named in the record. Its
    absent `holdout_twins` is 'keep' — what it trained with — so a release at today's default 'drop' is a difference; a setting
    outside the table that one side lacks is a difference too."""
    import release_checks as RC

    from test_release_checks import net

    older = {"weight_decay": None, "lr_schedule": None}

    def measurement(extra: dict) -> tuple[RC.Net, ...]:
        nets = tuple(net("V_meas", NK.MEASUREMENT, s, args=extra) for s in (0, 1))
        return tuple(RC.Net(n.path, n.kind, n.seed, n.n, {k: v for k, v in n.args.items() if k not in older}, n.train_ids, n.record) for n in nets)

    today = {"weight_decay": 1e-4, "lr_schedule": "constant", "holdout_twins": "keep"}
    release = tuple(net("V_rel", NK.RELEASE, s, args=today) for s in (0, 1))
    check = RC.same_recipe(release, measurement({"holdout_twins": "keep"}))
    assert check.passed, check.refusal
    assert check.numbers["absent_settings_read_as"]["V_meas_model_n19_seed0.pt"] == {"weight_decay": 1e-4, "lr_schedule": "constant",
                                                                                     "network_kind": "measurement"}
    assert check.numbers["absent_settings_read_as"]["V_rel_model_n21_seed0.pt"] == {}
    dropped = tuple(net("V_rel", NK.RELEASE, s, args=today | {"holdout_twins": "drop"}) for s in (0, 1))
    assert RC.same_recipe(dropped, measurement({})).refusal == "2 setting(s) differ beside the kind: holdout_twins"
    assert RC.same_recipe(release, measurement({"holdout_twins": "keep", "pattern": "f"})).refusal == "2 setting(s) differ beside the kind: pattern"
