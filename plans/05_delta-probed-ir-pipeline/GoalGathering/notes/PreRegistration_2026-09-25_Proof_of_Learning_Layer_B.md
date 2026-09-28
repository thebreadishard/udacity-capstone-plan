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

## Interim (not the registered prefix) — 27 September, 18:3x: the fixed recipe on every admitted layer-B molecule finished by Sunday evening

Run on the laptop at 18:33 (four threads, 231 s), after `fetch_layerB_shards.sh merge` had brought 290 finished layer-B molecules from shards 0–3
(hel1-18, hel1-21, hel1-16, hel1-14) into the local corpus; the CCX53 shards 4 and 5 had not started (E8 still running). `m05/e7_rungB_pairs.py
corpus/molecules out/E7_rungB_layerB_2026-09-27 --use-analytic --split layerB --sizes all --seeds 0,1,2` → **pool 274 admitted layer-B molecules**
(16 of the 290 not admitted), hold-outs (a) 42 layer-A parents, (b) 39 scaffold molecules (fluoranthene, fluorene cores), (c) A2 molecules with more
atoms than the largest training molecule (26); 498 molecules in all; 60 epochs, seeds 0–2. Record: `out/E7_rungB_layerB_2026-09-27.json/.md`.

| hold-out | ring coupling ratio (B1 MLP, seed mean) | corrected ω RMS, cm⁻¹ (zero rule) | prediction set 1 at ≈ 300 (fixed recipe, `E11_power_law_2026-09-25b_analytic.md`) | B2 GBT ratio / ω |
|---|---|---|---|---|
| (a) bare parents | **0.61** | **6.18** (23.45) | 0.42 [0.42, 0.42] / 4.26 [4.20, 4.33] | 0.63 / 6.83 |
| (b) unseen scaffolds | **0.64** | **5.60** (23.09) | 0.46 [0.45, 0.47] / 4.82 [4.64, 4.99] | 0.56 / 6.16 |
| (c) A2 larger than the training maximum | **0.70** | **5.59** (22.85) | 0.56 [0.54, 0.57] / 5.36 [5.27, 5.46] (size split > 26 atoms) | 0.70 / 6.75 |

Diagonal RMS per family on (a): C–H stretch 1.75, C–H oop 6.77, ring in-plane 7.69, other 14.16 (the A2-trained model of 23 September at 175
molecules: 2.6 / 4.0 / 5.4 / 8.5); block RMS 1.88 against the median rule's 4.05; Duschinsky overlap 0.998; ΔH residual ratio 0.42.

**Reading (interim; no verdict by the rule of 12:1x).** The point lies *above* both prediction sets on every hold-out — ratio 0.61 against 0.42 on
the parents, 0.64 against 0.46 on the scaffolds, 0.70 against 0.56 on the size hold-out; corrected frequencies 6.2 / 5.6 / 5.6 cm⁻¹ against 4.3 /
4.8 / 5.4 — and above the 175-molecule A2-trained model it was compared with (0.43 / 0.47; 4.7 / 5.1 cm⁻¹). The non-neural check (B2) gives the same
picture (0.63 / 0.56 / 0.70), so it is the training set, not the optimiser. What the training set is: the 290 finished layer-B molecules have a
median of 18 atoms (maximum 26) and 80 % carry a heteroatom, against a median of 25 atoms (maximum 30) and 57 % for the 199 finished A2 molecules
and 21 atoms and 22 % for the parents (`corpus/manifest.csv`, read tonight) — layer B as computed so far is smaller and more heteroaromatic than
the molecules the hold-outs score, and the corpus factory's hashed order does not put the PAH-like part of B first. The prediction sets were fitted
on pools of A + A2 molecules that resemble the parents; the registered layer-B curve was never a prediction of the *level* at 300 but of the
*slope* over 100 → 300 → 600 → 1,200 within layer B, and that slope is not readable from one point. What this point does say: a network trained on
274 small, mostly heteroaromatic molecules still halves the ring-coupling error on unseen scaffolds and cuts the corrected-frequency error from 23
to 5.6–6.2 cm⁻¹ (zero rule 23), i.e. the local-coordinate target transfers across chemistry, at a lower level than within the PAH-like class. Open
and not decided here: whether the registered curve should be read on layer B alone (as written) or on A2 + B (a new registration), and whether
the factory's order for layer B should be re-hashed towards the PAH-like cores — both for the user, with the tuned point beside this one.

## Interim (not the registered prefix) — 27 September, 19:2x: the tuned protocol (stages 1 + 2) on the same 274 molecules

