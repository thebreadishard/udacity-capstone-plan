"""Decision 66 (17 Nov 2026): whatever reads a hold-out error refuses a release network, which trained on the hold-outs. The kind is
stored in the checkpoint's own arguments; the evaluator copies it into its record, and the readers of records refuse on that.

Here on made-up records and checkpoints: the evaluator's two refusals and its in-sample sets, the promotion arm, module 08's accuracy
and — through it — the licence, and the product-error read. The evaluator's whole run on trained release checkpoints is in
`test_release_checks.py`."""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

import pytest

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "modules" / "08_industry_synthesis"))
sys.path.insert(0, str(PLAN / "probes"))
sys.path.insert(0, str(PLAN / "modules" / "05_support_predictor" / "m05"))
import network_kind as NK  # noqa: E402
import promotion_read as PR  # noqa: E402

V13 = tuple(f"E7_rungC_chain35_analytic_model_n750_seed{s}.pt" for s in range(3))
REFUSAL = r"is a release network \(decision 66\)"


def eval_record(path: Path, kind: str | None) -> Path:
    """An evaluation record with the read-outs an arm needs, of the given kind (None: a record from before the decision)."""
    readout = {"diag_rms": dict.fromkeys(PR.FAMILIES, 2.0), PR.RATIO: 0.2}
    rec = {"model": "m.pt", "holdout_b_file": f"corpus/{PR.FROZEN_B}", "substituted_analytic": [], "a": readout, "b": readout}
    path.write_text(json.dumps(rec if kind is None else rec | {NK.FIELD: kind}), encoding="utf-8")
    return path


def test_a_promotion_arm_refuses_a_release_networks_record(tmp_path):
    old = [eval_record(tmp_path / f"old{s}.json", None) for s in range(2)]
    stated = [eval_record(tmp_path / f"m{s}.json", NK.MEASUREMENT) for s in range(2)]
    assert PR.load_eval_arm(old).mean("a", "other") == PR.load_eval_arm(stated).mean("a", "other") == 2.0
    with pytest.raises(NK.ReleaseNetworkError, match=rf"r1\.json {REFUSAL}.*an arm of its read-outs"):
        PR.load_eval_arm([stated[0], eval_record(tmp_path / "r1.json", NK.RELEASE)])


@pytest.fixture
def v13_records(tmp_path, monkeypatch):
    """v1.3's evaluation, clean hold-out (a) and product-error records, copied to a folder the accuracy reads instead of module 05's."""
    from m08 import accuracy as A

    names = [*A.evaluation_records(V13), *A.clean_a_records(V13), A.M05_OUT / f"E7_rungC_chain35_analytic{A.PRODUCT_SUFFIX}"]
    for p in names:
        shutil.copy(p, tmp_path / p.name)
    monkeypatch.setattr(A, "M05_OUT", tmp_path)
    return tmp_path


def state_kind(path: Path, kind: str) -> None:
    path.write_text(json.dumps(json.loads(path.read_text(encoding="utf-8")) | {NK.FIELD: kind}), encoding="utf-8")


@pytest.mark.parametrize(("record", "reading"), [("E7_rungC_chain35_analytic_eval_frozenb_seed1.json", "an arm of its read-outs"),
                                                 ("E7_rungC_chain35_analytic_a8read_seed2.json", "an arm of its read-outs"),
                                                 ("E7_rungC_chain35_analytic_product_error.json", "its product error on the hold-outs")])
def test_the_accuracy_and_the_licence_refuse_a_release_networks_record(v13_records, record, reading):
    """Each of the three kinds of record the accuracy reads; the licence has no other source than the accuracy, so it is refused too."""
    from m08 import accuracy as A
    from m08 import licence

    assert licence.state(A.accuracy_of(V13))["quantity"] == A.PRODUCT          # as copied: measurement networks, read as always
    state_kind(v13_records / record, NK.MEASUREMENT)
    assert licence.state(A.accuracy_of(V13))["quantity"] == A.PRODUCT          # stated: the same
    state_kind(v13_records / record, NK.RELEASE)
    with pytest.raises(NK.ReleaseNetworkError, match=rf"{record.replace('.', chr(92) + '.')} {REFUSAL}.*{reading}"):
        A.accuracy_of(V13)
    with pytest.raises(NK.ReleaseNetworkError, match=REFUSAL):
        licence.state(A.accuracy_of(V13))


def test_the_shape_read_refuses_a_release_networks_record(v13_records):
    from m08 import accuracy as A

    record = v13_records / "E7_rungC_chain35_analytic_eval_frozenb_seed0.json"
    state_kind(record, NK.RELEASE)
    with pytest.raises(NK.ReleaseNetworkError, match="its read-outs on the hold-outs"):
        A._records([record])


def checkpoint(path: Path, kind: str | None) -> Path:
    torch = pytest.importorskip("torch")
    torch.save({"args": {"lr": 1e-3} if kind is None else {"lr": 1e-3, NK.FIELD: kind}, "train_ids": ["A_x"]}, path)
    return path


def test_the_kind_is_read_from_the_checkpoint_itself(tmp_path):
    from m08 import pipeline as P

    models = (checkpoint(tmp_path / "old.pt", None), checkpoint(tmp_path / "m.pt", NK.MEASUREMENT), checkpoint(tmp_path / "r.pt", NK.RELEASE))
    assert P.network_kinds(models) == {"old.pt": NK.MEASUREMENT, "m.pt": NK.MEASUREMENT, "r.pt": NK.RELEASE}


