# Module 06 — Generative AI Applications: candidate molecules for the atlas (prepared 24 September 2026; training after the 28th)

**Status.** Designed (`DESIGN_2026-09-24.md`), pre-registered (`PRE_REGISTRATION.md`, fixed before any training), dataset frozen from PubChem
(`data/README.md` carries the query, the date, the filters, the counts and the SHA-256), code written with tests (`m06/`, six tests, seconds).
**Run on 26 September 2026** (earlier than planned, on the rented CCX53 while the anchor laptop stayed untouched): three seeds and the conditioned model trained with
`m06/train.py`, the pre-registered notebook executed with 10,000 samples per model — 6 of 7 registered read-outs met, the miss being a project-fit prediction
(0.30–0.60) that the model exceeded (0.945); the 5-gram baseline beaten on every line. Numbers in `notebook/results.json`, the outcome section in
`PRE_REGISTRATION.md`, the report `Generative_AI_Analysis_Report.docx/.pdf` built from the results file by `make_summary.py` (20:0x). On 5 October 2026 the generator became a registered source for the corpus (the batch route of TASKS 22: 2,272 new fused aromatic ring systems from 130,000 proposals, 308 of them PubChem molecules; [PreRegistration_2026-10-04_Candidate_Generator_Batch_Route.md](https://github.com/thebreadishard/udacity-capstone-plan/blob/master/plans/05_delta-probed-ir-pipeline/GoalGathering/notes/PreRegistration_2026-10-04_Candidate_Generator_Batch_Route.md)); its rows enter the manifest as layer G and reach version 1.0 at the first computed pool. The user's three decisions of the design note were taken as recommended and confirmed on 5 October 2026 (PubChem as the source; the dataset frozen at the 24 September snapshot; generated candidates only as a separately labelled source)
on 24 September (PubChem; freeze now; candidates as a separately labelled source for the atlas) — to be confirmed or changed at any time.

## Project description (as it will read)

*For readers without chemistry:* This module is a language model for molecules. A molecule can be written as a line of text, a SMILES string (`c1ccccc1` is benzene), and the 'fused aromatic' molecules — flat carbon-ring systems whose rings share edges, the family the project's spectroscopy pipeline serves — are its sentences. Input: 161,000 such strings of real, deposited molecules from the public PubChem database. The model learns their grammar character by character, the way a language model learns from sentences, and then writes new strings. Output: proposals that look like the real ones but are not among them; chemistry software checks each one (a valid molecule? new? similar in size and composition to the real ones?). The purpose is a list of candidates for the pipeline to compute next, never a claim about any molecule. The proposals have not entered the pipeline or the Spectrum Atlas yet: the route that would take them there — an exported, gated list as a new layer of the corpus — is tracked in the plan repository's task list. Terms are defined in the [glossary](https://github.com/thebreadishard/udacity-capstone-plan/blob/master/plans/05_delta-probed-ir-pipeline/modules/GLOSSARY.md).

*Re-execution of 5 October 2026, not adopted:* the lay-reader pass's execution half re-ran the notebook with `M06_REUSE=1`. Seeds 0 and 1 reproduced the 26 September numbers to the digit, but seed 2's checkpoint had never been saved on 26 September (only its training log), so the reuse path trained seed 2 anew (20 epochs, 6 threads): a different model with validity 0.647 at T 1.0 against 0.923, which flipped two of the seven pre-registered read-outs. A retrained seed is a new run, not a reproduction, so the 26 September record stands (notebook, `results.json`, report restored from git; the 4 October plain-language opening is in them), and the retrained checkpoint is registered `invalid` in `MODELS.md`. What follows, as a dated follow-up if the user wants it (TASKS 26): retrain seed 2 with the recipe and save it, and store the drawn samples so a re-execution evaluates stored artefacts instead of redrawing.

**Task type: sequence generation with a Transformer.** A molecule is written as a SMILES string; a small decoder-only Transformer (the project's **candidate generator**, versions 0.1 and 0.2 in `MODELS.md` — an experiment outside the pipeline; 4 layers,
4 heads, d 256, ≈ 3 M parameters, own PyTorch code) trained on public fused-aromatic chemistry generates new substituted and heteroatom PAH
candidates, optionally conditioned on ring count and heteroatom set. The candidates are ranked by how close they sit to the families the project's
learned correction layer is licensed for and offered to the atlas as *what to compute next*. The success criterion is a valid, diverse, novel and
on-distribution generator whose candidates the pipeline can run — not a beautiful sample.

**Dataset.** PubChem compound records with a fused-aromatic core (naphthalene, quinoline, isoquinoline, indole, benzofuran, benzothiophene,
quinoxaline, benzimidazole, azulene), retrieved through PUG-REST, filtered with RDKit (neutral; C, H, N, O, S, F, Cl; ≤ 30 heavy atoms; no
isotopes; ≥ 2 fused aromatic rings; one canonical SMILES each) and frozen as `data/pubchem_aromatics_2026-09-24.csv` with a checksum (committed as two gzip parts). Public domain,
deposited real chemistry — not synthetic, not AI-generated, not the dataset of any earlier module.

## How to run

```bash
pip install -r requirements.txt
python -m pytest -q m06/tests                       # the model code's tests, seconds
jupyter notebook notebook/generative_model.ipynb
```

Run all cells top to bottom. The full run trains three seeds and the conditioned model (hours on a CPU); the stored notebook is that run
(26 September 2026). `M06_QUICK=1 jupyter notebook notebook/generative_model.ipynb` runs the same cells as a pipeline check (2,000 training
molecules, one seed; the notebook labels its numbers as not a result). The notebook reads the dataset from the two committed gzip parts in
`data/` (the frozen CSV is 12.8 MB; header and rows of the parts are the CSV row for row). Before submission the pipeline check was executed
in a fresh clone of this repository, with nothing else present. `requirements.txt` was created with `pip freeze > requirements.txt`.

### Where the data come from

`data/README.md` records the PubChem query (PUG-REST, 24 September 2026), the filters, the counts at every step and the SHA-256 of the
frozen CSV. The script that ran the query (`m06/fetch_pubchem_aromatics.py`), the notebook's builder (`notebook/make_notebook.py`), the
report's builder (`make_summary.py`), the design note and the provenance notes stay in the plan's repository, in the module's folder
[`modules/06_generative_candidates`](https://github.com/thebreadishard/udacity-capstone-plan/tree/master/plans/05_delta-probed-ir-pipeline/modules/06_generative_candidates).

## Files

- `PRE_REGISTRATION.md` — split, tokenizer, model, metrics and predictions, fixed before training; its outcome section.
- `notebook/generative_model.ipynb` — task and model choice, load and inspect, the model, training with curves, sampling and the
  pre-registered metrics with a failure gallery and nearest neighbours, the conditioning change, ethics, summary.
- `notebook/results.json` (the numbers), `notebook/figures/`, `notebook/out/` (the training logs of the three seeds and the conditioned model).
- `m06/` — `data.py` (dataset, Murcko scaffold split, tokenizer, conditioning prefixes), `model.py` (the Transformer, sampling), `train.py`
  (protocol, per-epoch log, early stopping, `generate`), `evaluate.py` (the pre-registered metrics), `baseline_ngram.py` (the 5-gram
  baseline), `tests/test_m06.py`.
- `data/` — `README.md` and the dataset as two gzip parts.
- `Generative_AI_Analysis_Report.pdf` — the report in the Udacity APA 7 template; `MODELS.md` — the generator's versions.
- `SUBMISSION.txt` — the list of files this repository holds.

## Repository

Submitted as the public repository `udacity-generative-ai-applications` (its default branch `main` is the one the review reads). Its
commit history is this module's own, carried over from the plan's repository
[udacity-capstone-plan](https://github.com/thebreadishard/udacity-capstone-plan), where the module lives as
`plans/05_delta-probed-ir-pipeline/modules/06_generative_candidates/`. The last commit on `main` keeps only the files listed in
`SUBMISSION.txt`.

*Parked, not dropped (26 Sep 10:0x): the module's original idea — a generative proposer of coupled-cluster *measurement patterns* scored by pattern efficiency — is kept as a standout candidate in [Standout_2026-09-26_Pattern_Proposal_Generator.md](https://github.com/thebreadishard/udacity-capstone-plan/blob/master/plans/05_delta-probed-ir-pipeline/GoalGathering/notes/Standout_2026-09-26_Pattern_Proposal_Generator.md), with the reading of when its response data exist.*
