# Overarching Goal — Plan 04 CC-Anchored IR Pipeline

**Status.** Prime directive as of 2026-09-02. Supersedes plan 03. Draft; not complete as a plan.
Every other plan-04 document must agree with this file; if they drift, this file wins and the
other file is patched.

## Prime directive

Build **one pipeline**: any individual aromatic molecule in, an infrared spectrum out —
and make that spectrum **demonstrably more accurate than the best prediction currently
available anywhere for that molecule**.

The success criterion is **relative and measured**, not absolute. "Chemical precision" is not
the promise; *beating the frozen lines* is. The opponents are named and versioned in
[Frozen_Lines_to_Beat.md](Frozen_Lines_to_Beat.md) and may not be swapped after a comparison
has been scored. The scoreboard is laboratory data (matrix-isolation, gas-phase, IRMPD),
never another calculation, wherever laboratory data exists.

## The scientific question

> Can a per-molecule pipeline — equilibrium geometry, the best affordable Hessian, and a
> machine-learned / reduced-dimensional anharmonic correction trained on self-generated
> DLPNO-CCSD(T) points — produce infrared band positions and intensities that measurably beat
> scaled-harmonic DFT (PAHdb v4.00) and DFT-ceiling MLMD (Mai 2025) against laboratory
> spectra, and do so at sizes where no anharmonic or CC-quality prediction exists at all?

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
   reduced-dimensional surface trained on self-generated DLPNO-CCSD(T) points (geometries
   along normal modes / short MD); C–H stretches treated with extra care; VPT2 or MD-based
   spectra from that surface.
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
  — a measured bonus, pre-registered before it is run.
- **Tier 3 — not promised.** A new microcanonical photon-by-photon radiative model is someone
  else's thesis.

## Size and compute (decided 2026-09-02)

- **Size:** the method must work on super-large aromatics — **including C₃₈₄H₄₈ and larger**.
  For C₃₈₄H₄₈ the only existing prediction anywhere is scaled harmonic B3LYP/4-31G.
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
  forbidden (observational meaning ends around 10 cm⁻¹; lab matrix tolerances ~15 cm⁻¹).

## Forbidden quotes (this thesis)

Do not write any of the following as a Module 08 result:

- "Chemically precise infrared lines" (absolute claim; the criterion is relative and measured).
- "We beat PAHdb / Mai 2025" without the pre-registered per-band comparison printed by a probe.
- "We identified PAHs in a JWST spectrum."
- "The pipeline works to C₃₈₄H₄₈" unless that molecule's rung actually ran and was scored.
- Any band position without its measured error source named.

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
