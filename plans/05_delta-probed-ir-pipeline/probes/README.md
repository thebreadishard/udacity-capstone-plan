# Probes — Plan 05

Conventions, carried from plans 01–04:

- A number that is not printed by a script in this folder is not a result.
- Probes that need inputs which do not exist yet print `NOT_RUN` and exit cleanly.
- A probe is not a plan and does not get a plan number.
- Pre-registered comparisons (frozen lines, ladder rungs) are scored by scripts here, never
  by hand in a document.
- **[05]** A probe pattern set is a versioned input: its hash is printed by every recovery
  probe that uses it.

## Probes that exist

None under plan 05 yet. Plan 04's NIST gas-phase coverage probe and its raw cache exist in
`plans/04_cc-anchored-ir-pipeline/probes/` and are re-run under this plan's hash as owed
probe 2 below; their measured result (gas IR present for benzene, naphthalene, pyrene,
chrysene, triphenylene; tetracene solid-only; coronene absent) is carried as provenance.

## Probes owed (in the order they decide things)

1. **Zero-CC dry run** (`dryrun_dft_delta_recovery.py`): Δ between two DFT functionals at R0
   and at the largest molecule the laptop's DFT Hessian affords; recover Δ₂ with the plan's
   solver from a hashed pattern set; print K needed to reach a declared held-out residual,
   and the recovered-vs-direct frequency error per family. Validates the estimator at DFT
   level only.
2. **Lab-scoreboard re-read**: regenerate the plan-02 band table (PAHdb experimental uids,
   NIST JCAMP) and the plan-04 NIST coverage scan under this plan's hash.
3. **Gradient availability** (`anchor_gradient_availability.py`): per candidate code, does an
   analytic gradient at the anchor level run at R0 with frozen domains? Prints code, version,
   yes/no, wall-clock. Decides mode E vs G.
4. **R0 pilot**: geometry → DFT Hessian → harmonic bands, **timed**; then the R0 probe batch
   with frozen domains and the **Q7 reference**: a direct numerical local-CC (and canonical)
   Hessian minus the DFT Hessian. Produces **no pipeline-vs-lab number** (Ladder §4).
5. **Anchor-licence probes** (Q6): local-CC vs canonical and TightPNO vs NormalPNO
   harmonic-frequency deltas at the licence molecule; normal-mode smoothness with and without
   frozen domains.
6. **Locality decay** (`delta_locality_decay.py`, Q8): |Δ₂| between atom pairs vs distance at
   R1, then R2, then R3; fitted r_c; K per rung side by side.
7. **Resonance probe** (before any R2 Δ₃/Δ₄ is used, DFT level is enough): pyrene CH-stretch
   family via GVPT2 vs raw VPT2 vs MD-ACF.
8. **Classification probe** per rung: `wall_clock_per_probe × K` against the 168 h checkpoint
   (Compute_Budget §2).
