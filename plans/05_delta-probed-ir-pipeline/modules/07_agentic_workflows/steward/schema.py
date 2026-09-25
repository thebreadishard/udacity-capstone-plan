"""Action allow-list and the proposal schema. Anything not listed here cannot be executed, whatever the reasoning step proposes."""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

# The complete allow-list. Creating/deleting machines, spending, publishing, changing a rule, verdicts and deletes are NOT here on purpose (rule R25).
ACTIONS = {
    "status": "read the status of a host or job (remote_status); args: host, job",
    "read_result": "read a whitelisted result file; args: path",
    "check_runner": "list processes of a job family on a host with a self-safe pattern; args: host, pattern",
    "remove_stale_lock": "remove a lock file whose recorded pid is dead on the same host; args: host, lock_path",
    "dry_run": "run a job's command file with its dry-run arguments; args: host, job",
    "launch": "start a job once, detached, after a passed dry run; args: host, job",
    "retry_failed": "queue the registered retry of failed rows at the end of a shard; args: host, job, ids",
    "record_reading": "record a result read against its registered rule; args: result_path, statistic, value, control_value",
    "record_ledger": "append a dated ledger line; args: text",
    "wait": "do nothing until the next observation; args: minutes",
    "escalate_to_human": "notify the human with the observation quoted and the candidate rules; args: message, quote",
}

ActionName = Literal[
    "status", "read_result", "check_runner", "remove_stale_lock", "dry_run", "launch", "retry_failed",
    "record_reading", "record_ledger", "wait", "escalate_to_human",
]


class Proposal(BaseModel):
    """One proposed step: the action, its arguments, the rule it applies and a one-sentence reason (structured output of the reasoning step)."""

    action: str = Field(description="one of the allow-listed actions, or anything else — which the gate will refuse")
    args: dict = Field(default_factory=dict)
    rule_id: Optional[str] = Field(default=None, description="the id of the rule in rules_v1.json this step applies, e.g. R01")
    reason: str = Field(default="", description="one sentence, quoting the observation it answers")


class GateResult(BaseModel):
    approved: bool
    reasons: list[str] = Field(default_factory=list)
    forced_action: Optional[Proposal] = Field(default=None, description="what the gate substitutes when it refuses (wait or escalate)")
