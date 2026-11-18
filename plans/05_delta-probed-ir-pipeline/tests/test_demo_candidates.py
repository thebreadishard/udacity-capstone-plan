"""The demo candidates' table (`probes/demo_candidates.py`, TASKS 152) on synthetic verdicts: the short list first and by time, a refusal
shown with its reason and never short-listed."""
from __future__ import annotations

import sys

from pin_tools import PLAN

sys.path.insert(0, str(PLAN / "probes"))
import demo_candidates as DC


def row(name: str, minutes: int | None, short: bool, time_on: str = "pyscf 2.15.0") -> dict:
    return {"name": name, "smiles": "c1ccccc1", "admitted": True, "atoms": 12, "functions": 102, "minutes": minutes, "time_on": time_on,
            "role": "unseen", "seen": "not in the catalogue: the network has not seen it", "short_list": short}


def test_the_short_list_comes_first_by_time_and_a_refusal_keeps_its_reason():
    rows = [row("slow", 40, False), row("b", 25, True), {"name": "ion", "smiles": "[NH4+]", "admitted": False, "reason": "net formal charge"},
            row("a", 10, True)]
    text = DC.markdown(rows, 6)
    body = [ln.split(" | ")[0].lstrip("| ") for ln in text.splitlines() if ln.startswith("| ") and not ln.startswith(("| name", "|---"))]
    assert body[:2] == ["a", "b"] and "Short list: 2 of 4." in text
    assert "refused: net formal charge | no |" in text


def test_a_version_without_a_fit_takes_the_other_version_s_time_labelled_or_none(monkeypatch):
    """Review of 18 Nov: with --pyscf 2.15.0 (no fit today) RT.estimate raised on the first admitted molecule and the tool died."""
    other = {"basis_functions": 166, "seconds": 1620, "within_half_hour": True, "pyscf": "2.14.0", "other_version": True}
    monkeypatch.setattr(DC.RT, "estimate_or_other", lambda smiles, threads, pyscf: other)
    t = DC.timing("c1ccc2ccccc2c1", 6, "2.15.0")
    assert t == {"functions": 166, "minutes": 27, "within_half_hour": True, "time_on": "pyscf 2.14.0's time, not 2.15.0's (no 2.15.0 fit yet)"}
    monkeypatch.setattr(DC.RT, "estimate_or_other", lambda smiles, threads, pyscf: None)
    t = DC.timing("c1ccc2ccccc2c1", 6, "2.15.0")
    assert t["minutes"] is None and t["time_on"] == "no pyscf 2.15.0 fit yet" and not t["within_half_hour"]
    text = DC.markdown([row("x", None, False, t["time_on"]), row("y", 20, True)], 6)
    assert "| x | `c1ccccc1` | 12 | 102 | — | no pyscf 2.15.0 fit yet |" in text
