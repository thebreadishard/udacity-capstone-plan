"""The clean hold-out (a) read (`probes/holdout_a_clean_read.py`, TASKS 157) on synthetic records before any run: seed means per family, the
licence line (≤ 3 cm⁻¹ on both hold-outs; exactly on it is licensed), a family the clean set moves across the line, and the refusals the
aggregation inherits (a record without the clean set, or not read on the frozen hold-out (b))."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from pin_tools import PLAN

sys.path.insert(0, str(PLAN / "probes"))
import holdout_a_clean_read as HC

FROZEN = "corpus/holdout_b_frozen_2026-10-08.txt"


def record(tmp: Path, seed: int, a: dict, a8: dict, b: dict, frozen: str = FROZEN) -> Path:
    def hold(d: dict) -> dict:
        return {"diag_rms": d, "coupling_ratio": 0.2, "per_molecule": {}}

    rec = {"holdout_b_file": frozen, "substituted_analytic": ["A_x"], "a": hold(a), "a8": hold(a8), "b": hold(b)}
    p = tmp / f"eval_seed{seed}.json"
    p.write_text(json.dumps(rec), encoding="utf-8")
    return p


def fam(ring: float, ch: float, oop: float, other: float) -> dict:
    return {"ring-ip": ring, "CH-stretch": ch, "CH-oop": oop, "other": other}


def test_seed_means_and_a_family_the_clean_set_moves_across_the_line(tmp_path):
    paths = [record(tmp_path, s, fam(1.6, 1.1, 2.0, 3.3), fam(1.7, 1.2, 3.1 + 0.02 * s, 3.4), fam(2.1, 2.5, 2.7, 3.9)) for s in range(3)]
    rows = {r["family"]: r for r in HC.table(paths)}
    assert rows["CH-oop"]["a8"] == pytest.approx(3.12) and rows["CH-oop"]["licensed_stored"] and not rows["CH-oop"]["licensed_clean"]
    assert rows["ring-ip"]["licensed_clean"] and not rows["other"]["licensed_stored"]
    assert "Licence changed by the clean (a8): CH-oop." in HC.markdown(list(rows.values()), paths)


def test_exactly_on_the_line_is_licensed(tmp_path):
    paths = [record(tmp_path, s, fam(3.0, 1.0, 1.0, 1.0), fam(3.0, 1.0, 1.0, 1.0), fam(3.0, 1.0, 1.0, 1.0)) for s in range(2)]
    assert all(r["licensed_clean"] for r in HC.table(paths))


def test_a_record_without_the_clean_set_or_on_another_b_is_refused(tmp_path):
    p = record(tmp_path, 0, fam(1, 1, 1, 1), fam(1, 1, 1, 1), fam(1, 1, 1, 1))
    rec = json.loads(p.read_text(encoding="utf-8"))
    del rec["a8"]
    q = tmp_path / "no_a8.json"
    q.write_text(json.dumps(rec), encoding="utf-8")
    with pytest.raises(ValueError, match="absent"):
        HC.table([p, q])
    r = record(tmp_path, 1, fam(1, 1, 1, 1), fam(1, 1, 1, 1), fam(1, 1, 1, 1), frozen="corpus/other.txt")
    with pytest.raises(ValueError, match="frozen hold-out"):
        HC.table([p, r])
