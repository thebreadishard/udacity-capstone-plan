"""The run steward — module 07's bounded agent (LangGraph; 25 September 2026).

A single agent that keeps a pre-registered computational campaign moving: it observes machines and result files, proposes ONE action that
cites a rule from `rules/rules_v1.json`, passes it through a deterministic gate, acts through allow-listed tools, and records every step in
a ledger. The LLM proposes, code disposes. Replay mode runs the eight pre-registered scenarios on the real log excerpts of 25 September 2026
without touching any machine."""
