"""The checks before release networks are shipped (`probes/release_checks.py`; decision 66, design note of 17 Nov 2026, §4), and the
evaluator's one read of a release network (`rungC_eval_saved.py --insample-read`).

Each check's rule on made-up numbers; then the whole script and the evaluator on four small networks trained here on the frozen pin
corpus — two seeds of each kind, the whole pool, four epochs, one thread (about a minute). Those networks are mechanics, not results:
their four epochs end at the cap, so the script must refuse them by check 4 and still record every number of the other four."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

torch = pytest.importorskip("torch")
pytest.importorskip("rdkit")
from pin_tools import M05, PIN_CORPUS, PLAN, require_frozen_corpus, single_thread_env  # noqa: E402

sys.path.insert(0, str(PLAN / "probes"))
import release_checks as RC  # noqa: E402

NK = RC.NK
BENZENE, POOL_ANALYTIC, HELD_ANALYTIC = "A_8448043181", ["A_541c53d1a5", "A_e72997e726"], ["A_8448043181", "A_fdc27f1bd1"]
ARGS = {"lr": 3e-4, "epochs": 200, "patience": 20, "sizes": "all", "molecules": "corpus/molecules", "seeds": "0,1", "threads": 8}


def net(name: str, kind: str, seed: int, **kw) -> RC.Net:
    """A checkpoint as the checks read it, without a file: `args`, `train_ids`, `n`, `best_epoch`, `pool` and the record's kind may be given."""
    args = ARGS | {"out_prefix": f"out/{name}"} | ({NK.FIELD: kind} if kind == NK.RELEASE else {}) | kw.get("args", {})
    n = kw.get("n", 21 if kind == NK.RELEASE else 19)
    record = {"epochs": args["epochs"], "lr_schedule": kw.get("schedule", "constant"), "pool": kw.get("pool", n),
              "curve": {str(n): {"per_seed": [{"seed": seed, "best_epoch": kw.get("best_epoch", 120), "inner_val_ids": kw.get("stopped_on", [])}]}}}
    record |= kw.get("record", {NK.FIELD: kind})
    return RC.Net(path=Path(f"{name}_model_n{n}_seed{seed}.pt"), kind=kind, seed=seed, n=n, args=args,
                  train_ids=frozenset(kw.get("train_ids", POOL_ANALYTIC)), record=record)


def pair(**release_kw) -> tuple[tuple[RC.Net, ...], tuple[RC.Net, ...]]:
    return (tuple(net("V_rel", NK.RELEASE, s, **release_kw) for s in (0, 1)), tuple(net("V_meas", NK.MEASUREMENT, s) for s in (0, 1)))


def test_the_recipe_is_the_same_when_only_the_kind_and_the_runs_own_fields_differ():
    release, measurement = pair(args={"threads": 4, "seeds": "0"})
    check = RC.same_recipe(release, measurement)
    assert check.passed and check.refusal is None and list(check.numbers["differences"].values()) == [{}, {}]
    assert check.numbers["ignored"] == ["out_prefix", "threads", "seeds", "network_kind"]


def test_a_setting_that_differs_beside_the_kind_is_refused_with_its_name_and_count():
    release, measurement = pair(args={"lr": 1e-3, "patience": 30})
    check = RC.same_recipe(release, measurement)
    assert not check.passed and check.refusal == "4 setting(s) differ beside the kind: lr, patience"
    assert check.numbers["differences"]["V_rel_model_n21_seed0.pt"]["lr"] == {"measurement": 3e-4, "release": 1e-3}


def test_sizes_may_differ_only_where_the_measurement_network_trained_on_its_whole_pool():
    release = tuple(net("V_rel", NK.RELEASE, s) for s in (0, 1))
    whole = tuple(net("V_meas", NK.MEASUREMENT, s, args={"sizes": "19"}) for s in (0, 1))          # 19 of a pool of 19
    assert RC.same_recipe(release, whole).passed
    part = tuple(net("V_meas", NK.MEASUREMENT, s, args={"sizes": "19"}, pool=40) for s in (0, 1))  # 19 of a pool of 40
    check = RC.same_recipe(release, part)
    assert check.refusal == "2 setting(s) differ beside the kind: sizes" and not any(check.numbers["measurement_trained_on_its_whole_pool"].values())


