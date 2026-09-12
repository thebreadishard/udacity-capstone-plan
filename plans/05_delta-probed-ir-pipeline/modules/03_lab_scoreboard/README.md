# Module 03 — the laboratory scoreboard (Udacity "Conduct a Statistical Analysis Using Python")

## Project description

A statistical analysis of laboratory infrared band positions of polycyclic aromatic hydrocarbons
(PAHs) measured in two ways: frozen in an argon matrix at 10 K (NASA's PAHdb experimental library)
and as a hot vapour (NIST Chemistry WebBook gas-phase records). The analytical question, fixed in
`PRE_REGISTRATION.md` before any matrix band was paired with a gas peak: **is the offset between a
band's matrix position and its gas-phase position zero, per band family?** The answer feeds the larger
capstone project, whose own predictions will later be scored against exactly these laboratory numbers.

**What I built:** a builder that turns the two sources into one tidy band table and forms the
matrix–gas pairs under the pre-registered rule (`build_lab_tables.py`), a notebook with descriptive
statistics, three visual models and one pre-registered hypothesis test (`notebook/analysis.ipynb`),
and the Statistical Analysis Report (`module_summary.pdf`).

**Dataset:** `notebook/bands_lab.csv`, 4,218 rows × 31 columns (21 at the first build; ten u_band columns added on 12 September, see below) — every band of the PAHdb
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

Run all cells top to bottom. The notebook is also rebuilt and executed by
`python notebook/make_notebook.py`; the dataset and the pairs are regenerated from the sources already
in this repository by `python build_lab_tables.py`; the report is rebuilt by `python make_summary.py`
(python-docx plus Microsoft Word for the PDF). `requirements.txt` was created with
`pip freeze > requirements.txt`.

## Files

- `PRE_REGISTRATION.md` — the frozen test form (committed alone, before the join was computed).
- `build_lab_tables.py` — dataset and pairs; `out/SUMMARY.md` lists counts, constants and input checksums.
- `notebook/analysis.ipynb` — Load · Descriptive statistics · Visual models · Hypothesis test · Summary.
- `notebook/test_results.json` — the test output the report's table is built from.
- `module_summary.pdf` (`.docx`) — the Statistical Analysis Report in the Udacity APA 7 template; the
  instructions also call this file `Statistical_Analysis_Report.pdf` — it is the same document.
- `PROVENANCE.md` — sources, versions, checksums, status and what is still owed (project notes).
