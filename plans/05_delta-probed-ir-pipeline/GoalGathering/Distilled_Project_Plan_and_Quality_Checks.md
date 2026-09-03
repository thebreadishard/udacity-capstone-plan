# Distilled project plan and quality checks — Plan 05

Agrees with [Overarching_Goal.md](Overarching_Goal.md); the Goal file wins on drift. Opponents:
[Frozen_Lines_to_Beat.md](Frozen_Lines_to_Beat.md). Rungs and stop conditions:
[Frozen_Ladder_and_Tolerances.md](Frozen_Ladder_and_Tolerances.md). Costs:
[Compute_Budget_2026-09-03.md](Compute_Budget_2026-09-03.md). Modules: `Capstone_Mapping.md`
(written after the Round-7 reviews).

**Status.** Draft, 2026-09-03. Not complete as a plan. Nothing here is a result.

---

## §1 Claim

A per-molecule pipeline — DFT geometry, analytic DFT Hessian and dipole derivatives, plus a
**probed coupled-cluster correction Δ to the force constants** (Δ₂ on all modes; Δ₃/Δ₄ on the
scored families), recovered from K local-CC evaluations with frozen correlation domains —
produces IR **band positions** that, on the gas-phase rungs R0–R1, **agree with the known
truth within the stated margin (primary) and beat the frozen lines under the pre-registered
paired comparison (secondary)**; on R2–R3 the beat comparison runs only for families that
pass the M03 matrix–gas gate, all others pre-declared inconclusive. On reach rung R6 —
conditional on B3 — it produces a labelled theory-vs-theory spectrum with an uncertainty
statement that is explicitly an extrapolation, **together with the probe count K(R6) printed
next to K(R3)**. Intensities are reported, not part of this claim.

If a gate fails, the claim is the fail-closed sentence of §8, not a quieter product.

## §2 Question and positioning

> What does a coupled-cluster correction to the force constants buy, per band, on top of the
> best available DFT-level IR prediction — and how many coupled-cluster evaluations does that
> correction actually need, as a function of molecule size?

| Neighbour | Already does | This plan still asks |
|---|---|---|
| PAHdb v4.00 (line A) | scaled-harmonic breadth to C₃₈₆ | quantify and beat its per-band error |
| Mai 2025 (line C) | MLMD anharmonic to C₂₁₆, T-dependent | beat its *teacher* where lab data exists; meet it theory-vs-theory on reach rungs |
| Lam 2020 (bib 13) | QM harmonic + ML anharmonic, 37 small molecules, RMSD 21–23 cm⁻¹ | CC-anchored, per molecule, at PAH sizes, without relaxing tolerances |
| Ethereal AI (bib 7) | ML-corrected scale factors | reproduce as M04; anharmonicity must beat *corrected* harmonic |
| O1NumHess (bib 23); Sanders et al. (bib 24) | O(1)-gradient / compressed-sensing recovery of a **full** Hessian, DFT level | apply the recovery to the **CC−DFT difference**, extend it to Δ₃/Δ₄, and measure whether K saturates on PAHs |
| Hybrid CC/DFT QFFs (bib 14, 27) | CC harmonic + DFT anharmonic on small molecules | the same allocation of CC, obtained by probing rather than by a full CC Hessian, at sizes where a full CC Hessian is impossible |
| Plan 04 (git tree, superseded) | the same criterion with a learned per-molecule surface | the same claim at a cost that is measured to saturate |

**Not novel:** running DFT/local CC; compressed sensing; GVPT2. **Scored:** the frozen
evaluation contract on a Δ-probed per-molecule pipeline across a declared size ladder, with
the probe count as a reported quantity.

## §3 Levels and anchors (frozen intent; deck hashes at Q0 per rung)

