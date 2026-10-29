"""The anchor-count test's planner and reader (`probes/anchor_count_plan.py`, TASKS 82, 29 Oct 2026, with amendment 1), on synthetic
records: every outcome (a count, at or below 100, above 200, the cap binding, no reading), the repeat control R, arm (a2) as a reference
that does not decide the outcome, the input gate's refusals, and the chain's steps."""
import sys
from pathlib import Path

import pytest

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
import anchor_count_plan as AC  # noqa: E402  (after the sys.path insert)

FAMS = AC.FAMILIES
SEEDS = (0, 1, 2)


def fams(oop: float, stretch: float = 2.4, epoch: int = 40) -> dict:
    return {"ring-ip": 2.0, "CH-stretch": stretch, "CH-oop": oop, "other": 4.0, "loss": 0.03, "epoch": epoch}


def record(k: int, seed: int, modes: dict[str, dict]) -> dict:
    """One fine-tune record: its base as it is ('none') and per draw every mode's family means, training loss and kept epoch; a small
    spread per seed and draw so that the standard errors are finite."""
    draws = []
    for d in range(AC.AR.draws_for(k)):
        wiggle = 0.01 * (seed + d)
        draws.append({"train": [], "modes": {m: {"read": {"family_mean": {f: v[f] + wiggle for f in FAMS}}, "final_loss": v["loss"] + wiggle / 100,
                                                  "best_epoch": v["epoch"]} for m, v in modes.items()}})
    return {"k": k, "seed": seed, "none": {"family_mean": {f: 78.0 + 0.01 * seed for f in FAMS}}, "draws": draws}


def curve(oop: dict[int, float], **kw) -> dict[int, dict]:
    return {k: fams(oop[k], **kw) for k in AC.SIZES}


DOWN = dict(zip(AC.SIZES, (3.4, 3.25, 3.05, 2.95, 2.85), strict=True))      # crosses between 150 and 170
FLAT = dict.fromkeys(AC.SIZES, 3.3)
A2 = curve(dict(zip(AC.SIZES, (3.1, 2.95, 2.8, 2.7, 2.6), strict=True)), stretch=2.2)


def assess(c_r2: dict[int, dict], a2_r2: dict[int, dict] = A2, shift_before: dict[str, float] | None = None) -> dict:
    """Arm (c) with its R2 curve (R1 and R0 flat) and arm (a2) with its own; the follow-up's cells equal this test's at REPEAT_K unless
    `shift_before` moves one arm's CH-oop there."""
    c_by_k = {k: [record(k, s, {AC.R2: c_r2[k], AC.R1: fams(3.3), AC.R0: fams(3.4)}) for s in SEEDS] for k in AC.SIZES}
    a2_by_k = {k: [record(k, s, {AC.R2: a2_r2[k]}) for s in SEEDS] for k in AC.SIZES}
    before = {}
    for arm, v in (("c", c_r2), ("a2", a2_r2)):
        moved = v[AC.REPEAT_K] | {"CH-oop": v[AC.REPEAT_K]["CH-oop"] + (shift_before or {}).get(arm, 0.0)}
        before[arm] = AC.AR.cell([record(AC.REPEAT_K, s, {AC.R2: moved}) for s in SEEDS], AC.R2, AC.ES_MAX_EPOCHS)
    return AC.assess(c_by_k, a2_by_k, before)


def test_a_count_between_the_points_when_the_curve_crosses():
    res = assess(curve(DOWN))
    assert res["repeat"]["holds"]
    n = res["crossings"][f"c {AC.R2}"]["CH-oop"]["k"]
    assert 150 < n < 170 and res["outcome"] == f"count {n:.0f}"


def test_arm_a2_is_reported_and_does_not_decide_the_outcome():
    res = assess(curve(DOWN), a2_r2=curve(FLAT, stretch=1.0))       # arm (a2) never crosses and sits far apart on CH-stretch
    assert res["crossings"][f"a2 {AC.R2}"]["CH-oop"]["k"] is None
    assert res["outcome"] == f"count {res['crossings'][f'c {AC.R2}']['CH-oop']['k']:.0f}"


@pytest.mark.parametrize("arm", ["c", "a2"])
def test_no_reading_when_an_arm_does_not_repeat_the_follow_up(arm):
    res = assess(curve(DOWN), shift_before={arm: 0.3})
    assert not res["repeat"]["holds"] and res["repeat"]["per_arm"][arm]["CH-oop"] and res["outcome"] == "no reading"


