# Overarching Goal — Plan 05 Δ-Probed IR Pipeline

**Status.** Prime directive as of 2026-09-03. Supersedes plan 04's Goal file (kept in the tree
until the user removes plan 04). Draft; not complete as a plan. Every other plan-05 document
must agree with this file; if they drift, this file wins and the other file is patched.

## Prime directive

Build **one pipeline**: any individual aromatic molecule in, an infrared spectrum out —
and make that spectrum's **band positions demonstrably more accurate than the best prediction
currently available anywhere for that molecule**, wherever the laboratory data can decide it:
unconditional on the gas-phase rungs (R0–R1); behind the M03 matrix–gas decidability gate on
R2–R3 (undecidable families are pre-declared inconclusive); and never on reach rungs, where
the deliverable is a labelled theory-vs-theory spectrum, conditional on cluster access.
Positions are the scored quantity; intensities are reported, not part of this criterion.

**And do it at a coupled-cluster cost that does not grow with the molecule.** That second
sentence is what plan 05 adds. It is not a claim; it is the measured quantity K (probes per
rung) in the ladder, and the plan fails closed if K does not saturate.

The success criterion is **relative and measured**, not absolute. "Chemical precision" is not
the promise; *beating the frozen lines where the data can decide it* is. The opponents are
named and versioned in [Frozen_Lines_to_Beat.md](Frozen_Lines_to_Beat.md) and may not be
swapped after a comparison has been scored. The scoreboard is laboratory data, never another
calculation.

## The scientific question — two questions, one per claim type

The accuracy/reach split ([Frozen_Ladder_and_Tolerances.md](Frozen_Ladder_and_Tolerances.md)
§1) is binding; the two questions are never concatenated into one claim:

> **Accuracy (rungs R0–R3).** Can a per-molecule pipeline — DFT geometry and harmonic
> Hessian, plus a **probed** coupled-cluster correction to the force constants (Δ₂ on all
> modes; Δ₃/Δ₄ on the scored band families), recovered from a size-independent number of
> local-CC evaluations — produce infrared band positions that measurably beat scaled-harmonic
> DFT (PAHdb v4.00), the in-house calibrated harmonic baseline, and — where its coverage
> reaches — DFT-ceiling MLMD (Mai 2025), per band against laboratory spectra?
>
> **Reach (rung R6).** Can the same pipeline, unchanged, produce a spectrum with a stated error
> budget at sizes where no anharmonic or CC-quality prediction exists at all — where no
> laboratory spectrum exists either, so no "beat" is claimed — **at a probe count measured to
> be of the same order as at R3**?

**What is scored.** Band **positions**. Intensities are computed from DFT dipole derivatives
and reported with provenance; no CC correction to dipoles is promised (local-correlation
discontinuities corrupt finite-difference field properties — bibliography item 30); they are
*scored* only where the pilot note names a gas-phase intensity scoreboard. Band pairing is
fixed in the pilot note, never chosen by "strongest band in a window". On R2–R3 the accuracy
question is answered only on families that pass the **Module-03 matrix–gas decidability gate**.

Embedded in the accuracy question is the **efficiency sub-question**, which is what makes plan
05 a different plan: *how many coupled-cluster evaluations does a CC-quality force-constant
correction actually need, and does that number stop growing with the molecule?* It is answered
by measurement (Ladder §4: K per rung; Q7/Q8), never by the literature figures that motivated
it.

## Method skeleton (to be distilled)

Per molecule, with the rung chosen by the declared size ladder:

1. **Geometry + harmonic Hessian + dipole derivatives** at a declared DFT level (B3LYP-class,
   basis frozen per rung), analytic, on GPU where the deck names one. This is the global,
   delocalised part and stays per molecule. DFT cubic/semi-diagonal quartic constants for
   the scored families from finite differences of the analytic DFT Hessian (or from a
   DFT-trained potential, if the deck names one and its residual is printed).
2. **Δ-probing.** Δ = local-CC minus DFT, near equilibrium, as force constants. A hashed set
   of **K displacement patterns** (simultaneous multi-atom displacements built so every atom's
   local displacement space is complete, plus mode-targeted patterns for the promised
   families). At every pattern, local CC (DLPNO- or LNO-CCSD(T), code fixed in the Q0 deck)
   and DFT are evaluated **with correlation domains and pair lists frozen at the reference
   geometry**. Δ₂ (and Δ₃/Δ₄ on the scored families' modes) is recovered by one
   sparse-recovery solve in the DFT normal-mode basis. Two recovery modes, decided per rung by
   a timed probe: **mode E** (energies only) and **mode G** (analytic local-CC gradients where
   a code provides them at that size). Anchors are licensed by measured deltas (Q6), the
   recovery by a reference comparison at R0–R1 (Q7), and the size claim by the measured
   locality decay (Q8).
3. **Spectra** via the **resonance-explicit routes** frozen in plan 04 (GVPT2 with named
   thresholds and a polyad cap; MD-ACF with CH-stretch labelled classical; or CH-stretch
   unscored at that rung), on DFT-plus-Δ. **Raw VPT2 without resonance treatment is forbidden
   on promised families.** No scale factor on anharmonic output.
4. **Error budget**: every claimed band carries its measured error sources — DFT level;
   recovery residual on held-out probes; local-CC noise floor (with vs without frozen
   domains); locality tail beyond r_c; matrix–gas shift where matrix data is used.

Known risks, named now: Δ may not be local enough (Q8); local-CC gradients may not exist at
the anchor level so mode E's probe count is 2M-plus rather than O(1) (the classification rule
decides B2/B3, never a hope); frozen domains may not be available in the chosen code; the
harmonic-first allocation of CC may still lose to calibrated harmonics on some families (P4's
Δ=0 null row remains mandatory and publishable).

