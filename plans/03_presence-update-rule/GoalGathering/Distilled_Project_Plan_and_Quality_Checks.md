# Distilled project plan and quality checks — Plan 03

Agrees with [`Overarching_Goal.md`](Overarching_Goal.md). If they drift, the Goal file wins and this file is patched. Numerical caps live in [`Compute_Budget_2026-09-01.md`](Compute_Budget_2026-09-01.md). The molecule ladder lives in [`Frozen_Ladder_and_Tolerances.md`](Frozen_Ladder_and_Tolerances.md).

**Status.** Draft. Not complete as a plan. Nothing here is a result.

---

## §1 Claim

A shared local stencil can step a 3-D presence-and-field state on a frozen grid with:

- a declared one-step error on H₂ (P1),
- a declared rollout horizon on H₂ (P2),
- a fixed-point test on the unperturbed ground state (P0),
- a zero-shot transfer report on H₂O (P3),
- a comparison to a frozen linear Maxwell+continuity stencil (P4).

Same weights for every cell, every time step, every molecule on the ladder. No molecule name as an input. No spectrum as a training target.

If a gate fails, the claim is the fail-closed sentence in §8, not a quieter product.

---

## §2 Question

> Does one local field rule, trained only on teacher time-evolution of presence and fields, stay a fixed point, roll out for a declared horizon on H₂, and transfer to H₂O better than a frozen linear constitutive stencil that sees the same teacher?

**Not the question.** Does a voxel PES beat MACE on IR peaks (plan 01). Does a CCSD(T) anchor buy anharmonic PAH bands (plan 02).

### §2.1 Prior art (working list; verify-on-use)

Identifiers are in [`Relevant_Scientific_Papers.md`](Relevant_Scientific_Papers.md). Do not cite them in a scored document until the Verify column is filled. Positioning, not a literature review:

| Neighbour | What it already does | What this thesis still asks |
|---|---|---|
| Real-space TDDFT (Octopus family) | Steps KS orbitals / density on a grid | Can a *shared local stencil* imitate one step without a new KS solve? |
| Maxwell–TDDFT | Lets \(\mathbf{E},\mathbf{B}\) live, not just Poisson | Use those channels as part of the *state*, not as a reconstruction of \(\rho\) |
| Neural TDDFT propagators (1-D public sets) | Learn a time step on published 1-D trajectories | Does the same idea hold in 3-D on H₂ → H₂O with a fail-closed certificate? |
| FNO / NCA | Global modes or local cell updates on fields | Default here is a *tiny local conv*, not a new operator family |
| Plan 01 field PES | Energy as a functional of \(\rho\) | Forbidden product. The field survives; the PES-to-IR product does not |

**What is not novel:** running TDDFT; storing cubes; training a 3-D CNN. **What is scored:** a frozen evaluation contract (P0–P4) on one shared rule, with an honest mean-field limit in the claim sentence.

Inconclusive on P3/P4 is publishable. It is not a licence to change the metric after the test.

---

## §3 Labels and teachers

Scientific labels = teacher time series from a **named code** and a **hashed input deck**. Module 02–04 tables are third-party public CSVs. They are not teacher cubes.

### §3.1 Recipe (frozen)

| Item | Choice |
|---|---|
| Code | **Octopus**. NWChem is not the teacher. |
| Functional | **ALDA** |
| Propagation | Real-time TDDFT |
| \(\mathbf{E},\mathbf{B}\) | Teacher **Maxwell–TDDFT**. Not Poisson. Not mixed mid-study. |
| Nuclei | Frozen **point charges**. They source \(\mathbf{E}\) only. |
| Grid | Cartesian, outer spacing \(0.20\,a_0\), nuclear refinement \(h(r)\sim 0.20\,a_0/Z\), box = molecule + \(\ge 6\,a_0\) vacuum, absorbing rim if ionising, **non-periodic** |
| \(\Delta t\) | Teacher \(0.05\) au. Learner \(k=1\). |
| H-atom | Analytic 1-e / grid TDSE. Diagnostic only. |
| H₂ | Octopus RT-TDDFT + Maxwell. **Promised** train + P0–P2. |
| H₂O | Same family. **Promised** P3 only. Never in the H₂ train hash. |
| Exact 2-e H₂ | Horizon 10. Not Module 08. |

Channels written every teacher step: \(\rho_-\), \(\mathbf{j}\), \(\mathbf{E}\), \(\mathbf{B}\). \(\rho_+\) is a bookkeeping channel (zeros / optional nuclear-smear diagnostic), not a second dynamical fluid.

### §3.2 Windows and splits

- Cut windows **after** Q0 is hashed.
- Train and test disjoint in **time**, then hashed (Q4).
- Second split by **kick protocol**: field-free / linear-response kick / resonant pulse, hashed.
- Water geometries absent from the H₂ train hash (Q5).
- Frame 0 of each teacher run must pass Q1 (electron count) and Q2 (dipole identity residual) before any window is labelled “train”.

### §3.3 If the teacher cannot be produced

Caps: 80 h human I/O; 168 h wall-clock for H + H₂ + H₂O. Escalation is §7.2. Do not coarsen the grid, drop Maxwell, or switch codes to keep the brand.

