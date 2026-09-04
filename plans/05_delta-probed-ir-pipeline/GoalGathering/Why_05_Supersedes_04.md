# Why plan 05 supersedes plan 04

**Status.** Argument of record, 2026-09-03; revised the same day after Round-7 Pass A (issues
1, 8, 15, 16) and Pass B (issues 3, 4, 5, 13). Plan 04 is **not** wrong; it is superseded
because its cost sits in the wrong object. Plan 04's folder is **kept in the tree** for now —
removing it is the user's decision, not this document's; plans 01–03 were restored to the tree on 2026-09-04 as read-only records (user decision 2).

**Notation used from here on.** Δ is the difference between the local coupled-cluster (local-CC)
and the DFT potential energy surfaces near the equilibrium geometry, written as force
constants: **Δ₂** the correction to the Hessian (second derivatives), **Δ₃** to the cubic
constants, **Δ₄** to the semi-diagonal quartic constants. **Local CC** means DLPNO-CCSD(T)
(domain-based local pair natural orbital coupled cluster) or LNO-CCSD(T) (local natural
orbital), both controlled locality truncations of CCSD(T). **Mode E** recovers Δ from energies
only; **mode G** from analytic gradients. **K** is the number of local-CC evaluations a rung
actually needed (a measured output, defined in the Ladder); in mode E, K = 2M + K_off. **GVPT2**
is second-order vibrational perturbation theory with resonances treated explicitly; **MD-ACF**
is a spectrum from the dipole autocorrelation of molecular dynamics; **CMA** is the Concordant
Mode Approach (bibliography items 42–43).

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
that Δ₂ is small, smooth and short-ranged in real space. That bet is the plan's central risk
(Q6, Q8), not a premise. Round-7 Pass B put the arithmetic on the record: in mode E, coronene
costs 2M + K_off ≥ 204 + K_off local-CC energies — a factor 30–50 below plan 04's asserted 10⁴
points before K_off is known — and that, not any "O(1)", is plan 05's defensible advantage.

## What plan 05 changes — the complete list

One idea: **where the coupled-cluster budget is spent and how it is collected.** Its
consequences touch more documents than one line, so every change of frozen intent relative to
plan 04 is listed here. Anything not on this list is inherited unchanged.