Same pool, hold-outs, seeds and read-outs as the fixed-recipe point above; `--tune --tune-stage2` (inner validation split per seed: learning rate
× width, then loss × optimiser); 2,817 s on four laptop threads beside the fixed run. Record: `out/E7_rungB_layerB_tuned_2026-09-27.json/.md`.

| hold-out | ratio, tuned (fixed) | corrected ω RMS, tuned (fixed) | prediction set 2 at ≈ 300 (tuned protocol, `E11_power_law_2026-09-25c_tuned.md`) |
|---|---|---|---|
| (a) bare parents | **0.59** (0.61) | **5.85** (6.18) | 0.39 [0.38, 0.40] / 3.57 [3.43, 3.73] |
| (b) unseen scaffolds | **0.65** (0.64) | **5.18** (5.60) | 0.44 [0.42, 0.47] / 4.29 [3.99, 4.58] |
| (c) A2 larger than the training maximum | **0.65** (0.70) | **5.01** (5.59) | 0.56 / 5.36 (size split, fixed recipe only) |

Diagonal RMS on (a), tuned: C–H stretch 1.58, C–H oop 4.86, ring in-plane 7.36, other 13.57 (fixed: 1.75 / 6.77 / 7.69 / 14.16). B2 GBT unchanged
(it is not tuned): 0.63 / 0.56 / 0.70.

**Reading (interim; no verdict).** The tuned protocol moves the level a little and in the expected direction — corrected frequencies 0.3–0.6 cm⁻¹
lower on all three hold-outs, the size hold-out's ratio 0.70 → 0.65, the C–H out-of-plane diagonal 6.8 → 4.9 on the parents — and leaves the
picture of the fixed-recipe point unchanged: both points lie above both prediction sets by 0.17–0.21 in the coupling ratio, for the reason given
above (the layer-B molecules computed so far are smaller and more heteroaromatic than the hold-outs). This is the 25 September finding again: the
recipe moves the level, not the distance to the prediction. Nothing here passes or fails the registered rule; the registered 100- and 300-tables
follow when the hashed order is complete, and the two questions above (B alone or A2 + B; re-hash B's order) are for the user.

## Dated amendment 27 September, 19:5x — a second, labelled curve on A + A2 + B (the user: "2: akkoord"; registered before it runs)

**Why.** The interim point of tonight showed that layer B as computed so far (small, mostly heteroaromatic) trains a model that scores the
ladder-like hold-outs worse than the A + A2 pool did. The registered curve (layer B alone, slope over 100 → 300 → 600 → 1,200) is unchanged and
keeps its verdict. Beside it, a second curve answers the mandate's question directly — *does adding layer B to the PAH-like pool help the ladder?*

**Definition.** `m05/e7_rungB_pairs.py corpus/molecules out/E7_rungB_A2B_<date> --use-analytic --split e6 --sizes all --seeds 0,1,2` with
`--pool-layers A,A2` (point 0: the PAH-like pool alone, every admitted A and A2 molecule outside the E6 hold-outs) and with `--pool-layers A,A2,B`
(point k: the same plus every admitted layer-B molecule at that date). E6 hold-outs (a) the 10 layer-A molecules of 19 September and (b) the 39
scaffold molecules; the fixed recipe; three seeds; the same read-outs. The curve is indexed by the number of layer-B molecules in the pool
(tonight ≈ 274; then at the registered 300 / 600 / 1,200 as they come). Each point is a `--sizes all` run of minutes on the laptop.

**Lines.** *B helps the ladder:* point k lies below point 0 on the ring-coupling ratio and the corrected-frequency RMS on both hold-outs by more
than the three-seed spread. *B adds nothing:* within the spread. *B hurts:* above the spread — then the order of layer B (decision 3, tomorrow) is
the first lever, and the registered layer-B curve is read as a transfer curve across chemistry, not as the ladder's curve.
**Prediction:** tonight's point lies within the spread of point 0 on (a) and slightly below on (b) (the scaffold hold-out is closer to layer B's
chemistry); after the re-hash, the +300 point lies below point 0 on both. **Order of work:** point 0 and tonight's point k run after the rung C
training finishes (the laptop is not shared); read against these lines; the result goes below this amendment.

## Dated amendment 27 September, 19:5x — the order of layer B is re-hashed towards the PAH-like cores tomorrow (the user: "3: morgen")

