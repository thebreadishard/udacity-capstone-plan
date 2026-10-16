"""probes/chain40_read.py on synthetic arms: every registered branch, the boundaries, the still-learning clause, refused inputs."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "probes"))
import chain40_read as cr

FAM = {f: (1.0, 1.0, 1.0) for f in cr.FAMILIES}


def arm(*b: float) -> cr.Arm:
    return cr.Arm(b_ratio=b, b_plus_ratio=b, a_ratio=b, b_families=FAM)


@pytest.mark.parametrize(("full", "branch"), [
    ((0.29, 0.29, 0.29), "covers"),            # Δ = −0.035
    ((0.295, 0.295, 0.295), "covers"),         # Δ = −0.03 exactly: ≤ covers
    ((0.300, 0.300, 0.300), "between"),        # Δ = −0.025
    ((0.310, 0.310, 0.310), "between"),        # Δ = −0.015 exactly: not > −0.015
])
def test_branches_on_delta_with_a_flat_curve(full, branch):
    v = cr.decide(arm(*full), arm(*full))
    assert v.branch == branch and not v.still_learning


def test_stop_when_flat_and_still_learning_overrides_it():
    flat = cr.decide(arm(0.315, 0.316, 0.314), arm(0.316, 0.315, 0.317))
    assert flat.branch == "stop" and not flat.still_learning
    learning = cr.decide(arm(0.315, 0.316, 0.314), arm(0.340, 0.341, 0.339))
    assert learning.still_learning and learning.branch == "still learning"


def test_still_learning_needs_the_gap_beyond_two_standard_errors():
    noisy_half = arm(0.30, 0.34, 0.38)          # mean 0.34, se 0.023: a 0.024 gap is inside twice the combined se
    v = cr.decide(arm(0.315, 0.316, 0.317), noisy_half)
    assert not v.still_learning and v.branch == "stop"


def test_still_learning_needs_the_full_arm_below_chain_37():
    v = cr.decide(arm(0.330, 0.331, 0.329), arm(0.360, 0.361, 0.359))
    assert not v.still_learning and v.branch == "stop"


def test_one_seed_is_refused():
    with pytest.raises(ValueError, match="two seeds"):
        _ = arm(0.3).standard_error


def _eval(tmp_path: Path, name: str, b: float, frozen: bool = True) -> Path:
    block = {"coupling_ratio": b, "diag_rms": dict.fromkeys(cr.FAMILIES, 2.0)}
    rec = {"holdout_b_file": "corpus/holdout_b_frozen_2026-10-08.txt" if frozen else "corpus/other.txt", "a": block, "b": block, "b+": block}
    p = tmp_path / name
    p.write_text(json.dumps(rec), encoding="utf-8")
    return p


def test_main_writes_the_report_and_refuses_an_unfrozen_eval(tmp_path):
    full = [_eval(tmp_path, f"f{i}.json", b) for i, b in enumerate((0.30, 0.31, 0.32))]
    half = [_eval(tmp_path, f"h{i}.json", b) for i, b in enumerate((0.33, 0.34, 0.35))]
    assert cr.main(["--full", *map(str, full), "--half", *map(str, half), "--out", str(tmp_path / "read")]) == 0
    assert "Branch: between" in (tmp_path / "read.md").read_text(encoding="utf-8")
    assert json.loads((tmp_path / "read.json").read_text(encoding="utf-8"))["verdict"]["branch"] == "between"
    with pytest.raises(ValueError, match="frozen"):
        cr.load_arm([_eval(tmp_path, "x.json", 0.3, frozen=False)])
