# Investigation log, 1 October 2026 — why does every rung-C head stop at a ring-coupling ratio ≈ 0.42?

*The user, 07:5x: "Wees Sherlock Holmes vandaag en onderzoek structureel, een voor een, alle opties die je veelbelovend lijken. Stop niet." This file
is the running log of that day: one hypothesis per row, the test that decides it, the number, the status. Each run is registered in
`PreRegistration_2026-09-25_RungC_Equivariant_vs_Pair_Model.md` before it starts (dated amendments); the ledger keeps the outcomes; this file keeps
the chain of reasoning. Read-outs as everywhere: (a) = hold-out of 10 scaffold cores, ring-coupling ratio against the zero rule, ω = corrected
frequency rms in cm⁻¹.*

## The fact to explain

| model | data | (a) ratio | ω | source |
|---|---|---|---|---|
| pair model, rung B (hand-made features) | 175 | 0.43 | 4.8 | 27 Sep |
| equivariant, Cartesian head (C1, C2) | 175 / 449 / 750 | 0.81 / 0.83 / 0.82 | — | 30 Sep |
| hybrid head, pattern (c), carried recipe | 175 / 750 | 0.43 / 0.431 | 4.44 / 4.30 | 1 Oct 05:0x, 06:1x |
| hybrid head, pattern (d) | 175 / 750 | 0.40 (0.39–0.42) / **0.37 (0.36–0.38)** | 4.7 / **4.00** | 1 Oct 07:3x, 09:0x |
| hybrid head, pattern (f) + ridge target | 175 | **0.33 (0.32–0.34)**, (b) 0.40 | 4.6 | 1 Oct 15:0x |
| **rung B (hand features), pattern (f)** | 175 / 750 | **0.32**, (b) 0.41 / 0.32, (b) 0.43 | 4.5 / 4.5 | 1 Oct 15:4x, 16:3x — flat with data |
| **hybrid head, pattern (f), projected target** | 175 / 750 | **0.28 (0.27–0.29)**, (b) 0.41 / **0.26 (0.25–0.28)**, (b) 0.38 | 4.6 / 3.8 | 1 Oct 18:0x, 23:0x — T1 ratio met at 750 |
| hybrid head, pattern (f), projected, pattern + 0.3 × kring | 175 / **750** | 0.24 (0.22–0.26), (b) 0.37 / **0.22 (0.21–0.22), (b) 0.33**, ΔH 0.14 | 5.0 / **3.5** | 1 Oct 19:5x, 22:3x — **T1's ratio met at 750; ω 3.5 against the ≤ 3 criterion** |

Three heads with different inductive biases, two data volumes, one recipe search: the same floor. Something shared stops them.

## Hypotheses and their tests

| # | hypothesis | test | number | status |
|---|---|---|---|---|
| H1 | the head cannot express the correction (pattern too narrow) | overfit one molecule, 5,000 steps: what remains is expressiveness | benzene: pattern c 0.15 → pattern d **0.02** (ΔH residual 0.079 → 0.007) | **confirmed**: ceiling removed on benzene; 175: 0.43 → 0.40 (edge), 750: 0.43 → **0.37**, ω 4.30 → 4.00, (b) 0.47 → 0.43 — and the data step 175 → 750 moves this head (0.40 → 0.37) where pattern c was flat. Pattern d carried. |
| H2 | the targets are noise (finite-difference Hessians of the corpus deck) | 27 two-route molecules: FD ΔH read as a prediction of the analytic ΔH, `probes/rungC_target_noise_floor.py` | typical molecule **0.07–0.16** (ΔH residual 0.02–0.08); benzene 7.98, pyridine 0.50, one suspect 3.00 — all three carry analytic targets in training (`--use-analytic`) | **rejected as the 0.42**: the noise floor of a typical target is ≈ 0.1 |
| H3 | an input never reaches the network (ablation = dead wire) | sensitivity at initialisation, `tests/test_rungC_input_wiring.py` | H_low → 0 changes the output by 46 % (Cartesian) / 24 % (hybrid); rank-2 rows carry gradient | **rejected**: the ablations are learned indifference |
| H4 | the encoder is the floor: 171k parameters trained from 175–750 molecules cannot form the environment the head needs | (2a) QM9-pretrained mean body under the hybrid head vs a fresh mean body, pattern d, 175; (2b) the same pretraining for 20 epochs (running since 08:04 on six cores, ≈ 13:00); (2c) capacity: deep 5 × 64, wide 3 × 128 | 2a: fresh mean **0.42** (0.38–0.44) vs pretrained mean **0.41** (0.37–0.48), ω 5.6 / 5.3 — within spreads | 2a **flat**; 2b (20 epochs, validation still falling, cap binds) **flat** on d + ridge at 175: 0.46 (0.42–0.50), best epochs 182 / 200 / 116 → chain 15 re-tests on the carried recipe (f) at 300 epochs; 2c queued |
| H5 | the pattern ceiling is benzene-specific | overfit naphthalene, 2-methylnaphthalene, styrene with pattern d; then the least-squares ceiling per pattern (`rungC_pattern_ceiling.py`) and the masked projected target | overfits **0.41 / 0.40 / 0.12**; LS ceiling on pattern d **0.04 / 0.09 / 0.03**; masked projected target **0.38 / 0.42 / 0.17** | **the overfits land on the aux target's own bound, not on the pattern's** → H9 |
| H9 | the pattern term's target (projected truth on the pattern) is the floor of every head | lever 4: `--aux-target ls` (least-squares ΔF on the pattern), 175 then 750 | bound 0.38–0.42 on naphthalenes = the week's floors 0.37–0.43; plain LS target explodes (entries 1e7–1e10; run of 11:21 stopped); ridge-anchored target at λ_rel 1e-3 keeps the projected scale and lowers the bound to 0.25–0.27 | **mechanism found for the bound; as a lever not yet** (rung B on the ridge target 15:1x: B1 0.48 against 0.43 — the pair model cannot use it either): ridge target at 175 reads 0.44 (0.42–0.45) against 0.40 — the better-bound target is learned worse (gap 0.28 vs 0.09 above the bounds); chain 12 (λ 1e-1 / 1e-2, weight 0.3) and chain 9b (pattern f) decide |
| H6 | early stopping cuts the fit (decision 51) | best epoch vs the cap in every record | lever 1 at 175: best epochs 97 / 30 / 140 of the cap 200 (patience 20 on the inner validation) | **not binding** on the cap; seed 1's early stop (30) is the seed with the worse ω — patience is a lever to keep in view |
| H7 | the (a) read-out is dominated by one or two of its ten molecules | per-molecule ratio of the best model on hold-out (a) | chain 2, seed 0: 0.28–0.55 (fresh), 0.12–0.48 (pretrained) over the ten | **rejected**: the spread is across scaffolds, no molecule dominates |
| H8 | the loss is not the read-out quantity | lever 3: `--aux kring`, the term on the ring-mode block of K itself (tested against `k_of`), pattern d, 175, 3 seeds, against lever 1's 0.40 | (a) **0.29** (0.27–0.32) against 0.40, (b) 0.41 against 0.50 — but ω **7.3** against 4.7 and ΔH residual 0.4–1.0 | **confirmed on the ring couplings, refuted as a recipe**: the aligned loss buys the couplings with the rest of the Hessian → lever 3b = pattern term (ridge target) + kring term: (a) **0.28**, (b) 0.41, but ω 6.5 and ΔH residual 0.41 at equal weights (15:4x) → chain 14 searches the kring weight on pattern f |

