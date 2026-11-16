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

## 9. Amendment, 26 October 2026 12:3x — what building the code showed (before any number)

1. **The parity-odd factor and rung B's pair features do not combine** (`rungC_config`: the pair features carry signed primitive values,
   which are parity-odd), and the carried recipe uses the pair features. 'Parity factor on' (§2) is therefore not a fixed choice but a
   categorical of the search: the control is the carried recipe (pair features), `c01_control_parity` the same values with the parity
   factor and without the pair features (the one ablation), and each drawn configuration takes one of the two by a fair coin. The
   no-worsening rule decides between them like any other hyperparameter.
2. **The pool** is layers A, A2, B, P3 and P3c (`--pool-layers A,A2,B,P3,P3c`); on 26 Oct 15 of the 60 cations carry both analytic
   labels, about 29 after the CCX53's fourteen are fetched. Cation rows without analytic labels train on FD as the loader does.
3. **Fixed numbers:** search seed 20261026, selection set `26:0.15` (seed 26, 15 % of the pool by whole scaffold cores), epoch cap
   300, patience 20. The target (projected or ridge) is part of every configuration, so the frozen list and its sha256 are written by
   `probes/v14_search.py plan --target <chain 44's choice> --carried-models <three checkpoints>` after chain 44's read, before the first
   training; the carried version's checkpoints are named in the same file.
4. **The cation number** of §4 is the per-molecule corrected ω rms of the cation rows in the selection set against the neutral rows:
   the trainer's per-molecule record carries no per-family diagonal.
