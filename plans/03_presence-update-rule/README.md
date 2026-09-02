# Plan 03 — Presence-Update-Rule

**Status: draft as of 2026-09-01. Current plan; not complete.**  
Supersedes plan 02 (Coupled-Cluster Anharmonic IR). Plans 01 and 02 were **removed from the tree** on
2026-09-01 — documents and, for plan 02, its leftover psi4 run artifacts. They remain in git history;
plan 02's raw `.npz` frequency arrays were force-added in `800f3aa` first.

Contradiction pass 2026-09-01 and the Round-5 Pass A pass are recorded in
[GoalGathering/Frozen_Ladder_and_Tolerances.md](GoalGathering/Frozen_Ladder_and_Tolerances.md).
The remaining freeze (two budgets, \(k=1\), P2 = 200 steps, kernel 3, conservation off) is
[GoalGathering/Compute_Budget_2026-09-01.md](GoalGathering/Compute_Budget_2026-09-01.md).
Do not call this folder “complete as a plan” until a review has closed.

**Promised deliverable.** A *single* translation-equivariant local update rule

\[
(\rho_+,\rho_-,\mathbf{j},\mathbf{E},\mathbf{B})_{\mathcal{N}(x)}
\;\longmapsto\;
(\rho_+,\rho_-,\mathbf{j},\mathbf{E},\mathbf{B})_{x}^{t+\Delta t}
\]

trained as one 3-D stencil / small conv-net, evaluated on a **frozen** real-space grid, with a pre-registered one-step and rollout test on **H₂** and a transfer test on **H₂O**.

Infrared spectra, JWST identification, and C₃₈₄H₄₈ are **not** Module 08 promises. They sit in Horizon 10–12.

Nothing in this folder has been executed. Nothing here is a result.

## Reading order

1. This file — orientation. **Draft, not complete.**
2. [GoalGathering/Overarching_Goal.md](GoalGathering/Overarching_Goal.md) — prime directive
3. [GoalGathering/Frozen_Ladder_and_Tolerances.md](GoalGathering/Frozen_Ladder_and_Tolerances.md)
4. [GoalGathering/Compute_Budget_2026-09-01.md](GoalGathering/Compute_Budget_2026-09-01.md)
5. [GoalGathering/Distilled_Project_Plan_and_Quality_Checks.md](GoalGathering/Distilled_Project_Plan_and_Quality_Checks.md)
6. [GoalGathering/Capstone_Mapping.md](GoalGathering/Capstone_Mapping.md)
7. [GoalGathering/Relevant_Scientific_Papers.md](GoalGathering/Relevant_Scientific_Papers.md)
8. [GoalGathering/Inheritance_of_Reviews.md](GoalGathering/Inheritance_of_Reviews.md) — itemised map of plan-01/02 issues (not a stamp)
9. [probes/README.md](probes/README.md)
10. [GoalGathering/Why_03_Supersedes_02.md](GoalGathering/Why_03_Supersedes_02.md) — argument of record for the pivot

Round 5:

- [GoalGathering/Professor_Review_2026-09-01_Round5_PassA.md](GoalGathering/Professor_Review_2026-09-01_Round5_PassA.md) — **the first review of this plan** (cold read). Findings addressed in spec on 2026-09-01; see the Round-5 Pass A block in the frozen ladder.
- [GoalGathering/Review_Brief_2026-09-01_Round5_PassA.md](GoalGathering/Review_Brief_2026-09-01_Round5_PassA.md) — the brief that produced it
- [GoalGathering/Professor_Review_2026-09-01_Round5_PassB.md](GoalGathering/Professor_Review_2026-09-01_Round5_PassB.md) — the adversarial domain review, 2026-09-01. **Verdict: no green light for the scope as frozen**; conditional green light for a matter-only scope. Twelve blocking findings, **none addressed**.
- [GoalGathering/Review_Brief_2026-09-01_Round5_PassB.md](GoalGathering/Review_Brief_2026-09-01_Round5_PassB.md) — the brief that produced it

Do not copy deleted plan-01/02 reviews from git history into this folder.

Inheritance tally (must match [Inheritance_of_Reviews.md](GoalGathering/Inheritance_of_Reviews.md)): **8 superseded** (2, 10, 11, 14, R3-2, R4B-1, R4B-3, R4B-4), **5 re-scoped** (1, 7, 12, R3-1, R3-4), **16 carried** (3, 4, 5, 8, 9, 13, 15, R3-3, R3-5, R3-6, R4A-1, R4A-2, R4A-3, R4B-2, R4B-5, R4B-6), **1 addressed in spec** (6). \(8+5+16+1=30\).
