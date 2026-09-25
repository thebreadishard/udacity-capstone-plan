"""The rule table: the project's paid-for lessons as data. Loaded once; the reasoning step reads it whole, the gate uses the ids."""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_RULES = HERE.parent / "rules" / "rules_v1.json"


def load_rules(path: Path | str = DEFAULT_RULES) -> list[dict]:
    d = json.load(open(path, encoding="utf-8"))
    rules = d["rules"]
    ids = [r["id"] for r in rules]
    assert len(ids) == len(set(ids)), "duplicate rule ids"
    return rules


def by_id(rules: list[dict]) -> dict[str, dict]:
    return {r["id"]: r for r in rules}


def rules_as_text(rules: list[dict]) -> str:
    """Compact rendering for the reasoning step's prompt: id, name, trigger, required, forbidden."""
    return "\n".join(f"{r['id']} {r['name']} — when: {r['trigger']} — do: {r['required']} — never: {r['forbidden']}" for r in rules)
