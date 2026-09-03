# Overarching Goal — Plan 04 CC-Anchored IR Pipeline

**Status.** Prime directive as of 2026-09-02. Supersedes plan 03. Draft; not complete as a plan.
Every other plan-04 document must agree with this file; if they drift, this file wins and the
other file is patched.

## Prime directive

Build **one pipeline**: any individual aromatic molecule in, an infrared spectrum out —
and make that spectrum's **band positions demonstrably more accurate than the best prediction
currently available anywhere for that molecule**, wherever the laboratory data can decide it:
unconditional on the gas-phase rungs (R0–R1); behind the M03 matrix–gas decidability gate on
R2–R3 (undecidable families are pre-declared inconclusive); and never on reach rungs, where
the deliverable is a labelled theory-vs-theory spectrum, conditional on cluster access.
Positions are the scored quantity (see "What is scored"); intensities are reported, not part
of this criterion.

The success criterion is **relative and measured**, not absolute. "Chemical precision" is not
the promise; *beating the frozen lines where the data can decide it* is. The opponents are
named and versioned in [Frozen_Lines_to_Beat.md](Frozen_Lines_to_Beat.md) and may not be
swapped after a comparison has been scored. The scoreboard is laboratory data
(matrix-isolation, gas-phase, IRMPD), never another calculation.

## The scientific question — two questions, one per claim type

The ladder's accuracy/reach split ([Frozen_Ladder_and_Tolerances.md](Frozen_Ladder_and_Tolerances.md) §1)
is binding here too; the two questions are never concatenated into one claim:

> **Accuracy (rungs R0–R3).** Can a per-molecule pipeline — equilibrium geometry, the best
> affordable Hessian, and a machine-learned / reduced-dimensional anharmonic correction
> trained on self-generated DLPNO-CCSD(T) points — produce infrared band positions that
> measurably beat scaled-harmonic DFT (PAHdb v4.00), the in-house calibrated harmonic
> baseline, and — where its coverage reaches — DFT-ceiling MLMD (Mai 2025), per band against
> laboratory spectra?
>
> **Reach (rung R6).** Can the same pipeline, unchanged, produce a spectrum with a stated
> error budget at sizes where no anharmonic or CC-quality prediction exists at all — where no
> laboratory spectrum exists either, so no "beat" is claimed?

**What is scored.** Band **positions** are the scored quantity. Intensities are computed and
reported with provenance (dipole derivatives at the declared level); they are *scored* only
where the pilot note names a gas-phase intensity scoreboard for that molecule — matrix
intensities never score. Band pairing for the position comparison is fixed in the pilot note
and never chosen by "strongest band in a window" at comparison time (a measured plan-02 bug).
On R2–R3 the accuracy question is answered only on families that pass the **Module-03
matrix–gas decidability gate** (Ladder §2, Promised); a family whose matrix–gas delta swamps
its beat margin is pre-declared inconclusive on matrix — that sentence is part of the claim.

The gap is documented in the frozen-lines file: harmonic DFT reaches C₃₈₆, MLMD-anharmonic
(DFT teacher) reaches C₂₁₆, QFF-anharmonic reaches C₁₈–C₂₄, CC-quality reaches approximately
benzene. Everything between C₁₈ and C₃₈₄ is contested or empty, and the current keeper of the
status quo states in print that its systematic uncertainties "are currently unquantified"
(Ricca et al. 2026, ApJS 282, 7).

## Method skeleton (from the source conversation, to be distilled)

Per molecule, with the rung chosen by a declared size ladder:

1. **Geometry + Hessian** at the best affordable electronic-structure level; harmonic
   frequencies and intensities from it.
2. **Anharmonic correction** where the ladder affords it: a machine-learned or
   reduced-dimensional surface trained on self-generated **DLPNO-CCSD(T)** points (DLPNO =
   domain-based local pair natural orbital coupled cluster — a controlled locality truncation
   usable where canonical CC is not), sampled along normal modes and short MD; C–H stretches
   treated with extra care; spectra via the **resonance-explicit routes of Distilled §3**
   (GVPT2 with named thresholds and a polyad cap, MD-ACF with CH-stretch labelled classical,
   or CH-stretch unscored at that rung). **Raw VPT2 without resonance treatment is forbidden
   on promised families.**
3. **Error budget**: every claimed band carries a stated, measured error source (level,
   fit RMSE, sampling), compared per band against the lab scoreboard.
4. Known risks, named in the source conversation itself: DLPNO local-threshold roughness of
   the surface; fit and sampling error erasing the CC advantage; the warning (Tang 2025) that
   harmonic-plus-scaling often already fits band profiles — the pipeline must show *where*
   anharmonicity and the CC anchor actually pay.

## Temperature and emission (the 0 K question)

Scored product = **0 K absorption** against laboratory data. Space applications need emission
after UV heating; that is handled as three declared tiers:

