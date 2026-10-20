"""Chain 41's run tooling (13 Oct 2026): the id files written from the frozen set file, the registered read (q5 = r_S / r_K with r_K the mean of
the two folds' ratios, fixed before any number) and the generic wait condition on analytic labels."""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
import chain41_prepare as P  # noqa: E402
import chain41_read as R  # noqa: E402
import ids_have_labels as L  # noqa: E402


def _rec(diag=None, **sets):
    diag = diag or dict.fromkeys(R.FAMILIES, 2.0)
    return {k: {"coupling_ratio": v, "corrected_freq_rms": 5.0, "corrected_freq_rms_zero_rule": 9.0, "per_molecule": {}, "diag_rms": diag}
            for k, v in sets.items()}


def test_the_read_pools_the_folds_by_their_mean_and_applies_the_lines():
    size = [_rec(s5=0.60, s4N=0.40)] * 3
    res = R.read(size, [_rec(s5=0.30)] * 3, [_rec(s5=0.50)] * 3)
    assert np.isclose(res["r_K"], 0.40) and np.isclose(res["q5"], 1.5) and res["verdict"].startswith("between")
    assert R.verdict(1.3).startswith("carries") and R.verdict(1.8).startswith("steep") and np.isclose(res["beside"]["size_arm_s4N"], 0.40)


def test_the_four_families_are_read_per_arm_and_required():
    size = [_rec(diag={"CH-stretch": 3.0 + s, "CH-oop": 5.0, "ring-ip": 4.0, "other": 5.0}, s5=0.4, s4N=0.3) for s in (0.0, 0.3, 0.6)]
    res = R.read(size, [_rec(s5=0.4)] * 3, [_rec(s5=0.4)] * 3)
    fam = res["beside"]["family_rms_s5"]
    assert np.isclose(fam["size"]["CH-stretch"], 3.3) and np.isclose(fam["control_fold1"]["CH-oop"], 2.0)
    assert set(fam) == {"size", "control_fold1", "control_fold2"}
    bare = [{k: {kk: vv for kk, vv in v.items() if kk != "diag_rms"} for k, v in r.items()} for r in size]
    with pytest.raises(KeyError):
        R.read(bare, [_rec(s5=0.4)] * 3, [_rec(s5=0.4)] * 3)


def test_the_id_files_follow_the_frozen_set_file():
    d = json.load(open(P.SRC, encoding="utf-8"))
    ls = P.lists(d)
    assert len(ls["s5"]) == 30 and len(ls["s4N"]) == 30 and len(ls["all_labelled"]) == 60
    assert not set(ls["fold1_test"]) & set(ls["fold2_test"]) and set(ls["fold1_test"]) | set(ls["fold2_test"]) == set(ls["s5"])
    assert not set(ls["fold1_test"]) & (set(d["control_fold1"]["train_extra"]))


def test_ids_have_labels_names_what_is_missing(tmp_path):
    needed = (L.GEOMETRY, *L.LABEL_SETS["analytic"][0])
    (tmp_path / "X").mkdir()
    for f in needed:
        (tmp_path / "X" / f).write_text("{}")
    (tmp_path / "Y").mkdir()
    (tmp_path / "Y" / "geometry.json").write_text("{}")
    assert L.missing(["X", "Y", "Z"], tmp_path) == {"Y": ["hessian_b3lyp_analytic.npz", "hessian_wb97x_analytic.npz"], "Z": list(needed)}


def test_a_set_that_lost_molecules_is_not_read():
    import pytest
    size = [_rec(s5=0.6, s4N=0.4)] * 3
    bad = [dict(_rec(s5=0.3), s5={**_rec(s5=0.3)["s5"], "dropped": ["P3_x"]})] * 3
    with pytest.raises(SystemExit, match="lost 1 registered"):
        R.read(size, bad, [_rec(s5=0.5)] * 3)


def test_only_the_amended_molecules_may_be_missing():
    """19 Oct 2026: the two molecules the amendment names leave the read; any other drop still refuses it."""
    allowed = [dict(_rec(s5=0.3), s5={**_rec(s5=0.3)["s5"], "dropped": sorted(R.AMENDED_OUT)})] * 3
    R.require_complete(allowed, "s5")
    mixed = [dict(_rec(s5=0.3), s5={**_rec(s5=0.3)["s5"], "dropped": [*sorted(R.AMENDED_OUT), "P3_other"]})] * 3
    with pytest.raises(SystemExit, match="P3_other"):
        R.require_complete(mixed, "s5")


def test_a_steep_q5_reads_by_the_control_curve():
    """14 Oct 2026, learning-curve amendment: a steep q5 is 'data-limited' when the control still learns from half to full, and goes to the
    search when its curve is flat; never a verdict on the mandate from one point."""
    size = [_rec(s5=0.80, s4N=0.40)] * 3
    full1 = [_rec(s5=v) for v in (0.30, 0.31, 0.29)]
    full2 = [_rec(s5=v) for v in (0.30, 0.29, 0.31)]
    learning = R.read(size, full1, full2, None, [_rec(s5=v) for v in (0.45, 0.46, 0.44)], [_rec(s5=v) for v in (0.45, 0.44, 0.46)])
    assert learning["control_curve"]["still_learning"] and "data-limited" in learning["verdict"]
    flat = R.read(size, full1, full2, None, [_rec(s5=v) for v in (0.31, 0.30, 0.29)], [_rec(s5=v) for v in (0.29, 0.31, 0.30)])
    assert not flat["control_curve"]["still_learning"] and "search" in flat["verdict"]
    assert R.read(size, full1, full2)["control_curve"] is None


def test_the_half_folds_keep_two_per_scaffold_and_scaffolds_come_from_the_name():
    import chain41_half_folds as H
    d = json.load(open(H.FOLDS, encoding="utf-8"))
    rows = {r["id"]: r for r in __import__("csv").DictReader(open(H.CANDIDATES, encoding="utf-8"))}
    for n in (1, 2):
        fold = d[f"control_fold{n}"]
        parent_of = {i: H.scaffold_name(rows, i) for i in fold["train_extra"]}
        kept, dropped = H.half(fold, parent_of)
        assert len(kept) == 2 * len(fold["scaffolds_trained"]) and len(kept) + len(dropped) == len(fold["train_extra"])
        assert set(parent_of.values()) == set(fold["scaffolds_trained"])
