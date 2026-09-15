# Compute budget — Plan 05 (14 September 2026)

**Status.** The compute budget of plan 05 as it stands on 14 September 2026, written as one document for the supervisor. It states the three budgets, the rule that decides where a computation may run, what has been measured so far on the student's machine, what the external routes would cost by estimate, and the operating rules for long runs. Caps and checkpoints are rules, not estimates; every measured number names the script that printed it, and a quantity no probe has printed reads NOT_RUN. The working record behind this document, with its measurement log, is `Compute_Budget_2026-09-03.md`; the Ladder (`Frozen_Ladder_and_Tolerances.md`) is the single binding statement of every rule, and this document cites it rather than restating it. Notation (K, K_off, K_cap, ρ\*, mode E/G) is defined in the Goal and the Ladder.

---

## 1. Three budgets

| Budget | Currency | Rule | Governs |
|---|---|---|---|
| **B1 human** | attention hours | **uncapped, logged**: one bucket per entry; when plumbing dominates the log a written review is triggered, never a ceiling. A separate bucket, "side project: mode G", covers milestones M2–M5, with a 12-week calendar checkpoint from the pilot note's commit date and a 4-weekly alarm | everything a person does |
| **B2 own machine** | wall-clock hours on the machine the student owns | **168 hours per rung pilot is a checkpoint, not a kill**: crossing it forces a written decision — continue knowingly, reroute to B3, or stop | DFT Hessians through R3, dry runs, R0–R1 probes, ML training |
| **B3 external** | cluster core-hours and rented GPU-hours | **no number until three things exist in writing**: (a) access — an allocation, or a spend cap for rented time; (b) a timed probe on the actual machine, printed by a script; (c) a per-rung cap derived from it | local-CC probe batches that do not fit B2; the reach rungs, including their DFT Hessians; GPU canonical-CC licence runs |

**The B2 machine.** An ASUS Vivobook 18 (M1807HA): AMD Ryzen 7 260 at 3.8 GHz, 8 cores / 16 threads; integrated Radeon 780M graphics (512 MB, no CUDA-class GPU); 32 GB DDR5-5600 (31.3 GB usable); 954 GB SSD with about 790 GB free. The laptop is dedicated to the capstone and available around the clock (the student works weekdays on a separate client machine), so long runs start on any day and are checked asynchronously; the 168-hour threshold is reached in seven calendar days. Because the laptop has no CUDA-class GPU, every GPU DFT Hessian is a B3 object (rented), and the CPU path is the B2 default for DFT Hessians through R3. A workstation has been priced (`notes/Hardware_Note_2026-09-10.md`: 16 cores, 128 GB, about €4,700 with a UPS) and is **not bought**; it would become B2 by a written decision naming it, taken only after evidence and the supervisor's approval, and nothing about B2 is a precondition of the plan.