def test_a_training_record_of_another_kind_than_its_checkpoint_is_refused():
    release, measurement = pair(record={})                                    # the release trainings' records state no kind
    check = RC.same_recipe(release, measurement)
    assert check.refusal.startswith("2 training record(s) state another kind than their checkpoint: V_rel_model_n21_seed0.pt")


@pytest.mark.parametrize(("kw", "passed", "read_as"), [({"best_epoch": 120}, True, "120"), ({"best_epoch": 180}, False, "180 AT CAP"),
                                                      ({"best_epoch": 199, "schedule": "cosine"}, True, "199 LATE"),
                                                      ({"best_epoch": None}, False, "None")])
def test_early_stopping_is_decision_51s_rule_from_the_search(kw, passed, read_as):
    release = (net("V_rel", NK.RELEASE, 0, **kw), net("V_rel", NK.RELEASE, 1))
    check = RC.early_stopping(release)
    row = check.numbers["seeds"]["V_rel_model_n21_seed0.pt"]
    assert check.passed is passed and row["read_as"] == read_as and row["cap"] == 200 and check.numbers["cap_margin"] == RC.V14.CAP_MARGIN
    assert row["at_cap"] == RC.V14.at_cap(RC.V14.SeedRead({}, {}, kw["best_epoch"], 200, {}), kw.get("schedule", "constant"))   # the one rule
    if not passed:
        assert check.refusal.startswith(f"1 release seed(s) stopped by the cap or trained without early stopping: V_rel_model_n21_seed0.pt "
                                        f"(best epoch {kw['best_epoch']} of 200)")


def config(release, measurement, tmp_path: Path, **kw) -> RC.Config:
    a8 = tmp_path / "a8.txt"
    a8.write_text("\n".join(kw.pop("listed", HELD_ANALYTIC)) + "\n", encoding="utf-8")
    return RC.Config(**({"release": release, "measurement": measurement, "molecules": PIN_CORPUS / "molecules", "holdouts": {"a8": a8},
                         "out": tmp_path / "record", "sample": 40, "threads": 1} | kw))


def test_what_cannot_be_checked_is_refused_before_a_molecule_is_read(tmp_path):
    release, measurement = pair()
    with pytest.raises(SystemExit) as e:
        RC.Config(release=measurement[:1], measurement=release, molecules=tmp_path / "none", holdouts={"b": tmp_path / "b.txt"},
                  out=tmp_path / "r", sample=0, threads=9)
    for reason in ("V_meas_model_n19_seed0.pt is a measurement network, named as a release one", "V_rel_model_n21_seed0.pt is a release network, named "
                   "as a measurement one", "the same seeds", "no corpus/molecules", "--holdout b: no file", "--threads 9", "--sample 0"):
        assert reason in str(e.value)
    with pytest.raises(SystemExit, match="at least two measurement seeds"):
        config(release[:1], measurement[:1], tmp_path)


def scaled_corrections(monkeypatch, scale: dict[str, float]) -> None:
    """Replace the networks by ΔH = scale · H_B3LYP, the scale by the checkpoint's stem and seed: every band moves by a known share."""
    def correction(models, folder):
        lo, _ = RC.low_hessian(folder)
        per_seed = [scale[m.name.partition("_model_")[0] + m.stem[-1]] * lo for m in models]
        return np.mean(per_seed, axis=0), per_seed

    monkeypatch.setattr(RC.P, "correction", correction)


