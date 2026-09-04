# Overarching Goal — Plan 05 Δ-Probed IR Pipeline

**Status.** Prime directive as of 2026-09-03; revised the same day after Round-7 Pass A and
again after Round-7 Pass B. Supersedes plan 04's Goal file (kept in the tree until the user
removes plan 04). Draft; not complete as a plan. Every other plan-05 document must agree with
this file; if they drift, this file wins and the other file is patched.

**Notation.** Δ = local coupled cluster (local CC: DLPNO- or LNO-CCSD(T), a controlled locality
truncation of CCSD(T)) minus DFT, as force constants: **Δ₂** (Hessian correction), **Δ₃**
(cubic), **Δ₄** (semi-diagonal quartic). **Mode E** = Δ recovered from energies only; **mode G**
= from analytic local-CC gradients. **K** = the number of local-CC evaluations a rung needed
(measured; Ladder §3 defines it); in mode E, K = 2M + K_off, where 2M is the diagonal floor
(M modes) and **K_off** the off-diagonal count. **Structural prior** = the fixed, parameter-free
regulariser of the promised recovery (frequency-banded; Distilled §3); **learned prior** = the
Module-05 Transformer, a bonus. **GVPT2** = resonance-explicit second-order vibrational
perturbation theory; **MD-ACF** = spectrum from the dipole autocorrelation of molecular
dynamics; **CMA** = the Concordant Mode Approach (bibliography items 42–43), the nearest
published relative of this plan's diagonal recovery.

## Prime directive

Build **one pipeline**: any individual aromatic molecule in, an infrared spectrum out —
and make that spectrum's **band positions demonstrably more accurate than the best prediction
currently available anywhere for that molecule**, wherever the laboratory data can decide it:
unconditional on the gas-phase rungs (R0–R1); on R2–R3 per family, gas-scored families
decidable by their measured grid and matrix-scored families behind the M03 matrix–gas gate
(undecidable families pre-declared inconclusive); and never on reach rungs, where the
deliverable is a labelled theory-vs-theory spectrum, conditional on cluster access. Positions
are the scored quantity; intensities are reported, not part of this criterion.

**And record what the coupled-cluster part cost, as a measured probe count per rung.** The
promised route is **mode E**: K = 2M + K_off local-CC energies with frozen domains, where the
science and the open cost question live in K_off. The cost record is promised for every rung
that ran. **The only size sentence the thesis may write is numeric** (Ladder §1): how K_off went
from R1 to R3 against how M went — and, if analytic local-CC gradients turn out to run at all
three rungs (mode G, a bonus on the verified 2026-09-03 landscape), the same for K. No cost
adjective is ever written. A rung where mode E cannot resolve the correction above the
local-CC noise floor (Q6, a frozen formula) carries no "beat" language and says so.

The success criterion is **relative and measured**, not absolute. "Chemical precision" is not
the promise; *beating the frozen lines where the data can decide it* is. The opponents are
named and versioned in [Frozen_Lines_to_Beat.md](Frozen_Lines_to_Beat.md) and may not be
swapped after a comparison has been scored. The scoreboard is laboratory data, never another
calculation.

## The scientific questions — three, one per claim type

The accuracy/reach split ([Frozen_Ladder_and_Tolerances.md](Frozen_Ladder_and_Tolerances.md)
§1) is binding; the questions are never concatenated into one claim:

> **Accuracy (rungs R0–R3).** Can a per-molecule pipeline — DFT geometry, harmonic Hessian
> and anharmonic constants, plus a **probed coupled-cluster correction Δ₂ to the harmonic
> force constants**, recovered from K local-CC energies with frozen domains — produce infrared
> band positions that measurably beat scaled-harmonic DFT (PAHdb v4.00), the in-house
> calibrated harmonic baseline, and — where its coverage reaches — DFT-ceiling MLMD (Mai
> 2025), per band against laboratory spectra?
>
> **Cost (all rungs that ran).** In mode E, how many off-diagonal probes K_off did the
> correction need at the frozen residual target, per rung — and did K_off saturate between
> R1, R2 and R3 (Q8c)? In mode G, if it exists at all three rungs, the same for K.
>
> **Reach (rung R6).** Can the same pipeline — with Δ₂ obtained by **fragment probing**,
> licensed by Q8 on directly measured blocks at R2–R3 (user directive 2026-09-04: a permitted
> method, decided by measurement) — produce a spectrum with a stated error budget at sizes
> where no anharmonic or CC-quality prediction exists at all, with its cost record printed
> beside R3's? **Whole-molecule probing at R6 is not promised in any branch**: in mode E it is
> at least 2M = 2,580 local-CC energies of a 432-atom molecule.

