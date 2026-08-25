# Plan 02 — Coupled-Cluster Anharmonic IR

**Status: current, rewrite in progress.** Supersedes [plan 01](../01_voxel-field-pes/) as of
2026-08-23. See [../README.md](../README.md) for why the project turned.

Nothing here has been executed. This is a plan.

---

## What this plan is

Predict **anharmonic infrared band families and relative intensities for named PAH sizes and charge
states**, with the electronic structure anchored to a **measured** coupled-cluster reference rather
than to DFT, and end in a **pre-registered, fail-closed identification** against one frozen
JWST/PAHdb product.

The inversion relative to plan 01, in one line:

> **Borrow the representation; own the theory anchor and the nuclear motion.**

Precision lives in the theory ladder and the nuclear-motion method, not in the neural architecture.
The machine-learned potential is an interpolator between gold-rung points, and every architectural
choice is made for *reliability of high-order derivatives* rather than for novelty.

## The deliverable, stated precisely (R3)

Three readings of "chemically precise IR spectra" exist; this plan adopts the third and forbids the
first.

| | Reading | Status |
|---|---|---|
| **R1** | Rovibrational line lists, sub-cm⁻¹ | Forbidden — not achievable for any PAH inside a master's |
| **R2** | Band envelopes from classical MD + dipole-ACF FFT | Not the deliverable — already published at C₂₁₆ scale in 2025; retained as a temperature diagnostic |
| **R3** | Quantum anharmonic (GVPT2-class) band centres within a stated cm⁻¹ of a **named** experimental standard, plus relative integrated intensities from a dipole moment surface, plus a **four-term error budget** | **The objective** |

Every cm⁻¹ claim carries the budget: **(A)** ML/PES error vs the gold rung, **(B)** local vs
canonical coupled cluster, **(C)** GVPT2 vs VCI or experiment, **(D)** matrix shift / excitation
model. A single pooled number is a fail.

## Pipeline

```
      target list (pre-registered)              frozen observational product
              │                                            │
              ▼                                            ▼
 [1] theory ladder             [3] MLIP             [5] GVPT2 / VCI       [7] cascade +
   canonical CCSD(T)   ──▶      fine-tuned    ──▶     QFF from MLP    ──▶  fail-closed ID
   ↕ measured error          foundation model       + dipole surface
   DLPNO / LNO-CCSD(T)              ▲                       ▲
   = the GOLD RUNG                  │                       │
              │              [2] Δ-ML / transfer      [6] DMS: field vs
              └──────────────────▶   correction           tensor vs charge
                                      ▲
                                 [4] active-learning proposal engine
```

## Reading order

1. [GoalGathering/Overarching_Goal.md](GoalGathering/Overarching_Goal.md) — the prime directive
2. [GoalGathering/Restructure_Proposal_2026-08-23_Project12_in_Module08.md](GoalGathering/Restructure_Proposal_2026-08-23_Project12_in_Module08.md) — why the plan turned, six weighed alternatives, the literature, the module remap, gates G0–G6, the effort arithmetic, the risk register
3. [GoalGathering/Distilled_Project_Plan_and_Quality_Checks.md](GoalGathering/Distilled_Project_Plan_and_Quality_Checks.md) — the technical plan. **Read its banner first: §1–§4 are rewritten, §5–§9 are still plan 01's text.**
4. [GoalGathering/Relevant_Scientific_Papers.md](GoalGathering/Relevant_Scientific_Papers.md) — bibliography, items 26–36 are the R3 evidence base

## Rewrite status

| Section | State |
|---|---|
| `Overarching_Goal.md` | ✅ rewritten |
| `Distilled` §1 evolution, §2 question, §2.1 prior art, §2.2 demoted DMS question | ✅ rewritten |
| `Distilled` §3 what it IS, §4 what it is NOT | ✅ rewritten |
| `Distilled` §5 data pipeline, §6 architecture, §7 roadmap, §8 QA, §9 precision claims | ⛔ still plan 01 |
| `Capstone_Mapping.md` | ⛔ still plan 01 — rewritten only after a Round-4 review, so a rejected pivot does not cost two rewrites |
| `GoalGathering/Horizon/10–12` | ⛔ still plan 01, banner-marked as absorbed provenance |
| Dutch `Uitleg/` | ✗ none yet — plan 01's version explains the voxel approach |

## Decisions taken

| # | Decision |
|---|---|
| 1 | Adopt **R3**. R1 stays forbidden; R2 is demoted to a diagnostic. |
| 2 | The voxel field model moves from the **energy** surface to the **dipole** surface, as one of three pre-registered legs. Never on the critical path. |
| 3 | **No post-master's horizon.** Projects 10–12 are absorbed into Modules 03–08. Whatever R3 does not reach is a limitation in Module 08, not a queued project. |
| 4 | **ORCA** as the single production stack (free academically, native Windows, canonical CC and DLPNO in one code), with **MRCC / LNO-CCSD(T)** as arbiter for gate G1 only. |
| 5 | **MACE family**: MACE-OMOL-0 primary (charge/spin embedding, so cations work), MACE-OFF as fallback, MACE-POLAR-1 as the dipole-surface comparator. Code MIT, weights ASL (academic, non-commercial). |
| 6 | The molecule ladder and cm⁻¹ tolerances are **frozen in a dated commit before the first gold-rung job**. Not yet done. |
| 7 | Dataset eligibility for Modules 03–05 still needs **written mentor approval** (Round 3, issue 3). Reduced by the pivot, not closed. |

## Terminology

**"Gold rung"** and **"gold-anchored"** are this project's internal shorthand, inherited from plan
01. *"Gold standard"* for CCSD(T) is established literature usage; *"gold-anchored"* is not. It is
defined in `Overarching_Goal.md` and may be used inside these documents, but a thesis chapter or
paper title must say **"anchored to a measured coupled-cluster reference"** or **"CCSD(T)-quality"**.