## Temperature and emission (the 0 K question) — carried from plan 04 unchanged

Scored product = **0 K absorption** against laboratory data. Emission after UV heating in
three declared tiers: **tier 1 promised** — post-process through the published NASA Ames
cascade model (AmesPAHdbPythonSuite), inherited machinery, honestly labelled; **tier 2
conditional** — temperature-dependent shifts from MD on a DFT-plus-Δ potential, protocol
written only after the tier-2 lab references are pinned (bibliography debt 4 unpaid);
**tier 3 not promised**.

## Size and compute (carried, with the plan-05 addition)

- **Size:** the method must work on super-large aromatics — **including C₃₈₄H₄₈-class species
  (the 101–386-carbon PAHdb bin) and larger**. Whether C₃₈₄H₄₈ itself has a PAHdb v4.00 entry
  is an unpaid check (frozen-lines debt 6); the R6 target species is chosen from the atlas.
- **Compute:** the plan must not die on compute. Start on the laptop (R0 pilot proves the
  pipeline end-to-end, including a **zero-CC dry run** of the probing machinery — DFT-vs-DFT
  Δ — at any size the DFT Hessian affords); escalate to UvA supercomputer access or rented
  GPU time when a rung demands it, under [Compute_Budget_2026-09-03.md](Compute_Budget_2026-09-03.md):
  human hours **logged, never capped**; laptop wall-clock as **checkpoints**; cluster
  node-hours and rented GPU-hours under per-rung dated notes after timed probes. The
  classification rule is `wall_clock_per_probe × K_rung` against the 168 h checkpoint.

## Scope boundaries (carried)

- The degree **ends at Module 09**. No Horizon documents, no Projects 10–12.
- Light–matter dynamics is **out** (plan-03 Pass B verdict binds: one scope, one clock).
- JWST spectra motivate the work; **species identification is not a promise**.
- No sub-tolerance language: observational meaning ends around 10 cm⁻¹; matrix data carries
  its own measured shift; ~1 cm⁻¹-class accuracy is claimed **only if** the lab comparison and
  the declared controls (recovery residual, local-CC noise floor, threshold sensitivity) all
  allow it — and never on matrix data.
- **No transferable, train-once spectrum model.** Every molecule gets its own probed Δ. The
  M05 learned Δ-prior is an efficiency experiment whose effect is measured (P3) and which
  never replaces probes on a promised rung.

## Open decisions for the user (not part of the promised set)

1. **Fragment probing** (Research note §5): probing Δ on capped fragments of radius r_c instead
   of on the whole flake would make R6's CC cost independent of size, at the price of using a
   *local correction* obtained on one flake for another. Plan 04's no-transfer rule was written
   against motif transfer of band positions; whether it covers a locality-verified electronic
   correction is a scope decision. Until decided, plan 05 promises whole-molecule probing only
   and treats fragment probing as a labelled bonus arm at R4–R6.
2. **Removal of the plan-04 folder** from the tree (git history keeps it either way).

## Forbidden quotes (this thesis)

Do not write any of the following as a Module 08 result:

- "Chemically precise infrared lines."
- "We beat PAHdb / Mai 2025" without the pre-registered per-band comparison printed by a probe.
- "We identified PAHs in a JWST spectrum."
- "The pipeline works to C₃₈₄H₄₈" unless that molecule's rung actually ran and was scored.
- "The coupled-cluster cost is size-independent" unless Q8 printed the decay and K printed
  at ≥ 2 rungs of different size.
- Any band position without its measured error source named.

## Value hierarchy (user directive 2026-09-02, carried)

Beating the lines on benzene is **not the point**; the small rungs license and calibrate. **The
destination is the territory where nothing exists yet**: super-large aromatics that no method
has ever treated beyond scaled-harmonic DFT. Winning small is not a precondition for going
large; scoring honestly is. The honesty rules are how unknown territory is entered, not why it
is avoided.

## Expectations per size tier (user directive 2026-09-03, carried verbatim in substance)

1. **Small (R0–R1):** truth is known; the pipeline must **agree** within the stated margin.
2. **Medium (R2–R3):** land within the margin **natively, without any generic scale factor**.
3. **Large (R4–R5, bonus):** named-expert judgment, expert and question fixed in a dated note
   before any R4 spectrum exists — a datum, not a quote.
4. **Super-large (R6):** **earned trust**, citing the tier record exactly as it stands.

## Hours (user directive 2026-09-03, carried)

**No cap on human hours anywhere in this plan.** Hours are logged, never limited; no deadline
is a gate; machine checkpoints survive as honesty devices only. Udacity module deadlines are
school facts handled in the mapping, never a science gate.

## What is inherited

From plans 01–04, method-agnostic and kept: measured-not-asserted probes; never cite from
recall; pre-registration, frozen splits with hashes, ≥3 seeds, tuning parity; declared effect
size, inconclusive publishable; escalation ladders declared in advance, stopping is a result;
fail-closed reporting; deviations as dated notes committed before the affected number is known.
From plan 02: the lab-comparison machinery (git history). From plan 04 specifically: the
opponents, scoreboards, ladder, tolerances, gates and both Round-6 reviews with their closures.

## Industry frame (carried)

Reliability-gated spectral prediction for laboratory astrophysics and aerosol/combustion
diagnostics: a per-molecule spectrum **with a quantified error budget**, or an explicit refusal
naming the rung that could not be afforded — now with the cost of that spectrum stated as a
measured probe count, so a database keeper can price a species before asking for it.
