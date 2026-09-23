# Pre-registration E6 — the embedding line as a learning curve in *data*, not a verdict at 45 molecules (written 19 September 2026, 23:2x, before any A2 molecule is computed; the user: "Nee zeggen na slechts 45 moleculen is niet goed. Laten we 'blijven trainen' tot hetgeen geleerd is dat we willen weten.")

## What we want to know

Tonight's E-series (same file, `PreRegistration_2026-09-19_E_Series_Learned_Mode_Embeddings.md`) established on 45 proxy molecules: the ring-in-plane family's per-mode label is ill-posed (E4); the family block's mean transfers to ≈ 4 cm⁻¹; the couplings inside the block do not transfer at 30 training molecules by any model tried (E5b coupling ratio 1.4–1.8 against the zero rule); nothing beats the mode-token Transformer on the diagonal (12.4). None of that says what happens at 200 or 868 molecules. Word embeddings work at scale; the question is the **slope**.

## Data

Corpus layer A2 (`modules/05_support_predictor/corpus/manifest.csv`, 868 rows): mono-substituted three- and four-ring cores — the class the ring family is about. Same deck as layer A (B3LYP and ωB97X Hessians at the B3LYP/6-31G* geometry), same runner, sharded across rented machines (`run_corpus.py --layer A2 --shard i/K`, merged by `merge_shards.py`). Median 25 atoms; from the layer-A timing law (wall ∝ N^3.2 on the CPX62) ≈ 70 min per molecule on 16 threads, ≈ 95 min at the 90th percentile.

**Phase 1:** the first ≈ 200 molecules in hash order (4 machines × 50, ≈ 2.5 days, ≈ €60 incl. VAT). **Phase 2:** the remaining ≈ 670 (≈ €160), started when phase 1 is in — on the user's word in both cases, because it is their credit.

## Held-out sets, fixed now

