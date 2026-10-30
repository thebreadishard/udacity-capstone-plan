"""The C1 re-read (`probes/c1_reread_plan.py`, TASKS 145) on synthetic records before the run: the registered rule (covers below random
draws on CH-oop by more than two combined se at two of k = 5, 10, 20), a difference just inside two se that does not count, one size not
being enough, a missing record refused; and the chain: every fine-tune R2 on base (c), the covers' own reservoirs."""
from __future__ import annotations

import sys

import pytest

from pin_tools import PLAN

sys.path.insert(0, str(PLAN / "probes"))
import c1_reread_plan as C1


def records(values: list[list[float]]) -> list[dict]:
    """One record per seed, one draw per value: CH-oop of the R2 read, the other families fixed."""
    def read(x: float) -> dict:
        return {"modes": {C1.MODE: {"read": {"family_mean": {"ring-ip": 2.0, "CH-stretch": 2.0, "CH-oop": x, "other": 4.0}}}}}
    return [{"draws": [read(x) for x in seed]} for seed in values]


def arm(base: float, spread: float = 0.1) -> list[dict]:
    return records([[base - spread, base, base + spread] for _ in range(3)])


def test_covers_below_at_two_sizes_hold():
    res = C1.assess({5: arm(6.0), 10: arm(5.0), 20: arm(4.0)}, {5: arm(5.0), 10: arm(4.0), 20: arm(4.0)})
    assert res["C1"] == {"holds": True, "at": [5, 10]}


def test_one_size_is_not_enough_and_a_small_difference_does_not_count():
    se = C1.AP.family_column(arm(5.0), C1.MODE)["CH-oop"][1]
    cov = arm(5.0 - 0.9 * 2.0 * float((2 * se**2) ** 0.5))                    # 0.9 of two combined se below: inside the line
    res = C1.assess({5: arm(6.0), 10: arm(5.0), 20: arm(4.0)}, {5: arm(5.0), 10: cov, 20: arm(4.2)})
    assert res["C1"] == {"holds": False, "at": [5]}


def test_a_missing_record_is_refused(tmp_path):
    with pytest.raises(SystemExit, match="missing records"):
        C1.read(tmp_path)


def test_the_chain_fine_tunes_r2_on_base_c_with_the_covers_as_reservoirs():
    st = C1.steps("out/c1_reread_x", 750)
    assert len(st) == 3 * 3 + 3 * 3 * 3                                       # random: seeds × k; covers: seeds × k × draws
    assert all(s["argv"][s["argv"].index("--modes") + 1] == "body1_es" for s in st)
    assert all("base_c_model_n750_seed" in s["argv"][3] for s in st)
    covers = [s for s in st if s["label"].startswith("cv_")]
    assert all(s["argv"][s["argv"].index("--reservoir") + 1].endswith(f"cover_k{s['label'].split('_')[1][1:]}_d{s['label'].split('_')[2][1:]}.txt")
               for s in covers)
    assert all(s["argv"][s["argv"].index("--es-max-epochs") + 1] == "120" for s in st)