def test_the_pool_sample_is_seeded_and_the_kinds_may_differ_as_the_seeds_do(tmp_path, monkeypatch):
    require_frozen_corpus()
    release, measurement = pair()
    cfg = config(release, measurement, tmp_path)
    assert RC.pool_sample((*release, *measurement), cfg.molecules, 40) == (POOL_ANALYTIC, 2)
    assert RC.pool_sample((*release, *measurement), cfg.molecules, 1) == RC.pool_sample((*release, *measurement), cfg.molecules, 1)
    scaled_corrections(monkeypatch, {"V_meas0": 0.010, "V_meas1": 0.012, "V_rel0": 0.011, "V_rel1": 0.011})
    check = RC.pool_agreement(cfg)
    rows = check.numbers["families"]
    assert check.passed and check.numbers["sample"] == POOL_ANALYTIC and check.numbers["drawn_from"] == 2
    assert all(v["difference"] < 1e-6 < v["seed_spread"] and v["n_bands"] > 0 for v in rows.values())      # equal seed means; the seeds differ
    scaled_corrections(monkeypatch, {"V_meas0": 0.010, "V_meas1": 0.012, "V_rel0": 0.030, "V_rel1": 0.030})
    check = RC.pool_agreement(cfg)
    assert not check.passed and check.refusal.startswith("the kinds differ by more than the measurement seeds do in 4 family(ies): ring-ip (")
    assert all(v["difference"] > v["seed_spread"] for v in check.numbers["families"].values())
    nowhere = tuple(net("V_rel", NK.RELEASE, s, train_ids=["B_01b90d2c0a"]) for s in (0, 1))                # no common molecule with labels
    assert RC.pool_agreement(config(nowhere, measurement, tmp_path)).refusal.startswith("no pool molecule that every network trained on")


def test_the_hold_outs_must_be_learnt_and_never_leaked(tmp_path, monkeypatch):
    require_frozen_corpus()
    everything = [*POOL_ANALYTIC, *HELD_ANALYTIC]
    release = tuple(net("V_rel", NK.RELEASE, s, train_ids=everything) for s in (0, 1))
    measurement = tuple(net("V_meas", NK.MEASUREMENT, s) for s in (0, 1))
    errors = {"V_rel": 1.0, "V_meas": 2.0}
    monkeypatch.setattr(RC, "family_errors", lambda ids, molecules, models: {
        f: {"rms": errors[models[0].name.partition("_model_")[0]] + (1.5 if f == "CH-oop" and "V_rel" in models[0].name else 0.0), "n_bands": 7}
        for f in RC.FAMILIES})
    check = RC.holdouts_learnt(config(release, measurement, tmp_path))
    assert check.refusal == ("1 hold-out reading(s) not below the measurement networks' or not readable: (a8) CH-oop: 2.500 in-sample against "
                             "2.000 cm⁻¹ held out")
    assert check.numbers["sets"]["a8"]["families"]["other"] == {"release": 1.0, "measurement": 2.0, "n_bands": 7}
    errors["V_rel"] = 0.4                                                      # every family below now (CH-oop 1.9 against 2.0)
    listed = [*HELD_ANALYTIC, "A2_02f13355a2"]                                # one listed molecule the release never trained on: named
    check = RC.holdouts_learnt(config(release, measurement, tmp_path, listed=listed))
    assert check.passed and check.numbers["sets"]["a8"]["dropped_not_in_the_release_training_data"] == ["A2_02f13355a2"]
    assert (check.numbers["sets"]["a8"]["n_listed"], check.numbers["sets"]["a8"]["n_read"]) == (3, 2)
    leaking = tuple(net("V_meas", NK.MEASUREMENT, s, train_ids=[*POOL_ANALYTIC, BENZENE]) for s in (0, 1))
    check = RC.holdouts_learnt(config(release, leaking, tmp_path))
    assert not check.passed and f"(a8) 1 molecule(s) are in a measurement network's training data ({BENZENE})" in check.refusal
    untrained = tuple(net("V_rel", NK.RELEASE, s) for s in (0, 1))
    assert "(a8) no listed molecule is in the release networks' training data" in RC.holdouts_learnt(config(untrained, measurement, tmp_path)).refusal


