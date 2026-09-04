# Compute budget — Plan 05 (2026-09-03)

**Status.** First plan-05 budget, written 2026-09-03 and revised the same day after Round-7
Pass A (issues 1, 2, 19d, 20) and Pass B (issues 1, 5, 6, 8, 10). Inherits plan 04's
2026-09-03 budget (human hours uncapped; own-machine checkpoints; external preconditions) under
that file's own supersede-only rule — a later change needs a new dated file, never an edit in
place. Caps and checkpoints are **not estimates**; measured slots read NOT_RUN until a probe
prints them. Notation (K, K_off, K_cap, ρ\*, mode E/G) is defined in the Goal and Ladder.

---

## 1. Three budgets

Two of the three are plan 04's; the changes are named (Why_05 change 10).

| Budget | Currency | Rule | Governs |
|---|---|---|---|
| B1 human | attention hours | **uncapped, logged** (user directive 2026-09-03): one bucket per entry; the plan-01 alarm (plumbing dominating the log) triggers a written review, never a ceiling | everything a person does |
| B2 own machine | wall-clock hours on **the machine the student owns**. **Decided 2026-09-04: this is the current laptop, an ASUS Vivobook 18 M1807HA-S8022W** — AMD Ryzen 7 260 (8 cores / 16 threads), integrated AMD Radeon graphics (no CUDA-class GPU), RAM as printed by the R0 pilot probe (the SKU ships as 16 or 32 GB DDR5; the plan-04 proposal recorded 32 GB); a replacement is bought **only if a probe shows it necessary**, by dated note | **168 h per rung pilot is a checkpoint, not a kill**: crossing it forces a dated note — continue knowingly / reroute to B3 / stop | DFT Hessians through R3, dry runs, R0–R1 probes, ML training |
| B3 external | cluster node-hours **and rented GPU-hours** (a plan-05 addition) | **no number until three things exist in writing**: (a) access — an allocation, or a dated spend cap for rented time; (b) a timed probe on the actual machine, printed by a script; (c) a per-rung cap note derived from it | local-CC probe batches that do not fit B2; reach rungs **including their DFT Hessians**; GPU canonical-CC licence runs |

Rented GPU time is a B3 object because it is bought, not because it is remote; the same three
preconditions apply, with a money cap where an allocation would stand. Because the current
laptop has no CUDA-class GPU, **every GPU DFT Hessian is B3** (rented), and the CPU path is the
B2 default for DFT Hessians through R3. If the student buys a machine, it becomes B2 by a dated
note naming it; nothing about B2 is a precondition.

## 2. The classification rule (arithmetic, not judgement)

With **K_cap** for the rung and mode frozen in the pilot note (Ladder §4.9) and the wall-clock
per probe printed by the timed probe for that rung, mode and machine:

```
wall_clock_per_probe × K_cap(rung, mode) × c_CPS  >  168 h   →   the probe batch is a B3 object
```

where c_CPS = 2 if Q6's threshold line made CPS extrapolation mandatory at that rung's size
class, else 1. If it classifies as B3 and B3's preconditions are unmet, the rung waits or stops
**by dated note**, and the wait is reported. The rule never kills a rung by itself; K_cap may
not be lowered to pass it, ρ\* may not be raised, and CPS may not be dropped (Ladder stop 2).
Both modes are classified separately. K_cap(G) reads NOT_RUN — and mode G is unavailable — for
any rung where the gradient-availability probe printed "no".

## 3. What is new in plan 05's cost picture, and what is not yet measured

Plan 05's promised route is mode E; the open cost question is K_off. Nothing about it is a
budget fact until printed. Literature figures are motivation only:

