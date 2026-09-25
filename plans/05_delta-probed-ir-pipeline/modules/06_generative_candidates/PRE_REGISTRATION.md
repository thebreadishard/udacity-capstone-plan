# Module 06 — pre-registration (written 24 September 2026, before any training)

**Task.** Generate candidate fused-aromatic molecules as SMILES with a character-level decoder-only Transformer trained on the frozen PubChem
dataset (`data/README.md` records the query, the date, the filters, the counts and the SHA-256). Outputs are spectroscopic *targets* for the atlas,
labelled as a separate source; no synthesis or property claims.

**Data handling, fixed now.** Split by Murcko scaffold, hashed (sha1 of the scaffold SMILES): 80 % train, 10 % validation, 10 % test; a scaffold
never straddles splits. Tokens: characters, with two-character elements (`Cl`, `Br`) and bracket atoms kept as single tokens; a start and an end token;
sequences longer than 96 tokens dropped (count reported). Optional conditioning prefix tokens: ring-count class (2, 3, ≥ 4) and heteroatom set (none,
N, O, S, mixed); the unconditioned model is the primary one, the conditioned one a secondary read-out.

**Model, fixed now.** 4 layers, 4 heads, d_model 256, feed-forward 1024, dropout 0.1, learned positional embeddings, ≈ 3 M parameters; AdamW
(lr 3e-4, weight decay 0.01), cosine schedule with 500 warm-up steps, batch 128, 20 epochs or early stop on validation loss (patience 3); seed 0
primary, seeds 1 and 2 for the spread of the metrics. Sampling at temperature 1.0 (primary) and 0.7 (secondary), 10,000 samples per setting.

**Metrics, fixed now** (definitions as in MOSES / GuacaMol, cited in the report).
- validity = fraction of samples RDKit parses; uniqueness = unique canonical SMILES among valid; novelty = valid unique samples whose canonical
  SMILES is not in the training set; scaffold novelty = whose Murcko scaffold is not in the training set.
- distribution match: Wasserstein-1 distances of heavy-atom count, aromatic-ring count and heteroatom count between samples and the test split.
- project fit: fraction of valid, novel samples that are neutral, C/H/N/O/S/F/Cl only, ≤ 30 heavy atoms and fused-aromatic (the corpus families).
- conditioning obedience (secondary model): fraction of samples whose ring-count class and heteroatom set equal the prefix.
- memorisation: fraction of samples identical to a training SMILES (reported beside novelty).

**Predictions (fixed now).** validity ≥ 0.85, uniqueness ≥ 0.95, novelty ≥ 0.50 at temperature 1.0 (seed 0); scaffold novelty ≥ 0.30;
project fit 0.30–0.60; conditioning obedience ≥ 0.80; memorisation ≤ 0.10; the three seeds within ±0.03 on validity. At temperature 0.7 validity
rises and novelty falls (both stated qualitatively; the numbers are read, not predicted).

**What counts as a failure and how it is reported.** Validity < 0.70 or novelty < 0.30 is a failed run; it is reported as such with the failure
gallery (invalid strings, duplicates of training molecules, non-fused or charged outputs) and one remedy tried and documented — never a silent
re-run with new settings. Nothing in the metrics is tuned on the test split.

**Compute.** One CPU-day at most or an hour on a rented server after 28 September; the module never runs on the anchor laptop before the anchor
is read. The dataset freeze (this note's companion) is downloads and filters only.

**Provenance.** Every number in the notebook and the report comes from `notebook/results.json` written by the executed notebook; the report
cites cells, not memory. Seeds, versions and the dataset SHA-256 are printed in the notebook's first cell.

## Dated amendment 2026-09-25 11:0x — a baseline the model must beat; measured compute; the primary seed trained ahead of the notebook run

**Baseline (secondary control, added before any full training; the primary metrics and predictions above are unchanged).** A token-level 5-gram
Markov model with stupid back-off (`m06/baseline_ngram.py`), fitted on the train split only, sampled 10,000 times at temperature 1.0 and evaluated
with the same `evaluate_samples`. It knows local token statistics and nothing else, so it is the control that separates "learned the grammar and the
chemistry" from "copied the token frequencies". Predictions (25 September, before the baseline ran): validity 0.30–0.60 (bracket and ring-closure
bookkeeping fail beyond five tokens), uniqueness ≥ 0.95, novelty ≥ 0.95, memorisation ≤ 0.02, project fit ≤ 0.15, W1 distances larger than the
Transformer's. **Reading rule:** the Transformer's seed-0 model at temperature 1.0 must beat the baseline by ≥ 0.25 in validity and ≥ 0.15 in project
fit, with smaller W1 distances on all three descriptors; if it does not, the model has not learned more than token statistics and the module's
verdict is FAIL whatever the absolute numbers. The baseline row is reported in the notebook's evaluation table and in the report.

**Compute, measured.** The quick run of 25 September 08:5x gives 86–94 s per epoch on 2,000 molecules at four threads (`notebook/results.json`,
`training`), i.e. ≈ 1.6 h per epoch on the 125,065 training molecules — about 30 h per seed at four threads, not the "hour on a rented server" written
above; the pre-registration's budget line was wrong by an order of magnitude, the recipe is not changed. Consequence: the run is split. Seed 0 (the
primary) is trained now on the rented CCX53 at low priority (`nice -n 15`, eight threads, beside naphthalene E8, which is not CPU-bound), with the
notebook's own `train_model` through `m06/train.py` and the same seed, recipe and dataset; its weights and training log go to `notebook/out/seed0/`.
The notebook, when it runs in full, loads them if `M06_REUSE=1` (a cache of the identical computation, printed in the cell) and trains what is
missing (seeds 1, 2 and the conditioned model), so the executed notebook stays the record. Nothing runs on the laptop.

**Baseline outcome 11:0x** (`out/baseline_ngram_2026-09-25.json`, run on the CCX53, 47 s): validity **0.030**, uniqueness 0.855, novelty 0.996,
scaffold novelty 0.992, memorisation 0.003, project fit 0.024, W1 13.4 / 2.59 / 3.32. The validity prediction (0.30–0.60) was wrong by an order of
magnitude: five tokens of context cannot close rings or brackets over the spans these molecules need (the invalid samples are almost all unbalanced ring
closures), and the valid samples are short. Recorded as written; the reading rule stands and the notebook computes the baseline live in its evaluation
cell (same split, same seed, same evaluation) so the executed notebook remains the record.