def test_benzene_is_reported_by_name_and_refused_when_the_release_did_not_train_on_it(tmp_path, monkeypatch):
    require_frozen_corpus()
    scaled_corrections(monkeypatch, {"V_meas0": 0.0, "V_meas1": 0.0, "V_rel0": 0.01, "V_rel1": 0.01})
    release, measurement = pair(train_ids=[*POOL_ANALYTIC, BENZENE])
    check = RC.benzene(config(release, measurement, tmp_path))
    bands = check.numbers["bands"]
    assert check.passed and check.numbers["molecule"] == BENZENE == RC.BENZENE and len(bands) == 30
    assert all(b["measurement"] == b["b3lyp"] and b["release"] > b["b3lyp"] for b in bands)      # ΔH = 0 gives B3LYP; a stiffer H, higher bands
    assert {b["family"] for b in bands} == set(RC.FAMILIES) and set(check.numbers["family_error"]) == set(NK.KINDS)
    assert check.numbers["in_training_data_of"] == {"release": [n.path.name for n in release], "measurement": []}
    assert check.numbers["previous_release"] == "none" and "previous_release" not in bands[0]      # a first release
    assert check.numbers["fitted_by_release_networks"] == [n.path.name for n in release]
    stopped = (release[0], net("V_rel", NK.RELEASE, 1, train_ids=[*POOL_ANALYTIC, BENZENE], stopped_on=[BENZENE]))   # seed 1 drew it for stopping
    assert RC.benzene(config(stopped, measurement, tmp_path)).numbers["fitted_by_release_networks"] == [release[0].path.name]
    previous = tuple(net("V_prev", NK.RELEASE, s) for s in (0, 1))
    scaled_corrections(monkeypatch, {"V_meas0": 0.0, "V_meas1": 0.0, "V_rel0": 0.01, "V_rel1": 0.01, "V_prev0": 0.02, "V_prev1": 0.02})
    beside = RC.benzene(config(release, measurement, tmp_path, previous=previous))
    assert beside.passed and beside.numbers["previous_release"] == [n.path.name for n in previous]
    assert all(b["previous_release"] > b["release"] > b["measurement"] for b in beside.numbers["bands"])
    assert set(beside.numbers["family_error"]) == {"measurement", "release", "previous_release"}
    record = {"date": "-", "passed": True, NK.RELEASE: [n.path.name for n in release], NK.MEASUREMENT: [], "checks": {
        name: {"passed": True, "refusal": None, "numbers": {"sample": [], "drawn_from": 0, "families": {}, "sets": {}}} for name in RC.CHECKS}}
    record["checks"]["benzene"]["numbers"] = beside.numbers
    assert "| B3LYP | family | ωB97X | measurement | release | previous release |" in RC.markdown(record)
    with pytest.raises(SystemExit, match=r"V_meas_model_n19_seed0\.pt is a measurement network, named as a release one"):
        config(release, measurement, tmp_path, previous=measurement)
    half = (release[0], net("V_rel", NK.RELEASE, 1))
    assert RC.benzene(config(half, measurement, tmp_path)).refusal == f"1 release network(s) did not train on {BENZENE}"
    empty = config(release, measurement, tmp_path, molecules=tmp_path)
    assert RC.benzene(empty).refusal.endswith("0 bands reported")