- **Tier 1 — promised.** Post-process pipeline output through the published NASA Ames cascade
  emission model (AmesPAHdbPythonSuite, `cascade`). Inherited machinery, honestly labelled;
  our contribution is better input bands, not a new emission model.
- **Tier 2 — conditional.** If the per-molecule ML surface exists, MD at chosen internal
  energy yields temperature-dependent band shifts and widths from the dipole autocorrelation
  — a measured bonus. Its comparison protocol may be written **only after** the tier-2 lab
  references are pinned (bibliography debt 4 is unpaid); no tier-2 plot is ever shown against
  literature fetched after the plot exists.
- **Tier 3 — not promised.** A new microcanonical photon-by-photon radiative model is someone
  else's thesis.

## Size and compute (decided 2026-09-02)

- **Size:** the method must work on super-large aromatics — **including C₃₈₄H₄₈-class species
  (the 101–386-carbon PAHdb bin) and larger**. For that bin the only existing predictions
  anywhere are scaled harmonic B3LYP/4-31G. Whether C₃₈₄H₄₈ *itself* has a PAHdb v4.00 entry
  is an unpaid check (frozen-lines debt 6, an M02 task); the R6 target species is chosen from
  what the opponent atlas actually contains.
- **Compute:** the plan must not die on compute. Start on a laptop (benzene pilot proves the
  pipeline end-to-end), escalate to UvA supercomputer access (collaboration with a UvA
  professor — the user's sister) when a rung demands it. Three budgets, each capped in a
  dated compute-budget doc before the corresponding rung starts: human hours, laptop
  wall-clock, cluster node-hours. The source conversation's own estimate — ~10⁴ DLPNO points
  for coronene = thousands of node-hours — is the class of cost the third budget exists for.

## Scope boundaries

- The degree **ends at Module 09**. No Horizon documents, no Projects 10–12.
- Light–matter dynamics (Maxwell, TDDFT propagation) is **out**. Plan 03's Pass B verdict
  binds: one scope, one clock. Emission is post-processing (tier 1), never a co-owned solver.
- JWST spectra motivate the work and may be shown in Module 08's industry frame; **species
  identification in an observed spectrum is not a promise**.
- No spectrum is claimed below the resolution the evidence supports; sub-cm⁻¹ language is
  forbidden (observational meaning ends around 10 cm⁻¹; matrix data carries its own shift
  uncertainty, measured by Module 03). The source conversation's bind is carried verbatim:
  ~1 cm⁻¹-class accuracy is claimed **only if** the lab comparison *and* the declared controls
  (test RMSE, DLPNO-threshold sensitivity) both allow it — and never on matrix data.

## Forbidden quotes (this thesis)

Do not write any of the following as a Module 08 result:

- "Chemically precise infrared lines" (absolute claim; the criterion is relative and measured).
- "We beat PAHdb / Mai 2025" without the pre-registered per-band comparison printed by a probe.
- "We identified PAHs in a JWST spectrum."
- "The pipeline works to C₃₈₄H₄₈" unless that molecule's rung actually ran and was scored.
- Any band position without its measured error source named.

## Value hierarchy (user directive, 2026-09-02)

Beating the lines on benzene is **not the point** — benzene's existing data may already be
excellent, and losing there is not a project failure. The small rungs exist to *license and
calibrate* the pipeline (the R1 anchor check, the pilot note, the gates), not to be its
destination. **The destination is the territory where nothing exists yet**: super-large
aromatics that no method has ever treated beyond scaled-harmonic DFT. Entering unknown
territory is the goal, not a risk to be minimised away.

Two consequences, so this directive cannot be quoted against the freeze:

1. **Winning small is not a precondition for going large.** The ladder requires R3 to be
   *scored* before reach rungs start — scored includes lost and inconclusive. An honest loss
   or a gate-closed inconclusive on R2–R3 does not cancel R6.
2. **The honesty rules are how unknown territory is entered, not why it is avoided.** No
   accuracy claim without a scoreboard, labelled extrapolations, fail-closed certificates —
   those rules exist precisely so the pipeline *can* go where nothing can check it, without
   lying about what that means.

## What is inherited

From plans 01–03, method-agnostic and kept: measured-not-asserted probes; never cite from
recall; pre-registration, frozen splits with hashes, ≥3 seeds, tuning parity; declared effect
size, inconclusive publishable; escalation ladders declared in advance, stopping is a result;
fail-closed reporting; deviations as dated notes committed before the affected number is known.

From plan 02 specifically: the measured lab-comparison machinery (PAHdb experimental band
reads with recorded uids; NIST JCAMP recipe; class-resolved band centres) — in git history,
recomputable, and the quantitative floor under the frozen lines.

## Industry frame

Reliability-gated spectral prediction for laboratory astrophysics and aerosol/combustion
diagnostics: a database keeper or instrument team gets a per-molecule spectrum **with a
quantified error budget**, or an explicit refusal naming the rung that could not be afforded.
Not "AI for astronomy." Not identification-as-a-service.