**Where CC is spent, and why only there.** The promised correction is harmonic (Δ₂). The
hybrid quartic-force-field literature (items 14, 27, and the Esposito 2024 naphthalene work,
item 45) puts the coupled-cluster pay-off in the quadratic constants and leaves cubic and
quartic constants at DFT level; and the energy-only probes of mode E cannot produce the
three-index cubic constants φ_ijk that PAH combination-band resonances need (Round-7 Pass B
issue 3). Plan 05 therefore promises **no CC correction to anharmonic constants**. A
**diagonal-cubic bonus probe** (Δ₃ along each scored family's mode, four energies per mode)
reports how large that correction would have been; if it is below the beat margin at R0–R1,
that is the published reason the allocation was right. The DFT cubic and semi-diagonal quartic
constants are computed for a family set **closed under the resonance search** (partner modes
displaced too).

**What is scored.** Band **positions**. Intensities are computed from DFT dipole derivatives
and reported with provenance; no CC correction to dipoles is promised — local-correlation
domain changes produce micro-hartree discontinuities that wreck finite-difference field
properties even with fixed PNO dimensions (item 30, full text) — and they are *scored* only
where the pilot note names a gas-phase intensity scoreboard. Band pairing is fixed in the pilot
note, never chosen by "strongest band in a window".

## Method skeleton (to be distilled)

Per molecule, with the rung chosen by the declared size ladder:

1. **Geometry + harmonic Hessian + dipole derivatives** at a declared DFT level (B3LYP-class,
   basis frozen per rung), analytic, on GPU where the deck names one. The global, delocalised
   part; per molecule. At R6 this Hessian is itself a B3 object (thousands of basis functions,
   ~1,300 perturbations) unless a timed probe at the R4 species shows otherwise. DFT cubic and
   semi-diagonal quartic constants from finite differences of the analytic DFT Hessian along
   the resonance-closed family set.
2. **Δ-probing (Δ₂).** A hashed, ordered set of displacement patterns: simultaneous multi-atom
   displacements built so every atom's local displacement space is complete, plus explicit
   two-mode patterns for every off-diagonal block the zero-CC dry run flags as large (CMA-2's
   diagnostic, written as a pattern rule before any response exists). Amplitudes are chosen
   **from** the Q6 step grid (the largest step under the noise line), never the reverse. At
   every pattern, local CC and DFT are evaluated **with correlation domains, pair lists and
   PNO counts frozen at the reference geometry**. Patterns are consumed in hashed order; the
   recovery (sparse, in the DFT normal-mode basis, **frequency-banded** structural prior:
   off-diagonals within a frequency band unpenalised, outside it ℓ₁-penalised, plus a low-rank
   term) is re-solved as patterns accrue, and **K is the count at which the held-out residual
   first falls below the frozen target ρ\***. Licences: Q6 (anchor noise, bias and threshold
   sensitivity against frozen formulas), Q7 (recovery vs direct references at R0–R1, printed
   for the diagonal-only and the full recovery), Q8 (locality on **directly measured** blocks,
   and saturation of K_off).
3. **Spectra** via the **resonance-explicit routes** frozen in plan 04 — GVPT2 with named
   thresholds and a polyad cap; MD-ACF on a *defined* DFT-plus-Δ potential (Distilled §3); or
   CH-stretch unscored at that rung — on DFT-plus-Δ₂. **Raw VPT2 without resonance treatment
   is forbidden on promised families.** No scale factor on anharmonic output.
4. **Error budget**: every claimed band carries its measured error sources — DFT level;
   held-out residual; local-CC noise floor and domain-freezing bias against the Q6 formulas;
   the long-range share of the family's correction measured on direct blocks (Q8b);
   matrix–gas shift where matrix data is used.

Known risks, named now, each with the gate that measures it: frozen-domain local-CC energies
may not be smooth at the micro-hartree level that mode E needs — the published fixed-PNO-
dimension remedy failed for field derivatives (item 30) and nuclear displacements are untested
(Q6, with thresholds); Δ₂ may not be near-diagonal in the DFT mode basis for aromatic ring
modes — CMA-0 fails on exactly those (item 43) — which is why the prior is banded and Q7 prints
diagonal-only and full recoveries side by side; Δ may not be local, or local for C–H modes and
not for the delocalised C–C families (Q8a/b on direct blocks, per family); K_off may grow with
the near-degenerate manifold (Q8c on K_off); mode G may not exist above R1 on the verified
landscape (the gradient-availability probe, with memory); the local-approximation error itself
grows with acene length (item 44; the TightPNO/NormalPNO and CPS columns of Q6); the CC
correction may not improve on DFT-level anharmonicity on some families (P4's Δ=0 null row) or
may lose to calibrated harmonics, whose fitted factors already absorb the mean of a ~5 cm⁻¹
harmonic difference (item 45, snippet; a P2 outcome) — both publishable.

## Temperature and emission (the 0 K question) — carried from plan 04

Scored product = **0 K absorption** against laboratory data. Emission after UV heating in
three declared tiers: **tier 1 promised** — post-process through the published NASA Ames
cascade model (AmesPAHdbPythonSuite), inherited machinery, honestly labelled; **tier 2
conditional** — temperature-dependent shifts from MD on the *defined* DFT-plus-Δ potential
(Distilled §3), protocol written only after the tier-2 lab references are pinned (bibliography
debt 4 unpaid); **tier 3 not promised**. "Tier" here is an emission tier; the size tiers of the
expectations section below are numbered separately.

## Size and compute (carried, with the plan-05 additions)

- **Size:** the method must work on super-large aromatics — **including C₃₈₄H₄₈-class species
  (the 101–386-carbon PAHdb bin) and larger**. Whether C₃₈₄H₄₈ itself has a PAHdb v4.00 entry
  is an unpaid check (frozen-lines debt 6); the R6 target species is chosen from the atlas.
  R6 is reached by fragment probing, licensed by Q8 at R2–R3 (decided 2026-09-04; recorded
  in the pilot note).
- **Compute:** the plan must not die on compute. Start on the current laptop — the B2 machine
  named in the budget (decided 2026-09-04: an 8-core Ryzen 7 260 without a CUDA-class GPU;
  replaced only if a probe shows it necessary) — (R0 pilot proves the
  pipeline end-to-end, including a **zero-CC dry run** of the probing machinery — Δ between
  B3LYP and a functional with markedly more exact exchange, so the dry run brackets
  delocalisation error — at any size the DFT Hessian affords); escalate to UvA supercomputer
  access or rented GPU time when a rung demands it, under
  [Compute_Budget_2026-09-03.md](Compute_Budget_2026-09-03.md): human hours **logged, never
  capped**; own-machine wall-clock as **checkpoints**; cluster node-hours and rented GPU-hours
  under per-rung dated notes after timed probes. The classification rule is
  `wall_clock_per_probe × K_cap` against the 168 h checkpoint, with K_cap a pilot-note cap;
  if Q6 makes CPS threshold extrapolation mandatory, every probe counts double in that rule.

## Scope boundaries (carried)

- The degree **ends at Module 09**. No Horizon documents, no Projects 10–12.
- Light–matter dynamics is **out** (plan-03 Pass B verdict binds: one scope, one clock).
- JWST spectra motivate the work; **species identification is not a promise**.
- No sub-tolerance language: observational meaning ends around 10 cm⁻¹; matrix data carries
  its own measured shift; ~1 cm⁻¹-class accuracy is claimed **only if** the lab comparison and
  the declared controls (held-out residual, local-CC noise floor, threshold sensitivity) all
  allow it — and never on matrix data.
- **No transferable, train-once spectrum model.** Every molecule gets its own probed Δ₂. The
  learned prior (M05) is an efficiency experiment whose effect is measured (P3) **on the
  dry-run corpus and bonus rungs only**; it never enters any promised rung — R0–R3 or R6 —
  neither the scored spectrum nor K.

## Open decisions for the user (not part of the promised set until decided)

1. ~~Fragment probing~~ — **decided 2026-09-04: in, subject to Q8** (see "The goal binds;
   methods are means"). R6 is promised as fragment-probed Δ₂, conditional on Q8 on direct
   blocks at R2–R3 and on B3. Whole-molecule R6 is not promised.
2. ~~Removal of the plan-04 folder~~ — **decided 2026-09-04: every plan folder stays in the tree** (plans 01–03 restored as read-only records).
3. ~~The R2 A-scored set~~ — **decided 2026-09-04: the re-read stands** (Why_05 change 14;
   Ladder §2 dated note).
4. **The Module-05 target and corpus** (Distilled §5–§6): a Transformer that predicts the
   *support* of Δ₂ in the DFT mode basis, trained on a DFT-vs-DFT corpus built from the public
   Hessian QM9 set (item 47) plus recomputed B3LYP Hessians. If the user will not accept a
   DFT–DFT target for the deep-learning module, M05 is a demonstration and is defended as one.

## Forbidden quotes (this thesis)

Do not write any of the following as a Module 08 result:

- "Chemically precise infrared lines."
- "We beat PAHdb / Mai 2025" without the pre-registered per-band comparison printed by a probe.
- "We identified PAHs in a JWST spectrum."
- "The pipeline works to C₃₈₄H₄₈" unless that molecule's rung actually ran and was scored.
- **"Size-independent", "O(1)", "does not grow with the molecule", "saturates", or any cost
  adjective** — cost is reported as the printed record (Ladder §1) and, after Q8(c), as the
  printed ratios; never as an adjective.
- "A coupled-cluster anharmonic correction" — none is promised; the diagonal-cubic probe is a
  reported bonus number.
- "Never done before" — the diagonal mode-E recovery is CMA-0 applied to a difference (items
  42–43); what the search did not find is stated in the Research note §8 and nowhere else.
- Any band position without its measured error source named.

## The goal binds; methods are means (user directive, 2026-09-04)

The user's ruling on fragment probing, recorded verbatim in substance: *it is not for the
user to dictate whether probing in fragments is allowed. If it works and the goal is reached
with it, fine; if it does not work, then not. The goal must not drop out of sight. The goal
must be reached: a pipeline that works.* Consequences, so this directive cannot be quoted
against the freeze:

1. **Fragment probing is a permitted method, not a scope question.** Whether it is *used* at
   R4–R6 is decided by measurement — Q8(a/b) on directly measured blocks at R2 and R3 for the
   scored families — and by nothing else. Open decision 1 is closed: **in, subject to Q8**.
2. **The no-transfer rule is clarified, not weakened.** It forbids transferring *spectra or
   band positions* between molecules (the motif-atlas failure plan 02 measured). A
   locality-verified electronic correction, measured on one region and applied to another
   region whose local environment is the same within r_max, is a method whose validity Q8
   measures per family; it is labelled as such in every certificate that uses it.
3. **R6 stays a promised object**, as fragment-probed Δ₂, conditional on Q8 at R2–R3 and on
   B3. If Q8 fails for a family, that family's correction is withdrawn from the R6 certificate
   with the measured long-range share; if it fails for all scored families, R6 is reported
   with the fail-closed sentence of Distilled §8 — the goal was kept in sight and the method
   was measured to fall short of it, which is a result.
4. **The honesty rules remain the way the goal is pursued, not a reason to stop short of it.**
   No gate in this plan exists to avoid the large molecules; every gate exists so that the
   pipeline can be taken there without lying about what it delivers.

## Value hierarchy (user directive 2026-09-02, carried)

Beating the lines on benzene is **not the point**; the small rungs license and calibrate. **The
destination is the territory where nothing exists yet**: super-large aromatics that no method
has ever treated beyond scaled-harmonic DFT. Winning small is not a precondition for going
large; scoring honestly is. The honesty rules are how unknown territory is entered, not why it
is avoided.

## Expectations per size tier (user directive 2026-09-03, carried in substance)

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
