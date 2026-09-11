# Module 02 — the opponent atlas (Udacity AI Programming Foundations project)

## Project description

A reproducible data workflow that reads NASA's public library of computed infrared spectra of
polycyclic aromatic hydrocarbons (PAHs) into tidy tables, cleans them, and explores what the library
contains: how many molecules of which size and charge, which scale factors were applied, and which of
the molecules on this project's test ladder have an entry. The result is the "opponent atlas": the
reference predictions that the project's own pipeline will later be compared against.

**What I built:** a streaming XML parser (`build_opponent_atlas.py`), two smaller readers for the
other comparison lines, a Jupyter notebook with two cleaning functions, one EDA function and five
labelled figures (`notebook/data_workflow.ipynb`), and a written summary (`module_summary.pdf`).

**Dataset:** NASA Ames PAH IR Spectroscopic Database, computed library version 4.00 —
https://www.astrochemistry.org/pahdb/theoretical/4.00 (download form; the derived tabular file used by
the notebook is `notebook/species_pahdb_theoretical_4.00.csv`, 10,749 rows × 27 columns). The data are
computed science data, not AI-generated.

## How to run the project

```bash
pip install -r requirements.txt
jupyter notebook notebook/data_workflow.ipynb
```

Run all cells top to bottom (the notebook is also rebuilt and executed by
`python notebook/make_notebook.py`). To regenerate the tables from the raw XML, place the PAHdb
download in `data/` and run `python build_opponent_atlas.py data/<file>.xml`.

`requirements.txt` was created with `pip freeze > requirements.txt`.

## Reflection questions

**Where could poor data cleaning introduce bias?** Three places. If the charge suffix in the formula
string were not separated, the same molecule would be counted several times and neutral species
would look rarer than they are. If the 32 species whose basis set is unresolved were silently
assigned to the majority basis, the boundary at which the coarser 4-31G description starts (212
carbons) would be wrong. And if isomers (same formula and charge, different molecules) were dropped
as "duplicates", the library would lose thousands of entries and the coverage of the larger molecules
would be misstated. The notebook checks each of these explicitly and keeps unresolved cases flagged
rather than guessed.

**How would the workflow change for a machine-learning project?** The tables would need a
train/validation/test split by *molecule*, not by band, because bands of one molecule are strongly
correlated; feature columns (size, charge, basis, family) would be encoded; and the scale-factor
column would have to be undone (divided out) before any model sees the frequencies, or the model
would learn the database's post-processing instead of the physics.

**How would you prepare it for a neural network?** Per-molecule inputs would become fixed-size
representations (a binned spectrum or a padded stick list), targets would be standardised, and the
same molecule-level split would be enforced; the 4-31G species would be held out or flagged, since
they are computed at a different level.

**Where could agentic automation help?** The download and version checks (fetching a new library
release, verifying its checksum, re-running the parser and diffing the species and scale-factor
tables against the previous version) are a repeatable pipeline an agent could run on a schedule, with
a human reviewing the diff. The scale-factor discrepancy this project found is exactly the kind of
change such a check would surface.

## Repository

Part of the `udacity-capstone-plan` repository (branch `module-02-opponent-atlas`, merged into
`master`); project notes and provenance in `PROVENANCE.md`, the long-form report in `REPORT.md`.
