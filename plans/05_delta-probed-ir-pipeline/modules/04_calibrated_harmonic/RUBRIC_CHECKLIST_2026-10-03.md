# Module 04 — rubric checklist (weekend review 2, 3 October 2026)

*What the rubric (Rubrics/04_Applied_Machine_Learning.md, Tasks 1–8 and the grading tables) asks, what exists, what is still missing and
who owes it. The notebook was re-executed on 3 October 2026 with the new follow-up section (0 error outputs; the first run's numbers
reproduced exactly); the first checklist file written for 04.*

| Rubric item | Requirement | Status 3 Oct | Missing / owner |
|---|---|---|---|
| Notebook execution | runs top to bottom, outputs present | **done** — `notebook/modeling.ipynb` written and executed by `notebook/make_notebook.py` (≈ 1 min); metrics tables, three figures, output CSVs | — |
| Data preparation and preprocessing | loaded correctly; missing values, encoding, scaling as the models need | **done** — no missing values (checked), numeric standardisation for ridge, one-hot family, raw features for the trees; the choices stated beside the code | — |
| Model selection and implementation | ≥ 1 supervised model in scikit-learn, appropriate | **done** — ridge regression and `HistGradientBoostingRegressor`, beside two analytic references (zero model, per-family constant), all from the frozen `RECIPE.md` | — |
| Training and evaluation | trained, ≥ 1 appropriate metric, results displayed | **done** — leave-one-molecule-out (83 folds), MAE (primary), RMSE, R², share within 5 cm⁻¹; per family and per ladder molecule; `model_results.json` (tracked since 3 Oct) | — |
| Reproducibility | `pip freeze` file | **done** — `requirements.txt` of 12 Sep | regenerate only if the environment changes before submission |
| Evaluation metrics justification (report) | why these metrics | **done** — "Modeling Approach": MAE because the plan scores per-band absolute error; RMSE and R² beside it; the within-5 share as the practical reading | — |
| Results interpretation (report) | actual results explained | **done** — "Results": no model learns the error; the two diagnostics (instance-level split, offset-versus-scatter decomposition); **the follow-up paragraph of 3 Oct (early stopping, decision 51)** | — |
| Model limitations and trade-offs (report) | ≥ 1 limitation and its impact | **done** — "Limitations": the join as a model (≈ 11 % of pairs above 15 cm⁻¹), matrix not gas phase, 83 molecules ≤ 50 carbons, unequal band reliability | — |
| Bias and responsible use (report) | ≥ 1 bias/ethical concern and one step taken | **done** — selection of measured molecules; the author's interest in a weak baseline, countered by the recipe committed before training | — |
| Notebook organisation | headings for preparation, modelling, evaluation, outputs | **done** — Load and inspect · Preparation · Model selection and training · Evaluation · Follow-up (3 Oct) · Summary | — |
| Code readability and documentation | readable, docstrings/comments | **done** — `make_models` docstring, commented diagnostics; the builder is ruff-clean under the repository hook | — |
| Written analysis quality (report) | clear for technical and non-technical readers | **done** — "Interpretation for a Non-Technical Audience" plus the technical sections; rebuilt 3 Oct with the follow-up paragraph | — |
| Citations (report) | in-text citations, consistent References | **done** — APA author–year (Friedman 2001, Roberts et al. 2017, Hudgins & Sandford 1998, …), References section | — |
| Workflow completeness | complete, professional, portfolio-ready | **done** — recipe → builder → table → notebook → report, all regenerable; early-stopping rule applied as a dated follow-up (decision 51) | the student's own pass before submission |

## Open points (not rubric failures)

- **Baseline column.** By the recipe's rule as written, the early-stopping run makes the trees the lowest-MAE model (6.34 against ridge
  6.40). The RECIPE leaves that choice to the pilot note; the ridge column stands until the note says otherwise (PROVENANCE, Owed).
- **Zenodo release of `training_table.csv`** (reading 1): the deposit tooling exists since 3 Oct (`tools/zenodo_deposit.py`); the
  deposit and the click are the student's, after paper D's data release.

- Lay-reader pass done 4 Oct 2026 (TASKS item 20): the target, the scale factor, the matrix and the evaluation explained in plain words in README, notebook and report; `modules/GLOSSARY.md` linked. Notebook and report rebuilt.
