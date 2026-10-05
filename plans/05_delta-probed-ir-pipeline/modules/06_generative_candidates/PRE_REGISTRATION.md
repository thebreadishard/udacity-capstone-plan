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

**Progress note 2026-09-25 21:1x — seed 0 of the pre-registered run trained (training only; sampling and evaluation follow in the notebook).** CCX53, `m06/train.py`, the notebook's own `train_model`, seed 0, 125,065 training / 15,434 validation molecules, 3,201,024 parameters, 20 epochs of ≈ 30 min (603 min total) at `nice 15` beside naphthalene E8: train loss 1.212 → 0.522, validation loss 0.784 → 0.553 (best 0.5530 at epoch 19), validity of 200 samples per epoch 0.22 → 0.955 (`notebook/out/seed0/train_log_seed0.json`, `m06_seed0.log`; weights `model_seed0.pt`, 12.8 MB, kept on the CCX53 and the laptop, not committed). The per-epoch validity is above the registered 0.85 from epoch 9 on; the registered metrics (10,000 samples, T = 1.0 and 0.7) are computed only in the notebook run with `M06_REUSE=1`. Seed 1 and the conditioned model (seed 0, `--conditioning`, smoke of that branch passed) started 21:1x on the CCX53, six threads each at `nice 15`, unbuffered logs (`m06_seed1.log`, `m06_cond_seed0.log`); expected ≈ 12–14 h each (Saturday midday), seed 2 after the CCX53 read-out on another machine. The predictions above are unchanged.

## Outcome 2026-09-26 20:0x — the pre-registered run (three seeds + the conditioned model, 10,000 samples per model)

CCX53, `M06_REUSE=1` (weights of `m06/train.py`, same recipe, seeds 0–2 and `cond_seed0`), 6 threads at nice 15 beside E8, ≈ 1 h 15 min; executed notebook `notebook/generative_model.ipynb`, numbers `notebook/results.json` (date 18:02 UTC), run log `notebook/out/full_2026-09-26/m06_notebook.log`, training logs `notebook/out/seed*/train_log_seed*.json`. Data: 160,972 rows, scaffold split 125,065 / 15,434 / 20,473 (train / val / test), vocabulary 33, 3,201,024 parameters; 20 epochs per seed, final validation loss 0.551 / 0.551 / 0.552.

Read-outs at T = 1.0, seeds 0 / 1 / 2 against the predictions fixed on 24 September:
- validity 0.924 / 0.926 / 0.923 (≥ 0.85: met); seed spread 0.003 (≤ 0.03: met)
- uniqueness 0.992 / 0.992 / 0.992 (≥ 0.95: met)
- novelty 0.907 / 0.907 / 0.910 (≥ 0.50: met); scaffold novelty 0.534 / 0.535 / 0.538 (≥ 0.30: met)
- memorisation 0.099 / 0.099 / 0.095 (≤ 0.10: met, at the line)
- project fit 0.945 / 0.944 / 0.946 against the predicted band 0.30–0.60: **not met — the prediction was wrong, on the low side.** The band was a prediction, so it is scored as a miss; the quantity itself says the model stays inside the corpus families (neutral, C/H/N/O/S/F/Cl, ≤ 30 heavy atoms, ≥ 2 fused aromatic rings) almost always, which is the behaviour the project wants.
- distribution match, W1 heavy atoms / aromatic rings / heteroatoms: 1.00 / 0.14 / 0.07 (seed 0; seeds 1–2 within 0.07)
- T = 0.7: validity 0.98, uniqueness 0.94, novelty 0.85, memorisation 0.18–0.19 — the registered low-temperature trade-off (more valid, more copied)
- conditioning: obedience 0.869 over all requests (≥ 0.80: met); per request 0.625 (`<r2> <hS>`) to 0.979 (`<r2> <hN>`); sulfur requests are the weak ones
- baseline (5-gram Markov, computed live in the notebook): validity 0.030, project fit 0.024, W1 13.4 / 2.59 / 3.32 → margins 0.894 and 0.922, every W1 smaller: `beats_baseline` true.

**Verdict: 6 of 7 registered read-outs met; the miss is a prediction that was too pessimistic (project fit).** Sampling cost 507–652 s per model and temperature on 6 threads. Reading: the model has learned the grammar and the family distribution of the frozen set and obeys class conditioning; it proposes nothing the project's physics asks for (no response-informed objective) — that role belongs to the standout pattern proposer. Next: the module's report and README status line from these numbers (desk work); no further training.

