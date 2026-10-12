"""TASKS 49 (12 Oct 2026): large PAHs labelled by analytic Hessians alone. The trainer's loader admits such a folder only when asked (under
--use-analytic), builds its features from the analytic pair exactly as from the FD pair, and E6.splits never trains on layer T. The jobs for
those folders optimise without FD Hessians. The loader tests copy benzene's corpus folder (git-ignored data), so they are skipped where the
corpus is absent."""
import json
import shutil
import sys
from pathlib import Path

import numpy as np
import pytest

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "modules" / "05_support_predictor" / "m05"))
sys.path.insert(0, str(PLAN / "probes"))
BENZENE = PLAN / "modules" / "05_support_predictor" / "corpus" / "molecules" / "A_8448043181"


@pytest.fixture
def corpus(tmp_path):
    if not (BENZENE / "hessian_b3lyp.npz").exists():
        pytest.skip("corpus data not present (git-ignored)")
    mdir = tmp_path / "molecules"
    fd, an, bare = mdir / "A_fd", mdir / "T_analytic", mdir / "T_unflagged"
    for d in (fd, an, bare):
        d.mkdir(parents=True)
        shutil.copy(BENZENE / "geometry.json", d)
    for tag in ("b3lyp", "wb97x"):
        shutil.copy(BENZENE / f"hessian_{tag}.npz", fd / f"hessian_{tag}.npz")
        shutil.copy(BENZENE / f"hessian_{tag}.npz", an / f"hessian_{tag}_analytic.npz")
        shutil.copy(BENZENE / f"hessian_{tag}.npz", bare / f"hessian_{tag}_analytic.npz")
    (fd / "result.json").write_text(json.dumps({"layer": "A"}))
    (an / "result.json").write_text(json.dumps({"layer": "T", "labels": "analytic_only"}))
    (bare / "result.json").write_text(json.dumps({"layer": "T"}))            # analytic files but no flag: never admitted
    return mdir


def test_analytic_only_folders_enter_only_when_asked_with_the_same_features(corpus):
    import e6_learning_curve as E6
    plain = E6.load_corpus(corpus)
    assert set(plain) == {"A_fd"}
    both = E6.load_corpus(corpus, analytic_only_ok=True)
    assert set(both) == {"A_fd", "T_analytic"} and both["T_analytic"]["hessian_source"] == "analytic"
    for k in ("tokens", "K", "target", "freq"):
        assert np.array_equal(np.asarray(both["T_analytic"][k]), np.asarray(both["A_fd"][k])), k
    assert np.array_equal(np.asarray(both["T_analytic"]["family"]), np.asarray(both["A_fd"]["family"]))


def test_layer_t_is_never_pooled(corpus):
    import e6_learning_curve as E6
    mols = E6.load_corpus(corpus, analytic_only_ok=True)
    _, _, _, pool = E6.splits(mols)
    assert "T_analytic" not in pool


def test_the_jobs_optimise_without_fd_hessians_and_name_their_layer(tmp_path):
    import large_pah_jobs as LJ
    sp = {"uid": 18, "formula": "C24H12", "skeleton": "C1CC2", "symbols": ["C", "H"], "xyz": [[0.0, 0.0, 0.0], [0.0, 0.0, 1.1]]}
    j = LJ.job(sp, "T", str(tmp_path), {"basis": "6-31G*"})
    assert j["hessians"] is False and j["optimise"] is True and j["layer"] == "T" and j["id"].startswith("T_") and len(j["id"]) == 12
    assert j["xyz_angstrom"] == [["C", 0.0, 0.0, 0.0], ["H", 0.0, 0.0, 1.1]] and j["source"]["pahdb_uid"] == 18
