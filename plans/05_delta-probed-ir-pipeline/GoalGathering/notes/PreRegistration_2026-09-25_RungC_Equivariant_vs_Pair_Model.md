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
