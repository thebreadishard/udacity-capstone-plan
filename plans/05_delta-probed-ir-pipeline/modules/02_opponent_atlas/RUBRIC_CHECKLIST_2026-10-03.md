# Module 02 — rubric checklist (weekend review 2, 3 October 2026)

*What the rubric (Rubrics/02_AI_Programming_Foundations_Project.md, Tasks 1–10 and the grading table) asks, what exists, what is still
missing and who owes it. Evidence is a file or a cell, never a memory. The notebook was re-read and its outputs counted on 3 October 2026
(22 cells, 0 error outputs); the first module checklist written for 02 — the desk pass of 22 September left no checklist file here.*

| Rubric item | Requirement | Status 3 Oct | Missing / owner |
|---|---|---|---|
| Notebook execution | runs top to bottom without errors | **done** — `notebook/data_workflow.ipynb` is written and executed by `notebook/make_notebook.py`; last execution 22 Sep (packaging change only), 0 error outputs; everything it reads is in the repository (`bands_derived/`, species CSV) | — |
| Data ingestion | loads with pandas, first rows displayed | **done** — Ingestion section: `pd.read_csv` of `species_pahdb_theoretical_4.00.csv` (10,749 × 27), `head()` shown | — |
| Data cleaning functions | ≥ 2, defined and used, docstrings | **done** — `split_charge_suffix` and `flag_unresolved_basis`, both with docstrings, both applied | — |
| Exploratory analysis function | ≥ 1 EDA function defined and used | **done** — `coverage_summary` (species per ladder rung per comparison line), docstring, used for Figure 4 | — |
| Visualizations | ≥ 3 with title and labelled axes | **done** — five figures (size × charge histogram, scale factors, positions by family, ladder coverage, C₃₈₄H₄₈ sticks), each with `set_title` and both axis labels | — |
| Reproducibility | `requirements.txt` from `pip freeze` | **done** — file of 11 Sep (`pip freeze`); rebuilt notebook ran in that environment on 22 Sep | regenerate only if the environment changes before submission |
| Cleaning justification | why each step was needed | **done** — the Cleaning section's markdown states what each of the two steps fixes; the README's bias answer gives the consequence of skipping each (double counting; a wrong 4-31G boundary) | — |
| Visualization interpretation | one accurate reading per figure | **done** — a "Figure n interpretation" paragraph under each of the five figures | — |
| Summary & interpretation | insights, patterns, assumptions, limitations in sentences | **done** — Summary cell (four paragraphs: taught, patterns, assumptions/limitations, surprising) | — |
| Bias awareness | README answer on poor cleaning → bias | **done** — README "Where could poor data cleaning introduce bias?" (three concrete places) | — |
| Required sections with headings | Setup, Ingestion, Cleaning, EDA, Visualizations, Summary | **done** — headings in that order | — |
| Docstrings and formatting | every student function documented, readable code | **done** — the three functions; the builder is ruff-clean under the repository hook | — |
| README | description, run instructions, all reflection questions | **done** — description, dataset, how to run, four reflection answers, Files, Repository (Files section replaces the dated addendum, 3 Oct) | — |
| Git/GitHub usage | multiple commits, ≥ 1 branch beyond main | **done in this repository** — branch `module-02-opponent-atlas` merged into `master`, many commits | **the rubric's Task 2 names the repository `ai-programming-foundations-project` with at least two branches; the name is free since 22 Sep — the student creates it from this folder at submission (user's action)** |
| Future integration reflections | ML workflow, neural-network preparation, agentic automation | **done** — the three README answers | — |
| Workflow completeness | professional, reusable workflow | **done** — parser → tables → notebook → report, all regenerable (`build_opponent_atlas.py`, `make_bands_derived.py`, `make_notebook.py`, `make_summary.py`) | — |
| Summary report with citations (Task 10) | `module_summary.pdf` in the APA 7 template, Danchev (2022) cited | **done** — built 11 Sep from the same numbers the notebook prints; the 22 Sep notebook rebuild changed packaging, not a number | the student's own pass before submission |

## Open points (not rubric failures)

- The repository name and branch count of Task 2 are a submission-time action (above).
- Line D (the 2026 machine-learning PAH-IR predictors, PROVENANCE's dated note of 13 Sep) is not a row in the atlas; it is
  outside the rubric and belongs to the plan's opponents table, where paper D's claim already cites those works.

- Lay-reader pass done 4 Oct 2026 (TASKS item 20): plain-language opening in README, notebook and report; basis set, scale factor, charge names and cm⁻¹ explained at first use; `modules/GLOSSARY.md` linked. Notebook and report rebuilt.
