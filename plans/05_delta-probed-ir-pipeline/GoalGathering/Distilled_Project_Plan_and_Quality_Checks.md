# Distilled project plan and quality checks — Plan 05

Agrees with [Overarching_Goal.md](Overarching_Goal.md), which defines the notation; the Goal
file wins on drift. Opponents: [Frozen_Lines_to_Beat.md](Frozen_Lines_to_Beat.md). Rungs and
stop conditions: [Frozen_Ladder_and_Tolerances.md](Frozen_Ladder_and_Tolerances.md). Costs:
[Compute_Budget_2026-09-03.md](Compute_Budget_2026-09-03.md). Modules: `Capstone_Mapping.md`
— **owed**, written after the Round-7 reviews; references to "the mapping" below are to that
owed file.

**Status.** Draft, 2026-09-03; revised the same day after Round-7 Pass A. Not complete as a
plan. Nothing here is a result.

---

## §1 Claim

A per-molecule pipeline — DFT geometry, analytic DFT Hessian and dipole derivatives, plus a
**probed coupled-cluster correction Δ to the force constants** (Δ₂ on all modes; Δ₃/Δ₄ on the
scored families, from R0 onward), recovered from K local-CC evaluations with frozen correlation
domains — produces IR **band positions** that, on the gas-phase rungs R0–R1, **agree with the
known truth within the stated margin (primary) and beat the frozen lines under the
pre-registered paired comparison (secondary)**; on R2–R3 the beat comparison runs per family
under the Ladder §2 decidability rule (gas-scored families by measured grid; matrix-scored
families behind the M03 gate), all others pre-declared inconclusive. On reach rung R6 —
conditional on B3 — it produces a labelled theory-vs-theory spectrum with an uncertainty
statement that is explicitly an extrapolation. **For every rung that ran, the cost record
(Ladder §1) is part of the claim.** A size claim is made only under Ladder §1's condition.
Intensities are reported, not part of this claim.

If a gate fails, the claim is the fail-closed sentence of §8, not a quieter product.

## §2 Question and positioning

> What does a coupled-cluster correction to the force constants buy, per band, on top of the
> best available DFT-level IR prediction — and how many coupled-cluster evaluations did that
> correction need, per rung and per mode?

| Neighbour | Already does | This plan still asks |
|---|---|---|
| PAHdb v4.00 (line A) | scaled-harmonic breadth to C₃₈₆ | quantify and beat its per-band error |
| Mai 2025 (line C) | MLMD anharmonic to C₂₁₆, T-dependent | beat its *teacher* where lab data exists; meet it theory-vs-theory on reach rungs |
| Lam 2020 (bib 13) | QM harmonic + ML anharmonic, 37 small molecules, RMSD 21–23 cm⁻¹ | CC-anchored, per molecule, at PAH sizes, without relaxing tolerances |
| Ethereal AI (bib 7) | ML-corrected scale factors | reproduce as M04; anharmonicity must beat *corrected* harmonic |
| O1NumHess (bib 23); Sanders et al. (bib 24) | O(1)-gradient / compressed-sensing recovery of a **full** Hessian, DFT level | apply the recovery to the **CC−DFT difference**, extend it to Δ₃/Δ₄, and measure whether K saturates on PAHs — not found in the 2026-09-03 search (Research note §6); Pass B is asked to falsify |
| Hybrid CC/DFT QFFs (bib 14, plan-02 record; bib 27, Crossref) | CC harmonic + DFT anharmonic on small molecules | the same allocation of CC, obtained by probing rather than by a full CC Hessian; whether it holds for PAHs is what Q7's Δ₃/Δ₄ arm and P4(a) measure |
| Plan 04 (git tree, superseded) | the same criterion with a learned per-molecule surface | the same claim at a cost that is measured |

**Not novel:** running DFT/local CC; compressed sensing; GVPT2. **Scored:** the frozen
evaluation contract on a Δ-probed per-molecule pipeline across a declared size ladder, with
the probe count as a reported quantity.

