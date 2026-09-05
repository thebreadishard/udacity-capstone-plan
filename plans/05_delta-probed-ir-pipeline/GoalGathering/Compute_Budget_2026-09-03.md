# Compute budget — Plan 05 (2026-09-03)

**Status.** First plan-05 budget, written 2026-09-03 and revised the same day after Round-7
Pass A (issues 1, 2, 19d, 20) and Pass B (issues 1, 5, 6, 8, 10). Inherits plan 04's
2026-09-03 budget (human hours uncapped; own-machine checkpoints; external preconditions).
Plan 04's supersede-only rule is **not** inherited (inheritance is not authority): this file is
edited in place with dated markers, and every revision is listed here — Round-8 Pass A/B
(2026-09-04: B2 laptop named; canonical feasibility probe; noise-injection column) and Round-9
Pass A (2026-09-04: the feasibility probe's decision rule; the pre-note list aligned with
probes/README; K_cap(G) wording) and Round-9 Pass B (2026-09-04: symmetrised dry-run responses;
M1 by projection; one canonical gradient; M4/M5 at 36 gradients; part (c) classified), Round-10 Pass A (2026-09-04: K in energies;
61 / 72 / 1,801 with arithmetic; anthracene as a direct-coupling probe) and Round-10 Pass B
(2026-09-04: per-energy noise injection and c₀ in §4.1; the §3 units paragraph; arms A/B in
§4.2 and §4.5). **Frozen text as of 2026-09-04 (after review rounds 7–10 and the seam check of the Round-10 Pass B patch).** From here on this file changes only by a dated note that names the finding or measurement behind the change; the Ladder is the single binding statement of every rule, and other files cite it rather than restate it. Caps and checkpoints are **not estimates**; measured slots read NOT_RUN until a probe
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
Both modes are classified separately. K_cap(G) is filled for every rung from the gradient-mode
noise-injected dry run and is simply unused on a rung where mode G is not licensed.

## 3. What is new in plan 05's cost picture, and what is not yet measured

Plan 05's promised route is mode E; the open cost question is K_off. Nothing about it is a
budget fact until printed. Literature figures are motivation only:

