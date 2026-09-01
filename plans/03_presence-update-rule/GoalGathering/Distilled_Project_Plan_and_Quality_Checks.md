# Distilled project plan and quality checks — Plan 03

Agrees with `Overarching_Goal.md`. If they drift, the Goal file wins and this file is patched.

## §1 Claim

A shared local stencil can step a 3-D presence-and-field state on a frozen grid with a declared one-step error on H₂, a declared rollout horizon, a fixed-point test on the unperturbed ground state, and a zero-shot transfer report on H₂O.

## §2 Question

Does locality-plus-fields transfer across molecules better than a frozen linear constitutive stencil, when both see the same teacher?

Not: does a voxel PES beat an equivariant GNN on IR peaks.

## §3 Labels and teachers

- Scientific labels = teacher time series from a named code and a hashed input deck.
- Teacher code: **Octopus**. Functional: **ALDA**. Same grid family on H₂ and H₂O.
- H₂ teacher: Octopus RT-TDDFT. Exact two-electron evolution is **not** the Module 08 teacher; it is Horizon 10 / the H-atom diagnostic.
- H₂O teacher: Octopus RT-TDDFT, same grid family.
- Density and current come from the teacher. \(\mathbf{E},\mathbf{B}\) come from the **teacher Maxwell–TDDFT solver**, hashed with the deck. Do not mix in a Poisson reconstruction mid-study.
- Nuclei are frozen point charges on the scored window. They source \(\mathbf{E}\) only.
- Module 02–04 labels are third-party public tables. They are not teacher cubes.

## §4 Deviations

A deviation is allowed only in writing, dated, with the probe that forced it. Compromising P0 to save P2 is forbidden. Changing the grid after **Q0 is hashed** (Module 05 scientific corpus) is a deviation. Module 02 never sees a cube, so it cannot freeze one.

## §5 Architecture

- Default: 3-D convolution, kernel **3×3×3**, shared weights, 12 channels as declared.
- State channels: \(\rho_+\), \(\rho_-\), \(j_x,j_y,j_z\), \(E_x,E_y,E_z\), \(B_x,B_y,B_z\) (12). Drop \(\mathbf{B}\) only if a probe shows it is numerically zero on the ladder; that drop is a deviation.
- Optional packing \(z=\rho_++i\rho_-\) is bookkeeping, not \(\psi\).
- One forward pass per time step over the whole tensor. No per-cell Python loop.
- Learner \(k=1\): one forward pass = one teacher \(\Delta t = 0.05\) au.
- Baselines: linear finite-difference stencil (continuity + Maxwell). The single Module 05 comparison axis is kernel **5×5×5**, not an FNO, unless a §4 note says otherwise.

## §6 Training

- Loss: weighted MSE on \(\rho_-\) and \(\mathbf{j}\); \(\mathbf{E},\mathbf{B}\) are teacher Maxwell channels and **are** in the loss.
- Conservation penalty on \(N=\int\rho_-\) is **off**. Turning it on requires a dated note before training, with the weight frozen then.
- Seeds \(\ge 3\). Tuning parity with the baseline. No test-window peeking.

## §7 Quality checks (must all be runnable scripts under `probes/`)

| ID | Check |
|---|---|
| Q0 | Grid hash reproducible from the generator (Module 05 scientific corpus, not Module 02) |
| Q1 | \(\int\rho_-\) equals electron count on teacher frame 0 |
| Q2 | Dipole identity holds on teacher \(\rho_-\) to a stated residual |
| Q3 | P0 script exists and writes a number |
| Q4 | Train/test hashes do not overlap |
| Q5 | Water geometries do not appear in the H₂ train hash |
| Q6 | One training step is one conv over the volume, timed |

## §8 Module 08 verdict language

Use one of:

- “P0 and P1 passed on H₂; P2 passed / failed; P3 transfer vs linear baseline: win / lose / inconclusive.”
- “Teacher cap exceeded; the plan stopped at rung \_\_.”

No third sentence that smuggles a spectrum.

## §9 Non-claims

Mean-field closure. Frozen nuclei on the attosecond window (unless a named probe includes Ehrenfest). No QED. No JWST. No C₃₈₄H₄₈.
