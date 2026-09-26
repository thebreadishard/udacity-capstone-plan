# Module 06 — Generative AI Applications: candidate molecules for the atlas (prepared 24 September 2026; training after the 28th)

**Status.** Designed (`DESIGN_2026-09-24.md`), pre-registered (`PRE_REGISTRATION.md`, fixed before any training), dataset frozen from PubChem
(`data/README.md` carries the query, the date, the filters, the counts and the SHA-256), code written with tests (`m06/`, six tests, seconds).
Nothing trained yet: the first training run and the notebook execution happen after the supervisor conversation of 28 September, on a rented
server or a CPU-day, never on the anchor laptop before the anchor is read. The user's three decisions of the design note were taken as recommended
on 24 September (PubChem; freeze now; candidates as a separately labelled source for the atlas) — to be confirmed or changed at any time.

## Project description (as it will read)

**Task type: sequence generation with a Transformer.** A molecule is written as a SMILES string; a small decoder-only Transformer (4 layers,
4 heads, d 256, ≈ 3 M parameters, own PyTorch code) trained on public fused-aromatic chemistry generates new substituted and heteroatom PAH
candidates, optionally conditioned on ring count and heteroatom set. The candidates are ranked by how close they sit to the families the project's
learned correction layer is licensed for and offered to the atlas as *what to compute next*. The success criterion is a valid, diverse, novel and
on-distribution generator whose candidates the pipeline can run — not a beautiful sample.

**Dataset.** PubChem compound records with a fused-aromatic core (naphthalene, quinoline, isoquinoline, indole, benzofuran, benzothiophene,
quinoxaline, benzimidazole, azulene), retrieved through PUG-REST, filtered with RDKit (neutral; C, H, N, O, S, F, Cl; ≤ 30 heavy atoms; no
isotopes; ≥ 2 fused aromatic rings; one canonical SMILES each) and frozen as `data/pubchem_aromatics_<date>.csv` with a checksum. Public domain,
deposited real chemistry — not synthetic, not AI-generated, not the dataset of any earlier module.

## How to run what exists

```bash
python m06/fetch_pubchem_aromatics.py            # the data freeze (network; cached; idempotent)
python -m pytest -q m06/tests                    # six tests, seconds
python m06/train.py data/pubchem_aromatics_<date>.csv out/seed0 --quick   # smoke: 2,000 molecules, 2 epochs (minutes on a CPU)
python m06/train.py data/pubchem_aromatics_<date>.csv out/seed0           # the pre-registered run (after the 28th)
M06_QUICK=1 python notebook/make_notebook.py                              # the notebook, quick mode: a pipeline check in minutes, marked as such
python notebook/make_notebook.py                                          # the notebook, pre-registered run (three seeds + the conditioned model; hours on a CPU)
python make_summary.py                                                    # Generative_AI_Analysis_Report.docx/.pdf from notebook/results.json
```

## Files

- `DESIGN_2026-09-24.md` — the design note (task, dataset choice, model, evaluation, ethics, rubric mapping).
- `PRE_REGISTRATION.md` — split, tokenizer, model, metrics and predictions fixed before training.
- `data/` — `README.md` (query, filters, counts, SHA-256) and the frozen CSV; `cache/` (raw PubChem responses, not committed).
- `m06/fetch_pubchem_aromatics.py` — the data freeze; `data.py` (CSV, Murcko scaffold split by sha, tokenizer, conditioning prefixes);
  `model.py` (the Transformer, sampling); `train.py` (protocol, per-epoch log with validity of 200 samples, early stop, `generate`);
  `evaluate.py` (the pre-registered metrics); `tests/test_m06.py`.
- `notebook/make_notebook.py` → `generative_model.ipynb` (25 September 2026; 27 cells: task and model choice, load and inspect, the model, training with
  curves, sampling and the pre-registered metrics with a failure gallery and nearest neighbours, the conditioning change, ethics, summary; `results.json`).
- `make_summary.py` → `Generative_AI_Analysis_Report.docx/.pdf` in the rubric's section order, every number from `results.json`, banner and no PDF in quick mode.
- `requirements.txt` (the environment of 25 September), `PROVENANCE.md` (data, code, pre-registration, runs — dated notes appended).
- To come with the pre-registered run after the 28th: the executed notebook, the report PDF, a dated `RUBRIC_CHECKLIST`.

*Parked, not dropped (26 Sep 10:0x): the module's original idea — a generative proposer of coupled-cluster *measurement patterns* scored by pattern efficiency — is kept as a standout candidate in `GoalGathering/notes/Standout_2026-09-26_Pattern_Proposal_Generator.md`, with the reading of when its response data exist.*
