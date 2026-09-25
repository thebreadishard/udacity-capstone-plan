# Module 07 — rubric checklist (25 September 2026, 18:1x)

| Task | Rubric asks | Where | Status |
|---|---|---|---|
| 1 | agentic task, scope, boundaries; single/multi-agent; decisions and tools | notebook header; `DESIGN_2026-09-25.md` §Scope | done |
| 2 | components (persona, loop, memory, tools); architecture diagram; design choices and tradeoffs | notebook §2 + `figures/architecture.png`; report §Architecture | done |
| 3 | initialisation, decision logic, state, tool invocation, safeguards; executes as intended | `steward/` (schema, rules, gate, tools, policy, graph); notebook §3 | done (replay mode) |
| 4 | example runs, observable outputs, reasoning notes, ≥ 1 limitation or failure | notebook §4 (8 scenarios, ledgers, escalations) + §4.1 (S3 repetition bug, brittleness, untested LLM policy) | done for the deterministic policy; **LLM policy pending the user's Anthropic key** (`M07_LLM=1`) |
| 5 | 4–6 sentence summary | notebook §5 | done |
| 6 | report with the seven sections and academic citations | `Agentic_AI_System_Design_Report.docx/.pdf` (`make_summary.py`; 8 references) | done; LLM paragraph fills itself from `results.json` when the key run exists |
| 7 | `requirements.txt` by `pip freeze` | `requirements.txt` (the repository's `.venv`, Python 3.13.9) | done |
| — | uses tools covered in the course | LangGraph (the LangChain/LangGraph elective), decision of 5 Sep 2026; Anthropic API endpoint (decision 17) | done |
| — | not reused from a previous capstone project | first agent of any of the plans | done |

**Owed before submission:** the LLM-policy run (three repeats, temperature 0, model id logged) and its numbers in notebook §4 and the report; a second reader's pass over the gate
with the diff only (quality policy, promotion item 7) if the steward ever runs live; the diagram redrawn in the project's diagram conventions if the mentor asks for the sheet form.