def test_the_kinds_module_says_that_trained_on_is_not_fitted_on():
    assert "'Trained on' is not 'fitted on'" in NK.__doc__ and "stopped on the rest, a different part per seed" in NK.__doc__


def test_a_release_checkpoint_is_refused_as_a_measurement_whatever_the_registry_says(tmp_path):
    """`model_registry.require_measurement`: the one gate on the files themselves, for every script that reads an error."""
    import model_registry as MR

    measurement = checkpoint(tmp_path / "m.pt", NK.MEASUREMENT)
    MR.require_measurement((measurement, checkpoint(tmp_path / "old.pt", None)), "its product error on the hold-outs")
    with pytest.raises(SystemExit, match=rf"r\.pt {REFUSAL}.*its product error on the hold-outs"):
        MR.require_measurement((measurement, checkpoint(tmp_path / "r.pt", NK.RELEASE)), "its product error on the hold-outs")


def test_the_evaluator_refuses_a_release_network_without_its_flag_and_the_flag_on_a_measurement_network():
    pytest.importorskip("torch")
    import rungC_eval_saved as ES

    release, measurement = {"args": {NK.FIELD: NK.RELEASE}}, {"args": {}}
    assert ES.read_kind(measurement, "m.pt", insample=False) == NK.MEASUREMENT
    assert ES.read_kind(release, "r.pt", insample=True) == NK.RELEASE
    with pytest.raises(SystemExit, match=rf"r\.pt {REFUSAL}.*hold-outs \(a\) and \(b\).*--insample-read, written under 'insample_<set>'"):
        ES.read_kind(release, "r.pt", insample=False)
    with pytest.raises(SystemExit, match=r"--insample-read is the release networks' read.*m\.pt is a measurement network"):
        ES.read_kind(measurement, "m.pt", insample=True)


def options(tmp_path: Path, **kw) -> argparse.Namespace:
    return argparse.Namespace(**({"holdout_b_file": None, "eval_ids_file": [], "molecules": str(tmp_path)} | kw))


def test_a_release_networks_sets_carry_in_sample_names(tmp_path):
    pytest.importorskip("torch")
    import rungC_eval_saved as ES

    (tmp_path / "frozen.txt").write_text("b1\nb2\n", encoding="utf-8")
    (tmp_path / "a8.txt").write_text("# the clean eight\na1\ngone\n", encoding="utf-8")
    mols = dict.fromkeys(["a1", "a2", "b1", "b2", "b_new", "p1"], 0)
    held = {"a": ["a1", "a2"], "b": ["b1", "b2", "b_new"]}
    a = options(tmp_path, holdout_b_file=str(tmp_path / "frozen.txt"), eval_ids_file=[f"a8={tmp_path / 'a8.txt'}"])
    sets = ES.release_sets(a, mols, held, ["p1", "a1", "a2", "b1", "b2"], substituted=["a1"])
    assert [(name, ids) for name, ids, _ in sets] == [("insample_a", ["a1", "a2"]), ("insample_b", ["b1", "b2"]), ("insample_a8", ["a1"])]
    assert sets[2][2] == {"file": str(tmp_path / "a8.txt"), "dropped": ["gone"], "n_analytic": 1}
    assert not {name for name, _, _ in sets} & {"a", "b", "b+", "a8"}          # never a hold-out's own name, and no (b+)
    with pytest.raises(SystemExit, match=r"--insample-read \(b\): 1 of its 3 molecules are not in the network's training data \(b_new\)"):
        ES.release_sets(options(tmp_path), mols, held, ["p1", "a1", "a2", "b1", "b2"], substituted=[])   # derived (b): one never trained on
    with pytest.raises(SystemExit, match=r"--insample-read \(a\): 1 of its 2 molecules"):
        ES.release_sets(a, mols, held, ["p1", "a1", "b1", "b2"], substituted=[])
    (tmp_path / "none.txt").write_text("gone\n", encoding="utf-8")
    with pytest.raises(SystemExit, match=r"--insample-read \(x\): the set has no admitted molecule"):
        ES.release_sets(options(tmp_path, eval_ids_file=[f"x={tmp_path / 'none.txt'}"]), mols, held, ["a1", "a2", "b1", "b2", "b_new"], [])


def test_the_names_of_explicit_sets_are_checked_for_both_kinds(tmp_path):
    pytest.importorskip("torch")
    import rungC_eval_saved as ES

    (tmp_path / "s.txt").write_text("x1\n", encoding="utf-8")
    assert ES.listed_sets([f"s5={tmp_path / 's.txt'}"]) == {"s5": (str(tmp_path / "s.txt"), ["x1"])}
    for spec, reason in ((f"a={tmp_path / 's.txt'}", "is taken"), ("s5", "expected NAME=FILE"), (f"b+={tmp_path / 's.txt'}", "is taken")):
        with pytest.raises(SystemExit, match=reason):
            ES.listed_sets([spec])
    with pytest.raises(SystemExit, match="is taken"):
        ES.listed_sets([f"s5={tmp_path / 's.txt'}", f"s5={tmp_path / 's.txt'}"])
