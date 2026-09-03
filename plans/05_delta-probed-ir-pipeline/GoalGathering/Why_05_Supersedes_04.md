# Why plan 05 supersedes plan 04

**Status.** Argument of record, 2026-09-03; revised the same day after Round-7 Pass A (issues
1, 8, 15, 16). Plan 04 is **not** wrong; it is superseded because its cost sits in the wrong
object. Plan 04's folder is **kept in the tree** for now — removing it is the user's decision,
not this document's; plans 01–03 remain git history only.

**Notation used from here on.** Δ is the difference between the local coupled-cluster (local-CC)
and the DFT potential energy surfaces near the equilibrium geometry, written as force
constants: **Δ₂** the correction to the Hessian (second derivatives), **Δ₃** to the cubic
constants, **Δ₄** to the semi-diagonal quartic constants. **Local CC** means DLPNO-CCSD(T)
(domain-based local pair natural orbital coupled cluster) or LNO-CCSD(T) (local natural
orbital), both controlled locality truncations of CCSD(T). **Mode E** recovers Δ from energies
only; **mode G** from analytic gradients. **K** is the number of local-CC evaluations a rung
actually needed (a measured output, defined in the Ladder). **GVPT2** is second-order
vibrational perturbation theory with resonances treated explicitly; **MD-ACF** is a spectrum
from the dipole autocorrelation of molecular dynamics.

## What plan 04 got right and plan 05 keeps verbatim

Everything that was governance rather than method: the relative and measured criterion; the
accuracy/reach split; the frozen opponents and scoreboards; the M03 matrix–gas decidability
gate; resonance-explicit routes only; no scale factor on anharmonic output; positions scored,
intensities reported; the three separated budgets with human hours uncapped; the pilot note
written before any pipeline-vs-lab number; mandatory null rows; fail-closed sentences; the
four-tier expectations; the value hierarchy (unknown territory is the goal). Plan 04's Round-6
Pass A and Pass B findings, and the user decisions that closed them, **bind plan 05 too** and
are not re-litigated.

## The block plan 04 could not lift

Plan 04's Round-6 Pass B (2026-09-02) found, and the plan accepted, that:

- the R2–R3 point factory (~10⁴ local-CC points per molecule, a source-conversation
  assertion) is a B3 object without an allocation (finding 4);
- R6 is either unaffordable or unfalsifiable as promised (finding 5);
- local-CC curvature noise may swallow the anharmonic signal (finding 2, Q6).

Plan 04 answered with honesty devices (classification rule, fail-closed R6, Q6 probes). It did
not change the arithmetic. On 2026-09-03 the user reported an independent assistant's estimate
that a single large PAH would still take "many, many hours" of supercomputer time under plan
04 — an assertion, but the same direction as everything asserted before it. **No timed local-CC
point has been run under any plan**; the block is an arithmetic expectation, not a measurement.

The reason is structural. Plan 04 pays coupled-cluster prices to learn a *whole surface* over
3N−6 coordinates, almost all of which DFT already describes; the CC anchor's only new
information is the CC−DFT difference Δ. Plan 05 bets — and measures, before relying on it —
that Δ is small, smooth and short-ranged in real space. That bet is the plan's central risk
(Q8), not a premise.

## What plan 05 changes — the complete list

One idea: **where the coupled-cluster budget is spent and how it is collected.** Its
consequences touch more documents than one line, so every change of frozen intent relative to
plan 04 is listed here. Anything not on this list is inherited unchanged.

