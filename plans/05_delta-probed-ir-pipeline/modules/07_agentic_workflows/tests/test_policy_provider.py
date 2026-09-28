"""The provider switch of the reasoning node (28 Sep 2026): the endpoint follows the environment, only key *presence* is read, and the OpenAI-compatible
route (the course's Vocareum keys through OPENAI_BASE_URL) is recorded by host name, never by key. No network: `resolve_provider` is pure and the
client objects are built without a call."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from steward.policy import PROVIDERS, LLMPolicy, resolve_provider  # noqa: E402


def test_no_key_refuses():
    with pytest.raises(RuntimeError):
        resolve_provider({})


def test_key_presence_picks_the_provider_and_the_default_model():
    assert resolve_provider({"OPENAI_API_KEY": "voc-x"}) == ("openai", PROVIDERS["openai"][1], "api.openai.com")
    assert resolve_provider({"ANTHROPIC_API_KEY": "k"}) == ("anthropic", PROVIDERS["anthropic"][1], None)
    assert resolve_provider({"ANTHROPIC_API_KEY": "k", "OPENAI_API_KEY": "voc-x"})[0] == "anthropic"          # both present → decision 17's endpoint


def test_explicit_provider_model_and_vocareum_host():
    p, m, host = resolve_provider({"STEWARD_PROVIDER": "openai", "STEWARD_MODEL": "gpt-4.1-mini", "OPENAI_API_KEY": "voc-x",
                                   "OPENAI_BASE_URL": "https://openai.vocareum.com/v1"})
    assert (p, m, host) == ("openai", "gpt-4.1-mini", "openai.vocareum.com")
    with pytest.raises(ValueError):
        resolve_provider({"STEWARD_PROVIDER": "gemini", "OPENAI_API_KEY": "x"})


def test_openai_policy_builds_without_a_call(monkeypatch):
    pytest.importorskip("langchain_openai")
    monkeypatch.setenv("OPENAI_API_KEY", "voc-test-not-a-real-key"); monkeypatch.setenv("OPENAI_BASE_URL", "https://openai.vocareum.com/v1")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False); monkeypatch.delenv("STEWARD_PROVIDER", raising=False); monkeypatch.delenv("STEWARD_MODEL", raising=False)
    pol = LLMPolicy(rules=[])
    assert pol.provider == "openai" and pol.endpoint_host == "openai.vocareum.com" and "voc-" not in pol.name
    assert pol.name == "llm (openai via openai.vocareum.com, structured output)"
