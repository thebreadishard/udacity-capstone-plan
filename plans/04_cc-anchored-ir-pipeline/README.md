# Plan 04 — CC-Anchored IR Pipeline

**Status: draft, folder created 2026-09-02. Not complete as a plan. Nothing here is a result.**  
Supersedes plan 03 (Presence-Update-Rule), which remains in the tree only until its scheduled
removal; do not add new work to plan 03. Plans 01 and 02 are git history only.

**Promised deliverable (Module 08).** A pipeline: **any individual aromatic molecule in, an
infrared spectrum out** — with a per-size method ladder, a coupled-cluster-anchored accuracy
claim where the ladder affords it, and a pre-registered comparison against the frozen
state-of-the-art lines in
[GoalGathering/Frozen_Lines_to_Beat.md](GoalGathering/Frozen_Lines_to_Beat.md).

The sequence **ends at Module 09**. There is no `Horizon/` and there are no Projects 10–12.
Chemically better IR of complex aromatics is the reason for the work, not a post-degree item.

## Reading order

1. This file — orientation. **Draft, not complete.**
2. [GoalGathering/Overarching_Goal.md](GoalGathering/Overarching_Goal.md) — prime directive
3. [GoalGathering/Frozen_Lines_to_Beat.md](GoalGathering/Frozen_Lines_to_Beat.md) — the named,
   versioned opponents and the laboratory scoreboards
4. [probes/README.md](probes/README.md) — probe conventions (no probes exist yet)

## Not yet written (owed, in order)

- **Molecule ladder + tolerances** (dated freeze doc; benzene laptop pilot is the declared
  first rung intent, C₃₈₄H₄₈-and-larger the declared top; rungs and stop conditions must be
  measured, not asserted).
- **Compute budget** (dated doc; three budgets now: human hours, laptop wall-clock, cluster
  node-hours — the third is new in plan 04).
- **Capstone_Mapping** (module map 02–09 against Rubrics v1.5.1; note the corrected reading in
  [`Rubrics/README.md`](../../Rubrics/README.md): the Module 03/04 Accepted-Sources lists are
  examples, not a closed gate).
- **Relevant_Scientific_Papers** (working bibliography; the frozen-lines doc carries the
  verified identifiers so far).
- Distilled technical plan, quality gates, review briefs.

## Provenance

Plan 04 is based on the planning conversation [`AI_Chats/grok_chat_4.md`](../../AI_Chats/grok_chat_4.md)
(read in full, 360 lines): one CC run yields one energy (optionally analytic forces); a full CC
surface is feasible for water and impossible for coronene's 102 vibrational coordinates; the
workable recipe for large aromatics is an accurate equilibrium Hessian plus a machine-learned /
reduced-dimensional anharmonic correction trained on self-generated DLPNO-CCSD(T) points, built
**per molecule** — and that per-molecule computation *is* the pipeline.

Round-5 Pass B (plan 03) still binds the architecture: no double-scope on one frozen clock.
Plan 04 does one thing — matter, nuclei, spectra. Light enters only as the emission
post-processing layer (tier 1, inherited cascade model), never as a co-owned Maxwell solver.

## What survives from plans 01–03

Method-agnostic governance, carried verbatim:

- measured-not-asserted arithmetic in `probes/`; missing inputs print `NOT_RUN`
- never cite from recall; verify-on-use; DOI before claim
- pre-registration; frozen splits with hashes; ≥3 seeds; tuning parity
- declared effect size; **inconclusive is publishable**
- escalation ladders declared in advance; stopping is a result
- fail-closed reporting; deviations only as dated notes committed before the number is known
