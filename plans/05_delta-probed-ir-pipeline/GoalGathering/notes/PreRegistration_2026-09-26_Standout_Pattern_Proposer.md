# Pre-registration 2026-09-26 — standout: the generative pattern proposer, tested as a simulation on the corpus Δ-Hessians

*Written 26 September 2026, 10:1x, before any code of the experiment ran (the user, 10:1x: "Doe het maar zodra je er tijd voor hebt"). The idea is
module 06's original one (Capstone_Mapping.md § Module 06, 6 September; parked note `Standout_2026-09-26_Pattern_Proposal_Generator.md`). Everything
below is fixed now; deviations get dated amendments. Nothing here runs on the laptop beyond a three-molecule smoke; the simulation runs on a rented
machine when one is free. Priority: below the Sunday interim reading, the module-06 notebook run and the Monday package.*

## The question

K_off, the number of off-diagonal coupled-cluster responses a rung spends, is the scarce quantity. The plan spends it by a deterministic, hashed deck
(single-mode ± block first, then two-mode patterns within a frequency band and multi-mode completion patterns, in seeded order). **Can a proposer that
has seen other molecules order the patterns of a new molecule so that the recovery reaches the same residual with fewer responses?** Measured at zero
CC cost, because with the corpus's full Δ-Hessians every pattern response is an exact projection — no new quantum chemistry is needed for the
experiment. The real coupled-cluster responses (anchor, benzene, later the label plan) are the confirmation, not the training set.

## Data (fixed)