def test_above_200_when_the_curve_never_reaches_the_line():
    assert assess(curve(FLAT))["outcome"] == "above 200"


def test_at_or_below_100_when_the_first_point_is_already_at_the_line():
    assert assess(curve(dict.fromkeys(AC.SIZES, 2.9)))["outcome"] == "count ≤ 100"


def test_the_cap_binding_makes_the_read_undecided():
    at_cap = int(0.9 * AC.ES_MAX_EPOCHS)
    res = assess(curve(DOWN, epoch=at_cap))
    assert all(res["cap_binds"].values()) and res["outcome"] == "undecided: the cap binds"
    assert not any(assess(curve(DOWN, epoch=at_cap - 1))["cap_binds"].values())


def test_the_range_brackets_the_count():
    c = assess(curve(DOWN))["crossings"][f"c {AC.R2}"]["CH-oop"]
    assert c["low"] <= c["k"] <= c["high"]


def test_the_report_names_the_outcome_every_mode_and_both_bases():
    res = assess(curve(DOWN))
    text = "\n".join(AC.report_lines(res))
    assert f"**Outcome: {res['outcome']}.**" in text and all(f"| c {m} |" in text for m in AC.C_MODES)
    assert f"| a2 {AC.R2} |" in text and "| c | base as is |" in text and "| a2 | base as is |" in text


# ------------------------------------------------------------------------------------------------------------------- the input gate
BASE_C = ["{python}", "m05/rungC_train.py", "corpus/molecules", "out/ap/base_c", "--epochs", "200", "--distortion-file", "out/ap/d.json"]
BASE_A2 = ["{python}", "m05/rungC_train.py", "corpus/molecules", "out/ar/base_a2", "--epochs", "200", "--family-scale",
           "ring-ip=-0.34,CH-stretch=-0.79,CH-oop=-0.43,other=-1.16"]
LOG = "analytic second-route Hessians substituted for 862 molecules\n"
DIST = {"families": {"CH-stretch": {"mean": -0.79, "rest": -0.79}}}


def test_the_gate_passes_bases_that_differ_only_by_the_distortion():
    assert AC.input_gate(BASE_C, BASE_A2, LOG, LOG, DIST) == {"labels": 862, "ch_stretch_factor": -0.79}


@pytest.mark.parametrize(("argv_a2", "log_a2", "dist", "match"), [
    ([*BASE_A2[:4], "--epochs", "150", *BASE_A2[6:]], LOG, DIST, "differ beyond"),
    (BASE_A2, LOG.replace("862", "601"), DIST, "862 and 601"),
    (BASE_A2, "", DIST, "nowhere"),
    (BASE_A2, LOG, {"families": {"CH-stretch": {"mean": -0.79, "rest": -0.5}}}, "CH-stretch's factor"),
    (BASE_A2[:6], LOG, DIST, "--family-scale appears 0 times"),
])
def test_the_gate_refuses(argv_a2, log_a2, dist, match):
    with pytest.raises(SystemExit, match=match):
        AC.input_gate(BASE_C, argv_a2, LOG, log_a2, dist)


def test_the_chain_steps():
    st = AC.steps("out/ac", 750)
    c = [s for s in st if s["label"].startswith("c_")]
    a2 = [s for s in st if s["label"].startswith("a2_")]
    assert len(c) == len(a2) == len(SEEDS) * len(AC.SIZES) == len(st) // 2
    assert all("anchor_price_2026-10-28/base_c_model_n750_seed" in s["argv"][3] for s in c)
    assert all("anchor_recipe_2026-10-28/base_a2_model_n750_seed" in s["argv"][3] for s in a2)
    assert all(s["argv"][s["argv"].index("--modes") + 1] == "body1_es,head_all_es,head_all" for s in c)
    assert all(s["argv"][s["argv"].index("--modes") + 1] == "body1_es" for s in a2)
    assert all(s["argv"][s["argv"].index("--es-max-epochs") + 1] == "120" for s in st)
    subsets = {s["label"]: s["argv"][s["argv"].index("--subsets") + 1] for s in st}
    assert {v for lab, v in subsets.items() if "_k200_" in lab} == {"1"} and {v for lab, v in subsets.items() if "_k200_" not in lab} == {"3"}
