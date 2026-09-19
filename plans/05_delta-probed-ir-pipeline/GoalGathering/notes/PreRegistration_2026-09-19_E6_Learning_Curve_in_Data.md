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
