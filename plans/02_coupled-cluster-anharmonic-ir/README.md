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
| `Distilled` §5 data pipeline — molecule ladder, three data products, gold-rung audit, shrink ladder | ✅ rewritten |
| `Distilled` §6 architecture — MLIP, training loss, active learning, QFF/GVPT2, dipole surface, excitation model | ✅ rewritten |
| `Distilled` §7 roadmap — gates G0–G6, three pre-registered comparisons | ✅ rewritten |
| `Distilled` §8 QA, §9 precision claims | ⛔ still plan 01 |
| `Capstone_Mapping.md` | ⛔ still plan 01 — rewritten only after a Round-4 review, so a rejected pivot does not cost two rewrites |
| `GoalGathering/Horizon/10–12` | ⛔ still plan 01, banner-marked as absorbed provenance |
| Dutch `Uitleg/` | ✗ none yet — plan 01's version explains the voxel approach |

## Review status

**This plan has not been reviewed.** Round 4 is pending, and is deliberately scheduled *after* the
Distilled Plan rewrite so that a rejected pivot does not cost two rewrites.

The three professor reviews live in [plan 01](../01_voxel-field-pes/GoalGathering/), because that is
what they reviewed. They are **not** copied here: three reviews sitting in this folder would imply
this plan had survived them, and it has not.

What did carry over is the findings. Plan 01 closed fifteen blocking issues; the pivot inherited,
transferred or superseded each one deliberately rather than discarding them:

| Issue | Origin | Fate in this plan |
|---|---|---|
| 1 — Phase 1 has no owner | R1 | **Superseded.** No Workstream P1; the production surface is a module deliverable. |
| 2 — \(E=\mathcal{E}[\rho,R]\) is a slogan, not an implementation | R1 | **Superseded.** No longer the energy model (§2.2). |
| 3 — a level of theory plus a count is not a method | R1 | **Inherited** → §5.3, as a decision procedure with smoke test and cost pilot. |
| 4 — prime directive promises spectral lines | R1 | **Inherited and sharpened** → the R1/R2/R3 split in `Overarching_Goal.md` §1. |
| 5 — rubric landmines, DOI before claim | R1 | **Inherited**, still binding. |
| 6 — the GNN competitor is off the critical path | R1 | **Inverted.** The equivariant GNN *is* the production surface (§4). |
| 7 — the grid cannot carry an all-electron density | R2 | **Transferred** to the DMS-field leg, where the reference split still applies. |
| 8 — gates are mutually inconsistent and self-loosening | R2 | **Inherited** → §5.8, with the artifact category re-aimed at MLIP derivative noise. |
| 9 — the novelty check missed ML orbital-free DFT | R2 | **Inherited as method** → §2.1 rewritten against the *current* neighbours; the OF-DFT lineage is scoped to §2.2. |
| 10 — \(\Phi\) is a nuclear-identity bypass channel | R2 | **Scoped** to the DMS-field leg. |
| 11 — the IR observable was never trained or validated | R2 | **Inherited** → §5.4. Its finding that \(\boldsymbol\mu=-\int\mathbf r\,\Delta\rho\,dV\) exactly is now the *basis* of the DMS-field leg. |
| 12 — no gate covers translation/rotation invariance | R2 | **Resolved by construction.** An equivariant GNN is exactly rotation-invariant; this is one of the reasons it replaced the voxel model. |
| 13 — the comparison is falsifiable in wording only | R2 | **Inherited** → §7.1 pre-registration, retargeted at the DMS bake-off and the model bake-off. |
| 14 — the Module 03 row count does not add up | R2 | **Superseded** with the dataset it counted. |
| 15 — there is no calendar anywhere | R2 | **Inherited** → the restructure proposal §10 effort arithmetic. |
| R3-1 — the experiment does not isolate representation | R3 | **Superseded** with the research question (§2). |
| R3-2 — energy and force labels may be mutually inconsistent | R3 | **Inherited verbatim** → §5.6. Δ-learning makes it stricter, not looser. |
| R3-3 — dataset eligibility is unresolved | R3 | **Still open.** Reduced by the pivot, not closed. Decision 7 below. |
| R3-4 — dipole supervision is unfinished | R3 | **Inherited** → §5.4, with separate derivative sets for cations. |
| R3-5 — "chemically precise" is asserted, not demonstrated | R3 | **Inherited and strengthened** → §5.5 splits error term (B) into local-vs-canonical and basis convergence, both measured. |
| R3-6 — the calendar is non-operational | R3 | **Inherited** → restructure proposal §10. |

Six superseded, one inverted, one resolved by construction, twelve carried forward, one still open.
A Round-4 reviewer should start from this table: the question is not whether the pivot discarded the
discipline, but whether the twelve landed correctly.

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