@pytest.fixture(scope="module")
def trained(tmp_path_factory):
    """Two seeds of each kind on the frozen corpus's whole pool, by the carried recipe without the analytic labels (every hold-out
    molecule then has labels of the one kind and enters the release pool), four epochs; a module-05 folder that holds the corpus."""
    pytest.importorskip("geometric")
    import chain_runner

    require_frozen_corpus()
    work = tmp_path_factory.mktemp("release_checks")
    m05 = work / "m05"
    shutil.copytree(PIN_CORPUS / "molecules", m05 / "corpus" / "molecules")
    shutil.copy(PIN_CORPUS / "manifest.csv", m05 / "corpus" / "manifest.csv")
    recipe = [a for a in chain_runner.BASE if a != "--use-analytic"] + [*chain_runner.RECIPE_V11, "--epochs", "4", "--patience", "2"]
    for stem, extra in (("V_meas", []), ("V_rel", ["--network-kind", "release"])):
        argv = [str(m05 / "corpus" / "molecules"), str(work / stem), *recipe, "--sizes", "all", "--seeds", "0,1", "--threads", "1", "--save-model",
                "--no-event-log", *extra]
        done = subprocess.run([sys.executable, str(M05 / "rungC_train.py"), *argv], env=single_thread_env(), stdin=subprocess.DEVNULL,
                              capture_output=True, text=True, encoding="utf-8", check=False)
        assert done.returncode == 0, done.stderr[-2000:]
    (work / "a8.txt").write_text("\n".join(HELD_ANALYTIC) + "\n", encoding="utf-8")
    return work, m05, sorted(work.glob("V_rel_model_n*_seed*.pt")), sorted(work.glob("V_meas_model_n*_seed*.pt"))


def test_the_script_records_every_number_and_refuses_networks_stopped_by_the_cap(trained, capsys):
    work, m05, release, measurement = trained
    argv = [*map(str, release), "--measurement", *map(str, measurement), "--m05", str(m05), "--holdout", f"a8={work / 'a8.txt'}", "--threads", "1"]
    assert RC.main(argv) == 1
    record = json.loads((work / "V_rel_release_checks.json").read_text(encoding="utf-8"))
    checks = record["checks"]
    assert record["passed"] is False and list(checks) == list(RC.CHECKS)
    assert any(r.startswith("check 4 (early_stopping): 2 release seed(s) stopped by the cap") for r in record["refusals"])
    assert "REFUSED check 4" in capsys.readouterr().out and len(record["refusals"]) == sum(not checks[c]["passed"] for c in RC.CHECKS)
    assert checks["same_recipe"]["passed"] and not checks["early_stopping"]["passed"] and checks["benzene"]["passed"]
    assert all(d == {} for d in checks["same_recipe"]["numbers"]["differences"].values()) and len(checks["same_recipe"]["numbers"]["differences"]) == 2
    assert set(checks["same_recipe"]["numbers"]["record_kinds"].values()) == set(NK.KINDS)
    # checks 2 and 3 on four-epoch networks: every number is there and the verdict is the numbers', whichever way these fall
    pool = checks["pool_agreement"]["numbers"]
    assert pool["sample"] == POOL_ANALYTIC and all(v["difference"] > 0 and v["seed_spread"] > 0 for v in pool["families"].values())
    assert checks["pool_agreement"]["passed"] is all(v["difference"] <= v["seed_spread"] for v in pool["families"].values())
    a8 = checks["holdouts_learnt"]["numbers"]["sets"]["a8"]
    assert a8["n_read"] == 2 and all(v["release"] > 0 and v["measurement"] > 0 for v in a8["families"].values())
    assert checks["holdouts_learnt"]["passed"] is all(v["release"] < v["measurement"] for v in a8["families"].values())
    benzene = checks["benzene"]["numbers"]
    assert len(benzene["bands"]) == 30 and benzene["in_training_data_of"] == {"release": [p.name for p in release], "measurement": []}
    assert benzene["previous_release"] == "none" and set(benzene["fitted_by_release_networks"]) <= {p.name for p in release}
    stopped_on = {s["seed"]: BENZENE in s["inner_val_ids"] for row in json.loads((work / "V_rel.json").read_text(encoding="utf-8"))["curve"].values()
                  for s in row["per_seed"]}
    assert len(benzene["fitted_by_release_networks"]) == sum(not v for v in stopped_on.values())       # the training record's own split
    assert sorted(record["model_sha16"]) == sorted(p.name for p in (*release, *measurement)) and record["run"]["peak_memory_gb"] > 0
    md = (work / "V_rel_release_checks.md").read_text(encoding="utf-8")
    assert "REFUSED: the release networks are not shipped" in md and "| 4 early_stopping | NO |" in md and f"## 5 Benzene ({BENZENE})" in md
    assert not list(work.glob("*.tmp"))