| Item | Choice |
|---|---|
| Geometry, harmonic Hessian, dipole derivatives | DFT (B3LYP-class, basis per rung), analytic; GPU code (GPU4PySCF-class) if the deck names one, CPU otherwise. The *baseline level* and the global part of every spectrum |
| DFT anharmonic constants (cubic, semi-diagonal quartic) | finite differences of the analytic DFT Hessian along the promised families' modes (reduced-dimensionality, bib 28); a DFT-trained potential may replace this only if named in the deck with its residual printed |
| Anchor level | local CC = **DLPNO-CCSD(T) or LNO-CCSD(T)**, code and thresholds fixed in the deck; **domains and pair lists frozen at the reference geometry for every displaced evaluation**; **licensed by measured deltas, not by trust** (Q6: local-CC vs canonical harmonic-frequency deltas at the licence molecule — R1 if canonical runs there, else R0-only + declared cross-basis protocol; TightPNO vs NormalPNO deltas at the licence molecule and one R2-size family; smoothness along every promised mode **with and without frozen domains**) |
| Δ-probing (the plan-05 object) | Δ = local CC − DFT as force constants. **Patterns:** a hashed set of K simultaneous multi-atom displacements built so every atom's local displacement space is complete (O1NumHess-class construction), plus mode-targeted 1-D/2-D cuts along the promised families' DFT modes for Δ₃/Δ₄. **Recovery:** sparse recovery of Δ₂ in the DFT normal-mode basis (near-diagonal prior; ℓ₁-regularised, with an off-diagonal low-rank term), and least squares for the targeted Δ₃/Δ₄; the **uninformed prior** is the promised route. **Modes:** E (energies only; K ≈ 2M + K_off) or G (gradients; K expected O(1)) — chosen per rung by the gradient-availability probe; both K values printed. **Hold-out:** a fraction f_h of probes never enters the recovery and yields the residual that goes into the error budget. **Licence:** Q7 at R0–R1 against a directly computed reference Δ₂; Q8 locality decay at R1–R3 |
| Anharmonic machinery | GVPT2 on DFT-plus-Δ, or MD-ACF on a DFT-plus-Δ potential, chosen per rung in the pilot note, **resonance-explicit** (GVPT2: named r₃/r₄ thresholds, polyad cap, CH-stretch dropped if the cap is exceeded; MD-ACF: CH-stretch labelled classical; or CH-stretch never scored). Raw VPT2 without resonance treatment is forbidden on any promised family |
| Intensities | DFT dipole derivatives; no charge-flux shortcut; **no CC correction to dipoles promised** (bib 30 — PNO discontinuities corrupt field derivatives) |
| Scale factors | **none on anharmonic output.** A harmonic fallback declares its factor + fit set |
| Emission | tier 1 = published cascade model on our bands, labelled inherited |

## §4 Deviations

A deviation exists only as a dated note committed **before** the affected quantity is measured.
Forbidden without one:

- Loosening any pilot-note number or margin, in either direction, after it is frozen.
- **Writing or amending the pilot note after any pipeline-vs-lab number exists.**
- Re-windowing or re-classing a lab band after a pipeline number for that molecule exists.
- **Adding, removing or re-weighting probe patterns after the recovery residual for that rung
  is known;** lowering K below the frozen value; using unfrozen domains for a probe.
- Any lab scoreboard value entering training, validation, stopping, sampling or **probe
  design** decisions of the pipeline. The **M04 calibrated baseline** is the single declared
  exception (trains on lab residuals by design; leave-molecule-out; recipe frozen; outputs
  appear only as a P2 opponent column and the P5 empirical uncertainty layer).
- Weakening the M04 baseline after the pilot note.
- Using the learned Δ-prior on a promised accuracy rung's scored spectrum; using it to lower
  K without a P3 result on held-out probes at the previous rung.
- Swapping or re-versioning an opponent line after a comparison against it is scored.
- "Beat" language on a reach rung; a scale factor on anharmonic output; a cost sentence
  outside Ladder §1's third form.
