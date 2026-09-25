# Module 07 — provenance

Every number in the notebook and the report traces to a file named here. Dated notes are appended; nothing above them is rewritten.

- **Rule table** `rules/rules_v1.json` (25 Sep 2026): 32 rules compiled from `QUALITY_POLICY.md` (incident → guard table), `CLAUDE.md`, the user's feedback
  notes and the obstacle ledger; 22 enforced by the gate, 10 by the reasoning step. Each rule names its source incident.
- **Code** `steward/`: `schema.py` (closed allow-list of 11 actions; `Proposal`), `rules.py`, `gate.py` (deterministic checks R01, R04, R05, R06, R14, R21, R24, R25, R32
  and a launch budget), `tools.py` (`ReplayTools`: observations from fixtures, effects declared by the scenario; instruction scan for R24), `policy.py`
  (`RuleTablePolicy` deterministic reference; `LLMPolicy` = `langchain_anthropic.ChatAnthropic` with structured output, temperature 0, model id in every reason),
  `graph.py` (LangGraph `StateGraph`: observe → propose → gate → act → record → loop/END). Versions: langgraph 1.2.12, langchain-core 1.6.5, langchain-anthropic 1.7.4
  in the repository's `.venv` (Python 3.13.9).
- **Scenarios** `scenarios/scenarios.json` (S1–S8, pre-registered in `DESIGN_2026-09-25.md`), fixtures `scenarios/fixtures/*.txt` = verbatim excerpts of the logs of
  25 September 2026 fetched from hel1-16 and the CCX53 (S8's instruction line is synthetic and marked so).
- **Tests** `tests/test_gate.py`: 11 tests — negative controls per guard (a launch without a dry run, a second instance, a live or foreign lock, a reading without its
  control, a fresh checkpoint, an observed instruction, human-gated arguments, an unknown rule id) and the replay of all eight scenarios with the deterministic policy.
- **Runs** `run_scenarios.py --policy rules` → `out/scenario_results_2026-09-25_rules.json`: **8/8 pass** (17:5x). `--policy llm` not run yet: needs `ANTHROPIC_API_KEY`
  (the user's; not set in this environment). Nothing touches a machine in replay mode.

**Dated note 17:5x — first build.** Package, gate, replay tools, deterministic policy, LangGraph graph, scenarios and tests written and green on the first
evening after the user's "bouw maar zodra het rustig is"; the LLM policy is written and untested; notebook, report, diagram and `requirements.txt` follow.

**Dated note 18:1x — deliverables.** `notebook/make_notebook.py` → `agentic_system.ipynb` executed top to bottom in the `.venv` (Tasks 1–5; the replay of S1–S8 inside the notebook: 8/8; `results.json`, `figures/architecture.png` drawn by matplotlib from the graph's structure). `make_summary.py` → `Agentic_AI_System_Design_Report.docx/.pdf` (APA 7 template, seven sections, eight references: Amodei 2016, Greshake 2023, Mitchell 2019, Schick 2023, Shavit 2023, Wang 2024, Xi 2023, Yao 2023). `requirements.txt` = `pip freeze` of the `.venv` (99 lines). `RUBRIC_CHECKLIST_2026-09-25.md`. Not yet: the LLM-policy run (needs the user's key); the report's paragraph for it fills itself from `results.json`.
