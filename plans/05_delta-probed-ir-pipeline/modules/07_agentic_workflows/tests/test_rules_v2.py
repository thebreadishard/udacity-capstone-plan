"""rules_v2.json (3 Oct 2026): v1's rules unchanged and in order, the new rules R33–R41 with every field filled and a dated source, ids unique and
sequential, enforce in {gate, reason}; v2 is the default since 3 Oct 2026 (S9–S17 replay 17/17), v1 stays loadable."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
from steward.rules import DEFAULT_RULES, by_id, load_rules  # noqa: E402

FIELDS = ("id", "name", "trigger", "required", "forbidden", "enforce", "source")


def test_v2_extends_v1_without_touching_it():
    v1 = json.load(open(HERE / "rules" / "rules_v1.json", encoding="utf-8"))["rules"]
    v2 = json.load(open(HERE / "rules" / "rules_v2.json", encoding="utf-8"))["rules"]
    assert v2[: len(v1)] == v1
    new = v2[len(v1):]
    assert [r["id"] for r in new] == [f"R{n}" for n in range(33, 33 + len(new))] and len(new) >= 9
    assert len({r["id"] for r in v2}) == len(v2)
    for r in new:
        assert all(r.get(k) for k in FIELDS), r["id"]
        assert r["enforce"] in ("gate", "reason")
        assert "2026" in r["source"], r["id"]


def test_loader_default_is_v2_and_v1_loads():
    assert DEFAULT_RULES.name == "rules_v2.json"
    assert len(load_rules(HERE / "rules" / "rules_v1.json")) == 32
    rules = load_rules(HERE / "rules" / "rules_v2.json")
    rid = by_id(rules)
    assert "R37" in rid and "carried" in rid["R37"]["required"]
    assert rid["R32"]["name"] == "ask the human when a state matches no rule"     # the escalation rule is still there, unchanged