(a) The 12 layer-A molecules held out all day (unchanged, so every number is comparable with tonight's). (b) A scaffold hold-out inside A2: all substituted molecules of **two cores** chosen by hash of the core name once the A2 manifest's cores are listed (pyrene and one three-ring core if the hash falls so; the choice is written into the results file before training), so that the curve also measures transfer to an unseen core.

## Models on the curve (identical settings to tonight; three seeds)

M1 mode-token Transformer, per-mode target (the reference of the day); M2 the same with the **block target** (RECIPE amendment of 19 Sep: diagonal and couplings of the family block, loss balanced as in E5b); M3 E5b-tok (encoder + bilinear on K); M4 E5b-atoms; M5 the ridge and median baselines. Training sizes: 45, 100, 200 (phase 1); 400, 868 (phase 2). Per family: held-out RMS of the diagonal; for the ring family also the coupling ratio to the zero rule and the block RMS against the median rule.

## Readings, fixed now

- **Slope.** For each model and family the exponent of log RMS vs log n over the phase-1 points. The question "does the embedding line work" is answered by the exponent of M3/M4 on the ring diagonal and on the coupling ratio: **steeper than −0.25 over 45 → 200 means it is data-limited and phase 2 is expected to bring it under the Transformer**; flatter than −0.1 with the coupling ratio still ≥ 1.0 at 200 means the couplings of this proxy are not a learnable function of the mode's context at any size we can afford, and the block-mean route (M2 / median) is what pipeline A licenses for the ring family.
- **Crossing.** The first n at which any model's ring coupling ratio drops below 1.0, and below 0.7 (the E5 win); the first n at which the ring block RMS beats the median rule.
- **Transformer.** M1's ring diagonal at 200 against 12.4; M2's block against the median rule; whether M2's diagonal, read out from the block, is better or worse than M1's per-mode training (the block target's cost or gain).
- **Scaffold.** The same read-outs on hold-out (b); a gap of more than 3 cm⁻¹ between (a) and (b) on the ring block means the cores do not transfer and the label count of the 18 Sep desk note is counted per core.

## What this does not decide

Anything about the coupled-cluster correction (still two real points); the design note's Stage 1 (atom-level ΔH model) — it is run on the same curve when it exists; the BHHLYP − B3LYP proxy question (a separate, cheaper check on benzene and naphthalene, to be run first).

## Cost and safety

All DFT on rented machines; all training on the laptop at one thread and nice 19 (minutes per model per size) or on a rented machine; the anchor run is not touched. Results `modules/05_support_predictor/out/E6_learning_curve_in_data_<date>.{json,md}`; outcome sections appended here per phase.

**Added 20 Sep, 11:0x — first failure in phase 1.** Shard 1, acenaphthylene+ethynyl (A2_12c940207d): the B3LYP/6-31G* geometry optimisation did not converge in 50 optking steps (near-linear C≡C–H bend; 375 s). Anthracene+ethynyl on shard 3 converged, so the ethynyl group is not excluded. Failed molecules are not dropped from the curve silently: after phase 1 they get one retry in Cartesian coordinates with 200 steps; a molecule that fails twice is listed in the phase report with its error, and the curve sizes are counted on molecules actually labelled.

## Outcome, phase 1 (23 September 2026, 09:4x) — the curve is flat where it matters

Run: `modules/05_support_predictor/m05/e6_learning_curve.py` on the CCX53 (16 threads, 73 min); results
`modules/05_support_predictor/out/E6_learning_curve_in_data_2026-09-23.{json,md,log}`. Data: 244 molecules (A 45, A2 199;
the 20 with an imaginary mode kept, as on 19 September). Hold-out (a) = the 12 layer-A molecules of 19 September; hold-out (b) = the scaffold
cores **fluoranthene and fluorene** (the first two in sha1 order of the core name, 41 molecules; written to the results file before training). Pool 191, so the
sizes are [45, 100, 191] (the pre-registered "200" is 191). Three seeds; settings of 19 September (M1 600 steps, E5 1500 steps; M2 = the module's ΔH block
model, 30 epochs, block loss only). One departure from the plan: the "45" point is the first 45 of the mixed pool in hash order, not the 30-molecule
training set of 19 September, so that night's numbers (ring diagonal 12.4, coupling ratios 1.78 / 1.36) are a fourth point at n = 30, not a row here.

**Slope (the pre-registered question).** Ring coupling ratio to the zero rule on (a): M2 1.00 → 1.00 → 1.00 (slope +0.00),
M3 E5b-tok 1.91 → 1.81 → 1.86 (-0.02), M4 E5b-atoms 1.43 → 1.33 → 1.34 (-0.04). The criterion was
"steeper than −0.25 means data-limited"; every slope lies between −0.04 and 0.00. **The coupling read-out is not data-limited between 45 and 191
molecules: four times the data moves it by nothing.** No model crosses ratio 1.0 at any n — M2 predicts couplings of zero and sits at 1.00 exactly;
the balanced E5b models are worse than the zero rule at every n. Diagonal slopes on (a): ring M1 -0.11, M2 -0.13,
M3 +0.01, M4 -0.04 (slow gains); CH-oop M1 -0.34, M2 -0.26 (the clearest learning in data).

**Crossing.** Ratio < 1.0: never; < 0.7: never. Ring block (mean shift of the block) against the training-median rule on (a): M3 and M4 tie it at 45
(3.84 / 3.75 vs 3.90) and do not pull away; M2 is worse than the median at every n (4.63 → 5.63).
On (b) the median rule stands at 1.20 and no model reaches it (best M2 1.43).

**Transformer.** M1's ring diagonal on (a) at 191: 11.50 against 12.4 at n = 30 on 19 September; M2's diagonal read out from the block,
11.66, is the same — the block target costs nothing on the diagonal and buys nothing on the couplings. CH-oop 6.26 → 3.81 (M1).
*Open:* M1's "other" family on (a) worsens from 9.0 to 28.0 in all three seeds (per seed at 191: 26.0, 29.2, 28.7) while M2 stays at
11.4 and (b) improves (12.2 → 7.6); systematic, not seed scatter; the per-molecule diagnosis is queued on the CCX53.

**Scaffold.** Gap (b) − (a) on the ring block at 191: M2 -4.21, M3 -2.14, M4 -2.94 — the unseen cores are *easier* than the layer-A set, well inside
the 3 cm⁻¹ criterion; ring diagonal on (b) 7.08 → 6.05 (M1), 8.42 → 5.91 (M2). Cores transfer for the diagonal; the label count is not per core.

**What this decides.** By the rule fixed above, phase 2 (≈ 670 more A2 molecules, ≈ €160) is **not** expected to bring the coupling ratio under 1.0 and is
not started for that purpose. The transferable object stays the family-block diagonal (the 19 September lesson, now on 244 molecules with a flat coupling
curve behind it). The couplings need a different representation before more data is bought for them — a question for the 28th, not a run. The rule
itself held: the verdict rests on a curve, not on a point.
