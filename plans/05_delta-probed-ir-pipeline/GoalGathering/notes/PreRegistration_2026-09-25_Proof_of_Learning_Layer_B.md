# Pre-registration 2026-09-25, 07:0x — the proof that the network learns: the layer-B learning curve (the user: "Ja, doe de laag B run")

**Question (fixed).** Does the local ΔH model keep improving with data, on hold-outs that stand for the mandate's direction (bare cores, unseen
scaffolds, larger molecules), or does it plateau above the label noise? This is the user's success criterion for the design ("het bewijs dát het
netwerk leert is het allerbelangrijkste"). Written before any layer-B molecule is finished.

**Data (fixed).** Corpus layer B as defined on 12 September (`corpus/DESIGN_2026-09-12.md`, `build_manifest.py`): 4,353 mono- and di-substituted
aromatic and heteroaromatic molecules of 8–26 atoms in the hashed manifest order; deck v1 unchanged; computed as five shards on CPX62s
(`run_corpus.py --layer B --shard i/5`, shards 0 and 1 started 25 September on hel1-18 and hel1-21; 2–4 join as machines free up). Molecules with an
imaginary mode in either functional are excluded as in E6/E7, and the second-route screen of the corpus README applies before any table is read.
The learning-curve **training sets are the first 100 / 300 / 600 / 1,200 admitted layer-B molecules in the hashed order**, whichever shard
computed them; a table is read only when every molecule of its prefix is done or excluded (a missing one that is still pending blocks the table).
Layers A and A2 are **not** in the training pool of this test (they are the hold-outs); a second, secondary curve adds the A2 pool to each
training set and is reported beside the first.

**Hold-outs (fixed, disjoint from the training sets):**
- (a) **bare parents:** the layer-A molecules without a substituent (the 14 cores of A2 and the other layer-A aromatics), admitted ones only;
- (b) **unseen scaffolds:** E6's two scaffold cores and all their A2 derivatives (`E6.splits`), as in E7 rung B;
- (c) **larger than any training molecule:** the admitted A2 molecules with more atoms than the largest molecule in the training set at hand
  (layer B tops at 26 atoms; A2 runs to 30–34) — the size-extrapolation hold-out.

**Model (fixed for this test).** E7 rung B's pair model (`m05/e7_rungB_pairs.py`: MLP 2 × 128 on pair features, three seeds, plus the
gradient-boosted check) — the floor. When the equivariant ΔH model of the 23 September decision exists, the identical table is rerun with it;
that rerun is a separate dated section, not a replacement.

**Read-outs (fixed; E6/E7):** corrected-frequency RMS (same-family blocks) and ring coupling ratio to the zero rule on each hold-out at each
training size; ΔH residual ratio; the slope of log(ratio) against log(n) per hold-out; the second-route noise floor of the labels (analytic vs
finite-difference Hessians, per-mode RMS on the molecules that have both) printed beside the curve.

**Reading (fixed before any number):**
- **Pass ("the network learns"):** on all three hold-outs the corrected-frequency RMS and the ring coupling ratio decrease monotonically over
  100 → 300 → 600 → 1,200 (seed means; a single non-monotone step smaller than the seed spread does not break monotonicity), with a slope of at
  least a factor 1.5 per decade of data on (a) and (c), and any plateau no higher than three times the second-route noise floor.
- **Fail:** flat (slope worse than a factor 1.15 per decade) on (a) or on (c) — the model does not learn what the mandate needs from more data
  of this kind; the next step is then the model (equivariant, more capacity) or the data kind (bare cores, larger molecules in the pool), not
  more of the same.
- **Between:** anything else; the per-hold-out slopes say which direction is short of data and which of model.
- Intermediate tables (at 300, at 600) are read and recorded as they come but carry no verdict; the verdict is at 1,200.

**Not registered:** family breakdowns, the secondary curve's reading, and anything read from the equivariant rerun.

**Cost.** ≈ 1,700 CPX62-hours for the first 1,200 (≈ €400); the rest of layer B continues afterwards as corpus work. The tables themselves are
minutes on the laptop or a CPX62.

