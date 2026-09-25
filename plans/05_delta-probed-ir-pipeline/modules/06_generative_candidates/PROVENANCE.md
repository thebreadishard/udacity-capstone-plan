# Module 06 — provenance

Every number in the notebook and the report traces to a file named here. Dated notes are appended; nothing above them is rewritten.

## Data

- `data/pubchem_aromatics_2026-09-24.csv` — 160,972 molecules; built by `m06/fetch_pubchem_aromatics.py` on 24 September 2026 (PubChem PUG-REST
  fast-substructure searches for nine fused-aromatic cores, 50,000 CIDs each, property batches; RDKit filters: neutral, C/H/N/O/S/F/Cl, ≤ 30 heavy
  atoms, no isotopes, ≥ 2 fused aromatic rings). Query, counts per filter step, retrieval date and SHA-256 (`c7fe9e9e2932da0d…`) in `data/README.md`;
  committed as two gzip parts (the pre-commit hook refuses files above 1.5 MB), reassembly line in the same README. Public-domain records (PubChem);
  Zenodo deposit prepared (`GoalGathering/notes/Zenodo_Deposits_2026-09-24.md`, deposit 3, CC0 for the compilation).
- Splits: Murcko scaffold → sha1 → 80/10/10 (`m06/data.py: split_of`), deterministic and machine-independent; counts printed in notebook section 1.

## Code

- `m06/data.py` (loader, scaffold split, character tokenizer, vocabulary, conditioning prefix), `m06/model.py` (decoder-only Transformer, own code,
  ≈ 3 M parameters), `m06/train.py` (AdamW, warm-up + cosine, early stopping on validation loss, per-epoch validity of 200 samples; `--quick` for a
  pipeline check), `m06/evaluate.py` (the pre-registered metrics), `m06/tests/test_m06.py` (six tests, seconds).
- `notebook/make_notebook.py` → `notebook/generative_model.ipynb` (25 September 2026): writes the cells and executes them top to bottom;
  `M06_QUICK=1` runs the pipeline check (2,000 training molecules, 2 epochs, one seed, 1,000 samples) and marks the results as such.
- `make_summary.py` → the report (docx + PDF, APA 7 template) from `notebook/results.json`.

## Pre-registration

`PRE_REGISTRATION.md`, 24 September 2026, before any training: data handling, model, training recipe, metrics and their predictions
(validity ≥ 0.85, uniqueness ≥ 0.95, novelty ≥ 0.50, scaffold novelty ≥ 0.30, project fit 0.30–0.60, conditioning obedience ≥ 0.80,
memorisation ≤ 0.10, three seeds within ±0.03 on validity). Design and rubric mapping: `DESIGN_2026-09-24.md`.

## Runs

- **2026-09-25 (quick mode, pipeline check — not a result):** `generative_model.ipynb` executed with `M06_QUICK=1` on the rented CCX53
  (`/root/m05run/06_generative_candidates/notebook/`, env `m05`, four threads) to prove the notebook runs top to bottom; its `results.json` is
  marked `quick: true` and is not the module's result. *(Dated note below records the outcome.)*
- **Pre-registered run (three seeds, 20 epochs, 10,000 samples; the conditioned model):** not yet run — after 28 September, on a rented server or
  the desktop (one CPU-day at most), never on the laptop while an anchor-class run is on it.

**Dated note 2026-09-25 08:5x — quick-mode execution done (pipeline check).** `generative_model.ipynb` ran top to bottom on the CCX53 (env `m05`, four threads, `M06_QUICK=1`: 2,000 training molecules, 2 epochs, one seed, 1,000 samples, plus the conditioned model) after three fixes the check itself forced: RDKit drawing needs libXrender on a headless server; the neighbour grid must tolerate an empty sample set; and `hetero_class` misread the letter pair "Cc" as an element and `[nH]` as hydrogen (rewritten per token, regression tests added). Quick numbers — 2 % validity after two epochs, 94 % uniqueness, 100 % novelty, obedience 8 % — are what two epochs on 2,000 molecules give and are **not the module's result**; `results.json` is marked `quick: true`, and `make_summary.py` produced the docx with its banner and no PDF, as designed. The pre-registered run (three seeds, 20 epochs, 10,000 samples) stays after 28 September.
