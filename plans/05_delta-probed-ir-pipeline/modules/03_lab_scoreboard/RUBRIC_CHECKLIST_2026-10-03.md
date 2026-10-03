# Module 03 — rubric checklist (weekend review 2, 3 October 2026)

*What the rubric (Rubrics/03_Conduct_a_Statistical_Analysis_Using_Python.md, Tasks 1–8 and the grading tables) asks, what exists, what is
still missing and who owes it. The notebook was re-executed on 3 October 2026 after a text fix (17 cells, 0 error outputs, every number
identical to the run of 12 September); the first checklist file written for 03.*

| Rubric item | Requirement | Status 3 Oct | Missing / owner |
|---|---|---|---|
| Data ingestion | dataset loads and displays | **done** — Load section: `bands_lab.csv` (4,218 × 31), `head()` and dtypes shown | — |
| Descriptive statistics | summary statistics, categorical counts, distributions | **done** — `describe()` of the numeric columns, `value_counts` of phase/role/family, per-phase frequency distribution | — |
| Visualizations | ≥ 3 visual models, titles and labelled axes | **done** — positions by phase, offsets per family, offset against position (Figures 1–3) | — |
| Hypothesis test | one valid test with hypotheses, statistic, p-value | **done** — pre-registered Wilcoxon signed-rank test of a zero matrix−gas offset per family, H0/H1 stated, statistic and p per family, Holm correction, pooled secondary test; `test_results.json` (tracked since 3 Oct) | — |
| Notebook summary | findings and challenges | **done** — Summary cell (eight NIST WebBook records plus the four benzene scoreboard bands; count corrected 3 Oct) | — |
| Reproducibility | `pip freeze` file | **done** — `requirements.txt` of 11 Sep | regenerate only if the environment changes before submission |
| Interpretation of statistics (report) | descriptive statistics read accurately | **done** — report "Results" reads the counts and distributions from the CSVs | — |
| Test selection justification (report) | why this test fits data and question | **done** — "Methods": paired, non-normal offsets, small n per family → Wilcoxon; Holm for six families | — |
| Results interpretation (report) | test results and figure patterns read correctly | **done** — "Results": six families reject after Holm, two inconclusive by construction, the sign's consistency | — |
| Limitations and bias (report) | ≥ 1 limitation, ≥ 1 bias source, explained | **done** — "Limitations and Potential Bias": matrix shift and hot-band shift inseparable; four molecules carry the result; the join rule as a model | — |
| Citations (report) | concepts, methods, assumptions cited; references section | **done** — APA author–year in text, References list verified against Crossref/DataCite (Lusa et al. 2024 included) | — |
| Report organisation | all sections, clear | **done** — Overview · Dataset · Methods · Results · Non-technical interpretation · Limitations and bias · References; `module_summary.pdf` = `Statistical_Analysis_Report.pdf` | — |
| Non-technical explanation | plain-language findings | **done** — "Interpretation for a Non-Technical Audience" | — |
| Dataset appropriateness | public, measured, fit for statistics and a test | **done** — PAHdb experimental 3.10 + NIST WebBook, not synthetic, not the module 02 dataset (stated in notebook and report) | — |
| Visual-model comparison (design justification) | what each visual model reveals, which best supports the question | **done** — the "Comparing the three visual models" paragraph reads each figure and names Figure 2 as the model that answers the question, because the question is asked per family | — |
| Workflow completeness | complete, professional, portfolio-ready | **done** — pre-registration → builder → dataset → notebook → report, all regenerable | the student's own pass before submission |

## Open points (not rubric failures)

- The report (22 Sep build) and the notebook (3 Oct re-execution) print the same numbers; no report rebuild was needed for the text fix,
  which touched the notebook summary and the README only.
