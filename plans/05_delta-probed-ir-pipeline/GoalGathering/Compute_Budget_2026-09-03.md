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
| B1 human | attention hours | **uncapped, logged** (user directive 2026-09-03): one bucket per entry; the plan-01 alarm (plumbing dominating the log) triggers a written review, never a ceiling. **A separate bucket "side project: mode G"** (2026-09-04) for milestones M2–M5, with a calendar 12-week checkpoint from the pilot note's commit date and the 4-weekly alarm rule of the side-project note §4; probe M1 is booked to pipeline infrastructure | everything a person does |
| B2 own machine | wall-clock hours on **the machine the student owns**. **Decided 2026-09-04: this is the current laptop, an ASUS Vivobook 18 M1807HA-S8022W** — AMD Ryzen 7 260 at 3.80 GHz (8 cores / 16 threads) with integrated AMD Radeon 780M graphics (512 MB, no CUDA-class GPU), **32.0 GB DDR5-5600 (31.3 GB usable)**, 954 GB SSD with ~790 GB free — read from the machine's System → About page on 2026-09-04 (screenshot supplied by the user); the R0 pilot probe re-prints RAM and free disk at run time. A replacement is bought **only if a probe shows it necessary**, by dated note | **168 h per rung pilot is a checkpoint, not a kill**: crossing it forces a dated note — continue knowingly / reroute to B3 / stop | DFT Hessians through R3, dry runs, R0–R1 probes, ML training |
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
| Gradients for a full Hessian, DFT level | O1NumHess: a gradient count that levels off around 100–124 for hundreds of atoms; worst covalent case a conjugated polyene, MAD 6–12 cm⁻¹ (bib 23, fetched) | K(G) per rung — NOT_RUN; mode G is the aimed-for route, built in the side project; K_cap(G) is frozen from the gradient-mode dry run for every rung |
| Local-CC single point, coronene, TZ | grok_chat_4 assertion: tens of minutes to hours per node | wall_clock_per_probe(R3) — NOT_RUN |
| Local-approximation error growth | Altun et al.: DLPNO error on acenes grows ≈ linearly with ring count; CPS(6/7) reduces it at 2× cost (bib 44, fetched) | Q6 threshold line; c_CPS — NOT_RUN |
| DFT Hessian on GPU | GPU4PySCF: 30× over a 32-core node (abstract, bib 25); an 84-atom def2-TZVPP Hessian in ~30 min on one A100 (snippet only) | **B3 (rented) at every rung — the B2 laptop has no CUDA GPU**; the CPU Hessian timing per rung through R3 is the B2 slot — NOT_RUN. **R6 (C₃₈₄H₄₈: 3,552 basis functions at 4-31G, ~1,300 perturbations) is B3** unless a timed probe at the R4 species shows otherwise |
| Canonical CCSD(T) on GPU | TeraChem: 63 atoms / >1,000 bf, (T) in ~8 h on one node (bib 26, fetched) | Q6 licence-reference timing at pyrene — NOT_RUN, B3 |
| Local-CC(T) gradient | PySCFAD AD gradients demonstrated to 29 atoms; no production code offers one (bib 31–34, fetched) | the gradient-availability probe with peak memory — NOT_RUN |

The plan-02 old-laptop facts remain provenance only (CCSD(T)/6-31G* benzene 19.6 s; canonical
(T) fails at ~114 bf with 28 GB; B3LYP/6-31G* Hessians: benzene 3.3 min, naphthalene 12.7 min,
coronene frequency job 176 min). Every one is re-timed on the B2 laptop named in §1 before use (the plan-02 numbers come from an older machine).

## 4. Order of timed probes (each prints machine, date, settings, wall-clock; gradient probes also peak memory)

Before the pilot note (DFT-only and timings; no local-CC Δ₂ may exist yet):