- Starting a B3 job without the budget file's preconditions; starting any reach rung before
  R3 is scored; estimating K(R6) before Q8 has printed at R1, R2 and R3.

## §5 Architecture and the one comparison axis

- **Promised pipeline component:** the sparse-recovery solver (classical: convex ℓ₁ /
  least-squares; no neural network is on the promised path). It is Module 04's applied-ML
  object only if the mapping needs it there; otherwise it is infrastructure.
- **Model family for Module 05: Transformer** (equivariant attention over atom / DFT-mode
  tokens) predicting a **prior for Δ₂ blocks** from DFT-level features, trained on the
  published corpus of probed Δ tensors from earlier rungs. Anything outside CNN/RNN/Transformer
  returns to the user before training.
- **The controlled comparison (frozen): learned prior vs uninformed prior at matched K.**
  Same probe patterns, same held-out set, same solver, ≥3 seeds for the prior: does the prior
  lower the held-out residual at fixed K, or reach the frozen residual at lower K? The effect
  size is pilot-note item 5. This axis is the rubric's required experiment and the plan's
  efficiency question at once. **The promised spectra never depend on its outcome.**
- Baselines in every comparison table: line A (scaled harmonic), M04 calibrated harmonic, and
  the null rows (§7, P4).

## §6 Training discipline

- The probed-Δ corpus is published (Zenodo DOI, deck hashes) before Module 05 starts. Splits
  by molecule and by probe batch, hashed (Q3). Stopping on validation only. Test touched once
  per pre-registered evaluation.
- The lab scoreboard is outside all of it (Q4).
- ≥3 seeds; mean ± SD; tuning parity between the prior and any alternative prior. The M04
  baseline has its own frozen recipe.
- The M06 generative pattern-proposer (mapping) may propose displacement patterns; every
  accepted pattern is evaluated by a real calculation and enters the hashed pattern set
  **before** the recovery for that rung runs, never after.

## §7 Quality checks and gates

Scripts under `probes/`. A number not printed by a script is not a result.

### Q (integrity, per rung)

| ID | Check | Pass |
|---|---|---|
| Q0 | deck hash: levels, basis, local-CC code + thresholds, **domain-freezing flag, pattern set, solver settings, K, f_h, r_c** frozen per rung | SHA256 reproducible |
| Q1 | scoreboard reproduction: lab band table regenerated under this plan's hash | matches the pilot note's band list |
| Q2 | timed probes exist for every budget-governed step (machine, date, settings, wall-clock) | printed |
| Q3 | split overlap (molecule and probe batch) | prints 0 |
| Q4 | lab-leak check: no scoreboard value reachable from any training artifact or **pattern-design input** of the pipeline; M04 checked for leave-molecule-out instead | prints 0 |
| Q5 | minimum check: converged geometry, 0 imaginary frequencies, 3N−6 modes | pass/fail |
| Q6 | anchor-licence probes: local-CC vs canonical and TightPNO vs NormalPNO harmonic-frequency deltas at the licence molecule (+ one R2-size family); normal-mode smoothness (second-difference noise vs step) **with and without frozen domains** | deltas and noise printed; breach **is** Ladder stop 4 |
| **Q7** | **probing licence** at R0 and R1: recovered Δ₂ (uninformed prior, frozen K) vs a directly computed reference Δ₂ (full numerical local-CC Hessian minus DFT Hessian, same frozen domains; at R0 also canonical), per family in cm⁻¹; held-out residual; the **shuffled-probe null** (probe responses randomly permuted must fail this gate) | within pilot-note item 10; null fails; breach is Ladder stop 4 |
| **Q8** | **locality decay**: |Δ₂| between atom pairs vs distance at R1, R2, R3; fitted decay length r_c; and K(R1), K(R2), K(R3) side by side at the frozen residual | decay printed; K does not grow faster than the pilot-note criterion; breach is Ladder stop 4 (size claim withdrawn) |

### P (science, fail-closed)

