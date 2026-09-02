# Distilled project plan and quality checks — Plan 04

Agrees with [Overarching_Goal.md](Overarching_Goal.md); the Goal file wins on drift. Opponents:
[Frozen_Lines_to_Beat.md](Frozen_Lines_to_Beat.md). Rungs and stop conditions:
[Frozen_Ladder_and_Tolerances.md](Frozen_Ladder_and_Tolerances.md). Caps:
[Compute_Budget_2026-09-02.md](Compute_Budget_2026-09-02.md). Modules:
[Capstone_Mapping.md](Capstone_Mapping.md).

**Status.** Draft, 2026-09-02. Not complete as a plan. Nothing here is a result.

---

## §1 Claim

A per-molecule pipeline — geometry, best affordable Hessian, and a machine-learned anharmonic
correction trained on self-generated DLPNO-CCSD(T) points — produces IR band positions and
intensities that, on the accuracy rungs R0–R3, beat the frozen lines per band against
laboratory data under a pre-registered paired comparison; and on reach rung R6 produces a
spectrum with a stated error budget where no anharmonic prediction of any kind exists.

If a gate fails, the claim is the fail-closed sentence of §8, not a quieter product.

## §2 Question and positioning

> What does a CC anchor buy on top of the best available DFT-level IR prediction, per band,
> at sizes where the existing methods' own authors state their systematics are unquantified?

| Neighbour | Already does | This plan still asks |
|---|---|---|
| PAHdb v4.00 (line A) | scaled-harmonic breadth to C₃₈₆ | quantify and beat its per-band error |
| Mai 2025 (line C) | MLMD anharmonic to C₂₁₆, T-dependent | beat its *teacher* (DFT ceiling) with an R1-checked local-CC anchor |
| Lam 2020 (bib 13) | QM harmonic + ML anharmonic, 37 small molecules, RMSD 21–23 cm⁻¹ | do it CC-anchored, per-molecule, at PAH sizes, without relaxing tolerances to match |
| Ethereal AI (bib 7) | ML-corrected scale factors | reproduce as the in-house M04 baseline; anharmonicity must beat *corrected* harmonic |

**Not novel:** running DFT/DLPNO; fitting a surface; VPT2/MD spectra. **Scored:** the frozen
evaluation contract (pre-registered paired comparisons, null rows, certificates) on a
CC-anchored per-molecule pipeline across a declared size ladder.

## §3 Levels and anchors (frozen intent; deck hashes at Q0 per rung)

| Item | Choice |
|---|---|
| Geometry + harmonic Hessian | DFT (B3LYP-class, basis per rung), the *baseline level*; frozen per rung in the Q0 deck |
| Anchor points | DLPNO-CCSD(T), thresholds frozen in the deck; **licensed by the R1 canonical check** (canonical CCSD(T) is affordable at R0–R1 — measured, plan 02) |
| Anharmonic machinery | ML surface on sampled geometries (normal-mode + short-MD sampling; M06 proposals once available) → VPT2 or MD-ACF spectra; declared per rung |
| Intensities | dipole derivatives at the declared level; no charge-flux shortcut (plan-01/02 lesson) |
| Scale factors | **none on anharmonic output.** A harmonic fallback declares its factor + fit set |
| Emission | tier 1 = published cascade model on our bands, labelled inherited |

## §4 Deviations

A deviation exists only as a dated note committed **before** the affected quantity is measured.
Forbidden without one:

- Loosening any pilot-note number or margin, in either direction, after it is frozen.
- Re-windowing or re-classing a lab band after a pipeline number for that molecule exists.
- Any lab scoreboard value entering training, validation, stopping, or sampling decisions.
- Swapping or re-versioning an opponent line after a comparison against it is scored.
- "Beat" language on a reach rung; a scale factor on anharmonic output.
- Starting a cluster job without the budget file's §3 preconditions; starting any reach rung
  before R3 is scored.
- Editing the ladder, the lines, or this file's gates after they govern a scored number.

## §5 Architecture and the one comparison axis

- **Model family: Transformer** (attention over atom / internal-coordinate tokens), declared
  explicitly for the Module 05 rubric. Anything outside CNN/RNN/Transformer returns to the
  user before training (mapping §5.2).
