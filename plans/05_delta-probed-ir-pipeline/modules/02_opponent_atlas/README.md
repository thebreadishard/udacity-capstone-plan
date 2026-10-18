# Module 02 — the opponent atlas (Udacity AI Programming Foundations project)

## Project description

A reproducible data workflow that reads NASA's public library of computed infrared spectra of
polycyclic aromatic hydrocarbons (PAHs) into tidy tables, cleans them, and explores what the library
contains: how many molecules of which size and charge, which scale factors were applied, and which of
the molecules on this project's test ladder have an entry. The result is the "opponent atlas": the
reference predictions that the project's own pipeline will later be compared against.

*For readers without chemistry:* molecules vibrate, and each vibration absorbs infrared light at one colour; the list of those colours and their
strengths is the molecule's infrared spectrum, and astronomers use such spectra to tell which molecules are in space. NASA keeps a library of
*computed* spectra for thousands of flat carbon-ring molecules (PAHs); this module reads that library into clean tables and asks what it holds,
how the numbers were adjusted, and which of the project's own test molecules it covers. Terms such as basis set, scale factor and cation are
explained where they first appear and in the [glossary](https://github.com/thebreadishard/udacity-capstone-plan/blob/master/plans/05_delta-probed-ir-pipeline/modules/GLOSSARY.md).

**What I built:** a Jupyter notebook with two cleaning functions, one EDA function and five labelled
figures (`notebook/data_workflow.ipynb`), and a written summary (`module_summary.pdf`). The tables the
notebook reads were made by a streaming XML parser and two smaller readers for the other comparison
lines; those scripts stay in the plan's repository (see *Where the data come from* below).

**Dataset:** NASA Ames PAH IR Spectroscopic Database, computed library version 4.00 —
https://www.astrochemistry.org/pahdb/theoretical/4.00 (download form; the derived tabular file used by
the notebook is `notebook/species_pahdb_theoretical_4.00.csv`, 10,749 rows × 27 columns). The data are
computed science data, not AI-generated.

## How to run the project

```bash
pip install -r requirements.txt
jupyter notebook notebook/data_workflow.ipynb
```

Run all cells top to bottom. Everything the notebook reads is in this repository: the species table
beside it, the three small comparison tables under `out/`, and `notebook/bands_derived/` — the aggregates and
samples of the computed library's band table (2,517,399 rows, 51 MB, not shipped) that the band-level cells use.
Before submission the notebook was executed in a fresh clone of this repository, with nothing else present.

`requirements.txt` was created with `pip freeze > requirements.txt`.

### Where the data come from

The tables were made from the PAHdb XML download by scripts that stay in the plan's repository, in the module's
folder [`modules/02_opponent_atlas`](https://github.com/thebreadishard/udacity-capstone-plan/tree/master/plans/05_delta-probed-ir-pipeline/modules/02_opponent_atlas): `build_opponent_atlas.py` (the
streaming parser), `build_line_c_table.py` and `build_cheap_line_table.py` (the two other comparison lines),
`notebook/make_bands_derived.py` (the band aggregates) and `notebook/make_notebook.py` (writes and executes this
notebook). Sources, versions and checksums are in that folder's `PROVENANCE.md`, the long-form report in `REPORT.md`.

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

## Files

- `notebook/data_workflow.ipynb` — Setup · Ingestion · Cleaning · EDA · Visualizations · Summary.
- `notebook/species_pahdb_theoretical_4.00.csv` — the tidy species table of the computed library (10,749 rows × 27 columns).
- `notebook/bands_derived/` — aggregates and samples of the band table that the band-level cells read.
- `notebook/figures/` — the five figures, as the notebook writes them.
- `out/anharmonic_1.00/species.csv`, `out/lineC_mai2025/species.csv`, `out/cheapline_bos2025/species.csv` — the species
  tables of the three other comparison lines (PAHdb's anharmonic library, the Mai 2025 peak lists, the Bos 2025 table).
- `module_summary.pdf` — the written summary in the Udacity APA 7 template.
- `SUBMISSION.txt` — the list of files this repository holds.

## Repository

Submitted as the repository `ai-programming-foundations-project` (the name Task 2 of the rubric gives), with two branches: `main` and the development branch `module-02-opponent-atlas`. Its commit history is this module's own, carried over from the plan's repository [udacity-capstone-plan](https://github.com/thebreadishard/udacity-capstone-plan), where the module lives as `plans/05_delta-probed-ir-pipeline/modules/02_opponent_atlas/`. The last commit on `main` keeps only the files listed in `SUBMISSION.txt`: the notebook, the data it reads, the figures and the summary.
