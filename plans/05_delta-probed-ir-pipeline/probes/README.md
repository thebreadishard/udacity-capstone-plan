# Probes — Plan 05

Conventions, carried from plans 01–04:

- A number that is not printed by a script in this folder is not a result.
- Probes that need inputs which do not exist yet print `NOT_RUN` and exit cleanly.
- A probe is not a plan and does not get a plan number.
- Pre-registered comparisons (frozen lines, ladder rungs) are scored by scripts here, never
  by hand in a document.
- **[05]** A pattern set is a versioned, ordered input: its hash, the hold-out seed and f_h are
  printed by every recovery probe that uses it. K is printed, never typed.

## Probes that exist

None under plan 05 yet. Plan 04's NIST gas-phase coverage probe and its raw cache exist in
`plans/04_cc-anchored-ir-pipeline/probes/` and are re-run under this plan's hash as owed
probe 2 below; their measured result (gas IR present for benzene, naphthalene, pyrene,
chrysene, triphenylene; tetracene solid-only; coronene absent; R2 gas grids ~4 cm⁻¹) is
carried as provenance and already re-shaped the R2 row (Ladder §2, dated note).

## Probes owed (in the order they decide things; Compute_Budget §4 gives the timing order)

**Before the pilot note** (DFT-only and timings; no local-CC Δ may exist yet):

1. **Zero-CC dry run** (`dryrun_dft_delta_recovery.py`): Δ between two DFT functionals at R0
   and at the largest molecules the laptop's DFT Hessian affords; recover Δ₂ (and Δ₃/Δ₄ on the
   promised families' modes) with the plan's solver from a hashed, ordered pattern set with
   seeded hold-out; print the residual curve ρ(n), the dry-run K at a declared ρ, and the
   recovered-vs-direct frequency error per family. Feeds pilot-note items 8–9. Validates the
   estimator at DFT level only.
2. **Lab-scoreboard re-read**: regenerate the plan-02 band table (PAHdb experimental uids,
   NIST JCAMP) and the plan-04 NIST coverage scan under this plan's hash; print the gas grid
   per molecule and family (feeds the decidability rule).
3. **Gradient availability** (`anchor_gradient_availability.py`): per candidate code, does an
   analytic gradient at the anchor level run at R0 with frozen domains? Prints code, version,
   yes/no, wall-clock. Decides mode E vs G; K_cap(G) reads NOT_RUN where the answer is no.
4. **R0 pilot**: geometry → DFT Hessian → harmonic bands, **timed**; one timed local-CC
   single point with frozen domains (timing only). Produces **no local-CC Δ and no
   pipeline-vs-lab number**.

**After the pilot note is committed:**

5. **R0 probe batch and Q7** (`q7_probing_licence.py`): the R0 responses in hashed order, K(R0)
   at ρ\*, the cost record; then the references (numerical local-CC Hessian with frozen
   domains; canonical CCSD(T) Hessian; finite-difference Δ₃/Δ₄ along the promised modes) and
   the Q7 table (i)–(iv), including the shuffled-probe null and the discriminability factor.
6. **Anchor-licence probes** (Q6): local CC vs canonical and TightPNO vs NormalPNO
   harmonic-frequency deltas at the licence molecule; normal-mode smoothness with and without
   frozen domains; the domain-freezing bias column at R0.
7. **R1**: canonical feasibility on the new machine; R1 probe batch; Q7 at R1 (with the
   "tests the recovery, not the freezing" sentence if no canonical arm); first Q8(a/b)
   (`q8_locality.py`).
8. **Resonance probe** (before any R2 spectrum, DFT level is enough): pyrene CH-stretch
   family via GVPT2 vs raw VPT2 vs MD-ACF.
9. **Classification probe** per rung: `wall_clock_per_probe × K_cap` against the 168 h
   checkpoint (Compute_Budget §2).
10. **R2, R3**: probe batches, Q8(a/b) per rung, Q8(c) per pair of rungs (same mode, same
    prior), the cost records side by side.