- Molecules: every corpus folder with both projected Hessians (`corpus/molecules/*/hessian_{b3lyp,wb97x}.npz`), analytic second route where present
  (as E7 `--use-analytic`), molecules with an imaginary mode excluded (the corpus's rule). On 26 Sep: 229 in layers A/A2, layer B growing (111).
- The object: the mode-basis Δ₂ in dimensionless normal coordinates of the B3LYP modes, Δ_ij = ∂²ΔE/∂q_i∂q_j = L_iᵀ ΔH_mw L_j / √(ω_i ω_j) (E_h),
  i.e. Δ = 2K/HARTREE2CM with K the E5 coupling matrix. Response of a pattern a in mode E: R_s(a) = ½ aᵀ Δ a (`design_row_E` of
  `probes/dryrun_dft_delta_recovery.py`); mode G is not simulated here.
- Splits, hashed by molecule id (sha1, as E6): **proposer training** = 70 % of layers A2 and B; **proposer validation** = 10 % of A2/B;
  **evaluation molecules** = the 42 layer-A parents (module 05's held-out PAH tensors; never in training) plus the remaining 20 % of A2/B. The
  proposer sees, for an evaluation molecule, only what the deck sees: B3LYP frequencies, mode vectors, atom types, F_low pair scalars — never its Δ₂.

## The decks and the recovery (reused, not rewritten)

- **P0, the deterministic deck** = `build_deck` of the dry-run probe (Q_S 1.0; singles in seeded order; two-mode patterns for pairs within 200 cm⁻¹
  and 4M random sparse multi-mode patterns, in a seeded shuffle; 20 % of the off-diagonal patterns held out per molecule, seed 20260906). Its hash
  is recorded per molecule.
- **Recovery** = the probe's stage C: banded ℓ₁ (FISTA) over the diagonal + off-diagonal unknowns, weights from `band_weights` with the w rule,
  λ grid {1e-7, 1e-6, 1e-5, 1e-4}, chosen on the held-out patterns; ρ(n) after every complete ± pair; **ρ_off** (off-diagonal part) as in the probe's
  "K_off at ρ_off ≤ 0.3" line.
- **Proposers** (each produces an *ordering* of the same off-diagonal pattern pool after the mandatory 2M single-mode block; nothing is added or removed,
  so every variant consumes the same candidates and only the order differs — this is what makes the comparison fair and the deck rule intact):
  - **P1, scorer:** a pair model of the rung-B kind (`m05/e7_rungB_pairs.py` features, MLP, trained on the training split's |Δ_ij|) predicts |Δ_ij|
    for the new molecule; two-mode patterns are ordered by predicted |Δ_ij| descending, multi-mode patterns by the **mean** of predicted |Δ| over the
    pairs they touch (amended 10:1x, before any real molecule ran: the registered planted-block test showed that the *sum* ranks broad random
    patterns above the targeted two-mode pattern of the strongest pair; the mean is the expected information per unknown spent); ties by the hashed order.
    The same rule scores P2 and the oracle P3.
  - **P2, generative (the frozen intent):** a conditional VAE over two-mode/multi-mode pattern vectors a (M-dimensional, padded, conditioned on the
    molecule's mode-structure tokens), trained on the *useful* patterns of the training molecules (those whose response explains the most held-out
    residual in a greedy pass); at test time it samples 4M candidates, the acquisition rule ranks the pool by the VAE's likelihood times the
    predicted response magnitude of P1 (expected residual reduction under the structural prior); the ordering is then frozen and hashed *before* any
    response is read.
  - **P3, oracle (upper bound, not a proposer):** patterns ordered by the true |Δ_ij| of the molecule — what a perfect proposer would do. Reported to
    scale the gains; never a claim.
- Noise columns: exact responses (primary) and Gaussian noise per energy with σ chosen so that ρ_noise ≈ 0.05 (the pilot's DFT floor class), same
  seeds for every proposer.

## Read-outs and pass lines (fixed)

Per evaluation molecule and proposer, in mode E: **K_off(0.3)** = smallest n − 2M at which ρ_off(n) ≤ 0.3 on the held-out patterns (primary; the probe's
line), **K_off(0.1)** (secondary), and **n₁₀** = smallest n at which the relative Frobenius error of the recovered off-diagonal block against the true
Δ₂ is ≤ 10 % (truth-based, possible only in a simulation; reported beside the others). Summary: median ratio K_off(P)/K_off(P0) over the evaluation
molecules, with the fraction of molecules improved; three proposer seeds (0, 1, 2); the 42 parents and the A2/B evaluation set reported separately.

| line | what | pass | fail |
|---|---|---|---|
| S1 | P1 (scorer) vs P0 | median K_off(0.3) ratio ≤ 0.80 and ≥ 70 % of molecules improved, on both evaluation sets | ratio ≥ 0.90 or < 50 % improved |
| S2 | P2 (VAE) vs P1 | ratio ≤ 0.90 (the generative model adds something beyond the scorer) | ratio ≥ 1.0: the VAE does not beat the scorer |
| S3 | headroom | P3 (oracle) ratio reported; a proposer that reaches ≤ 1.5 × the oracle's K_off is "near the ceiling" | — |
| S4 | transfer to size | on the parents larger than any training molecule, the P1 ratio is within 0.10 of its A2/B ratio | the gain vanishes with size |

**Predictions on record (26 September, before the export ran).** P0 needs K_off(0.3) of the order of the number of in-band pairs (hundreds of energies
on a 60-mode molecule). P1 halves it on the substituted evaluation set (ratio ≈ 0.5) and gains less on the bare parents (≈ 0.7), because the scorer's
weakest class is the off-diagonal atom-sharing pairs (E11.7). P2 lands between P0 and P1 (S2 fails) at this training size — 200 molecules cannot
teach a pattern VAE more than a scorer knows — and is worth re-testing when layer B has 600 molecules. Oracle ≈ 0.3. With noise, all ratios move
toward 1.

**Verdict rule.** S1 pass → the proposer is a real efficiency lever; the label plan's decks may take the P1 ordering *before the hash* (the plan's own
rule: proposers add or order patterns only before any response exists), announced as a dated amendment of the Ladder. S1 fail → published as the
outcome; the deterministic deck stays. S2 is the module's own question and is reported either way; the rubric is satisfied by the experiment, not by a win.

## Guards

Hashed order recorded per molecule and proposer before any response is read; the proposer never sees the evaluation molecule's Δ₂; the PAH parents never
train anything; three seeds; every number in the report traces to the results JSON; the export script gets a test on a synthetic Δ₂ (a planted
off-diagonal block must be recovered by the deterministic deck within its ρ line) before the real run; the simulation runs on a rented machine, the laptop
sees a three-molecule smoke only; `--dry-run` before every launch; nothing before the Sunday reading is done.

## Cost

Export: seconds per molecule (desk). Recovery curves: a FISTA solve per n step per λ — minutes per molecule; ≈ 80 evaluation molecules × 4 orderings ×
3 seeds ≈ a few CPU-hours on a CPX62, run when one is free (after the layer-B shards or beside them at nice 15). VAE and scorer training: minutes.
Build: two to three days of desk work in quiet hours. Artefacts as for module 06: notebook, report, requirements, design note, this pre-registration's
outcome section.

## Dated amendments before the first real run

- **10:1x — registered export test and three-molecule smoke done** (`tests/test_pp_planted.py`, 5 green; laptop, one thread, seconds). Benzene (M 30,
  334 patterns): K_off(0.3) is 480 energies in the hashed order and 32 in the oracle order — the ordering matters by a factor 15 on one molecule. Two
  small layer-B molecules (M 18, 21): ρ_off never reaches 0.3 with the whole deck (ends 0.44 / 0.56, exact responses), i.e. the *deck*, not the order, is
  the limit there.
- **10:1x — finding that changes a read-out:** across 289 corpus molecules only **≈ 45 %** of the off-diagonal coupling power (Δ₂ at the proxy level,
  ωB97X − B3LYP) lies inside the deck's 200 cm⁻¹ band (median in-band share: A 0.43, A2 0.47, B 0.42; `modules/standout_pattern_proposer/out/inband_share_2026-09-26.json`). The two-mode
  block of the deterministic deck cannot see the rest; the random multi-mode patterns can only under the ℓ₁ penalty. Therefore: (a) **n₁₀ is read on the
  in-band pairs** (primary) and on all pairs (secondary, expected not to be reached); (b) a **second registered experiment E2** is added: the pool is
  widened to two-mode patterns for *every* pair (P0′ = the same construction without the band filter, hashed) and the same orderings P1′/P2′/P3′ are
  compared on that pool, with the band kept only as the solver's prior. E2 answers whether the proposer's real value is choosing among out-of-band
  couplings, which is what the 6 September idea meant by "propose patterns". Pass lines and predictions for E2 as for S1–S4; prediction: the P1′/P0′
  ratio is smaller than P1/P0 (≈ 0.4) because the pool is larger and the scorer's ranking has more to choose from. This in-band share is also a plan-05
  finding in its own right (the Ladder's band prior at the proxy level) and goes to the ledger; it is not judged here.
- **10:5x — P2 redefined as the learned-representation scorer (the user: the idea was to learn the embedding, not prescribe it; "Ik wil wat het beste
  resultaat geeft").** P2 = the rung-C equivariant body (`m05/rungC_equivariant.py`: atomic numbers, coordinates, the registered pair scalars of H_low;
  nothing prescribed beyond O(3) and permutation equivariance) → per-atom features, projected onto the B3LYP modes by their atom participations into a
  learned embedding per mode → a pair read-out predicting log₁₀|Δ_ij|; trained on the training split, selected on the validation split, three seeds.
  **P2b** = the conditional VAE of the original text, optional and only after P2. **P12** = P1 and P2 combined (average of standardised predicted
  log scores) as a third candidate. The order of work and its logic: P1 first (minutes; it measures the gap to the oracle that any learned model must
  close), then P2, then P12; every variant runs on both pools (E1 band, E2 all pairs). Selection is by the validation split only; every variant is
  reported on the evaluation molecules, winners and losers. Predictions added now: P1 closes about half the gap between P0 and the oracle on the
  band pool; on the all-pairs pool P2 beats P1 (ratio P2/P1 ≤ 0.85) because the out-of-band couplings are where learned atom-sharing features matter
  most; P12 is at least as good as the better of the two on both pools. If 300 molecules prove too few for P2, C2-style pretraining on the Hessian
  QM9 set is the registered next lever, not a new architecture.
- **11:0x — compute placement (the user: "Doe het allemaal zo snel als mogelijk zonder een run te schaden").** The export (seconds per molecule) and
  the scorer fits (P1 minutes, P2 ≈ 40 min per seed) run on the laptop on **one thread at low priority** beside the densification (8 of 16 threads busy;
  a single extra thread does not slow it measurably — checked against its heartbeat), the recovery simulation (hours) on a rented CPX62 the user creates.
  The simulation uses ≈ 60 solves per curve (stride adapts to the pool) and the λ grid {1e-6, 1e-5} (the two values the smoke selected), recorded in
  the results JSON.
- **12:0x — fallback read-outs registered before any merged result is read.** The band-pool shards report, molecule after molecule, that ρ_off ≤ 0.3 is
  not reached under P0, P1 or the oracle (the band finding predicted this: half the coupling power is outside the deck's reach). So that the primary
  read-out does not silently become empty: if P0 reaches ρ_off ≤ 0.3 on fewer than half the evaluation molecules, the primary comparison becomes
  **n_half** — the energies beyond the single block at which an ordering first reaches the midpoint between ρ_off after the single block and P0's final
  ρ_off (P0's target for every ordering on that molecule) — with the **AUC ratio** (mean ρ_off over P0's checkpoint grid) as the second line, both as
  median ratios against P0 with the fraction improved, and the same two on the in-band Frobenius column. Pass line S1 then reads: median n_half ratio
  ≤ 0.80 with ≥ 70 % improved; S2/S3/S4 likewise on n_half. `readout.py` computes all of it from the stored curves; the registered K_off levels stay in
  the report wherever they are reached. Prediction unchanged in direction: P1 ≈ 0.5 (band pool, A2/B), ≈ 0.7 on the parents; oracle ≈ 0.3.
- **12:1x — a fair chance for the learned embedding (the user: "waken dat we het leren van de juiste embedding niet te snel afkappen").** No negative
  statement about P2 is licensed by the first run. Before any "the embedding adds nothing" sentence, the registered search runs, in this order, each
  stage read on the validation split and only the chosen recipe on the evaluation molecules: (1) optimiser recipe — learning rate {3e-4, 1e-3, 3e-3} ×
  mode-embedding width {64, 128}, patience 20 instead of 8, up to 300 epochs; (2) target and loss — log₁₀|Δ| (registered) against a rank/Huber
  variant, because the read-out is an *ordering* and a ranking loss matches it; (3) capacity — 3 vs 5 interaction blocks, mode embedding from both scalar
  and vector channels (‖v‖ per channel added to s); (4) data — retrain when layer B passes 300 molecules (the simulation costs no quantum chemistry,
  so this repeats weekly); (5) pretraining — the C2 idea, the body pretrained on the Hessian QM9 set to predict full Hessians, then fine-tuned. The
  first run's P2 (patience 8, ≈ 60 epochs, val MSE 0.33 vs P1 0.36) is stage 0. The same rule as `feedback-no-negative-conclusion-without-search`:
  a flat result under one frozen recipe licenses nothing.