| Gate | What | Language allowed |
|---|---|---|
| P0 | pipeline sanity at the rung (Q5 + end-to-end spectrum produced + K printed) | "ran" |
| P1 | harmonic cross-check at R0: our unscaled DFT harmonic bands vs line A's unscaled values, within a declared convention window | "consistent" |
| P2 | **the beat comparison** (accuracy rungs): paired per-band \|error\| on positions vs lab, pipeline vs line A, M04 baseline, and line B where present; per family; margins from the pilot note. Intensities reported alongside; scored only where the pilot note names a gas-phase intensity scoreboard | "beat / lost / inconclusive" |
| P3 | the §5 axis: learned prior vs uninformed prior at matched K, ≥3 seeds, effect size from the pilot note | "the prior buys X probes" |
| P4 | **null rows, mandatory**: (a) **Δ = 0** (DFT harmonic + DFT anharmonic, no CC correction), scored by the same script, bands, windows, seeds and aggregation as the P2 claim it nullifies, must lose that comparison — else the CC claim is void and reported as "explained by the calibrated harmonic baseline"; (b) a noise-input run must fail Q5/P0; (c) the **shuffled-probe null** of Q7 must fail Q7 | — |
| P5 | reach certificate (R4–R6): end-to-end run + error budget (empirical component = M04 uncertainty layer; labelled **an extrapolation from R0–R3**) + theory-vs-theory table + **K(R6) beside K(R3)** + the certificate or refusal | "reached", never "beat" |

If P0 fails at a rung, P2 is not interpreted there. If P4(a) shows Δ=0 passing, the one
pre-authorised sentence is: **"the coupled-cluster claim is void and the result is reported as
explained by the calibrated harmonic baseline."** It cannot be negotiated after the fact.

## §8 Fail-closed sentences (pre-written)

- "Rung Rn did not run: [cap/precondition/binary/option] — see the dated note."
- "Rung Rn ran and lost to [line] on [families]: paired table attached."
- "The coupled-cluster correction did not improve on Δ=0 at Rn; the claim is void and the
  result is reported as explained by the calibrated harmonic baseline."
- "Family [F] at Rn is **pre-declared inconclusive on matrix**: the M03-measured |matrix−gas|
  delta is not smaller than the beat margin. No beat, no loss."
- "Reach rung Rn produced a spectrum with the attached error budget; no accuracy claim is made
  because no laboratory spectrum exists."
- **"Δ is not local / not recoverable at this size:** Q8 (or Q7) breached at Rn with the
  attached decay and residual curves; the size claim is withdrawn and no point factory is
  substituted."

## §9 Claim ladder (keyed to gates)

1. P0+P1 at R0 → "the pipeline exists and is convention-clean."
2. Q7 at R0–R1 → "the probed Δ₂ reproduces a direct CC force-constant correction within the
   tolerance, at K probes."
3. Agreement within margin at R0–R1 + P2 win + P4 clean → "a probed CC correction reproduces
   known truth on small PAHs against gas-phase data — and beats the lines, secondary to
   agreement."
4. Q8 at R1–R3 → "the correction is local with decay length r_c, and K went n₁ → n₂ → n₃."
5. P2 at R2–R3 on families that pass the M03 gate → "…and it holds where PAHdb's anharmonic
   front ends, on the families the lab data can decide."
6. P3 effect ≠ 0 → "the learned prior buys X probes" (bonus; never load-bearing).
7. P5 at R6 (conditional on B3) → "the pipeline reaches a C₃₈₄H₄₈-class species from the atlas
   at K(R6) probes against K(R3): a labelled theory-vs-theory spectrum plus an uncertainty
   statement that is explicitly an extrapolation from R0–R3."
8. Tier-1 emission on any of the above → "and here is what JWST would see, via the inherited
   cascade model."

Each step cites only the gates above it. A missing gate truncates the ladder; it never
re-words it.
