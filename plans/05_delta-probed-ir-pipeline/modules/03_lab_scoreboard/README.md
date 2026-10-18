# Module 03 — the laboratory scoreboard (Udacity "Conduct a Statistical Analysis Using Python")

## Project description

A statistical analysis of laboratory infrared band positions of polycyclic aromatic hydrocarbons
(PAHs) measured in two ways: frozen in an argon matrix at 10 K (NASA's PAHdb experimental library)
and as a hot vapour (NIST Chemistry WebBook gas-phase records). The analytical question, fixed in
`PRE_REGISTRATION.md` before any matrix band was paired with a gas peak: **is the offset between a
band's matrix position and its gas-phase position zero, per band family?** The answer feeds the larger
capstone project, whose own predictions will later be scored against exactly these laboratory numbers.

*For readers without chemistry:* a molecule's infrared spectrum is the list of colours at which it absorbs infrared light (positions, in the unit
cm⁻¹) and how strongly (intensities). Laboratories measure these spectra in two ways: with the molecules frozen into solid argon at −263 °C (a
*matrix*), which is precise but can shift the positions slightly, or as a hot vapour (*gas phase*), which is closer to the conditions in space but
blurrier. This module asks, for each kind of vibration, whether the two agree, because the project's own predictions will be judged against these
numbers. The statistical test is a rank test (Wilcoxon) that asks whether the shifts are centred on zero without assuming a bell curve; the Holm
correction accounts for asking that question six times at once. One-line definitions of the terms are in the [glossary](https://github.com/thebreadishard/udacity-capstone-plan/blob/master/plans/05_delta-probed-ir-pipeline/modules/GLOSSARY.md).

**What I built:** a notebook with descriptive statistics, three visual models and one pre-registered
hypothesis test (`notebook/analysis.ipynb`), and the Statistical Analysis Report
(`Statistical_Analysis_Report.pdf`, also as `module_summary.pdf`). The tidy band table and the
matrix–gas pairs the notebook reads were made by a builder script that stays in the plan's repository
(see *Where the data come from* below).

**Dataset:** `notebook/bands_lab.csv`, 4,218 rows × 31 columns — every band of the PAHdb
*experimental* library v3.10 (https://www.astrochemistry.org/pahdb/experimental/3.10, 84 species,
3,896 bands) plus the peaks of eight gas-phase NIST Chemistry WebBook records
(https://webbook.nist.gov/chemistry/, six PAHs) and the four benzene bands of the project's
quantitative scoreboard. The pairs used by the test are in `notebook/pairs_matrix_gas.csv` (74 rows).
These are laboratory measurements, publicly available before this project started, not synthetic, not
AI-generated, and not the Module 02 dataset (which was the *computed* PAHdb library).

## How to run the project

```bash
pip install -r requirements.txt
jupyter notebook notebook/analysis.ipynb
```

Run all cells top to bottom. The notebook needs only the files in `notebook/`; before submission it was
executed in a fresh clone of this repository, with nothing else present. `requirements.txt` was created with
`pip freeze > requirements.txt`.

### Where the data come from

The dataset and the pairs were made by `build_lab_tables.py`, which reads the parsed PAHdb experimental tables
and the NIST WebBook cache; it stays in the plan's repository, in the module's folder
[`modules/03_lab_scoreboard`](https://github.com/thebreadishard/udacity-capstone-plan/tree/master/plans/05_delta-probed-ir-pipeline/modules/03_lab_scoreboard), together with `notebook/make_notebook.py`
(writes and executes this notebook), `make_summary.py` (builds the report), the module's further band-list scripts
and `PROVENANCE.md` (sources, versions, checksums).

## Files

- `PRE_REGISTRATION.md` — the frozen test form (committed alone, before the join was computed).
- `notebook/analysis.ipynb` — Load · Descriptive statistics · Visual models · Hypothesis test · Summary.
- `notebook/bands_lab.csv` — the dataset: one row per laboratory band (4,218 rows × 31 columns).
- `notebook/pairs_matrix_gas.csv` — the matrix–gas pairs formed under the pre-registered rule.
- `notebook/test_results.json` — the test output the report's table is built from.
- `notebook/figures/` — the three figures, as the notebook writes them.
- `Statistical_Analysis_Report.pdf` — the Statistical Analysis Report in the Udacity APA 7 template; `module_summary.pdf` is the same file
  under the name the rubric's overview uses.
- `SUBMISSION.txt` — the list of files this repository holds.
