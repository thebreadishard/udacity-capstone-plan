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

## Status 2026-10-03 18:2x — weekend review 2

- README status rewritten to the current state. `rules/rules_v2.json` = v1 + R33–R41 (the week's incidents and decisions, sourced); scenarios S1–S8 still replay v1; the new rules' scenarios and the switch of the default are the full pass's work.
- The LLM-policy run still waits for a key (Vocareum or Anthropic); the deterministic policy's 8/8 and the 11 tests unchanged.

## Status 2026-10-03 23:4x — the full pass's work on 07 done

- Scenarios S9–S17 for R33–R41 written from the week's records and registered before the branches (DESIGN amendment 23:4x); baseline under the v1
  default 0 of 9 (`out/scenario_results_2026-10-03_rules_v1_baseline.json`: four launched, three waited, two recorded the same reading at every
  step — the repeat-yourself bug of S3 in a second place, fixed with R27 in the reading branch).
- Policy branches and gate checks for the nine rules; `tests/test_gate_v2.py` (12 tests: a negative control per gate check, the policy branches,
  the replay); 29 tests green; `run_scenarios.py` 17/17 (`out/scenario_results_2026-10-03_rules.json`); `rules_v2.json` is the default, v1 loads.
- Notebook rebuilt (19 cells, 0 errors; sections 1, 4, 4.1 and 5 updated), report rebuilt with the seventeen-scenario table. The LLM-policy run
  still waits for a key the user sets (Task 4's own-model run); the deterministic policy is the reference.

- Lay-reader pass done 4 Oct 2026 (TASKS item 20): a plain-language opening in README, notebook (builder and the executed notebook's markdown) and report; `modules/GLOSSARY.md` linked; the report rebuilt; the notebook re-executed after the TZ run (decision 58, text and execution split).

## Status 2026-11-20 — after a re-read against the rubric (text fixes only; nothing executed)

The table at the top is the state of 25 September and is left as written. Where it is out of date, the files say:

- **Task 4.** The row says "8 scenarios". There are 17 (S1–S17 in `scenarios/scenarios.json`; the notebook's section 4 replays all
  seventeen), 17/17 with the deterministic policy. The LLM-policy run is still pending: `notebook/results.json` has
  `"llm_policy": null` and notebook, report and README say so.
- **Notebook.** 20 cells (9 code cells, execution counts 1–9 in order, 0 error outputs), last executed on 17 October 2026
  (20:31 UTC); the entry of 3 October above counts 19.
- **Task 6, the report's name.** The rubric uses three names: `module_summary.pdf` (its line 124),
  `Agentic_AI_Systems_Analysis_Report.pdf` (line 171, the submission checklist) and `Agentic_AI_System_Design_Report.pdf` (lines 437
  and 521). The report now ships under all three; the two new files are byte copies and must be copied again after every rebuild.
- **Task 7.** The README's run line was `jupyter notebook …`, but `requirements.txt` has no `notebook` package; it now uses
  `jupyter execute` (nbclient is in the file). The tests' docstrings and the README no longer point at plan-repository paths.
- **Tests.** 29 test functions (11 + 12 + 4 + 2).

Open:

- **Owed before submission, unchanged: the LLM-policy run** (`M07_LLM=1` with a key I set), then notebook and report rebuilt. Until
  then the report's evaluation section says its language-model numbers are still to come.
- **Task 6, the report's sections.** `make_summary.py` writes eight headings (Overview · System Architecture and Design · Decision
  Logic and Behavior · Safety, Reliability, and Transparency · Observed Behavior and Limitations · Ethical and Responsible Use
  Considerations · Future Improvements · References); the rubric's submission checklist (lines 172–182) lists ten. Writing plus a
  rebuild of the report.
- **Task 7.** `requirements.txt` is the freeze of the project's shared `.venv` and holds packages the module does not use (rdkit, ase,
  playwright); a freeze of a clean environment is owed.
- The fresh-clone check with the new `SUBMISSION.txt`, and my own pass over notebook, README and report.
