# Module 06 — Generative AI Applications: candidate molecules for the atlas (design stage, 24 September 2026)

**Status:** designed, nothing run. `DESIGN_2026-09-24.md` holds the task, the dataset choice (PubChem aromatic subset — public domain, not used
by modules 02–05), the model (character-level Transformer on SMILES, own PyTorch code), the pre-registered evaluation, the ethics section and the
rubric mapping. Three decisions are the user's (dataset, timing, whether the candidates feed the website's "listed" layer); the build starts after
the supervisor conversation of 28 September. The data freeze (one script, no compute) can be done on any quiet hour before that.

## Project description (as it will read)

**Task type: sequence generation with a Transformer.** A molecule is written as a SMILES string; a small decoder-only Transformer trained on public
aromatic chemistry generates new substituted and heteroatom PAH candidates, optionally conditioned on ring count and heteroatom set. The candidates
are ranked by how close they sit to the families the project's learned correction layer is licensed for, and offered to the atlas as *what to
compute next*. The success criterion is a valid, diverse, novel and on-distribution generator whose candidates the pipeline can actually run — not
a beautiful sample.

**Dataset (planned):** PubChem compound records filtered to fused-aromatic frameworks (≥ 2 fused aromatic rings; C, H, N, O, S, F, Cl; ≤ 30 heavy
atoms; neutral), retrieved through PubChem's public interfaces, filtered with RDKit and frozen as a checksummed CSV with the query and date.
Public domain, deposited real chemistry — not synthetic, not AI-generated, not the dataset of any earlier module.

## How to run what exists

Nothing yet. The layout will follow module 05: `m06/` scripts with tests, `notebook/make_notebook.py` → `generative_model.ipynb`,
`make_summary.py` → the report, `PROVENANCE.md`, `PRE_REGISTRATION.md`, a dated `RUBRIC_CHECKLIST`, `requirements.txt` from the environment.

## Files

- `DESIGN_2026-09-24.md` — the design note.
