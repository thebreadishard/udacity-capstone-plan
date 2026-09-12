# Module 04 — the calibrated-harmonic baseline (Udacity "Applied Machine Learning")

## Project description

**Supervised regression.** Can a machine-learning model learn the error that NASA's scaled-harmonic
library of computed PAH infrared spectra makes against laboratory band positions, from descriptors of
the band and the molecule alone? The corrected library would be the strongest fair opponent for the
larger capstone project, so the whole recipe — target, join rule, features, four models,
leave-one-molecule-out evaluation, metrics, no tuning, seed 0 — was fixed in `RECIPE.md` and committed
before the first training run.

**What I built:** a builder that joins the computed and the laboratory bands into one training table
(`build_training_table.py`), a notebook that prepares the features, trains and evaluates the models
(`notebook/modeling.ipynb`), and the Machine Learning Analysis Report (`module_summary.pdf`).

**Dataset:** `notebook/training_table.csv`, 2,477 rows × 28 columns — one row per matched pair of a
laboratory band (PAHdb experimental library v3.10, argon matrix,
https://www.astrochemistry.org/pahdb/experimental/3.10) and a computed band (PAHdb theoretical library
v4.00, https://www.astrochemistry.org/pahdb/theoretical/4.00) of the same molecule, 83 molecules.
Target: `y_cm` = laboratory position − scaled computed position. It is a derived table of public
measured and computed science data, not AI-generated, and distinct from the Module 02 dataset (the
computed library alone) and the Module 03 dataset (the laboratory bands alone): the information here
is the *pairing*, which exists in neither.

## How to run the project

```bash
pip install -r requirements.txt
jupyter notebook notebook/modeling.ipynb
```

Run all cells top to bottom (about one minute; 83 folds × 2 fitted models). The notebook is also
rebuilt and executed by `python notebook/make_notebook.py`; the training table is regenerated from
Module 02's parsed libraries by `python build_training_table.py`; the report by `python make_summary.py`
(python-docx plus Microsoft Word for the PDF). `requirements.txt` was created with
`pip freeze > requirements.txt`.

## Files

- `RECIPE.md` — the frozen recipe candidate (committed alone, before training).
- `build_training_table.py` — the join; `out/SUMMARY.md` lists counts, constants and input checksums.
- `notebook/modeling.ipynb` — Load and inspect · Preparation · Model selection and training · Evaluation · Summary;
  writes `model_results.json`, `opponent_column_ladder.csv` (held-out predictions for the project's test
  molecules) and `uncertainty_layer.csv`.
- `module_summary.pdf` (`.docx`) — the Machine Learning Analysis Report in the Udacity APA 7 template
  (the instructions also call it `Machine_Learning_Analysis_Report.pdf`; same document).
- `PROVENANCE.md` — sources, checksums, status, and what is still owed (project notes).