- **The controlled comparison (frozen): Δ-learning vs direct.** Same splits, same tuning
  budget, ≥3 seeds each: (a) DFT surface + learned Δ to DLPNO anchors; (b) direct fit to
  DLPNO anchors alone. This axis is simultaneously the rubric's required experiment and the
  thesis question (what does the anchor buy).
- Baselines present in every comparison table: line A (scaled harmonic), M04 calibrated
  harmonic, and the **null row** (§7, P4).

## §6 Training discipline

- Splits over sampled geometries: train / validation / test disjoint by sampling batch,
  hashed (Q3). Stopping on validation only. Test touched once per pre-registered evaluation.
- The lab scoreboard is outside all of it (Q4): the pipeline's spectra meet lab data only
  inside the P2 comparison scripts.
- ≥3 seeds; mean ± SD; tuning parity between the Δ and direct arms (§5).
- The M06 generative sampler may propose geometries; every accepted proposal is labelled by a
  real calculation before it enters any split (mapping M06).

## §7 Quality checks and gates

Scripts under `probes/`. A number not printed by a script is not a result.

### Q (integrity, per rung)

| ID | Check | Pass |
|---|---|---|
| Q0 | deck hash: levels, basis, DLPNO thresholds, sampling protocol frozen per rung | SHA256 reproducible |
| Q1 | scoreboard reproduction: lab band table (uids, windows, classes) regenerated under this plan's hash | matches the pilot note's band list |
| Q2 | timed probes exist for every budget-governed step (B2/B3 protocol) | machine, date, settings, wall-clock printed |
| Q3 | split overlap | prints 0 |
| Q4 | lab-leak check: no scoreboard value reachable from any training artifact | prints 0 |
| Q5 | minimum check: converged geometry, 0 imaginary frequencies, 3N−6 modes | pass/fail per molecule |

### P (science, fail-closed)

| Gate | What | Language allowed |
|---|---|---|
| P0 | pipeline sanity at the rung (Q5 + end-to-end spectrum produced) | "ran" |
| P1 | harmonic cross-check at R0: our unscaled harmonic bands vs line A's unscaled values, within a declared convention window — catches parsing and unit bugs, not science | "consistent" |
| P2 | **the beat comparison** (accuracy rungs): paired per-band \|error\| vs lab, pipeline vs line A, M04 baseline, and line B where present; margins from the pilot note; per family | "beat / lost / inconclusive" |
| P3 | the §5 axis: Δ-learning vs direct, ≥3 seeds, declared effect size in the pilot note | "the anchor buys X" |
| P4 | **null rows, mandatory** (Pass-A/B lessons: gates must fail on garbage and on doing nothing): (a) Δ=0 (harmonic-only) must lose P2 wherever the anharmonic claim is made — if Δ=0 passes, the anharmonic claim is void; (b) a noise-input run must fail Q5/P0 | — |
| P5 | reach certificate (R4–R6): end-to-end run + error budget + theory-vs-theory table + the certificate or refusal | "reached", never "beat" |

If P0 fails at a rung, P2 is not interpreted there. If P4(a) shows Δ=0 passing, every P2 win
at that rung is reported as "explained by the harmonic baseline" — that sentence is
pre-authorised and cannot be negotiated after the fact.

## §8 Fail-closed sentences (pre-written)

- "Rung Rn did not run: [cap/precondition/binary] — see the dated note."
- "Rung Rn ran and lost to [line] on [families]: paired table attached."
- "The anharmonic correction did not improve on Δ=0 at Rn; the claim reduces to the
  calibrated harmonic baseline."
- "Reach rung Rn produced a spectrum with the attached error budget; no accuracy claim is
  made because no laboratory spectrum exists."

## §9 Claim ladder (keyed to gates)

1. P0+P1 at R0 → "the pipeline exists and is convention-clean."
2. P2 win at R0–R1 + P4 clean → "CC-anchored anharmonic beats the lines on small PAHs."
3. P3 effect ≠ 0 → "the anchor itself, not the fitting, buys the improvement."
4. P2 at R2–R3 → "…and it holds where PAHdb's anharmonic front ends."
5. P5 at R6 → "the pipeline reaches C₃₈₄H₄₈-class with a stated error budget — the first
   beyond-scaled-harmonic spectrum there."
6. Tier-1 emission on any of the above → "and here is what JWST would see, via the inherited
   cascade model."

Each step cites only the gates above it. A missing gate truncates the ladder; it never
re-words it.