def test_the_script_refuses_the_kinds_the_wrong_way_round(trained):
    work, m05, release, measurement = trained
    with pytest.raises(SystemExit, match="is a measurement network, named as a release one"):
        RC.main([*map(str, measurement), "--measurement", *map(str, release), "--m05", str(m05), "--holdout", f"a8={work / 'a8.txt'}"])


def evaluate(monkeypatch, argv: list[str]) -> None:
    """The evaluator's own `main` on a checkpoint outside the registered folders: the registry gate is replaced, nothing else."""
    import rungC_eval_saved as ES

    monkeypatch.setattr(ES.MR, "require_carried", lambda path, allow=False, status_file=None, kind=None: {"status": "fixture"})
    monkeypatch.setattr(sys, "argv", ["rungC_eval_saved.py", *argv])
    assert ES.main() == 0


def test_the_evaluator_reads_a_release_network_in_sample_only_and_under_in_sample_names(trained, monkeypatch, capsys):
    import promotion_read as PR

    work, m05, release, measurement = trained
    corpus = ["--molecules", str(m05 / "corpus" / "molecules"), "--threads", "1"]
    with pytest.raises(SystemExit, match=r"is a release network \(decision 66\).*--insample-read"):
        evaluate(monkeypatch, [str(release[0]), str(work / "refused"), *corpus])
    assert not (work / "refused.json").exists()
    with pytest.raises(SystemExit, match="is a measurement network, whose read on a hold-out is a hold-out read"):
        evaluate(monkeypatch, [str(measurement[0]), str(work / "refused"), *corpus, "--insample-read"])
    for seed, model in enumerate(release):
        evaluate(monkeypatch, [str(model), str(work / f"insample{seed}"), *corpus, "--insample-read", "--eval-ids-file", f"a8={work / 'a8.txt'}"])
    record = json.loads((work / "insample0.json").read_text(encoding="utf-8"))
    sets = [k for k, v in record.items() if isinstance(v, dict) and "per_molecule" in v]
    assert sets == ["insample_a", "insample_b", "insample_a8"] and not {"a", "b", "b+", "a8"} & set(record)
    assert record[NK.FIELD] == NK.RELEASE and sorted(record["insample_a8"]["per_molecule"]) == sorted(HELD_ANALYTIC)
    assert "in-sample, not a hold-out error (decision 66)" in (work / "insample0.md").read_text(encoding="utf-8")
    with pytest.raises(NK.ReleaseNetworkError):                               # and no reader takes the record for an arm
        PR.load_eval_arm([work / "insample0.json", work / "insample1.json"], holdouts=("insample_a", "insample_b"))
    evaluate(monkeypatch, [str(measurement[0]), str(work / "held_out"), *corpus])
    held = json.loads((work / "held_out.json").read_text(encoding="utf-8"))
    assert held[NK.FIELD] == NK.MEASUREMENT and {"a", "b"} <= set(held) and not any(k.startswith(NK.INSAMPLE_PREFIX) for k in held)
    capsys.readouterr()


def test_a_measurement_pool_that_lost_its_twins_counts_as_whole():
    """n is read against the pool before the hold-out twins left it (v1.4: n1082, pool 1080): `all` is still what it trained on."""
    release = tuple(net("V_rel", NK.RELEASE, s) for s in (0, 1))
    twins = tuple(net("V_meas", NK.MEASUREMENT, s, args={"sizes": "21"}, n=21, pool=19) for s in (0, 1))
    check = RC.same_recipe(release, twins)
    assert check.passed and all(check.numbers["measurement_trained_on_its_whole_pool"].values())
