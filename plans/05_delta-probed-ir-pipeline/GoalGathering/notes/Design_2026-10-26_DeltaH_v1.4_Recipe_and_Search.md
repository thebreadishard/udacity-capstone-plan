# Design and draft registration, 26 October 2026 — ΔH-network version 1.4: what it carries, and a search for hyperparameters we do not know

*Registered 26 October 2026 12:1x on the user's answers to §8, before any v1.4 number exists; the frozen configuration list and the test-set hashes are added by step 0 before the first training. TASKS 129. The user, 26 Oct: "Houd bij neurale netwerken rekening met het feit dat we vantevoren niet weten wat de beste
hyperparameters zijn."*

## 1. Why a new version

The audit of 26 Oct found that the carried network is still version 1.1 (chain 34, 5 Oct; `modules/05_support_predictor/out/MODELS_STATUS.json`):
trained on 750 molecules with finite-difference labels, without the five-ring pool, without a single cation, with the parity-odd factor of
TASKS 52 off. Every later read (chain 42's large molecules, the anharmonic step, the comparison with experiment) runs on the carried network,
and after the compute stop of 15 November a design error can no longer be repaired with a server run. Version 1.3 is chain 35 (chain 34's
recipe on analytic labels) if its read carries it (design note of 5 Oct, correction of 26 Oct). Version 1.4 is the recipe that carries
everything learned since, with its hyperparameters chosen by a registered search rather than inherited.

## 2. What is fixed (design decisions with evidence, not tuned)

| choice | evidence |
|---|---|
| hybrid pair head on pattern f, ΔH = Bᵀ ΔF B, SQM-like class scales, pair features | E7 (23 Sep): couplings learnable only in local coordinates; rung C (1 Oct) |
| equivariant body, sum aggregation, fresh (no QM9 pretraining) | rung C C2 incident (28 Sep); the pretrained body superseded |
| family-balanced K-diagonal term (mode 'family') | chain 34 beat chain 24 on every family of both hold-outs (decision 57, 4 Oct) |
| analytic training labels | chain 35h2 (17 Oct): lower on every quantity of both hold-outs; chain 35's full read decides the size of the gain |
| early stopping on a validation set, best epoch recorded, a rerun when the best epoch is within 10 % of the cap | decision 51 |
| charge-state input | pool 3 (decision 54); `design_check.py charge_rows` refuses cations without an index; smoke of 3 Oct |
| parity-odd factor on mixed-parity pairs **on** | TASKS 52: the head breaks σ_h without it (up to 2.4 cm⁻¹ in-plane/out-of-plane couplings on the anchors against ≤ 0.19 true); exact to 1e-15 with it. Screened once against off (§4) so its cost in accuracy is measured, not assumed |
| the target (projected or ridge) | chain 44's registered read (TASKS 66), if it has run; otherwise a categorical of the search — open point (b) |

## 3. The data

Training pool: the corpus rows with analytic labels in layers A, A2 (with the five-ring children of chains 40/40b), B, P3 neutrals (aza
four-rings, cyclopenta-fused five-rings) and P3c cations (charge input) — 1,236 folders on 26 Oct, the exact count after the test sets are
taken out is printed by step 0. Rung 4 is not in it (dropped 17 Oct, decision 63; TASKS 124). Never in training **or selection**, frozen and
hashed by step 0 before anything trains: hold-out (a) (the E6 split), (b) (`corpus/holdout_b_frozen_2026-10-08.txt`), (c)
(`corpus/holdout_c.txt`, the parents of pool 3's families, three cations among them), chain 41's s5/s4N, chain 42's four shape molecules and
lever 5's molecules, and the rung-4 test list. Molecules whose labels failed on the label server train on FD labels and are named.

## 4. The search: hyperparameters we do not know

**What is known and what is not.** The carried values (lr 3e-4, body 3 × 64, head hidden 256, weight decay 1e-4 fixed in the code, K-ring
weight 0.3, K-diagonal weight 0.1, epochs 200 with patience 20; `probes/chain_runner.py` RECIPE_V11, `m05/rungC_train.py` AdamW line) were
never searched for the hybrid head at today's pool size. The only searches were on the Cartesian head at 175 molecules (27 Sep: lr 1e-3 with
200 epochs best, 3e-3 diverged) and the loss-weight ablations 34b/34c (no response). Pool size changes the best capacity and regularisation, so
the values of September are a starting point, not an answer.

**Selection never touches the hold-outs.** Choosing on (a) or (b) would make their numbers optimistic and void the read. A *selection set* is
carved from the training pool, ~15 %, **grouped by parent scaffold** (the unit hold-out (b) is split by), fixed by a seed and hashed at step 0.
The trainer's inner validation split stays for early stopping only: it is a random per-molecule split, so a molecule's siblings sit on both
sides and it rewards memorising a family, which is not the generalisation the hold-outs test.

**Selection score and the no-worsening rule.** The registered read-outs (E6.readout, as on the hold-outs) on the selection set, each
divided by its line (the four families' diagonal rms by 3 cm⁻¹, the coupling ratio by 0.25), averaged: one number in which 1.0 means 'on
the lines'. **A configuration is eligible only when none of the five is worse than the control's** (the user's rule of 26 Oct, decision
57's amendment); the score ranks the eligible ones. The worst of the five and the cation rows' score are reported beside it.

**Space** (bounded by the evidence above; log scale where marked):

| hyperparameter | range | carried |
|---|---|---|
| learning rate | 1e-4 – 1e-3, log | 3e-4 |
| weight decay | 1e-5 – 1e-3, log | 1e-4 |
| body width × blocks | {64, 96, 128} × {3, 4} | 64 × 3 |
| head hidden width | {128, 256, 512} | 256 |
| K-ring weight | 0.1 – 1.0, log | 0.3 |
| K-diagonal weight | 0.03 – 0.3, log | 0.1 |
| epoch cap / patience | 300 / 20 (decision 51's rerun rule guards the cap) | 200 / 20 |

Kept fixed: AdamW, one molecule per step, gradient norm clipped at 5, inner validation 15 %. A learning-rate schedule is a candidate for a
later version, not v1.4 (it needs code no run has used).

**Method: random search on a frozen list, then confirmation with seeds.** Random search beats a grid when only a few of the dimensions matter
(Bergstra & Bengio 2012), and a list drawn once with a fixed seed and committed before the first training leaves no room to steer the search
by its own results. Stage 1: the carried configuration (the control) plus 24 drawn configurations, one seed each, the full pool, with the
parity factor on; plus the control with the parity factor off (the one ablation). Stage 2: the best four of stage 1 by selection score and the
control, three seeds each (stage 1's seed reused). Stage 1 screens on one seed, so its no-worsening filter is noisy: it ranks by score and
reports the filter; the filter decides in stage 2. **The winner** is the eligible stage-2 configuration (no seed mean of the five above the
control's) with the lowest mean selection score — and it replaces the control only when its advantage exceeds twice the combined standard
error of the two seed means; otherwise the control's values stay (the simpler choice when the data cannot tell). Stage 2 also trains the
winner with the target chain 44 did not choose (three seeds), so the target choice is checked at the winning hyperparameters. Every
stage-1 and stage-2 score is reported, including the losers.

**Price.** Chain 41's size arm trained 972 molecules in 3,778 / 7,011 / 5,796 s per seed on 8 threads (`out/E7_rungC_chain41_size.json`), ≈ 1.6 h;
at ~1,200 molecules ≈ 2 h per training. Stage 1: 26 trainings ≈ 52 h; stage 2: 10 new trainings and 3 for the target check ≈ 26 h; the read: minutes. About three
laptop days, one training at a time (peak ≈ 7.7 GB against the 13 GB budget). Free of charge: the laptop.

## 5. The read and the promotion

The winner's three stage-2 models are the version 1.4 candidates, read once on every frozen test set: (a), (b), (c) (cations separately),
chain 41's s5/s4N, and beside them the selection score. Promotion by decision 57 with its amendment of 26 Oct against the carried version
at that moment (1.1, or 1.3 if chain 35 carried): no seed mean of the five above the carried one's on either hold-out and at least one
below → carried as 1.4; otherwise the per-quantity table goes to the user. The comparison reuses `probes/chain35_read.py`'s logic, moved into one shared module (one implementation). **Predictions,
written before any number:** the search moves the hold-outs less than the data does — most of v1.4's gain over 1.1 comes from the analytic
labels and the added rows; the winner's hyperparameters differ from the carried ones in learning rate and capacity more than in the loss
weights (34b/34c found no response there); the parity factor costs less than the seed range.

## 6. The CC transfer's hyperparameters

The whole-head fine-tune (TASKS 130: the fit mode since 26 Oct) runs at 300 epochs and lr 1e-3, values of 7 Oct. They are chosen on the
proxy check's tasks (distorted DFT standing in for CC; `m05/proxy_transfer_check.py`, the PX design of 21 Oct), never on the eleven real
anchors, which are the test: a small grid (epochs {100, 300, 1000} × lr {3e-4, 1e-3}) on arm (a), read on its CH-oop and intensity
numbers. Registered separately, after v1.4's stage 1.

## 7. Code before the runs (on a branch in its own worktree, merged after chain 35 has run)

1. `rungC_config.TrainConfig`: `weight_decay` as a validated field (default 1e-4, the carried value; today a literal in the AdamW line), and
   TASKS 72 step 4 — the defaults become the carried recipe, the 27 Sep recipe a named preset — once no queued chain relies on a default.
2. The selection set: `--selection-split <seed>:<fraction>` grouped by parent scaffold, its ids hashed in the record, and a `selection` block
   per seed with E6.readout's numbers; refused together with `--overfit-one` and the like before loading.
3. `probes/v14_search.py plan|read`: draws the frozen list (numpy seed, sha256 of the list in the registration), writes stage 1's and stage
   2's chain files, reads the scores and applies the winner rule; tested on synthetic records (every branch, ties, the two-SE rule).
4. The shared promotion read (from `chain35_read.py`), used by chain 35 and by v1.4.
A regression pin first: the trainer with the carried recipe and no new switch must give the current record to the bit.

## 8. The user's answers (26 Oct 12:1x)

(a) 'Een nieuwe versie mag geen van de vijf verslechteren' — the no-worsening rule of §4 and §5, decision 57's amendment; the averaged
score ranks what passes it. (b) Chain 44 kept, first after chain 35 (it fits the wait for the cation labels and answers its own size
question); stage 2 checks its target at the winning hyperparameters. (c) The budget agreed. (d) The order agreed: chain 35's read →
the code of §7 merged → chain 44 (Wed 28 – Thu 29 Oct) → stage 1 from the cation fetch (≈ Thu 29 Oct evening, ≈ 52 h) → stage 2
(≈ 26 h) → the read ≈ Mon 2 Nov → chain 42 after lever 5.

### The open points as they were put

(a) The selection score: the mean of the five line-normalised read-outs (proposed), or the worst of them. (b) The target: wait for chain
44's registered read (≈ 36 laptop hours, 18 trainings) and take its winner, or fold projected/ridge into the search as a categorical and
close chain 44 with a marker. (c) The budget: about three laptop days as above, or fewer configurations. (d) Order on the laptop after
Wednesday: chain 35's read → code (§7) → chain 44 if kept → v1.4 stage 1 when the cation labels are in (the CCX53's cations ≈ 29–30 Oct).