---

## §4 Deviations

A deviation is allowed only in writing, dated, with the probe that forced it. **A deviation note that changes a gate number, a split, or a frozen constant must be committed *before* the affected quantity is measured.** A note written after the number is known is not a deviation, it is a result being edited; the honest form of that is a failed gate.

Forbidden without a note:

- Compromising P0 to save P2.
- Changing the grid after Q0 is hashed.
- Turning the conservation penalty on after looking at a test window.
- Mixing Poisson into a Maxwell study.
- Putting water in the H₂ train hash.
- Quoting a spectrum, JWST, or C₃₈₄H₄₈ as a Module 08 result.
- **Loosening any P0–P4 number, in either direction, once the 8 h pilot has printed.**
- **Promoting the 5×5×5 comparison axis (or any other axis) to the thesis object after 3×3×3 has been scored.**
- **Editing the frozen linear baseline in `probes/linear_stencil.py` after Q0.**

Module 02 never sees a cube, so it cannot freeze one.

---

## §5 Architecture

The object is **one** translation-equivariant 3-D convolution.

### §5.1 State

**Eleven** channels, same order everywhere (2 densities + 3 current + 3 electric + 3 magnetic). The count is `len(grid_spec.CHANNEL_ORDER)`; no prose number overrides it. *Corrected 2026-09-01: this list was described as twelve in four places while enumerating eleven.*

\[
(\rho_+,\;\rho_-,\;j_x,j_y,j_z,\;E_x,E_y,E_z,\;B_x,B_y,B_z)
\]

Packing \(z=\rho_++i\rho_-\) is bookkeeping, not \(\psi\). Phase is **not** a promised channel (Horizon 10).

Drop \(\mathbf{B}\) only if a probe prints that it is numerically zero on the ladder. That drop is a §4 deviation.

### §5.2 Forward pass

- Input: the 11-channel tensor on the frozen grid at time \(t\).
- Operator: 3-D conv, **shared weights**, kernel **3×3×3**, padding that preserves the grid shape (periodic only if the teacher box is periodic; otherwise zero / absorb to match the teacher rim). The frozen box is finite, so **non-periodic is the default** and the learner and the P4 baseline must use the same boundary treatment.
- Output: the 11-channel tensor at \(t+\Delta t\). One forward pass = one teacher step (\(k=1\)).
- No per-cell Python loop. One conv over the volume (Q6 times this).
- Nuclei enter as **fixed point sources of \(\mathbf{E}\)**, not as atom-type features and not as a moving \(\rho_+\) fluid.

### §5.3 Baseline and comparison axis

- **P4 baseline:** frozen **linear** finite-difference stencil: continuity for \(\rho_-,\mathbf{j}\) plus discrete Maxwell for \(\mathbf{E},\mathbf{B}\), with a constitutive closure declared in the same hashed deck as the teacher (no learned coefficients). Implemented in [`probes/linear_stencil.py`](../probes/linear_stencil.py); after Q0 it is frozen (§4).
  - **Boundaries are non-periodic**, matching the frozen box. A periodic baseline conserves \(N\) to round-off by construction, which would make P0 on the baseline a test that cannot fail. *Corrected 2026-09-01: it was periodic, and P0 passed on random noise at \(4\times10^{-15}\).*
  - **Maxwell is leapfrogged and CFL sub-cycled.** At the frozen \(h=0.20\,a_0\) and \(\Delta t=0.05\) au the ratio \(c\,\Delta t/h = 34.26\), against an explicit 3-D limit of \(1/\sqrt{3}\approx0.577\). The baseline therefore takes \(\lceil 34.26/(0.5/\sqrt{3})\rceil = 119\) Maxwell sub-steps per teacher step. *Corrected 2026-09-01: forward Euler at one sub-step reached NaN inside the 200-step P2 horizon while P0 still printed pass.* The teacher's own integrator is Octopus's, not this one; the sub-cycling is a property of the baseline only.
- **Module 05 axis:** kernel **5×5×5**, everything else identical. Not an FNO unless a §4 note says otherwise. It is a comparison axis, not a fallback thesis object (§4).
- Fine-tune-on-water is a labelled ablation. It is not the P3 headline.

---

## §6 Training

Supervised one-step pairs from H₂ (optional H-atom) teacher windows only.

### §6.1 Loss

Weighted MSE on \(\rho_-\), \(\mathbf{j}\), \(\mathbf{E}\), \(\mathbf{B}\). Channel weights frozen before training. Default: equal weights on the four groups \(\{\rho_-\}\), \(\{\mathbf{j}\}\), \(\{\mathbf{E}\}\), \(\{\mathbf{B}\}\); \(\rho_+\) not in the loss.

**Conservation penalty off.** Turning it on requires a dated note *before* training, with the weight frozen then. P0 must not be trained into a tautology.

No spectral term. No molecule embedding. No test-window peeking.

### §6.2 Seeds, parity, stopping

