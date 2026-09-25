"""The deterministic gate: every proposal passes through here before anything is done. No LLM. Each check names the rule it enforces
(rules/rules_v1.json). A refusal substitutes `escalate_to_human` (when a rule says a human decides, or when no rule fits) or `wait`."""
from __future__ import annotations

from .schema import ACTIONS, GateResult, Proposal

# actions that may only run when specific observations are present (facts are gathered by tools; see tools.py for the fact keys)
LAUNCH_LIKE = {"launch"}


def _facts(state: dict) -> dict:
    """Merge the fact dicts of all observations so far (later observations win)."""
    f: dict = {}
    for o in state.get("observations", []):
        f.update(o.get("facts", {}))
    return f


def _escalate(msg: str, quote: str = "", rule_id: str = "R32") -> Proposal:
    return Proposal(action="escalate_to_human", args={"message": msg, "quote": quote}, rule_id=rule_id, reason="gate refusal")


def check(p: Proposal, state: dict, rules_by_id: dict) -> GateResult:
    reasons: list[str] = []
    facts = _facts(state)
    job = p.args.get("job") or p.args.get("pattern") or ""
    # 0. allow-list and rule citation (R25, R32)
    if p.action not in ACTIONS:
        return GateResult(approved=False, reasons=[f"action '{p.action}' is not in the allow-list (R25/R32)"],
                          forced_action=_escalate(f"the reasoning step proposed a non-allow-listed action '{p.action}'", p.reason, "R25"))
    if p.rule_id not in rules_by_id and p.action not in ("wait",):
        reasons.append(f"rule id '{p.rule_id}' is not in the rule table (R32)")
        return GateResult(approved=False, reasons=reasons, forced_action=_escalate("a proposal without a valid rule id", p.reason))
    # 1. instructions found in observed content are never followed (R24): a proposal whose reason or args quote an imperative from a log is refused
    for o in state.get("observations", []):
        if o.get("facts", {}).get("contains_instruction_to_agent") and p.action not in ("escalate_to_human", "record_ledger", "wait"):
            return GateResult(approved=False, reasons=["observed content contains an instruction addressed to the agent; only escalation is allowed (R24)"],
                              forced_action=_escalate("a log contains text instructing the agent; not followed", o.get("text", "")[:300], "R24"))
    # 2. launch only after a passed dry run of the same job (R01), never a second instance (R06), never on the laptop during the anchor (R04)
    if p.action in LAUNCH_LIKE:
        if facts.get(f"dry_run_exit:{job}") != 0:
            reasons.append(f"no passed dry run recorded for job '{job}' (R01)")
        if facts.get(f"live_pid:{job}") or facts.get(f"process_running:{job}"):
            reasons.append(f"a live instance of '{job}' exists (R06)")
        if p.args.get("host") == "laptop" and facts.get("anchor_running"):
            reasons.append("the laptop carries an anchor-class run (R04)")
        if reasons:
            forced = Proposal(action="dry_run", args={"host": p.args.get("host"), "job": job}, rule_id="R01", reason="gate: dry run first") \
                if not facts.get(f"live_pid:{job}") and facts.get(f"dry_run_exit:{job}") is None and p.args.get("host") != "laptop" else _escalate("; ".join(reasons), "", "R06")
            return GateResult(approved=False, reasons=reasons, forced_action=forced)
    # 3. a lock is removed only when its pid is dead on the same host and no runner process exists (R05)
    if p.action == "remove_stale_lock":
        lock = facts.get("lock")
        if not lock:
            reasons.append("no lock observed (R05)")
        else:
            if lock.get("pid_alive") is not False:
                reasons.append("the lock's pid is alive or unknown (R05)")
            if lock.get("same_host") is not True:
                reasons.append("the lock belongs to another host (R05)")
            if facts.get("runner_process_count") is None:
                reasons.append("the process list has not been checked with a self-safe pattern (R06)")
            elif facts.get("runner_process_count", 1) > 0:
                reasons.append("a runner process is alive (R05)")
        if reasons:
            return GateResult(approved=False, reasons=reasons, forced_action=Proposal(action="check_runner", args={"host": p.args.get("host"), "pattern": "python [r]un_corpus.py --"}, rule_id="R06", reason="gate: check the process list first") if facts.get("runner_process_count") is None and lock else _escalate("; ".join(reasons), "", "R05"))
    # 4. a reading of a 'the model respects/learns X' statistic needs its target control (R14)
    if p.action == "record_reading":
        stat = str(p.args.get("statistic", "")).lower()
        if any(k in stat for k in ("respect", "symmetr", "consisten", "learn")) and p.args.get("control_value") is None:
            reasons.append(f"statistic '{stat}' recorded without the same statistic on the target (R14)")
            return GateResult(approved=False, reasons=reasons, forced_action=_escalate("a consistency/learning statistic without its target control; the control must be computed first", stat, "R14"))
    # 5. a training run with a fresh checkpoint is progressing; no restart-like action (R21) — 'launch' of the same job counts as a restart
    if p.action in LAUNCH_LIKE and facts.get(f"checkpoint_age_min:{job}") is not None and facts[f"checkpoint_age_min:{job}"] < 2 * facts.get(f"epoch_period_min:{job}", 30):
        reasons.append("the job's checkpoint is fresh: it is progressing, stdout is buffered (R21)")
        return GateResult(approved=False, reasons=reasons, forced_action=Proposal(action="wait", args={"minutes": 30}, rule_id="R21", reason="gate: progressing"))
    # 6. human gates (R25): anything mentioning a machine, money or publication in args is refused even under an allowed action name
    text = " ".join(str(v) for v in p.args.values()).lower()
    if p.action not in ("escalate_to_human", "record_ledger") and any(k in text for k in ("create server", "delete server", "hcloud", "publish", "git push", "rm -rf")):
        reasons.append("the arguments touch a human-gated action (R25)")
        return GateResult(approved=False, reasons=reasons, forced_action=_escalate("human-gated action requested", text[:200], "R25"))
    # 7. rate limit: one launch per step, at most max_launches per run
    if p.action in LAUNCH_LIKE and state.get("launches", 0) >= state.get("max_launches", 3):
        reasons.append("launch budget of this run exhausted")
        return GateResult(approved=False, reasons=reasons, forced_action=_escalate("launch budget exhausted", "", "R25"))
    return GateResult(approved=True, reasons=reasons)