## §3 Levels, anchors and the Δ-probing object (frozen intent; deck hashes at Q0 per rung)

| Item | Choice |
|---|---|
| Geometry, harmonic Hessian, dipole derivatives | DFT (B3LYP-class, basis per rung), analytic; GPU code (GPU4PySCF-class) if the deck names one, CPU otherwise. The *baseline level* and the global part of every spectrum |
| DFT anharmonic constants (cubic, semi-diagonal quartic) | finite differences of the analytic DFT Hessian along the promised families' modes (reduced-dimensionality precedent: bib 28) |
| Anchor level | local CC = **DLPNO-CCSD(T) or LNO-CCSD(T)**, code and thresholds fixed in the deck; **domains and pair lists frozen at the reference geometry for every displaced evaluation**; **licensed by measured deltas, not by trust** (Q6) |
| **Patterns** | a hashed, ordered set of simultaneous multi-atom displacements built so every atom's local displacement space is complete (O1NumHess-class construction, bib 23), plus mode-targeted 1-D/2-D cuts along the promised families' DFT modes for Δ₃/Δ₄. Amplitudes fixed in the deck |
| **Responses** | mode E: the energy difference Δ(E) at the pattern geometry minus at equilibrium; mode G: the components of the gradient difference Δ(∇E). Every response is local CC minus DFT, both with frozen domains |
| **Structural prior** (the promised route) | sparse recovery of Δ₂ in the DFT normal-mode basis: ℓ₁ penalty on off-diagonal elements (near-diagonal prior) plus an off-diagonal low-rank term; parameter-free apart from the regularisation weights, which are fixed in the deck from the dry run. Δ₃/Δ₄ on the scored families by least squares on the mode-targeted responses. "Structural" means it contains no learned parameters; the **learned prior** (M05) replaces the ℓ₁ term by a Transformer prediction and is a bonus arm only |
| **Hold-out and residual ρ** | a fraction f_h of patterns, chosen by the seeded deck rule before any response exists, never enters the recovery. **ρ** = RMS over held-out patterns of (response predicted by the recovered Δ − computed response) ÷ RMS of the computed held-out responses; dimensionless; computed separately for the Δ₂ and the Δ₃/Δ₄ pattern classes. ρ is the error-budget term, the P3 metric and the quantity K is defined on |
| **K** | measured: the smallest pattern count, in hashed order, at which ρ ≤ ρ\* (Ladder §3). Reported in the cost record with mode, prior, ρ\*, wall-clock and probe file. Capped by K_cap (pilot note) |
| **Modes** | E (energies; K = 2M + K_off, where 2M is the diagonal floor and K_off the off-diagonal count that Q8(c) tests) or G (gradients; literature at DFT level suggests ~10² for a full Hessian — bib 23 — which is *not* this project's number). Chosen per rung by the gradient-availability probe; both printed where both exist |
| Anharmonic machinery | route (a) **GVPT2** on DFT-plus-Δ — named r₃/r₄ thresholds, polyad cap, CH-stretch dropped from scored families if the cap is exceeded; route (b) **MD-ACF** on the **defined DFT-plus-Δ potential**: a deck-named DFT-trained potential (its residual printed) plus Δ applied as the quadratic (Δ₂) and targeted cubic (Δ₃) correction in DFT normal coordinates, valid within the probed amplitude, CH-stretch labelled classical — **unavailable unless the deck names that potential**; route (c) CH-stretch never scored at that rung. Raw VPT2 without resonance treatment is forbidden on any promised family |
| Intensities | DFT dipole derivatives; no charge-flux shortcut; **no CC correction to dipoles promised** (conservative; bib 30 is a Crossref record, full text unread) |
| Scale factors | **none on anharmonic output.** A harmonic fallback declares its factor + fit set |
| Emission | tier 1 = published cascade model on our bands, labelled inherited |

## §4 Deviations

A deviation exists only as a dated note committed **before** the affected quantity is measured.
Forbidden without one:

- Loosening any pilot-note number or margin, in either direction, after it is frozen.
- **Writing or amending the pilot note after any local-CC Δ response or any pipeline-vs-lab
  number exists.**
- Re-windowing or re-classing a lab band after a pipeline number for that molecule exists.
- **Adding, removing or re-weighting patterns after any residual is known; choosing held-out
  members after responses exist; writing K before it is measured; raising ρ\* or K_cap; using
  unfrozen domains for a probe.**
- Any lab scoreboard value entering training, validation, stopping, sampling or **pattern
  design** decisions of the pipeline. The **M04 calibrated baseline** is the single declared
  exception (trains on lab residuals by design; leave-molecule-out; recipe frozen; outputs
  appear only as a P2 opponent column and the P5 empirical uncertainty layer).
- Weakening the M04 baseline after the pilot note.
- **The learned prior on any promised rung (R0–R3, R6)** — spectrum, K or cost record; a Q8
  ratio or an R6 sentence that mixes priors or modes.
- Swapping or re-versioning an opponent line after a comparison against it is scored.
- "Beat" language on a reach rung; a scale factor on anharmonic output; a cost sentence
  outside Ladder §1's two forms.
- Starting a B3 job without the budget file's preconditions; starting any reach rung before
  R3 is scored; wording a size claim before Q8(c) has printed at R1→R2 and R2→R3 in mode G.

## §5 Architecture and the one comparison axis

- **Promised pipeline component:** the sparse-recovery solver with the structural prior
  (classical convex optimisation; no neural network on the promised path).
- **Model family for Module 05: Transformer** (equivariant attention over atom / DFT-mode
  tokens) predicting a **prior for Δ₂ blocks** from DFT-level features. Anything outside
  CNN/RNN/Transformer returns to the user before training.
- **The controlled comparison (frozen): learned prior vs structural prior at matched K, on a
  bonus rung (R4 or R5) or on the dry-run corpus.** Same patterns, same held-out set, same
  solver, ≥3 seeds for the prior: does the prior lower ρ at fixed K, or reach ρ\* at lower K?
  The effect size is pilot-note item 5. **No promised spectrum or cost record depends on its
  outcome.**
- Baselines in every comparison table: line A (scaled harmonic), M04 calibrated harmonic, and
  the null rows (§7, P4).

## §6 Training discipline

- **The M05 corpus** = the zero-CC dry-run Δ tensors (DFT-vs-DFT, for as many atlas species as
  the DFT Hessians afford, any size) plus the probed local-CC Δ tensors from the rungs that
  have run. Published (Zenodo DOI, deck hashes) before Module 05 starts. Whether that
  publication satisfies the rubric's "not reused from an earlier capstone project" clause is
  **decided in the mapping** (plan 04's reading-1 / reading-2 logic for M04 is the template);
  nothing here pre-empts it. Splits by molecule and by pattern batch, hashed (Q3). Stopping on
  validation only. Test touched once per pre-registered evaluation.
- The lab scoreboard is outside all of it (Q4).
- ≥3 seeds; mean ± SD; tuning parity between the learned prior and any alternative prior. The
  M04 baseline has its own frozen recipe.
- The M06 generative pattern-proposer (mapping, owed) may propose displacement patterns; every
  accepted pattern enters the hashed, ordered set **before** any response for that rung is
  computed, never after.

## §7 Quality checks and gates

Scripts under `probes/`. A number not printed by a script is not a result.

### Q (integrity, per rung)

| ID | Check | Pass |
|---|---|---|
| Q0 | deck hash: levels, basis, local-CC code + thresholds, **domain-freezing flag, ordered pattern set and amplitudes, solver settings and regularisation weights, hold-out seed and f_h, ρ\*, K_cap** frozen per rung | SHA256 reproducible |
| Q1 | scoreboard reproduction: lab band table regenerated under this plan's hash | matches the pilot note's band list |
| Q2 | timed probes exist for every budget-governed step (machine, date, settings, wall-clock) | printed |
| Q3 | split overlap (molecule and pattern batch) | prints 0 |
| Q4 | lab-leak check: no scoreboard value reachable from any training artifact or pattern-design input of the pipeline; M04 checked for leave-molecule-out instead | prints 0 |
| Q5 | minimum check: converged geometry, 0 imaginary frequencies, 3N−6 modes | pass/fail |
| Q6 | anchor-licence probes: local CC vs canonical and TightPNO vs NormalPNO harmonic-frequency deltas at the licence molecule (+ one R2-size family); normal-mode smoothness (second-difference noise vs step) **with and without frozen domains**; **domain-freezing bias**: at R0, Δ₂ along each mode with frozen domains vs free domains vs canonical | deltas, noise and bias printed; breach **is** Ladder stop 4 |
| **Q7** | **probing licence** at R0 and R1, run **after** the pilot note: (i) recovered Δ₂ (structural prior, at the measured K) vs a directly computed reference Δ₂ — full numerical local-CC Hessian minus DFT Hessian with the same frozen domains, and at R0 also canonical CCSD(T) minus DFT (the only reference independent of the freezing); metric: per-family RMS harmonic-frequency difference; (ii) recovered Δ₃/Δ₄ on the promised families vs finite differences of the reference Hessians along those modes; metric: per-family GVPT2 shift difference; (iii) **discriminability**: the recovered Δ must be closer to the reference than Δ = 0 is, by at least the factor d₇; (iv) **shuffled-probe null**: responses randomly permuted across patterns, recovered by the same solver, must fail (i)–(iii). A **dry-run column** (Δ between two DFT functionals at R0 and at the largest affordable size, reference = direct DFT−DFT Hessian difference) is printed alongside, before the pilot note, as the estimator check | (i) ≤ τ₇,₂ and (ii) ≤ τ₇,₃ per family; (iii) holds; (iv) fails; breach is Ladder stop 4. **At R1 without a canonical arm, Q7 tests the recovery, not the freezing** — that sentence is printed with the result |
| **Q8** | **locality and saturation**, form frozen in Ladder §3: (a) per atom pair, ‖Δ₂ block‖ vs distance, fitted to A·exp(−r/r_c); r_c printed as a measurement; pairs beyond r_max carry ≤ ε₈ of Σ‖block‖²; (b) per scored family, the share of the family's Δ-shift carried by pairs beyond r_max is ≤ ε₈; (c) K(R_{n+1}) ≤ γ·K(R_n), same mode, same prior, same ρ\*, for R1→R2 and R2→R3 — in mode G on K; in mode E on K_off only | (a), (b) per rung R1–R3; (c) per pair of rungs; NOT_RUN if modes differ; breach is Ladder stop 4 |

### P (science, fail-closed)

| Gate | What | Language allowed |
|---|---|---|
| P0 | pipeline sanity at the rung (Q5 + end-to-end spectrum produced + cost record printed) | "ran" |
| P1 | harmonic cross-check at R0: our unscaled DFT harmonic bands vs line A's unscaled values, within a declared convention window | "consistent" |
| P2 | **the beat comparison** (accuracy rungs): paired per-band \|error\| on positions vs lab, pipeline vs line A, M04 baseline, and line B where present; per family; margins from the pilot note; decidability per Ladder §2. Intensities reported alongside; scored only where the pilot note names a gas-phase intensity scoreboard | "beat / lost / inconclusive" |
| P3 | the §5 axis: learned prior vs structural prior at matched K, bonus rung or dry-run corpus, ≥3 seeds, effect size from the pilot note | "the prior buys X" |
| P4 | **null rows, mandatory.** (a) **Δ = 0** (DFT harmonic + DFT anharmonic, no CC correction), scored by the same script, bands, windows, seeds and aggregation as the P2 claim it nullifies: on every family where the pipeline claims "beat", the Δ=0 arm's family mean \|error\| must exceed the pipeline's by at least that family's beat margin. (b) a noise-input run must fail Q5/P0. (c) the shuffled-probe null must fail Q7 | — |
| P5 | reach certificate (R4–R6): end-to-end run + error budget (empirical component = M04 uncertainty layer; labelled **an extrapolation from R0–R3**) + theory-vs-theory table + **the cost record, in the same table as R3's** + the certificate or refusal | "reached", never "beat" |

Consequence sentences, pre-authorised and identical here and in §8:

- If **P4(a)** fails on a family: **"The coupled-cluster correction did not improve on the
  DFT-anharmonic arm at Rn on family F; the coupled-cluster claim for F is void and the result
  is reported as explained by DFT-level anharmonicity."** (Losing to the M04 calibrated
  harmonic baseline is a different outcome — a P2 loss — with §8's second sentence.)
- If **P4(b)** passes where it should fail: **"The sanity gates at Rn are void; no P2 result at
  Rn is interpreted until the gate is repaired by dated note and re-run."**
- If **P4(c)** passes where it should fail: **"Q7 is not discriminating at Rn at the frozen
  tolerance; Δ is not licensed at Rn"** — Ladder stop 4 applies.

If P0 fails at a rung, P2 is not interpreted there.

## §8 Fail-closed sentences (pre-written)

- "Rung Rn did not run: [cap/precondition/binary/option] — see the dated note."
- "Rung Rn ran and lost to [line] on [families]: paired table attached."
- "The coupled-cluster correction did not improve on the DFT-anharmonic arm at Rn on family F;
  the coupled-cluster claim for F is void and the result is reported as explained by DFT-level
  anharmonicity."
- "The sanity gates at Rn are void; no P2 result at Rn is interpreted until the gate is
  repaired by dated note and re-run."
- "Q7 is not discriminating at Rn at the frozen tolerance; Δ is not licensed at Rn."
- "Family [F] at Rn is **pre-declared inconclusive on matrix**: the M03-measured |matrix−gas|
  delta is not smaller than the beat margin. No beat, no loss."
- "Reach rung Rn produced a spectrum with the attached error budget; no accuracy claim is made
  because no laboratory spectrum exists."
- "Δ was not recovered at Rn within K_cap; the rung's Δ is absent and the fallback of Ladder
  §5.4 was scored instead."
- "Δ is not local at Rn on family F: Q8(a/b) breached with the attached decay curve and
  long-range share; no accuracy claim finer than that share is made for F."
- "The probe count did not saturate between R1 and R3 in mode G (Q8c breached, ratios
  attached); no size claim is made, and this spectrum's cost is not an extrapolable quantity."
- "Mode E only at Rn: K = 2M + K_off = …; no size claim."

## §9 Claim ladder (keyed to gates)

1. P0+P1 at R0 → "the pipeline exists and is convention-clean."
2. Q7 at R0–R1 → "the probed Δ₂ and Δ₃/Δ₄ reproduce direct CC force-constant corrections
   within tolerance, at the measured K, and beat the zero correction by the discriminability
   factor."
3. Agreement within margin at R0–R1 + P2 win + P4 clean → "a probed CC correction reproduces
   known truth on small PAHs against gas-phase data — and beats the lines, secondary to
   agreement."
4. Q8(a/b) at R1–R3 → "the correction decays with distance with fitted length r_c, and the
   scored families' corrections are carried by pairs within r_max."
5. P2 at R2–R3 on decidable families → "…and it holds where PAHdb's anharmonic front ends, on
   the families the lab data can decide."
6. Q8(c) in mode G at R1→R2 and R2→R3 → the size claim, in Ladder §1's numeric form only.
7. P3 effect ≠ 0 on a bonus rung → "the learned prior buys X" (bonus; never load-bearing).
8. P5 at R6 (conditional on B3) → "the pipeline reaches a C₃₈₄H₄₈-class species from the atlas
   with the attached cost record beside R3's: a labelled theory-vs-theory spectrum plus an
   uncertainty statement that is explicitly an extrapolation from R0–R3."
9. Tier-1 emission on any of the above → "and here is what JWST would see, via the inherited
   cascade model."

Each step cites only the gates above it. A missing gate truncates the ladder; it never
re-words it.