| # | Plan 04 | Plan 05 | Where |
|---|---|---|---|
| 1 | Object paid for at CC level: a per-molecule learned surface (10³–10⁴ points) | **Δ₂ on all modes**, probed; **no CC correction to anharmonic constants** (a diagonal-cubic bonus probe reports its size) | Goal, Distilled §3 |
| 2 | CC data collected by sampled geometries, learned by a Transformer surface | **Probed**: a hashed, ordered set of simultaneously multi-displaced patterns; Δ₂ recovered by sparse recovery in the DFT normal-mode basis with a fixed, **frequency-banded** structural prior | Distilled §3 |
| 3 | Where CC enters the spectrum: anharmonic correction on a DFT Hessian | **Harmonic only** (Δ₂); DFT supplies cubic and semi-diagonal quartic constants on a resonance-closed family set — the hybrid-QFF allocation (items 14, 27, 45), adopted because mode E cannot produce the three-index cubic constants PAH resonances need (Pass B issue 3) | Distilled §3 |
| 4 | Local-CC noise averaged by the fit; Q6 smoothness probe | **Domains, pair lists and PNO counts frozen at the reference geometry** for every probe; noise, bias and threshold sensitivity measured against **frozen formulas** (Q6 with thresholds, pilot-note item 13); CPS extrapolation as a deck option | Ladder §3, Distilled Q6 |
| 5 | P3 axis: Δ-learning vs direct fit | P3 axis: **learned prior vs structural prior at matched K** on the dry-run corpus — a bonus experiment, never on a promised rung | Distilled §5 |
| 6 | Gates Q0–Q6 | Gates Q0–Q8: **Q7 probing licence** (Δ₂ vs direct references at R0–R1, printed for diagonal-only and full recovery, with a discriminability clause and a shuffled-probe null), **Q8 locality and saturation on directly measured blocks** in a form frozen now | Distilled §7 |
| 7 | Pilot-note item 5 = P3 effect size (Δ vs direct); item 8 = N_min | Item 5 redefined (prior saving); N_min removed; **new items 8–13**: residual target ρ\*, cap K_cap, hold-out fraction and seed, Q7 tolerance and d₇, Q8 numbers and direct-block pairs, Q6 numbers and pattern amplitude; item 2 gains an expected-effect line | Ladder §4 |
| 8 | Two sentence types (accuracy, reach) | **A third sentence type, the cost record**, promised for every rung that ran; a separate **numeric size sentence** in a mode-E form (on K_off, the promised route) and a mode-G form (bonus), each allowed only after Q8(c) | Ladder §1 |
| 9 | Prime directive: one sentence | Prime directive gains a second sentence: the CC cost is recorded as a measured probe count; mode E is the promised route; no cost adjective is ever written | Goal |
| 10 | B2 = the laptop; B3 = cluster node-hours | B2 = **the machine the student owns**; B3 = cluster node-hours **and rented GPU-hours**, same three preconditions with a money cap in place of an allocation; the R6 DFT Hessian is B3 unless a timed probe shows otherwise | Budget §1, §3 |
| 11 | Resolution-floor controls: test RMSE, DLPNO-threshold sensitivity | Controls: **held-out residual, local-CC noise floor, threshold sensitivity** | Ladder §3 |
| 12 | Stop 1: ORCA/DLPNO unavailable | Stop 1 also fires if **no code can freeze domains, pair lists and PNO counts** at the anchor level | Ladder §5 |
| 13 | P4(a) null arm: harmonic-only | P4(a) null arm: **DFT harmonic + DFT anharmonic, no CC correction**, with its own consequence sentence; P4(b) and P4(c) gain consequence sentences | Distilled §7–§8 |
| 14 | R2 A-scored set: pyrene, tetracene, chrysene; triphenylene reported only ("no laboratory spectrum") | R2 set **re-read against plan 04's own coverage probe**: triphenylene has NIST gas-phase IR and joins the A-scored set on its gas families; tetracene is matrix-only and fully M03-gated; the ~4 cm⁻¹ gas-grid caveat travels; a per-family decidability rule | Ladder §2 |
| 15 | Anharmonic routes (a) GVPT2, (b) MD-ACF, (c) CH-stretch unscored | Same three, with route (b)'s object **defined** (a deck-named DFT-trained potential plus the Δ₂ correction within the probed amplitude); without that deck entry route (b) is unavailable | Distilled §3 |
| 16 | M05 training corpus: own DLPNO point corpus | M05 corpus: **public Hessian QM9 plus recomputed B3LYP Hessians** (a DFT-vs-DFT Δ₂ corpus at scale), plus the PAH dry-run and probed tensors; M05 target = the **support of Δ₂** in the DFT mode basis (CMA-2's diagnostic, learned); distinctness under the rubric decided in the mapping; the target itself is open decision 4 | Distilled §5–§6 |
| 17 | Machine: CPU laptop → cluster | DFT Hessians on GPU where the deck names one; local CC as before | Goal, Budget |
| 18 | Cost question implicit | **Cost question anchored on mode E / K_off** (the promised route); mode G is a bonus on the verified 2026-09-03 gradient landscape (no production local-CC(T) nuclear gradient; PySCFAD AD gradients demonstrated to 29 atoms); the "CCSD gradient + energy-only (T)" idea of the research note has **no engine** and is withdrawn | Goal, Ladder §1, Research note §8 |
| 19 | R6 promised as a whole-molecule run conditional on B3 | **R6 promised as fragment-probed Δ₂**, conditional on Q8 on direct blocks at R2–R3 and on B3 (user decision 2026-09-04: fragment probing is a method decided by measurement, not a scope question). Whole-molecule R6 is not promised | Goal, Ladder §2 |
| 20 | — | **Novelty rewritten with citation**: the diagonal mode-E recovery is the Concordant Mode Approach applied to a difference (items 42–43); mode-tracking (item 46) and gradient-based compressed sensing (item 24) are named prior art; what remains proposed is stated in Research note §8 | Research note §8, Distilled §2, Frozen_Lines §1 |
| 21 | Dry run: two DFT functionals, unspecified | Dry run: **B3LYP against a high-exact-exchange functional**, so the calibration Δ contains mode rotations; dry-run-flagged blocks get explicit two-mode patterns | Distilled §3, Budget §4 |
| 22 | Q8 on whatever the pipeline produced | Q8 on **direct blocks** (reference Hessian at R0–R1; a prior-free direct-block probe at R2–R3); an **anthracene** locality probe as a dated bonus between R1 and R2 | Ladder §3, Distilled Q8, Budget §4 |
| 23 | Mulas 2018 described as "anharmonic DFT-QFF" | Functional named: **B97-1** (TZ2P pyrene, 6-31G* coronene), verified by the Round-7 Pass B reviewer from the full text | Frozen_Lines §3, bibliography item 6 |

## What plan 05 does not change

The rungs and species R0–R6 and their claim types A/R; the opponents and their versions; the
scoreboards; the numerical tolerances (10 cm⁻¹ floor, 15 cm⁻¹ working matrix convention with
the M03-measured binding value, ~1 cm⁻¹ bind); the hours directive; the module skeleton 02–09
and rule 0 of the mapping; the no-transfer rule as plan 04 wrote it — clarified on 2026-09-04
to what it always covered, spectra and band positions, so that a locality-verified electronic
correction is a method Q8 measures, not a transfer; the emission tiers; the neutral-charge rule; the Round-6
closures.

## The measurement that would say plan 05 was a mistake

If, at R1, frozen-domain local-CC energies are not smooth under the Q6 noise line (mode E
cannot see a beat-margin correction); or, at R0–R1, the recovered Δ₂ does not reproduce a
directly computed reference within tolerance (Q7); or, at R1–R3, the Δ₂ blocks measured
directly do **not** decay with distance, or the scored families' corrections are carried by
long-range pairs (Q8a/b); or K_off does not saturate between rungs (Q8c) — plan 05 has no size
advantage over plan 04 and says so, per family. Those probes are cheap relative to any point
factory and run before any reach rung. A plan-05 that fails them is reported as "Δ₂ is not
smooth / not recoverable / not local at this size, measured thus"; it does not quietly become
plan 04 with a new name, and it does not fall back to a point factory whose affordability no
plan has measured. Round-7 Pass B named the five cheapest of these measurements in order; they
are the first five owed probes.
