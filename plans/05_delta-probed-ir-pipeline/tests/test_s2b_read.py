"""probes/s2b_read.py (S2b registration, 'Read'), on synthetic records before any S2b number (CLAUDE.md, 'Evidence'): the per-family verdict
rules on crafted curves (licensed, still learning with a size, an asymptote above the line, flat, the reference k when fewer than 17
scaffolds train, too few to read), the x2* choice and its tie rule, refused inputs (a repeated id, a malformed set list, a plan without
k = 16), and the whole read end to end on molecules whose label is exactly a per-family slope times Δ_xtb (licensed) and on pure noise (not
licensed), with one family absent from a scaffold."""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes"))
pytest.importorskip("sklearn")
B = pytest.importorskip("s2b_read")

SLOPE = {"CH-stretch": 0.9, "CH-oop": 0.6, "ring-ip": 0.8, "other": 0.7}
OFFSET = {"CH-stretch": -2.0, "CH-oop": 1.5, "ring-ip": -0.5, "other": 0.0}
SMALL_PLAN = B.ReadPlan(n_subsets=4, search_configs=(B.Config("ridge", "F1"), B.Config("ridge", "F3")))


def crafted(fn, ks=(4, 6, 8, 12, 16, 24), n_all=31, se=0.05):
    rows = {str(k): {"r": fn(k), "r_se": se} for k in ks if k < n_all}
    rows["all"] = {"r": fn(n_all), "r_se": 0.0, "k": n_all}
    return rows


def test_licensed_when_any_full_set_read_meets_the_line():
    v = B.family_verdict({"c": crafted(lambda k: 5.0)}, {"x0": 9.0, "c": 5.0, "x2": 2.9})
    assert v["licensed_by"] == ["x2"] and v["reading"].startswith("licensed by x2")


def test_still_learning_gets_a_size():
    v = B.family_verdict({"x1": crafted(lambda k: 2.0 + 20 * k ** -0.7)}, {"x1": 2.0 + 20 * 31 ** -0.7})
    assert v["still_learning"] and v["extrapolation"]["scaffolds_needed"] > 31 and "sizes S2c" in v["reading"]


def test_an_asymptote_above_the_line_reads_flat():
    v = B.family_verdict({"b": crafted(lambda k: 4.0 + 10 / k)}, {"b": 4.0 + 10 / 31})
    assert v["still_learning"] and v["extrapolation"]["scaffolds_needed"] is None and "route A" in v["reading"]


def test_flat_reads_route_a_and_the_best_curve_model_is_read():
    v = B.family_verdict({"c": crafted(lambda k: 6.0), "x1": crafted(lambda k: 5.0)}, {"c": 6.0, "x1": 5.0})
    assert v["best_curve_model"] == "x1" and not v["still_learning"] and v["reading"].endswith("route A for the large targets")


def test_reference_k_falls_back_to_half_the_training_scaffolds():
    rows = crafted(lambda k: 5.0, n_all=14)
    assert "16" not in rows and B.reference_k(rows) == 6


def test_too_few_scaffolds_cannot_be_read():
    with pytest.raises(ValueError, match="cannot be read"):
        B.reference_k(crafted(lambda k: 5.0, ks=(4,), n_all=5))


def test_x2_choice_takes_the_most_chosen_and_the_first_on_a_tie():
    a, b, c = (cfg.name for cfg in B.X2_GRID[:3])
    choice = B.x2_choice({"ring-ip": {"chosen": {b: 3, a: 1}}, "other": {"chosen": {c: 2, b: 2}}})
    assert choice["ring-ip"].name == b and choice["other"].name == b


def test_merge_refuses_an_id_in_two_sets():
    part = {"g": {"s": [{"id": "A_1"}]}, "x": {}}
    with pytest.raises(ValueError, match="A_1 is in set"):
        B.merge({"S2": part, "S2b": part})


def test_read_sets_refuses_malformed_lists(tmp_path):
    ok = {k: str(tmp_path) for k in B.SET_KEYS} | {"name": "S2", "selection": str(tmp_path / "sel.json")}
    (tmp_path / "sel.json").write_text("{}", encoding="utf-8")
    for bad, why in (([], "non-empty"), ([ok | {"surprise": 1}], "unknown keys"), ([ok, ok], "repeat"),
                     ([ok | {"root": str(tmp_path / "nowhere")}], "missing")):
        (tmp_path / "sets.json").write_text(json.dumps(bad), encoding="utf-8")
        with pytest.raises(ValueError, match=why):
            B.read_sets(str(tmp_path / "sets.json"))
    (tmp_path / "sets.json").write_text(json.dumps([ok]), encoding="utf-8")
    assert B.read_sets(str(tmp_path / "sets.json"))[0].name == "S2"


def test_a_plan_without_the_reference_k_is_refused():
    with pytest.raises(ValueError, match="reference k"):
        B.ReadPlan(ks=(4, 8, 12))


def synthetic(labels, n_scaf=20, per=24, seed=5):
    """One molecule per scaffold, window modes only, with the search's local (9) and proximity (2) columns; scaffold 0 has no 'other'."""
    rng = np.random.default_rng(seed)
    by_scaf = {}
    for s in range(n_scaf):
        fam = rng.choice(B.FAMILIES[:3] if s == 0 else B.FAMILIES, size=per)
        xtb = rng.normal(-15, 8, size=per)
        by_scaf[f"s{s:02d}"] = [{"omega": rng.uniform(600, 1900, size=per), "family": fam, "h": rng.uniform(0, 1, size=per),
                                 "o": rng.uniform(0, 1, size=per), "local": rng.normal(size=(per, 9)), "prox": rng.normal(size=(per, 2)),
                                 "delta": labels(fam, xtb, rng), "xtb": xtb}]
    return by_scaf


def test_exact_slopes_are_licensed_end_to_end():
    data = synthetic(lambda fam, xtb, _rng: np.array([SLOPE[f] * x + OFFSET[f] for f, x in zip(fam, xtb, strict=True)]))
    r = B.read_scope(data, SMALL_PLAN)
    assert set(r["verdicts"]) == set(B.FAMILIES)
    for fa, v in r["verdicts"].items():
        assert "x1" in v["licensed_by"] and v["full_set"]["x1"] < 0.05, fa
        assert set(r["curves"][fa]) == set(B.CURVE_MODELS) and "16" in r["curves"][fa]["x1"]


def test_pure_noise_is_not_licensed_end_to_end():
    data = synthetic(lambda fam, _xtb, rng: rng.normal(0, 6, size=len(fam)))
    r = B.read_scope(data, SMALL_PLAN)
    for fa, v in r["verdicts"].items():
        assert v["licensed_by"] == [] and v["reading"].startswith("line 2 missed"), fa
        assert v["reference_k"] == 16 and v["training_scaffolds"] == 19
