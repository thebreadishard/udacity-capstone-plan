"""The anchor-count test's planner and reader (`probes/anchor_count_plan.py`, TASKS 82, 29 Oct 2026), on synthetic records: every
outcome (a count, at or below 100, above 200, the cap binding, no reading), G′ reading each run against its own base, the input gate's
refusals, and the chain's steps."""
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


def record(k: int, seed: int, base_stretch: float, modes: dict[str, dict]) -> dict:
    """One fine-tune record: its base as it is ('none', CH-stretch `base_stretch`), and per draw every mode's family means, training
    loss and kept epoch; a small spread per seed and draw so that the standard errors are finite."""
    draws = []
    for d in range(AC.AR.draws_for(k)):
        wiggle = 0.01 * (seed + d)
        draws.append({"train": [], "modes": {m: {"read": {"family_mean": {f: v[f] + wiggle for f in FAMS}}, "final_loss": v["loss"] + wiggle / 100,
                                                  "best_epoch": v["epoch"]} for m, v in modes.items()}})
    base = {f: 3.0 for f in FAMS} | {"CH-stretch": base_stretch + 0.01 * seed}
    return {"k": k, "seed": seed, "none": {"family_mean": base}, "draws": draws}


def curve(oop: dict[int, float], **kw) -> dict[int, dict]:
    return {k: fams(oop[k], **kw) for k in AC.SIZES}


DOWN = dict(zip(AC.SIZES, (3.4, 3.25, 3.05, 2.95, 2.85), strict=True))      # crosses between 150 and 170
FLAT = dict.fromkeys(AC.SIZES, 3.3)


def assess(c_r2: dict[int, dict], c_base: float = 3.5, a2_base: float = 2.6, a2_stretch: float = 2.2, c_stretch_of=None) -> dict:
    """Arm (c) with its R2 curve (R1 and R0 flat), arm (a2) at CH-stretch `a2_stretch` from its base `a2_base`."""
    c_by_k, a2_by_k = {}, {}
    for k in AC.SIZES:
        c_mode = c_r2[k] | ({"CH-stretch": c_stretch_of(k)} if c_stretch_of else {})
        c_by_k[k] = [record(k, s, c_base, {AC.R2: c_mode, AC.R1: fams(3.3), AC.R0: fams(3.4)}) for s in SEEDS]
        a2_by_k[k] = [record(k, s, a2_base, {AC.R2: fams(2.7, stretch=a2_stretch)}) for s in SEEDS]
    return AC.assess(c_by_k, a2_by_k)


def test_a_count_between_the_points_when_the_curve_crosses():
    res = assess(curve(DOWN, stretch=3.1))                       # change (c) 3.1 − 3.5 = −0.4 against (a2) 2.2 − 2.6 = −0.4
    assert res["control"]["holds"] and res["control"]["fails"] == 0
    n = res["crossings"][AC.R2]["CH-oop"]["k"]
    assert 150 < n < 170 and res["outcome"] == f"count {n:.0f}"


def test_the_control_forgives_a_gap_the_bases_already_have():
    # arm (c) ends 0.9 above arm (a2) on CH-stretch, but its base started 0.9 above: G′ holds where the old control G failed
    res = assess(curve(DOWN, stretch=3.1), c_base=3.5, a2_base=2.6, a2_stretch=2.2)
    assert res["control"]["holds"]
    assert res["table"]["c"][AC.R2][100]["family"]["CH-stretch"][0] - res["table"]["a2"][AC.R2][100]["family"]["CH-stretch"][0] > 0.8


def test_no_reading_when_arm_c_improves_less_from_its_base_at_two_k():
    res = assess(curve(DOWN, stretch=3.1), c_stretch_of=lambda k: 3.4 if k in (120, 170) else 3.1)
    assert res["control"]["fails"] == 2 and not res["control"]["holds"] and res["outcome"] == "no reading"


def test_one_failing_k_is_allowed():
    res = assess(curve(DOWN, stretch=3.1), c_stretch_of=lambda k: 3.4 if k == 120 else 3.1)
    assert res["control"]["fails"] == 1 and res["control"]["holds"]


def test_above_200_when_the_curve_never_reaches_the_line():
    assert assess(curve(FLAT, stretch=3.1))["outcome"] == "above 200"


def test_at_or_below_100_when_the_first_point_is_already_at_the_line():
    assert assess(curve(dict.fromkeys(AC.SIZES, 2.9), stretch=3.1))["outcome"] == "count ≤ 100"


def test_the_cap_binding_makes_the_read_undecided():
    at_cap = int(0.9 * AC.ES_MAX_EPOCHS)
    res = assess(curve(DOWN, stretch=3.1, epoch=at_cap))
    assert all(res["cap_binds"].values()) and res["outcome"] == "undecided: the cap binds"
    assert not any(assess(curve(DOWN, stretch=3.1, epoch=at_cap - 1))["cap_binds"].values())


def test_the_range_brackets_the_count():
    c = assess(curve(DOWN, stretch=3.1))["crossings"][AC.R2]["CH-oop"]
    assert c["low"] <= c["k"] <= c["high"]


def test_the_report_names_the_outcome_and_every_mode():
    res = assess(curve(DOWN, stretch=3.1))
    text = "\n".join(AC.report_lines(res))
    assert f"**Outcome: {res['outcome']}.**" in text and all(f"| {m} |" in text for m in AC.C_MODES) and "| a2 | base as is |" in text


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
