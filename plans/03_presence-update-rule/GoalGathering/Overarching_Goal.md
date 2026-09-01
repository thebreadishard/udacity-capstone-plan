# Overarching Goal — Plan 03 Presence-Update-Rule

**Status.** Current plan as of 2026-08-29; contradiction pass 2026-09-01. Supersedes plan 02.  
**Not complete as a plan.** This file is the prime directive. Distilled Plan §2 and §9 must agree with it.

## Prime directive

Learn **one** local presence-update rule on a frozen 3-D grid.

The rule maps the neighbourhood of a cell — net-plus density, net-minus density, current, electric field, magnetic field — to the same quantities in that cell one electronic time step later. The same weights apply to every cell, every time step, every molecule on the ladder.

The scientific question is **not** “can a voxel PES beat MACE on IR peaks” (plan 01) and **not** “can a measured CCSD(T) anchor buy anharmonic PAH bands” (plan 02). It is:

> Does a shared local stencil, trained only on teacher time-evolution of fields and presence, remain a fixed point on an unperturbed ground state, roll out for a declared electronic horizon on H₂, and transfer to H₂O without being retrained on water’s chemistry?

No spectrum is a training target. No molecule name is an input feature.

## What this is

A computational-physics *and* deep-learning thesis whose industry frame is a **reliability-gated surrogate propagator**: one GPU convolution per attosecond-scale step instead of one electronic-structure call per step.

The physical content, stated without software:

- On one point in space an electron does not feel twelve labelled forces. It feels one \(\mathbf{E}\) and one \(\mathbf{B}\).
- Plus and minus must not be summed into one net \(\rho\) before the update. A proton-plus-electron cell is not empty vacuum.
- Presence \(\rho_-\) is real. Current \(\mathbf{j}\) is a real vector. The complex \(\psi\) is a packaging of presence and phase; phase is not optional if the next step is to be determined.
- The many-electron “if I am here, where is he” correlation is **not** promised. The 3-D field is a closed mean-field / TDDFT-like world. That limitation is in the claim sentence, not in a footnote.

## Promised Module 08 exit

A scored stack that contains all of the following, or an explicit fail-closed sentence naming which gate failed:

1. Frozen grid specification (hash of the generator script + spacing + box + nuclear-refinement rule). The grid is a constant. Q0 hashes it when the scientific corpus is built (Module 05). It is not a research object after that hash. Module 02 is a public table and does not freeze the grid.
2. Teacher trajectories for **H atom** (analytic / 1-e sanity), **H₂** (Octopus RT-TDDFT, ALDA, frozen grid), **H₂O** (same teacher family).
3. One shared conv-stencil trained on H₂ (and optionally H-atom) teacher pairs \((\text{neighbourhood}_t \to \text{cell}_{t+\Delta t})\).
4. Pre-registered tests, frozen before training:
   - **P0** fixed point: unperturbed ground-state rollout may not drain or create more than \(\varepsilon_N\) electrons in \(T_0\) steps.
   - **P1** one-step: next-cell error vs teacher on a held-out H₂ time window, \(\ge 3\) seeds, declared MAE / relative \(L^2\).
   - **P2** rollout: error vs teacher after \(T\) steps on H₂, same seeds.
   - **P3** transfer: the H₂-trained rule, **untrained on water**, scored on H₂O teacher windows (zero-shot). Fine-tune-on-water is a labelled ablation, not the headline.
   - **P4** baseline: the learned rule vs a frozen linear stencil (finite-difference continuity + Maxwell + a declared constitutive closure). Inconclusive is a valid outcome.
5. An honest scope sentence: C₃₈₄H₄₈, anharmonic IR, and JWST/PAHdb identification are why a later worker would care. They are not capabilities built in Modules 02–09.

## Forbidden quotes (this thesis)

Do not write any of the following as a Module 08 result:

- “We identified PAHs in a JWST spectrum.”
- “Chemically precise anharmonic infrared lines.”
- “The network learned many-electron correlation.”
- “One \(\rho\) for plus and minus is enough.”
- “The grid was the contribution.”
- “C₃₈₄H₄₈ was simulated with the learned rule.”

## Why 02 is superseded

Plan 02 is complete as a plan and blocked on measurement: a coupled-cluster rung that must be *measured* before the module map can be written, plus a locality assumption that already failed on a published PAH band family. That is a wall in the *label factory*, not in the learner.

Plan 03 moves the scarce resource to a question that Modules 03–06 can actually score: a local dynamical rule with public-or-generated-computational trajectories, a frozen discretisation, and tests that do not wait on a 31 GB in-core CCSD(T) naphthalene.

Plan 01 already died on the other wall: two-thirds of 840 h spent making voxels respectable so that a spectrum could be read off. Plan 03 forbids that spend. The grid is frozen when Q0 is hashed (Module 05 scientific corpus) and then only *audited*, never redesigned, unless a probe shows the teacher itself is grid-divergent. Redesign requires a written deviation under Distilled Plan §4. Module 02 does not touch cubes.

## What is inherited

From 01 and 02, method-agnostic and kept:

- measured-not-asserted arithmetic in `probes/`
- never cite from recall; DOI before claim
- pre-registration, frozen splits with hashes, \(\ge 3\) seeds, tuning parity
- declared effect size; inconclusive is publishable
- escalation ladders declared in advance; stopping is a result
- fail-closed reporting
- the exact dipole identity \(\boldsymbol\mu = -\int \mathbf{r}\,\Delta\rho\,dV\) as a *diagnostic* of the learned \(\rho_-\), not as a spectral product

The field representation survives. The PES-to-IR product does not. The CC-anharmonic product does not.

## Hours

Fixed baseline **840 h** across Modules 02–09, matching plan 01’s accounting unit.

| Bucket | Cap | Why |
|---|---|---|
| Frozen grid + teacher I/O | 80 h | Plan 01 spent ~560 h here. That is forbidden. |
| Public-rubric datasets (M02–M04) | 160 h | Rubrics 02–04 demand third-party tabular data. |
| Learned stencil + tests P0–P4 | 320 h | The thesis. |
| Generative + agentic + synthesis | 200 h | Rubrics 06–08. |
| Contingency / reviews | 80 h | |

If the teacher-grid bucket exceeds 80 h, the plan is off the rails. Stop and write the deviation. Do not silently become plan 01.

Two budgets, not one: the 80 h cap is **human I/O**. Octopus wall-clock for the promised H / H₂ / H₂O Maxwell set is capped at **168 h** in [Compute_Budget_2026-09-01.md](Compute_Budget_2026-09-01.md). Neither number is a measured runtime.

## Industry frame

Reliability-gated **surrogate electronic propagator** for digital-twin and attosecond-lab software: a lab or vendor can step a presence field locally when a full TDDFT step is too slow, with a published fixed-point and rollout certificate. Not “AI for drug discovery.” Not “PAH identification as a service.”
