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

## Dated amendment 12:4x — stage 2 of the tuned protocol: loss function and optimiser (the user: "loss function, optimizer zijn belangrijke componenten")

**Rule adopted (QUALITY_POLICY):** a negative conclusion about the model — a flat curve, "cannot learn X", "the model is the limit" — is licensed only
after the pre-registered search over optimiser, loss function and the main hyperparameters has run at that data size. Everything read so far
(E6, E7 rung B, the E11.5 fits) was one frozen recipe and is now labelled as such where it is quoted.

**Stage 2 (fixed before it runs).** At the learning rate and width stage 1 selects, four settings: loss {MSE, Huber with δ = 1 in the class-scaled
units} × optimiser {AdamW (as before), SGD with Nesterov momentum 0.9 at ten times the learning rate}; the (MSE, AdamW) cell is stage 1's result and is not
retrained. Same inner split, same early stopping, same selection statistic; the winner is retrained on all training molecules. Three extra trainings
per point. Not in the grid, with the reason: batch size (4,096 on 10⁵–10⁶ pairs is not in the way; halving it doubles the steps, which the epoch count
already supplies), depth (rung C's question), learning-rate warm-up (cosine from a small model's default is stable here; if stage 2's Huber/SGD cells
win, warm-up is added to a stage 3 and registered first). **Prediction:** the loss function matters more than the optimiser for this target — Huber
within 0.02 of MSE on the hold-outs, SGD not better than AdamW at any size; stage 2 moves the 175-point by less than 0.02 in ratio. **Reading:** the
same rule as stage 1 — the tuned protocol (stages 1 + 2) becomes primary if its slope reaches 1.5× where the frozen recipe's does not; a stage-2 winner
that is not (MSE, AdamW) is reported with its inner-validation margin, and the choice is fixed for all later points.

**Stage 3, registered 12:4x (the user: in one of the referenced papers a quantity whose derivative could not be taken was handled by choosing a different loss
function).** The same move applies here. The model is trained on the per-pair internal-coordinate ΔF (MSE), but it is *read* on projected quantities — the
family block K = Lᵀ ΔH_mw L and the corrected frequencies. The projection is linear in ΔF, so a loss in the read-out's own metric is differentiable:
L = MSE(ΔF pairs) + λ · MSE(K block of the same molecule, frequency-weighted as the read-out weights it), λ ∈ {0.1, 1}, computed per molecule inside the
batch. Stage 3 runs only if stage 2 has run, at stage 2's setting, with the same inner split and rule; prediction: it lowers the corrected-frequency RMS on
the hold-outs by 0.2–0.5 cm⁻¹ at 175 and leaves the ring coupling ratio within 0.02, because it re-weights the same information towards what is measured.
The literature reference is added to the notes when the user names the paper; the principle — choose the loss for the quantity you read out, not for the
quantity that is convenient to store — is recorded here as the design rule for rung C's loss as well.