1. **Zero-CC dry run, both modes** (B2): Δ between B3LYP and a high-exact-exchange functional
   at R0 and at the largest sizes the laptop's DFT Hessian affords; recovered by the plan's own
   solver from a hashed, ordered pattern set with seeded hold-out, once from energies and once
   from DFT gradients. Prints the residual curves, the dry-run K and K_off per mode, the
   flagged off-diagonal blocks, the recovered-vs-direct frequency error per family, and **the
   B2 laptop's per-molecule DFT Hessian timing** (which fixes the M05 subset size by dated
   note). Feeds pilot-note items 8, 9 (both modes), 13.
2. **Probe M1 — frozen spaces** (B2, main project): the candidate local-CC code stores its
   spaces at the reference geometry and reloads them at displaced geometries; reproduces the
   reference energy to 10⁻⁹ E_h; prints (does not judge) the second-difference scatter along
   one benzene mode. Fails → Ladder stop 1.
3. **Gradient availability, run/no-run at equilibrium** (B2): for each candidate code (ORCA
   DLPNO, Psi4 DLPNO, MRCC LNO, PySCFAD LNO-CC), does an analytic gradient at the anchor level
   run **at the equilibrium geometry** of benzene and naphthalene, with frozen spaces? Prints
   run/no-run, version, wall-clock, peak memory. No displaced-geometry gradient is computed
   before the pilot note. The side project's M2–M5 later supply the answers at R0–R3.
4. **Single-point timing** (B2): one local-CC energy at benzene with frozen spaces — a timing
   only.
5. **R1 smoothness probe** (B2, ~30 local-CC energies of naphthalene): three modes, nine
   points each at q ∈ [−1, 1], TightPNO, with and without frozen spaces; the script prints the
   second-difference **scatter** σ_E per mode and step against the Q6 mode-E line and writes
   the second-difference **means** to a hashed, sealed file opened only after the pilot note.
   Fixes the pattern amplitude.
6. **Pilot note committed** (the 2026-09-04 decisions recorded by reference).

After the pilot note:

7. **R0 probe batch and Q7 references** (B2): the first real `wall_clock_per_probe`, K(R0),
   the cost record; the numerical local-CC and canonical Hessians; Q7 printed for
   diagonal-only and full recovery; the diagonal-cubic bonus probe; the sealed smoothness
   means opened; **side-project M2** (gradient correct and under the mode-G noise line at
   benzene).
8. **R1**: canonical feasibility on the B2 laptop (the Q6/Q7 canonical arm at R1 exists only
   if it runs); R1 probe batch; Q7 twice; Q8(a/b) on the reference Hessian; Q6 threshold
   column; **side-project M3**.
9. **Anthracene locality probe** (dated bonus, B2 or B3 by the rule; ≈ 2×66+1 = 133 frozen-
   domain local-CC energies): a full numerical Δ₂ printed as Q8(a) per pair and as the
   mode-basis matrix per family — the cheapest direct test of whether the C–C block is
   long-ranged before R2 money is spent.
10. **R2/R3 classification** (B2 probe, then the rule decides, with c_CPS).
11. **R2**: the pyrene canonical diagonal check (two canonical CCSD(T)/cc-pVDZ energies per
    mode, one mode per family; B3 if the machine cannot); the Q6 noise grid at R2 size in the
    mode(s) used; the direct-block probe (≈12 energies per deck-chosen pair); probe batch
    (structural recovery, and the prior-assisted recovery on the same responses for the
    licence-earning comparison); Q8(a/b) on direct blocks; Q8(c) R1→R2; **side-project M4**.
12. **R3**: direct-block probe; batch (both recoveries); **coronene probed in fragments** and
    compared with coronene probed whole (the fragment licence, part b); Q8(c) R2→R3;
    **side-project M5** (gradient run/no-run at coronene).
13. **B3 probes** only after §1's three preconditions; the R4 DFT-Hessian timing probe decides
    whether the R6 Hessian is B3; the direct-block probe on the R6 fragments (fragment
    licence, part c).

## 5. Protocol (carried)

- A timing quoted anywhere but a `probes/` script output is invalid.
- Time on a quiet machine or twice (plan-02 lesson: load produced a spurious 2× effect).
- Queue generously; order jobs by what they *decide*; spend human hours on judgement.
- Supersede this file only with a new dated compute-budget doc.
