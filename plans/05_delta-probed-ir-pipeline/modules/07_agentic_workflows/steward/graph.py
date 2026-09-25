"""The LangGraph state graph: observe → propose → gate → act → record → (loop | end). The reasoning node is the only place a model is called;
the gate and the tools are plain Python nodes."""
from __future__ import annotations

from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph

from .gate import check
from .rules import by_id, load_rules
from .schema import Proposal
from .tools import ReplayTools

TERMINAL = {"wait", "escalate_to_human"}


class StewardState(TypedDict, total=False):
    observations: list[dict]
    proposal: dict
    gate: dict
    executed: dict
    actions_taken: list[dict]
    ledger: list[str]
    escalations: list[dict]
    launches: int
    max_launches: int
    step: int
    max_steps: int
    done: bool


def build_graph(policy, tools: ReplayTools, rules: list[dict] | None = None):
    rules = rules or load_rules(); rid = by_id(rules)

    def observe(s: StewardState) -> dict:
        new = tools.observe(s.get("step", 0))
        return {"observations": s.get("observations", []) + new}

    def propose(s: StewardState) -> dict:
        p = policy.propose(dict(s))
        return {"proposal": p.model_dump()}

    def gate(s: StewardState) -> dict:
        p = Proposal(**s["proposal"]); g = check(p, dict(s), rid)
        return {"gate": g.model_dump()}

    def act(s: StewardState) -> dict:
        g = s["gate"]; p = Proposal(**s["proposal"])
        if not g["approved"]:
            p = Proposal(**g["forced_action"]) if g.get("forced_action") else Proposal(action="wait", args={"minutes": 30}, rule_id="R22", reason="gate refused; waiting")
        effect = tools.act(p) if p.action not in ("wait",) else {"source": "wait", "text": f"waited {p.args.get('minutes', 30)} min", "facts": {}}
        upd: dict[str, Any] = {"executed": p.model_dump(), "observations": s.get("observations", []) + [effect],
                               "actions_taken": s.get("actions_taken", []) + [{"action": p.action, "args": p.args, "rule_id": p.rule_id, "approved": g["approved"], "forced": not g["approved"]}]}
        if p.action == "launch":
            upd["launches"] = s.get("launches", 0) + 1
        if p.action == "escalate_to_human":
            upd["escalations"] = s.get("escalations", []) + [p.args]
        return upd

    def record(s: StewardState) -> dict:
        p = Proposal(**s["executed"]); g = s["gate"]
        line = tools.ledger_line(p, g.get("reasons", []), g["approved"])
        step = s.get("step", 0) + 1
        done = p.action in TERMINAL or step >= s.get("max_steps", 8)
        return {"ledger": s.get("ledger", []) + [line], "step": step, "done": done}

    def route(s: StewardState) -> str:
        return END if s.get("done") else "observe"

    g = StateGraph(StewardState)
    for name, fn in (("observe", observe), ("propose", propose), ("gate", gate), ("act", act), ("record", record)):
        g.add_node(name, fn)
    g.add_edge(START, "observe"); g.add_edge("observe", "propose"); g.add_edge("propose", "gate"); g.add_edge("gate", "act"); g.add_edge("act", "record")
    g.add_conditional_edges("record", route, {END: END, "observe": "observe"})
    return g.compile()


def run_scenario(scenario: dict, policy, rules: list[dict] | None = None, max_steps: int = 8) -> dict:
    tools = ReplayTools(scenario)
    app = build_graph(policy, tools, rules)
    final = app.invoke({"observations": [], "actions_taken": [], "ledger": [], "escalations": [], "launches": 0, "max_launches": 3, "step": 0, "max_steps": max_steps, "done": False},
                       config={"recursion_limit": 10 * max_steps + 10})
    taken = [a["action"] for a in final["actions_taken"]]
    exp = scenario["expected"]
    ok_seq = taken[:len(exp["sequence"])] == exp["sequence"] if exp.get("sequence") else True
    ok_forbidden = not any(a in exp.get("forbidden", []) for a in taken)
    ok_rules = all(a.get("rule_id") in exp.get("rules_any", [a.get("rule_id")]) for a in final["actions_taken"][:1]) if exp.get("rules_any") else True
    return {"id": scenario["id"], "policy": getattr(policy, "name", "?"), "actions": taken, "rules": [a.get("rule_id") for a in final["actions_taken"]],
            "forced_by_gate": [a["action"] for a in final["actions_taken"] if a.get("forced")], "expected": exp, "pass": bool(ok_seq and ok_forbidden and ok_rules),
            "ledger": final["ledger"], "escalations": final.get("escalations", [])}