| # | Plan 04 | Plan 05 | Where |
|---|---|---|---|
| 1 | Object paid for at CC level: a per-molecule learned surface (10³–10⁴ points) | **Δ₂ on all modes; Δ₃/Δ₄ on the scored families**, probed | Goal, Distilled §3 |
| 2 | CC data collected by sampled geometries, learned by a Transformer surface | **Probed**: a hashed set of simultaneously multi-displaced patterns; Δ recovered by sparse recovery in the DFT normal-mode basis with a fixed *structural prior* | Distilled §3 |
| 3 | Where CC enters the spectrum: anharmonic correction on a DFT Hessian | **Δ₂ first** (harmonic), then Δ₃/Δ₄ on scored families; DFT supplies the remaining anharmonic constants | Distilled §3 |
| 4 | Local-CC noise averaged by the fit; Q6 smoothness probe | **Domains and pair lists frozen at the reference geometry** for every probe; noise and bias measured with/without freezing (Q6) | Ladder §3, Distilled Q6 |
| 5 | P3 axis: Δ-learning vs direct fit | P3 axis: **learned prior vs structural prior at matched K** — a bonus experiment, never on a promised rung | Distilled §5 |
| 6 | Gates Q0–Q6 | Gates Q0–Q8: **Q7 probing licence** (Δ₂ *and* Δ₃/Δ₄ vs direct references at R0–R1, with a shuffled-probe null), **Q8 locality and saturation** in a form frozen now | Distilled §7 |
| 7 | Pilot-note item 5 = P3 effect size (Δ vs direct); item 8 = N_min | Item 5 redefined (prior saving); N_min removed; **new items 8–12**: residual target ρ\*, cap K_cap, hold-out fraction and seed, Q7 tolerances, Q8 numbers | Ladder §4 |
| 8 | Two sentence types (accuracy, reach) | **A third sentence type, the cost record** (K, mode, prior, ρ\*, wall-clock, probe file), promised for every rung that ran; a separate **size claim**, allowed only after Q8(c) passes in mode G at R1–R3 | Ladder §1 |
| 9 | Prime directive: one sentence | Prime directive gains a second, **conditional** sentence: the CC cost is measured as K and the size claim is earned by Q8 in mode G or not made | Goal |
| 10 | B2 = the laptop; B3 = cluster node-hours | B2 = **the machine the student owns** (the laptop or its replacement, GPU or not); B3 = cluster node-hours **and rented GPU-hours**, same three preconditions with a money cap in place of an allocation | Budget §1 |
| 11 | Resolution-floor controls: test RMSE, DLPNO-threshold sensitivity | Controls: **held-out residual, local-CC noise floor, threshold sensitivity** | Ladder §3 |
| 12 | Stop 1: ORCA/DLPNO unavailable | Stop 1 also fires if **no code can freeze domains** at the anchor level | Ladder §5 |
| 13 | P4(a) null arm: harmonic-only | P4(a) null arm: **DFT harmonic + DFT anharmonic, no CC correction**, with its own consequence sentence; P4(b) and P4(c) gain consequence sentences | Distilled §7–§8 |
| 14 | R2 A-scored set: pyrene, tetracene, chrysene; triphenylene reported only ("no laboratory spectrum") | R2 set **re-read against plan 04's own coverage probe**: triphenylene has NIST gas-phase IR and joins the A-scored set on its gas families; tetracene is matrix-only and fully M03-gated; the ~4 cm⁻¹ gas-grid caveat travels | Ladder §2 |
| 15 | Anharmonic routes (a) GVPT2, (b) MD-ACF, (c) CH-stretch unscored | Same three, with route (b)'s object **defined** (a deck-named DFT-trained potential plus the Δ expansion within the probed amplitude); without that deck entry route (b) is unavailable | Distilled §3 |
| 16 | M05 training corpus: own DLPNO point corpus | M05 corpus: **zero-CC dry-run Δ tensors (DFT-vs-DFT, any number of atlas species) plus the probed CC Δ tensors**; distinctness under the rubric decided in the mapping, not here | Distilled §6 |
| 17 | Machine: CPU laptop → cluster | DFT Hessians on GPU where the deck names one; local CC as before | Goal, Budget |

## What plan 05 does not change

The rungs and species R0–R6 and their claim types A/R; the opponents and their versions; the
scoreboards; the numerical tolerances (10 cm⁻¹ floor, 15 cm⁻¹ working matrix convention with
the M03-measured binding value, ~1 cm⁻¹ bind); the hours directive; the module skeleton 02–09
and rule 0 of the mapping; the no-transfer rule as plan 04 wrote it (fragment probing, which
would touch it, is an **open user decision**, not part of the promised set); the emission tiers;
the neutral-charge rule; the Round-6 closures.

## The measurement that would say plan 05 was a mistake

If, at R1–R3, the Δ₂ elements between atoms do **not** decay with distance, or the scored
families' corrections are carried by long-range pairs (Q8a/b), or the probe count in mode G
does not saturate between rungs (Q8c), or the recovered Δ does not reproduce a directly
computed reference within tolerance at R0–R1 (Q7), plan 05 has no size advantage over plan 04
and says so. Those probes are cheap relative to any point factory and run before any reach
rung. A plan-05 that fails them is reported as "Δ is not local / not recoverable at this size,
measured thus"; it does not quietly become plan 04 with a new name, and it does not fall back
to a point factory whose affordability no plan has measured.
