"""The anchor price's planner and reader (`probes/anchor_price_plan.py`, TASKS 82, 27 Oct 2026), on synthetic anchors and records: the
factors per family and context, the balanced cover, the 3 cm⁻¹ crossing, the registered lines C1 and C2, and the chain's steps."""
import sys
from pathlib import Path

import numpy as np
import pytest

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
import anchor_price_plan as AP  # noqa: E402  (after the sys.path insert)
import set3_decompose as SD  # noqa: E402

FAMS = AP.FAMILIES


def fam_entry(cc_mean: float, proxy_mean: float, centred: float, n: int = 6) -> dict:
    return {"total": {"mean": cc_mean, "centred_slope": centred}, "proxy mean": proxy_mean, "n": n}


def decompose() -> dict:
    """Three contexts; CH-oop's mean ratio 0 / -0.5 / -1 by context, the others uniform; one anchor with a single CH-stretch mode."""
    def anchor(i, ch_oop_ratio, n_stretch=6):
        return {"id": i, "CH-oop": fam_entry(20 * ch_oop_ratio, 20, -0.5), "other": fam_entry(-15, 10, -0.3),
                "ring-ip": fam_entry(-14, 10, 0.1), "CH-stretch": fam_entry(-34, 43, -5.0, n_stretch)}
    return {"benzene": anchor("A1", 0.0), "pyridine": anchor("A2", 0.1), "naphthalene": anchor("A3", -0.4),
            "quinoline": anchor("A4", -0.6), "azulene": anchor("A5", -1.0, n_stretch=1)}


CONTEXTS = {"benzene": "single", "pyridine": "single", "naphthalene": "fused", "quinoline": "fused", "azulene": "five"}


def test_contexts_come_from_the_anchor_ids():
    smiles = {"A1": "s1", "A2": "s2", "A3": "f1", "A4": "f2", "A5": "v"}
    ctx = AP.anchor_contexts(decompose(), smiles, lambda s: {"s": "single", "f": "fused", "v": "five"}[s[0]])
    assert ctx == CONTEXTS


def test_factors_per_family_and_context():
    f = AP.family_factors(decompose(), CONTEXTS)
    assert f["CH-oop"] == {"mean": {"five": -1.0, "fused": -0.5, "single": 0.05}, "rest": -0.5}
    assert f["other"] == {"mean": -1.5, "rest": -0.3}
    assert f["ring-ip"] == {"mean": -1.4, "rest": 0.1}
    assert f["CH-stretch"] == {"mean": -0.79, "rest": -0.79}        # uniform: the mean ratio on both parts; azulene's single mode left out


def test_a_family_no_anchor_carries_is_refused():
    d = {k: {kk: vv for kk, vv in v.items() if kk != "ring-ip"} for k, v in decompose().items()}
    with pytest.raises(SystemExit, match="ring-ip"):
        AP.family_factors(d, CONTEXTS)


def test_the_balanced_cover_takes_every_cell_before_a_second_and_cell_less_molecules_last():
    cells = {"a": {1, 2}, "b": {2}, "c": {3}, "d": {1}, "e": set(), "f": {3, 4}}
    first = AP.balanced_cover(cells, 2, np.random.default_rng(0))
    assert set(first) == {"a", "f"}                                   # four cells in two molecules
    assert "e" not in AP.balanced_cover(cells, 5, np.random.default_rng(0))
    assert AP.balanced_cover(cells, 6, np.random.default_rng(0)) == sorted(cells)
    assert AP.balanced_cover(cells, 3, np.random.default_rng(1)) == AP.balanced_cover(cells, 3, np.random.default_rng(1))


def test_the_crossing_interpolates_in_log_k():
    assert AP.crossing({5: 6.0, 10: 4.0, 20: 2.0}) == pytest.approx(np.exp(np.log(10) + 0.5 * np.log(2)))
    assert AP.crossing({5: 2.5, 10: 2.0}) == 5.0
    assert AP.crossing({5: 6.0, 10: 4.0}) is None
    assert AP.crossing({100: 3.17, 200: 2.82}) == pytest.approx(np.exp(np.log(100) + (0.17 / 0.35) * np.log(2)))