| Quantity | Literature figure (not this project's) | Plan-05 slot |
|---|---|---|
| Energy-only diagonal Δ₂ in the DFT mode basis | arithmetic: 2M energies (M modes; naphthalene 48, pyrene 72, coronene 102, C₃₈₄H₄₈ 1,290) — the CMA-0 count (bib 42–43) | the mode-E floor — fixed by M |
| Off-diagonal count | Sanders et al.: ~30 % of columns on anthracene in a cheap-method eigenbasis, ~log growth to 15 rings, DFT level (bib 24, fetched); CMA-2: ~33 selected off-diagonals on small molecules (bib 43, fetched) | **K_off** per rung — NOT_RUN; the quantity Q8(c) tests |
| Gradients for a full Hessian, DFT level | O1NumHess: a gradient count that levels off around 100–124 for hundreds of atoms; worst covalent case a conjugated polyene, MAD 6–12 cm⁻¹ (bib 23, fetched) | K(G) per rung — NOT_RUN; mode G is the aimed-for route, built in the side project; K_cap(G), n_min(G) and c(G) are frozen from the noise-injected gradient-mode dry run for every rung |
| Local-CC single point, coronene, TZ | grok_chat_4 assertion: tens of minutes to hours per node | wall_clock_per_probe(R3) — NOT_RUN |
| Local-approximation error growth | Altun et al.: DLPNO error on acenes grows ≈ linearly with ring count; CPS(6/7) reduces it at 2× cost (bib 44, fetched) | Q6 threshold line; c_CPS — NOT_RUN |
| DFT Hessian on GPU | GPU4PySCF: 30× over a 32-core node (abstract, bib 25); an 84-atom def2-TZVPP Hessian in ~30 min on one A100 (snippet only) | **B3 (rented) at every rung — the B2 laptop has no CUDA GPU**; the CPU Hessian timing per rung through R3 is the B2 slot — NOT_RUN. **R6 (C₃₈₄H₄₈: 3,552 basis functions at 4-31G, ~1,300 perturbations) is B3** unless a timed probe at the R4 species shows otherwise |
| Canonical CCSD(T) on GPU | TeraChem: 63 atoms / >1,000 basis functions, (T) in ~8 h on one node (bib 26, fetched) | Q6 licence-reference timing at pyrene — NOT_RUN, B3 |
| Local-CC(T) gradient | PySCFAD's released code has an LNO-CC module with a `ccsd_t.py` (`pyscfad/lno/`, bib 49, directory listing fetched 2026-09-04; whether (T) is differentiated end-to-end is side-project item (a)) and is reported to 29 atoms (bib 33); its behaviour with frozen spaces and its memory at PAH sizes are unmeasured | the gradient run/no-run before the note; side-project M2–M5 with peak memory — NOT_RUN |

The plan-02 old-laptop facts remain provenance only (CCSD(T)/6-31G* benzene 19.6 s; canonical
(T) fails at ~114 basis functions with 28 GB; B3LYP/6-31G* Hessians: benzene 3.3 min, naphthalene 12.7 min,
coronene frequency job 176 min). Every one is re-timed by a plan-05 probe before use (the plan-02 numbers were measured on this same laptop — see the dated note of 2026-09-05 below — but by plan-02 scripts, so they are provenance).

**Units.** K and K_off are counted in energies (mode E; a ± pair counts 2) or gradients (mode
G). No literature figure in the table above is in that unit: Sanders counts Hessian columns,
O1NumHess gradients (one gradient = 3N responses), CMA-2 selected off-diagonal *elements* (each
costing four energies). Every off-diagonal response costs two energies by design; the dry run
measures K_off, and the plan claims no number for it in advance.

**Dated note 2026-09-05 (machine and software facts; permitted change under the freeze — names its
findings).** (1) The plan-02 timings quoted in §3 were measured on **this** laptop (the plan-02
batch status names the machine Asus18 with 16 logical cores, 2026-08-28), not on an older
machine; the sentence "the plan-02 numbers come from an older machine" is withdrawn. They remain
provenance until a plan-05 probe re-prints them, because the plan-02 scripts are not plan-05
probes. Measured there with psi4 1.11, B3LYP/6-31G*: benzene Hessian 4.2 min, pyrene 54 min,
tetracene 72 min, chrysene 75 min, triphenylene 72 min, coronene 174 min (frequency jobs
including optimisation). (2) The B2 laptop has a working conda environment `qc` (psi4 1.11,
NumPy 2.5, SciPy 1.18, pandas 3.0) and **no pyscf, no PyTorch and no WSL**. The plan's anchor
code (pyscf-forge LNO-CCSD(T); PySCFAD for the side project) runs on Linux only, so **probe M1
and every local-CC probe need WSL (or the cluster)** — a software precondition that stands beside
stop 1 and is recorded here. DFT-only work (the dry run, the R0 pilot's DFT part, the module-05
corpus) runs now in `qc`. PyTorch is installed in a separate environment when module 05 starts,
so the psi4 environment stays intact. **Update, later on 2026-09-05:** WSL 2 (2.7.13) with Ubuntu
26.04 LTS is installed by the user; inside it a Python 3.12 environment `~/qc05` (created with uv)
holds **pyscf 2.14.0, pyscf-forge 1.1.1** (`pyscf.lno` with `lnoccsd_t.py` imports), **pyscfad
0.3.3** (`pyscfad.lno.ccsd_t` imports), jax 0.10.2, NumPy 2.5.2, SciPy 1.18.1, h5py 3.16; gfortran
15.2, cmake 4.2, OpenBLAS from apt. WSL is given 28 GB and 16 processors via `~/.wslconfig`
(default was 15 GB). Invocation from Windows: `wsl ~/qc05/bin/python <script>`; the repo is at
`/mnt/c/Users/thebr/Documents/CapstonePlan`. The PyPI versions are the pins until the deck names
commit hashes (side-project item (a)). Probe M1 can now run. **Measured later the same day (probe 4, `anchor_single_point_timing.py`,
WSL, 8 threads, benzene at the dry-run geometry, LNO thresholds 10⁻⁶/10⁻⁷, 15 fragments):**
cc-pVDZ (114 bf) LNO-CCSD(T) 180 s, canonical CCSD(T) 27 s, LNO − canonical 16 µE_h, peak 1.2 GB;
**cc-pVTZ (264 bf) LNO-CCSD(T) 2087 s, peak 5.5 GB; canonical CCSD(T) 755 s, peak 7.3 GB; LNO −
canonical 124 µE_h.** For the anchor-basis feasibility rule (Ladder §3): the Q6 bias line, 61
canonical energies × 755 s ≈ 12.8 h, **fits** (≤ 168 h, ≤ 31.3 GB); the full canonical reference
Hessian by energies, 1,801 × 755 s ≈ 378 h, **does not fit**; the 72-gradient branch waits for the
one measured canonical gradient (`canonical_gradient_timing.py`, running). A local-CC energy at the
anchor basis costs 3× a canonical one at benzene — locality pays only at larger molecules; probe M1
is therefore developed at cc-pVDZ (3 min per energy) and run once at cc-pVTZ (35 min per energy).

## 4. Order of timed probes (each prints machine, date, settings, wall-clock; gradient probes also peak memory)

Before the pilot note (DFT-only and timings; no local-CC Δ₂ may exist yet):

1. **Zero-CC dry run, both modes, with the noise-injection column** (B2): Δ between B3LYP and
   a high-exact-exchange functional at R0 and at the largest sizes the laptop's DFT Hessian
   affords; recovered by the plan's own solver from a hashed, ordered pattern set with seeded
   hold-out, once from energies and once from DFT gradients; then **the same recoveries with
   Gaussian noise injected per energy (below), R_s formed from the noisy energies**, K and ρ
   printed per σ_E — the column the stopping constant c and K_cap are taken from. Responses are the symmetric
   combinations R_s over ± pairs exactly as in the real run (Ladder §3), so the dry run measures
   Δ₂ recovery and not the fitting of the DFT−DFT force term. **Noise is injected per energy**
   (independent ε on every displaced energy; one shared ε₀ per molecule for the reference, drawn
   once; per component in mode G), the column indexed by σ_E — so c and K_cap are read at the
   noise the real run has — and the identification of the reference constant c₀ from the
   two-amplitude modes is tested here. The noiseless single-mode block prints the **DFT-arm
   floor** (grid-quadrature scatter of the DFT energies along the modes). Prints the residual curves, the
   dry-run K and K_off per mode and per σ, the flagged off-diagonal blocks, the band width w and
   weights by the Ladder §3 rule, the recovered-vs-direct frequency error per family, and **the
   B2 laptop's per-molecule DFT Hessian timing** (which fixes the M05 subset size by dated
   note). Feeds pilot-note items 8, 9 (both modes), 13.
