# Plan 02 — Coupled-Cluster Anharmonic IR

**Status: complete as a plan, blocked on measurement.** Supersedes
[plan 01](../01_voxel-field-pes/) as of 2026-08-23; reviewed and scope-reduced 2026-08-26 after
Round 4. Nothing here has been executed.

**Promised deliverable:** anharmonic infrared band positions and relative intensities for **benzene
and naphthalene, neutral**, with a four-term error budget, both baselines, and a hybrid quartic force
field whose split is decided by measurement. Cations, anthracene/phenanthrene and pyrene are **bonus,
not promise**.

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
3. [GoalGathering/Distilled_Project_Plan_and_Quality_Checks.md](GoalGathering/Distilled_Project_Plan_and_Quality_Checks.md) — the technical plan, §1–§9. All nine sections are rewritten for R3.
4. [GoalGathering/Relevant_Scientific_Papers.md](GoalGathering/Relevant_Scientific_Papers.md) — bibliography, items 26–36 are the R3 evidence base

## Rewrite status

| Section | State |
|---|---|
| `Overarching_Goal.md` | ✅ rewritten, scope-reduced 2026-08-26 |
| `Distilled` §1–§9, all nine sections | ✅ rewritten; §2, §5.9, §6.4 and §7 revised after Round 4 |
| `Relevant_Scientific_Papers.md` | ✅ items 26–39, three entries corrected |
| Molecule ladder and tolerances | ✅ **frozen twice** — [v1 2026-08-25](GoalGathering/Frozen_Ladder_and_Tolerances_2026-08-25.md), [v2 2026-08-26](GoalGathering/Frozen_Ladder_and_Tolerances_2026-08-26.md). v1 retained unedited to show what the scope was before the review |
| Round 4 review | ✅ [Pass A](GoalGathering/Professor_Review_2026-08-25_Round4_PassA.md), [Pass B](GoalGathering/Professor_Review_2026-08-25_Round4_PassB.md) |
| `Capstone_Mapping.md` | ⛔ still plan 01. **Blocked by Pass B approval conditions 1–3**, which require calculations that have not been run |
| `GoalGathering/Horizon/10–12` | ⛔ still plan 01, banner-marked as absorbed provenance |
| Dutch `Uitleg/` | ✅ started — [leeswijzer](Uitleg/00_Leeswijzer.md) + ch. 01. Havo-4 level, a running log of what has actually been measured |

### What has to happen before this plan moves again

| # | Blocked on | Gate |
|---|---|---|
| 1 | Measured cost table — one Hessian per candidate species, exact production settings | **G1a** |
| 2 | The hybrid decision: \(\omega_{\text{gold}}+\delta_{\text{cheap}}\) vs full gold QFF vs scaled harmonic, on benzene | **G1b** |
| 3 | Two dated amendments: the cheap level for \(\delta_{\mathrm{anh}}\), and the GVPT2 resonance criterion | **G0** |
| 4 | Written mentor approval on dataset eligibility (R3 issue 3, open since round 3) | — |

Until 1–3 exist, `Capstone_Mapping.md` stays unwritten. That is deliberate: the module mapping
depends on which rungs turn out to be affordable.

## Review status

**Round 4 complete.** Both passes returned, both recorded, all findings closed or accepted.

| Pass | Verdict | Record |
|---|---|---|
| **A** — cold read | Sound enough to proceed. Three blocking findings, all documentation-status drift, all closed | [Pass A](GoalGathering/Professor_Review_2026-08-25_Round4_PassA.md) |
| **B** — adversarial domain | **Conditional.** Green light only for a neutrals-first ladder with option F as the default deliverable. **No green light for the full neutral+cation pyrene claim** | [Pass B](GoalGathering/Professor_Review_2026-08-25_Round4_PassB.md) |

Pass B did not find the plan wrong. It found it **more expensive than it needed to be, aimed at the
wrong derivative, and promising more than the calendar allows.** Two decisions followed, both taken
2026-08-26:

1. **The hybrid quartic force field is now the primary method** — gold-rung harmonics,
   cheap-level anharmonic corrections, with gate **G1b** deciding before any production spend whether
   gold-rung high-order derivatives are ever computed.
2. **Option F is the primary deliverable** — benzene and naphthalene, neutral. Everything else is
   bonus.

**Plan 02 is now complete as a plan and blocked on measurement.** Three of the reviewer's five
approval conditions require calculations that have not been run; the other two are done. That is the
correct terminal state for a document whose whole argument was that it would measure rather than
assert.

The three earlier reviews live in [plan 01](../01_voxel-field-pes/GoalGathering/), because that is
what they reviewed. What carried over is the findings:

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

**Tally, so it can be audited rather than trusted** — 21 issues:

| Fate | Count | Issues |
|---|---:|---|
| Superseded | 4 | 1, 2, 14, R3-1 |
| Inverted | 1 | 6 |
| Resolved by construction | 1 | 12 |
| Re-scoped to the dipole-surface leg | 2 | 7, 10 |
| Carried forward | 12 | 3, 4, 5, 8, 9, 11, 13, 15, R3-2, R3-4, R3-5, R3-6 |
| **Still open** | 1 | R3-3 |

*(Corrected 2026-08-25 after Round-4 Pass A. The previous summary said "six superseded" and omitted
the re-scoped category entirely. It was wrong, and it was exactly the kind of unaudited count this
table exists to prevent — which is why the tally is now itemised.)*

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
| 6 | The molecule ladder and tolerances are **frozen twice**: [v1 2026-08-25](GoalGathering/Frozen_Ladder_and_Tolerances_2026-08-25.md) before any calculation, and [v2 2026-08-26](GoalGathering/Frozen_Ladder_and_Tolerances_2026-08-26.md) after Round 4 reduced the scope. v1 is retained unedited so the reduction is visible. |
| 7 | Dataset eligibility for Modules 03–05 still needs **written mentor approval** (Round 3, issue 3). Reduced by the pivot, not closed. |
| 8 | **The hybrid quartic force field is the primary method** (2026-08-26). Gold-rung harmonics, cheap-level anharmonic corrections, with gate G1b deciding whether gold-rung high-order derivatives are computed at all. |
| 9 | **Option F is the primary deliverable** (2026-08-26). Benzene and naphthalene neutral are promised; cations and larger rings are bonus. |

## Terminology

**"Gold rung"** and **"gold-anchored"** are this project's internal shorthand, inherited from plan
01. *"Gold standard"* for CCSD(T) is established literature usage; *"gold-anchored"* is not. It is
defined in `Overarching_Goal.md` and may be used inside these documents, but a thesis chapter or
paper title must say **"anchored to a measured coupled-cluster reference"** or **"CCSD(T)-quality"**.