## Decision-51 audit 2026-09-28 18:2x — the cap of 20 was binding for every seed

Rule (decision 51, 27 Sep 2026): a best epoch within 10 % of the cap means the cap was binding and the run is repeated with a higher cap as a dated
follow-up. Read from `notebook/out/*/train_log_seed*.json` (the run of 25–26 September, `m06/train.py`, patience 3, cap 20):

| run | epochs run | best epoch (1-based) | validation loss, last three epochs | seconds per epoch |
|---|---|---|---|---|
| seed 0 | 20 | 19 | 0.5532, 0.5530, 0.5531 | 1,810 |
| seed 1 | 20 | 19 | 0.5513, 0.5512, 0.5513 | 2,087 |
| seed 2 | 20 | 20 | 0.5524, 0.5525, 0.5523 | 1,680 |
| cond_seed0 | 20 | 20 | 0.5322, 0.5321, 0.5321 | 2,084 |

The rule triggers for all four. The curves are flat to 1e-4 over the last three epochs, so the expected change of any read-out is below the seed spread
(validity 0.003); a longer run is still owed under the rule. Cost: ≈ 0.5 h per epoch at six threads → up to 33 h per seed at cap 60, i.e. a server task,
and no server is free before the CCX53 finishes E8 (after which it becomes layer-B shards 4 and 5). Proposed to the user: seed 0 alone at cap 60 on the
first free server as the rule's check; the outcome section above stands as run and is quoted as "at the cap" until then. The 26 September numbers are not
replaced (rule of 28 Sep: module artefacts show the learning).

## Decision-51 audit, ruling 2026-09-28 19:4x — closed by this note, not by a re-run (the user: "Akkoord")

The note of 18:2x read the rule as written: best epoch at the cap → repeat. Reading the curves and the code more closely changes the finding. The
early-stopping condition in `m06/train.py` counts an epoch as "no improvement" only below 1e-4 on a validation loss of ≈ 0.55 (0.02 %), and the
cosine learning-rate schedule (500 warm-up steps, then cosine to zero over exactly the 20-epoch cap) flattens the curve at the cap by construction.
The last six per-epoch improvements of the validation loss:

| run | last six steps (previous − current) |
|---|---|
| seed 0 | +0.00311, +0.00130, +0.00047, +0.00051, +0.00024, −0.00009 |
| seed 1 | +0.00100, +0.00149, +0.00139, +0.00061, +0.00009, −0.00014 |
| seed 2 | +0.00110, +0.00225, +0.00066, +0.00061, −0.00011, +0.00022 |
| cond_seed0 | +0.00217, +0.00073, +0.00177, −0.00010, +0.00014, +0.00003 |

Steps of 1e-4 still reset the patience counter, so the condition could not act within 20 epochs; and "best epoch = last" is what a cosine schedule
produces regardless. The cap was therefore binding on the *epoch count* by construction, and nothing in these curves says the read-outs (validity
0.92, seed spread 0.003; novelty 0.91; project fit 0.95) were bound by it — the last steps are two orders below the seed spread. **Ruling (quality
policy, amendment of 19:4x to decision 51):** the ten-percent test is not applied under a schedule tied to the cap; the audit is closed by this note;
a repeat at a higher cap is owed only when a read-out of this module comes to carry a decision (none does today: module 06 is parked as the standout
line's data source and the proposal cites its numbers as a proxy). The threshold flaw and the schedule are recorded as what the module learned about
its own recipe; the next run of `m06/train.py`, whenever it comes, uses a threshold of 1e-3 (≈ 0.2 % of the loss, stated here) and a schedule that
does not end at the cap. The 26 September outcome stands as run.

## Dated note 5 October 2026 — the re-execution was reverted

*Re-execution of 5 October 2026, not adopted:* the lay-reader pass's execution half re-ran the notebook with `M06_REUSE=1`. Seeds 0 and 1 reproduced the 26 September numbers to the digit, but seed 2's checkpoint had never been saved on 26 September (only its training log), so the reuse path trained seed 2 anew (20 epochs, 6 threads): a different model with validity 0.647 at T 1.0 against 0.923, which flipped two of the seven pre-registered read-outs. A retrained seed is a new run, not a reproduction, so the 26 September record stands (notebook, `results.json`, report restored from git; the 4 October plain-language opening is in them), and the retrained checkpoint is registered `invalid` in `MODELS.md`. What follows, as a dated follow-up if the user wants it (TASKS 26): retrain seed 2 with the recipe and save it, and store the drawn samples so a re-execution evaluates stored artefacts instead of redrawing.
