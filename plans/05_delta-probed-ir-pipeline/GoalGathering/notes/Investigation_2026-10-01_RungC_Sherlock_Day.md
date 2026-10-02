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
| H4 | the encoder is the floor: 171k parameters trained from 175–750 molecules cannot form the environment the head needs | (2a) QM9-pretrained mean body under the hybrid head vs a fresh mean body, pattern d, 175; (2b) the same pretraining for 20 epochs (running since 08:04 on six cores, ≈ 13:00); (2c) capacity: deep 5 × 64, wide 3 × 128 | 2a: fresh mean **0.42** (0.38–0.44) vs pretrained mean **0.41** (0.37–0.48), ω 5.6 / 5.3 — within spreads | 2a **flat**; 2b **flat** on d + ridge (0.46); on the carried support (chain 15c, 2 Oct 00:0x) the pretrained mean body 0.26 / ω 4.7 beats a fresh *mean* body (0.30 / ω 7.0) and equals the fresh *sum* body (0.28 / 4.6) — pretraining repairs a weak start, adds nothing beyond a good body; parked behind ω; **2c (2 Oct 01:2x): wide 3 × 128 works on pattern d — 0.35 (0.34–0.36) / ω 3.7 against 0.40 / 4.7; deep 5 × 64 flat; on the carried recipe (chain 19, 02:4x) the wide body is **flat** — 0.22 (0.21–0.23) / ω 4.9 against 0.24 / 5.0 — width helped only the narrow support; carried body stays 3 × 64** |
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

*Status 2 Oct 01:4x (T2, first curve 175 / 449 / 750 = 0.24 / 0.235 / 0.22, ω 5.0 / 4.6 / 3.5):* ratio factor 1.17 per decade → 0.19 (0.18–0.21) at 5,000 — on the criterion; ω factor 1.69 per decade → 2.4 (2.1–2.8) at 5,000 — misses ≤ 2 (≈ 20,000 at this slope). The ratio's middle point is flat; the composition control (chain 20) runs before the curve is called a law. *Pattern d's curve (chain 6, 03:0x): 0.40 / 0.37 / 0.37 — a step then a flat, the mirror of the carried recipe's; same fitted factor 1.17 per decade. Two one-step curves are not a law yet.* **Composition control (chain 20, 03:0x): 175 B-heavy molecules give 0.275 against 0.24 for 175 A + A2 — the mixed-pool curve conflates count and composition; the 0.19-at-5,000 extrapolation is withdrawn; the curve is redrawn within A + A2 at 45 / 100 / 175 (chain 21).** *Chain 21 (04:1x): 0.29 / 0.25 / 0.24, ω 7.0 / 4.9 / 5.0 — a step to 100, then flat at fixed composition; the 750 gain (0.22, (b) 0.33) comes with layer B's different molecules. T2 restated: data pays through coverage more than count on this corpus; no extrapolation written; the next pool must grow in kind.*

## The ω question, framed (2 Oct 04:1x, from the carried model's record at 750, hold-out (a), mean of three seeds)

| mode family | model diag rms (cm⁻¹) | zero rule |
|---|---|---|
| ring in-plane | **2.4** | 19.7 |
| CH stretch | 3.5 | 43.6 |
| CH out-of-plane | 3.8 | 23.6 |
| other (substituent, skeletal) | **5.0** | 13.2 |

Per molecule (seed 0): 2.2–6.0 cm⁻¹, two molecules at 5.1 and 6.0. The ring block — the read-out the auxiliary terms aim at — is the best family; the ω
rms is carried by the *other* family, whose diagonal entries no term weights (the pattern term standardises them with a floored class scale, the kring
term ignores them). The first registered lever on ω is therefore a diagonal term over all modes beside the ring block (lever 5, `--kdiag-weight`). **Read 05:2x: weight 0.1 at 175 gives ω 2.78 (2.7–2.9) against 5.00, (a) 0.23 unchanged, ΔH 0.144 — T1's ω criterion met at 175; the 750 read is chain 23.**

## Decisions carried from the day

(filled as they fall)

## 2 October, 06:3x–06:5x — levers 1, 2 and 5 built; lever 2's first reading