**Stage 1 outcome 15:1x** (`modules/05_support_predictor/out/E7_rungB_tuned_2026-09-25.md/.json`, 2.2 h on the CCX53 at 4 threads). Chosen at every size and seed: learning rate 3e-3 (three times the fixed recipe's), width 128 in seven of nine cases, early stopping after 24–124 epochs (fixed: 60); the fixed setting's inner-validation MSE was 8–30 % higher than the chosen one's everywhere. Hold-outs, three-seed means, tuned vs fixed — ratio (a): 0.43 / 0.45 / **0.41** vs 0.47 / 0.45 / 0.43; ratio (b): 0.47 / 0.54 / **0.44** vs 0.51 / 0.50 / 0.47; corrected ω (a): 4.7 / 4.8 / **4.1** vs 5.9 / 5.1 / 4.7 cm⁻¹; (b): 5.1 / 5.8 / **4.5** vs 6.0 / 5.4 / 5.1. Seed spread at 175: 0.005 (a), 0.014 (b). Against the predictions: at 175 the tuned curve is 0.02–0.03 below the fixed one on the ratio (within the predicted 0.03) and 0.6 cm⁻¹ better on the corrected frequencies; the slope is **not** steeper — 1.06× per decade on both hold-outs against the fixed recipe's 1.14× / 1.15×, because tuning helped most at 45 molecules (the fixed recipe under-trains there) and the 100-point on (b) carries one poorly selected seed (0.63). **Reading by the rule:** the two curves do not agree within their seed spread, so hyperparameters do matter — for the *level* (0.02–0.03 in ratio, 0.6 cm⁻¹), not for the *slope*; neither curve reaches 1.5× per decade. No negative conclusion is drawn yet: stage 2 (loss × optimiser) runs next at the chosen setting, then stage 3; only after those is the slope a statement about the model. Practical consequence now: the layer-B tables report both curves from the 100-table on, and the tuned protocol's selection variance (the 100/(b) outlier) is itself a quantity to report beside each point.

**Stage 2 outcome 19:1x** (`modules/05_support_predictor/out/E7_rungB_tuned2_2026-09-25.md/.json`, 2.9 h on the CCX53 at 4 threads). At the stage-1 setting (lr 3e-3), the inner-validation cells per size and seed: MSE + AdamW wins at 45 and at 175 on all three seeds; at 100 Huber + AdamW wins on two seeds (0.2895 vs 0.2984; 0.2950 vs 0.3403); SGD with Nesterov momentum never wins (MSE + SGD 3–40 % worse; Huber + SGD 2–3× worse). Hold-outs: 45 and 175 identical to stage 1 (0.43 / 0.47; **0.41 / 0.44**, ω 4.1 / 4.5 cm⁻¹); the 100-point improves to 0.42 (a) / 0.52 (b) and ω 4.4 / 5.5 from stage 1's 0.45 / 0.54 and 4.8 / 5.8 — the Huber cells smooth the dip that stage 1's selection variance had put there. Slopes: 1.08× (a) / 1.07× (b) per decade (stage 1: 1.06×; fixed: 1.14× / 1.15×). **Against the predictions:** the loss function mattered more than the optimiser (yes), SGD was not better at any size (yes), the 175-point moved by less than 0.02 (it moved by 0.00). Reading: after stages 1 and 2 the optimiser and the loss do not change the answer to the slope question; stage 3 (the read-out-aligned loss) is running and is the last registered stage before a negative reading about the model at 175 becomes licensed.

**Stage 3 outcome 20:4x** (`modules/05_support_predictor/out/E7_rungB_tuned3_2026-09-25.md/.json`, 1.7 h on the CCX53). The read-out-aligned loss (λ = 0.1) was chosen on the inner split for two of three seeds at 175 (margins 0.0004 and 0.0020 in inner MSE — small) and one of three at 45; λ = 1 never. Hold-outs at 175: ratio **0.39 (a) / 0.42 (b)** (stage 2: 0.41 / 0.44; fixed: 0.43 / 0.47), corrected ω **3.75 / 4.20 cm⁻¹** (stage 2: 4.10 / 4.48; fixed: 4.71 / 5.14). Against the prediction: ω improved by 0.35 / 0.28 — inside the predicted 0.2–0.5; the ratio moved by 0.02 — at the edge of 'within 0.02'. Slopes 1.10× (a) / 1.09× (b) per decade (stage 2: 1.08 / 1.07; fixed: 1.14 / 1.15).

**Reading after the full registered search (stages 1–3), by the rule of 12:4x.** The recipe moves the *level* substantially and cumulatively — from the frozen recipe to stage 3 the coupling ratio on unseen molecules falls from 0.43 / 0.47 to 0.39 / 0.42 and the corrected-frequency error from 4.7 / 5.1 to 3.75 / 4.2 cm⁻¹, a fifth better for nothing but training choices — and it does not move the *slope*: 1.06–1.15× per decade under every recipe, against the registered 1.5×. The statement that is now licensed is therefore precise: *on 45–175 molecules the pair model's learning rate with data is about 1.1× per decade whatever the optimiser, loss and hyperparameters.* What is not licensed is 'the model is the limit' — the two remaining explanations are the data regime (a curve that steepens beyond a few hundred molecules; the layer-B tables decide, from the 100-table on, with both the fixed and the tuned protocol reported) and the model class (rung C, pre-registered, the user's decision on Sunday). Practical consequences: the tuned protocol (stages 1–3) becomes the *reported* recipe beside the fixed one in every layer-B table; the fixed recipe stays the primary of the registered pass rule because that rule was written for it; the E11.5 predictions for the layer-B curve are re-fitted on the tuned points as a second, labelled prediction set before the 100-table is read.

**Second, labelled prediction set — the tuned protocol (20:5x; `modules/05_support_predictor/out/E11_power_law_2026-09-25c_tuned.md`, fitted on the stage-3 curve, 45 / 100 / 175, size split unchanged from the fixed recipe).** Bare parents: ratio 1.10× per decade → **0.37 [0.35, 0.39] at 1,200** (fixed recipe's set: 1.14×, 0.39); corrected RMS 1.38× → **2.94 [2.71, 3.18] cm⁻¹** (fixed: 1.49×, 3.4). Unseen scaffolds: 1.09× → 0.42 [0.38, 0.46]; RMS 1.27× → 3.7 cm⁻¹. Size hold-out (fixed recipe only): 1.22× → 0.49. Reading of the layer-B tables: each table is read against *both* sets, each with its own recipe; the registered pass rule (≥ 1.5× per decade on the bare parents and the size hold-out, plateau ≤ 6.3 cm⁻¹) applies to the fixed recipe as written and is reported for the tuned one beside it. Neither set is changed after this line.

**Reading machinery in place (21:3x).** `m05/e7_rungB_pairs.py --split layerB`: pool = admitted layer-B molecules in hashed order (`E6.sha`), hold-out (a) = all admitted layer-A molecules (42), (b) = the E6 scaffold molecules (39), (c) = admitted A2 molecules with more atoms than the largest molecule of the training set at hand (recomputed per size; its zero rule stored per size). Smoke on the 64 layer-B molecules fetched from shards 0–2 at 21:3x (60 admitted; 2 epochs, one seed — `out/E7_rungB_layerB_smoke.md`, marked SMOKE, not a number to read). The commands of the interim reading (Sunday 20:00) and of every registered table, fixed now: fixed recipe `… out/E7_rungB_layerB_<date> --use-analytic --split layerB --sizes <prefixes or all> --seeds 0,1,2`; tuned protocol the same with `--tune --tune-stage2` (stage 3 via `--tune-stage3 <stage-2 json>`); both read against both prediction sets. Data path: shards' finished molecule directories (without psi4 scratch) are fetched into `corpus/shards_layerB/s<i>/` and copied beside layers A/A2 under `corpus/molecules/`; the manifest merge (`merge_shards.py`) happens when a shard ends.
