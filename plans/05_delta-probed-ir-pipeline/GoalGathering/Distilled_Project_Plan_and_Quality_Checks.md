# Distilled project plan and quality checks — Plan 05

Agrees with [Overarching_Goal.md](Overarching_Goal.md), which defines the notation; the Goal
file wins on drift. Opponents: [Frozen_Lines_to_Beat.md](Frozen_Lines_to_Beat.md). Rungs and
stop conditions: [Frozen_Ladder_and_Tolerances.md](Frozen_Ladder_and_Tolerances.md). Costs:
[Compute_Budget_2026-09-03.md](Compute_Budget_2026-09-03.md). Modules:
[Capstone_Mapping.md](Capstone_Mapping.md) (written after the Round-7 reviews; Pass 6 not
done).

**Status.** Draft, 2026-09-03; revised the same day after Round-7 Pass A and Pass B. Not
complete as a plan. Nothing here is a result.

---

## §1 Claim

A per-molecule pipeline — DFT geometry, analytic DFT Hessian and dipole derivatives, DFT cubic
and semi-diagonal quartic constants on a resonance-closed family set, plus a **probed
coupled-cluster correction Δ₂ to the harmonic force constants**, recovered from K local-CC
energies (mode E) with frozen correlation domains — produces IR **band positions** that, on
the gas-phase rungs R0–R1, **agree with the known truth within the stated margin (primary)
and beat the frozen lines under the pre-registered paired comparison (secondary)**; on R2–R3
the beat comparison runs per family under the Ladder §2 decidability rule, and only where the
Q6 noise gate passed at that size class, all others pre-declared inconclusive. On reach rung
R6 — as fragment-probed Δ₂ (decided 2026-09-04), conditional on Q8 at R2–R3 and on B3 — it
produces a labelled theory-vs-theory spectrum with an uncertainty statement that is
explicitly an extrapolation. **For every rung that ran, the cost record (Ladder §1) is part of
the claim.** A size sentence is written only under Ladder §1's conditions. No CC correction to
anharmonic constants is claimed. Intensities are reported, not part of this claim.

If a gate fails, the claim is the fail-closed sentence of §8, not a quieter product.

## §2 Question and positioning

> What does a coupled-cluster correction to the harmonic force constants buy, per band, on
> top of the best available DFT-level IR prediction — and how many coupled-cluster energies
> did that correction need, per rung, in its off-diagonal part?