The corpus factory's hashed order for layer B put small heteroaromatic molecules first (median 18 atoms, 80 % with a heteroatom among the first
290). Tomorrow, 28 September, in a dated amendment of the corpus design and this note: a new order for the *not yet computed* part of layer B that
takes the all-carbon and larger cores first, with the hash inside each class; the 290 finished molecules stay admitted; the shards are restarted at
their next natural pause with the new manifest; the registered curve's "first 100 / 300 / 600 / 1,200 in hashed order" is then read in the new order
and says so. Nothing changes tonight while E8 runs on the CCX53 and the four Hetzner shards continue.

## Outcome of the A + A2 + B amendment — 27 September, 20:1x: points 0 and k (laptop, four threads each, 212 s and 351 s)

`--split e6 --sizes all --seeds 0,1,2 --use-analytic`, records `out/E7_rungB_A2B_point0_2026-09-27.md/.json` (`--pool-layers A,A2`: pool 175 — exactly the
registered floor's pool) and `out/E7_rungB_A2B_pointk_2026-09-27.md/.json` (`--pool-layers A,A2,B`: pool 449 = 175 + 274 layer-B molecules); hold-outs
(a) 10 layer-A molecules, (b) 39 scaffold molecules.

| point | pool | (a) ratio, seeds 0/1/2 | (a) corrected ω | (b) ratio | (b) corrected ω |
|---|---|---|---|---|---|
| 0: A + A2 | 175 | 0.429 / 0.435 / 0.428 | 4.79 / 4.68 / 4.68 | 0.467 / 0.458 / 0.487 | 5.13 / 4.89 / 5.46 |
| k: A + A2 + B (274) | 449 | 0.426 / 0.428 / 0.434 | 4.60 / 4.87 / 4.62 | 0.465 / 0.466 / 0.459 | 4.86 / 5.64 / 5.17 |

Point 0 reproduces the 23 September floor (0.43 / 0.47; 4.7 / 5.1). Point k differs from it by less than the three-seed spread on every read-out:
(a) 0.431 → 0.429 and 4.72 → 4.70 cm⁻¹; (b) 0.471 → 0.463 and 5.16 → 5.22 cm⁻¹. B2 GBT: (a) 0.48, (b) 0.53 at point k.

**Reading by the amendment's lines: "B adds nothing" — within the spread on both hold-outs.** The prediction (within the spread on (a), slightly
below on (b)) is met on (a) and, for the ratio only, marginally on (b). 274 small, mostly heteroaromatic molecules added to the 175 PAH-like ones
neither help nor hurt the ladder-like hold-outs: the pair model's local target lets the extra chemistry sit beside the PAH-like class without
disturbing it, and it brings nothing the ladder needs. That is the second reason, after tonight's interim point, for the re-hash of layer B towards
the PAH-like cores (decision 3, tomorrow); the next point of this curve is read after the re-hash, at +300 layer-B molecules in the new order.

## Dated amendment 2026-09-28 19:3x — the order of layer B re-hashed towards the PAH-like cores (applied, corpus design amended in `modules/05_support_predictor/corpus/README.md`; the user: "Ja, doe maar")

`corpus/rehash_layerB.py --apply` ran at 19:29 on the laptop's manifest and, with the same script, on each shard server's own manifest (hel1-18, -21,
-16, -14; server copies `manifest.csv.pre_rehash_2026-09-28_1729`, laptop copy `…_1929`). Only the `priority` column of the *pending* layer-B rows
changed (4,062 on the laptop; 4,047–4,058 on the servers, whose finished and running rows keep their status); no other column moved; the note column
carries `rehash-2026-09-28`. New order: class 0 all-carbon cores with two or more rings, then all-carbon one-ring, then heteroaromatic two-ring, then
heteroaromatic one-ring; inside a class larger first in bands of four atoms, the hash inside a band (proposal `rehash_layerB_proposal_2026-09-28_1929.csv`:
the first 300 of the new order have a median of 24 atoms and 0 % heteroaromatic cores, against 18 atoms and 80 % among the 290 finished under the old
order). The runners re-read the manifest before every pick, so each shard follows the new order from its next molecule without a restart; nothing running
was interrupted. The finished molecules stay admitted. The CCX53 (shards 4 and 5, after E8) receives the same manifest before it starts.

**For the reading of the curve.** The registered points 300 / 600 / 1,200 are now read in the new order and the outcome says so: the point at 300 has a
different composition (larger, all-carbon) from the points at 100 and 175, so a change of slope there is first a change of population, then a
learning effect — the two are separated by the class-wise read-out already registered (bare parents / scaffolds / size), not by the pooled number.
