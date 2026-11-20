# Module 08 — rubric checklist (28 September 2026, 20:1x)

| Rubric asks | Where | Status |
|---|---|---|
| integrated AI system integrating ≥ 3 prior projects, intentional | `m08/` reads module 03 (tolerances), 05 (the network, its measured error and the licence), 06 (candidate), 07 (gate + rules); README §What it is; paper §3 | done (four in code; corrected 20 Nov 2026: module 04 is part of the paper's reasoning, no code reads its output) |
| cross-domain: data analysis, ML, DL, generative, agentic | 03, 05, 06 and 07 in code; 04 (machine learning) in the paper's reasoning: its result is why the cheap rung is shown with the laboratory tolerance (corrected 20 Nov 2026) | done |
| execution: runs as intended, observable outputs | `run_scenarios.py` 8/8; certificates in `out/certificates/`; ledger `out/requests_ledger.csv`; notebook §3 | done (S6 run 11 Oct: passes on the published site, `out/s6_accessibility_2026-10-11.json`) |
| industry problem definition | notebook header; paper §1; `DESIGN_2026-09-27.md` §1 | done |
| design rationale tied to prior work | paper §3–4; notebook §2 | done |
| trade-offs and constraints | paper §4; notebook §4 | done |
| ethical concern grounded in the industry and design | paper §5; notebook §5 (certified-looking spectrum for an unreached rung; refusal as first-class output) | done |
| responsible deployment reasoning | paper §5 (allow-list, gate, ledger, licence, cost record); `PRE_REGISTRATION.md` decisions 1–2 | done |
| synthesis paper 1,500–2,000 words, eight sections, professional audience | `Reflective_Synthesis_Paper.pdf` (the script prints the count and refuses outside the range; 1,948 body words on 20 Nov 2026, on interim results) | done |
| evidence-based reflection | every number in the paper from `notebook/results.json`; the failure case S8 and the S4c incident | done |
| citations: ≥ 3 credible, ≥ 1 scholarly, consistent style | four references (Mackie 2015 JCP; Ricca 2026 ApJS; Mitchell 2019 FAT*; Shavit 2023) in APA 7 | done |
| portfolio value | the public Spectrum Atlas + this service + the paper | done (atlas live since 24 Sep) |
| documentation and reproducibility; `requirements.txt` by `pip freeze` | `README.md`, `PROVENANCE.md`, `requirements.txt` (system Python 3.14, 103 lines: the `pip freeze` of 28 Sep 2026, frozen again at the snapshot build — noted 20 Nov 2026) | done |
| supporting diagrams and design files | `DESIGN_2026-09-27.md` §3 (system diagram); notebook §2 (officer → gate → worker → certificate); `figures/` | done |
| mentor presentation and defense (15 min) | not part of this build; the notebook's §1–5 are the storyline | owed on the day |

**Owed before submission (corrected 20 Nov 2026).** None of the three items listed here on 28 September is owed any more: the licence
is decision 65's and is read from the carried network's records; the CC-level test of the standout's plan line was run on 28 September and
failed, so the line stays "proxy" (`PRE_REGISTRATION.md`); no live worker is promised. Owed now: the final scenario run
(`run_scenarios.py --with-catalog`), the notebook and the paper rebuilt on it, the snapshot build with `steward/` and a fresh
`requirements.txt`, the open point of the standalone plan (module 05's code on the import path), the dry run of
`tools/make_module_repo.sh`, and the mentor presentation.

## Status 2026-10-03 18:1x — weekend review 2

- README status rewritten to the current state. Atlas republished 2 Oct (843 molecules, four CC anchors); the user's phone pass of 3 Oct closes the manual half of S6 (search, molecule page, 3D view); the axe half still needs the built site.
- Decision 52's pricing rule ('its family first') is a design input for the price table, not yet implemented in `m08/`; listed for the full weekend pass.
- Scenarios, tests, notebook and paper unchanged since 28 Sep; the rubric items are re-ticked in the full pass.

- Lay-reader pass done 4 Oct 2026 (TASKS item 20): a plain-language opening in README, notebook (builder and the executed notebook's markdown) and report; `modules/GLOSSARY.md` linked; the report rebuilt; the notebook re-executed after the TZ run (decision 58, text and execution split).

## Status 20 November 2026 08:18 — the checklist under decisions 63, 65 and 66

- Rows corrected today, each marked: the integration row (four modules in code, not five), the cross-domain row, the paper's word
  count, `requirements.txt`, and the "Owed before submission" paragraph.
- The notebook and the paper were rewritten and rebuilt on interim scenario results (`PROVENANCE.md`, addendum of 20 November 2026); both are
  rebuilt on the final run. `SUBMISSION.txt` and the README's Files and Repository sections exist.
- Not checked today: whether the paper needs an explicit "Evaluation and Reflection" heading (`modules/REVIEW_2026-10-17.md:76`).