| Neighbour | Already does | This plan still asks |
|---|---|---|
| PAHdb v4.00 (line A) | scaled-harmonic breadth to C₃₈₆ | quantify and beat its per-band error |
| Mai 2025 (line C) | MLMD anharmonic to C₂₁₆, T-dependent | beat its *teacher* where lab data exists; meet it theory-vs-theory on reach rungs |
| Lam 2020 (bib 13) | QM harmonic + ML anharmonic, 37 small molecules, RMSD 21–23 cm⁻¹ | CC-anchored, per molecule, at PAH sizes, without relaxing tolerances |
| Ethereal AI (bib 7) | ML-corrected scale factors | reproduce as M04; anharmonicity must beat *corrected* harmonic |
| **Concordant Mode Approach** (bib 42–43) | CCSD(T) diagonal force constants in a low-level (B3LYP/MP2) normal-mode basis from single-point energies, off-diagonals selected by a cheap diagnostic (CMA-2); canonical CC, molecules to ~17 atoms; diagonal-only fails on aromatic ring modes by ±20–28 cm⁻¹ | the same object as a **difference** (Δ₂ = CC − DFT), with **local CC and frozen domains** at PAH sizes; the off-diagonal block by banded sparse recovery from multi-mode patterns rather than one-by-one; the recovery licensed against direct references; locality and K_off measured |
| O1NumHess (bib 23); Sanders et al. (bib 24); mode-tracking (bib 46) | O(1)-gradient / compressed-sensing recovery of a **full** Hessian (DFT level; conjugated polyenes are O1NumHess's worst covalent case); selected high-level modes by few gradients | apply the pattern construction to Δ₂ and measure, on PAHs, whether K_off saturates |
| Hybrid CC/DFT QFFs (bib 14, 27, 45) | CC harmonic + DFT anharmonic on small molecules and naphthalene | the same allocation, with the CC harmonic part obtained by probing rather than a full CC Hessian; whether the allocation holds for PAH families is what the diagonal-cubic bonus probe and P4(a) report |
| Plan 04 (git tree, superseded) | the same criterion with a learned per-molecule surface | the same claim at a cost that is measured |

**Not novel:** running DFT/local CC; compressed sensing; CMA-style diagonal constants; GVPT2.
**Scored:** the frozen evaluation contract on a Δ₂-probed per-molecule pipeline across a
declared size ladder, with the probe count as a reported quantity.

## §3 Levels, anchors and the Δ-probing object (frozen intent; deck hashes at Q0 per rung)

| Item | Choice |
|---|---|
| Geometry, harmonic Hessian, dipole derivatives | DFT (B3LYP-class, basis per rung), analytic; GPU code (GPU4PySCF-class) if the deck names one, CPU otherwise. The *baseline level* and the global part of every spectrum. At R6 a B3 object unless a timed probe at the R4 species shows otherwise |
| DFT anharmonic constants (cubic, semi-diagonal quartic) | finite differences of the analytic DFT Hessian along the modes of the **resonance-closed family set** — every scored family mode plus every partner mode found by the r₃/r₄ resonance search (pilot-note item 7); this yields all φ_i** for those modes (the Mulas 2018 construction restricted); reduced-dimensionality precedent bib 28 |
| Anchor level | local CC = **DLPNO-CCSD(T) or LNO-CCSD(T)**, code and thresholds fixed in the deck; deck field `PNO extrapolation: none | CPS(6/7)` (bib 44); **domains, pair lists and per-pair PNO counts frozen at the reference geometry for every displaced evaluation**; **licensed by measured deltas against frozen formulas, not by trust** (Q6) |
| **Patterns** | a hashed, ordered set of simultaneous multi-atom displacements built so every atom's local displacement space is complete (O1NumHess-class construction, bib 23), plus explicit two-mode patterns for every off-diagonal block the dry run flags as large (the CMA-2 diagnostic as a pattern rule, bib 43). Amplitude q_s from the Q6 step grid (Ladder §3) |
| **Responses** | mode E: the energy difference Δ(E) at the pattern geometry minus at equilibrium; mode G: the components of the gradient difference Δ(∇E). Every response is local CC minus DFT, both with frozen domains |
| **Structural prior** (the promised route) | sparse recovery of Δ₂ in the DFT normal-mode basis with a **frequency-banded** regulariser: off-diagonal elements between modes closer than w are unpenalised (the DFT–CC mode-rotation block the near-diagonal model gets wrong on aromatics, bib 43); outside the band an ℓ₁ penalty; plus an off-diagonal low-rank term. w and the weights are deck numbers from the dry run. "Structural" means it contains no learned parameters; the **learned prior** (M05) replaces the banded term by a Transformer-predicted support and enters a promised rung only under the Ladder §3 licence |
| **Dry run** | Δ between **B3LYP and a functional with markedly more exact exchange** (BHLYP-class or HF), so that the calibration Δ contains mode rotations of the kind the CC Δ will; never two functionals of one family |
| **Hold-out and residual ρ** | a fraction f_h of patterns, chosen by the seeded deck rule before any response exists, never enters the recovery. **ρ** = RMS over held-out patterns of (response predicted by the recovered Δ₂ − computed response) ÷ RMS of the computed held-out responses; dimensionless. ρ is the error-budget term, the P3 metric and the quantity K is defined on |
| **K** | measured: the smallest pattern count, in hashed order, at which ρ ≤ ρ\* (Ladder §3); K_off = K − 2M in mode E. Reported in the cost record. Capped by K_cap (pilot note) |
| **Modes** | **E** (energies; the promised route) or **G** (gradients; bonus — on the 2026-09-03 landscape, bib 31–34 and 33, no production code offers a local-CC(T) nuclear gradient; PySCFAD's AD gradients are demonstrated to 29 atoms). Chosen per rung by the gradient-availability probe, which prints wall-clock and peak memory; both printed where both exist |
| **Diagonal-cubic bonus probe** | Δ₃ along each scored family's mode (φ_iii, four energies per mode at R0–R1): a reported number, no gate, no entry into any spectrum |
| Anharmonic machinery | route (a) **GVPT2** on DFT anharmonic constants with the Δ₂-corrected harmonic part — named r₃/r₄ thresholds, polyad cap, CH-stretch dropped from scored families if the cap is exceeded; route (b) **MD-ACF** on the **defined DFT-plus-Δ potential**: a deck-named DFT-trained potential (its residual printed) plus Δ₂ applied as the quadratic correction in DFT normal coordinates, valid within the probed amplitude, CH-stretch labelled classical — **unavailable unless the deck names that potential**; route (c) CH-stretch never scored at that rung. Raw VPT2 without resonance treatment is forbidden on any promised family |
| Intensities | DFT dipole derivatives; no charge-flux shortcut; **no CC correction to dipoles promised** (bib 30, full text: fixed-dimension PNO spaces did not remove field-derivative discontinuities) |
| Scale factors | **none on anharmonic output.** A harmonic fallback declares its factor + fit set |
| Emission | tier 1 = published cascade model on our bands, labelled inherited |

## §4 Deviations

A deviation exists only as a dated note committed **before** the affected quantity is measured.
Forbidden without one:

- Loosening any pilot-note number or margin, in either direction, after it is frozen.
- **Writing or amending the pilot note after any local-CC Δ₂ response or any pipeline-vs-lab
  number exists.**
- Re-windowing or re-classing a lab band after a pipeline number for that molecule exists.
- **Adding, removing or re-weighting patterns after any residual is known; choosing held-out
  members after responses exist; writing K before it is measured; raising ρ\*, K_cap or q_s;
  dropping CPS once mandatory; using unfrozen domains for a probe; computing a Q8 verdict on
  recovered blocks alone above R1.**
- Any lab scoreboard value entering training, validation, stopping, sampling or **pattern
  design** decisions of the pipeline. The **M04 calibrated baseline** is the single declared
  exception (trains on lab residuals by design; leave-molecule-out; recipe frozen; outputs
  appear only as a P2 opponent column and the P5 empirical uncertainty layer).
- Weakening the M04 baseline after the pilot note.
- **The learned prior on a promised rung without the Ladder §3 licence** (P3 saving shown;
  prior-free reference check at that rung within τ₇ / ε₈; `prior = learned` in the cost
  record); a Q8 ratio or an R6 sentence that mixes priors or modes.
- Swapping or re-versioning an opponent line after a comparison against it is scored.
- "Beat" language on a reach rung, or on a mode-E rung whose Q6 noise gate did not pass; a
  scale factor on anharmonic output; a cost sentence outside Ladder §1's two forms; a CC
  correction to anharmonic constants entering a spectrum.
- Starting a B3 job without the budget file's preconditions; starting any reach rung before
  R3 is scored; wording a size sentence before Q8(c) has printed at R1→R2 and R2→R3; starting
  R6 as a whole-molecule probe, or as a fragment probe before Q8 has printed at R2 and R3.

## §5 Architecture and the one comparison axis

- **Promised pipeline component:** the sparse-recovery solver with the banded structural prior
  (classical convex optimisation; no neural network on the promised path).
- **Model family for Module 05: Transformer** (equivariant attention over atom / DFT-mode
  tokens) predicting the **support of Δ₂ in the DFT mode basis** — which off-diagonal blocks
  are large — from DFT-level features: CMA-2's diagnostic, learned instead of computed. Anything
  outside CNN/RNN/Transformer returns to the user before training.
- **The controlled comparison (frozen): learned prior vs structural prior at matched K, on the
  dry-run corpus (primary) and on a bonus rung if one runs.** Same patterns, same held-out set,
  same solver, ≥3 seeds for the prior: does the prior lower ρ at fixed K, or reach ρ\* at lower
  K? The effect size is pilot-note item 5. **No promised spectrum depends on its outcome**; a
  promised rung's cost record may, once the Ladder §3 licence is earned (user directive
  2026-09-04).
- Baselines in every comparison table: line A (scaled harmonic), M04 calibrated harmonic, and
  the null rows (§7, P4).

## §6 Training discipline

- **The M05 corpus** (decided by the user 2026-09-04): the public **Hessian QM9** set (bib 47:
  41,645 molecules, ωB97x/6-31G* Hessians) plus B3LYP/6-31G* Hessians recomputed on an
  **aromatic-heavy subset** (benzene derivatives and conjugated rings over-represented; several
  thousand molecules; B2 work under the 168 h checkpoint — plan-02 provenance: 3.3 min per
  benzene Hessian on the old laptop), giving Δ₂ = ωB97x − B3LYP per molecule with the
  exact-exchange contrast the dry run needs. The PAH dry-run tensors and the probed local-CC Δ₂
  tensors from the rungs that have run (by R3: seven) are a **held-out test set only**, never
  training data. Published (Zenodo DOI, deck hashes) before Module 05 starts. Success is the
  P3 saving and the Ladder §3 licence, not accuracy for its own sake. Whether the recomputed side counts as reuse under the
  rubric is **decided in the mapping** (plan 04's reading-1 / reading-2 logic for M04 is the
  template); nothing here pre-empts it. Splits by molecule and by pattern batch, hashed (Q3).
  Stopping on validation only. Test touched once per pre-registered evaluation.
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
| Q0 | deck hash: levels, basis, local-CC code + thresholds + CPS field, **domain-freezing flag, ordered pattern set and amplitude q_s, banded-prior w and weights, hold-out seed and f_h, ρ\*, K_cap, direct-block pair list** frozen per rung | SHA256 reproducible |
| Q1 | scoreboard reproduction: lab band table regenerated under this plan's hash | matches the pilot note's band list |
| Q2 | timed probes exist for every budget-governed step (machine, date, settings, wall-clock, peak memory for gradient probes) | printed |
| Q3 | split overlap (molecule and pattern batch) | prints 0 |
| Q4 | lab-leak check: no scoreboard value reachable from any training artifact or pattern-design input of the pipeline; M04 checked for leave-molecule-out instead | prints 0 |
| Q5 | minimum check: converged geometry, 0 imaginary frequencies, 3N−6 modes | pass/fail |
| **Q6** | **anchor licence against frozen formulas** (Ladder §3, numbers at item 13): **noise** — second-difference scatter σ_E of frozen-domain ΔE along three modes (a C–C stretch, a C–H stretch, a CH-oop), nine points each at q ∈ [−1, 1], with and without frozen data, at R1 and at the R2-size family, against σ_E ≤ 0.82·τ·q_s² on the grid q_s ∈ {0.25, 0.5, 1.0}; **bias** — |Δ₂(frozen) − Δ₂(canonical)| per mode at R0, and diagonal-only along one mode per family at pyrene (two canonical energies per mode); **threshold** — TightPNO−NormalPNO frequency deltas at the licence molecule and the R2-size family, and local CC vs canonical harmonic-frequency deltas at the licence molecule | each line printed with its verdict; noise breach at a size class ⇒ no mode-E "beat" there; bias or threshold breach ⇒ Ladder stop 4 (threshold breach ⇒ CPS mandatory) |
| **Q7** | **probing licence for Δ₂** at R0 and R1, run **after** the pilot note: (i) recovered Δ₂ (structural prior, at the measured K) vs a directly computed reference Δ₂ — full numerical local-CC Hessian minus DFT Hessian with the same frozen domains, and at R0 also canonical CCSD(T) minus DFT (the only reference independent of the freezing); metric: per-family RMS harmonic-frequency difference; **printed twice — for the diagonal-only recovery (CMA-0 on Δ) and for the full banded recovery**, with the recovered Δ₂ shown as a matrix in the DFT mode basis against the reference; (ii) **discriminability**: the full recovery must be closer to the reference than Δ₂ = 0 is, by at least d₇; (iii) **shuffled-probe null**: responses randomly permuted across patterns, recovered by the same solver, must fail (i)–(ii); (iv) Q8(a/b) computed on the reference Δ₂ and on the recovered Δ₂ side by side. A **dry-run column** (B3LYP-vs-high-exchange Δ at R0 and at the largest affordable size, reference = direct DFT−DFT Hessian difference) is printed before the pilot note as the estimator check | (i) ≤ τ₇ per family for the full recovery (the diagonal-only result is reported, not gated); (ii) holds; (iii) fails; (iv) agrees within ε₈; breach is Ladder stop 4. **At R1 without a canonical arm, Q7 tests the recovery, not the freezing** — that sentence is printed with the result |
| **Q8** | **locality and saturation on direct blocks**, form frozen in Ladder §3: (a) per atom pair, ‖Δ₂ block‖ vs distance, fitted to A·exp(−r/r_c), r_c printed as a measurement, pairs beyond r_max carrying ≤ ε₈ of Σ‖block‖² — on the reference Hessian at R0–R1 and on the **direct-block probe** at R2–R3 (deck-chosen π-system pairs at near, mid, far distances; each 3×3 block by four-point finite differences of ΔE along paired atomic displacements, ≈12 energies per pair), with the recovered blocks printed beside; (b) per scored family, the share of the family's Δ-shift carried by pairs beyond r_max ≤ ε₈, with the direct far blocks substituted into the recovered Δ₂; (c) K_off(R_{n+1}) ≤ γ·K_off(R_n), same prior, same ρ\*, for R1→R2 and R2→R3 in mode E; in mode G on K only if the gradient probe printed "yes" at all three rungs | (a), (b) per rung R1–R3; recovered-vs-direct disagreement > ε₈ is a Q7-class breach; (c) per pair of rungs; NOT_RUN if modes differ; breach is Ladder stop 4 |

### P (science, fail-closed)

| Gate | What | Language allowed |
|---|---|---|
| P0 | pipeline sanity at the rung (Q5 + end-to-end spectrum produced + cost record printed) | "ran" |
| P1 | harmonic cross-check at R0: our unscaled DFT harmonic bands vs line A's unscaled values, within a declared convention window | "consistent" |
| P2 | **the beat comparison** (accuracy rungs): paired per-band \|error\| on positions vs lab, pipeline vs line A, M04 baseline, and line B where present; per family; margins from the pilot note; decidability per Ladder §2; mode-E rungs only where Q6-noise passed. Intensities reported alongside; scored only where the pilot note names a gas-phase intensity scoreboard | "beat / lost / inconclusive" |
| P3 | the §5 axis: learned prior vs structural prior at matched K, dry-run corpus or bonus rung, ≥3 seeds, effect size from the pilot note | "the prior buys X" |
| P4 | **null rows, mandatory.** (a) **Δ₂ = 0** (DFT harmonic + DFT anharmonic, no CC correction), scored by the same script, bands, windows, seeds and aggregation as the P2 claim it nullifies: on every family where the pipeline claims "beat", the Δ₂=0 arm's family mean \|error\| must exceed the pipeline's by at least that family's beat margin. (b) a noise-input run must fail Q5/P0. (c) the shuffled-probe null must fail Q7 | — |
| P5 | reach certificate (R4–R6): end-to-end run + error budget (empirical component = M04 uncertainty layer; labelled **an extrapolation from R0–R3**) + theory-vs-theory table + **the cost record, in the same table as R3's** + the fragment-locality evidence from R2–R3 if fragments were used + the certificate or refusal | "reached", never "beat" |

Consequence sentences, pre-authorised and identical here and in §8:

- If **P4(a)** fails on a family: **"The coupled-cluster correction did not improve on the
  DFT-anharmonic arm at Rn on family F; the coupled-cluster claim for F is void and the result
  is reported as explained by DFT-level anharmonicity."** (Losing to the M04 calibrated
  harmonic baseline is a different outcome — a P2 loss — with §8's second sentence.)
- If **P4(b)** passes where it should fail: **"The sanity gates at Rn are void; no P2 result at
  Rn is interpreted until the gate is repaired by dated note and re-run."**
- If **P4(c)** passes where it should fail: **"Q7 is not discriminating at Rn at the frozen
  tolerance; Δ₂ is not licensed at Rn"** — Ladder stop 4 applies.

If P0 fails at a rung, P2 is not interpreted there.

## §8 Fail-closed sentences (pre-written)

- "Rung Rn did not run: [cap/precondition/binary/option] — see the dated note."
- "Rung Rn ran and lost to [line] on [families]: paired table attached."
- "The coupled-cluster correction did not improve on the DFT-anharmonic arm at Rn on family F;
  the coupled-cluster claim for F is void and the result is reported as explained by DFT-level
  anharmonicity."
- "The sanity gates at Rn are void; no P2 result at Rn is interpreted until the gate is
  repaired by dated note and re-run."
- "Q7 is not discriminating at Rn at the frozen tolerance; Δ₂ is not licensed at Rn."
- "Mode E at the Rn size class is above the noise line (Q6: σ_E = … vs … at q_s = …); no
  'beat' language is written for mode-E results there; the cost record is attached."
- "Family [F] at Rn is **pre-declared inconclusive on matrix**: the M03-measured |matrix−gas|
  delta is not smaller than the beat margin. No beat, no loss."
- "Reach rung Rn produced a spectrum with the attached error budget; no accuracy claim is made
  because no laboratory spectrum exists."
- "R6 is not reached: Q8 failed on direct blocks at R2–R3 for [families] / B3 did not exist —
  the refusal, with the measured long-range shares, is the Module 08 result for R6."
- "Δ₂ was not recovered at Rn within K_cap; the rung's Δ₂ is absent and the fallback of Ladder
  §5.4 was scored instead."
- "Δ₂ is not local at Rn on family F: Q8(a/b) on direct blocks breached with the attached decay
  curve and long-range share; no accuracy claim finer than that share is made for F."
- "K_off did not saturate between R1 and R3 (Q8c breached, ratios attached); no size sentence
  is written."

## §9 Claim ladder (keyed to gates)

1. P0+P1 at R0 → "the pipeline exists and is convention-clean."
2. Q6 noise at R1 under the line → "frozen-domain local-CC energies are smooth enough at
   step q_s for mode E to resolve a τ correction" — or its negation, printed.
3. Q7 at R0–R1 → "the probed Δ₂ reproduces a direct CC force-constant correction within
   tolerance at the measured K, beats the zero correction by d₇, and the diagonal-only
   recovery [does / does not] suffice on the C–C families."
4. Agreement within margin at R0–R1 + P2 win + P4 clean → "a probed CC correction reproduces
   known truth on small PAHs against gas-phase data — and beats the lines, secondary to
   agreement."
5. Q8(a/b) on direct blocks at R1–R3 → "the correction decays with distance with fitted length
   r_c, and the scored families' corrections are carried by pairs within r_max" — per family.
6. P2 at R2–R3 on decidable families with Q6 passed → "…and it holds where PAHdb's anharmonic
   front ends, on the families the lab data can decide."
7. Q8(c) on K_off at R1→R2 and R2→R3 → the mode-E size sentence, numeric form only.
8. P3 effect ≠ 0 → "the learned prior buys X on the dry-run corpus" (bonus; never load-bearing).
9. P5 at R6 → "the pipeline reaches a C₃₈₄H₄₈-class species from
   the atlas by fragment-probed Δ₂ whose locality was measured at R2–R3, with the attached cost
   record beside R3's: a labelled theory-vs-theory spectrum plus an uncertainty statement that
   is explicitly an extrapolation from R0–R3" — or the refusal.
10. Tier-1 emission on any of the above → "and here is what JWST would see, via the inherited
    cascade model."

Each step cites only the gates above it. A missing gate truncates the ladder; it never
re-words it.
