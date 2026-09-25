"""Tools. Two modes: `ReplayTools` (scenarios: observations come from fixtures, actions record their effect and update facts — no machine is
touched) and, later, `LiveTools` (the project's remote_status / remote_launch wrappers). The observation format is shared: a dict with
`source`, `text` (verbatim log excerpt) and `facts` (structured, what the gate reads). Every recorded ledger line carries the clock read in the
same call (rule R08)."""
from __future__ import annotations

import datetime as dt
import re

from .schema import Proposal

INSTRUCTION_RE = re.compile(r"\b(agent|assistant|steward)\b.{0,40}\b(delete|remove|rm -rf|ignore (all|previous)|you must|run the following)", re.I)


def stamp() -> str:
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M")


def scan_for_instructions(text: str) -> bool:
    """Observed content that addresses the agent with an imperative is flagged; the gate then allows only escalation (R24)."""
    return bool(INSTRUCTION_RE.search(text or ""))


class ReplayTools:
    """Observations are the scenario's fixture batches, one per step; actions produce deterministic effects that the scenario declares."""

    def __init__(self, scenario: dict):
        self.scenario = scenario
        self.batches = scenario["observations"]
        self.effects = scenario.get("effects", {})
        self.log: list[dict] = []

    def observe(self, step: int) -> list[dict]:
        out = []
        for o in (self.batches[step] if step < len(self.batches) else []):
            o = dict(o); o.setdefault("facts", {})
            if scan_for_instructions(o.get("text", "")):
                o["facts"]["contains_instruction_to_agent"] = True
            out.append(o)
        return out

    def act(self, p: Proposal) -> dict:
        """Perform an approved action in replay: return an observation describing the effect (from the scenario's declared effects)."""
        key = p.action
        eff = self.effects.get(key) or {}
        rec = {"time": stamp(), "action": p.action, "args": p.args, "rule_id": p.rule_id, "effect": eff.get("text", f"{p.action} performed (replay)")}
        self.log.append(rec)
        return {"source": f"effect of {p.action}", "text": rec["effect"], "facts": dict(eff.get("facts", {}))}

    def ledger_line(self, p: Proposal, gate_reasons: list[str], approved: bool) -> str:
        status = "done" if approved else "REFUSED"
        return f"[{stamp()}] {p.action} {p.args} — rule {p.rule_id} — {p.reason[:140]} — {status}" + (f" ({'; '.join(gate_reasons)})" if gate_reasons else "")