5. **The code** (branch `v14-search-code`, merged after chain 35): `--weight-decay`, `--selection-split`, `probes/promotion_read.py`
   (shared with chain 35's read), `probes/v14_search.py`; the stage chains and runspecs are written by the reads themselves.

## 10. Amendment, 12 Nov 2026, 21:3x — the target is a categorical of the search (before the frozen list is written)

The user, 8 Nov ('bij 3 de verkorte route'): no separate chain 44; projected and ridge become a categorical of the search (§8's option (b)). `probes/v14_search.py`: the control keeps the carried target (projected); a second one-factor ablation, `c02_control_target`, is the control with the ridge target (`--aux-target ls`); each drawn configuration takes its target by a fair coin of its own generator (seed 20261027), so every other drawn value is what it was (tested); the drawn configurations are named from c03. The list is 27 configurations (stage 1 ≈ 54 h). `plan` no longer takes `--target`. Stage 2's target check stays: the winner is also trained with the other target (three seeds), so the choice is checked at the winning hyperparameters. The search runs on the corpus with the 222's labels merged (TASKS 171).

## 11. Amendment, 15 Nov 2026, 19:2x — the search's power, the schedule, the repaired labels (before the frozen list is written)

The user, 15 Nov, asked before the launch whether the search was world class, and on the answer: 'Verbeterd, leersnelheid moet altijd
onderdeel zijn van onze zoektocht. Start zodra het kan.' and 'Ja, v1.4 op de gerepareerde labels.' No configuration has been drawn into a
file and no v1.4 training has run; `out/v14/` does not exist.

**What was weak.** The registration's care stands (a frozen hashed list, a scaffold-grouped selection set, the control, the no-worsening
rule, two SE, the losers reported). Its power did not: stage 1 ranked 27 configurations on one seed while v1.3's three seeds differ by up
to 0.8 cm⁻¹ within a family on hold-out (a) (CH-stretch 0.91 / 1.74 / 0.91, 'other' 4.09 / 3.27 / 3.51; `out/E7_rungC_chain35_analytic_a8read_seed*.json`);
24 points covered seven ranges and two coins; the learning rate was constant although chain 35's best epochs were 101, 162 and 198 of a cap
of 200 (`out/E7_rungC_chain35_analytic.json`); and two of the seven ranges were the loss weights, on which 34b/34c measured no response and
§5 predicts none.

**What changes.**
1. **The learning-rate schedule is a categorical of the search**: `constant` (the carried recipe) or `cosine` — a linear warm-up over five
   epochs, then half a cosine from the drawn rate down to 1 % of it at the epoch cap (`rungC_config.learning_rate`, `--lr-schedule`). A new
   one-factor ablation, `c03_control_schedule`, is the control with the cosine. The rule from now on: the learning rate, its value and its
   schedule, is part of every search of ours.
2. **The two loss weights are no longer drawn**: every configuration carries the control's (K-ring 0.3, K-diagonal 0.1).
3. **Stage 1 trains two seeds of every configuration** (0 and 1) and ranks by their mean score; stage 2 adds the third seed (2) for the
   best four and the control, so the winner rule still reads three seeds. The list is 16 configurations — the control, its three ablations
   and 12 drawn (named from c04) — and the price is what §10's was: 32 + 5 + 3 trainings against 27 + 10 + 3.
4. **The three two-valued choices of a drawn configuration (parity or pair features, target, schedule) are dealt as one design**, not
   by fair coins: the eight combinations and the half fraction in which an even number of the three differ from the carried value,
   shuffled once (seed 20261027). Every value comes six times and every pair of two choices' values three times. With twelve
   configurations the coins gave ten of one target. Seen on the list alone, before any training; the drawn ranges keep seed 20261026.
5. **A cosine configuration trains every epoch of the cap** (`--patience 300`: never stopped, the best state on the inner validation
   term restored at the end). The carried patience of 20 would end it near epoch 120–180, as chain 35's constant-rate seeds ended, with
   the rate still at 0.35–0.67 of its value: a warm-up and a mild decay, not the anneal the schedule is. **Decision 51's cap rule is
   the constant rate's**: under the cosine the rate reaches its floor at the cap by construction, so a late best epoch is the schedule
   working, and a higher cap would be another schedule, not a rerun; the reads mark such a seed LATE and refuse nothing. A cosine
   training therefore costs about 3.5 h against 2 h, and the search about 100 h instead of 80.
6. **Each seed of stage 1 is a step of its own** (records `…s1a_…` for seed 0, `…s1b_…` for seed 1), every configuration's seed 0
   first: a restart loses one training, and the first pass is a complete one-seed ranking should the laptop stop there.
7. **The winner rule's bias is named.** Two of a candidate's three seeds are the ones stage 1 chose it on and the control was not
   chosen, so the two-SE comparison flatters a candidate. read2 prints seed 2 alone beside the mean, and the promotion of §5 on the
   hold-outs, which no selection touched, stays the guard. Three fresh seeds in stage 2 would remove the bias for ten more trainings;
   that is the user's to ask for. **The user, 16 Nov 2026: not asked for** — stage 2 adds seed 2 only; the hold-outs are the guard.
8. **The labels.** The search trains and selects on the corpus as it stands after the low-mode repair's swap of 14 Nov (TASKS 201, 216)
   and with the 222 pool molecules' analytic labels merged (TASKS 171). The hold-out labels are repaired too, so the promotion compares
   like with like only because the final chain reads the carried version's three checkpoints again on the same folders
   (`_write_final_chain`: `eval_carried_seed*`); v1.3's published numbers (1.77 / 2.12 …) are not the comparison.

**What does not change.** The space's ranges for the learning rate, the weight decay, the body and the head; the selection set (`26:0.15`),
the pool layers, the epoch cap and patience; the score, the no-worsening rule, the two-SE winner rule, the target check at the winner and
the promotion of §5. One change per version (the user, 30 Oct) is kept in this sense: the schedule is a setting the search chooses, the
network's parts are v1.3's with what §2 already added; v1.5 remains the order-free inputs alone.

**Predictions, written before any number.** The cosine control (c03) beats the control on the selection score by more than their seed
spread; the winner, if there is one, carries the cosine; the seed spread of a cosine configuration is smaller than a constant one's;
capacity matters less than the schedule. If c03 does not beat the control, the plateau seen in chain 35's best epochs was noise in the
inner validation term and not a rate that stayed too high.

**Reviewed before the list was frozen** by an independent reader (15 Nov, 19:4x), whose findings are points 4 to 7 as they stand: the
first draft kept patience 20 under the cosine, shuffled the three choices separately, trained both seeds in one step and did not name
the winner rule's bias. The 222's labels need the low-mode repair before the search (they were made with the code of 7 Nov).

**Not in this version, named for the next search:** stopping poor configurations early (successive halving; it needs a resumable
checkpoint), scaffold-fold cross-validation of the selection score, a batch size above one, an averaged copy of the weights.

**The code** (branch `v14-search-power`, in its own worktree): `rungC_config.py` (`lr_schedule`, `learning_rate`, the refusal of a cosine
no longer than its warm-up), `rungC_train.py` (the epoch's rate, the record's `lr_schedule`), `probes/v14_search.py`, their tests. The
trainer's pin was rewritten: with the new key `lr_schedule` removed it equals the old pin entry for entry, every weight digest included.

**The list is frozen: 15 Nov 2026, 21:5x, before the first training.** `out/v14/configs.json`, 16 configurations, sha256
`1d4887457642e49b109f266a669f4abb0029c09686b38f6a790e7c406a6719e8`; the carried version named in it is chain 35's three checkpoints
(`out/E7_rungC_chain35_analytic_model_n750_seed{0,1,2}.pt`). The corpus it runs on: the 222 pool molecules' analytic labels merged at
21:2x by a checked copy (`probes/labels_merge_checked.py`; 888 files, every `geometry.json` byte-equal;
`probes/results_m1/labels_server_final_2026-11-15/merge_fd222.json`), and the two of them with a label mode below 20 cm⁻¹ repaired and
swapped (B_2804096c51 B3LYP 15.75 → 19.90, ωB97X 63.13 → 65.90 cm⁻¹; B_6c1f2b1966 9.27 → 7.64, 49.57 → 49.16; the largest change
outside the repaired mode 0.113 cm⁻¹ against the registered 0.5; `probes/results_m1/low_mode_swap_fd222_2026-11-15/swap.json`, the
originals under `corpus/superseded_2026-11-15/`). Smoked first on that corpus: c03_control_schedule and c04 through the trainer's
`--smoke` at an epoch cap of 7 (mechanics only). The run spec the search writes asked for a progress gap of 180 minutes against the
schema's 120; corrected in `probes/v14_search.py` with a test, and in the stage-1 run spec — the list itself was not touched.

## 12. Amendment, 16 Nov 2026, 12:1x — the promotion is read on the winner retrained on the whole pool (after data)

**This amendment is written after data.** Stage 1 is running. On 16 Nov the five finished trainings of seed 0 (c00 to c04, records
`…s1a_…`) were read on hold-out (a), read-only, beside v1.3's three checkpoints (`probes/results_m1/v14_holdout_a_look_2026-11-16/`).
§5 says the hold-outs are read once, for the winner and the carried version; that look came before the winner exists, and what follows
was decided knowing its numbers. No whole-pool training has run and no promotion has been read.

**What was seen.** Biphenylene (A_72b86c2331, one of hold-out (a)'s ten molecules) reads a corrected ω rms of 7.03 to 10.35 cm⁻¹ in the
five trainings (9.57, 7.03, 10.35, 9.60, 9.51) against 1.38 to 2.27 for v1.3's three seeds (2.24, 2.27, 1.38). Hold-out (a)'s
corrected ω rms is 3.10 to 3.87 in the five against 2.10 to 2.36 for v1.3 (`compare_holdout_a.txt`). All five configurations show it,
the control included.

**The cause.** The selection split (`26:0.15`) sets 169 molecules of 18 whole scaffold cores aside and leaves a pool of 913, of which 911 are
trained on (two twins of hold-out molecules are dropped after the split; the checkpoints are still named `n913`). One of the
18 cores is biphenylene: all 8 biphenylene derivatives are in the selection set and none is trained on, while the carried version
(chain 35) trained on 7 of them (`relatives.txt`). The same table shows biphenyl (19 derivatives in the selection set, 19 in v1.3's
pool) and phenanthrene (16 against 12), both hold-out (a) molecules too. The ranking of the configurations is not touched: every
configuration trains on the same 911. But the promotion of §5 compares the winner's stage checkpoints with a carried version that saw
those derivatives, and the no-worsening rule would refuse the winner for the split, not for its recipe.

**What changes.**
1. **The final chain trains the winner's recipe again on the whole pool**: the same trainer command without `--selection-split`, seeds
   0, 1, 2, records `…s3full_…`. Early stopping uses the trainer's inner validation split, as in every training. A step `register`
   then enters the chain's six new checkpoints in the model registry as `candidate`: the evaluator stops on a model the registry does
   not know (decision 55), and the first version of this amendment had no such step.
2. **The promotion is read on those three models.** `eval_winner_seed*` evaluates the whole-pool checkpoints, not the stage checkpoints.
   read3 refuses a winner eval whose checkpoint was trained with a selection split, or that is not the winner's whole-pool checkpoint
   of that seed: it reads the checkpoint's name from the eval record and the split from the trainer's record beside the checkpoint.
3. **Decision 51's cap rule covers the whole-pool trainings**, as read2 applies it to the winner: read3 refuses a constant-rate model
   whose best epoch lies within 10 % of the cap and marks a cosine one LATE. The case is not remote: the constant-rate best epochs
   seen so far are 205, 149 and 214 of 300 on 911 molecules (c00, c01, c02, seed 0), the threshold is 270, and the whole pool is
   18.6 % larger. The way out is fixed here, before any whole-pool training: a recorded amendment to this note and a whole-pool rerun
   of the same recipe at a cap of 450 epochs, nothing else changed. The epoch cap is a constant of the search and the final chain is
   written once, so nothing but such an amendment reruns it; read3's refusal names this route.
4. read3's report says in one line that the winner was retrained on the whole pool and why.

**What does not change.** The frozen list and its sha256 (§11); the selection rule and the selection set; stages 1 and 2, their chains
and their records (the stage-1 chain comes out byte for byte from the changed code, pinned by a test); the score and the two-SE winner
rule; the target check, which stays a selection-set comparison of two arms trained with the split (the winner's three stage seeds
against the other target's three); the no-worsening rule of §5 and its thresholds; the carried version's three checkpoints, read again
on the same hold-out folders.

**The price.** Three more trainings. Stage 1 measures 2.3 h for a constant-rate training and 2.8 h for a cosine on 911 molecules;
the whole pool is 1,080, so by the pool ratio a whole-pool training takes about 2.7 h (constant) or 3.3 h (cosine): about 8 laptop
hours for a constant-rate winner and about 10 for a cosine. The run spec of the final chain states three trainings at the search's
planning figures (2 h, 3.5 h), three at 1080/911 of them, and an hour for the evals.

**The caveat that stays.** The whole-pool models trained on the selection set, so they have no untouched selection score, and read3
prints none. The two hold-outs are the only read of them. The recipe was chosen on 911 trained molecules and is applied to 1,080
(the whole-pool checkpoints are named `n1082`, the pool before the same two twins are dropped); that it
carries over is assumed, not measured. And the look at hold-out (a) is on the record above: the amendment changes what the candidate
trains on, not which configuration wins or what it must reach.

**Expectation, written before any whole-pool model exists.** The user, 16 Nov: 'als er niets extra's geleerd wordt, dan is er iets
aan de hand'. The whole pool is 1,080 molecules against the carried version's 750. In the five seed-0 stage trainings (911 molecules)
hold-out (b) already reads a corrected ω rms of 2.18 to 2.65 cm⁻¹ against the carried version's 2.85 to 3.24, and hold-out (a) without
biphenylene 1.94 to 2.59 against 2.03 to 2.25 (`probes/results_m1/v14_holdout_a_look_2026-11-16/holdout_a_without.txt`). Expected of
the whole-pool winner, on the mean of its three seeds: hold-out (b) below the carried version, hold-out (a) not above it. If (a) is
above, it is looked at per molecule before the promotion is decided either way. read3 prints the two means for both versions and says
whether the expectation held; it decides nothing, the no-worsening rule does.

**Prediction, written before any whole-pool training.** Biphenylene's corrected ω rms on the three whole-pool models lies nearer the
carried version's 1.4 to 2.3 cm⁻¹ than the search's 7.0 to 10.3. The statistic: the mean over the three whole-pool seeds of the
corrected ω rms of A_72b86c2331 on hold-out (a), from the eval records' per-molecule read-out. The line: at most 4.7 cm⁻¹, halfway
between the two ranges. read3 prints the per-seed numbers and the mean for the winner and the carried version, with PASS or FAIL. If
it fails, the promotion is read as it is; the cause named here is then not the whole story, and it is looked at before any further
amendment.

**The code** (branch `v14-final-full-pool`, in its own worktree, not merged when this was written): `probes/v14_search.py`
(`trainer_argv`'s keyword `selection_split`, `_write_final_chain`, `whole_pool_reads`, `prediction_read`, `cmd_read3`) and
`tests/test_v14_search.py`. An independent reader reviewed the first version of this section and its code (16 Nov): the pool sizes,
the price at the whole pool's size, the way out of the cap rule and the closed prediction above are that review's findings.

## 13. Amendment, 16 Nov 2026, 12:3x — the score is read on the selection set without biphenylene (after data)

**This amendment is written after data**, the same data as §12: the five finished trainings of seed 0 (c00 to c04), looked at
read-only (`probes/results_m1/v14_holdout_a_look_2026-11-16/`: `sel_by_core.txt`, `sel_sensitivity.txt`). Stage 1 is running; read1
has not run and no configuration has been ranked. The user decided on 16 Nov: the score that picks the winner is read without the
scaffold core biphenylene; only biphenylene.

**What was seen.** Biphenylene is the only four-membered ring in the corpus. The split put all 8 of its derivatives in the selection
set and none in the pool, so no configuration can learn it. The control's corrected ω error on those 8 is a median of 9.46 cm⁻¹ (the
largest 12.66) against medians of 1.3 to 3.8 for every other core of the selection set but fluoranthene (7.39 on 3 molecules). The 8
are 5 % of the set and carry 25 to 39 % of its squared frequency error in the five trainings, and the order of the five changes with
them. Per-molecule corrected ω rms over the selection set, with and without biphenylene:

| configuration (seed 0) | all 169 | without biphenylene (161) | biphenylene's share of the squared error |
|---|---|---|---|
| c00_control | 3.64 | 2.96 | 37 % |
| c01_control_parity | 3.77 | 3.34 | 25 % |
| c02_control_target | 3.90 | 3.13 | 39 % |
| c03_control_schedule | 3.58 | 3.06 | 30 % |
| c04 | 3.83 | 3.28 | 31 % |

**The caveat of that measurement.** It is on the corrected ω per molecule. The registered score — the mean of the four families'
diagonal rms and the coupling ratio, each over its line — was not recomputed without biphenylene: the stage records hold no
per-molecule family read-outs. That the registered score moves as this table does is expected, not measured; the reads print both
scores, so it will be.

**The rule.** The score that ranks stage 1, picks the winner in stage 2 and reads the target check is the registered formula read on
the selection set without the scaffold core biphenylene: 161 of the 169 molecules. The 8 are the molecules of the records' own
`holdout_sel` whose manifest name is `biphenylene+…`; the code refuses any other count than 8 of 169, so a changed corpus or split
cannot change the rule unseen. Every read prints the registered score, on all 169, beside the scored one, and says in one line what
the registered score would do: read1 whether it sends the same configurations to stage 2 (the same in the same order, the same in
another order, or others); read2 whether the winner rule gives the same winner among the stage-2 candidates, which stage 1 chose on
the scored set (it is not the winner a search run wholly on the registered score would have had); read3 whether the target check
decides the same way.

**How it is read.** The stage records' selection read is over all 169, so each stage checkpoint is read once more, by the evaluator
the final chain uses (`rungC_eval_saved.py --eval-ids-file`; it needed no change, and it refuses a set the model trained on). Each
read (read1, read2, read3) makes the evaluations it lacks before it scores, one checkpoint at a time; a record that exists is reused,
and a record is moved into place only when its evaluation has finished. The stage-1 chain is frozen and running and ends in read1, so
for stage 1 the evaluations can only run there; stage 2 and the final chain use the same path, not chain steps of their own, so
the path read1 has exercised is the only one. Each evaluation also reads all 169, and the read refuses a record whose score on the
169 differs from the trainer's own by more than 0.001: a second route to the registered number. If that check refuses — a label
repaired in the corpus between a training and its read would do it, honestly — the stage is not readable on the changed labels: the
changed molecules are named from the two per-molecule read-outs and the route is a recorded amendment here; the tolerance is never
loosened to let a read through. Before its evaluation a stage checkpoint is entered in the model registry as `candidate` (the
registrar `chain_runner`'s chains use; a model that has a status keeps it), because the evaluator stops on a model the registry does
not know. `python probes/v14_search.py seleval [--only CONFIG]` makes and checks the evaluations of every stage training that has
finished, one line each with its seconds and its difference to the trainer's score: one real evaluation is the smoke run of this path
before read1 needs it, and the rest can be made ahead. Counts: 32 evaluations in read1, 5 in
read2, 3 in read3. The time of one is not measured; an evaluation loads the corpus as a training does and predicts hold-outs (a) and
(b) and the 169, and the search's planning figure for a hold-out evaluation is about 3 minutes.

**What does not change.** The frozen list and its sha256; the split itself (`26:0.15`, the 169, never trained in stages 1 and 2); the
score's formula and its lines (3 cm⁻¹, 0.25); the two-SE winner rule and the no-worsening rule; the stage-1 chain file; §12's
promotion on the whole-pool models, which have no selection score. The 8 biphenylene derivatives stay in the corpus and are trained
on in §12's whole-pool retraining.

**Fluoranthene stays in.** Its 3 molecules read badly too (median 7.39), but 16 trained molecules carry its cyclopenta-fused ring:
benzo[k]fluoranthene (5), aza-fluoranthene-1, -4 and -5 (10) and acenaphthene (1). A configuration can learn the ring from them, so
its error says something about a recipe. No trained molecule has a four-membered ring.

**What this costs in rigour.** A selection rule changed after five of the 32 stage-1 trainings were seen on the set it concerns. What
limits the damage: the excluded molecules are named by a structural fact fixed before any training (the one four-membered ring, all
of it in the selection set), not by which configuration they favour; the count is fixed in code; the registered score is printed
beside the scored one in every read, so a reader sees what the amendment changed.

**The code** (branch `v14-final-full-pool`, on top of §12's): `probes/v14_search.py` (`EXCLUDED_SELECTION_CORES`, `selection_sets`,
`make_selection_eval`, `scored_read`, the three reads) and `tests/test_v14_search.py`, the evaluator stubbed.

## 14. Amendment, 16 November 2026, 21:0x: v1.4 is the carried recipe on the whole pool; the search goes on beside it

**After data, on the user's word.** The user wants version 1.4 before the weekend before 25 November ('Bij voorkeur voor het weekend
voor de 25e'; then, to this proposal, 'Ja, doe dat'). The search as registered cannot give it: 25 trainings of stage 1 are left, about
6 of stage 2 and 6 of the final chain, some 37 at about 3 h each — the laptop has eight cores and the trainer uses them all, so nothing
runs beside it — which ends on Saturday 21 or Sunday 22 November at the earliest.

**What was seen when this was written** (read-only, seed 0 of seven of the sixteen configurations; `probes/results_m1/v14_holdout_a_look_2026-11-16/`):
on the selection set without the biphenylene core (§13) no configuration is below the control — c00 2.96, c03 3.06, c06 3.13, c02 3.13,
c04 3.28, c01 3.34, c05 3.45 cm⁻¹ (corrected frequencies, per molecule) — while every one of the seven is below every seed of the
carried version on hold-out (b): 2.18–2.69 against 2.85–3.24, and level with it on hold-out (a) without biphenylene: 1.94–2.59 against
2.03–2.25. So what the stage trainings show is the data's gain, not a recipe's.

**The amendment.**
1. The carried recipe — c00_control: the recipe of version 1.3, RECIPE_V11 with the constant rate — is trained on the whole pool
   (1,080 molecules; three seeds) by the final chain's own whole-pool step, built from `v14_search.train_step(control, "s3full",
   "0,1,2", selection_split=False)`; chain `probes/runs/v14_data.json`, run spec `v14_data`. Both arms are then read on the hold-outs
   (`eval_data_seed*`, `eval_carried_data_seed*`).
2. **The promotion is the registered one** (§5; `promotion_read.compare` and `promotion`: worse on none of the read-outs on either
   hold-out, by the registered rule). If it passes, these three models are carried as **version 1.4**. If it does not, nothing is
   carried, and the cause is looked at per molecule before anything else is decided.
3. The search is paused at a step boundary for this and resumes where it stopped (its runner skips finished steps). Its winner, if it
   is not the control, replaces version 1.4 only by the registered route: stage 2, the final chain, read3 — then read against version
   1.4 as the carried version, not against 1.3. If the control wins the search, these three models are the final chain's whole-pool
   models already.
4. Nothing else changes: the frozen list and its sha256, the selection set and §13's score, the lines, the two-SE and no-worsening
   rules, §12's whole-pool retraining for any other winner.

**Stated before any whole-pool model exists** (§12 already says it; repeated because this is now the deciding read): hold-out (b)
below the carried version on the mean of three seeds; hold-out (a) not above it; biphenylene (A_72b86c2331) at most 4.7 cm⁻¹ on the
mean of three seeds, where the stage trainings read 7.0–10.3 without its derivatives and the carried version 1.4–2.3 with seven of them.

**What it costs in rigour.** It is the third amendment after data, and it turns 'the search's winner' into 'the control unless the
search beats it'. The control is the one configuration that was not chosen on any selection score, so no selection bias enters the
promoted models; what is lost is only that a better recipe, if the remaining nine configurations hold one, arrives later as a
replacement instead of first. The licence (decision 65 as amended on 16 Nov) is read on the product's quantity for whichever
version is carried; `probes/product_error_read.py` must be run for the new models before a certificate is made (TASKS 246 (e)).
