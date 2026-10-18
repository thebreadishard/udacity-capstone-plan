# Module 04 — the calibrated-harmonic baseline (Udacity "Applied Machine Learning")

## Project description

**Supervised regression.** Can a machine-learning model learn the error that NASA's scaled-harmonic
library of computed PAH infrared spectra makes against laboratory band positions, from descriptors of
the band and the molecule alone? The corrected library would be the strongest fair opponent for the
larger capstone project, so the whole recipe — target, join rule, features, four models,
leave-one-molecule-out evaluation, metrics, no tuning, seed 0 — was fixed in `RECIPE.md` and committed
before the first training run.

*For readers without chemistry:* a molecule's infrared spectrum is the list of colours (band positions, in the unit cm⁻¹) at which it absorbs
infrared light. NASA's library predicts these positions by computer and multiplies them by a fixed number slightly below one (a *scale factor*) to
bring them closer to measurements. The question here is whether a machine-learning model can predict the error that remains, band by band, from
simple facts about the band and its molecule — so that the library could be corrected without new physics. Each model is judged on molecules it
never saw (*leave-one-molecule-out*), by how far its corrected positions still are from the laboratory ones (the mean absolute error, in cm⁻¹). The
answer is no: the remaining error is band-to-band scatter that those facts do not capture. One-line definitions are in the [glossary](https://github.com/thebreadishard/udacity-capstone-plan/blob/master/plans/05_delta-probed-ir-pipeline/modules/GLOSSARY.md).

**What I built:** a notebook that prepares the features, trains and evaluates the models
(`notebook/modeling.ipynb`), and the Machine Learning Analysis Report (`Machine_Learning_Analysis_Report.pdf`, also as `module_summary.pdf`).
The training table was made by a builder that joins the computed and the laboratory bands; it stays in the plan's repository (see
*Where the data come from* below).

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

Run all cells top to bottom (about one minute; 83 folds × 2 fitted models). The notebook needs only the
files in `notebook/`; before submission it was executed in a fresh clone of this repository, with nothing else
present. `requirements.txt` was created with `pip freeze > requirements.txt`.

### Where the data come from

The training table was made by `build_training_table.py`, which joins the two parsed PAHdb libraries; it stays in
the plan's repository, in the module's folder [`modules/04_calibrated_harmonic`](https://github.com/thebreadishard/udacity-capstone-plan/tree/master/plans/05_delta-probed-ir-pipeline/modules/04_calibrated_harmonic),
together with `notebook/make_notebook.py` (writes and executes this notebook), `make_summary.py` (builds the
report) and `PROVENANCE.md` (sources, checksums and the table's distinctness from the Module 02 and 03 datasets).

## Files

- `RECIPE.md` — the frozen recipe candidate (committed alone, before training).
- `notebook/modeling.ipynb` — Load and inspect · Preparation · Model selection and training · Evaluation · Follow-up of
  3 October 2026 (the tree model with early stopping under the project's decision 51; the first run's numbers stand) · Summary.
- `notebook/training_table.csv` — the dataset (2,477 rows × 28 columns).
- `notebook/model_results.json`, `notebook/opponent_column_ladder.csv` (held-out predictions for the project's test molecules),
  `notebook/uncertainty_layer.csv` — what the notebook writes.
- `notebook/figures/` — the three figures, as the notebook writes them.
- `Machine_Learning_Analysis_Report.pdf` — the Machine Learning Analysis Report in the Udacity APA 7 template; `module_summary.pdf` is the
  same file under the name the rubric's overview uses.
- `SUBMISSION.txt` — the list of files this repository holds.

## Repository

Submitted as the public repository `udacity-applied-machine-learning`, with two branches: `main` (the default branch the review reads) and
the development branch `module-04-calibrated-harmonic`. Its commit history is this module's own, carried over from the plan's repository
[udacity-capstone-plan](https://github.com/thebreadishard/udacity-capstone-plan), where the module lives as
`plans/05_delta-probed-ir-pipeline/modules/04_calibrated_harmonic/`. The last commit on `main` keeps only the files listed in `SUBMISSION.txt`.
