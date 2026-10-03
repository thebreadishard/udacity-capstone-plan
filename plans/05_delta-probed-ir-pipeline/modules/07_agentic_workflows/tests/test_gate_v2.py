"""Gate and policy tests for the rules of 27 September – 3 October 2026 (R33–R41) and the R27 reading fix: every new check fails without its fact
(negative control), passes with the fact resolved, and scenarios S9–S17 replay with the deterministic policy. Run: ../../.venv python -m pytest
modules/07_agentic_workflows/tests -q"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from steward.gate import check  # noqa: E402
from steward.graph import run_scenario  # noqa: E402
from steward.policy import RuleTablePolicy  # noqa: E402
from steward.rules import by_id, load_rules  # noqa: E402
from steward.schema import Proposal  # noqa: E402

RULES = load_rules(); RID = by_id(RULES)
SCEN = json.load(open(Path(__file__).resolve().parents[1] / "scenarios" / "scenarios.json", encoding="utf-8"))["scenarios"]
LAUNCH = Proposal(action="launch", args={"host": "h", "job": "j"}, rule_id="R01", reason="x")
READY = {"job_due": "j", "dry_run_exit:j": 0}


def state(facts=None, actions=None):
    return {"observations": [{"source": "t", "text": "", "facts": facts or {}}], "actions_taken": actions or [], "launches": 0, "max_launches": 3}


def refused_with(g, rule):
    return (not g.approved) and g.forced_action is not None and g.forced_action.action == "escalate_to_human" and g.forced_action.rule_id == rule


def test_default_table_is_v2_with_the_new_rules():
    assert all(f"R{n}" in RID for n in range(33, 42)) and len(RULES) == 41


def test_new_library_call_needs_upstream_test_R33():
    call = {"script": "p.py", "call": "Gradients(mycc).kernel()", "upstream_test_cited": None}
    assert refused_with(check(LAUNCH, state({**READY, "new_library_call": call}), RID), "R33")
    assert check(LAUNCH, state({**READY, "new_library_call": dict(call, upstream_test_cited="grad/test/test_ccsd_t.py")}), RID).approved
    assert check(LAUNCH, state(READY), RID).approved


def test_inherited_setting_must_match_elements_R35():
    st = {"name": "frozen", "value": 6, "derived_from_elements": 10, "molecule": "naphthalene", "override_recorded": False}
    assert refused_with(check(LAUNCH, state({**READY, "inherited_setting": st}), RID), "R35")
    assert check(LAUNCH, state({**READY, "inherited_setting": dict(st, value=10)}), RID).approved
    assert check(LAUNCH, state({**READY, "inherited_setting": dict(st, override_recorded=True)}), RID).approved


def test_thread_budget_R36():
    plan = {"cores": 16, "lanes": {"a": 8, "b": 8, "c": 16}}
    assert refused_with(check(LAUNCH, state({**READY, "launch_plan": plan}), RID), "R36")
    assert check(LAUNCH, state({**READY, "launch_plan": {"cores": 16, "lanes": {"a": 8, "b": 8}}}), RID).approved
    p = RuleTablePolicy().propose(state({"watchdog": {"stall_min": 300, "longest_step_min": 400}}))
    assert p.action == "escalate_to_human" and p.rule_id == "R36"


def test_reading_needs_a_carried_model_R37():
    rp = Proposal(action="record_reading", args={"result_path": "r.json", "statistic": "rms per family", "value": 5.9, "control_value": 6.4}, rule_id="R13", reason="x")
    sup = {"path": "m.pt", "status": "superseded", "override": False}
    assert refused_with(check(rp, state({"model_status": sup}), RID), "R37")
    assert check(rp, state({"model_status": dict(sup, status="carried")}), RID).approved
    assert check(rp, state({"model_status": dict(sup, override=True)}), RID).approved
    assert check(rp, state(), RID).approved


def test_targets_per_family_R38_policy():
    rp = {"result_path": "r.json", "statistic": "corrected omega rms, all modes", "value": 2.96, "control_value": 4.1, "per_family": False, "floor_and_ceiling_measured": False}
    p = RuleTablePolicy().propose(state({"reading_pending": rp}))
    assert p.action == "escalate_to_human" and p.rule_id == "R38"
    p = RuleTablePolicy().propose(state({"reading_pending": dict(rp, per_family=True, floor_and_ceiling_measured=True)}))
    assert p.action == "record_reading" and p.rule_id == "R13"


def test_reading_recorded_once_R27():
    rp = {"result_path": "r.json", "statistic": "rms per family", "value": 5.9, "control_value": 6.4}
    p = RuleTablePolicy().propose(state({"reading_pending": rp}, actions=[{"action": "record_reading"}]))
    assert p.action == "wait" and p.rule_id == "R27"


def test_push_after_single_test_R39():
    pp = {"branch": "b", "tests_run": "pytest -k one", "whole_file_run": False}
    led = Proposal(action="record_ledger", args={"text": "pushed branch b"}, rule_id="R27", reason="x")
    assert refused_with(check(led, state({"push_pending": pp}), RID), "R39")
    assert check(led, state({"push_pending": dict(pp, whole_file_run=True)}), RID).approved
    p = RuleTablePolicy().propose(state({"push_pending": pp}))
    assert p.action == "escalate_to_human" and p.rule_id == "R39"


def test_deletion_needs_fetched_line_R40():
    sd = {"host": "ccx53", "done_line": "HEL2 DONE", "fetched_line": False}
    led = Proposal(action="record_ledger", args={"text": "server deleted after DONE"}, rule_id="R27", reason="x")
    assert refused_with(check(led, state({"server_done": sd}), RID), "R40")
    assert check(led, state({"server_done": dict(sd, fetched_line=True)}), RID).approved
    p = RuleTablePolicy().propose(state({"server_done": sd}))
    assert p.action == "escalate_to_human" and p.rule_id == "R40"


def test_guard_that_warned_and_continued_R41():
    ge = {"script": "p.py", "check": "frozen core", "outcome": "warned and continued"}
    assert refused_with(check(LAUNCH, state({**READY, "guard_event": ge}), RID), "R41")
    assert check(LAUNCH, state({**READY, "guard_event": dict(ge, outcome="stopped with the reason")}), RID).approved


def test_validation_claim_R34_policy():
    p = RuleTablePolicy().propose(state({"validation_claim": {"text": "validated on benzene", "number": None, "counterpart": None}}))
    assert p.action == "escalate_to_human" and p.rule_id == "R34"
    p = RuleTablePolicy().propose(state({"validation_claim": {"text": "gradient vs FD on water", "number": 1e-7, "counterpart": "finite differences of the energy"}}))
    assert p.action == "wait"


def test_scenarios_s9_to_s17_replay_and_all_seventeen_pass():
    results = {s["id"]: run_scenario(s, RuleTablePolicy(), RULES) for s in SCEN}
    assert [results[f"S{n}"]["actions"][0] for n in range(9, 18)] == ["escalate_to_human"] * 9
    assert [results[f"S{n}"]["rules"][0] for n in range(9, 18)] == [f"R{n}" for n in range(33, 42)]
    assert all(r["pass"] for r in results.values()), [k for k, r in results.items() if not r["pass"]]