def record(values_by_draw: list[dict[str, float]], modes=("head_all",)) -> dict:
    return {"draws": [{"train": [], "modes": {m: {"read": {"family_mean": v}} for m in modes}} for v in values_by_draw]}


def fams(ch_oop: float) -> dict[str, float]:
    return {"ring-ip": 2.0, "CH-stretch": 1.5, "CH-oop": ch_oop, "other": 3.5}


CURVE_C = {5: 7.0, 10: 5.5, 20: 4.0, 50: 3.4, 100: 2.9, 200: 2.6}
CURVE_A = {5: 6.55, 10: 5.0, 20: 4.04, 50: 3.6, 100: 3.17, 200: 2.82}


def random_records(curve: dict[int, float], rng: np.random.Generator) -> dict:
    return {k: [record([fams(v + rng.normal(0, 0.05)) for _ in range(AP.DRAWS)]) for _ in AP.PC.SEEDS] for k, v in curve.items()}


def synthetic(cover_gain: float) -> tuple[dict, dict, dict]:
    rng = np.random.default_rng(7)
    cover = {k: [record([fams(CURVE_C[k] - cover_gain + rng.normal(0, 0.05))], modes=("head_all", "scratch"))
                 for _ in range(len(AP.PC.SEEDS) * AP.COVER_DRAWS)] for k in AP.COVER_SIZES}
    return random_records(CURVE_C, rng), cover, random_records(CURVE_A, rng)


def test_c1_holds_when_the_cover_is_clearly_lower_and_not_when_equal():
    res = AP.assess(*synthetic(cover_gain=1.0))
    assert res["C1"] == {"holds": True, "at": list(AP.COVER_SIZES)}
    assert AP.assess(*synthetic(cover_gain=0.0))["C1"]["holds"] is False


def test_c2_reads_every_family_and_arm_a_beside_it():
    c2 = AP.assess(*synthetic(cover_gain=0.0))["C2"]
    assert 50 < c2["arm_c"]["CH-oop"] < 100
    assert c2["arm_c"]["ring-ip"] == 5.0 and c2["arm_c"]["other"] is None
    assert 100 < c2["arm_a"]["CH-oop"] < 200


def test_a_missing_value_stops_the_read():
    rand, cover, arm_a = synthetic(cover_gain=0.0)
    rand[5][0]["draws"][0]["modes"]["head_all"]["read"]["family_mean"]["CH-oop"] = float("nan")
    with pytest.raises(SystemExit, match="non-finite"):
        AP.assess(rand, cover, arm_a)


def test_the_report_names_both_lines():
    text = "\n".join(AP.report_lines(AP.assess(*synthetic(cover_gain=1.0))))
    assert "**C1**" in text and "holds" in text and "**C2**" in text and "| 10 | cover, scratch |" in text
    assert "| 200 | arm (a), whole head |" in text


def test_the_chain_trains_one_base_then_every_fine_tune():
    st = AP.steps("out/ap", 750, ["--use-analytic"])
    labels = [s["label"] for s in st]
    assert labels[:2] == ["base_c", "register"]
    assert len(labels) == 2 + len(AP.PC.SEEDS) * (len(AP.RANDOM_SIZES) + len(AP.COVER_SIZES) * AP.COVER_DRAWS)
    base = st[0]["argv"]
    assert base[base.index("--distortion-file") + 1] == "out/ap/distortion.json" and "--family-scale" not in base
    k200 = next(s["argv"] for s in st if s["label"] == "ft_c_k200_seed0")
    assert k200[k200.index("--subsets") + 1] == "1" and k200[k200.index("--modes") + 1] == "head_all"
    cv = next(s["argv"] for s in st if s["label"] == "cv_c_k20_d1_seed2")
    assert cv[cv.index("--reservoir") + 1] == "out/ap/cover_k20_d1.txt" and cv[cv.index("--modes") + 1] == "head_all,scratch"
    assert cv[cv.index("--read") + 1].endswith("proxy_check_2026-10-21/a_read.txt")


def test_the_decomposition_reports_the_mean_and_the_centred_slope():
    a, b = np.array([1.0, 2.0, 6.0]), np.array([2.0, 3.0, 4.0])
    c = SD.compare(a, b)
    assert c["mean"] == pytest.approx(3.0)
    assert c["centred_slope"] == pytest.approx(2.5)
