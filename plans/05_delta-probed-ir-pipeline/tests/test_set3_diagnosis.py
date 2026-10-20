"""probes/set3_diagnosis.py: the runs' command lines, the refusals, and the per-family summary on a synthetic record."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes"))
import set3_diagnosis as D

anchors_present = (D.SET3 / "manifest.json").exists()


@pytest.mark.skipif(not anchors_present, reason="needs anchor set three's manifest (git-ignored)")
def test_the_validation_run_repeats_arm_m_on_the_copied_corpus():
    argv = D.run_argv(D.VALIDATE, "out/x", Path("corpus/molecules"))
    assert argv[argv.index("--modes") + 1] == "head_l2" and argv[argv.index("--head-l2") + 1] == "1"
    assert [argv[n + 1] for n, x in enumerate(argv) if x == "--held"] == list(D.S3.NEW)
    assert sum(x == "--anchor" for x in argv) == 11 and argv[2] == str(Path("corpus/molecules"))


@pytest.mark.skipif(not anchors_present, reason="needs anchor set three's manifest (git-ignored)")
def test_each_experiment_runs_one_mode_on_its_base_model():
    for name, (mode, _extra, chain) in D.EXPERIMENTS.items():
        argv = D.run_argv(name, "out/x", Path("m"), seed=1)
        assert argv[argv.index("--modes") + 1] == mode and argv[3] == D.MODEL.format(chain=chain, seed=1), name
        assert ("--allow-any-model" in argv) == (chain != D.CHAIN34), name


def test_plan_refuses_without_the_corpus_and_unknown_names(tmp_path):
    with pytest.raises(SystemExit, match="missing"):
        D.plan(tmp_path, "t", ["E01_ref_lambda1"], [0])
    (tmp_path / "corpus" / "molecules").mkdir(parents=True)
    with pytest.raises(SystemExit, match="unknown"):
        D.plan(tmp_path, "t", ["E99"], [0])


def test_summary_splits_original_and_new_anchors():
    def col(oop, inten=None):
        c = {"freq_rms_by_family": {"CH-oop": oop, "other": 1.0, "ring-ip": 2.0, "CH-stretch": 3.0}, "coupling_ratio": 0.5}
        if inten is not None:
            c["intensity"] = {D.S3.MATCHED: inten}
        return c
    orig, new = next(iter(D.S3.ORIGINALS)), next(iter(D.S3.NEW))
    rec = {"folds": {orig: {"network_head_l2": col(10.0, 0.2), "zero_rule": col(20.0, 0.4)},
                     new: {"network_head_l2": col(4.0), "zero_rule": col(8.0)}}}
    s = D.summary(rec, "network_head_l2")
    assert s["CH-oop all"] == 7.0 and s["CH-oop orig"] == 10.0 and s["CH-oop new"] == 4.0
    assert s["intensity"] == pytest.approx(0.2) and s["intensity zero rule"] == pytest.approx(0.4) and s["ring ratio"] == 0.5