**Lever 1 (T3) built and registered** (amendment 06:4x in the rung-C pre-registration). `rungC_train.py`: the per-molecule tensor build is
`molecule_tensors(...)`, `--save-model` writes the hybrid model per seed, `load_hybrid_model` / `freeze_for_transfer` rebuild it and leave only the head's
last layer and the SQM α trainable. `m05/rungC_cc_transfer.py`: the four CCSD(T)/cc-pVDZ anchors become the high level of their corpus entry
(`substitute_cc`, the analytic B3LYP as the low level), leave-one-anchor-out with five columns (zero rule, per-class α scaling on three anchors, network
untouched, α tuned, head tuned) and a per-family corrected-ω rms (T3's line reads ring-ip). Six tests; ruff clean; the smoke with a 2-epoch model runs the
four folds in 67 s. What the smoke already shows about the *data*, independent of the model: the zero rule (B3LYP as is) is 54–64 cm⁻¹ rms against
CCSD(T)/cc-pVDZ over all modes, 26 cm⁻¹ on naphthalene's ring-ip modes, 76–98 cm⁻¹ on CH-oop and CH-stretch — the cc-pVDZ CC correction is large and
family-dependent, which is why the line is in-plane. The models for the real folds come from chain 24 (lane A after chain 8b; ≈ 10:00).

**Lever 2 — the error map** (`probes/rungC_error_map.py`; `out/rungC_error_map_2026-10-02.md`, `next_pool_candidates_2026-10-02.csv`). Fifteen
pattern-f hybrid records, per-molecule hold-out errors averaged over seeds and records, kinds from the manifest SMILES. **The error follows the scaffold
size, not the substituent:** benzene 0.11, benzonitrile 0.14, three fused rings 0.20 (phenanthrene 0.21, phenanthridine 0.20), biphenyl 0.24, fluorene
family 0.28–0.39, fluoranthene family 0.34–0.44; within a scaffold the substituent moves the ratio by ≤ 0.1 (fluoranthene bare 0.34, +CF₃ 0.43). ω rms by
kind 3.1–7.5 cm⁻¹. The fluorene and fluoranthene cores are hold-out (b)'s scaffolds by construction (pool count 0–4 for most of their kinds), so (b)
measures transfer to an unseen scaffold — and the pool has almost no four-ring scaffolds at all (two bare, 27 substituted done in A2; 93 four-ring and
441 three-ring A2 rows are *pending*). **Coverage lever named:** the next pool is the pending A2 three- and four-ring rows (pyrene+X, acridine+X,
dibenzofuran+X) before more B rows. The candidate list (200 ids, ≤ 19 heavy atoms): 55 four-ring and 8 three-ring A2 rows, 106 fused two-ring B rows
(the weak 2ar-fused kinds: NH₂, CONH₂, CN, NO₂), 25 single-ring B rows (new substituent kinds), 6 biphenyls. Cost: the corpus route (psi4 FD B3LYP +
ωB97X) ran ≈ 1 h per 12-heavy molecule on the laptop; 200 rows ≈ 10 laptop-days or one CPX62 week — a decision for the user; the list is ready.

**Lever 5 — dipole derivatives, route decided and smoke-tested.** The corpus psi4 outputs carry no dipole derivatives and the installed pyscf-properties
(0.1.0) has no `infrared` module, so the route is central finite differences of the analytic SCF dipole at the corpus's DFT settings
(`probes/dipole_derivs_fd.py`; `mf.dip_moment` as in pyscf's `scf/test/test_rhf.py`). Two routes per molecule: the translation sum rule
Σ_A ∂μ/∂R_A = q·I and two step sizes. **Water, B3LYP/6-31G*:** sum rule 2.5e-6 e (limit 1e-4), |P(h) − P(h/2)| 3.0e-6 e, intensities 79.5 / 2.5 / 23.4
km/mol at 1679 / 3871 / 4000 cm⁻¹ (B3LYP's known pattern for water; 108 s at 4 threads for 18 SCF pairs) — `probes/results_m1/water_dipole_fd_2026-10-02/`.
Cost on the hold-outs: 3N × 2 SCF per molecule, ≈ 30–60 min for a 20-atom molecule at 4 threads; the analytic alternative (the CPHF `mo1` of the Hessian
object, as pyscf-properties' `infrared/rhf.py` does it) is the throughput lever if intensities enter the read-outs for the whole corpus.

**Registered now — the intensity read-out (lever 5, step 2).** For each hold-out molecule with an APT: double-harmonic intensities from the *same*
low-level APT with (i) the modes of the true corrected Hessian H_low + ΔH_true and (ii) the modes of the predicted H_low + ΔH_pred; read-out = the cosine
overlap of the two Lorentzian-broadened spectra (FWHM 10 cm⁻¹, 500–3500 cm⁻¹) and the intensity-weighted rms of the per-mode relative intensity error;
baseline = the zero rule (modes of H_low). Prediction: the carried model's spectra overlap ≥ 0.95 on hold-out (a) where the zero rule sits near 0.85 — the
intensities move mainly through the mode mixing (Duschinsky) that the ratio already measures; the APT's own level dependence (B3LYP vs CC) is a second
term, read later when the E8 probe stores dipoles. First data: the ten hold-out (a) parents on the laptop when a lane frees (chain 23's lane, ≈ 09:00).

## 2 October, 07:3x — the next pool runs (the user: "Reken die 200 kandidaten maar op een CPX62"); the coverage prediction, registered before the data lands

**What runs.** The 200 ids of `out/next_pool_candidates_2026-10-02.csv` (63 three- and four-ring A2 rows, 137 B rows of the weak fused-two-ring and
new single-ring kinds) on the new CPX62 `ubuntu-32gb-hel1-2` (46.62.227.91 — same name as the deleted naphthalene server, different IP), the corpus
route as it was for layer B (psi4 1.11, deck v1: B3LYP and ωB97X/6-31G* FD Hessians at the B3LYP geometry), two runners of 8 threads × 12 GB on two
copies of the corpus dir, each with a cost-balanced half of the ids (`scratchpad/next_pool_ids_{a,b}.txt`; `bootstrap_nextpool_1002.sh`). Expected
≈ 1–2 h per molecule per runner → 4–7 days; results come back through `merge_shards.py` as the layer-B shards did.

**The test this is (lever 2, T2 as coverage).** The carried recipe (pattern f, projected target, pattern + 0.3 kring + 0.1 K-diagonal, 3 × 64 body)
retrained on pool + the 200 (same hold-outs (a) and (b), three seeds; a 750-row control with the same recipe is chain 17/23's record). **Predictions.**
Hold-out (b) — the fluorene/fluoranthene scaffolds, 0.33–0.36 today — falls to ≤ 0.28 because four-ring fused scaffolds enter the pool for the first
time (the error map's gradient: 0.11 → 0.20 → 0.3 → 0.4 with scaffold size); the 4ar-fused kinds in the per-kind map fall by ≥ 0.05 each; hold-out (a)
stays within its seed spread (0.21–0.24). **Lines.** *Coverage confirmed:* (b) ≤ 0.28 with (a) unchanged → the next pools are chosen by scaffold
coverage, and the A2 pending rows (441 three-ring, remaining four-ring) come next. *Count, not coverage:* (b) improves by < 0.03 → the 200 did what any
200 would (compare the 449 → 750 step: 0.37 → 0.33 on (b) for 300 B rows), and the scaffold hypothesis is dropped for the next pool. *Worse:* a
(b) above 0.36 means the new rows carry noise (FD B3LYP: the target noise floor is ratio ≈ 0.1) — check the analytic second route on a sample before
reading further. The error map is rerun on the new records as the mechanical check (`probes/rungC_error_map.py`).

## 2 October, 10:2x — T1 met; the APT route switched to CPHF; the next pool's pace

**T1 met at 750** (chain 23, outcome in the pre-registration): hold-out (a) ratio 0.22 (0.215–0.226), ω 2.82 cm⁻¹ (2.59–2.98), ΔH residual 0.139, best
epochs 79–113 of 200; hold-out (b) 0.33 / ω 3.6. The proposal of 1 Oct asked ≤ 0.25 and ≤ 3 cm⁻¹ on (a): both satisfied by all three seeds on ω except
seed 1 (2.98, within). The remaining gap is (b), the unseen scaffolds — the next pool's question.

**Lever 5, the route changed at 07:4x.** The FD APT loop ran ≈ 5 min per SCF on a 22-atom molecule (6N SCFs → 11 h per molecule) and was stopped by pid;
`probes/dipole_derivs_cphf.py` computes the APT from the CPHF response (`hessian.rhf` `make_h1` / `solve_mo1`, as pyscf's `hess_elec` does, plus the
derivative dipole integrals `int1e_irp`), with the sum rule and the FD APT as the two routes: water 4.6e-7 (sum rule) and **1.3e-5 against the FD
route**, 7 s against 108 s. On the hold-out parents it costs 60–80 min per 22–23-atom molecule at 4 threads beside the two torch lanes (the CPHF with
the xc response at grid 99/590 dominates); A_fdc27f1bd1 PASS 1.8e-5, A_e72997e726 PASS 1.2e-5, **benzene FAIL 1.1e-4** (limit 1e-4, marginal) — the
benzene FD run at the end of the loop measures whether this is CPHF accuracy (then tighten `conv_tol_cpscf` and rerun) or the limit set too tight for a
12-atom molecule's basis. The trainer reads `dipole_b3lyp_cphf.npz` first, FD second; chain 24 (lane A, after chain 8c, ≈ 10:4x–14:00) is the first
record that can carry the intensity read-outs — for the molecules whose APT exists when it starts (three to five of ten); the full set reads from chain 25's
models or a later record.

**Next pool pace (46.62.227.91):** dibenzothiophene+CONH₂ (25 atoms) took 2.0 h on runner b; pyrene+SH (27 atoms) was still running after 4.5 h on
runner a. At 2–4 h per A2 molecule and ≈ 1 h per B molecule the 200 take ≈ 8–12 days on one CPX62, not the 4–7 estimated — the A2 four-ring rows are the
cost. Options for the user at lunch: a second CPX62 for the A2 half (≈ €25 per week), or let it run. Watchdog quiet.

**Chain 8c (d + ridge at 750, the route's last record):** seeds 0–1 (a) 0.60 / 0.46 — the ridge target at λ 1e-3 on pattern d is as bad at 750 as at
175 (0.44); the route stays closed (chain 12's λ 0.1 cell was the only working one, and pattern f + projected beats it).

**11:0x — intensity read-out, first numbers (smoke model, two APT molecules; `probes/rungC_eval_saved.py`).** The zero rule's spectrum overlap is
**0.20–0.28**, not the ≈ 0.85 guessed at 06:5x: with a 10 cm⁻¹ FWHM the 23 cm⁻¹ frequency shift of the uncorrected modes already destroys the
cosine, so the overlap is a frequency-position metric first and an intensity metric second (the 2-epoch smoke model with ω ≈ 6 cm⁻¹ already reaches
0.97 / 0.81). The intensity-weighted relative rms is the intensity-specific number: smoke model 0.29 / 0.17 against zero rule 0.54 / 0.39. The
registered line (overlap ≥ 0.95 for the carried model) stands; the relative rms is read beside it as the quantity that answers the intensity
question. Full read: chain 26 (chain 24's three models on all ten (a) parents once their APTs are in).

## 2 October, 14:1x — chain 24 read; the anthracene lanes relieved

**Chain 24** (outcome in the pre-registration): (a) 0.22 / ω 2.73, (b) 0.34 / 3.6 — T1 reproduced; models saved; intensity read-outs on the two APT
molecules: overlap 0.97–0.99 against 0.24 (zero rule), weighted relative intensity error 0.18–0.23 against 0.47. Chain 25 (T3 folds) started 14:08;
the head fine-tune runs in seconds per fold.

**Anthracene, 14:1x.** No gradient file after 5 h 50 min of lane time (reference: 1.7 h at 16 threads alone; a gradient at 8 threads should take ≈ 3.4 h,
≈ 4.3 h under proportional contention). Four lanes × 8 threads + the two-route check lane × 8 = 40 threads on 32 vCPUs; every process shows ≈ 7 cores
busy, which OpenMP spin-waits also produce — the CPU-hour comparison with the reference says nothing. Action: the check lane's threads reniced to 19
(its work is kept; it yields to the four production lanes); the lanes themselves untouched. If no file lands by 15:30 the lanes are inspected one by one
(pyscf scratch, iteration state); the launch recipe gets the rule *threads ≤ cores including the check lane* either way (TASKS).

## 2 October, 14:2x — T3 read: transfers but short; T3b registered

Three CC anchors plus the proxy-trained network bring an unseen anchor's in-plane ω from 25–28 cm⁻¹ (B3LYP) to **5–6 cm⁻¹** (α-tuned network),
against 6–10 for the SQM-like per-class scaling without a network; the full-head fine-tune overfits three molecules (naphthalene 0.25–0.67 across the
three models). The ≤ 3 cm⁻¹ line is not met (naphthalene 6.0 at best). Outcome table in the pre-registration. Next: T3b (L2-to-proxy regularised head,
chain 27, minutes) and anthracene as the fourth training anchor. The CH-oop and CH-stretch CC corrections (all-mode ω 6–26) are a separate question: the
cc-pVDZ level's own out-of-plane behaviour (R0 deck, 22 Sep) — nothing in the proxy carries it.

## 2 October, 14:2x — lever 3: where a CCSD(T) gradient's time goes (benzene, cc-pVDZ, frozen 6, both (T) C kernels; laptop WSL, `probes/results_m1/cc_timing_benzene_2026-10-02.log`)

| threads | reference gradient total | SCF + CCSD (by difference) | (T) + CCSD lambda | gradient assembly |
|---|---|---|---|---|
| 4 | 402 s | 67 s | 303 s | 32 s |
| 8 | 253 s | 56 s | 175 s | 22 s |
| 16 | 197 s | 49 s | 128 s | 20 s |

Caveat: every run shared the 16 cores with a torch lane (8 threads) and the CPHF APT loop (4), the 16-thread point also with chain 25 — the absolute
numbers are pessimistic, the shape is what counts. **The lambda stage is 65–75 % of a gradient and the part that stops scaling:** 4 → 16 threads gives
2.4× on lambda, 1.4× on SCF + CCSD (already small here), 1.6× on the assembly; the whole gradient 2.0×. On naphthalene (28 min per gradient at 8 threads,
1 Oct) and anthracene (≈ 4 h) the same stage dominates with a steeper N⁷. **Design note.** (1) The lambda stage = the CCSD Λ iterations (pyscf's
`ccsd_lambda`, Python-level loops over the ovvv/vvvv blocks, OpenMP only inside the BLAS calls) plus our (T)-lambda C kernel (OpenMP over ijk, scales).
Two measured options, in order: (a) *more lanes, fewer threads each* — 8 threads give 1.6× the throughput of 16 on this stage per core-hour; anthracene
already runs 4 lanes × 8 (memory ≈ 13 GB per lane, so a CCX53 carries 4–5 lanes at 24 atoms); the rule from today: **lanes × threads ≤ cores including
the check lane**. (b) *the Λ update in C* — the same route as the (T) kernels (PR #3469/#3470 family): the `update_lambda` of `ccsd_lambda.py` spends its
time in `einsum` over the vvvv and ovvv blocks; moving the two largest contractions to a kernel with OpenMP over occupied pairs is the next concrete
code item, measurable on water/benzene against pyscf's own Λ (two routes). Not pursued: DF-CCSD(T) (no gradient path in pyscf), a different CC code
(the probe's two-route checks and gate 1 are built on pyscf). (2) The SCF + CCSD part stays ≤ 25 %; nothing to do there before (b). Lever 3 is read; the
code item (b) sits in the throughput row of TASKS, after the Sherlock day.

## 2 October, 15:0x — T3b read; anthracene's measured pace

**T3b** (outcome in the pre-registration): no λ beats α-tuning on all four anchors (fluorobenzene resists); λ = 1 ties it, is stable on naphthalene and
gives its lowest ratio (0.23). α-tuning stays the transfer recipe; the next T3 read is with anthracene as the fourth training anchor. Incident on the way:
`Path.with_suffix` on a dotted prefix overwrote two cells — `record_paths` by concatenation in both scripts, test added (`test_record_paths_keep_a_dotted_prefix`).

**Anthracene:** first four gradients at 14:42 after **6.65 h each** at 8 threads with 40 threads on 32 vCPUs (reference 1.7 h at 16 threads alone — the
lambda stage at 24 atoms is almost the whole gradient, as lever 3's table says). Ten to eleven gradients per lane → Hessian ≈ 5 Oct morning (the check lane
reniced since 14:13 should shave a little). Rule written: lanes × threads ≤ cores including the check lane; for the next anchor of this size: 3 lanes × 10 + check
lane at 2 on a CCX53, or the check lane after the lanes.
