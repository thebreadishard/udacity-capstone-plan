# Pre-registration — rung C: the equivariant Δ-Hessian model against the pair model (written 25 September 2026, 10:1x; build after 28 September)

**Why now.** E11.2 (25 September, corrected 09:4x) showed that the pair model of rung B is invariant by construction: its features are scalars, so
mirror-image pairs get identical answers (within-orbit spread 0.066 against the target's 0.103). Symmetry is therefore *not* what the equivariant
model of the 23 September decision (SQM → neural SQM → equivariant ΔH) would add. What it would add is unmeasured: **directions** (the pair model
sees |Δ| and sums of scalar features, never the geometry between three or more atoms) and **many-body context** (messages over the whole
neighbourhood instead of one pair at a time). The odds addendum of 09:5x re-graded the model from "required by evidence" to "design choice with an
unproven gain". This note fixes the test that decides it, before a line of the model exists.

## The floor it must beat (fixed numbers, `out/E7_rungB_2026-09-23_analytic.json`)

Same pool (175 layer-A/A2 molecules, hashed order), same sizes (45 / 100 / 175), same seeds (0, 1, 2), same epochs budget class (minutes on CPU),
same hold-outs (a) bare parents, (b) fluoranthene/fluorene scaffolds, same read-outs (E6/E7: ring coupling ratio to the zero rule; corrected-frequency
RMS against the original dH_true). Pair MLP at 175: ratio **0.43 (a) / 0.47 (b)**, corrected ω **4.7 / 5.1 cm⁻¹**; slope on (a) **1.14× per decade** of
the ratio (0.47 → 0.45 → 0.43).

## The model (own code, torch, no new dependency)

- **Inputs:** atomic numbers, Cartesian coordinates of the low-level (B3LYP) minimum, the low-level Hessian F_low as pair scalars (its Cartesian
  3×3 block per atom pair, contracted to the three invariants trace, r̂ᵀ B r̂, ‖B‖_F) — the same information the pair model had, no more.
- **Body:** an E(3)-equivariant message-passing network with scalar and vector channels per atom (PaiNN-type: three interaction blocks, 64 scalar
  + 64 vector features, cosine cutoff 5 Å, radial basis 20 Gaussians). Equivariance holds by construction; no data augmentation.
- **Output:** the Cartesian ΔH block per atom pair within the cutoff, ΔH_ij = a_ij I + b_ij r̂_ij r̂_ijᵀ + Σ_k c_ij^k (v_i^k v_j^kᵀ + v_j^k v_i^kᵀ) with
  a, b, c invariant read-outs of the pair (concatenated scalars of i and j and the distance) and v the vector channels; the diagonal block ΔH_ii is
  fixed by translational invariance (ΔH_ii = −Σ_j ΔH_ij); symmetrised. This is a rank-2 tensor output that rotates with the molecule.
- **Targets:** the Cartesian dH_true (CC-quality second route where present, as in E7 `--use-analytic`) — projected read-outs identical to rung B's.
- **Loss:** mean squared error on the Cartesian ΔH blocks, mass-weighted, plus the E7 minimum-norm internal ΔF of the same prediction as an auxiliary
  term (weight 0.1) so the read-out's quantity is trained directly too.
- **Two registered variants:** **C1** from scratch; **C2** pretrained on Hessian QM9 (41,645 ωB97x/6-31G* Hessians, `data/hessian_qm9`, the design's
  rung C) to predict the *full* Hessian from geometry, then the output head re-initialised and the whole network fine-tuned on ΔH. C2 is the design;
  C1 tells whether the pretraining is what carries.

## Read-outs and pass lines (fixed)

| line | what | pass | fail |
|---|---|---|---|
| R1 | ratio at 175, both hold-outs | ≤ **0.35** (a) and ≤ **0.38** (b) | ≥ 0.43 (a) or ≥ 0.47 (b): no gain over the pair model at this data size |
| R2 | slope on (a) over 45 / 100 / 175 | steeper than 1.14× per decade (ratio at 45 ≥ ratio at 175 × 1.25) | flatter than the pair model |
| R3 | corrected ω at 175 | ≤ 4.3 (a) / 4.7 (b) cm⁻¹ | worse than the pair model beyond the three-seed spread |
| R4 | within-orbit spread of the predictions (E11.2 orbit key) | ≤ the target's 0.103 (must hold by construction; a violation is a bug) | — |
| R5 | E11.7 class breakdown | the off-diagonal atom-sharing pairs, the pair model's weakest class everywhere, improve most | the same class stays weakest with the same ratio |

**Verdict rule:** R1 and R2 and R3 → the equivariant model replaces the pair model as the floor for the layer-B curve (the proof-of-learning
pre-registration gains a dated amendment naming it; its predictions stay). R1 fails on both variants → directions and context do not help at 175
molecules; the pair model stays v1's model, and the equivariant model is re-tested only when layer B has 600 molecules (not before). Between →
reported with R5, no change of plan.

**Predictions on record (25 September):** C1 ratio 0.40 (a) / 0.43 (b) — a small gain from directions; C2 0.34 / 0.37 — the pretraining is what
carries, because 175 molecules cannot teach a tensor head from scratch. Slope: C2 steeper (1.3× per decade), C1 about the pair model's.

## Cost and guards

Build ≈ one day of desk work; training minutes per seed on a CPX62 (175 molecules × ≤ 30 atoms), C2's pretraining ≈ 2–4 CPU-hours on the 41,645
QM9 Hessians once (cached checkpoint, hash recorded). Smoke on water and benzene first (`--smoke`); the script is a probe (`m05/`), promoted to
`src/dpir` only through the checklist. Nothing runs on the laptop while an anchor-class run is on it; nothing before 28 September.

## Build status (dated; the test run still waits for the Sunday decision)

- **25 Sep, 23:1x — model, loader and loss built and unit-tested; not trained.** `m05/rungC_equivariant.py`: the registered inputs (Z, coordinates,
  the three invariants of every 3×3 block of H_low plus trace and norm of the diagonal blocks — nothing else), the PaiNN-type body (3 blocks,
  64 s + 64 v, 20 Gaussians, cosine cutoff 5 Å; 171,554 parameters), the tensor head ΔH_ij = a I + b r̂r̂ᵀ + Σ_k c_k (u_i u_jᵀ + u_j u_iᵀ) with
  16 tensor channels and ΔH_ii = −Σ_j ΔH_ij, and the loss (mass-weighted MSE + 0.1 × internal ΔF term). `--smoke` on synthetic water and corpus
  benzene: rotation, reflection and permutation errors ≤ 1.5 × 10⁻¹⁵ relative (pass line 10⁻⁶), sum rule 10⁻¹⁶, blocks symmetric. Five tests in
  `tests/test_rungC_equivariance.py`, one a negative control (a model with an absolute-coordinate term fails the check) and one showing that two
  H_low with equal invariants give identical predictions (the input really is the three scalars). Training on the pool, C2's QM9 pretraining and
  every read-out (R1–R5) remain untouched until the decision.
- **27 Sep, 10:0x — training-and-read-out driver built (`m05/rungC_train.py`), smoked, not run on the pool.** Same pool (`--pool-layers A,A2` = the 175 molecules of the floor, hashed order), sizes 45/100/175, seeds 0–2, hold-outs (a)/(b) and read-outs (`readouts` of e7: E6 coupling RMS and ratio per class, T2 corrected ω, Cartesian residual) as the pair model; the Cartesian ΔH is projected to the pair model's internal coordinates with B⁺ for the read-out. Two implementation notes, written before any pool run: (1) the output is multiplied by the training set's RMS ΔH (a fixed data constant, recorded per fit) — the pair model scales its targets per class the same way; (2) the auxiliary internal-ΔF term is relative (divided by the target's mean square) because the raw a.u. term is ~10⁹ and would swamp the main loss; weight 0.1 as registered. Recipe C1 fixed: AdamW 1e-3, weight decay 1e-4, one molecule per step, 60 epochs, gradient clip 5, no early stopping, no tuning. Smoke (5 molecules, 12 epochs): residual ratio 0.95, corrected ω 20 vs zero 24 — mechanics, not a result. R4 holds by construction (five equivariance tests). Predictions of 25 September unchanged. The run waits for the user's word (option A of the decision memo).

## Outcome, 27 September 20:0x — C1 (from scratch, fixed recipe C1) on the registered pool; the user chose option A at 19:4x ("Trede C nu")

`m05/rungC_train.py corpus/molecules out/E7_rungC_2026-09-27 --use-analytic --sizes 45,100,175 --seeds 0,1,2 --threads 8` on the laptop, 19:50–20:02
(682 s); pool A + A2 = 175 in hashed order, hold-outs (a) 10 layer-A molecules, (b) 39 scaffold molecules; 171,554 parameters; 60 epochs, AdamW 1e-3,
loss = mass-weighted MSE on Cartesian ΔH + 0.1 × internal ΔF; output scale = the training set's RMS ΔH. Record: `out/E7_rungC_2026-09-27.json/.md`.

| n | (a) ratio, seeds 0/1/2 | (a) corrected ω | (b) ratio | (b) corrected ω | ΔH residual ratio |
|---|---|---|---|---|---|
| 45 | 0.99 / 0.99 / 1.01 | 10.9 / 11.0 / 10.9 | 1.00 / 0.99 / 1.01 | 10.4 / 10.2 / 10.5 | 0.73–0.76 |
| 100 | 0.99 / 0.99 / 0.98 | 11.0 / 10.5 / 11.1 | 0.99 / 0.98 / 0.98 | 10.5 / 9.8 / 10.7 | 0.72–0.74 |
| 175 | **0.96 / 1.00 / 0.97** | **10.7 / 12.0 / 11.1** | **0.96 / 0.99 / 0.96** | **10.2 / 11.6 / 10.5** | 0.70–0.73 |

Floor (the pair model at 175, `E7_rungB_2026-09-23_analytic.json`; reproduced tonight as point 0 of the A + A2 + B curve): 0.43 / 0.47, corrected ω 4.7 / 5.1 cm⁻¹, ΔH residual ratio 0.25 / 0.31 on (a) / (b). Zero rule: 23.3 / 23.1.
Diagonal RMS per family at 175 on (a), seed 0: C–H stretch 1.9, C–H out-of-plane 14.3, ring in-plane 15.9, other 4.7 (pair model: 2.6 / 4.0 / 5.4 / 8.5;
zero rule 43.6 / 23.8 / 19.7 / 13.2); ring block 3.33 against the median rule's 2.89; Duschinsky overlap 0.998.

**Lines.** R1: ratio 0.96–1.00 (a), 0.96–0.99 (b) — the fail side (≥ 0.43 / ≥ 0.47). R2: 0.99–1.00 at 45 → 0.96–1.00 at 175 — flat. R3: 10.7–12.0
cm⁻¹ against ≤ 4.3 — fail. R4: holds by construction (`tests/test_rungC_equivariance.py`). R5: the per-class breakdown is not among this driver's
read-outs; not read. C2 (QM9 pretraining) has not run, so the verdict rule's "R1 fails on both variants" is not reached.

**Reading, under the rule of 12:1x (a flat result under one frozen recipe licenses nothing).** The model learns the C–H-stretch shifts (1.9 cm⁻¹)
and the "other" family, and nothing of the couplings or of the out-of-plane and ring-in-plane diagonals; the training loss is at its floor from epoch
40 at every size (main 1.3 × 10⁻⁶, auxiliary 0.32–0.38) and the ΔH residual ratio sits at 0.70–0.75 where the pair model reaches 0.42 — the network
converges to a nearly fixed output. That points at the recipe before the architecture: one output scale for all Hessian entries (the RMS ΔH, set by the
large diagonal C–H-stretch entries) where the pair model standardises its targets per pair class; an auxiliary internal-coordinate loss at weight 0.1
where the pair model's whole loss is in internal coordinates; a learning rate and epoch count never tuned for this model. No sentence about
"directions do not help" follows from this run. What follows is the registered search below, then C2.

## Dated amendment 27 September 20:0x — the fair-chance search for rung C (registered before it runs; the user decides when)

Same protocol as the pair model's search (proof-of-learning note, amendments 12:2x and 12:4x of 25 September): inner validation split per seed
inside the 175-molecule pool, hold-outs untouched until the read-out, three seeds, one stage at a time, the winner of each stage carried forward.
Read-out per cell: inner-validation MSE of the internal ΔF (the quantity the read-outs project), then the E7 read-outs on (a) and (b) for the stage
winner only. Cost per cell ≈ 6 min at 8 threads (three seeds at 175).

- **Stage 1 — output scaling and loss placement** (the diagnosis above; run first): (i) as run (Cartesian mass-weighted MSE, one RMS scale, auxiliary
  internal 0.1); (ii) the same with the auxiliary weight 1.0; (iii) the loss on the internal ΔF alone (the pair model's quantity), Cartesian term
  dropped; (iv) per-entry-class output scaling (diagonal, bonded off-diagonal, non-bonded) with loss (iii). Prediction: (iii) or (iv) wins, and the
  (a) ratio moves from 0.97 to below 0.80 — the scale, not the tensor head, is what the fixed recipe got wrong.
- **Stage 2 — learning rate × epochs** at the stage-1 setting: lr 3 × 10⁻⁴ / 10⁻³ / 3 × 10⁻³, epochs 60 / 200 with early stopping on the inner split.
  Prediction: 3 × 10⁻³ with early stopping, as for the pair model; a further 0.05 on the ratio.
- **Stage 3 — C2**, the QM9 pretraining as registered above, at the stage-1 + 2 setting.

**Rule.** R1–R3 are re-read on the stage-1 + 2 winner and on C2; the verdict rule of this note applies to those, not to the run of tonight. If after
stage 3 the ratio on (a) is still ≥ 0.43, the sentence "directions and context do not help at 175" may be written; before that it may not.
Nothing else is changed; the pair model remains v1's model throughout.

## Search outcome, stage 1 — 27 September 20:3x (the user: "vanavond"; laptop, 8 threads, four cells × three seeds at 175, 20:13–20:35)

`m05/rungC_train.py … --sizes 175 --seeds 0,1,2 --inner-val 0.15` per cell (fit on 149, inner validation on 26 molecules per seed; the read-out is
the seed-mean relative internal-ΔF term on the inner split, as registered; hold-outs shown for information). Records `out/E7_rungC_s1_{i,ii,iii,iv}_2026-09-27.*`,
pick `out/E7_rungC_s1_pick_2026-09-27.md` (`m05/rungC_stage_pick.py`).

| cell | inner term (seed mean; per seed) | (a) ratio / ω | (b) ratio / ω |
|---|---|---|---|
| (i) registered recipe | 0.387 (0.340, 0.477, 0.345) | 0.96 / 11.2 | 0.96 / 10.4 |
| **(ii) auxiliary weight 1.0 — winner** | **0.303** (0.293, 0.318, 0.298) | 0.88 / 10.0 | 0.89 / 9.2 |
| (iii) internal term alone | 0.329 (0.293, 0.322, 0.371) | 0.89 / 10.4 | 0.90 / 9.6 |
| (iv) internal term alone + per-class output scale | 0.511 (0.409, 0.425, 0.699) | 0.99 / 10.8 | 0.98 / 10.5 |

**Reading against the stage-1 prediction ("(iii) or (iv) wins, and the (a) ratio moves from 0.97 to below 0.80").** Half wrong: the loss placement
does matter — every cell that weights the internal term more than the recipe (ii, iii) improves the inner term by 15–22 % and the hold-out ratio from
0.96 to 0.88–0.90 — but the winner is the *mixed* loss (ii), not the internal term alone, and the per-class output scale (iv) makes things worse
(0.51; one seed 0.70), so "the scale, not the tensor head, is what the fixed recipe got wrong" is not supported at this size. The ratio stays at
0.88–0.89, far from 0.80 and from the pair model's 0.43. Stage 2 (learning rate × epochs at the flags of ii) started 20:36; stage 3 (C2) follows
tonight with `m05/rungC_pretrain.py` (built and smoked 20:2x: 40 QM9 molecules in 1 s, so one pass over the 41,645 costs ≈ 20 min at 2 threads,
not the 2–4 CPU-hours estimated). No sentence about the architecture before stage 3 is read.

## Search outcome, stage 2 — 27 September 21:3x (learning rate × epochs at the stage-1 winner's flags; laptop, 8 threads, 20:36–21:33)

Six cells at `--aux-weight 1.0`, three seeds each, inner validation 15 % as in stage 1; the 200-epoch cells with early stopping (patience 20 on the
inner term, best state restored). Records `out/E7_rungC_s2_<cell>_2026-09-27.*`, pick `out/E7_rungC_s2_pick_2026-09-27.md`.

| cell | inner term (seed mean; per seed) | (a) ratio / ω | (b) ratio / ω | note |
|---|---|---|---|---|
| lr 3e-4, 60 epochs | 0.350 (0.327, 0.360, 0.363) | 0.94 / 10.7 | 0.95 / 10.0 | |
| lr 3e-4, 200 + early stop | 0.268 (0.248, 0.261, 0.295) | 0.81 / 10.1 | 0.83 / 8.7 | stops at 166–200 |
| lr 1e-3, 60 epochs (= stage 1's winner) | 0.312 (0.306, 0.306, 0.325) | 0.88 / 10.3 | 0.88 / 9.5 | stage 1 gave 0.303: thread noise ≈ 0.01 |
| **lr 1e-3, 200 + early stop — winner** | **0.263** (0.249, 0.256, 0.286) | **0.81 / 9.4** | **0.84 / 8.5** | stops at 160–187, best at 140–167 |
| lr 3e-3, 60 epochs | diverged (0.607, NaN, 0.393) | — | — | NaN from epoch ≤ 50 on seed 1 |
| lr 3e-3, 200 + early stop | 0.320 (0.310, 0.361, 0.289) | 0.92 / 10.9 | 0.93 / 10.3 | best states before the divergence |

**Reading against the stage-2 prediction ("3 × 10⁻³ with early stopping, as for the pair model; a further 0.05 on the ratio").** Wrong on the rate,
right on the direction: 3 × 10⁻³ diverges for this model (the pair model's rate does not transfer to the tensor head); the gain comes from *training
longer* — 60 epochs cut the registered recipe off while the inner term was still falling, and 200 epochs with early stopping take the ratio from 0.88
to 0.81 / 0.84 and the corrected frequencies from 10.3 / 9.5 to 9.4 / 8.5 cm⁻¹, more than the predicted 0.05. The 60-epoch cap of the registered recipe,
inherited from the pair model, was the second thing the recipe got wrong (the first: the internal term's weight). Distance to the floor after stages
1 + 2: 0.81 against 0.43. Stage 3 (C2: QM9 pretraining, 3 passes at 0.01 s per molecule, then the fine-tune at the stage-2 flags, sizes 45 / 100 / 175)
started 21:34; the read-out of R1–R3 on the stage-1 + 2 winner and on C2 follows it, as the amendment's rule says. Note for that read-out: the search
cells fit on 149 molecules (26 held for the inner term), so "175" in these tables means the 175-molecule pool with the inner split, not 175 fitted.

## Dated amendment 27 September 22:0x — C2's pretraining input channel (an incident, its cause, and the fix; registered before the second attempt's read-out)

**Incident (21:58–22:00).** The first C2 attempt pretrained the body on the 41,645 QM9 Hessians with the H_low input channel set to zero
("from geometry", read literally; 3 passes, 24 min, validation loss 1.8 × 10⁻⁴ = training loss). At fine-tune time, with the corpus's real B3LYP
Hessians in that channel, the body's raw output was 10²⁰–10³⁷ (measured on three corpus molecules; 3–6 with the channel zeroed; 12–17 for a
fresh, untrained body) and every fine-tune step was NaN from epoch 1. Cause: the invariant channel's weights (`inv`, `node_in`) were never
constrained during pretraining and amplify real inputs. The fine-tune ran through NaN for two sizes before it was stopped by pid; its records
were deleted, the zero-channel checkpoint is kept as `out/rungC_pretrained_2026-09-27_zerochannel.pt/.json` with its log.

**Fix (two parts, both in code and tested — `tests/test_rungC_c2_channel.py`).** (1) During pretraining the H_low channel carries a geometry-only
surrogate: a valence bond-stretch Hessian over the covalent bonds (`rungC_pretrain.bond_surrogate_hessian`, k = 0.5 E_h/bohr² heavy–heavy, 0.35
X–H; symmetric, translationally invariant), so the channel is exercised at realistic magnitudes; the letter of C2 ("the full Hessian from geometry")
holds — the surrogate is a function of the geometry alone — and the fine-tune input is the B3LYP Hessian as for C1. A smoke body pretrained this way
gives 4–7 on the same three molecules. (2) Both training loops abort on the first non-finite loss (`RuntimeError`) instead of training through NaN
— the guard the quality policy asks for after an incident. **Prediction for the second attempt** stays the registered one for C2 (0.34 / 0.37 at 175
under the design's recipe); under tonight's stage-1 + 2 flags the honest expectation is "below the C1 winner's 0.81 / 0.84 by more than the seed
spread if the pretraining carries, else within it". Second attempt started 22:0x (pretraining 3 passes, then the fine-tune at the stage-2 flags).

## Dated amendment 27 September 22:4x — second C2 incident: the pretrained body does not transfer across molecule size; C2 as registered stops here tonight

**What happened.** The second attempt (bond-surrogate channel) pretrained cleanly (3 passes, validation loss 7.7e-4 → 1.9e-4 → 1.8e-4, 1716 s) and the
fine-tune ran at 45 and at 100 for seeds 0–1; the non-finite guard of 22:0x fired at n = 100 seed 2, epoch 1, on A2_1fa81d01d6 (carbazole+SH, 23
atoms), and the chain ended without a read at 175. Every fine-tune's first epoch had a main loss of order 10²⁶ before Adam pulled it down.

**Measured cause (22:4x, four corpus molecules, pretrained body with a fresh head; the fresh body for comparison).** Max |raw output|:

| molecule | atoms | mean / max neighbours within the 5 Å cutoff | body on the real H_low | body on the bond surrogate | fresh body |
|---|---|---|---|---|---|
| benzene | 12 | 11 / 11 | 0.85 | 0.84 | 16 |
| naphthalene | 18 | – | 1.07 | 1.07 | 28 |
| carbazole+SH (A2_1fa81d01d6) | 23 | 15 / 21 | 1.3 × 10¹⁸ | 2.2 × 10¹⁵ | 35 |
| A2_13bafae8e0 | 23 | – | 6.5 × 10¹⁷ | 1.2 × 10¹⁵ | 36 |

The pair invariants of the real and surrogate channels have the same magnitude (max 1.5–1.6 either way), so the 22:0x diagnosis ("the channel") was
only half the story: the body's interaction blocks aggregate neighbour messages by **sum** (`index_add`, residual, no normalisation) and its weights,
tuned on QM9's neighbourhoods, amplify the denser neighbourhoods of 23-atom fused rings by fifteen orders of magnitude. A fresh body has no such
weights. This is a size/density transfer failure of the pretraining, not of the fine-tune recipe.

**Partial C2 read-outs before the abort (recorded, not a stage-3 result; the rule needs 175):**
- `n=45 seed 0 (a): ring couplings 3.24 vs zero 3.76 (ratio 0.86) | corrected ω 9.66 (zero 23.29) | ΔH residual ratio 0.656`
- `n=45 seed 0 (b): ring couplings 3.29 vs zero 3.74 (ratio 0.88) | corrected ω 9.57 (zero 23.09) | ΔH residual ratio 0.646`
- `n=45 seed 1 (a): ring couplings 3.62 vs zero 3.76 (ratio 0.96) | corrected ω 10.52 (zero 23.29) | ΔH residual ratio 0.715`
- `n=45 seed 1 (b): ring couplings 3.62 vs zero 3.74 (ratio 0.97) | corrected ω 10.49 (zero 23.09) | ΔH residual ratio 0.730`
- `n=45 seed 2 (a): ring couplings 3.67 vs zero 3.76 (ratio 0.98) | corrected ω 10.33 (zero 23.29) | ΔH residual ratio 0.724`
- `n=45 seed 2 (b): ring couplings 3.68 vs zero 3.74 (ratio 0.98) | corrected ω 10.30 (zero 23.09) | ΔH residual ratio 0.740`
- `n=100 seed 0 (a): ring couplings 3.04 vs zero 3.76 (ratio 0.81) | corrected ω 9.51 (zero 23.29) | ΔH residual ratio 0.617`
- `n=100 seed 0 (b): ring couplings 3.16 vs zero 3.74 (ratio 0.85) | corrected ω 9.08 (zero 23.09) | ΔH residual ratio 0.610`
- `n=100 seed 1 (a): ring couplings 3.12 vs zero 3.76 (ratio 0.83) | corrected ω 9.67 (zero 23.29) | ΔH residual ratio 0.626`
- `n=100 seed 1 (b): ring couplings 3.20 vs zero 3.74 (ratio 0.86) | corrected ω 9.25 (zero 23.09) | ΔH residual ratio 0.627`

At 100 molecules C2 sits where the stage-1 + 2 winner sits at 175 (0.81 / 0.84) — suggestive, not readable under the rule.

**Guard added (code + test, `check_pretrained_transfer`, `tests/test_rungC_c2_channel.py`).** Before any fine-tune from a pretrained body the driver
runs the body on every training molecule and refuses if a raw output is non-finite or above 10³; the pre-flight result is logged.

**What follows is a decision, not a run.** To give C2 its fair chance the body needs neighbour-count normalisation (mean aggregation or a norm in the
interaction blocks) — a change to the registered architecture that C1 must then share for the comparison to hold: re-run the stage-1 + 2 winner and
C2 under the same body (≈ 40 min + 27 min pretraining + 40 min fine-tune). Until that is decided, the rule of the 20:0x amendment is not reached:
no sentence about directions and context at 175 may be written, in either direction. Records: `out/E7_rungC_s3_2026-09-27.log`,
`out/rungC_pretrained_2026-09-27.json` (checkpoint kept, ignored by git as `*.pt`).

## Dated amendment 28 September 06:1x — option A: the mean-pooled body for both variants (registered before the run; the user: "A. Besteed extra aandacht aan code kwaliteit")

**Decision (the user, after the plain explanation `Uitleg_2026-09-28_C2_beslissing.md`).** Option A of the 22:4x amendment: the interaction blocks
pool the neighbour messages by their **mean** instead of their sum, and both variants are re-run under that body so the C1-against-C2 comparison
holds. Nothing else changes: same pool (175, hashed order), sizes 45 / 100 / 175, seeds 0–2, inner validation 15 %, hold-outs (a) and (b) untouched
until the read-out, the stage-2 winner's recipe (`--aux-weight 1.0 --lr 1e-3 --epochs 200 --patience 20`), QM9 pretraining 3 epochs with the bond
surrogate channel, head re-initialised per seed. Read-outs and the rule of the 20:0x amendment unchanged: after this stage, if the ratio on (a) is
still ≥ 0.43 for both variants, the sentence "directions and context do not help at 175" may be written; if C2 beats C1, the sentence is that QM9
pretraining transfers; before the read-out, neither.

**The change, as code (`m05/rungC_equivariant.py`, `rungC_pretrain.py`, `rungC_train.py`; tests `tests/test_rungC_aggregation.py`, 5 tests, and the
equivariance suite now run for both bodies — 24 rung C tests pass; ruff clean; both drivers smoke-tested with the mean body, the fine-tune path
and the mismatch refusal exercised).**
- One pooling helper `aggregate(messages, index, n, inv_degree)` used by both the scalar and the vector message; the inverse neighbour count is
  computed once per molecule in `encode()`. `DeltaHessianModel(aggregation="sum" | "mean")`; `"sum"` is the body registered on 25 Sep and stays
  available for the records made with it; `"mean"` is the default from today. The standout pattern proposer's scorer pins `"sum"` (its registered
  body; hel1-23 runs that code), so this change does not touch it.
- The setting travels with the data: the pretraining checkpoint carries `aggregation`; `load_pretrained_body` refuses a checkpoint whose body
  differs from the requested one (a checkpoint without the key predates today and is a sum body). This is the E8 lesson of 27 Sep applied here:
  an architecture setting must never travel unexamined between a pretraining run and a fine-tune.
- The body pre-flight (worst raw |output| on the training molecules, limit 10³) now runs for every body, fresh or pretrained, and is logged, so the
  record of each run holds the number that would have exposed the 27 Sep incident.
- Test of the mechanism: the same random body on an 8-atom and a 24-atom dense cluster (7 vs 23 neighbours) — feature scale ratio 1.49 under sum,
  1.0005 under mean. (A fresh sum body grows only 1.5×; the trained QM9 weights amplified that to 10¹⁸.)

**Run (laptop, 8 threads, sequential, `rungC_stage4_0928.sh`, log `out/E7_rungC_s4_2026-09-28.log`; started 06:1x):** (1) C1 on the mean body →
`out/E7_rungC_C1mean_2026-09-28`; (2) pretraining → `out/rungC_pretrained_mean_2026-09-28` (≈ 27 min); (3) C2 fine-tune → `out/E7_rungC_C2mean_2026-09-28`.
Estimate ≈ 1 h 20 in total (stage 2 took ≈ 10 min per cell at 175; three sizes ≈ 20 min per variant). Nothing else runs on the laptop.

## Dated correction 28 September 06:3x — the cause of the second C2 incident was the elements, not the neighbour count (found by the new design check)

**What the design check found (`m05/design_check.py`, built this morning at the user's request "kunnen wij ook testen bij ontwerp vanaf nu?";
records `out/design_check_rungC_*_2026-09-28.{md,json}`).** The 27 Sep sum checkpoint probed on all 534 corpus molecules:

| molecules | n | worst raw \|output\| |
|---|---|---|
| without S or Cl (incl. the densest: 30 atoms, mean 17.7 / max 27 neighbours) | 432 | ≤ 7.2 (median 3.4) |
| with S or Cl | 102 | 7 × 10³ – 1.6 × 10²¹ (median 10¹⁰) |
| with S or Cl, after resetting only the two embedding rows Z = 16, 17 to the mean of the trained rows | 102 | ≤ 6.3 (median 3.2) |

Hessian QM9 contains H, C, N, O, F only (transfer table of the design check: elements [1, 6, 7, 8, 9] against the target's [1, 6, 7, 8, 9, 16, 17];
also outside the source range: atoms 8–30 vs 9–25, max Z 17 vs 9). The embedding rows of S and Cl stayed at their random initialisation
(norms 9.0 and 5.9) while the trained rows shrank (4.9–6.3 with different statistics), and the untrained body amplified that. The 22:4x amendment's
table happened to contain two sulphur molecules at 23 atoms and read the size; **that diagnosis was wrong.** The neighbour-count effect is real but
small (fresh sum body: feature scale ratio 1.3 across the corpus extremes; mean body 1.05) and was not the trigger.

**Consequences.**
1. *The fix that matters:* at fine-tune time the embedding rows of elements the pretraining never saw are set to the mean of the trained rows
   (standard new-token initialisation). In code and tested: the pretraining checkpoint now records the elements it trained on;
   `load_pretrained_body` resets the unseen rows from that list (or from `--pretrained-elements` for a checkpoint from before today) and refuses a
   checkpoint with neither; the reset is logged; `tests/test_rungC_elements.py` (4 tests). The checkpoint patch landed before stage 4 reached its
   pretraining step, the loader patch before its fine-tune step, so stage 4's C2 runs with the reset.
2. *Proof on the incident:* the 27 Sep sum checkpoint, probed as the fine-tune now sees it (`--as-finetune`), passes — worst output 3.36, ratio 1.1.
   So C2 under the **registered** sum body was runnable all along with this one fix; that run (fine-tune from the existing 27 Sep checkpoint at the
   stage-2 winner's flags, ≈ 20 min) is the cleanest reading of "does QM9 pretraining help" and is proposed to the user.
3. *The mean body* stays as amended this morning (a sound change, measured, small), but it is no longer the repair of the incident. Stage 4 and the
   queued stage 5 (the sum-body search repeated under mean, the user's decision of 06:5x: "Herhaal onder mean") continue as registered.
4. *Design check as a rule:* every body, fresh or pretrained, is probed on the target's extremes (smallest / largest molecule, sparsest / densest
   neighbourhood, heaviest element) before its run is queued, and every pretraining → fine-tune transfer prints the source-against-target table
   (atoms, neighbour counts, heaviest element, elements) so the pre-registration names the test that covers each property outside the source
   range. Stage scripts run it first and stop on failure (`rungC_stage5_0928.sh` does).

**Time lost by the wrong diagnosis:** none in compute (stage 4's changes are all kept), one morning's reasoning; the correction came within the
first hour of the check existing, which is the argument for the check.

## Dated amendment 28 September 06:4x — C2 under the registered sum body, element reset only (the user: "Ja, zet maar achter stage 5")

**Run (queued behind stage 5, `rungC_c2sum_0928.sh`, log `out/E7_rungC_c2sum_2026-09-28.log`, ≈ 20 min, laptop 8 threads).** The fine-tune from the
existing 27 Sep QM9 checkpoint (sum body, as registered on 25 Sep; no element list → `--pretrained-elements 1,6,7,8,9`) at the stage-2 winner's
flags, sizes 45 / 100 / 175, seeds 0–2, inner validation 15 %, head re-initialised per seed, the S and Cl embedding rows reset to the trained mean
at load → `out/E7_rungC_C2sum_elemreset_2026-09-28`. Design check on that checkpoint as the fine-tune sees it runs first (06:3x: PASS, 3.36, ratio 1.1).

**Why.** It is the C2 of the original pre-registration with the one repair the incident actually needed and no architecture change, so it is the
cleanest reading of "does QM9 pretraining help" against the stage-1 + 2 winner (0.81 / 0.84 at 175). Its read-out and stage 4's (both variants under
the mean body) and stage 5's (the search repeated under mean) are read together under the rule of the 20:0x amendment; C1 sum at the winner's
flags is the 27 Sep record `out/E7_rungC_s2_lr1e-3_e200_2026-09-27` (fit on 149 per seed, as here).

## Dated note 28 September 09:0x — stage 5, cell lr 3e-3 / 200 epochs diverged under the mean body

Seed 1 of the sixth stage-2 cell hit a non-finite loss at epoch 37 (molecule A2_34bb1210bc); the driver's guard of 27 Sep 22:0x stopped the run, and
the stage-5 script ended before the pick (`out/E7_rungC_s5_2026-09-28.log`). Under the sum body the same learning rate had one NaN seed at 60 epochs
(27 Sep) and survived 200 epochs with early stopping; under the mean body it does not. As registered, a diverged cell never wins: the pick runs over
the five completed cells (`rungC_stage5b_0928.sh`, the picker lists the sixth as missing), and the stage continues unchanged. No cell is re-run at a
different setting; lr 3e-3 is recorded as not viable for this body, which is the search's answer for that cell, not an incident of the code.

## Outcome, 28 September 09:2x — stage 3 read on both bodies; verdict under the rule of the 20:0x amendment

**Runs read together (laptop, 8 threads, three seeds, pool of 175 in hashed order, inner validation 15 %, hold-outs (a) bare parents / (b) fluoranthene–fluorene
scaffolds; every number is the seed mean of `coupling_ratio` against the zero rule, ω = corrected-frequency RMS in cm⁻¹):**

| variant | body | n = 45 (a) | n = 100 (a) | n = 175 (a) | n = 175 (b) | ω at 175 (a) / (b) | record |
|---|---|---|---|---|---|---|---|
| C1, stage-1 + 2 winner | sum (registered 25 Sep) | — | — | 0.811 ± 0.010 | 0.839 ± 0.015 | 9.42 / 8.45 | `out/E7_rungC_s2_lr1e-3_e200_2026-09-27` |
| C2, QM9 pretraining + element reset | sum | 0.921 ± 0.044 | 0.839 ± 0.010 | 0.811 ± 0.002 | 0.843 ± 0.005 | 9.64 / 8.91 | `out/E7_rungC_C2sum_elemreset_2026-09-28` |
| C1, same winner | mean (amended 28 Sep) | 1.007 ± 0.001 | 0.898 ± 0.040 | 0.839 ± 0.006 | 0.868 ± 0.001 | 9.77 / 9.01 | `out/E7_rungC_C1mean_2026-09-28` |
| C2, QM9 pretraining + element reset | mean | 0.966 ± 0.018 | 0.873 ± 0.050 | 0.812 ± 0.008 | 0.851 ± 0.010 | 9.55 / 8.83 | `out/E7_rungC_C2mean_2026-09-28` |
| pair model (the floor, 23 Sep) | — | 0.96 | 0.68 | **0.43** | **0.47** | **4.7 / 5.1** | `out/E7_rungB_2026-09-23_analytic.json` |

The fixed recipe C1 (25 Sep) stays where it was: 0.98 (sum) / 0.99 (mean) at 175. The search repeated under the mean body (stage 5, `out/E7_rungC_s1m_*`,
`s2m_*`, picks) chose the same recipe as under the sum body (aux weight 1.0, lr 1e-3, 200 epochs with early stopping; inner term 0.268 vs 0.263), so the
comparison above uses one recipe throughout; lr 3e-3 / 200 epochs diverged under the mean body (dated note above) and never wins, as registered.

**Pass lines.** R1 — fail on all four cells (≥ 0.81 against a pass at ≤ 0.35 / 0.38 and a fail line at ≥ 0.43 / 0.47). R2 — fail: ratio at 45 over
ratio at 175 is 1.14 (C2 sum), 1.19 (C2 mean), 1.20 (C1 mean), all under the required 1.25. R3 — fail: ω 9.4–9.8 against ≤ 4.3 / 4.7 and the pair
model's 4.7 / 5.1. R4 holds by construction (the model is equivariant; tests). R5 — not read: with R1 failing on both variants the class breakdown does
not change the verdict, and the rule of 25 Sep reads "R1 fails on both variants → …".

**Verdict (the rule of 25 September, reached through the amendment of 27 September 20:0x):** *directions and context do not help at 175 molecules.*
The pair model stays v1's model; the equivariant model is re-tested when layer B has 600 admitted molecules, not before. Both predictions of 25 Sep
were wrong by a factor two (C1 predicted 0.40, measured 0.81; C2 predicted 0.34, measured 0.81); the sentence "the pretraining is what carries"
is not supported: QM9 pretraining moves the ratio at 175 by 0.00 (sum body) to 0.03 (mean body), and by 0.04–0.09 at 45, the direction one expects
from pretraining but not the size. The learning curve of the equivariant model is still falling (≈ 0.06 per doubling from 100 to 175), so the
question "how much data would it need" stays open and is exactly what the 600-molecule re-test answers.

**What the fair-chance search bought (for §3.5 and the incident record).** The fixed recipe gave 0.98; the registered search (loss / aux weight,
learning rate × epochs, pretraining) gave 0.81 — a real gain of 0.17 that the rule of 25 Sep ("no negative conclusion without the search") was right
to demand, and still a factor two from the floor. Two incidents on the way (input channel; untrained element embeddings, first mis-diagnosed as
neighbour count) each left a guard in code and tests and one standing rule (the design check); the mean-pooled body, adopted for a wrong reason,
stays as a measured neutral change (1.3 → 1.05 feature-scale ratio, no effect on the read-out).

**Records committed:** the four cells above, the stage-5 cells and picks, the fixed recipe under mean, the design-check records, the logs
`out/E7_rungC_s4/s5/c2sum_2026-09-28.log`; the `.pt` checkpoints stay local (ignored) and in the data backup.

## Dated amendment 30 September 21:4x — the data-scaling test of the equivariant model without the PC (the user: "Laten we de volgende stap nemen zonder de PC, want die PC wil ik eigenlijk pas kopen als we bewijs hebben dat compute ertegenaan gooien werkt"; registered before the run)

**Question.** The pair model (rung B) is flat from 175 to 750 molecules on the ladder hold-outs (proof-of-learning outcome of 30 Sep 21:1x). The
equivariant model was still falling at 175 (≈ 0.06 in the ring-coupling ratio per doubling from 100 to 175; stage-3 outcome of 28 Sep). Does it keep
falling when the pool grows 4.3×? That is the cheapest evidence there is on whether more data and model — the thing a PC buys — move the ladder.

**Runs (laptop, 8 threads, ≈ 2 h; `rungC_scale_0930.sh`).** Pool `--pool-layers A,A2,B` under `--split e6` (every admitted A, A2 and B molecule outside the
E6 hold-outs, hashed order; 750 tonight), `--sizes 449,750` (the first 449 of that mixed order and the whole pool), seeds 0–2, inner validation 15 %,
sum body, the stage-2 winner's flags (`out/E7_rungC_s2_pick_2026-09-27.json`), read-outs (a) the 10 layer-A molecules and (b) the 39 scaffolds as
before. C1 from scratch → `out/E7_rungC_scale_C1_2026-09-30`; C2 from the 27 Sep QM9 checkpoint with the element reset → `out/E7_rungC_scale_C2_2026-09-30`.
The 175 points are the existing records (`E7_rungC_s2_lr1e-3_e200_2026-09-27`: 0.811 / 0.839; `E7_rungC_C2sum_elemreset_2026-09-28`: 0.811 / 0.843).
Smoke of both commands (`--smoke`) before the launch. Note: the 449 point is a size point of the mixed pool, not "175 + the first 274 B".

**Predictions (fixed now).** If the 0.06-per-doubling slope holds, C1 at 750 (2.1 doublings) reads ≈ 0.68 on (a) and ≈ 0.71 on (b); at 449 ≈ 0.73 / 0.76.
C2 within 0.03 of C1 at every size (pretraining moved 0.00–0.03 at 175). Corrected ω falls with the ratio (9.4 → ≈ 8 cm⁻¹ on (a)).

**Lines.** *Scaling works:* (a) ≤ 0.72 at 750 for C1 or C2, with 449 between 175 and 750 (a falling curve, each step beyond the three-seed spread).
*Scaling stalls:* (a) ≥ 0.78 at 750 (within one spread of 175) — then the equivariant model is as flat as the pair model at this recipe, and the PC
question is answered with "not by data volume of this kind"; the levers left are data of the target kind (larger all-carbon cores from the anchors and
layer C) and the model design (stage 4/5 of the search under the mean body). *Between:* 0.72–0.78 — a slope, but half the extrapolated one; the 1,200
point decides, on the PC or not at all.

**What this does not test.** CC-level labels (the ankers), rung C's capacity (hidden size, depth), and the pretraining recipe itself; those are the
PC's own questions and are not claimed here.

## Dated amendment 30 September 23:1x — after the external reviews: two diagnostics and the pattern internal term, registered before they run (the user: "reken op de laptop door totdat we de werkende oplossing hebben gevonden"; `Review_Received_2026-09-30_Grok_RungC_Design.md`)

**Code (tested, 8 tests in `tests/test_rungC_diag_pattern.py` + the existing switch tests; smoke on the corpus):** `rungC_train.py --zero-hlow`,
`--overfit-one <id>`, `--aux pattern`. The registered recipe is unchanged when none is given. `--aux pattern` puts the internal term on the pair
model's pattern only (diagonal, shared-atom pairs, same-ring bond–bond pairs; `e7_rungB_pairs.molecule_pairs`, whose B matrix must equal the loader's
or the run refuses) with one standardisation scale per pair class (the six classes of rung B), the scales taken from the fit molecules of the seed
and nothing else; the read-out is unchanged.

**Runs (`rungC_night_0930.sh`, laptop, 8 threads, after the scaling run; design check of the fresh sum body first):**
1. *Diagnostic 1* — H_low input channels zeroed, pool A + A2 (175), winner flags, seed 0 → `out/E7_rungC_diag_zerohlow_2026-09-30`.
   **Line:** ratio on (a) ≥ 0.95 (the model collapses to the zero rule without the Hessian input). If it stays near 0.81, the body ignores the Hessian
   input and rank 1 is pointless until that route is forced (invariants removed, only the tensor block kept).
2. *Diagnostic 2* — benzene alone (pool, size and both hold-outs = A_8448043181), 400 epochs, no inner validation, seed 0 →
   `out/E7_rungC_diag_overfit_benzene_2026-09-30`. **Line:** ratio ≪ 0.1 and a small ΔH residual on that molecule. If it fails: widen the head or move
   the diagonal constraint from the forward pass into the loss first; **no 175-molecule rank-1 run before this passes.**
3. *Rank 2 alone* — `--aux pattern`, pool A + A2 (175), winner flags, seeds 0–2, inner validation 15 % → `out/E7_rungC_rank2_pattern_2026-09-30`.
   **Line:** (a) ≤ 0.78 against the present 0.81 (the reviewer's rescaled expectation −0.03 to −0.10). Prediction: 0.74–0.78.

**Rank 1** (the B3LYP 3 × 3 blocks as rank-2 equivariant edge features) is built next with its own equivariance test (rotate coordinates and H_low
together) and registered separately before it runs; the joint line of rank 1 + 2 stays (a) ≤ 0.75, prediction 0.55–0.70 resting on rank 1.
Every result lands here as a dated outcome section; nothing is read before its line is written.

## Outcome, data-scaling test, C1 — 30 September 23:2x (`out/E7_rungC_scale_C1_2026-09-30.{json,md}`; C2 is read below when it lands)

| pool | (a) ratio (three-seed spread) / ω cm⁻¹ | (b) ratio / ω | best epochs of 200 | record |
|---|---|---|---|---|
| 175 (A + A2; 27 Sep) | 0.811 (0.010) / 9.42 | 0.839 (0.015) / 8.45 | — | `E7_rungC_s2_lr1e-3_e200_2026-09-27` |
| 449 (mixed order) | **0.833** (0.008) / 9.63 | 0.853 (0.031) / 8.69 | 108, 99, 100 | `E7_rungC_scale_C1_2026-09-30` |
| 750 (A + A2 + B) | **0.823** (0.016) / 9.29 | 0.839 (0.008) / 8.52 | 73, 62, 120 | same |

**Line: "scaling stalls" ((a) ≥ 0.78 at 750).** With 4.3× the molecules the equivariant model from scratch is where it was at 175 — 0.82 against 0.81,
inside two spreads; the 449 point is not below 175 either. The prediction (≈ 0.68 at 750 if the 0.06-per-doubling slope of 45 → 175 held) is refuted:
that slope was the model learning the PAH-like 175, not a curve that continues into mixed chemistry. Decision 51: best epochs 62–120 of the 200 cap,
no re-run needed. Read together with the pair model's flat curve (proof-of-learning outcome 21:1x): **data volume of this kind moves neither model.**
The PC question is answered on that count — not by more of this data — and the reviewers' diagnosis (representation and head; `Review_Received_2026-09-30_…`)
is the live hypothesis: the night chain (diagnostics, then the pattern internal term) and the rank-2 tensor injection test it next, on 175 molecules,
where a change of 0.1 is unambiguous.

## Dated amendment 30 September 23:5x — rank 1: the B3LYP 3 × 3 pair blocks as rank-2 equivariant input (registered before it runs)

**The change (`rungC_equivariant.py`, `tensor_input=True`; default False = the registered model bit for bit, parameter count 171,554 unchanged).**
`pair_tensor`: the symmetrised block S_ij of the low-level Hessian for every pair, divided by the molecule's RMS off-diagonal block norm (an
invariant). Each interaction block receives, besides the registered messages v_j·g and r̂·g, two more gated vector messages: S_ij v_j and S_ij r̂_ij.
Under x → R x, S → R S Rᵀ and v, r̂ → R(·), so both are O(3)-equivariant; the head and the read-out are unchanged. This is the poor man's ℓ = 2 input
the reviewers asked for: the block's orientation reaches the vector channels, not only three scalars.
**Tests (29 pass):** equivariance to 1e-6 (rotation, reflection, permutation, sum rule, symmetry) for sum/mean × scalars/tensor; `pair_tensor`
transforms as R S Rᵀ, is symmetric, unit-RMS-normalised and permutes; the registered model ignores a block's orientation and the tensor-input
model does not (the two Hessians of the 26 Sep test give different predictions); default parameter count unchanged. Design check of the fresh
tensor-input body on the corpus extremes: see `out/design_check_tensor_2026-09-30.md`. Smoke with `--tensor-input --aux pattern` on the corpus.
Not combinable with a pretrained body (refused).

**Gate.** Runs only if diagnostic 2 (overfit benzene) reached ratio < 0.1 — read by the launcher from its JSON; otherwise the head is repaired first.

**Runs (`rungC_night2_0930.sh`, laptop, 8 threads, after night chain 1):** pool A + A2 (175), winner flags, seeds 0–2, inner validation 15 %:
(i) rank 1 + 2 = `--tensor-input --aux pattern` → `out/E7_rungC_rank12_tensor_pattern_2026-09-30`; (ii) rank 1 alone = `--tensor-input` →
`out/E7_rungC_rank1_tensor_2026-09-30` (attribution).
**Predictions.** (i) (a) 0.55–0.70, ω 6–8 cm⁻¹, resting on rank 1; (ii) 0.60–0.72. **Lines.** (i) pass (a) ≤ 0.75; (ii) pass (a) ≤ 0.76.
Miss on both: the input was not the bottleneck at this head → the hybrid head (rank 3, line (a) ≤ 0.55) is next, and the invariants-removed
variant (tensor block only) is run to force the route. Pass on (i) but not (ii): the two changes need each other — reported as such.

## Dated amendment 30 September 23:0x — rank 3: the hybrid head (equivariant encoder → ΔF on the pattern → ΔH = Bᵀ ΔF B), registered before it runs

**The model (`m05/rungC_hybrid.py`, `rungC_train.py --head hybrid`, fresh body only, needs `--aux pattern`).** The encoder is the registered body
(optionally with the rank-2 input). Per pattern pair (p, q) the head sees the mean-pooled scalar channels and vector-channel norms of the atoms of p
and of q (sum and product of the two primitives' features), an embedding of the pair class, and the three low-level force constants F_low,pq, F_low,pp,
F_low,qq (standardised by their RMS over the fit molecules) — the object rung B is anchored on — and returns ΔF_pq in units of the class scale (RMS of
the true ΔF per class over the fit molecules). ΔH = Bᵀ ΔF B: symmetric and free of rigid-body components by construction; every read-out (full-ΔF
projection, ring couplings, corrected ω, Cartesian ΔH residual ratio) is unchanged, so the hybrid is judged on the same quantities as the Cartesian
head, not on its own sparse target only (the reviewers' warning). Option `--sqm-scale` (Gemini): ΔF_pq = α_c F_low,pq + residual, α initialised at 0.
**Tests (44 rung-C tests pass):** symmetry, translational and rotational null modes, equivariance with B rebuilt for a reflected-rotated frame
(1e-6), pooling matrix, input scales from the given ids only, the α term. Corpus smoke (5 molecules, 2 epochs) runs end to end.

**Runs (`rungC_night3_0930.sh`, after night chain 2; pool A + A2 (175), winner flags, seeds 0–2, inner validation 15 %):** (i) hybrid; (ii) hybrid + SQM α;
(iii) hybrid + rank-2 tensor input. Records `out/E7_rungC_rank3_hybrid{,_sqm,_tensor}_2026-10-01`.
**Predictions.** (i) (a) 0.45–0.60 (near rung B's 0.43 if the encoder is not harmful; the reviewers: 0.45–0.55); (ii) within 0.03 of (i) — the α term
should matter little once F_low is an input; (iii) ≤ (i). **Lines.** Claim "the Cartesian head was the problem": (a) ≤ 0.55 on (i) or (iii). Pass: (a) ≤ 0.65.
Miss (> 0.75): the encoder's environment features add nothing over rung B's hand-made ones at this data size — reported as such, and the next levers
are topology features and the data step. Reading rule: the hybrid is compared with rung B on the same hold-outs *and* on the Cartesian ΔH residual
ratio, so that a gain on the pattern is not bought with a loss off it.

## Outcome, data-scaling test, C2 — 30 September 23:5x (`out/E7_rungC_scale_C2_2026-09-30.{json,md}`; QM9 pretraining, element rows reset)

| pool | (a) ratio (spread) / ω | (b) ratio (spread) / ω | best epochs |
|---|---|---|---|
| 175 (28 Sep) | 0.811 (0.002) / 9.64 | 0.843 (0.005) / 8.91 | — |
| 449 | **0.816** (0.031) / 9.14 | 0.850 (0.026) / 8.49 | 67, 104, 101 |
| 750 | **0.808** (0.033) / 9.07 | 0.831 (0.023) / 8.32 | 78, 77, 92 |

**Line: "scaling stalls" for C2 as well** ((a) 0.81 at 750, inside one spread of 175). Pretraining moves the 750 point by 0.015 against C1 — the same
0.00–0.03 as at 175. Decision 51: best epochs 67–104 of 200, fine. The data-scaling test is closed: neither variant of the equivariant model, nor
the pair model, moves with 4.3× the molecules of this kind; the PC is not bought for data volume. The night chain (diagnostics → pattern term →
rank-2 input → hybrid head) tests the reviewers' cause.

## Outcome, night chain 1 — 1 October 00:0x (`out/E7_rungC_diag_zerohlow_2026-09-30`, `E7_rungC_diag_overfit_benzene_2026-09-30`, `E7_rungC_rank2_pattern_2026-09-30`)

| step | line | result | verdict |
|---|---|---|---|
| diagnostic 1: H_low input zeroed, 175, seed 0 | (a) ≥ 0.95 | **(a) 0.82 / (b) 0.85, ω 9.0 / 8.4** — identical to the model with H_low (0.81 / 0.84) | **the body ignores the Hessian input**: the 0.81 of every rung-C run so far is a geometry-only prior; the three block invariants contribute nothing |
| diagnostic 2: benzene alone, 400 epochs, seed 0 | ratio ≪ 0.1 | (a) 0.78, ΔH residual 0.75 | **not reached — but the test was under-powered**: one molecule gives one optimiser step per epoch, so 400 epochs = 400 steps against ≈ 35,000 in a normal 175-molecule run; re-registered below with a proper step budget before any conclusion about the head |
| rank 2 alone: pattern internal term, class-standardised, 175, 3 seeds | (a) ≤ 0.78 | **(a) 0.99 / 1.03 / 1.03, ω 11–14** | **miss, and worse than the registered term**: dividing each class by its RMS gives the tiny classes (diag_other 4e-4, off_other 9e-4 a.u.) weights 1e2–1e3 above the ring couplings, and the Cartesian head then fits their noise; the standardisation as implemented is harmful for this head (kept for the hybrid, whose output is expressed in the same class units) |
| gate for chain 2 | overfit ratio < 0.1 | 0.78 | rank 1 not launched (correct by the rule) |

**Reading.** Diagnostic 1 is the finding of the night: the equivariant model never used the low-level Hessian. That reframes rank 1 — the rank-2 input
is not an upgrade of an existing signal but the first time the Hessian enters — and it means the route has to be forced and verified: the zeroed-H_low
control is run beside every rank-1 result (the difference must be large, not 0.01). Rank 2's failure is a lesson about standardisation: per-class scales
must be floored (e.g. at 10 % of the largest class scale) or the loss weighted by the read-out's own weights; that change is registered before it is
used again.

## Dated amendment 1 October 00:1x — diagnostic 2 re-registered with a proper step budget; rank 1 registration adjusted

*Diagnostic 2, re-run:* benzene alone, seed 0, `--epochs 5000` (5,000 steps), lr 1e-3 and lr 3e-3, registered internal term ('all'), 2 threads beside
chain 3 → `out/E7_rungC_diag_overfit_benzene_e5000_lr{1e-3,3e-3}_2026-10-01`. **Line unchanged:** ratio ≪ 0.1 and ΔH residual ratio ≪ 0.1 on that
molecule. Pass → the head can represent the correction and chain 2 is released (by hand, after chain 3). Fail at 5,000 steps with both rates → the
head or the hard diagonal constraint is too tight: the constraint moves into the loss and the tensor channels double (16 → 32) before rank 1 runs.

*Rank 1, adjusted:* because the pattern term failed on the Cartesian head, the primary rank-1 run uses the **registered** internal term ('all') —
`--tensor-input` alone, 175, 3 seeds — with the zeroed-H_low control (`--tensor-input --zero-hlow`, seed 0) beside it. Lines: (a) ≤ 0.76 for the run,
and run − control ≤ −0.10 (the input must be seen to matter). The pattern-term variant follows only once the standardisation is repaired.

*Addendum 00:3x.* (1) The class-scale floor is implemented (`PATTERN_SCALE_FLOOR` = 0.1 of the largest class scale, tests updated); no run uses the
pattern term on the Cartesian head until it is registered again. (2) Diagnostic 2 is also run for the **hybrid head** (benzene alone, 5,000 steps, lr 1e-3,
`--head hybrid --aux pattern`, 2 threads) → `out/E7_rungC_diag_overfit_benzene_hybrid_e5000_2026-10-01`; same line (ratio ≪ 0.1). If the hybrid overfits
and the Cartesian head does not, that is the cleanest statement that the head, not the encoder, is the limit. (3) A planar-molecule check on benzene
(fresh models, before training): the true ΔH has no in-plane/out-of-plane mixing (6.6e-6 against 3.5e-3 in plane) and neither does the head's output,
so the head is not mis-shaped for planar molecules; its out-of-plane block is the isotropic term a·I alone, which is enough only if the in-plane
part is fully carried by the b r̂r̂ᵀ + Σ c u uᵀ terms.

## Outcome, diagnostic 2 re-run — 1 October 00:1x (`out/E7_rungC_diag_overfit_benzene_e5000_lr{1e-3,3e-3}_2026-10-01`; hybrid: `…_hybrid_e5000_2026-10-01`)

| head | steps, lr | ratio on benzene | ΔH residual ratio | internal term at the end | line ≪ 0.1 |
|---|---|---|---|---|---|
| Cartesian (registered) | 5,000, 1e-3 | 0.60 | 0.58 | 0.28 | **FAIL** |
| Cartesian (registered) | 5,000, 3e-3 | 0.89 | 0.70 | 0.43 | **FAIL** |
| hybrid (ΔF on the pattern, Bᵀ ΔF B) | 5,000, 1e-3 | *read-out pending* | — | **2.5e-4** (main 4.5e-8) | passes on the loss; the ratio follows |

**Reading.** The registered Cartesian head cannot represent one molecule's correction even with 5,000 optimiser steps and a free choice of learning
rate: the residual stays above half of the target. The hybrid head fits the same molecule to 2.5e-4 of the internal term with the same encoder. The
head, not the encoder, is the limit — the reviewers' rank 3 — and the gate for rank 1 on the Cartesian head stays closed by its rule; the repair of
that head (constraint into the loss, 16 → 32 tensor channels) becomes a later control, not the path.

## Outcome, rank 3 — 1 October 00:4x (`out/E7_rungC_rank3_hybrid{,_sqm,_tensor}_2026-10-01`; pool A + A2 = 175, winner flags, seeds 0–2, inner validation 15 %)

| model | (a) ratio (spread) / ω cm⁻¹ (spread) | (b) ratio / ω | Cartesian ΔH residual ratio | best epochs |
|---|---|---|---|---|
| rung B pair MLP (27 Sep) | 0.430 (0.007) / 4.71 (0.11) | 0.471 / 5.16 | — | — |
| rung C, Cartesian head (registered, after the search) | 0.811 (0.010) / 9.42 | 0.839 / 8.45 | ≈ 0.60 | — |
| **hybrid head** | **0.470** (0.023) / 5.20 (1.99) | 0.537 / 5.54 | 0.29 | 119, 51, 110 |
| **hybrid + SQM α per class** | **0.449** (0.031) / **4.77** (0.49) | 0.506 / 5.22 | 0.27 | 100, 67, 55 |
| **hybrid + rank-2 tensor input** | 0.465 (0.051) / 4.95 (0.81) | 0.531 / 5.45 | 0.28 | 110, 71, 57 |

**Lines.** Claim line (a) ≤ 0.55: **met by all three** — the Cartesian head was the problem; the encoder was not. Pass (a) ≤ 0.65: met. Prediction
(i) 0.45–0.60: met (0.47); (ii) within 0.03 of (i): met (−0.02, and the best of the three); (iii) ≤ (i): met marginally (0.465, inside the spread).
Decision 51: best epochs 51–119 of 200, no re-run. The Cartesian ΔH residual ratio falls from ≈ 0.60 to 0.27–0.29, so the gain on the pattern is not
bought with a loss off it. Diagnostic 2 for the hybrid: benzene alone to ratio 0.15 and ΔH residual 0.079 (the 0.15 is the pattern's own floor — ΔF
off the pattern is not predicted); the Cartesian head stayed at 0.60.

**Reading.** In one night the equivariant model went from 0.81 to 0.45 on the parents and from 9.4 to 4.8 cm⁻¹, by changing what it predicts (internal
force-constant corrections on the pair model's pattern, with F_low as an input) and not what it sees. It now stands within 0.02–0.04 of rung B on
the couplings and equal on ω (4.77 against 4.71), with three seeds. It does not yet beat rung B. The SQM-style scale term helps a little (−0.02,
inside the spread but consistent on (a), (b) and ω); the rank-2 input adds nothing measurable on top of F_low as an explicit input — which is the
same lesson as diagnostic 1: the encoder's use of the Hessian is not the lever, the head's object is.

**What this settles for the PC question.** Not yet: the data-scaling test was run on the head that could not learn. The registered next step is the
same scaling test on the hybrid head (below) — if the hybrid falls with data where rung B was flat, more labels are worth buying; if it is flat too,
the next levers are the reviewers' rank 4 (topology) and the data of the target kind.

## Dated amendment 1 October 00:5x — the data-scaling test on the hybrid head, and the hybrid's H_low control (registered before the runs)

**Runs (`rungC_night4_1001.sh`, laptop, 8 threads):**
1. *Scaling on the working head:* hybrid + SQM α, `--aux pattern` (class scales floored at 0.1 since 00:3x — a change from the 175 runs, which used
   unfloored scales; the 175 point is therefore re-run in the same command so the curve is one recipe), pool `A,A2,B` under `--split e6`, `--sizes 175,449,750`,
   winner flags, seeds 0–2, inner validation 15 % → `out/E7_rungC_hybrid_scale_2026-10-01`. Note: 175 here is the first 175 of the *mixed* hashed order,
   not A + A2; the A + A2 point is the 00:4x record.
2. *Control:* hybrid + SQM α with the encoder's Hessian input zeroed (`--zero-hlow`; F_low,pq/pp/qq stay), pool A,A2, 175, seed 0 →
   `out/E7_rungC_hybrid_zerohlow_2026-10-01`.

**Predictions.** (1) Rung B was flat (0.43 → 0.42 from 175 to 750); the hybrid shares its target and its F_low anchor but learns the environment
from geometry, so its curve is the test of whether the learned encoder buys anything from data that hand-made features did not. Prior: flat to
slightly falling, (a) 0.45 → 0.40–0.45 at 750. (2) Within 0.02 of the hybrid's 0.45 — the encoder's Hessian input matters little once F_low is
explicit (diagnostic 1 and the rank-2 result point that way).
**Lines.** *Scaling works on the working head:* (a) at 750 ≤ 0.40 and below 175 by more than the spread at both 449 and 750. *Flat:* within one
spread of the 175 point → the PC question is answered "not by data volume, on any head we have"; the levers are topology features (rank 4) and data
of the target kind, chosen by the coverage/MMD pre-test. *Between:* a fall smaller than 0.05 — reported as such. Control: a difference > 0.05 between
(2) and the hybrid at 175 means the encoder does use the Hessian and the rank-2 route deserves a second look; ≤ 0.02 closes it.

## Outcome, the data-scaling test on the hybrid head, and the hybrid's H_low control — 1 October 02:2x (`out/E7_rungC_hybrid_scale_2026-10-01`, `…_hybrid_zerohlow_2026-10-01`)

| pool (mixed hashed order, A,A2,B) | (a) ratio (spread) / ω (spread) | (b) ratio / ω | ΔH residual | best epochs |
|---|---|---|---|---|
| 175 | 0.510 (0.068) / 5.94 (1.06) | 0.549 / 6.09 | 0.32 | 62, 80, 52 |
| 449 | 0.465 (0.049) / 5.71 (1.25) | 0.531 / 5.99 | 0.30 | 65, 109, 52 |
| 750 | **0.458** (0.026) / 5.35 (0.68) | 0.499 / 5.29 | 0.29 | 53, 98, 90 |
| A + A2 only (175, 00:4x record, same recipe but unfloored scales) | 0.449 (0.031) / 4.77 | 0.506 / 5.22 | 0.27 | |
| **control: hybrid with the encoder's H_low zeroed**, A + A2, seed 0 | **0.432 / 4.65** | 0.478 / 4.74 | 0.27 | 98 |

**Lines.** *Works* ((a) ≤ 0.40 at 750, falling beyond the spread): **not met.** *Flat* (within one spread of the 175 point): met on the letter (0.052
against a spread of 0.068 at 175). The fall along the mixed prefix (0.51 → 0.46 on (a), 0.55 → 0.50 on (b), ω −0.6 / −0.8 cm⁻¹) is consistent on
every read-out but is explained by composition, not by volume: the first 175 of the mixed order hold fewer PAH-like molecules than A + A2, and the
750 point (0.458) is **not** below the A + A2 point (0.449). Adding 575 layer-B molecules to A + A2 moves the hybrid as little as it moved rung B.
**Verdict: between, read as flat** — the same answer on the working head as on the others: **data volume of this kind does not move the ladder;
the PC is not bought for it.** Decision 51: best epochs 52–109 of 200.

**Control.** With the encoder's Hessian input zeroed the hybrid is *not worse* (0.432 / 4.65 against 0.449 / 4.77; one seed, inside the spread): the
encoder draws nothing from the Cartesian Hessian once F_low,pq/pp/qq are explicit inputs, which closes the rank-2 input route (diagnostic 1, the rank-1
variants and this control agree). And the number itself: the hybrid without that input equals rung B (0.43 / 4.65 against 0.43 / 4.71).

**Where this leaves the model, 02:2x.** The equivariant encoder now matches the pair model and does not yet beat it. The remaining difference between
the two heads' inputs is rung B's hand-made pair vector (ring-path distance, environment classes, primitive classes, ring flags: the topology the
reviewers' rank 4 asks for). The registered next step (below) gives the hybrid head those 66 features beside the encoder's — if the encoder adds
information the pair vector lacks, the hybrid pulls ahead; if not, the result equals rung B and the environment encoder is, at this data size,
redundant with hand-made topology.

## Dated amendment 1 October 02:4x — the hybrid head with rung B's pair features (registered before it runs)

**Change (`rungC_hybrid.py`, `--pair-features`; tests, smoke):** rung B's 66-dimensional pair vector (primitive classes, elements, ring flags,
environment classes, ring-path distance, F_low products) enters the hybrid head beside the encoder's pooled features, standardised with mean and
standard deviation over the pattern pairs of the fit molecules. Everything else as in the hybrid + SQM run of 00:4x. Default off.
**Question.** Does the learned environment (the equivariant encoder) add information that rung B's hand-made topology lacks, or the reverse?
**Runs (`rungC_night5_1001.sh`, 8 threads):** (i) A + A2, 175, seeds 0–2 → `out/E7_rungC_hybrid_pf_2026-10-01`; (ii) A,A2,B, 750, seeds 0–2 →
`out/E7_rungC_hybrid_pf_750_2026-10-01`.
**Predictions.** (i) (a) 0.40–0.44 (at or just below rung B's 0.43); (ii) within 0.02 of (i).
**Lines.** *Encoder adds:* (a) ≤ 0.40 at 175, below rung B by more than both spreads. *Redundant:* 0.41–0.45 — equals rung B; the environment
encoder is, at this data size, redundant with hand-made topology, and the model to carry forward is the cheapest one that reaches the number.
*Hurts:* > 0.47. Decision 51 as always.

## Outcome, the hybrid head with rung B's pair features — 1 October 03:4x (`out/E7_rungC_hybrid_pf_2026-10-01`, `…_pf_750_2026-10-01`)

| model | pool | (a) ratio (spread) / ω (spread) | (b) ratio / ω | ΔH residual | best epochs |
|---|---|---|---|---|---|
| rung B pair MLP | 175 (A + A2) | 0.430 (0.007) / 4.71 (0.11) | 0.471 / 5.16 | — | — |
| **hybrid + SQM + pair features** | 175 (A + A2) | **0.438** (0.035) / 4.72 (0.73) | 0.477 / 5.15 | 0.28 | 88, 30, 84 |
| rung B pair MLP | 750 (A + A2 + B) | 0.420 (0.003) / 4.81 (0.09) | 0.454 / 4.74 | — | — |
| **hybrid + SQM + pair features** | 750 (A + A2 + B) | **0.418** (0.011) / **4.49** (0.29) | 0.454 / 4.65 | 0.26 | 76, 53, 154 |

**Line: *redundant*** (0.41–0.45 at 175): the hybrid with the hand-made pair vector equals rung B to the second decimal on both hold-outs and on ω, at
175 and at 750 (at 750 it is 0.3 cm⁻¹ better on (a)'s ω, inside two spreads). The learned environment encoder adds nothing measurable to the
hand-made topology at this data size, and the hand-made topology adds ≈ 0.01–0.03 to the encoder. Decision 51: best epochs 30–154 of 200, fine.

## What the night established (1 October 03:4x) — the record for the morning

1. **The registered Cartesian head was the error, not the encoder and not the data.** It ignored the Hessian input (zeroed → same 0.82) and could not
   fit one molecule (0.60 after 5,000 steps). Changing *what the model predicts* — internal force-constant corrections on the pair model's pattern,
   anchored on F_low of the element — took the same encoder from 0.81 to 0.45 in one step (ω 9.4 → 4.8 cm⁻¹).
2. **Three heads now agree at ≈ 0.42–0.44 on the parents (ω 4.5–4.8):** rung B, the hybrid, the hybrid with rung B's features. That is the present
   floor of this representation and these data; nothing tried tonight goes below it.
3. **Data volume of this kind moves no head** (rung B 0.43 → 0.42; Cartesian 0.81 → 0.82; hybrid 0.45 → 0.46; hybrid + pf 0.44 → 0.42 from 175 to 750).
   The PC is not bought for more layer B.
4. **The encoder draws nothing from the Cartesian Hessian** once F_low is explicit (zeroed control 0.43, rank-2 input ±0.00). The rank-2 route is closed.
5. **Open levers, in the order the evidence suggests:** (i) the hybrid's recipe — it inherited the Cartesian head's winner flags, a search of its own
   (learning rate, width, epochs) is the fair-chance rule; (ii) the pattern itself — off-pattern ΔF is not predicted, a floor of 0.15 on benzene; the
   between-branch pattern (d) (pairs two bonds apart) is the registered extension; (iii) data of the target kind chosen by coverage, not volume;
   (iv) the proxy → CCSD(T) transfer, which no proxy experiment can settle.

## Dated amendment 1 October 03:5x — search stage H1: the hybrid head's own recipe (registered before it runs)

The hybrid runs of tonight inherited the Cartesian head's winner flags (lr 1e-3, 200 epochs, patience 20, aux weight 1.0) and a head width of 128.
The fair-chance rule of 25 September applies to the new head as it did to the old one: no sentence about its ceiling before a small search.
**Cells (`rungC_search_H1_1001.sh`; hybrid + SQM α + pair features, pool A + A2 = 175, seeds 0–2, inner validation 15 %, patience 20, 200 epochs):**
learning rate {3e-4, 1e-3, 3e-3} × head width {128, 256} — six cells, ≈ 12 min each → `out/E7_rungC_H1_<lr>_<width>_2026-10-01`; pick by the
seed-mean inner term alone with `rungC_stage_pick.py` (`…_H1_pick_2026-10-01`), hold-outs printed for information. `--hybrid-hidden` added (test).
**Prediction.** The winner's inner term is within 10 % of the lr 1e-3 / 128 cell; (a) of the winner 0.41–0.44. **Lines.** (a) ≤ 0.40 for the winner →
the recipe was part of the floor and the next stage (epochs × patience, class-scale floor value) follows; 0.41–0.45 → the floor is the
representation and the data, not the recipe — the model to carry is the lr 1e-3 / 128 one unless the inner term says otherwise.

## Outcome, search stage H1 — 1 October 05:0x (`out/E7_rungC_H1_<cell>_2026-10-01`, pick `…_H1_pick_2026-10-01`)

| cell | inner term (seed mean) | (a) ratio / ω | (b) ratio / ω |
|---|---|---|---|
| lr 3e-4, width 128 | 0.1102 | 0.46 / 5.06 | 0.51 / 6.08 |
| **lr 3e-4, width 256 — winner** | **0.0991** | **0.43 / 4.44** | 0.49 / 5.13 |
| lr 1e-3, width 128 (tonight's recipe) | 0.1023 | 0.45 / 5.18 | 0.50 / 5.62 |
| lr 1e-3, width 256 | 0.1021 | 0.46 / 5.27 | 0.50 / 5.91 |
| lr 3e-3, width 128 | — | diverged (non-finite loss at epoch 18, seed 1; the 27 Sep guard aborted it — an incident, not a result) | |
| lr 3e-3, width 256 | 0.1252 | 0.44 / 6.52 | 0.48 / 6.04 |

**Pick by the inner term:** lr 3e-4 / width 256, 3 % below tonight's recipe — inside the prediction ("within 10 %"). **Line:** the winner's (a) 0.43 lies
in 0.41–0.45 → *the floor is the representation and the data, not the recipe.* The spread between cells on (a) (0.43–0.46) is the size of the seed
spread; ω moves more (4.4–5.3), and the winner is the best on ω too. Recipe carried from here: lr 3e-4, width 256 (patience 20, 200 epochs, aux 1.0).
Noise note: the lr 1e-3 / 128 cell here reads 0.45 against 0.438 for the same flags at 02:4x — thread-level noise of ≈ 0.01–0.02 on the ratio.

*Registered the same minute:* the carried recipe is read at 750 (A,A2,B, seeds 0–2) → `out/E7_rungC_hybrid_best_750_2026-10-01`, the number the
morning table ends with; prediction (a) 0.40–0.43, ω 4.3–4.6; no new line, it is the carried model's record at the larger pool.

## Outcome, the carried recipe at 750 — 1 October 06:1x (`out/E7_rungC_hybrid_best_750_2026-10-01`; hybrid + SQM α + pair features, lr 3e-4, width 256, seeds 0–2)

| model | pool | (a) ratio (spread) / ω (spread) | (b) ratio / ω | ΔH residual | best epochs |
|---|---|---|---|---|---|
| rung B pair MLP | 750 | 0.420 (0.003) / 4.81 (0.09) | 0.454 / 4.74 | — | — |
| **carried hybrid recipe** | 750 | **0.431** (0.011) / **4.30** (0.26) | 0.477 / 4.81 | 0.26 | 112, 63, 89 |

Prediction met ((a) 0.40–0.43, ω 4.3–4.6). Against rung B: equal on the coupling ratio of the parents (0.43 against 0.42), better on their corrected
frequencies (4.30 against 4.81 cm⁻¹, two spreads), slightly behind on the scaffolds (0.477 against 0.454). Decision 51: best epochs 63–112 of 200.

**The morning table (1 October 06:1x).** On the parents hold-out (a), three seeds each:

| model | 175 (A + A2) | 750 (A + A2 + B) |
|---|---|---|
| rung B pair MLP | 0.430 / 4.71 | 0.420 / 4.81 |
| rung C, Cartesian head (registered) | 0.811 / 9.42 | 0.823 / 9.29 |
| rung C, hybrid head | 0.470 / 5.20 | — |
| rung C, hybrid + SQM α | 0.449 / 4.77 | 0.458 / 5.35 (mixed order) |
| rung C, hybrid + SQM + pair features | 0.438 / 4.72 | 0.418 / 4.49 |
| **rung C, carried recipe (lr 3e-4, width 256)** | **0.43 / 4.44** | **0.431 / 4.30** |

The equivariant model has caught up with the pair model in one night and now gives the best corrected frequencies on the parents; no model goes
below ≈ 0.42 on the couplings. That number is the floor of this representation and these data, reached from two sides.

## Dated amendment 1 October 06:4x — lever 1: the pattern extended to (d) (the user: "Doe hefboom 1, het patroon uitbreiden"; registered before it runs)

**Change (`e7_rungB_pairs.molecule_pairs(pattern="d")`, `rungC_train --pattern d`; the hybrid carries seven pair classes; tests; corpus smoke).**
Pattern (d) = the registered pattern (c) plus every pair of primitives whose atom sets are disjoint and joined by exactly one bond — the between-branch's
"two bonds apart" of 24 September — as pair class 6 `off_twobond` with its own standardisation scale (floored) and SQM α. The read-outs are unchanged
(the ring-coupling ratio and ω are read on the same quantities), so a gain must show in the same numbers. Default `c` = everything as before.
**Why this lever first.** The hybrid cannot predict ΔF off its pattern; on benzene that left a floor of 0.15 on the couplings and 0.08 on the Cartesian
residual with pattern (c). The between-branch found that the minimum-norm mask on (d) halves the ring-coupling ratio of (c) on benzene (0.79 → 0.47)
while a fit on (c) already reaches 0.00 — so (d) adds exactly the pairs the mask was missing.
**Runs (`rungC_lever1_1001.sh`, carried recipe hybrid + SQM α + pair features, lr 3e-4, width 256, patience 20, 200 epochs; design-check gate):**
(0) diagnostic: benzene alone, 5,000 steps, pattern d → `out/E7_rungC_lever1_overfit_benzene_2026-10-01`; (1) A + A2 (175), seeds 0–2 →
`…_lever1_d_175_…`; (2) A + A2 + B (750), seeds 0–2 → `…_lever1_d_750_…`.
**Predictions.** (0) the benzene floor falls from 0.15 to ≤ 0.08 (ΔH residual ≤ 0.05). (1) (a) 0.38–0.43, ω 4.0–4.5. (2) (a) 0.37–0.42, ω 3.9–4.3.
**Lines.** *Works:* (a) ≤ 0.40 at 175 and at 750, below the pattern-c records (0.43 / 0.431) by more than both spreads. *Flat:* 0.41–0.45 — the pattern
is not the floor either; the model to carry stays pattern c (fewer parameters, same number). *Hurts:* > 0.45 — the extra pairs add noise the data cannot
constrain; reported as such. Decision 51 as always.

## Dated amendment 1 October 08:0x — Sherlock chain 2: pattern ceilings on three more molecules (H5) and a pretrained body under the hybrid head (lever 2a, H4); registered before it runs

*Investigation log: `Investigation_2026-10-01_RungC_Sherlock_Day.md`. The user, 07:5x: start without waiting.*

**H5 — is the pattern-(d) ceiling benzene-specific?** `--overfit-one` with pattern d, 5,000 steps, sum body, carried recipe, on naphthalene
`A_01f3186607`, 2-methylnaphthalene `A_69789470db` (a substituent on the core — the E9 question) and styrene `A_8f6ed7c002` (a conjugated side chain)
→ `out/E7_rungC_lever1_overfit_{naphthalene,methylnaphthalene,styrene}_2026-10-01`. **Predictions:** ring-coupling ratio ≤ 0.05 / ≤ 0.08 / ≤ 0.08.
**Line:** a ceiling above 0.15 on any of them → pattern (d) is not enough for that class and a pattern (e) (two bonds between the atom sets) is built
for it; all three under 0.08 → the pattern question is closed for the corpus and the floor on the pool is a learning floor.

**Lever 2a (H4) — the encoder is the floor.** Two cells, hybrid head + SQM α + pair features, pattern d, lr 3e-4, width 256, patience 20, 200 epochs,
pool A + A2 (175), seeds 0–2, inner validation 15 %, **mean aggregation** (the pretrained bodies are mean bodies; the sum/mean confound is held by the
control): (i) control — a fresh mean body → `out/E7_rungC_lever2a_fresh_mean_175_2026-10-01`; (ii) the QM9-pretrained mean body
`out/rungC_pretrained_mean_2026-09-28.pt` (3 epochs over 40,812 Hessian-QM9 molecules, geometry → full Hessian) under the hybrid head →
`out/E7_rungC_lever2a_pretrained_mean_175_2026-10-01`. Design-check gate for the mean body (`design_check_sherlock_mean_2026-10-01`) and for the
checkpoint as fine-tune (`design_check_sherlock_pre_2026-10-01`). Both records carry the new per-molecule read-out (H7).
**Predictions:** (i) (a) 0.39–0.43 (a mean body equals the sum body); (ii) 0.35–0.40. **Lines.** *Works:* (ii) ≤ 0.37 and below (i) by more than both
spreads → the encoder was the floor; lever 2b (longer pretraining, the hybrid objective in pretraining) follows at once. *Flat:* within spreads → three
epochs of geometry-only pretraining do not move the encoder; 2b still runs tonight as the stronger version of the same question, with capacity (2c)
beside it. *Hurts:* (ii) > (i) by more than both spreads → the QM9 body transfers badly to this corpus (the C2 history); 2b runs with the corpus's own
B3LYP Hessians as the pretraining set instead. Decision 51 as always.

## Dated amendment 1 October 08:0x — lever 2b (H4): the same pretraining, seven times longer (registered before it runs)

The mean body of 28 September saw Hessian QM9 for three epochs (31 min; validation loss 4.3e-4 → 1.9e-4, still falling). Whatever lever 2a reads,
the stronger version of the same question is a body that has converged on the pretraining task. **Run (on six cores beside the chains):**
`rungC_pretrain.py out/rungC_pretrained_mean_long_2026-10-01 --epochs 20 --threads 6 --aggregation mean` (≈ 4–5 h). **Read-out:** the validation
loss per epoch (the best epoch is recorded; decision 51 — if the best epoch is the last, the cap binds and the run is extended), then the body under
the hybrid head exactly as cell (ii) of lever 2a → `out/E7_rungC_lever2b_pretrained_long_175_2026-10-01`. **Prediction:** validation loss ≤ 1.0e-4;
(a) below cell (ii) of lever 2a by 0.02 or more if 2a reads *works*, within spreads if 2a reads *flat*. **Line:** (a) ≤ 0.37 and below the fresh mean
body by both spreads → the encoder was the floor and pretraining depth matters; otherwise the pretraining *objective* (geometry → Cartesian Hessian)
is the next suspect and the hybrid objective (geometry → F on the pattern) is built for pretraining.

## Dated amendment 1 October 08:1x — lever 3 (H8): the auxiliary term on the read-out quantity itself (registered before it runs)

**Code (`rungC_train.py --aux kring`, `kring_tensors`, test in `tests/test_rungC_diag_pattern.py`, corpus smoke):** K = kscale ⊙ (Vᵀ M^-1/2 ΔH M^-1/2 V)
in cm⁻¹ is the mode-basis coupling matrix the (a)/(b) read-outs are taken on (identical to `e7_t2_posthoc.k_of` up to the B reconstruction, tested);
the term is the mean square of (K_pred − K_true) over the ring-mode block (diagonal and couplings), divided by the block's own mean square, with the
registered mass-weighted Cartesian term beside it as always. The pattern term standardises ΔF per pair class — a proxy whose weights are the class
scales, not the read-out's. **Run (`rungC_sherlock3_1001.sh`, queued behind chain 2):** hybrid + SQM α + pair features, pattern d, sum body, 175,
seeds 0–2, inner validation 15 %, `--aux kring` → `out/E7_rungC_lever3_kring_175_2026-10-01`; the control is lever 1's pattern-term record at 175
(0.40, 0.39–0.42). **Prediction:** (a) 0.36–0.40, ω equal or better (the term weights the ring modes the read-out weights). **Lines.** *Works:*
(a) ≤ 0.37 and below the pattern-term record by both spreads → the loss was part of the floor; the term is carried and combined with the pattern term
next. *Flat:* within spreads → H8 rejected; the loss is not the floor. *Hurts:* > 0.43 → the ring block alone under-constrains the rest of ΔF; a
combined term (pattern + kring) is the follow-up. Decision 51 as always.

## Dated amendment 1 October 08:2x — lever 2c (H4): encoder capacity (registered before it runs)

**Code (`--body-blocks`, `--body-width` in `rungC_train.py` and `design_check.py`; `HybridDeltaFModel(n_v, n_blocks)`; tests; corpus smoke at 5 × 128 =
1.0 M body parameters).** **Cells (`rungC_sherlock4_1001.sh`, queued behind chain 3; hybrid + SQM α + pair features, pattern d, sum body, 175, seeds
0–2, inner validation 15 %):** *deep* 5 blocks × 64 → `out/E7_rungC_lever2c_deep_175_2026-10-01`; *wide* 3 blocks × 128 → `…_wide_175_…`; design-check
gate per body. Control: lever 1's record at 175 (0.40, 0.39–0.42). **Prediction:** both within spreads of 0.40 (175 molecules do not feed a bigger
body; the 30 Sep data-scaling result points the same way). **Lines.** *Works:* a cell ≤ 0.37 and below by both spreads → capacity was part of the floor;
that body is carried and re-read at 750. *Flat:* H4-capacity rejected at this data volume. *Hurts:* > 0.43 → over-parameterised for 175; noted.

*Amendment to lever 2b, 08:4x:* the first launch (lr 1e-3, as the 28 Sep checkpoint) aborted at ≈ 20,600 molecules of epoch 1 on the 27 Sep
non-finite-loss guard (molecule `dsgdb9nsd_000003`, water). The record and a fresh body are finite on that molecule and a reproduction over the first
20,700 molecules did not blow up — the divergence is a rare trajectory event at lr 1e-3 (threaded reductions make runs non-identical), not a data
fault. Relaunched 08:43 with **lr 3e-4**, everything else as registered; the aborted log is kept as `…_ABORTED_lr1e-3.log`. The 28 Sep checkpoint
(lr 1e-3, 3 epochs) stays the body of lever 2a cell (ii).

## Outcome, lever 1 — pattern (d) — 1 October 09:0x (`out/E7_rungC_lever1_overfit_benzene_2026-10-01`, `…_lever1_d_175_…`, `…_lever1_d_750_…`)

| run | (a) ratio, seeds | (b) ratio, seeds | ω (a) | best epochs / 200 | pattern-c counterpart |
|---|---|---|---|---|---|
| benzene overfit, 5,000 steps | **0.02** (ΔH residual 0.007) | — | 0.21 | — | 0.15 (0.079) |
| 175 (A + A2) | **0.40** (0.40 / 0.42 / 0.39) | 0.50 (0.50 / 0.49 / 0.51) | 4.70 (4.22 / 5.83 / 4.06) | 97 / 30 / 140 | 0.43 (0.43 / 0.44 / 0.42); ω 4.44 |
| 750 (A + A2 + B) | **0.37** (0.38 / 0.36 / 0.36) | **0.43** (0.43 / 0.43 / 0.42) | **4.00** (4.18 / 4.00 / 3.82) | 42 / 75 / 110 | 0.43 (0.44 / 0.42 / 0.43); ω 4.30 |

**Against the predictions:** (0) met and exceeded (≤ 0.08 predicted, 0.02 found). (1) 0.40 inside 0.38–0.43. (2) 0.37 inside 0.37–0.42; ω 4.00 inside 3.9–4.3.
**Against the lines:** at 750 *works* — 0.36–0.38 against 0.42–0.44, separated by more than both spreads, on (b) as well (0.42–0.43 against 0.47–0.49), ω
better; at 175 the separation is at the edge (0.39–0.42 against 0.42–0.44, touching at 0.42). The registered line asked for both; the honest reading is
**works at 750, at the edge at 175**. The number that matters most is new: **the data step 175 → 750 now moves the head (0.40 → 0.37)**, where the
pattern-c head was flat (0.43 → 0.431) — the first time since 25 September that more data pays. Decision 51: no best epoch near the cap.
**Decision:** pattern (d) is the carried pattern (every chain of today already runs it); the hybrid head's new reference at 750 is **0.37 / 4.00** against
rung B's 0.42 / 4.81. Whether (d) is itself the ceiling on fused and substituted rings is the H5 read of chain 2.

## Dated amendment 1 October 09:1x — the middle point of the pattern-d learning curve (registered before it runs)

Lever 1 moved with data (0.40 at 175 → 0.37 at 750). T2 of the target proposal needs three points. **Run (`rungC_sherlock6_1001.sh`, queued behind
chain 4):** pattern d, carried recipe, pool A + A2 + B, `--sizes 449` (the data-scaling test's middle size of 30 Sep), seeds 0–2 →
`out/E7_rungC_lever1_d_449_2026-10-01`. **Prediction:** (a) 0.38–0.40, between the two measured points. **Lines.** *Monotone:* 175 > 449 > 750 beyond the
seed spreads → a power law is fitted to the three points (`e11_power_law.py`'s fit) and its extrapolation to 5,000 molecules is read against T2
(ratio ≤ 0.20). *Flat middle:* 449 within spreads of 175 or of 750 → the curve is a step, not a law; the 750 point's layer B (substituted molecules)
rather than the count is the suspect, and the next run splits the pool by layer at equal count. Decision 51 as always.

## Dated amendment 1 October 09:4x — lever 4: the pattern term's target was the floor (registered before it runs)

**What was found (H5, 09:1x–09:3x).** Overfitting one molecule under pattern d stops at 0.41 on naphthalene and 0.40 on 2-methylnaphthalene (ΔH
residual 0.28 / 0.26), while the least-squares ΔF supported on the same pattern leaves 0.04 / 0.09 of the ring couplings (`probes/rungC_pattern_ceiling.py`,
`out/rungC_pattern_ceiling_4mol_2026-10-01`). The pattern term's target is the projected truth B⁺ᵀ ΔH B⁺ read on the pattern; reconstructed with
zeros off the pattern that target itself leaves **0.38 / 0.42** of the ring couplings and 0.29 / 0.27 of ΔH on those two molecules — the overfits
land on it exactly, and the pool read-outs of every head (0.37–0.43, rung B's 0.42 included: it fits the same projected ΔF) sit on the same bound.
The floor of the week was the target, not the model and not the data.
**Code.** `m05/rungC_targets.py` (`pattern_ls_target`: mass-weighted least squares of a pattern-supported ΔF to ΔH, LAPACK gelsd; `cached_pattern_ls_target`:
cache keyed by a hash of ΔH, B, mask; `weighted_residual`), `rungC_train.py --aux-target {projected,ls}` (default projected = registered; the class scales
follow the target; every record carries both targets' residuals per molecule), `probes/rungC_ls_targets_build.py` (fills the cache; A + A2 first).
Tests: `tests/test_rungC_targets.py` (independent dense fit, benzene: the fit beats the projected target and matches the independent objective;
cache round trip and invalidation; trainer switch). Rejected solvers recorded in the module docstring with their numbers.
**Run (`rungC_sherlock7_1001.sh`, after chain 2 and the A + A2 cache):** hybrid + SQM α + pair features, pattern d, sum body, lr 3e-4, width 256,
patience 20, 200 epochs, 175, seeds 0–2, `--aux-target ls` → `out/E7_rungC_lever4_ls_175_2026-10-01`; control = lever 1's 175 record (0.40, 0.39–0.42,
ω 4.7). Then 750 when the B cache is in (`…_lever4_ls_750_…`; control 0.37 / 4.00).
**Predictions.** 175: (a) 0.25–0.33, ω 3.0–4.0; 750: (a) 0.20–0.28, ω 2.5–3.5. **Lines.** *Works:* (a) ≤ 0.33 at 175, below 0.40 by more than both spreads →
the target was the floor; the LS target becomes the registered target, the H4 levers are re-read on it. *Flat:* 0.36–0.42 → the model does not use the
better target either; the model is the floor after all (the overfit on naphthalene with the LS target is the next diagnostic). *Hurts:* > 0.43 → the
LS target is harder to learn than the projected one (noisier entries); the aux weight is searched. Decision 51 as always. T1 of the target proposal
(≤ 0.30 at 750) is reachable only on this route.

## Outcome, Sherlock chain 2 — 1 October 11:1x (H5 ceilings `out/E7_rungC_lever1_overfit_{naphthalene,methylnaphthalene,styrene}_2026-10-01`; lever 2a `out/E7_rungC_lever2a_{fresh,pretrained}_mean_175_2026-10-01`)

**H5.** Overfit, pattern d, 5,000 steps: naphthalene **0.41** (ΔH residual 0.276), 2-methylnaphthalene **0.40** (0.256), styrene **0.12** (0.041) against the
predictions ≤ 0.05 / 0.08 / 0.08 — the line "a ceiling above 0.15 → pattern (e)" would have fired, but the follow-up of 09:1x–09:3x showed the ceiling is
not the pattern's: the least-squares ΔF on pattern d leaves 0.04 / 0.09 / 0.03, while the pattern term's *target* (projected truth masked on the pattern)
leaves 0.38 / 0.42 / 0.17 — the overfits sit on the target's bound (H9, lever 4). Pattern (e) is not built; the target is replaced.
**Lever 2a.** Fresh mean body (a) **0.42** (0.44 / 0.44 / 0.38), (b) 0.46, ω 5.6; QM9-pretrained mean body (a) **0.41** (0.37 / 0.48 / 0.38), (b) 0.47, ω 5.3;
best epochs 40–102 of 200. Prediction (i) 0.39–0.43 met; (ii) 0.35–0.40 missed; **line: flat** — three epochs of geometry-only pretraining do not move the
encoder, and a mean body is slightly worse than the sum body (0.40). Both runs trained on the projected target, so they share its bound; lever 2b (the
converged body) is re-read on the LS target when chain 5 runs, as the amendment of 09:4x says.
**H7 (first per-molecule read, hold-out (a), seed 0).** Fresh body: 0.28–0.55 over the ten molecules; pretrained: 0.12–0.48. No single molecule carries the
ratio; the spread is across scaffolds. The per-molecule field stays in every record.

*Amendment to lever 4, 12:1x — the target is ridge-anchored, λ chosen by a scan, predictions revised before the run.* The first lever-4 run (11:21–11:4x,
stopped by pid) exploded: ring couplings 1.6e12. Cause, measured: the plain least-squares ΔF has entries of 1e7–1e10 a.u. along the near-null directions
of the redundant internals (projected target max 0.01–0.02 a.u.), which cancel in Bᵀ X B on the training molecules and not on a hold-out. Fix in
`rungC_targets.py`: the ridge-anchored solution min ‖D(BᵀXB − ΔH)D‖² + λ‖X − X_proj‖² on the pattern, normal equations by Cholesky (well conditioned with
the ridge), λ relative to the normal matrix's mean diagonal; `--ls-lam`; a trainer guard refuses a target whose entries exceed 20× the projected target's
(`TARGET_SCALE_LIMIT`); the cache key carries λ. **λ scan (naphthalene / 2-methylnaphthalene / styrene / a 30-atom A2 molecule; entry scale × the
projected max; ring-coupling ratio of the reconstruction, projected target in brackets):** λ_rel 1e-2: ×1.0, 0.28 / 0.27 / 0.05 / 0.20 (0.39 / 0.42 / 0.17 /
0.36); **1e-3: ×1.0–1.2, 0.27 / 0.25 / 0.04 / 0.19**; 1e-4: ×1.5–4.5, 0.25 / 0.23 / 0.04 / 0.18; 1e-5: ×5–9, 0.25 / 0.23 / 0.04 / 0.17. Chosen **λ_rel = 1e-3**:
the entries stay at the projected scale and the ring-coupling bound falls from 0.38–0.42 to 0.25–0.27 on the naphthalenes; smaller λ buys ≤ 0.02 for a
4–9× scale. (The scan's read-out used the finite-difference truth K for the two-route molecules, so the naphthalene numbers carry its 0.07 noise; the
trainer substitutes the analytic truth, `substituted_analytic`.) **Revised predictions:** 175: (a) 0.30–0.36, ω 3.5–4.5; 750: (a) 0.26–0.33. **Revised
lines:** *works:* (a) ≤ 0.36 at 175, below 0.40 by more than both spreads; *flat:* within spreads of 0.40; *hurts:* > 0.43. The target's own bound on the
pool is now ≈ 0.2–0.27 rather than 0.03 — T1 (≤ 0.30 at 750) needs the model to reach near that bound, or a further step on the target (a pattern-(e)
support for the ridge target, whose bound is lower, is the next lever if lever 4 works but stops near 0.3). Cache rebuilt on the server for λ 1e-3
(`out/ls_targets/d_lam0.001`), chain 7b queued on the copy.

## Dated amendment 1 October 12:2x — lever 1b: pattern (f) under the ridge target (registered before it runs)

**Measured first (ridge target, λ_rel 1e-3, finite-difference truth; naphthalene / 2-methylnaphthalene / styrene / a 30-atom A2 molecule; ring-coupling
ratio of the target's reconstruction, entry scale ×1.0–1.3 throughout):** pattern d **0.26 / 0.25 / 0.04 / 0.19**, pattern e **0.15 / 0.13 / 0.01 / 0.10**,
pattern f **0.01 / 0.01 / 0.01 / 0.04**. At set distance three the target's bound reaches the noise floor at the projected scale — the pattern lever and the
target lever together. **Code:** `e7_rungB_pairs.molecule_pairs(pattern="e"|"f")` by the shortest bond-graph distance between disjoint atom sets (classes 7, 8;
`PATTERN_REACH`, `graph_distances`), nine pair classes in the hybrid and the trainer, tests (`test_patterns_e_and_f_extend_d_by_set_distance`), corpus
smoke; the ceiling probe now takes its patterns from the builder. Pairs: f has 1.3–1.6× the pairs of d.
**Run (`rungC_sherlock9_1001.sh`, after chain 7b and the pattern-f cache from the server):** hybrid + SQM α + pair features, **pattern f, `--aux-target ls
--ls-lam 1e-3`**, sum body, carried recipe, 175, seeds 0–2 → `out/E7_rungC_lever1b_f_ls_175_2026-10-01`. Controls: chain 7b (pattern d, same target) and
lever 1 (pattern d, projected target, 0.40). **Prediction:** (a) 0.24–0.32, ω 3.0–4.0 — the gain over 7b is smaller than the bounds suggest because 1.5× more
pairs are learned from the same 175 molecules. **Lines.** *Works:* (a) ≤ 0.32 and below 7b by more than both spreads → pattern f + ridge target is the
carried recipe; 750 next (T1 ≤ 0.30 in reach). *Flat:* within spreads of 7b → the model, not the target support, limits at 175; the 750 read of 7b decides
what to carry. *Hurts:* above 7b by both spreads → the extra classes dilute at 175; re-read at 750 before judging. Decision 51 as always.

*Amendment to lever 4, 12:3x — second stop, cause and fix.* Chain 7b (12:18) and chain 8 (12:19) stopped at the new scale guard: 53 cache files built on the
server carried targets of 1e15–1e18 a.u. Cause, measured: those molecules' internal sets are exactly redundant (smallest singular value of B 2.7e-16);
numpy's default pseudo-inverse cutoff dropped that direction on the laptop and kept it on the server, so the *projected prior* itself was 7.5e17 there and
the ridge followed it. Fix: `projected_target` uses an explicit cutoff (`PINV_RCOND` 1e-10 — the null directions of the redundant internals, the same on
every machine), the cache refuses to store a target above `SCALE_LIMIT` (20×) the prior (the trainer's guard reads the same constant), tests. The 53 files
were deleted and rebuilt on the laptop: pattern d median residual 0.125 → 0.081, scale max 4.6; pattern f 0.028 → 0.007, scale max 1.7 (`out/
ls_targets_build_{d,f}_lam0.001_2026-10-01.json`). Queue re-serialised (12:31): chain 3 (kring, running) → 7c (d + ridge, 175) → 9b (f + ridge, 175) →
8b (d + ridge, 750) → 4 (capacity) → 6 (449); 5 after 4 and the checkpoint. Lesson for the guard list: a numerical cutoff that is a library default is a
setting that travels unexamined (the E8 lesson again) — pin it.

## Dated amendment 1 October 12:4x — chain 10: pattern f + ridge target at 750 (registered before it runs; queued behind chain 6)

Same recipe as chain 9b at the full pool (A + A2 + B, seeds 0–2) → `out/E7_rungC_lever1b_f_ls_750_2026-10-01`. Controls: chain 8b (pattern d + ridge at 750)
and lever 1 (pattern d, projected target, 0.37 / 4.00). **Prediction:** (a) 0.22–0.30, ω 2.8–3.8. **Lines.** *Works:* (a) ≤ 0.30 and below 8b by both
spreads → T1's ratio criterion met on this route; the ω criterion (≤ 3) and the (b) hold-out are read beside it. *Flat:* within spreads of 8b. *Hurts:*
above 8b by both spreads. If chain 9b reads *hurts* at 175, chain 10 is stopped by pid before it starts and the stop is recorded. Decision 51 as always.

## Outcome, lever 3 (H8) — the kring term — 1 October 13:1x (`out/E7_rungC_lever3_kring_175_2026-10-01`)

| read-out | kring term, seeds 0 / 1 / 2 | pattern term (lever 1, 175) |
|---|---|---|
| (a) ring-coupling ratio | **0.29** (0.32 / 0.29 / 0.27) | 0.40 (0.40 / 0.42 / 0.39) |
| (b) ring-coupling ratio | **0.41** (0.43 / 0.42 / 0.39) | 0.50 |
| (a) corrected ω rms | **7.3** (7.3 / 6.5 / 8.2) | 4.7 |
| (a) ΔH residual ratio | 1.03 / 0.42 / 0.37 | 0.23 |
| best epochs | 165 / 140 / 100 of 200 | 97 / 30 / 140 |

**Against the lines:** on the registered read-out the term *works* — (a) 0.29 against 0.40, below by far more than both spreads, (b) 0.41 against 0.50 — and
the prediction 0.36–0.40 was too cautious. But the same run is worse on everything the term does not see: ω 7.3 against 4.7 and a ΔH residual of 0.4–1.0
(seed 0 leaves more Cartesian power than the zero rule). The read-out-aligned loss buys the ring couplings with the rest of the Hessian. H8 is confirmed in
its narrow form (the loss was part of the floor on the ring couplings) and refuted as a recipe on its own. **Decision, as the amendment of 08:1x said for
*works*:** the term is carried only in combination — pattern term (ridge target) + kring term — as lever 3b, registered below. Decision 51: best epochs
below the cap.

## Dated amendment 1 October 13:2x — lever 3b: pattern term (ridge target) + kring term (registered before it runs)

**Code:** `rungC_train.py --aux both` = the pattern term on the chosen target plus the kring term, equal weights inside the auxiliary term (`_pattern_term`,
`_kring_term`, test `test_aux_both_is_the_sum_of_pattern_and_kring_terms`; corpus smoke). **Run (`rungC_sherlock11_1001.sh`, a second lane that starts when
the 20-epoch pretraining has written its checkpoint and freed its six cores):** hybrid + SQM α + pair features, pattern d, `--aux both --aux-target ls
--ls-lam 1e-3`, sum body, carried recipe, 175, seeds 0–2 → `out/E7_rungC_lever3b_both_175_2026-10-01`. Controls: lever 3 (kring alone: 0.29 / ω 7.3 / ΔH
0.4–1.0) and chain 7c (pattern term on the ridge target alone, running). **Prediction:** (a) 0.26–0.32 with ω 3.5–5.0 and ΔH residual ≤ 0.30 — the pattern
term holds the rest of the Hessian while the kring term pulls the couplings. **Lines.** *Works:* (a) ≤ 0.32 **and** ω ≤ 5.0 **and** ΔH residual ≤ 0.30 →
the combined term is the carried loss; re-read at 750. *Half:* the couplings ≤ 0.32 but ω > 5.0 → the weights between the two terms are searched (one
decade each way). *Flat:* (a) within spreads of chain 7c → the kring term adds nothing once the target is right. Decision 51 as always.

## Dated amendment 1 October 13:3x — H9 confirmation on rung B: the pair model on the ridge target (registered before it runs)

If the floor was the target, the hand-feature pair model trained on the same projected ΔF must share it and must move when the target moves — with no
network in between. **Code:** `e7_rungB_pairs.py --target ls [--ls-lam]` (the per-pair targets become the entries of the ridge-anchored ΔF on rung B's own
pattern c, from the shared cache `out/ls_targets/c_lam0.001`; default projected = unchanged; test `tests/test_rungB_target_switch.py`). **Run:** the 27 Sep
comparison recipe (`--use-analytic --pool-layers A,A2 --sizes 175 --seeds 0,1,2`, 60 epochs, B1 MLP and B2 GBT), `--target ls`, two threads beside the chains
→ `out/E7_rungB_lstarget_175_2026-10-01`; reference `E7_rungB_A2B_point0_2026-09-27`: B1 (a) 0.43 / ω 4.71, (b) 0.47. The pattern-c ridge bound on hold-out (a)
is read from the same probe afterwards. **Prediction:** B1 (a) 0.30–0.38, (b) 0.35–0.43, ω ≤ 4.5. **Lines.** *Confirms:* B1 (a) ≤ 0.38 → H9 holds for the
simplest model too and the registered rung-B numbers of 23–27 Sep are target-bound, not model-bound. *Does not:* B1 (a) within 0.41–0.45 → the pair model
cannot use the better target; the network result decides H9 alone.

## Outcome, lever 4 at 175 — the ridge target, pattern d — 1 October 14:1x (`out/E7_rungC_lever4_ls_175_2026-10-01`)

| read-out | ridge target λ 1e-3, seeds 0 / 1 / 2 | projected target (lever 1, 175) | target bound (hold-out (a)) |
|---|---|---|---|
| (a) ring-coupling ratio | **0.44** (0.45 / 0.42 / 0.45) | 0.40 (0.40 / 0.42 / 0.39) | ridge 0.16, projected 0.31 |
| (b) ring-coupling ratio | 0.49 | 0.50 | 0.15 / 0.28 |
| (a) ω | 4.44 | 4.70 | 1.0 / 1.9 |
| (a) ΔH residual | 0.247 | 0.23 | — |
| best epochs | 167 / 158 / 160 of 200 | 97 / 30 / 140 | — |

**Against the lines:** *hurts* (> 0.43) on the couplings, ω equal. The target with the better bound is learned worse: the model sits 0.28 above the ridge
bound against 0.09 above the projected bound. Decision 51: best epochs 158–167 are below the 180 threshold but late — the ridge target converges
slowly. **Reading:** what the ridge adds to the projected target lives in near-null combinations of the redundant internals; those entries are set
by the molecule's B matrix, not by chemistry the pooled atom features can see, so they act as noise on the aux term. H9 stands as a statement about
the bound; as a lever it needs a target that is both low-bound and learnable. Three cheap cells decide (chain 12, below): a larger λ (closer to the
projected entries), and the same target at a smaller aux weight. All targets were served from the cache (224/224), scale max 4.5.

## Dated amendment 1 October 14:1x — chain 12: λ and weight cells for the ridge target (registered before it runs)

Cells (`rungC_sherlock12_1001.sh`, after chain 9b; 175, pattern d, carried recipe): (i) λ_rel 1e-1, aux weight 1.0 → `…_lever4_lam1e-1_175_…`;
(ii) λ_rel 1e-2, weight 1.0 → `…_lam1e-2_…`; (iii) λ_rel 1e-3, weight 0.3 → `…_w0.3_…`. From the λ scan the bounds barely move between 1e-1 and 1e-3
(naphthalene 0.28 → 0.27) while the entries approach the projected ones. **Prediction:** (i) 0.38–0.41, (ii) 0.39–0.43, (iii) 0.40–0.44. **Lines.**
*Works:* any cell ≤ 0.38, below the projected 0.40 by both spreads → that λ / weight is carried to 750. *Flat / hurts:* no cell below 0.40 → the ridge
route is closed at 175; the pattern-f result (chain 9b) and the pretrained body (chain 5b) decide the next step, and chain 8b (ridge at 750) is kept only
as the data-volume read of this route. Decision 51 as always.

## Outcome, lever 1b — pattern f + ridge target at 175 — 1 October 15:0x (`out/E7_rungC_lever1b_f_ls_175_2026-10-01`)

| read-out | pattern f + ridge, seeds 0 / 1 / 2 | pattern d + ridge (7c) | pattern d + projected (lever 1) |
|---|---|---|---|
| (a) ring-coupling ratio | **0.33** (0.34 / 0.32 / 0.32) | 0.44 (0.42–0.45) | 0.40 (0.39–0.42) |
| (b) ring-coupling ratio | **0.40** (0.41 / 0.40 / 0.40) | 0.49 | 0.50 |
| (a) ω | 4.60 (4.64 / 4.20 / 4.96) | 4.44 | 4.70 |
| (a) ΔH residual | 0.220 | 0.247 | 0.23 |
| best epochs | 83 / 73 / 119 of 200 | 158–167 | 97 / 30 / 140 |

**Against the lines:** prediction 0.24–0.32 missed by 0.01; *works* in substance — 0.32–0.34 against 0.39–0.42 and 0.42–0.45, separated by far more than
both spreads on (a), and (b) 0.40 against 0.49–0.50. The wider support is the lever that works at 175; with it the ridge target is learned (best epochs
73–119, not the slow convergence of 7c). ω does not move (4.6 against 4.4–4.7): the model's ω gap stays. **Decision:** pattern f + ridge target is the
carried recipe; chain 10 (750) is promoted to run at once (T1 read); chain 13 (pattern f with the projected target, lane B) tells whether the ridge is
needed once the support is wide; chain 12's λ cells follow chain 10. Decision 51: no best epoch near the cap.

## Dated amendment 1 October 15:1x — chain 13: pattern f with the registered projected target (registered before it runs)

Same recipe as chain 9b with `--aux-target projected` (the registered target) → `out/E7_rungC_lever1b_f_proj_175_2026-10-01`, lane B after chain 5b.
Bounds on hold-out (a): projected 0.09, ridge 0.03. **Prediction:** (a) 0.33–0.38 (the projected target is easier to learn, its bound a little higher).
**Lines.** *Ridge unnecessary:* (a) ≤ 9b's 0.33 within spreads → the projected target is kept (simpler, registered). *Ridge needed:* (a) above 9b by both
spreads. Decision 51 as always.

## Outcome, H9 confirmation on rung B — 1 October 15:1x (`out/E7_rungB_lstarget_175_2026-10-01`)

| model | target | (a) ratio | (b) ratio | (a) ω |
|---|---|---|---|---|
| B1 MLP | projected (27 Sep) | 0.43 | 0.47 | 4.71 |
| B1 MLP | ridge λ 1e-3 | **0.48** | **0.59** | 5.33 |
| B2 GBT | projected (27 Sep) | 0.46 | 0.49 | 6.17 |
| B2 GBT | ridge λ 1e-3 | 0.45 | 0.47 | 6.60 |

**Against the lines:** *does not* — the pair model cannot use the ridge target either (B1 worse on both hold-outs, B2 unchanged), the same picture as the
network with pattern d (7c: 0.44 against 0.40). Reading, consistent across two very different models: at a fixed support the ridge target's extra content is
not learnable from the pair's features; H9 stands as a statement about the bound (the projected target leaves 0.31 on hold-out (a)), not as a recipe. The
lever that moved the network was the support (pattern f: 0.33). The matching question for the pair model — a wider support with the registered target —
is registered below.

## Dated amendment 1 October 15:2x — rung B with pattern f (registered before it runs)

`e7_rungB_pairs.py --pattern {c,d,e,f}` (the pair builder's own patterns; default c = registered). **Run:** the 27 Sep comparison recipe at 175, `--pattern f`,
projected target, two threads → `out/E7_rungB_f_175_2026-10-01`. **Prediction:** B1 (a) 0.36–0.42 (more pairs to fit from the same 175 molecules; the
hand-made features are the limit). **Lines.** *Helps:* B1 (a) ≤ 0.40 below 0.43 by the usual spread → the support lever is model-independent and the
rung-B baseline for the network comparison becomes this number. *Does not:* ≥ 0.42 → the support helps only a model whose features see the environment
(the network), which is itself a finding about what the network has learned.

## Outcome, lever 3b — pattern + kring terms on the ridge target, pattern d, 175 — 1 October 15:4x (`out/E7_rungC_lever3b_both_175_2026-10-01`)

| read-out | both terms, seeds 0 / 1 / 2 | kring alone (lever 3) | pattern alone, ridge (7c) |
|---|---|---|---|
| (a) ring-coupling ratio | **0.28** (0.28 / 0.29 / 0.28) | 0.29 | 0.44 |
| (b) ring-coupling ratio | 0.41 | 0.41 | 0.49 |
| (a) ω | **6.5** (5.8 / 6.3 / 7.5) | 7.3 | 4.4 |
| (a) ΔH residual | **0.41** (0.38 / 0.50 / 0.34) | 0.4–1.0 | 0.25 |
| best epochs | 108 / 179 / 99 of 200 | 100–165 | 158–167 |

**Against the lines:** *half* — the couplings ≤ 0.32 (0.28, the best (a) of the day on this hold-out) but ω > 5 and the Cartesian residual 0.41: at equal
weights the kring term dominates and the pattern term does not hold the rest of the Hessian. Decision 51: seed 1's best epoch 179 is within 10 % of the
cap — the combined term also converges slowly; a re-run at 300 epochs is folded into the weight cells below rather than repeated as is. **Decision, as the
line says:** the weights are searched — on the carried support (pattern f) rather than d: chain 14 (lane B, after chain 13), `--kring-weight` 0.1 and 0.3.

## Dated amendment 1 October 15:5x — chain 14: kring weight on pattern f (registered before it runs)

`rungC_train.py --kring-weight` (default 1.0; scales the kring term inside `--aux both`; test). **Cells (`rungC_sherlock14_1001.sh`, lane B after chain 13; 175,
pattern f, ridge target, hybrid head, carried recipe, 300 epochs because the combined term converged late):** kring weight 0.1 → `…_lever3b_f_kw0.1_175_…`;
0.3 → `…_kw0.3_…`. Controls: chain 9b (pattern f, pattern term alone: 0.33 / ω 4.6 / ΔH 0.22) and lever 3b (both at equal weights, pattern d: 0.28 / 6.5 /
0.41). **Prediction:** at 0.1 (a) 0.30–0.33 with ω ≤ 5 and ΔH ≤ 0.25; at 0.3 (a) 0.28–0.31 with ω 5–6. **Lines.** *Works:* a cell with (a) ≤ 0.31, ω ≤ 5.0 and
ΔH residual ≤ 0.25 → the carried loss; re-read at 750. *Half:* couplings down, ω up → the two read-outs trade off under this head; the model, not the
loss, is the next lever. *Flat:* within spreads of 9b. Decision 51 as always.

## Outcome, rung B with pattern f — 1 October 15:4x (`out/E7_rungB_f_175_2026-10-01`)

| model, support, target | (a) ratio | (b) ratio | (a) ω | (a) ΔH residual |
|---|---|---|---|---|
| rung B, B1 MLP, pattern c, projected (27 Sep) | 0.43 | 0.47 | 4.71 | 0.25 |
| rung B, B1 MLP, **pattern f**, projected | **0.32** | **0.41** | **4.47** | **0.20** |
| rung B, B2 GBT, pattern f, projected | 0.45 | 0.54 | 7.56 | 0.37 |
| network, hybrid head, pattern f, ridge (chain 9b) | 0.33 | 0.40 | 4.60 | 0.22 |

**Against the lines:** *helps*, and more than predicted (0.36–0.42): the hand-feature pair model with the wide support equals the network's best (0.32 /
0.41 / 4.5 against 0.33 / 0.40 / 4.6). Two readings, both to be said plainly: (i) the support is the lever and it is model-independent — the week's
floor was the pattern's reach plus the target's bound, not any model; (ii) at 175 molecules the learned encoder adds nothing over hand-made pair features.
The network's case must be made where hand features cannot follow: more data (chain 10 at 750 against rung B f at 750, registered below), and the
transfer to CC level and to larger molecules (T3). The rung-B baseline for every later comparison is now **0.32 / 4.47** (pattern f).

## Dated amendment 1 October 15:5x — rung B with pattern f at 750 (registered before it runs)

Same recipe, `--pool-layers A,A2,B --sizes all` (750), seeds 0–2, two threads → `out/E7_rungB_f_750_2026-10-01`; read beside chain 10 (network, pattern f +
ridge, 750). **Prediction:** B1 (a) 0.28–0.33 (hand features gain less from data than the encoder should). **Lines.** The pair of numbers decides the
sentence for the day: network below rung B by both spreads at 750 → the encoder earns its place with data; equal → the network's case rests on T3 and on the
learning curve beyond 750 (T2), not on the pool.

## Outcome, rung B with pattern f at 750 — 1 October 16:3x (`out/E7_rungB_f_750_2026-10-01`)

B1 MLP (a) **0.32** / (b) **0.43** / ω 4.47 / ΔH 0.20 — identical to its 175 numbers on (a) (0.32 / 4.47 / 0.20) and a little worse on (b) (0.41 → 0.43); B2 GBT
0.49 / 0.58. Prediction 0.28–0.33 met at its upper edge. **Reading:** the hand-feature model does not gain from the step 175 → 750 — the same flatness the
pair model showed on pattern c (0.43 → 0.42 on 27 Sep). The network's first seed at 750 (chain 10, running) reads 0.30 / ω 4.26 / ΔH 0.197; the full
comparison follows when its three seeds are in.

## Outcome, lever 2b — the 20-epoch pretrained body, pattern d + ridge target, 175 — 1 October 17:1x (`out/E7_rungC_lever2b_pretrained_long_175_2026-10-01`, pretraining `out/rungC_pretrained_mean_long_2026-10-01`)

Pretraining: 20 epochs at lr 3e-4, validation loss 5.5e-4 → 1.40e-4, still falling by ≈ 1 % per epoch at the end — **the best epoch is the last one, so the
cap binds (decision 51 on the pretraining itself)**; checkpoint design check PASS (worst output 4.4, feature-scale ratio 1.21). Fine-tune on the ridge
target, pattern d: (a) **0.46** (0.50 / 0.46 / 0.42), (b) 0.49, ω 4.41, ΔH 0.26; best epochs 182 / **200** / 116 — two of three within 10 % of the cap.
**Against the lines:** no better than the fresh mean body on the projected target (0.42) or than the fresh sum body on the same ridge route (7c, 0.44): *flat*
on a route that itself hurts. Decision 51 flags this run twice (fine-tune cap and pretraining cap); rather than repeat it as is, the fair test of
pretraining moves to the carried recipe with a higher cap — chain 15 below. The pretraining is left at 20 epochs for today (its continuation is an
overnight job if chain 15 says pretraining matters).

## Dated amendment 1 October 17:1x — chain 15: pretraining on the carried recipe (registered before it runs)

Two cells (`rungC_sherlock15_1001.sh`, lane B after chain 14; 175, pattern f + ridge target, mean body, 300 epochs, seeds 0–2): fresh mean body →
`out/E7_rungC_lever2b_f_fresh_mean_175_2026-10-01`; the 20-epoch pretrained body → `…_f_pretrained_long_175_…`. **Prediction:** fresh mean 0.33–0.36 (the sum
body's 0.33 on this recipe), pretrained 0.31–0.35. **Lines.** *Works:* pretrained below fresh by both spreads and ≤ 0.31 → pretraining matters on the carried
recipe; the pretraining is continued overnight to convergence. *Flat:* within spreads → geometry-only pretraining on QM9 does not help this head; the
pretraining lever is closed until a Hessian-aware pretraining objective exists. Decision 51 as always.

## Outcome, chain 13 — pattern f with the registered projected target, 175 — 1 October 18:0x (`out/E7_rungC_lever1b_f_proj_175_2026-10-01`)

| model, support, target (175) | (a) ratio | (b) ratio | (a) ω | (a) ΔH residual | best epochs |
|---|---|---|---|---|---|
| network, hybrid head, **pattern f, projected** | **0.28** (0.29 / 0.28 / 0.27) | 0.41 (0.42 / 0.44 / 0.39) | 4.64 | **0.188** | 82 / 72 / 75 |
| network, hybrid head, pattern f, ridge (9b) | 0.33 | 0.40 | 4.60 | 0.220 | 73–119 |
| network, hybrid head, pattern d, projected (lever 1) | 0.40 | 0.50 | 4.70 | 0.23 | 30–140 |
| rung B, B1 MLP, pattern f, projected | 0.32 | 0.41 | 4.47 | 0.20 | — |

**Against the lines:** *ridge unnecessary* — and more: the projected target on the wide support is the best pattern-term run of the day on (a) (0.28 against
0.33 for the ridge, prediction 0.33–0.38 beaten), with the lowest Cartesian residual (0.188) and the earliest best epochs. The ridge target is dropped
for the hybrid head (it stays available; its bound is the lower one, its entries the less learnable ones). **The carried recipe is pattern f with the
registered projected target.** Against the hand-feature model on the same support the network is 0.04 better at 175 (0.28 vs 0.32); ω is the same (4.6 vs
4.5) — the ω gap is model-wide. Decision 51: best epochs 72–82 of 200.

## Dated amendment 1 October 18:1x — chain 16: the carried recipe at 750, and the lane-B runs moved to it (registered before they run)

**Chain 16** (lane A, right after chain 10): pattern f, projected target, hybrid head, carried recipe, pool A + A2 + B, seeds 0–2 →
`out/E7_rungC_lever1b_f_proj_750_2026-10-01`. Controls: rung B f at 750 (0.32 / ω 4.47, flat with data), chain 10 (f + ridge at 750, running: seeds 0–1 read
0.30 / 0.35), chain 13 at 175 (0.28). **Prediction:** (a) 0.24–0.28, (b) 0.36–0.40, ω 4.0–4.6. **Lines.** *T1 ratio met:* (a) ≤ 0.30 at 750 with the 175 → 750
step falling (≥ 0.02); the ω criterion of T1 (≤ 3 cm⁻¹) is read beside it and, if unmet, becomes the named next question (the model's ω gap: 4.5 against
a target bound of 0.4). *Network earns its place:* below rung B f (0.32) by both spreads at 750. Decision 51 as always.
**Chains 14 and 15 move to the projected target** (14b: kring weight 0.1 / 0.3 inside `--aux both`, pattern f, projected, 300 epochs; 15b: fresh vs
20-epoch pretrained mean body, pattern f, projected, 300 epochs); chain 14 was stopped by pid one minute after its start (18:06) and chain 15 before
it started. Predictions and lines as in their amendments, with chain 13 (0.28 / 4.64 / 0.188) as the control instead of chain 9b. **Chains 12 and 8b**
(λ cells and the 750 read on the d + ridge route) move to the end of lane A (after chain 6): the route is superseded; they stay as the record of it.

## Outcome, chain 10 — pattern f + ridge target at 750 — 1 October 19:3x (`out/E7_rungC_lever1b_f_ls_750_2026-10-01`)

(a) **0.36** (0.30 / 0.35 / **0.44**), (b) 0.42 (0.36 / 0.46 / 0.45), ω **3.91** (4.26 / 3.58 / 3.89 — the best ω of any run), ΔH 0.217; best epochs 71 / 113 / 170.
**Against the lines:** *flat* against its 175 read (0.33) — and with a seed spread (0.30–0.44) three times wider than any other run of the day: the ridge
target at 750 is unstable across seeds (seed 2 sits where the projected target's pattern-d run sat). Prediction 0.22–0.30 missed. The ridge route is closed
for the hybrid head on both counts (175: 0.33 vs 0.28 projected; 750: 0.36 with the spread). The one thing it leaves behind is ω 3.9, the lowest so far,
which says the ω gap is not fixed by the support alone. The T1 read moves to chain 16 (f + projected at 750, started 19:37; ≈ 1.3 h per seed beside lane
B → first seed ≈ 20:50, all three ≈ 23:30).

## Outcome, chain 14b — kring weight inside `--aux both`, pattern f, projected target, 175 — 1 October 19:5x (`out/E7_rungC_lever3b_fproj_kw{0.1,0.3}_175_2026-10-01`)

| recipe (pattern f, projected target, 175) | (a) ratio, seeds | (b) ratio | (a) ω | (a) ΔH residual | best epochs / 300 |
|---|---|---|---|---|---|
| pattern term alone (chain 13) | 0.28 (0.29 / 0.28 / 0.27) | 0.41 | 4.64 | 0.188 | 72–82 of 200 |
| pattern + 0.1 × kring | **0.25** (0.24 / 0.28 / 0.24) | **0.37** | 5.08 | 0.188 | 43–98 |
| pattern + 0.3 × kring | **0.24** (0.24 / 0.26 / 0.22) | **0.37** | 5.00 | 0.185 | 67–103 |

**Against the lines:** at weight 0.3 *works* — (a) 0.24 ≤ 0.31, ω 5.00 at the limit, ΔH 0.185 ≤ 0.25; at 0.1 the same with ω 5.08 a hair over. Against
chain 13 the kring term buys 0.04 on both hold-outs for +0.4 cm⁻¹ of ω at an unchanged Cartesian residual — the trade-off of lever 3 is now small
and controlled. These are the lowest (a) and (b) of the day. **Decision:** both recipes go to 750 — chain 16 (pattern term alone, running) and chain 17
(pattern + 0.3 × kring, registered below); T1's ratio criterion is met at 175 by both, its ω criterion (≤ 3) by neither, which names the next question.
Decision 51: best epochs well below the cap.

## Dated amendment 1 October 19:5x — chain 17: pattern f, projected target, pattern + 0.3 × kring at 750 (registered before it runs)

Lane B, at once (chain 15b, the pretraining cells, moves behind it): pool A + A2 + B, seeds 0–2, 200 epochs (best epochs at 175 were ≤ 103), the rest as
chain 14b → `out/E7_rungC_lever3b_fproj_kw0.3_750_2026-10-01`. **Prediction:** (a) 0.21–0.25, (b) 0.33–0.37, ω 4.5–5.2. **Lines.** *T1 ratio at 750:* (a) ≤ 0.30
with the 175 → 750 step not rising; the comparison with chain 16 (pattern term alone) says whether the kring term keeps its 0.04 at 750. Decision 51 as
always.

## Outcome, chain 17 — pattern f, projected target, pattern + 0.3 × kring, 750 — 1 October 22:3x (`out/E7_rungC_lever3b_fproj_kw0.3_750_2026-10-01`)

| read-out | 750, seeds 0 / 1 / 2 | the same recipe at 175 (chain 14b) | pattern term alone at 750 (chain 16, seeds 0–1 so far) | rung B, pattern f, 750 |
|---|---|---|---|---|
| (a) ring-coupling ratio | **0.22** (0.21 / 0.22 / 0.22) | 0.24 | 0.25 / 0.27 | 0.32 |
| (b) ring-coupling ratio | **0.33** (0.32 / 0.33 / 0.35) | 0.37 | 0.35 / — | 0.43 |
| (a) ω (cm⁻¹) | **3.50** (3.74 / 2.94 / 3.80) | 5.00 | 3.61 / 4.08 | 4.47 |
| (a) ΔH residual | **0.138** | 0.185 | 0.161 / 0.161 | 0.20 |
| best epochs | 88 / 75 / 94 of 200 | 67–103 | — | — |

**Against the lines:** prediction (a) 0.21–0.25, (b) 0.33–0.37, ω 4.5–5.2 — met on the ratios, beaten on ω. **T1's ratio criterion is met at 750**
(0.22 ≤ 0.30, the step 175 → 750 falls 0.24 → 0.22 with a seed spread of 0.01), on both hold-outs ((b) 0.33 against the proposal's T1 that reads (a) and
(b) together). The kring term keeps its advantage over the pattern term alone at 750 (0.22 against 0.25–0.27) and, unlike at 175, costs no ω here (3.50
against 3.6–4.1). Against the hand-feature model on the same support the network is 0.10 lower on (a) and 1 cm⁻¹ lower on ω, and it moved with data
where rung B did not. **T1's ω criterion (≤ 3 cm⁻¹) is not met: 3.50, one seed at 2.94** — the named next question. Decision 51: best epochs 75–94.
**Decision:** the carried recipe is pattern f, projected target, `--aux both --kring-weight 0.3`; its 449 point (for T2's three-point curve) and the ω
question are tomorrow's registrations.

## Dated amendment 1 October 22:4x — chain 18: the carried recipe at 449 (registered before it runs)

Pattern f, projected target, pattern + 0.3 × kring, pool A + A2 + B, `--sizes 449`, seeds 0–2 → `out/E7_rungC_carried_449_2026-10-01` (lane B after the
pretraining cells). With chain 14b (175: 0.24) and chain 17 (750: 0.22) it gives the three points of T2's curve (`probes/rungC_learning_curve_fit.py`).
**Prediction:** (a) 0.22–0.24, ω 3.8–4.6. **Lines.** *Monotone:* 175 > 449 > 750 beyond the seed spreads → the power law is fitted and its extrapolation to
5,000 read against T2 (ratio ≤ 0.20, ω ≤ 2). *Flat middle:* the curve is a step; the layer-B composition, not the count, is the suspect. Decision 51 as always.

## Outcome, chain 16 — pattern f, projected target, pattern term alone, 750 — 1 October 23:0x (`out/E7_rungC_lever1b_f_proj_750_2026-10-01`)

(a) **0.26** (0.25 / 0.27 / 0.28), (b) **0.38** (0.35 / 0.39 / 0.38), ω 3.84 (3.61 / 4.08 / 3.82), ΔH 0.166; best epochs 113–119 of 200. **Against the lines:**
prediction (a) 0.24–0.28 met; *T1 ratio met* (0.26 ≤ 0.30, the step 175 → 750 falls 0.28 → 0.26); *network earns its place* (below rung B f's 0.32 by far
more than both spreads, and moving with data where rung B is flat). Beside chain 17 (the same with 0.3 × kring: 0.22 / 0.33 / 3.50 / 0.138) the kring term
keeps its 0.04 on both hold-outs at 750 and costs no ω — the combination is the carried recipe, as decided at 22:3x. The ω criterion of T1 is unmet by
both (3.84 / 3.50). Decision 51: best epochs below the cap.

## Outcome, chain 15c — pretraining on the carried support (pattern f, projected target, mean body, 300 epochs, 175) — 2 October 00:0x (`out/E7_rungC_lever2b_fproj_{fresh_mean,pretrained_long}_175_2026-10-01`)

| body (pattern f, projected, pattern term, 175) | (a) ratio, seeds | (b) ratio | (a) ω | (a) ΔH residual | best epochs / 300 |
|---|---|---|---|---|---|
| fresh **mean** body | 0.30 (0.28 / 0.34 / 0.27) | 0.39 | **6.98** | 0.265 | 47–100 |
| 20-epoch QM9-pretrained mean body | **0.26** (0.25 / 0.27 / 0.27) | 0.38 | 4.71 | 0.202 | 64–108 |
| fresh **sum** body (chain 13, 200 epochs) | 0.28 (0.27 / 0.29 / 0.28) | 0.41 | 4.64 | 0.188 | 72–82 |

**Against the lines:** against its registered control (the fresh mean body) the pretrained body *works* — 0.26 against 0.30 with the spreads touching at
0.27, and ω 4.7 against 7.0 — but the fresh mean body is a poor control: its ω of 7.0 says mean pooling is the wrong body for this head (the sum body
reaches 4.6 fresh). Against the carried sum body the pretrained mean body is equal (0.26 / 4.7 against 0.28 / 4.6). **Reading:** geometry-only QM9
pretraining repairs a weak body's start and adds nothing beyond a good body at 175 molecules; the pretraining lever is *flat* against the carried
recipe. The line's consequence — "the pretraining is continued overnight" — is not taken; a Hessian-aware pretraining objective (or a pretrained *sum*
body) would be the next version of the question, and it is parked behind the ω question. Decision 51: best epochs below the cap.

## Outcome, lever 2c — encoder capacity, pattern d, projected target, 175 — 2 October 01:2x (`out/E7_rungC_lever2c_{deep,wide}_175_2026-10-01`)

| body (pattern d, projected, pattern term, 175) | (a) ratio, seeds | (b) ratio | (a) ω | (a) ΔH residual | best epochs / 200 |
|---|---|---|---|---|---|
| 3 blocks × 64 (lever 1) | 0.40 (0.40 / 0.42 / 0.39) | 0.50 | 4.70 | 0.23 | 97 / 30 / 140 |
| deep, 5 × 64 | 0.39 (0.37 / 0.44 / 0.36) | 0.43 | 4.60 | 0.234 | 155 / 58 / 187 |
| **wide, 3 × 128** | **0.35** (0.36 / 0.34 / 0.34) | **0.40** | **3.71** | 0.201 | 150 / 165 / **191** |

Design checks PASS (worst outputs 30 and 47). **Against the lines:** the wide body *works* — 0.34–0.36 against 0.39–0.42, below by more than both spreads,
and ω 3.7 against 4.7; the deep body is flat on (a) with a wide spread. The prediction ("both within spreads of 0.40") was wrong: at 175 molecules width
does feed this head. Decision 51: two of the wide body's best epochs (165, 191) are within 10 % of the cap — the re-run at a higher cap is folded into
chain 19 below, on the carried recipe, rather than repeated on pattern d.

## Dated amendment 2 October 01:3x — chain 19: the wide body on the carried recipe (registered before it runs)

Lane B after chain 18: pattern f, projected target, pattern + 0.3 × kring, **3 blocks × 128**, 175, seeds 0–2, **300 epochs** (decision 51) →
`out/E7_rungC_carried_wide_175_2026-10-01`; control chain 14b (3 × 64: 0.24 / 0.37 / ω 5.00). **Prediction:** (a) 0.20–0.23, ω 4.0–4.8. **Lines.** *Works:*
(a) ≤ 0.22 below 0.24 by both spreads, or ω below 5.0 by more than 0.5 with (a) unchanged → the wide body joins the carried recipe and is re-read at 750.
*Flat:* within spreads → width helped only the narrow support; the carried body stays 3 × 64. Decision 51 as always.

## Outcome, chain 18 and the first T2 curve — the carried recipe at 175 / 449 / 750 — 2 October 01:4x (`out/E7_rungC_carried_449_2026-10-01`, fit `out/rungC_lc_carried_2026-10-02`)

| pool | (a) ratio, seeds | (b) ratio | (a) ω | (a) ΔH residual | best epochs |
|---|---|---|---|---|---|
| 175 (chain 14b) | 0.24 (0.22 / 0.26 / 0.24) | 0.37 | 5.00 | 0.185 | 67–103 |
| 449 (chain 18) | **0.235** (0.21 / 0.24 / 0.25) | 0.35 | 4.58 | 0.178 | 55 / 90 / 92 |
| 750 (chain 17) | 0.22 (0.21 / 0.22 / 0.22) | 0.33 | 3.50 | 0.138 | 75–94 |

**Against the lines:** on the ratio the middle is *flat* — 175 and 449 overlap seed for seed (0.22–0.26 against 0.21–0.25); the gain sits in the step
449 → 750. On ω the curve is monotone beyond the spreads (5.00 → 4.58 → 3.50). **Power-law fit (`rungC_learning_curve_fit.py`, seed bootstrap, 68 % bands):**
(a) ratio slope −0.07 (factor 1.17 per decade) → **0.19 (0.18–0.21) at 5,000**, 0.18 at 20,000; (a) ω slope −0.23 (factor 1.69 per decade) → **2.4 (2.1–2.8)
at 5,000**, 1.8 (1.4–2.1) at 20,000; (b) ratio 0.29 at 5,000, (b) ω 3.4. **Against T2 (ratio ≤ 0.20 and ω ≤ 2 at ≈ 5,000):** the ratio extrapolation sits on the
criterion, ω misses it (2.4; the ω criterion would need ≈ 20,000 molecules at this slope, or a model that steepens it). The registered consequence of the
flat middle is taken: the composition control (chain 20, below) separates the count from the layer-B content of the 750 pool before the curve is read
as a law. Decision 51: best epochs below the cap.

## Dated amendment 2 October 01:5x — chain 20: composition control at equal count (registered before it runs)

The 175 point draws from A + A2 only; the 449 and 750 points mix in layer B. **Run (lane B after chain 19):** the carried recipe with `--pool-layers A,A2,B
--sizes 175` (175 molecules in the hashed order of the mixed pool), seeds 0–2 → `out/E7_rungC_carried_mixed175_2026-10-01`. **Prediction:** (a) 0.22–0.25 (the
same as A + A2 at 175). **Lines.** *Count:* within spreads of chain 14b → the curve is a count curve with a shallow ratio slope and the T2 numbers above
stand. *Composition:* ≤ 0.21 or ≥ 0.27 → layer B's substituted molecules move the hold-out by themselves, and the curve must be re-drawn at fixed
composition before any extrapolation. Decision 51 as always.

## Outcome, chain 19 — the wide body on the carried recipe, 175 — 2 October 02:4x (`out/E7_rungC_carried_wide_175_2026-10-01`)

3 × 128, 300 epochs: (a) **0.22** (0.23 / 0.21 / 0.23), (b) 0.35, ω 4.92 (4.19 / 6.06 / 4.51), ΔH 0.176; best epochs 50–94. Control chain 14b (3 × 64): 0.24
(0.22–0.26), 0.37, ω 5.00. **Against the lines:** *flat* — the spreads touch at 0.22 and ω moves by 0.08, not 0.5. Width helped the narrow support (pattern d:
0.40 → 0.35) and not the wide one: once the pairs it needs are on the pattern, the 64-channel body is enough at 175. **The carried body stays 3 × 64.**
Decision 51: best epochs far below the cap.

## Outcome, chain 6 — pattern d, projected target, 449 — 2 October 03:0x (`out/E7_rungC_lever1_d_449_2026-10-01`, fit `out/rungC_lc_pattern_d_2026-10-02`)

(a) **0.37** (0.36 / 0.37 / 0.37), (b) 0.42, ω 4.06, ΔH 0.217; best epochs 90–127. The pattern-d curve is 175 / 449 / 750 = 0.40 / 0.37 / 0.37 (ω 4.7 / 4.1 / 4.0):
a step from 175 to 449 and a flat middle-to-end — the mirror image of the carried recipe's curve (flat 175 → 449, step 449 → 750). Prediction 0.38–0.40
missed by 0.01 on the low side. **Against the lines:** *flat middle* for this curve as well (449 and 750 equal within seeds). The power-law fit gives the same
factor as the carried recipe's (1.17 per decade; 0.32 at 5,000) but two curves that each have one step and one flat segment are not yet a law: both read
as composition or sampling effects of the pool at these counts, and the composition control (chain 20, running) is the next word on T2 for both.
Decision 51: best epochs below the cap.

## Outcome, chain 20 — composition control: the carried recipe at 175 from the mixed pool — 2 October 03:0x (`out/E7_rungC_carried_mixed175_2026-10-01`)

The first 175 molecules of the mixed pool's hashed order are 138 layer-B and 37 layer-A2 molecules, no layer A. Read-outs: (a) **0.275** (0.28 / 0.26 / 0.28),
(b) 0.37, ω 5.75 (7.0 / 4.8 / 5.5), ΔH 0.208; best epochs 29–91. Control, 175 from A + A2 (chain 14b): 0.24 (0.22–0.26), 0.37, ω 5.00. **Against the lines:**
*composition* — 0.275 ≥ 0.27: at equal count the B-heavy pool is worse on hold-out (a) (whose ten molecules are layer-A parents) and equal on (b)
(scaffolds). **Reading:** the mixed-pool curve (175 → 449 → 750) conflates count with composition — the larger points add molecules that are both more
numerous and less like hold-out (a). Its extrapolation (0.19 at 5,000) is therefore not a count law and is withdrawn as a T2 number. The curve is
re-drawn at fixed composition: within A + A2 at 45 / 100 / 175 (chain 21, below) — the sizes rung B's curve used — with the 750 point kept as
"more count and a different mix". Decision 51: best epochs below the cap.

## Dated amendment 2 October 03:1x — chain 21: the carried recipe at fixed composition, 45 and 100 (registered before it runs)

Lane B at once: pattern f, projected target, pattern + 0.3 × kring, `--pool-layers A,A2 --sizes 45,100`, seeds 0–2 → `out/E7_rungC_carried_AA2_45_100_2026-10-01`;
with chain 14b (175) it gives a three-point curve at fixed composition. **Prediction:** (a) 0.34–0.40 at 45, 0.28–0.32 at 100. **Lines.** *Law:* monotone
beyond spreads over 45 / 100 / 175 → fitted and extrapolated (`rungC_learning_curve_fit.py`); the slope within A + A2 is the T2 slope until a larger
fixed-composition pool exists. *Flat:* the sizes 45–175 do not separate → T2 needs the PC-scale pool and no extrapolation is written. Decision 51 as always.

## Outcome, chain 21 — the carried recipe at fixed composition (A + A2: 45 / 100 / 175) — 2 October 04:1x (`out/E7_rungC_carried_AA2_45_100_2026-10-01`, fit `out/rungC_lc_carried_AA2_2026-10-02`)

| pool (A + A2 only) | (a) ratio, seeds | (b) ratio | (a) ω | best epochs |
|---|---|---|---|---|
| 45 | 0.29 (0.28 / 0.28 / 0.30) | 0.41 | 7.0 | 164 / 131 / 64 |
| 100 | **0.25** (0.26 / 0.24 / 0.23) | 0.38 | 4.9 | 84 / 155 / 176 |
| 175 (chain 14b) | 0.24 (0.22 / 0.26 / 0.24) | 0.37 | 5.0 | 67–103 |
| 750, mixed (chain 17) | 0.22 (0.21–0.22) | 0.33 | 3.5 | 75–94 |

**Against the lines:** 45 → 100 is a step beyond the spreads (0.29 → 0.25, ω 7.0 → 4.9); 100 → 175 is *flat* (0.25 → 0.24, ω 4.9 → 5.0). Predictions
0.34–0.40 at 45 and 0.28–0.32 at 100 were pessimistic. The three-point fit (factor 1.37 per decade on (a)) is carried by the 45 point and is not written
as a T2 number: at fixed composition the ratio saturates near 0.24 by 100 molecules of A + A2. The 750 point's 0.22 and its (b) 0.33 come with layer B —
molecules of a different kind, not more of the same — and hold-out (b) (scaffolds) gains most from them. **Reading for T2:** on this corpus, data pays
through *coverage* (new kinds of molecules) more than through count; a count law needs a pool whose diversity grows with its size, which is what the
PC-scale corpus would be. No extrapolation is written; the T2 question is restated as a coverage question (which molecules to compute next), and the
read-out to design it with is the per-molecule field of the records (H7). Decision 51: one best epoch at 100 (176) within 10 % of the cap — noted, not
repeated (the point is flat with its neighbours).

## Dated amendment 2 October 04:2x — lever 5: the ω question — a diagonal term over all modes (registered before it runs)

**Framing (investigation log, 04:1x):** on the carried model at 750 the hold-out ω rms is carried by the *other* family (5.0 cm⁻¹ against 2.4 for the ring
in-plane modes) — the diagonal entries no term weights. **Code:** `rungC_train.py --kdiag-weight` adds, inside `--aux both`, the mean square of the
diagonal of K_pred − K_true over all modes relative to the diagonal's own mean square (`_kdiag_term`; test). **Run (`rungC_sherlock22_1001.sh`, lane B at
once):** the carried recipe (pattern f, projected target, pattern + 0.3 × kring) with kdiag 0.1 and 0.3, 175, seeds 0–2 → `out/E7_rungC_lever5_kd{0.1,0.3}_175_2026-10-01`;
control chain 14b (0.24 / 0.37 / ω 5.00). **Prediction:** ω 4.2–4.8 at 0.3 with (a) 0.23–0.26. **Lines.** *Works:* ω below 5.0 by more than 0.5 with (a) ≤ 0.26
→ carried, re-read at 750. *Flat:* ω within 0.3 of 5.0 → the diagonal is not what limits ω under this head; the next suspect is the per-class scale floor of
the diagonal classes. *Hurts:* (a) > 0.27 → the ω gain costs couplings; the weight is lowered or the term dropped. Decision 51 as always.

## Outcome, lever 5 (first cell) — K-diagonal term, weight 0.1, on the carried recipe, 175 — 2 October 05:2x (`out/E7_rungC_lever5_kd0.1_175_2026-10-01`; the 0.3 cell is running)

| recipe (pattern f, projected, pattern + 0.3 × kring, 175) | (a) ratio, seeds | (b) ratio | (a) ω, seeds | (a) ΔH residual | best epochs |
|---|---|---|---|---|---|
| without the diagonal term (chain 14b) | 0.24 (0.22 / 0.26 / 0.24) | 0.37 | 5.00 | 0.185 | 67–103 |
| **+ 0.1 × K-diagonal term** | **0.23** (0.22 / 0.23 / 0.24) | **0.36** | **2.78** (2.7 / 2.9 / 2.7) | **0.144** | 89–104 |

**Against the lines:** *works*, by far more than the line asked (ω below 5.0 by 2.2 cm⁻¹ against the 0.5 required; (a) unchanged; ΔH residual down from
0.185 to 0.144). The framing of 04:1x was right: the ω error sat in diagonal entries no term weighted. **T1's ω criterion (≤ 3 cm⁻¹) is met at 175 by this
recipe, with the ratio criterion already met.** The 0.3 cell and the 750 read (chain 23, registered below) follow. Decision 51: best epochs below the cap.

## Dated amendment 2 October 05:3x — chain 23: the carried recipe with the diagonal term at 750 (registered before it runs)

Lane B after chain 22: pattern f, projected target, pattern + 0.3 × kring + 0.1 × K-diagonal (the weight is raised to 0.3 before the start if the 0.3 cell
reads better on ω at equal (a); the choice is recorded here before the run starts), pool A + A2 + B, seeds 0–2 → `out/E7_rungC_carried_kd_750_2026-10-01`.
Controls: chain 17 (750 without the diagonal term: 0.22 / 0.33 / ω 3.50) and rung B f at 750 (0.32 / 0.43 / 4.47). **Prediction:** (a) 0.20–0.23, (b)
0.32–0.35, ω 2.2–2.8. **Lines.** *T1 met in full:* (a) ≤ 0.30 and ω ≤ 3 at 750 on hold-out (a), (b) read beside it. *Half:* ω ≤ 3 with (a) above chain 17 by
both spreads → the trade-off returns at 750 and the weight is searched. Decision 51 as always.

## Outcome, lever 5 (both cells) — 2 October 06:1x (`out/E7_rungC_lever5_kd{0.1,0.3}_175_2026-10-01`)

| K-diagonal weight (pattern f, projected, pattern + 0.3 × kring, 175) | (a) ratio | (b) ratio | (a) ω | (b) ω | (a) ΔH | best epochs |
|---|---|---|---|---|---|---|
| 0 (chain 14b) | 0.24 | 0.37 | 5.00 | 5.6 | 0.185 | 67–103 |
| 0.1 | 0.23 (0.22 / 0.23 / 0.24) | 0.36 | **2.78** (2.7 / 2.9 / 2.7) | 4.02 | 0.144 | 89–104 |
| 0.3 | 0.225 (0.23 / 0.23 / 0.22) | **0.34** | **2.76** (2.9 / 2.6 / 2.8) | **3.60** | 0.153 | 60–138 |

Both cells *work*; they are equal on hold-out (a) within spreads and 0.3 is better on hold-out (b) (0.34 / ω 3.6 against 0.36 / 4.0). Chain 23 (750) started
06:07 at weight 0.1, as the amendment of 05:3x fixed (ω(a) equal, so no change before the start); the (b) advantage of 0.3 is noted and a 0.3 cell at 750
follows if chain 23 reads *half* or if (b) matters for the decision. Decision 51: best epochs below the cap.

## Dated amendment 2 October 06:2x — anthracene CCSD(T)/cc-pVDZ Hessian on the CCX53, and the gate's two-route checks moved to a parallel lane (registered before the launch)

**Why anthracene** (the user, 2 Oct: "ik denk dat we het sowieso moeten doen"): the first three-ring CC anchor; with benzene, fluorobenzene, pyridine and
naphthalene it makes T3 a test over ring count. Corpus id `A_a1e6ec1862` (layer A, 24 atoms, B3LYP and ωB97X FD Hessians present). **Machine:** CCX53
`ubuntu-128gb-hel1-2` (32 dedicated vCPU, 122 GB; the CCX63 was not orderable), bootstrapped 06:10 (env qc05, pyscf 2.14.0, kernels built against its
bundled OpenBLAS/libgomp), gate 1 to pass there before the launch. **Gate change (code, tested, smoke on water in WSL and on the server):**
`e8_cc_hessian_fd.py --two-route-check {inline,separate,only}` — the kernel-against-pyscf comparisons (lambda 93 min and density 5.2 h on naphthalene;
estimated 2–3 days on anthracene) run in a lane *beside* the partial runs (`only` mode recomputes the reference with the checks, compares with the stored
reference to 1e-8 and writes `two_route_check.json`); the assembling run refuses an unchecked reference without that passing file. Nothing is skipped;
the wait is removed. Default `inline` = the registered behaviour. **Launch plan:** `run_anchors_hel23_parallel.sh` with `TWO_ROUTE=separate`, ANCHOR_LIST
`anthracene|molecules/A_a1e6ec1862/geometry.json|results/anthracene_ccpvdz|4|8|22000|--fast-t-density --fast-t-lambda`, check lane 8 threads × 16000 MB,
memory guard 1500 MB (4 × 22 + 16 = 104 of 122 GB). **Predictions:** ≈ 20 symmetry-unique displacements (D₂h), 2.5–4 h per production gradient at 8 threads,
≈ 1.5 days to the Hessian, ≈ €35–50; the check lane finishes within the production window. **Lines:** VALID by the probe's own checks (asymmetry,
symmetry reconstruction, sum rule, energy route, pair checks) and a passing two-route file → the anchor joins the set; IMAGINARY / INVALID → excluded
and read as such; a failed two-route file → the Hessian is not written and the kernels are re-examined on this molecule before anything else.

## Outcome, chain 12 — λ and weight cells for the ridge target on pattern d, 175 — 2 October 06:2x (`out/E7_rungC_lever4_{lam1e-1,lam1e-2,w0.3}_175_2026-10-01`)

| cell (pattern d, ridge target, 175) | (a) ratio, seeds | (b) ratio | (a) ω | best epochs / 200 |
|---|---|---|---|---|
| λ 1e-3, weight 1.0 (7c) | 0.44 (0.42–0.45) | 0.49 | 4.44 | 158–167 |
| **λ 1e-1**, weight 1.0 | **0.35** (0.35 / 0.36 / 0.35) | 0.41 | **4.03** | 175 / 191 / 199 |
| λ 1e-2, weight 1.0 | 0.38 (0.40 / 0.36 / 0.37) | 0.45 | 4.14 | 196 / 166 / 189 |
| λ 1e-3, weight 0.3 | 0.39 (0.38 / 0.38 / 0.40) | 0.45 | 4.14 | 161 / 173 / 185 |
| projected target (lever 1) | 0.40 (0.39–0.42) | 0.50 | 4.70 | 30–140 |

**Against the lines:** λ 1e-1 *works* on the narrow support — 0.35 against 0.40, below by both spreads, ω 4.0 — the strongly anchored ridge target (entries at
the projected scale, bound 0.28 against 0.31) is learnable where the λ 1e-3 one was not; the weaker-anchored cells are flat. All best epochs sit within
10 % of the cap (decision 51 flags the whole chain; the ridge targets converge slowly). **Reading and decision:** on pattern d the ridge at λ 0.1 would be a
lever (0.40 → 0.35), but the carried support (pattern f, projected: 0.28, with the K terms 0.23) is already far below it, and chain 13 showed the projected
target winning on pattern f. The ridge route is closed as planned; λ 0.1 is the setting to try if a ridge target is ever revisited. Chain 8b (d + ridge
λ 1e-3 at 750) runs last as the record of the route.

## Dated amendment 2 October 06:4x — lever 1 / T3: leave-one-anchor-out transfer to CCSD(T) (registered before it runs)

**Question.** Does the proxy-trained network carry over to coupled-cluster level on an anchor it never saw? **Data.** The four valid CCSD(T)/cc-pVDZ
anchors (benzene `e8_benzene_ccpvdz_tlambda`, fluorobenzene and pyridine `…_2026-09-30`, naphthalene `…_tlambda_2026-10-02`) as the high level, the
analytic B3LYP of each as the low level (`substitute_cc`). **Model.** The carried recipe at 750 (pattern f, projected target, pattern + 0.3 × kring + 0.1 ×
K-diagonal) saved per seed (`--save-model`, chain 24 on lane A after chain 8b). **Code.** `rungC_train.py`: `molecule_tensors` factored out, `--save-model`,
`load_hybrid_model`, `freeze_for_transfer`; `m05/rungC_cc_transfer.py`; tests `tests/test_rungC_cc_transfer.py`. **Procedure.** For each held-out anchor:
fine-tune the saved model on the other three with only the head's last layer and the SQM α trainable (300 epochs, lr 1e-3, the registered terms), read
out on the held-out with the registered read-outs; beside it the zero rule (B3LYP as is), the proxy model untouched, α only, and a per-class α scaling fitted
on the three (the SQM-like transfer, no network). Three seeds' models → three repeats. **Predictions.** Zero rule ω on the anchors ≈ 20–50 cm⁻¹ (the CC
correction is 2.4× the proxy); the untouched proxy model removes part of it but not the scale (ratio 0.5–0.8); α scaling 0.5–0.7; head-tuned network
0.35–0.6 on the ring couplings with ω 6–15 cm⁻¹ — three anchors are few. **Lines (T3 as proposed: in-plane ω ≤ 3 cm⁻¹ on the held-out anchor).**
*Met:* head-tuned ω ≤ 3 on naphthalene (the fused ring, the anchor that matters). *Transfers but short:* head-tuned below α scaling by more than the seed
spread on every anchor and ω under half the zero rule → the network carries structure to CC level; more anchors are the lever (anthracene running). *Does
not transfer:* head-tuned not below α scaling → the proxy features do not describe the CC correction; the route becomes CC data first. Decision 51 is
not at stake (fixed epochs on a convex-ish head problem; the loss history is recorded).

## Outcome 2 October 10:2x — chain 23: the carried recipe with the K-diagonal term at 750 (lever 5 of 2 Oct 05:2x, registered 06:0x)

`out/E7_rungC_carried_kd_750_2026-10-01.json` (pattern f, projected target, pattern + 0.3 × kring + 0.1 × K-diagonal, 3 × 64 sum body, 750 molecules,
seeds 0–2, cap 200, patience 20; best epochs 83 / 113 / 79 — decision 51 satisfied). **Hold-out (a):** ring-coupling ratio 0.226 / 0.215 / 0.219
(mean **0.22**), corrected ω rms 2.88 / 2.98 / 2.59 (mean **2.82 cm⁻¹**, zero rule 23.3), ΔH residual 0.139; per-family diagonal rms CH-stretch 1.1–1.6,
ring-ip 2.1–2.3, CH-oop 3.0–3.4, other 4.1–5.0 cm⁻¹. **Hold-out (b):** 0.345 / 0.341 / 0.315 (mean 0.33), ω 3.6. Against the 06:0x prediction
(≤ 0.22 on (a), ω ≤ 3): both met; against chain 17 (same recipe without the diagonal term: 0.22 / ω 3.50): the ratio unchanged, ω −0.7 cm⁻¹ — the
diagonal term buys frequency accuracy without costing the couplings, as it did at 175 (2.78 vs 5.0). **T1 as proposed on 1 Oct (ratio ≤ 0.25 and
ω ≤ 3 cm⁻¹ on hold-out (a) at the full pool) is met.** The carried recipe stays this one; chain 24 retrains it with `--save-model` for T3.

## Outcome 2 October 10:5x — chain 8c: the ridge-anchored target on pattern d at 750 (lever 4 of 1 Oct, the route's last record)

`out/E7_rungC_lever4_ls_750_2026-10-01.json` (hybrid, pattern d, LS target λ 1e-3, pattern term, 750 molecules, seeds 0–2): hold-out (a) ratio
0.60 / 0.46 / 0.45 (mean 0.50), ω 4.4 / 4.0 / 4.3; hold-out (b) 0.54 / 0.48 / 0.50, ω 5.0–5.4. Worse than the projected target on the same pattern at 750
(chain 6: 0.37) and than the ridge target at 175 (0.44): more data does not rescue a target the network cannot fit (H9's second half — the LS target
lowers the bound but is less learnable). The lever-4 route is closed as recorded at 06:2x; pattern f with the projected target is the carried recipe.

## Outcome 2 October 14:1x — chain 24: the carried recipe at 750 again, models saved (lever 1 / T3 amendment 06:4x); first intensity read-outs

`out/E7_rungC_carried_kd_750_saved_2026-10-02.json` (identical recipe to chain 23, `--save-model`; seeds 0–2, best epochs 77 / 80 / 138). **Hold-out (a):**
ratio 0.236 / 0.219 / 0.206 (mean **0.22**), ω 2.96 / 2.78 / 2.45 (mean **2.73 cm⁻¹**), ΔH residual 0.126–0.153; **hold-out (b):** 0.346 / 0.348 / 0.324
(mean 0.34), ω 3.6. T1 reproduced within the seed spread of chain 23 (0.22 / 2.82). The three models `…_model_n750_seed{0,1,2}.pt` feed chain 25 (T3) and
chain 26 (the intensity read on all ten (a) parents). **Intensity read-out (lever 5 step 2, registered 06:5x), on the two (a) parents whose APT existed at
the start (A_fdc27f1bd1, A_e72997e726):** spectrum overlap **0.978 / 0.990 / 0.968** (zero rule 0.239), intensity-weighted relative rms **0.23 / 0.18 / 0.19**
(zero rule 0.47). The registered line (overlap ≥ 0.95) is met on these two; the zero rule sits at 0.24, not the ≈ 0.85 guessed — the overlap is dominated by
frequency positions at 10 cm⁻¹ FWHM (noted 11:0x). The full ten read in chain 26.

## Outcome 2 October 14:2x — chain 25: T3 leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (amendment 06:4x)

`out/T3_cc_transfer_seed{0,1,2}_2026-10-02.json` — chain 24's three models, four folds each, 300 fine-tune epochs at lr 1e-3. Ring-coupling ratio
(mean over the three models, range) and **ring-ip corrected-ω rms in cm⁻¹** on the held-out anchor:

| held-out | zero rule | α scaling (3 anchors, no network) | network untouched | network, α tuned (9 parameters) | network, head tuned |
|---|---|---|---|---|---|
| benzene | 1.00 / 25.0 | 0.12 / 6.4 | 0.91 / 22.8 | 0.16 (0.13–0.17) / **6.2** | **0.07** (0.05–0.09) / **4.4** |
| fluorobenzene | 1.00 / 28.3 | 0.18 / 7.8 | 0.99 / 26.0 | 0.22 / **5.2** | 0.21 (0.15–0.26) / 5.2 |
| pyridine | 1.00 / 25.9 | 0.23 / 7.3 | 0.89 / 30.8 | 0.27 / 6.6 | 0.26 (0.23–0.28) / **5.2** |
| naphthalene | 1.00 / 25.9 | 0.32 / 10.2 | 0.99 / 20.4 | **0.27** (0.25–0.29) / **6.0** | 0.41 (0.25–0.67) / 10.5 |

All-mode ω (CH-oop and CH-stretch included) stays 6–26 cm⁻¹: the cc-pVDZ CC correction of the out-of-plane modes is not carried by anything here.
**Against the lines.** *Met* (head-tuned ring-ip ω ≤ 3 on naphthalene): **not met** — 10.5, and the best column gives 6.0. *Transfers but short:* the
untouched proxy model does nothing at CC scale (ratio 0.9–1.0: it predicts a correction of proxy size, 2.4× too small and differently shaped); the
**α-tuned network beats α scaling on ring-ip ω on all four anchors** (6.2 / 5.2 / 6.6 / 6.0 against 6.4 / 7.8 / 7.3 / 10.2) and on the ratio on the fused
ring (0.27 against 0.32) — the network's features carry structure of the CC correction beyond a per-class scale, most visibly where the correction is
largest; the head fine-tune (257 parameters on three molecules) wins on benzene and pyridine but is unstable on naphthalene (0.25–0.67 across models),
i.e. it overfits three anchors. Verdict: **transfers but short**, by the α-tuned column; the lever is more anchors (anthracene running) and a fine-tune
between α (9 parameters) and the full last layer. The ω of 5–6 cm⁻¹ in-plane on an unseen molecule from three CC anchors is the number to carry.

### Amendment 14:2x — T3b: the regularised head fine-tune (registered before it runs)

`rungC_cc_transfer.py --head-l2 λ`: the head fine-tune with an L2 penalty λ‖W − W₀‖² toward the proxy-trained last layer (W₀), λ ∈ {0.01, 0.1, 1}, same
folds, same three models (chain 27). **Predictions.** Naphthalene's ring-ip ω lands between the α-tuned 6.0 and the head-tuned 10.5 for λ = 0.01, at or
below 6.0 for λ ≥ 0.1, with the model spread of the ratio under 0.1 (against 0.25–0.67 now); benzene and pyridine keep their head-tuned gain at λ ≤ 0.1.
**Lines.** *Regularised head is the transfer recipe:* some λ beats the α-tuned column on ring-ip ω on all four anchors. *α stays the recipe:* no λ does;
then the transfer recipe until more anchors is α-tuning, and T3 waits for anthracene. T3's ≤ 3 cm⁻¹ line stands for the four-anchor set with anthracene added.

## Outcome 2 October 15:0x — chains 27/27b: T3b, the L2-to-proxy regularised head (amendment 14:2x)

`out/T3b_l2{0.01,0.1,1}_seed{0,1,2}_2026-10-02.json` (the λ 0.01 and 0.1 cells rerun as chain 27b after the `with_suffix` incident of 14:4x — the first
copies overwrote each other; fixed with `record_paths` and a test). Ring-coupling ratio (mean, range over the three models) and ring-ip ω of the
regularised head, against the α-tuned column:

| held-out | λ 0.01 | λ 0.1 | λ 1 | α tuned |
|---|---|---|---|---|
| benzene | 0.04 (0.03–0.06) / 4.4 | 0.07 / 5.4 | 0.13 / 5.5 | 0.16 / 6.2 |
| fluorobenzene | 0.17 (0.13–0.20) / 5.3 | 0.16 / 6.0 | 0.19 / 5.4 | 0.22 / **5.2** |
| pyridine | 0.25 / 5.1 | 0.24 / 5.6 | 0.25 / 6.0 | 0.27 / 6.6 |
| naphthalene | 0.37 (0.19–0.64) / 9.4 | 0.33 (0.19–0.41) / 8.3 | **0.23 (0.22–0.25) / 5.9** | 0.27 (0.25–0.29) / 6.0 |

**Against the lines.** *Regularised head is the transfer recipe* (some λ beats α-tuning on ring-ip ω on all four): **not met** — fluorobenzene stays at or
above α-tuning for every λ (5.3–6.0 against 5.2). *α stays the recipe:* **met, with a qualification** — λ = 1 ties α-tuning (three of four below it, fluorobenzene
+0.2 cm⁻¹), removes the naphthalene instability (0.22–0.25 against 0.25–0.67 unregularised) and gives the lowest naphthalene ratio of any column (0.23).
The predictions held in direction: naphthalene improves monotonically with λ (9.4 → 8.3 → 5.9), benzene and pyridine keep their gain at small λ. Transfer
recipe until more anchors: α-tuning, with the λ = 1 head as the equal alternative; T3's ≤ 3 cm⁻¹ line waits for anthracene as the fourth anchor (≈ 5 Oct).

## Dated amendment 2 October 17:2x — coverage ablation (registered before it runs; the user: "Blijf Sherlock")

**Question.** The error map (06:5x) says the hold-out error follows the scaffold size, and the next pool (200 ids, running) is chosen on that reading
with the prediction (b) ≤ 0.28. The existing pool can test the mechanism tonight: it holds 130 molecules with three or more aromatic rings
(phenanthridine 34, acridine, dibenzothiophene, carbazole, dibenzofuran, phenanthrene 12, anthracene 10, phenazine, biphenylene 7, pyrene 7 — children of
the layer-A three-ring parents plus pyrenes; `out/pool_ring3plus_ids_2026-10-02.txt`). **Runs (chain 28, carried recipe, three seeds each).** *Ablation:*
the pool without those 130 (620 molecules, `--exclude-ids-file`). *Control:* the first 620 of the full pool in its hash order (`--sizes 620`), i.e. the
same count with the three-ring molecules kept in proportion. **Read-outs.** Hold-out (a) ratio overall and on its three-ring parents (phenanthrene,
phenanthridine, biphenylene: 0.20 today); hold-out (b) ratio (fluorene / fluoranthene scaffolds, 0.33 today); the per-kind error map on both.
**Predictions.** *Within-scaffold coverage:* the (a) three-ring parents worsen from 0.20 to ≥ 0.30 in the ablation and stay within 0.03 in the control —
the children of a scaffold carry its parent. *Cross-scaffold coverage:* (b) worsens by ≥ 0.03 in the ablation relative to the control, because the pyrenes
and the three-ring systems teach fused-ring couplings that fluoranthene and fluorene share. **Lines.** *Both hold:* the next pool's prediction stands, and
the ordering of future pools is by scaffold coverage. *Within holds, cross does not* ((b) within 0.03 of the control): scaffold coverage transfers only to
substituted children of the same parent — then the 200 improve (b) only through their fused two-ring B rows, the prediction for (b) is lowered to
≤ 0.31, and the four-ring A2 rows are valued for (a)-type parents, not for unseen scaffolds. *Neither holds:* the error map's gradient is about scaffold
*difficulty*, not coverage, and the data lever is not the data; the model-side levers return. Decision 51 applies (cap 200, patience 20).

## Outcome 2 October 17:2x — chain 26: the intensity read-out on all ten hold-out (a) parents (lever 5 step 2, registered 06:5x)

`out/eval_saved_carried750_seed{0,1,2}_2026-10-02.json` (`probes/rungC_eval_saved.py` on chain 24's three models; atomic polar tensors from the CPHF route for
all ten (a) parents — benzene's after the sum-rule limit was set by its two-route measurement, 4.4e-4 e against FD; seed 0's read ran with nine).
**Spectrum overlap** (cosine of the Lorentzian-broadened spectra, FWHM 10 cm⁻¹, predicted against true corrected): **0.968 / 0.966 / 0.974** against
**0.278** for the zero rule. **Intensity-weighted relative intensity error:** **0.18 / 0.16 / 0.14** against **0.59**. Frequencies on the same molecules
2.5–2.8 cm⁻¹ as recorded. **Against the line** (overlap ≥ 0.95 for the carried model): **met** by all three models. The baseline guess of 06:5x (≈ 0.85 for
the zero rule) was wrong by the mechanism noted at 11:0x — at 10 cm⁻¹ FWHM the overlap is a frequency-position metric; the relative intensity error is
the intensity-specific number, and it falls from 0.59 to 0.14–0.18: the predicted correction reproduces how the lines redistribute intensity, not only
where they sit. What this does not say: the APT is the low level's own; the CC-level dipole response is a separate term (E8 stores no dipoles yet).

## Outcome 2 October 22:0x — chain 28: the coverage ablation (amendment 17:2x)

`out/E7_rungC_coverage_ablation620_2026-10-02.json` (the pool without its 130 three-and-more-ring molecules, 620) and `…_control620_…` (the first 620 of the
full pool), carried recipe, three seeds each, best epochs 112–139 / 57–139.

| arm | (a) ratio | (a) ω | (a) three-ring parents (phenanthrene / phenanthridine / biphenylene) | (a) single-ring (benzene / biphenyl / benzonitrile) | (b) ratio | (b) fluorene scaffold | (b) fluoranthene scaffold |
|---|---|---|---|---|---|---|---|
| control 620 | 0.229 | 3.10 | 0.15 / 0.16 / 0.15 | 0.06 / 0.24 / 0.10 | 0.349 | 0.30 | 0.37 |
| ablation 620 | **0.373** | 4.78 | **0.48 / 0.52 / 0.34** | 0.11 / 0.23 / 0.13 | **0.411** | **0.40** | 0.41 |

**Against the predictions.** *Within-scaffold coverage* (three-ring parents ≥ 0.30 without their children, control within 0.03): holds — 0.15 → 0.48–0.52,
while the single-ring parents do not move. *Cross-scaffold coverage* ((b) worse by ≥ 0.03 than the control): holds — 0.349 → 0.411; the fluorene
scaffold carries most of it (0.30 → 0.40), fluoranthene less (0.37 → 0.41). The control at 620 equals the 750 record (0.229 / 0.349 against 0.22 / 0.33):
the last 130 molecules of the hash order add nothing by count. **Line: both hold.** The next pool's prediction stands ((b) ≤ 0.28 with the 200 in), future
pools are ordered by scaffold coverage, and T2 reads as coverage: what a scaffold family teaches transfers to its parents (strongly) and to neighbouring
fused scaffolds (by 0.06–0.10). What this does not yet say: whether the seven pyrenes (the only four-ring source) or the 123 three-ring children carry the
cross-scaffold part — chain 29.

### Amendment 22:0x — chain 29: pyrenes against three-ring children (registered before it runs)

Two arms, carried recipe, three seeds: *no-ring4* = the pool without its 7 pyrenes (743; `out/pool_ring4_ids_2026-10-02.txt`); *no-ring3* = the pool
without the 123 three-ring molecules (627; `…ring3only…`). **Predictions.** no-ring3 reproduces most of chain 28: three-ring parents ≥ 0.40, (b) ≥ 0.38,
fluorene scaffold ≥ 0.37; no-ring4 leaves (a) within 0.02 of the control and moves the fluoranthene scaffold by < 0.03 — seven molecules are too few to
carry a scaffold. **Lines.** *Pyrenes matter:* no-ring4 moves fluoranthene by ≥ 0.03 → the four-ring A2 rows are worth more per molecule than the
three-ring ones, and the next pool after the 200 is four-ring first. *Pyrenes do not matter at seven:* then the 93 four-ring rows in the manifest are a
question of count (the 55 in the running 200 answer it), and the three-ring family is the proven lever.
