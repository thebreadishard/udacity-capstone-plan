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