**Software on B2.** Windows side: a conda environment `qc` with psi4 1.11 (DFT Hessians, the dry runs, the R0 pilot's DFT part, the Module 05 corpus). Linux side, needed because the anchor code runs on Linux only: WSL 2 with Ubuntu, a Python 3.12 environment `~/qc05` holding pyscf 2.14.0, pyscf-forge 1.1.1 (`pyscf.lno`, LNO-CCSD(T)), pyscfad 0.3.3 (the side project), JAX, NumPy, SciPy, h5py, gfortran, OpenBLAS; a second environment `~/qcad` for the gradient-cost measurement. The engine line printed in every record is **"pyscf 2.14.0 + pyscf-forge 1.1.1 + plan-05 patch 1"**: the patch (`probes/patches/`) restores an interface between pyscf-forge's out-of-core LNO path and pyscf 2.14's density-fitted CCSD, which is taken only when a fragment's four-virtual block does not fit in memory — the first naphthalene fragment of that size exposed it. WSL is given 25 GB of the 31.3 GB and 16 processors, with an 8 GB swap; Windows keeps about 6 GB. The repository is at `/mnt/c/Users/<user>/Documents/CapstonePlan`; the PyPI versions are the pins until the deck names commit hashes. **Invocation without conda activation** (the `conda` command is not on the PATH of the automated shells; found 13–14 September): `C:\ProgramData\anaconda3\Scripts\conda.exe run -n qc python …`, or the environment's own `python.exe` with `<env>\Library\bin` prefixed to PATH (without it psi4 fails at the first integral call with a delay-load DLL error); WSL scripts are launched through `probes/launch_detached.sh` (`PYBIN=~/qcad/bin/python` selects the PySCFAD environment).

**Rented GPU time** is a B3 object because it is bought, not because it is remote; the same three preconditions apply, with a money cap where an allocation would stand.

## 2. The classification rule (arithmetic, not judgement)

With K_cap for the rung and mode fixed in the pilot note (Ladder §4.9) and the wall-clock per probe printed by the timed probe for that rung, mode and machine:

```
wall_clock_per_probe × K_cap(rung, mode) × c_CPS  >  168 h   →   the probe batch is a B3 object
```

where c_CPS = 2 if Q6's threshold line made CPS extrapolation mandatory at that rung's size class, else 1. If a batch classifies as B3 and B3's preconditions are unmet, the rung waits or stops by written decision, and the wait is reported. The rule never kills a rung by itself; K_cap may not be lowered to pass it, ρ\* may not be raised, and CPS may not be dropped (Ladder stop 2). Both modes are classified separately; K_cap(G) is filled for every rung from the gradient-mode noise-injected dry run and is simply unused where mode G is not licensed.

## 3. What the cost picture is, measured and estimated

### 3.1 Measured on the B2 laptop (each line names its script; 8 threads unless stated)

| quantity | value | script / record |
|---|---|---|
| LNO-CCSD(T) energy, benzene, cc-pVDZ (114 basis functions), tight thresholds | 180 s, 1.2 GB peak; LNO − canonical 16 µE_h | `anchor_single_point_timing.py` |
| LNO-CCSD(T) energy, benzene, cc-pVTZ (264 bf), tight | 2,087 s, 5.5 GB peak; LNO − canonical 124 µE_h | same |
| canonical CCSD(T) energy, benzene, cc-pVTZ | 755 s idle, 850–1,272 s with the laptop in use; 7.3 GB | same; probe M1's truth line |
| canonical CCSD(T) analytic gradient, benzene, cc-pVDZ | 1,399 s, **13.9 GB** resident — about 50 energies' worth in this implementation | `canonical_gradient_timing.py` |
| canonical CCSD(T) gradient, benzene, cc-pVTZ | exceeded 20 GB before the gradient stage; **does not fit** this laptop | same (attempted) |
| probe M1, one three-arm point, benzene cc-pVTZ tight | 5,944–7,093 s; the 27-point scan 48 h; the 27-point canonical truth line 8.1 h; the chain 58 h without failure | `m1_frozen_spaces.py`, `results_m1/` |
| frozen-arm point at the anchor thresholds (xtight, [10⁻⁷, 10⁻⁸]), benzene cc-pVTZ | 4,576 s median, about 2 × the tight arm-A point (≈ 2,200 s) | `results_m1/XTIGHT_READIN.md` |
| one xtight energy for the R0 pilot deck, benzene | ≈ 75 min | derived from the line above |
| LNO-CCSD(T) energy, **naphthalene**, cc-pVTZ (412 bf, 24 fragments), tight | **41,375 s = 11.5 h, peak 19.83 GB** | `results_timing/naphthalene_ccpvtz_tight.log`, `naphthalene_cc-pvtz_tight.json` |
| the same energy at the anchor thresholds (xtight) — the factor **F** over tight | **138,305 s = 38.4 h of fragment solves (24 fragments, 35–239 min each), F = 3.34**; peak 15.35 GB with `--max-memory 16000` (out-of-core); finished 14 September 07:49. Like for like: the tight energy ran in-core in one segment, so F carries the out-of-core path as well as the thresholds (the benzene factor at equal settings ≈ 2). E_corr(T) −1.6870085 against −1.6866006 at tight | `results_timing/naphthalene_ccpvtz_xtight.log`, `naphthalene_cc-pvtz_xtight_fragments.json` |
| B3LYP/6-31G* Hessians with psi4 1.11 (frequency jobs including optimisation), provenance from plan 02 on this laptop | benzene 4.2 min, pyrene 54 min, tetracene 72 min, chrysene 75 min, triphenylene 72 min, coronene 174 min | plan 02 batch record; re-timed by a plan-05 probe before use |
| the two basis terms of decision 33 per naphthalene point (DF-MP2 at cc-pVQZ, 790 bf; DF-SCF at cc-pV5Z, 1,350 bf) | 60 s + 353 s ≈ 7 min — negligible beside the 38 h anchor energy | `results_timing/naphthalene_cc-pvtz_xtight.json` |
| Module 05 corpus factory, B3LYP/6-31G* Hessian per molecule (layers A/A′/B) | 3–7 min | `modules/05_support_predictor/corpus/` timing test (five molecules) |

**Consequences of the measurements.** (i) A local-CC energy at the anchor basis costs three times a canonical one at benzene: locality pays only at larger molecules, so probe M1 was developed at cc-pVDZ and run once at cc-pVTZ. (ii) The full canonical reference Hessian of benzene at cc-pVTZ is reachable by neither branch on this laptop — 1,801 energies × 755 s ≈ 378 h, or 72 gradients that do not fit in memory — while the Q6 bias line (61 energies, ≈ 12.8 h) fits; the R0 comparisons are drawn accordingly (Ladder §3). (iii) At R1 the full deck of 474 energies at tight thresholds is 5,450 laptop-hours ≈ 227 days, thirty times the 168-hour checkpoint; at the anchor thresholds it is F times more. (iv) Pyrene (620 basis functions) will not fit the laptop's memory at all. (v) The naphthalene energy is out-of-core for its largest fragments (resident 3–12 GB, scratch up to 37 GB in `~/qc_tmp`), which is why it fits under the 25 GB ceiling at all.

### 3.2 The anchor's thresholds and what they cost

The anchor runs at the tighter LNO thresholds [10⁻⁷, 10⁻⁸] ("xtight"): the benzene rescan brought the composite frequency bias from +0.47 / +0.03 / +0.79 to +0.11 / −0.01 / +0.23 cm⁻¹ on the three test modes with the smoothness unchanged (decision 20). The price is F per energy: about 2 at benzene at equal settings, and **3.34 at naphthalene as measured on 14 September** (with the out-of-core path in the ratio). Every naphthalene price below is therefore 11.5 h × 3.34 = 38 h per energy; the R1 deck of 474 energies is ≈ 18,200 laptop-hours ≈ 760 days.

### 3.3 The planning expectation for mode E (the measured dry-run count)

The benzene dry run (DFT − DFT stand-in) recovered the full correction with K_off = 388 energies for 435 off-diagonal unknowns at ρ_off ≤ 0.3 — the sparsity saving of a banded prior at R0 is nil. The plan therefore budgets mode E with **K_off ≈ M(M−1)/2 energies where no prior demonstrably bites** (naphthalene 1,128, pyrene 2,556, coronene 5,151) and, where the symmetry prior applies (decision 11), with the free-element count it leaves: same-representation pairs only, printed per rung beside the deck's off-diagonal count. At R1 that prior leaves 141 eligible pairs (D₂h, 48 modes), i.e. a deck of 4M + 2E = 474 energies against 1 + 2M + 4·M(M−1)/2 = 4,609 without it. The symmetry prior is what puts mode E on R1–R3 inside the 168-hour rule on any machine, not sparsity as such; the size sentence of the Ladder remains a measurement at R1–R3 and is expected to be earned, if at all, through the prior.

### 3.4 Literature figures (motivation only; none is in the plan's unit)

| quantity | literature figure (not this project's) | plan-05 slot |
|---|---|---|
| energy-only diagonal Δ₂ in the DFT mode basis | arithmetic: 2M energies (naphthalene 48 modes, pyrene 72, coronene 102, C₃₈₄H₄₈ 1,290) — the CMA-0 count | the mode-E floor, fixed by M |
| off-diagonal count | Sanders et al.: ~30 % of columns on anthracene in a cheap-method eigenbasis, ~log growth to 15 rings (DFT level); CMA-2: selected off-diagonals cost +33 % over diagonal-only for a mean maximum error of 0.17 cm⁻¹ | **K_off** per rung — the quantity Q8(c) tests |
| gradients for a full Hessian, DFT level | O1NumHess: 40–120 gradients for hundreds of atoms; error about twice a conventional finite-difference Hessian's | K(G) per rung; mode G is built in the side project |
| local-approximation error growth | DLPNO error on acenes grows ≈ linearly with ring count; CPS(6/7) reduces it at 2 × cost | Q6 threshold line; c_CPS |
| DFT Hessian on GPU | GPU4PySCF: about 30 × over a 32-core node | B3 (rented) at every rung; the CPU Hessian timing through R3 is the B2 slot; R6 (C₃₈₄H₄₈: 3,552 basis functions at 4-31G, ≈ 1,300 perturbations) is B3 unless a timed probe at R4 shows otherwise |
| canonical CCSD(T) on GPU | TeraChem: 63 atoms, > 1,000 basis functions, (T) in ≈ 8 h on one node | Q6 licence-reference timing at pyrene — B3 |
| local-CC(T) gradient | PySCFAD ships an LNO-CC module with (T) and is reported to 29 atoms; the ratio of a gradient's cost to an energy's is printed nowhere in the literature | the side project's first measurement (M2a, pre-registered: `notes/PreRegistration_2026-09-13_M2a_Gradient_Cost_Ratio.md`) |

**Units.** K and K_off are counted in energies (mode E; a ± pair counts 2) or gradients (mode G). Sanders counts Hessian columns, O1NumHess gradients (one gradient = 3N responses), CMA-2 selected off-diagonal elements (each costing four energies). Every off-diagonal response costs two energies by design; the dry run measures K_off, and the plan claims no number for it in advance.

### 3.5 The external route by estimate: Snellius (an orientation column, not a budget)

Facts from the SURF documentation (read 12 September 2026): Snellius has 525 "thin" Rome nodes (2 × AMD 7H12, 128 cores, 256 GiB), 738 "thin" Genoa nodes (2 × AMD 9654, 192 cores, 384 GiB), 72 + 48 "fat" nodes (1–1.5 TiB) and a few 4 TiB nodes; usage is charged in SBU, in practice one core-hour; an NWO **Small Compute** application grants up to 1,000,000 SBU with 200 GB of storage. Against those facts the laptop's measured numbers (naphthalene 41,375 s per tight energy on 8 cores ≈ 90 core-hours) give the following **estimates**, with stated assumptions: a Rome core slightly slower per clock than the laptop's; the 24 fragments of one energy spread over one node; a factor 2 for parallel inefficiency; F applied once measured.

| rung | laptop (measured) | Snellius (estimate) |
|---|---|---|
| R0 benzene | all of it; largely done | not needed |
| R1 naphthalene | 11.5 h per tight energy, 19.8 GB; 38 h per anchor energy (F = 3.34), 15.4 GB; the 474-energy deck ≈ 18,200 h ≈ 760 days | ≈ 700–1,000 SBU and 5–8 h wall per anchor energy on one thin node → ≈ 330,000–500,000 SBU for the deck; 25–41 days on four nodes; inside one Small Compute application (1,000,000 SBU) with the pilot and the thin decks, but no longer with room to spare |
| R2 pyrene | does not fit 25 GB | memory no obstacle; per energy an unmeasured 5–10 × naphthalene and a larger deck (72 modes) → order 1–2 million SBU: the edge of one application, or a second after the R1 result |
| R3 coronene | does not fit | thin nodes suffice for memory; per energy a further multiple → several million SBU: a Large Compute application, or the family- and mode-selective scoring the Ladder foresees |

R1 is small on Snellius; the step to R2 and R3 is an SBU question, which is what Q8 measures (does the energy count stop growing with size). **The first job on any allocation is one timed naphthalene energy on the actual node**, a few hours, which turns this column from estimate into measurement. The per-step table by route (laptop / desktop / Snellius, through Module 08) is printed by `probes/duration_table.py` into `probes/results_timing/DURATION_TABLE.md` and reprinted whenever a timing changes.

**What the priced workstation would and would not measure.** It would run the whole R1 deck in months of continuous use (an estimate from the core count, not a timing), time one pyrene energy (128 GB suffices; half a day to a day), replacing the "5–10 ×" above by a number, and measure the core scaling and fragment-parallel efficiency assumed above. It would not measure the Snellius numbers themselves (different processor, memory bandwidth, node size); the extrapolation would shrink from a factor ten to a factor two. The Module 05 corpus factory and the naphthalene dry run want the same machine, so R1 alone on the desktop is nearer four months or moves partly to the cluster.

### 3.6 Accepted items with prices

- **The R0 pilot's substitution comparison (decision 34):** by energies, 6 Hessian–vector products × ≈ 4M = 24M ≈ 720 energies at benzene (≈ 1.6 decks; a laptop-week at ≈ 75 min per xtight energy), or 12·g energy-equivalents with the side project's gradients; the energies-only price is paid only if M2 has not licensed gradients by then.
- **The R1 smoothness σ (decision 35):** a 9-point tight scan of one mode at naphthalene: 9 arm-A energies + 1 reference ≈ 10 × 11.5 h ≈ 4.8 laptop-days, after the naphthalene DFT dry run (two functionals, hours); the 27-point xtight scan the Ladder implied (≈ 50 days) is not run on the laptop.

## 4. Operating rules for long runs on B2 (each learned from a measured failure; all in force)

1. **Memory.** With WSL at 25 GB, Windows keeps about 6 GB; Windows terminates the whole WSL virtual machine — no Linux out-of-memory message, no traceback, a clean-looking exit — when its own memory runs out (Resource-Exhaustion-Detector event 2004). Therefore: anchor-level jobs run **one at a time**; while one runs, **no process over about 1 GB is started on the Windows side** (no Lean/Mathlib builds, no PDF rendering, no large notebooks, no psi4), and **no file above about 100 MB is parsed on the Windows side** — large inputs are cut with `sed`/`grep` first. Jobs that need more than the ceiling do not fit this laptop; pyscf's `max_memory` is set (16,000 MB) so that large integral blocks go to disk.
2. **Completion is read from the result files, never from the exit code**, because a VM kill looks like a clean exit to the harness.
3. **Launch detached.** Long runs start through `probes/launch_detached.sh` (own session via setsid and nohup; the log names the start time), because a run dies with the terminal session that started it.
4. **Hourly heartbeat.** Every run expected to last more than an hour leaves a line in its log at least once an hour (elapsed, CPU, resident memory, scratch size; the python step prints its own progress per point or per LNO fragment).
5. **Checkpoint and resume.** LNO energies are checkpointed per fragment (`probes/lno_checkpoint.py`; tested on benzene: abort after 2 of 15 fragments, resume, energies identical to 0.000 nE_h); scans write per-point results; an interrupted run is resumed with `--resume` and loses at most the fragment or point in progress. The wall-clock of a resumed energy is the **sum of fragment times from the checkpoint**, not the calendar span.
6. **Announce and check.** A long run is announced with its expected end time; before switching the laptop off, running jobs are listed with `wsl -e bash -c 'ps -eo etime,rss,cmd | grep "[p]ython"'`; a WSL session's processes die with the session leader, so a chain shell is never killed while a wanted child runs.
7. **Host and application updates** are applied only between runs, with nothing running.
8. **Scratch.** Out-of-core fragments write tens of gigabytes to `~/qc_tmp` on the WSL disk (never to the 14 GB `/tmp` tmpfs); scratch is checked and cleared between runs.

## 5. Timed probes: measured and remaining (each prints machine, date, settings, wall-clock; gradient probes also peak memory)

**Done before the pilot note.**

1. **Zero-CC dry run at benzene, mode E, with the noise-injection column** (B2): Δ between B3LYP and BHHLYP at 6-31G*, recovered by the plan's own solver from a hashed, ordered pattern set with seeded hold-out; responses are the symmetric ± combinations exactly as in the real run; noise injected per energy, K and ρ printed per σ_E; the DFT-arm floor printed. Measured: K_off = 388 for 435 unknowns at ρ_off ≤ 0.3 (§3.3). The naphthalene dry run (stage A, the tensor) is the next DFT job.
2. **Canonical feasibility probe** (B2): the bias line fits (61 energies ≈ 12.8 h), the full canonical reference does not (§3.1, consequence ii).
3. **Probe M1 — frozen spaces** (B2): the spaces stored at the reference geometry and transported by projection with Löwdin orthonormalisation; reference energy reproduced to 10⁻⁴ µE_h on reload; along three benzene modes the frozen arm scatters by 0.002–0.06 µE_h about a smooth curve where re-selection scatters by 7–11 µE_h at default and 0.9–2.7 µE_h at tight thresholds; frequency bias against canonical CCSD(T) +0.11 / −0.01 / +0.23 cm⁻¹ at the anchor thresholds; the cheap basis line (SCF and MP2 to cc-pV5Z at the same 27 points, 19 minutes) puts the basis term at 3–11 cm⁻¹ (decision 33).
4. **Laboratory scoreboard and u_band** (no compute; Module 03): band-centre uncertainties per gas record and family; decidability per family.
5. **Anchor timing at R1** (B2): one naphthalene energy at tight (§3.1); the xtight energy in progress (F).

**Remaining before the pilot note.**

6. **Gradient cost ratio g** (B2, `~/qcad`, pre-registered M2a): PySCFAD's shipped LNO engine, benzene cc-pVDZ, cells 0–4, thresholds g ≤ 6 / ≤ 20 / > 20 fixed before the run; decides whether the frozen-space gradient (M2) is built.
7. **Naphthalene DFT dry run, stage A** (B2, hours): the second functional's Hessian (the B3LYP half exists); then the symmetry-pattern counts and the pre-registered tensor battery on it.
8. **R0 pilot** (B2): geometry → DFT Hessian → harmonic bands, timed; one local-CC energy at benzene with frozen spaces — a timing only; no local-CC Δ₂ and no pipeline-vs-lab number before the note.
9. **R1 smoothness σ** (B2, decision 35, 4.8 laptop-days): fit coefficients to a hashed, sealed file opened only after the pilot note.
10. **Pilot note committed.**

**After the pilot note.**

11. **R0 probe batch and Q7 references** (B2): the first real `wall_clock_per_probe`, K(R0) under the noise-aware stopping rule, the cost record; Q7 for diagonal-only and full recovery; the substitution comparison (decision 34); the sealed smoothness fits opened; side-project M2 if licensed by g.
12. **R1**: probe batch (B2 for what fits, else B3 by §2); Q7 twice; Q8(a/b); the Q6 threshold column; side-project M3.
13. **Anthracene direct-coupling probe** (B2 or B3 by the rule): four frozen-space energies per (pair, family) on a deck-chosen pair list — the cheapest direct test of whether the C–C couplings are long-ranged before R2 money is spent.
14. **R2/R3 classification** by §2 with c_CPS; R2 and R3 as the Ladder states them (canonical diagonal checks, direct-coupling probes, batches in mode E and, where licensed, mode G; coronene probed from fragments and whole; side-project M4/M5, each classified by §2).
15. **B3 probes** only after §1's three preconditions; the R4 DFT-Hessian timing decides whether the R6 Hessian is B3; the fragment-vs-whole comparison on circumcoronene and the fragment-radius convergence tests at R4 and R6.

## 6. Protocol

- A timing quoted anywhere but a `probes/` script output is invalid.
- Time on a quiet machine or twice (a loaded machine once produced a spurious factor of two).
- Queue generously; order jobs by what they *decide*; spend human hours on judgement.
- A measured slot that has not been printed reads NOT_RUN; an estimate is labelled as one and names its assumptions.
