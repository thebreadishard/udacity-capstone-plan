"""Chain 41's run tooling (13 Oct 2026): the id files written from the frozen set file, the registered read (q5 = r_S / r_K with r_K the mean of
the two folds' ratios, fixed before any number) and the generic wait condition on analytic labels."""
import json
import sys
from pathlib import Path

import numpy as np

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
import chain41_prepare as P  # noqa: E402
import chain41_read as R  # noqa: E402
import ids_have_labels as L  # noqa: E402


def _rec(**sets):
    return {k: {"coupling_ratio": v, "corrected_freq_rms": 5.0, "corrected_freq_rms_zero_rule": 9.0, "per_molecule": {}} for k, v in sets.items()}


def test_the_read_pools_the_folds_by_their_mean_and_applies_the_lines():
    size = [_rec(s5=0.60, s4N=0.40)] * 3
    res = R.read(size, [_rec(s5=0.30)] * 3, [_rec(s5=0.50)] * 3)
    assert np.isclose(res["r_K"], 0.40) and np.isclose(res["q5"], 1.5) and res["verdict"].startswith("between")
    assert R.verdict(1.3).startswith("carries") and R.verdict(1.8).startswith("steep") and np.isclose(res["beside"]["size_arm_s4N"], 0.40)


def test_the_id_files_follow_the_frozen_set_file():
    d = json.load(open(P.SRC, encoding="utf-8"))
    ls = P.lists(d)
    assert len(ls["s5"]) == 30 and len(ls["s4N"]) == 30 and len(ls["all_labelled"]) == 60
    assert not set(ls["fold1_test"]) & set(ls["fold2_test"]) and set(ls["fold1_test"]) | set(ls["fold2_test"]) == set(ls["s5"])
    assert not set(ls["fold1_test"]) & (set(d["control_fold1"]["train_extra"]))


def test_ids_have_labels_names_what_is_missing(tmp_path):
    (tmp_path / "X").mkdir()
    for f in L.NEEDED:
        (tmp_path / "X" / f).write_text("{}")
    (tmp_path / "Y").mkdir()
    (tmp_path / "Y" / "geometry.json").write_text("{}")
    assert L.missing(["X", "Y", "Z"], tmp_path) == {"Y": ["hessian_b3lyp_analytic.npz", "hessian_wb97x_analytic.npz"], "Z": list(L.NEEDED)}


def test_a_set_that_lost_molecules_is_not_read():
    import pytest
    size = [_rec(s5=0.6, s4N=0.4)] * 3
    bad = [dict(_rec(s5=0.3), s5={**_rec(s5=0.3)["s5"], "dropped": ["P3_x"]})] * 3
    with pytest.raises(SystemExit, match="lost 1 registered"):
        R.read(size, bad, [_rec(s5=0.5)] * 3)
