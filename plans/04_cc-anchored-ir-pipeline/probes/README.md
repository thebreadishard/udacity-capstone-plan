# Probes — Plan 04

Conventions, carried from plans 01–03:

- A number that is not printed by a script in this folder is not a result.
- Probes that need inputs which do not exist yet print `NOT_RUN` and exit cleanly.
- A probe is not a plan and does not get a plan number.
- Pre-registered comparisons (frozen lines, ladder rungs) are scored by scripts here, never
  by hand in a document.

## Probes that exist

- [`nist_gas_coverage.py`](nist_gas_coverage.py) (first run 2026-09-02, completed 2026-09-03)
  — which R0–R3 molecules have gas-phase IR in the NIST WebBook. **Measured:** gas PRESENT
  for benzene, naphthalene, pyrene, chrysene (and triphenylene); tetracene solid-only;
  coronene has no WebBook IR at all. Raw evidence in [`nist_cache/`](nist_cache/). This is
  *coverage*, not decidability — the M03 delta statistics remain owed, and the R2 gas grids
  are ~4 cm⁻¹.

## Probes owed (with the ladder freeze, not before)

1. Benzene R0 pilot: geometry → Hessian → harmonic bands, **timed, and nothing further** — it
   produces no pipeline-vs-lab number. The lab comparison for benzene runs only after the
   pilot note is committed (Ladder §4); running it earlier would let the note be written
   against known results.
2. Lab-scoreboard re-read: regenerate the plan-02 band table (PAHdb experimental uids, NIST
   JCAMP) under this plan's own hash, so §6 of the frozen-lines file rests on a script in
   *this* tree.
3. DLPNO point cost: one timed DLPNO-CCSD(T) energy+gradient at a declared rung size and the
   frozen basis/thresholds, on the laptop — **the kill probe**: its wall-clock × the rung's
   frozen N_min against the 168 h B2 cap decides mechanically whether that rung's factory is
   B2, B3, or not run (Compute_Budget §3).
4. Resonance probe (before any R2 surface is fitted, DFT level is enough): pyrene CH-stretch
   family via GVPT2 vs raw VPT2 vs MD-ACF; if raw VPT2 moves the band by more than the beat
   margin relative to GVPT2, raw VPT2 is forbidden on that family (it already is forbidden on
   promised families — this probe measures by how much).
5. Anchor-license probes (Distilled Q6): DLPNO−canonical and TightPNO−NormalPNO
   harmonic-frequency deltas at the license molecule + normal-mode smoothness scan.