1b. **Canonical feasibility probe** (B2): one canonical CCSD(T) energy of benzene in the anchor
   basis (cc-pVTZ) on the B2 laptop; wall-clock and peak memory printed and extrapolated to **two
   counts** (with one canonical CCSD(T) gradient also run where the code has it — PySCF
   `pyscf/grad/ccsd_t.py`, fetched 2026-09-04 — so the gradient factor is measured): the Q6 bias line
   (61 energies — the diagonal along benzene's 30 modes) and the full canonical reference
   Hessian for Q7(i)/(iv) (72 canonical CCSD(T) gradients if the chosen code has them — printed
   — else 1,801 energies by central differences). **"Fits"** = extrapolated wall-clock ≤ the
   168 h checkpoint **and** peak memory ≤ 31.3 GB, per object. Decides, per object, whether it
   runs at R0 in the anchor basis, in cc-pVDZ with both arms re-run (bias line only), or as the
   first B3 request; if only the bias line fits, Q7(i) at R0 compares to the local-CC reference
   only and Q7(iv) reads the reference Hessian from the local-CC arm, sentence printed (Ladder
   §3, anchor basis). Expected printout: the bias line fits, the full reference does not; a
   cc-pVDZ bias line is a lower bound on the TZ freezing bias (Ladder §3).
2. **Probe M1 — frozen spaces** (B2, main project): the candidate local-CC code stores its
   spaces at the reference geometry and, at displaced geometries, transports the occupied and the
   virtual vectors by projection and Löwdin-orthonormalises them (Ladder §3 object; no localiser,
   no assignment); reproduces the reference energy to 10⁻⁹ E_h; along one totally symmetric, one
   degenerate and one non-symmetric benzene mode prints the continuity diagnostics (smallest
   singular value and largest pre-Löwdin off-diagonal of the overlaps) and E(A) − E(B), E(A) − E(C)
   per point (arms per Ladder §3), without a verdict; the raw displaced energies go to the sealed
   file, not to the printout. Fails → Ladder stop 1.
2a. **Lab-scoreboard re-read and u_band** (no compute; probes/README 2a): the plan-02 band
   table and the plan-04 NIST coverage scan regenerated under this plan's hash; per gas-phase
   band the stated resolution, centroid precision, temperature term and their quadrature sum
   u_band; the decidability verdict per family. Feeds pilot-note item 1.
3. **Gradient availability, run/no-run at equilibrium** (B2): for each candidate code (ORCA
   DLPNO, Psi4 DLPNO, MRCC LNO, PySCFAD LNO-CC), does an analytic gradient at the anchor level
   run **at the equilibrium geometry** of benzene and naphthalene, with frozen spaces? Prints
   run/no-run, version, wall-clock, peak memory. No displaced-geometry gradient is computed
   before the pilot note. The side project's M2–M5 later supply the answers at R0–R3.
4. **R0 pilot** (B2): geometry → DFT Hessian → harmonic bands, timed; one local-CC energy at
   benzene with frozen spaces — a timing only. **No local-CC Δ₂ and no pipeline-vs-lab number.**
5. **R1 smoothness probe** (B2, 72 local-CC energies of naphthalene = 4 modes × 9 points ×
   2 arms): four modes (C–C
   stretch, C–H stretch, CH-oop, one totally symmetric), nine points each at q ∈ [−1, 1],
   TightPNO, arms A and B of the Ladder §3 object (never arm C); the script prints **σ_E as the RMS residual about a
   degree-4 polynomial fit** per mode and arm, **and pooled per arm (ν = 16) — the pooled value is what is tested against
   the Q6 lines** at each grid step, the per-mode values printed and flagged if above twice the
   pooled (no σ_g exists before the note; mode G's constants are read at σ_g^assumed, Ladder §4
   item 8), and writes the **fit coefficients** (which
   contain the diagonal Δ₂ elements) to a hashed, sealed file opened only after the pilot note.
   Fixes the pattern amplitude.
6. **Pilot note committed** (the 2026-09-04 decisions recorded by reference).

After the pilot note:

7. **R0 probe batch and Q7 references** (B2): the first real `wall_clock_per_probe`, K(R0)
   under the noise-aware stopping rule, the cost record; the numerical local-CC and canonical
   Hessians (in the basis the feasibility probe allowed); Q7 printed for diagonal-only and full
   recovery; the diagonal-cubic bonus probe; the sealed smoothness fits opened; **side-project
   M2** (gradient correct against re-projected finite differences, under the mode-G noise line,
   with the projection term printed).
8. **R1**: canonical feasibility on the B2 laptop (the Q6/Q7 canonical arm at R1 exists only
   if it runs); R1 probe batch; Q7 twice; Q8(a/b) on the reference Hessian; Q6 threshold
   column; **side-project M3**.
9. **Anthracene direct-coupling probe** (dated bonus, B2 or B3 by the rule): the Q8(a)
   direct-coupling probe on anthracene with a deck-chosen pair list — four frozen-space local-CC
   energies per (pair, family), 4 × pairs × families, count printed (nine pairs and five families
   would be 180) — the cheapest direct test of whether the C–C couplings are long-ranged before
   R2 money is spent. (It is not a full Δ₂: that would be 1 + 2·66 + 4·C(66,2) = 8,713 energies.)
10. **R2/R3 classification** (B2 probe, then the rule decides, with c_CPS).
11. **R2**: the pyrene canonical diagonal check (two canonical CCSD(T) energies per mode in
    the R2 deck basis, one mode per family; B3 if the machine cannot); the Q6 noise grid at R2
    size in the mode(s) used; the direct-coupling probe (four energies per deck-chosen pair and
    family, step h); probe batch in mode E (and mode G if licensed) — structural recovery, and
    the prior-assisted recovery on the same responses for the licence-earning comparison;
    Q8(a/b) on direct couplings; Q8(c) R1→R2 per mode at the common threshold; **side-project
    M4** (nine gradients per Q6 mode, 36; classified by §2).
12. **R3**: direct-coupling probe; batch (both modes where licensed; both recoveries);
    **coronene probed from fragments at the smallest passing radius** and compared with
    coronene probed whole (fragment licence, part b: one comparison at one shell for interior
    pairs; "pending (b′)" if it fails); Q8(c) R2→R3 per mode at the common threshold;
    **side-project M5** (36 gradients at coronene with both checks; classified by §2).
13. **B3 probes** only after §1's three preconditions; the R4 DFT-Hessian timing probe decides
    whether the R6 Hessian is B3; at R4 the **fragment-vs-whole comparison on circumcoronene**
    (part b′, conditional on B3 classification) and the **fragment-radius convergence test on
    its central ring** (part c, first instance); at R6 the convergence test on the flake's
    interior (a probe batch classified by §2, 72 × families energies, ≈ 360 for five — expected
    laptop at one shell, B3 at two) and, where B3 allows, whole-flake direct couplings.

## 5. Protocol (carried)

- A timing quoted anywhere but a `probes/` script output is invalid.
- Time on a quiet machine or twice (plan-02 lesson: load produced a spurious 2× effect).
- Queue generously; order jobs by what they *decide*; spend human hours on judgement.
- Edit this file in place with a dated marker; the status line lists every revision.
