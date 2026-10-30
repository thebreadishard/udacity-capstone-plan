"""The demo candidates' table (`probes/demo_candidates.py`, TASKS 152) on synthetic verdicts: the short list first and by time, a refusal
shown with its reason and never short-listed."""
from __future__ import annotations

import sys

from pin_tools import PLAN

sys.path.insert(0, str(PLAN / "probes"))
import demo_candidates as DC


def row(name: str, minutes: int, short: bool) -> dict:
    return {"name": name, "smiles": "c1ccccc1", "admitted": True, "atoms": 12, "functions": 102, "minutes": minutes, "role": "unseen",
            "seen": "not in the catalogue: the network has not seen it", "short_list": short}


def test_the_short_list_comes_first_by_time_and_a_refusal_keeps_its_reason():
    rows = [row("slow", 40, False), row("b", 25, True), {"name": "ion", "smiles": "[NH4+]", "admitted": False, "reason": "net formal charge"},
            row("a", 10, True)]
    text = DC.markdown(rows, 6)
    body = [ln.split(" | ")[0].lstrip("| ") for ln in text.splitlines() if ln.startswith("| ") and not ln.startswith(("| name", "|---"))]
    assert body[:2] == ["a", "b"] and "Short list: 2 of 4." in text
    assert "refused: net formal charge | no |" in text
