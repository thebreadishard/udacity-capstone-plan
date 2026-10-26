"""probes/chain35_read.py on synthetic eval records: every registered branch, the edges of the lines (≤ 3, ≥ 0.3), the two baselines
disagreeing, decision 57's promotion, and the refusals (unfrozen (b), different analytic targets, one seed)."""
import json
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "probes"))
import chain35_read as R

GOOD_A = {"ring-ip": 1.9, "CH-stretch": 1.3, "CH-oop": 2.4, "other": 3.1}
SPREAD = (-0.05, 0.0, 0.05)


@dataclass(frozen=True)
class Spec:
    """An arm's seed means on hold-out (a); (b) is (a) + 3 cm⁻¹ unless given."""
    a: dict
    b: dict | None = None
    ratio_a: float = 0.18
    ratio_b: float = 0.31
    substituted: tuple[str, ...] = ("m1", "m2")
    holdout_b_file: str = "corpus/" + R.FROZEN_B
    seeds: int = 3


def write_arm(folder: Path, name: str, spec: Spec) -> list[Path]:
    """One eval JSON per seed around the spec's seed means (an exact ±0.05 spread, so the means are the given values)."""
    b = spec.b or {f: v + 3.0 for f, v in spec.a.items()}
    paths = []
    for s in range(spec.seeds):
        e = SPREAD[s] if spec.seeds == 3 else 0.0
        rec = {"holdout_b_file": spec.holdout_b_file, "substituted_analytic": list(spec.substituted),
               "a": {"diag_rms": {f: v + e for f, v in spec.a.items()}, R.RATIO: spec.ratio_a + e / 10},
               "b": {"diag_rms": {f: v + e for f, v in b.items()}, R.RATIO: spec.ratio_b + e / 10}}
        p = folder / f"{name}_seed{s}.json"
        p.write_text(json.dumps(rec), encoding="utf-8")
        paths.append(p)
    return paths


def verdict(tmp_path: Path, new: Spec, carried: Spec) -> R.Verdict:
    n, c = R.load_arm(write_arm(tmp_path, "new", new)), R.load_arm(write_arm(tmp_path, "carried", carried))
    return R.decide(n, c, R.compare(n, c))


def test_t1_met_at_the_edge_and_promoted_when_lower_everywhere(tmp_path):
    new = {"ring-ip": 3.0, "CH-stretch": 1.2, "CH-oop": 2.3, "other": 3.0}           # exactly on the ≤ 3 lines
    v = verdict(tmp_path, Spec(new, ratio_a=0.17, ratio_b=0.30), Spec({"ring-ip": 3.1, "CH-stretch": 1.3, "CH-oop": 2.4, "other": 3.4}))
    assert v.t1_met and v.branch == "T1 met" and v.promoted and "version 1.3" in v.promotion


def test_ratio_above_its_line_keeps_t1_open(tmp_path):
    v = verdict(tmp_path, Spec({**GOOD_A, "other": 2.9}, ratio_a=0.26), Spec({**GOOD_A, "other": 3.4}))
    assert not v.t1_met and v.branch == "labels part of it"


def test_a_fall_of_exactly_the_line_is_part_of_it_and_just_below_is_not(tmp_path):
    v = verdict(tmp_path, Spec({**GOOD_A, "other": 3.2}), Spec({**GOOD_A, "other": 3.5}))
    assert v.branch == "labels part of it" and v.other_fall == pytest.approx(0.3)
    w = verdict(tmp_path, Spec({**GOOD_A, "other": 3.21}), Spec({**GOOD_A, "other": 3.5}))
    assert w.branch == "labels not it"


def test_the_baselines_can_disagree_and_the_like_for_like_one_reads(tmp_path):
    # chain 34 read again at 3.60: fall 0.40 (part of it); against the registered 3.35: fall 0.05 (not it)
    v = verdict(tmp_path, Spec({**GOOD_A, "other": 3.30}), Spec({**GOOD_A, "other": 3.60}))
    assert v.branch == "labels part of it" and v.branch_against_registered == "labels not it" and not v.baselines_agree


def test_promotion_goes_to_the_user_when_any_quantity_is_worse(tmp_path):
    v = verdict(tmp_path, Spec({**GOOD_A, "CH-stretch": 1.4}), Spec({**GOOD_A, "other": 3.5, "CH-stretch": 1.3}))
    assert not v.promoted and "(a) CH-stretch" in v.worse and "goes to the user" in v.promotion


def test_equal_quantities_do_not_block_when_one_is_lower(tmp_path):
    """The user's rule (26 Oct): a new version may worsen none of the five; equal at the reported precision is allowed."""
    v = verdict(tmp_path, Spec({**GOOD_A, "other": 3.0}), Spec(GOOD_A))      # only 'other' on (a) and (b) lower, the rest equal
    assert v.promoted and v.worse == () and "lower on 2 of 10" in v.promotion


def test_equal_everywhere_promotes_nothing(tmp_path):
    v = verdict(tmp_path, Spec(GOOD_A), Spec(GOOD_A))
    assert not v.promoted and v.promotion == "equal everywhere: nothing to promote"


def test_refuses_an_unfrozen_holdout_b(tmp_path):
    with pytest.raises(ValueError, match="frozen hold-out"):
        R.load_arm(write_arm(tmp_path, "x", Spec(GOOD_A, holdout_b_file="corpus/holdout_b.txt")))


def test_refuses_arms_on_different_analytic_targets(tmp_path):
    new = R.load_arm(write_arm(tmp_path, "new", Spec(GOOD_A, substituted=("m1", "m2", "m3"))))
    carried = R.load_arm(write_arm(tmp_path, "carried", Spec(GOOD_A)))
    with pytest.raises(ValueError, match="different analytic targets"):
        R.decide(new, carried, R.compare(new, carried))


def test_refuses_one_seed(tmp_path):
    with pytest.raises(ValueError, match="at least two seeds"):
        R.load_arm(write_arm(tmp_path, "x", Spec(GOOD_A, seeds=1)))


def test_main_writes_both_records(tmp_path, capsys):
    new = write_arm(tmp_path, "new", Spec({**GOOD_A, "other": 2.9}))
    carried = write_arm(tmp_path, "carried", Spec({**GOOD_A, "other": 3.4, "ring-ip": 2.0, "CH-stretch": 1.4, "CH-oop": 2.5}, ratio_a=0.19,
                                                 ratio_b=0.32))
    out = tmp_path / "read"
    assert R.main(["--new", *map(str, new), "--carried", *map(str, carried), "--out", str(out)]) == 0
    rec = json.loads(out.with_suffix(".json").read_text(encoding="utf-8"))
    assert rec["verdict"]["promoted"] and rec["analytic_targets"] == 2 and len(rec["comparisons"]) == 10
    assert "**T1 met**" in out.with_suffix(".md").read_text(encoding="utf-8")
