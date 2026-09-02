# Probes — Plan 04

No probes exist yet. Conventions, carried from plans 01–03:

- A number that is not printed by a script in this folder is not a result.
- Probes that need inputs which do not exist yet print `NOT_RUN` and exit cleanly.
- A probe is not a plan and does not get a plan number.
- Pre-registered comparisons (frozen lines, ladder rungs) are scored by scripts here, never
  by hand in a document.

First probes owed (with the ladder freeze, not before):

1. Benzene R0 pilot: geometry → Hessian → harmonic bands, **timed, and nothing further** — it
   produces no pipeline-vs-lab number. The lab comparison for benzene runs only after the
   pilot note is committed (Ladder §4); running it earlier would let the note be written
   against known results.
2. Lab-scoreboard re-read: regenerate the plan-02 band table (PAHdb experimental uids, NIST
   JCAMP) under this plan's own hash, so §6 of the frozen-lines file rests on a script in
   *this* tree.
3. DLPNO point cost: one timed DLPNO-CCSD(T) single point at a declared rung size, before any
   node-hour budget is frozen.