**Consequence of a pass.** The design's central claim is demonstrated on the proxy at the scale the corpus allows; the proposal of 28 September
cites the 300-table (if it exists by then) as the first point of a curve whose reading rule is on record here.

## Dated amendment 12:1x — one interim reading before the 28th, labelled as such (the registered tables are unchanged)

The registered tables need the first 100 / 300 / … molecules *in hashed order*, which needs all five shards; shards 3 and 4 join only on
Saturday evening and Sunday, so the 100-table is expected Monday morning at the earliest and may slip past the conversation. To have one honest
number on Monday, an **interim reading** is declared now: training set = every admitted layer-B molecule finished on shards 0–2 by **Sunday 27
September 20:00** (shard membership is by id hash, so this is a random sample of layer B, not a curated one; its size is whatever it is, ≈ 150–250),
same three hold-outs, same read-outs, same model and seeds, read against the same power-law predictions at that size (interpolated on the log axis).
It is reported under the heading *interim (not the registered prefix)*, it cannot pass or fail the registered rule, and it does not replace the
100- and 300-tables, which follow as registered. Prediction for the interim point, from the fits of 25 September: bare parents ratio 0.42–0.44,
unseen scaffolds 0.43–0.45, size hold-out 0.55–0.58; a point clearly below those would say the small-data fits were pessimistic.

## Dated amendment 12:2x — the optimiser is part of the curve: a tuned curve beside the fixed-recipe curve (the user: "Nemen we mee dat we de optimale moeten vinden?")

**What is fixed today.** The pair model's recipe is one setting at every training size: two hidden layers of 128, AdamW at learning rate 1e-3 with weight decay
1e-4, cosine schedule over 60 epochs, batch 4,096, no early stopping, no validation split (`m05/e7_rungB_pairs.py: train_mlp`). The number of optimiser steps
grows with the data (about 1,500 at 45 molecules, 6,000 at 175), so the recipe does scale in that one respect; nothing else was ever tuned. A learning
curve measured with a single frozen recipe confounds two things: what the model *can* learn from n molecules, and what this one optimiser setting *happens*
to extract. A flat slope can be either.

**Protocol (pre-registered before it runs; the fixed-recipe curve above stays the primary until the rule below says otherwise).** At every training size n
and seed: (1) an inner validation split of 20 % of the *training* molecules, split by molecule with the same hash order (never a hold-out molecule);
(2) a fixed grid of six settings — learning rate {3e-4, 1e-3, 3e-3} × width {128, 256} — each trained with early stopping on the inner split's per-pair
MSE (patience 10 epochs, at most 200 epochs, cosine schedule over the epochs actually run) instead of the fixed 60; (3) the setting with the lowest
inner-validation MSE is retrained on all n training molecules with the epoch count early stopping chose; (4) the hold-outs are read exactly as for the fixed
recipe. The grid, the patience and the selection statistic are fixed here and are not enlarged after a reading. Cost: about seven trainings per point
instead of one — minutes.

**Predictions.** At 175 molecules the tuned curve lies within 0.03 of the fixed one on both hold-outs (the fixed recipe is not badly off: its steps scale with
the data and its loss is well conditioned); the slope of the tuned curve on the bare parents is steeper by at most 0.10 in the factor per decade
(1.14× → ≤ 1.24×). **Rule.** If the tuned slope reaches the registered 1.5× where the fixed one does not, the optimiser was the bottleneck and the tuned
protocol becomes the primary recipe for every later point (declared now, not after the fact); if both slopes stay below 1.5×, the model and the data are the
limit and the equivariant model (rung C) is the next lever; if the two curves agree within their seed spread, hyperparameters are not what decides this
question at these sizes, and the fixed recipe stays for its simplicity with the tuned curve reported beside it.

**First run.** Today on the 175-molecule pool (`--tune`, sizes 45 / 100 / 175, seeds 0–2) on the CCX53 at low priority — the same pool as the fixed curve of
23 September, so the two curves are compared point by point; the layer-B tables get both curves from the 100-table on.
