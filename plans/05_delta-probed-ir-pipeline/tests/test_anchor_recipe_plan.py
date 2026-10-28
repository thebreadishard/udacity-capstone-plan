"""The recipe follow-up's planner and reader (`probes/anchor_recipe_plan.py`, TASKS 82, 28 Oct 2026), on synthetic records: every outcome
of the registered lines (recipe-limited, partly recipe, data-limited, the cap binding, no reading), the control and fit lines, and the
chain's steps."""
import sys
from pathlib import Path

import pytest

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
import anchor_recipe_plan as AR  # noqa: E402  (after the sys.path insert)

FAMS = AR.FAMILIES
SEEDS = (0, 1, 2)


def record(k: int, seed: int, modes: dict[str, dict]) -> dict:
    """One fine-tune record: `modes` maps a mode to its family means, training loss and (early-stopped) kept epoch; a small spread per
    seed and draw so that the standard errors are finite."""
    draws = []
    for d in range(AR.draws_for(k)):
        wiggle = 0.01 * (seed + d)
        entry = {}
        for mode, v in modes.items():
            e = {"read": {"family_mean": {f: v[f] + wiggle for f in FAMS}}, "final_loss": v["loss"] + wiggle / 100}
            if "epoch" in v:
                e["best_epoch"] = v["epoch"]
            entry[mode] = e
        draws.append({"train": [], "modes": entry})
    return {"k": k, "seed": seed, "draws": draws}


def fams(oop: float, stretch: float = 2.4, loss: float = 0.03, epoch: int | None = None) -> dict:
    v = {"ring-ip": 2.0, "CH-stretch": stretch, "CH-oop": oop, "other": 4.0, "loss": loss}
    return v | ({"epoch": epoch} if epoch is not None else {})


def tables(c: dict[str, dict], a2: dict[str, dict]) -> dict:
    """The read's table from per-recipe family values (the same at both k), arm (c)'s R0 in its own records."""
    rc = {k: [record(k, s, {AR.RECIPES[r]: c[r] for r in ("R1", "R2")}) for s in SEEDS] for k in AR.SIZES}
    rc0 = {k: [record(k, s, {AR.RECIPES["R0"]: c["R0"]}) for s in SEEDS] for k in AR.SIZES}
    ra2 = {k: [record(k, s, {AR.RECIPES[r]: a2[r] for r in AR.RECIPES}) for s in SEEDS] for k in AR.SIZES}
    return AR.table(rc, rc0, ra2)


A2 = {"R0": fams(2.9), "R1": fams(2.8, epoch=30), "R2": fams(2.7, epoch=30)}
C_R0 = fams(3.33, stretch=3.5, loss=0.05)


def test_recipe_limited_when_a_new_recipe_reaches_the_line_below_r0():
    res = AR.lines(tables({"R0": C_R0, "R1": fams(3.1, epoch=30), "R2": fams(2.9, epoch=30)}, A2))
    assert res["outcome"] == "recipe-limited"
    assert res["per_recipe"]["R2"]["at_line"] and res["per_recipe"]["R2"]["below_R0"] and not res["per_recipe"]["R1"]["at_line"]
    assert not res["per_recipe"]["R0"]["G"]                                    # R0's CH-stretch control fails, as in arm (c)
    assert res["per_recipe"]["R2"]["G"] and res["per_recipe"]["R2"]["F"]


def test_partly_recipe_when_below_r0_but_not_at_the_line():
    res = AR.lines(tables({"R0": C_R0, "R1": fams(3.15, epoch=30), "R2": fams(3.2, epoch=30)}, A2))
    assert res["outcome"] == "partly recipe"


def test_data_limited_when_no_new_recipe_moves_ch_oop():
    res = AR.lines(tables({"R0": C_R0, "R1": fams(3.33, epoch=30), "R2": fams(3.34, epoch=30)}, A2))
    assert res["outcome"] == "data-limited"


def test_the_cap_binding_turns_a_data_limited_read_into_undecided():
    at_cap = int(0.9 * AR.ES_MAX_EPOCHS)
    res = AR.lines(tables({"R0": C_R0, "R1": fams(3.33, epoch=at_cap), "R2": fams(3.34, epoch=30)}, A2))
    assert res["per_recipe"]["R1"]["cap_binds"] and not res["per_recipe"]["R2"]["cap_binds"]
    assert res["outcome"] == "undecided: the cap binds"


def test_no_reading_when_the_control_fails_for_both_new_recipes():
    bad = {r: fams(2.9, stretch=3.5, epoch=30) for r in ("R1", "R2")}
    res = AR.lines(tables({"R0": C_R0, **bad}, A2))
    assert res["outcome"] == "no reading" and not any(v["G"] for v in res["per_recipe"].values())


def test_the_fit_line_compares_the_training_losses_at_200():
    res = AR.lines(tables({"R0": C_R0, "R1": fams(3.1, loss=0.06, epoch=30), "R2": fams(2.9, loss=0.04, epoch=30)}, A2))
    assert not res["per_recipe"]["R1"]["F"] and res["per_recipe"]["R2"]["F"] and not res["per_recipe"]["R0"]["F"]


def test_a_missing_training_loss_is_refused():
    recs = [record(100, s, {"head_all": fams(3.0)}) for s in SEEDS]
    recs[0]["draws"][0]["modes"]["head_all"]["final_loss"] = None
    with pytest.raises(SystemExit, match="non-finite"):
        AR.cell(recs, "head_all")


def test_the_chain_steps():
    st = AR.steps("out/ar", 750, ["--use-analytic"], {"ring-ip": -0.34, "CH-stretch": -0.79, "CH-oop": -0.43, "other": -1.16})
    labels = [s["label"] for s in st]
    assert labels[:2] == ["base_a2", "register"] and len(st) == 2 + 2 * len(SEEDS) * len(AR.SIZES)
    base = st[0]["argv"]
    assert "--family-scale" in base and "--distortion-file" not in base and base[base.index("--exclude-ids-file") + 1].endswith("a_exclude.txt")
    rc = [s for s in st if s["label"].startswith("rc_")]
    ra2 = [s for s in st if s["label"].startswith("ra2_")]
    assert all("anchor_price_2026-10-28/base_c_model_n750_seed" in s["argv"][3] for s in rc)
    assert all("out/ar/base_a2_model_n750_seed" in s["argv"][3] for s in ra2)
    assert all(s["argv"][s["argv"].index("--modes") + 1] == "head_all_es,body1_es" for s in rc)
    assert all(s["argv"][s["argv"].index("--modes") + 1] == "head_all,head_all_es,body1_es" for s in ra2)
    subsets = {s["label"]: s["argv"][s["argv"].index("--subsets") + 1] for s in st[2:]}
    assert {v for lab, v in subsets.items() if "_k200_" in lab} == {"1"} and {v for lab, v in subsets.items() if "_k100_" in lab} == {"3"}
    assert all(s["argv"][s["argv"].index("--es-max-epochs") + 1] == str(AR.ES_MAX_EPOCHS) for s in st[2:])


def test_the_report_names_the_outcome_and_every_recipe():
    res = AR.lines(t := tables({"R0": C_R0, "R1": fams(3.1, epoch=30), "R2": fams(2.9, epoch=30)}, A2))
    text = "\n".join(AR.report_lines({"table": t, **res}))
    assert "**Outcome: recipe-limited.**" in text and all(f"| {r} |" in text for r in AR.RECIPES)