| Quantity | Literature figure (not this project's) | Plan-05 slot |
|---|---|---|
| Energy-only diagonal Δ₂ in the DFT mode basis | arithmetic: 2M energies (M modes; naphthalene 48, pyrene 72, coronene 102, C₃₈₄H₄₈ 1,290) — the CMA-0 count (bib 42–43) | the mode-E floor — fixed by M |
| Off-diagonal count | Sanders et al.: ~30 % of columns on anthracene in a cheap-method eigenbasis, ~log growth to 15 rings, DFT level (bib 24, fetched); CMA-2: ~33 selected off-diagonals on small molecules (bib 43, fetched) | **K_off** per rung — NOT_RUN; the quantity Q8(c) tests |
| Gradients for a full Hessian, DFT level | O1NumHess: saturates ~100–124 for hundreds of atoms; worst covalent case a conjugated polyene, MAD 6–12 cm⁻¹ (bib 23, fetched) | K(G) per rung — NOT_RUN; mode G is a bonus on the 2026-09-03 landscape |
| Local-CC single point, coronene, TZ | grok_chat_4 assertion: tens of minutes to hours per node | wall_clock_per_probe(R3) — NOT_RUN |
| Local-approximation error growth | Altun et al.: DLPNO error on acenes grows ≈ linearly with ring count; CPS(6/7) reduces it at 2× cost (bib 44, fetched) | Q6 threshold line; c_CPS — NOT_RUN |
| DFT Hessian on GPU | GPU4PySCF: 30× over a 32-core node (abstract, bib 25); an 84-atom def2-TZVPP Hessian in ~30 min on one A100 (snippet only) | **B3 (rented) at every rung — the B2 laptop has no CUDA GPU**; the CPU Hessian timing per rung through R3 is the B2 slot — NOT_RUN. **R6 (C₃₈₄H₄₈: 3,552 basis functions at 4-31G, ~1,300 perturbations) is B3** unless a timed probe at the R4 species shows otherwise |
| Canonical CCSD(T) on GPU | TeraChem: 63 atoms / >1,000 bf, (T) in ~8 h on one node (bib 26, fetched) | Q6 licence-reference timing at pyrene — NOT_RUN, B3 |
| Local-CC(T) gradient | PySCFAD AD gradients demonstrated to 29 atoms; no production code offers one (bib 31–34, fetched) | the gradient-availability probe with peak memory — NOT_RUN |

The plan-02 old-laptop facts remain provenance only (CCSD(T)/6-31G* benzene 19.6 s; canonical
(T) fails at ~114 bf with 28 GB; B3LYP/6-31G* Hessians: benzene 3.3 min, naphthalene 12.7 min,
coronene frequency job 176 min). Every one is re-timed on the new machine before use.

## 4. Order of timed probes (each prints machine, date, settings, wall-clock; gradient probes also peak memory)

Before the pilot note (DFT-only and timings; no local-CC Δ₂ may exist yet):

1. **Zero-CC dry run** (B2): Δ between B3LYP and a high-exact-exchange functional at R0 and at
   the largest sizes the laptop's DFT Hessian affords; recovered by the plan's own solver from
   a hashed, ordered pattern set with seeded hold-out. Prints the residual curve, the dry-run K
   and K_off, the flagged off-diagonal blocks, and the recovered-vs-direct frequency error per
   family. Feeds pilot-note items 8, 9, 13.
2. **Gradient availability** (B2): for each candidate code (ORCA DLPNO, Psi4 DLPNO, MRCC LNO,
   PySCFAD LNO-CCSD(T)), does an analytic gradient at the anchor level run at R0, then at
   naphthalene/cc-pVTZ, then at pyrene if the machine allows, with frozen domains? Prints
   yes/no, version, wall-clock, peak memory. Decides mode E vs G per rung.
3. **Single-point timing** (B2): one local-CC energy (and gradient if available) at benzene
   with frozen domains — a timing only.
4. **R1 smoothness probe** (B2, ~30 local-CC energies of naphthalene): three modes, nine
   points each at q ∈ [−1, 1], TightPNO, with and without frozen data; second-difference
   scatter printed against the Q6 noise line on the step grid. Fixes the pattern amplitude.
5. **Pilot note committed** (with open decision 1 recorded).

After the pilot note:

6. **R0 probe batch and Q7 references** (B2): the first real `wall_clock_per_probe`, K(R0),
   the cost record; the numerical local-CC and canonical Hessians; Q7 printed for
   diagonal-only and full recovery; the diagonal-cubic bonus probe.
7. **R1**: canonical feasibility on the new machine (the Q6/Q7 canonical arm at R1 exists only
   if it runs); R1 probe batch; Q7 twice; Q8(a/b) on the reference Hessian; Q6 threshold
   column.
8. **Anthracene locality probe** (dated bonus, B2 or B3 by the rule; ≈ 2×66+1 = 133 frozen-
   domain local-CC energies): a full numerical Δ₂ printed as Q8(a) per pair and as the
   mode-basis matrix per family — the cheapest direct test of whether the C–C block is
   long-ranged before R2 money is spent.
9. **R2/R3 classification** (B2 probe, then the rule decides, with c_CPS).
10. **R2**: the pyrene canonical diagonal check (two canonical CCSD(T)/cc-pVDZ energies per
    mode, one mode per family; B3 if the machine cannot); the direct-block probe (≈12
    energies per deck-chosen pair); probe batch; Q8(a/b) on direct blocks; Q8(c) R1→R2.
11. **R3**: direct-block probe; batch; Q8(c) R2→R3.
12. **B3 probes** only after §1's three preconditions; the R4 DFT-Hessian timing probe decides
    whether the R6 Hessian is B3.

## 5. Protocol (carried)

- A timing quoted anywhere but a `probes/` script output is invalid.
- Time on a quiet machine or twice (plan-02 lesson: load produced a spurious 2× effect).
- Queue generously; order jobs by what they *decide*; spend human hours on judgement.
- Supersede this file only with a new dated compute-budget doc.
