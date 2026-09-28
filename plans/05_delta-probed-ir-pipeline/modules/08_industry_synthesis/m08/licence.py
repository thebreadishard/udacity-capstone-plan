"""The licence of the learned layer (module 05): which families may show a *predicted* correction. Read from the proof-of-learning pre-registration's
rule and the latest recorded layer-B table — never typed in. Today no family is licensed: the registered verdict falls at 1,200 admitted molecules."""
from __future__ import annotations

import re
from pathlib import Path

from .catalog import PLAN

PREREG = PLAN / "GoalGathering" / "notes" / "PreRegistration_2026-09-25_Proof_of_Learning_Layer_B.md"
READING = PLAN / "modules" / "05_support_predictor" / "out" / "E7_rungB_layerB_2026-09-27.md"
RULE = ("proof-of-learning pre-registration (25 Sep 2026): the verdict 'the network learns' falls at 1,200 admitted layer-B molecules on three "
        "hold-outs; intermediate tables at 300 and 600 are recorded and carry no verdict; no family is licensed before the verdict")


def latest_reading(path: Path = READING) -> dict:
    """The B1 MLP rows of the latest layer-B table: ring coupling ratio and corrected-ω RMS per hold-out, with the pool size."""
    out: dict = dict(source=str(path.relative_to(PLAN)).replace("\\", "/"), rows={})
    if not path.exists():
        return out
    text = path.read_text(encoding="utf-8")
    m = re.search(r"\((\d{4}-\d{2}-\d{2} \d{2}:\d{2})\)", text.split("\n")[0])
    out["date"] = m.group(1) if m else None
    for line in text.split("\n"):
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 12 and cells[2] == "B1 MLP":
            ratio = re.sub(r"\*", "", cells[8]); rms = cells[10].split()[0]
            out["rows"][cells[1]] = dict(n=int(cells[0]), ring_coupling_ratio=float(ratio), corrected_omega_rms=float(rms))
    return out


def state() -> dict:
    r = latest_reading()
    return dict(licensed_families=[], rule=RULE, rule_source=str(PREREG.relative_to(PLAN)).replace("\\", "/"), latest_reading=r,
                statement=("no family licensed: the registered verdict falls at 1,200 admitted layer-B molecules; the latest recorded table "
                           + (f"({r.get('date')}, pool {next(iter(r['rows'].values()))['n']}) shows ring coupling ratios "
                              + " / ".join(f"{k} {v['ring_coupling_ratio']:.2f}" for k, v in r["rows"].items()) + " against the zero rule, read as an interim only"
                              if r.get("rows") else "is not on disk")))


def licensed(family: str) -> bool:
    return family in state()["licensed_families"]