## The target bounds on the hold-outs (13:2x, `probes/rungC_target_bound_holdouts.py`, `out/rungC_target_bound_holdouts_2026-10-01`)

The read-out a model would get if it reproduced its pattern target exactly — the ceiling of each route on the molecules the runs are judged on:

| pattern | target | (a) ratio | (a) ω | (b) ratio | model reached |
|---|---|---|---|---|---|
| d | projected (registered) | **0.31** | 1.9 | 0.28 | 0.40 at 175, 0.37 at 750 (lever 1) |
| d | ridge λ 1e-3 (lever 4) | **0.16** | 1.0 | 0.15 | chain 7c / 8b |
| f | projected | 0.09 | 0.4 | 0.09 | — |
| f | ridge λ 1e-3 (lever 1b) | **0.03** | 0.2 | 0.03 | chain 9b / 10 |

Reading: on the registered route the model sits 0.06–0.09 above its own target's bound, so the floor of the week was the target by ≈ 0.3 and the model by
≈ 0.07. The ridge target on pattern d halves the bound; pattern f takes it to the noise floor. The ω gap (models 4.0–4.7 against a bound of 1.9) is the
model's, not the target's.

## Targets — proposal to the user (08:1x; the user asked "Wat spreken we af als de target(s)? Wanneer zijn we tevreden?")

Reference points on hold-out (a), proxy targets (ωB97X − B3LYP): zero rule ratio 1.00 / ω 23 cm⁻¹; hand-made pair model 0.42 / 4.8; measured noise
floor of a typical target (FD vs analytic, 24 molecules) **0.11 / 1.5 cm⁻¹** — nothing can be read below that on these targets.

| tier | question | target (hold-outs (a) and (b), 3 seeds, spreads reported) | when |
|---|---|---|---|
| T1 — the network learns the physics | does it beat hand-made features by a margin that is not noise? | ratio ≤ 0.30 and ω ≤ 3 cm⁻¹ at 750, and the 175 → 750 step falls by ≥ 0.05 | this week, laptop |
| T2 — compute helps (the PC question) | does more data keep paying? | learning curve 175 / 449 / 750 fits a power law whose extrapolation reaches ratio ≤ 0.20 (≈ 2× the noise floor) and ω ≤ 2 cm⁻¹ by ≈ 5,000 molecules | after T1 |
| T3 — the scientific goal | does the correction transport to CC level on a molecule the network never saw? | trained on the proxy + the other CC anchors, the held-out anchor's corrected harmonic frequencies within 3 cm⁻¹ rms of CCSD(T) (in-plane modes), against ≈ 10 cm⁻¹ for scaled B3LYP | when anchor set two is complete |

Satisfied = T1 met → T2 designed; T2 met → the PC; T3 met → the mandate's deliverable exists in small. Awaiting the user's word.

*Status 22:3x:* T1's ratio criterion is met at 750 by the carried recipe (0.22 / 0.33, step 175 → 750 falling); its ω criterion is not (3.50 against ≤ 3; one seed 2.94). The network moved with data (175 → 750) where the hand-feature model stayed at 0.32.

## Decisions carried from the day

(filled as they fall)
