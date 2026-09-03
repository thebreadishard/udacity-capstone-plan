# Compute budget — Plan 05 (2026-09-03)

**Status.** First plan-05 budget, written 2026-09-03 and revised the same day after Round-7
Pass A (issues 1, 2, 19d, 20). Inherits plan 04's 2026-09-03 budget (human hours uncapped;
own-machine checkpoints; external preconditions) under that file's own supersede-only rule —
a later change needs a new dated file, never an edit in place. Caps and checkpoints are **not
estimates**; measured slots read NOT_RUN until a probe prints them. Notation (K, K_cap, ρ\*,
mode E/G) is defined in the Goal and Ladder.

---

## 1. Three budgets

Two of the three are plan 04's; the changes are named (Why_05 change 10).

| Budget | Currency | Rule | Governs |
|---|---|---|---|
| B1 human | attention hours | **uncapped, logged** (user directive 2026-09-03): one bucket per entry; the plan-01 alarm (plumbing dominating the log) triggers a written review, never a ceiling | everything a person does |
| B2 own machine | wall-clock hours on **the machine the student owns** — the laptop or its replacement, with or without a GPU | **168 h per rung pilot is a checkpoint, not a kill**: crossing it forces a dated note — continue knowingly / reroute to B3 / stop | DFT Hessians, dry runs, R0–R1 probes, ML training |
| B3 external | cluster node-hours **and rented GPU-hours** (a plan-05 addition) | **no number until three things exist in writing**: (a) access — an allocation, or a dated spend cap for rented time; (b) a timed probe on the actual machine, printed by a script; (c) a per-rung cap note derived from it | local-CC probe batches that do not fit B2; reach rungs; GPU canonical-CC licence runs |

Rented GPU time is a B3 object because it is bought, not because it is remote; the same three
preconditions apply, with a money cap where an allocation would stand. If the student buys a
machine, it becomes B2 by a dated note naming it; nothing about B2 is a precondition.

## 2. The classification rule (arithmetic, not judgement)

With **K_cap** for the rung and mode frozen in the pilot note (Ladder §4.9) and the wall-clock
per probe printed by the timed probe for that rung, mode and machine:

```
wall_clock_per_probe × K_cap(rung, mode)  >  168 h   →   the probe batch is a B3 object
```

If it classifies as B3 and B3's preconditions are unmet, the rung waits or stops **by dated
note**, and the wait is reported. The rule never kills a rung by itself; K_cap may not be
lowered to pass it, and ρ\* may not be raised (Ladder stop 2). Both modes are classified
separately: a rung may be B3 in mode E and B2 in mode G, and the note says which. K_cap(G)
reads NOT_RUN — and mode G is unavailable — for any rung where the gradient-availability probe
printed "no".

## 3. What is new in plan 05's cost picture, and what is not yet measured

Plan 05 expects K in mode G to saturate with size. Nothing about that is a budget fact until
printed. Literature figures are motivation only:

| Quantity | Literature figure (not this project's) | Plan-05 slot |
|---|---|---|
| Gradients for a full Hessian, DFT level | O1NumHess: saturates ~100–124 for hundreds of atoms (bib 23, fetched) | K(G) per rung — NOT_RUN |
| Hessian columns needed, compressed sensing in a cheap-method eigenbasis, DFT level | Sanders et al.: 30 % on anthracene; ~log growth to 15 rings (bib 24, fetched) | K_off(E) — NOT_RUN |
| Energy-only diagonal Δ₂ in the DFT mode basis | arithmetic: 2M energies (M modes; coronene 102, C₃₈₄H₄₈ 1,290) | the mode-E floor — NOT_RUN |
| DFT Hessian on GPU | GPU4PySCF: 84 atoms, def2-TZVPP B3LYP, ~30 min on one A100 — a figure seen in a search snippet of the vendor paper (bib 25), not in its abstract | B2 or B3 timing per rung — NOT_RUN |
| Local-CC single point, coronene, TZ | grok_chat_4 assertion: tens of minutes to hours per node | wall_clock_per_probe(R3) — NOT_RUN |
| Canonical CCSD(T) on GPU | TeraChem: 63 atoms / >1,000 bf, (T) in ~8 h on one node (bib 26, fetched) | Q6 licence-reference timing — NOT_RUN, B3 |

The plan-02 old-laptop facts remain provenance only (CCSD(T)/6-31G* benzene 19.6 s; canonical
(T) fails at ~114 bf with 28 GB; B3LYP/6-31G* Hessians: benzene 3.3 min, naphthalene 12.7 min,
coronene frequency job 176 min). Every one is re-timed on the new machine before use.

## 4. Order of timed probes (each prints machine, date, settings, wall-clock)

1. **Zero-CC dry run** (B2, any time): Δ between two DFT functionals, recovered by the plan's
   own solver, at R0 and at the largest size the laptop's DFT Hessian affords. Prints the
   residual curve and the dry-run K at DFT level, from which the pilot note derives ρ\* and
   K_cap. Validates the estimator; says nothing about CC locality.
2. **Gradient availability** (B2): for each candidate code (ORCA DLPNO, Psi4 DLPNO, MRCC LNO,
   PySCFAD LNO), does an analytic gradient at the anchor level run at R0 size, and with
   frozen domains? Prints yes/no, version, wall-clock. Decides mode E vs G per code.
3. **Single-point timing** (B2): one local-CC energy (and gradient if available) at benzene
   with frozen domains — a timing only; no Δ is formed before the pilot note.
4. **Pilot note committed.**
5. **R0 probe batch and Q7 references** (B2): the first real `wall_clock_per_probe`, K(R0),
   and the Δ₂/Δ₃/Δ₄ references (local-CC and canonical).
6. **R1** (B2 unless classified otherwise): the first R1 probe measures *whether* canonical
   (T) runs on the new machine (Ladder R1 row); the Q6/Q7 canonical arm at R1 exists only if
   it does. Then the R1 probe batch, Q8(a/b).
7. **R2/R3 classification** (B2 probe, then the rule decides).
8. **B3 probes** only after §1's three preconditions.

## 5. Protocol (carried)

- A timing quoted anywhere but a `probes/` script output is invalid.
- Time on a quiet machine or twice (plan-02 lesson: load produced a spurious 2× effect).
- Queue generously; order jobs by what they *decide*; spend human hours on judgement.
- Supersede this file only with a new dated compute-budget doc.
