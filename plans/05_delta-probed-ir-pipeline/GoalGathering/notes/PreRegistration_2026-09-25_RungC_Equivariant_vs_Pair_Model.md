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