- Seeds \(\ge 3\).
- Tuning budget equal to the linear baseline (the baseline has none: it is frozen). The learned rule may use a declared validation slice of the **H₂ train** windows only.
- Stop on that validation slice, never on H₂ test, never on H₂O.
- The 8 h P1 pilot runs on that same **train/validation** slice. It may not touch an H₂ test window or any H₂O window, so the P4 effect size declared after it is not declared after seeing the comparison it governs.
- Report mean ± SD across seeds for P1–P4.

---

## §7 Quality checks and gates

Scripts under `probes/`. A number that is not printed by a script is not a result.

### §7.1 Scripts (Q)

| ID | Script | Pass |
|---|---|---|
| Q0 | `grid_hash.py` | SHA256 of generator + \(0.20\,a_0\) + box + refinement rule is reproducible |
| Q1 | `electron_count.py` | \(\int\rho_-\) on frame 0 matches nominal \(N\) to a printed residual |
| Q2 | `dipole_identity.py` | residual of \(\boldsymbol\mu + \int\mathbf{r}\,\rho_-\,dV\) printed |
| Q3 | `p0_fixed_point.py` | relative \(N\) drift after \(T_0\) printed for linear stencil and, later, the learned rule |
| Q4 | `split_overlap.py` | prints `0` if train/test hashes disjoint |
| Q5 | same family | prints `0` if no water in the H₂ train hash |
| Q6 | timed conv — **script does not exist yet**; waits on a hashed PyTorch op | one training step is one conv over the volume |
| — | `teacher_cost.py` | wall-clock vs 168 h, or honest “not run” |

### §7.2 Gates (P) — fail-closed

Numbers Module 08 may quote now (pilot may only tighten):

| Gate | What | H₂ | H₂O |
|---|---|---|---|
| P0 | \(\lvert N(t)-N(0)\rvert/N(0)\) after \(T_0=200\) field-free steps | \(< 10^{-3}\) | \(< 5\times 10^{-3}\), **report only** |
| P1 | one-step relative \(L^2\) on \(\rho_-\) | \(< 5\times 10^{-3}\), \(\ge 3\) seeds | report only |
| P2 | same after \(T=200\) steps | \(< 5\times 10^{-2}\) or fail-closed | report only |
| P3 | P1-style, zero-shot | — | measured, then compared: beat linear stencil or **inconclusive** |
| P4 | learned vs linear, relative \(L^2\) | declared \(\Delta\), 3 seeds | same language |

P3 is one test with two parts, and both are reported: the **zero-shot error itself** (the Overarching Goal's definition) and the **comparison to the frozen linear stencil on the same windows** (its pass language). Neither part may be dropped because the other looked better.

If P0 fails, P2 is not interpreted. Energy drift is reported, not a hidden gate.

### §7.3 Escalation (declared in advance)

1. Octopus+Maxwell cannot be installed inside the caps → **stop**. Name the missing binary. Do not Poisson.
2. First H₂ window exceeds 168 h wall-clock → **stop**. Do not coarsen \(0.20\,a_0\).
3. Human grid+teacher I/O exceeds 80 h → **stop**. Do not redesign the grid.
4. P0 fails on the linear stencil → the teacher or the grid is wrong, not the learner; do not train. Any repair to the grid after Q0 is a dated §4 note, exactly as in rungs 2 and 3 — this rung is not a licence to re-cut the grid quietly.
5. P0 fails only on the learned rule → fail-closed; do not interpret P2.
6. P3 does not beat the linear stencil → **inconclusive**. That is a result.
7. Teacher itself is grid-divergent (Q1/Q2 blow up when spacing is audited) → dated §4 note. Redesign is not silent.

Stopping is a result. Extending the ladder quietly is not.

---

## §8 Module 08 verdict language

Use one of:

- “P0 and P1 passed on H₂; P2 passed / failed; P3 transfer vs linear baseline: win / lose / inconclusive.”
- “Teacher cap exceeded; the plan stopped at rung \_\_.”

No third sentence that smuggles a spectrum.

Claim ladder (strongest at the top; a lower rung may be claimed only if every rung above it held or was explicitly marked failed):

1. Q0–Q5 passed on the hashed corpus.
2. Linear stencil P0 printed.
3. Learned rule P0, P1 on H₂.
4. Learned rule P2 on H₂, **or** fail-closed.
5. P3/P4 on H₂O: win / lose / inconclusive.

Forbidden quotes: see Overarching Goal. Mean-field closure stays in the claim sentence.

---

## §9 Non-claims

- Mean-field / TDDFT-like world. Not many-electron correlation. Not exact 2-e motion.
- Frozen point nuclei on the scored window. Not Ehrenfest. Not quantum nuclei.
- Not QED. Maxwell here is classical fields coupled to a TDDFT current.
- Not JWST. Not PAHdb identification. Not anharmonic IR.
- Not C₃₈₄H₄₈. Horizon 12 may report wall-clock of one conv step vs one TDDFT step, nothing else.
- Not “the grid was the contribution.”
- Not “one net \(\rho\) is enough.”

The industry sentence, if used: a **reliability-gated surrogate propagator** with a published fixed-point and rollout certificate. Not drug discovery. Not PAH-ID-as-a-service.
