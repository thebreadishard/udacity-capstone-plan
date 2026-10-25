"""probes/mai_teacher_overlap.py (TASKS 112, reading 2): only carbon skeletons are candidates, an entry matches by formula and skeleton, a
disagreeing duplicate is left out by name, and the statistics pool the modes per family."""
import sys
import zipfile
from pathlib import Path

import numpy as np
import pytest

pytest.importorskip("torch")
pytest.importorskip("rdkit")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes"))
import mai_teacher_overlap as M  # noqa: E402, RUF100  (after the sys.path insert: pre-commit's pinned ruff flags it, the newer one not)

from mai_fixtures import archive_entry, ring  # noqa: E402, RUF100


def test_only_carbon_skeletons_are_candidates():
    assert M.carbon_skeleton("c1ccc2ccccc2c1") and not M.carbon_skeleton("c1ccncc1") and not M.carbon_skeleton("")


def test_entries_match_by_formula_and_skeleton_and_disagreeing_duplicates_leave(tmp_path):
    benzene = M.skeleton(M.xyz_block(*ring(6)))
    cyclooctatetraene = M.skeleton(M.xyz_block(*ring(8)))
    z = tmp_path / "m.zip"
    with zipfile.ZipFile(z, "w") as w:
        w.writestr("IR_COMPAS/charge_0/C1M000001.xyz", archive_entry("C6H6", 6))
        w.writestr("IR_COMPAS/charge_0/C1M000002.xyz", archive_entry("C8H8", 8))
        w.writestr("IR_COMPAS/charge_0/C2M000002.xyz", archive_entry("C8H8", 8, first=1005.0))
    ours = {"A_b": {"formula": "C6H6", "skeleton": benzene}, "A_c": {"formula": "C8H8", "skeleton": cyclooctatetraene},
            "A_x": {"formula": "C10H8", "skeleton": "not in the archive"}}
    tables, left_out = M.match(z, ours)
    assert list(tables) == ["A_b"] and tables["A_b"][:, 0].tolist() == [1000.0, 3000.0]
    assert list(left_out) == ["A_c"] and "disagree" in left_out["A_c"]


def test_the_statistics_pool_modes_per_family():
    out = M.stats({"CH-stretch": [2.0, -2.0], "other": [1.0]})
    assert out["CH-stretch"]["rms"] == pytest.approx(2.0) and out["all"]["n"] == 3 and out["all"]["mean"] == pytest.approx(1 / 3)
    assert np.isclose(out["other"]["mean"], 1.0)
