# Review brief — Round 5, Pass A: cold read

**Give this to the reviewer first. Do not give Pass B until Pass A's findings are written down.**

---

## Your role

You are a careful, sceptical reader. You do **not** have the conversation that produced these
documents, and that is deliberate: the test is whether the plan stands up without its author present
to fill in gaps. That is also the situation at the thesis defense.

You are not being asked to judge the TDDFT, Maxwell, or stencil chemistry yet. Pass B does that.
Pass A asks one question:

> **Does this document set say what it thinks it says, and is any of it unsupported?**

## Context you need

- This is a **master’s capstone plan**, not a PhD proposal. One person, self-paced, roughly 10 hours
  of human attention per week, consumer hardware. No HPC is assumed.
- **Nothing has been executed.** There are no results. Every number is either a target, a literature
  value, a cap, or an estimate. Probe scripts that lack teacher files must print `NOT_RUN`.
- The plan you are reading (**plan 03**, Presence-Update-Rule) replaced plan 02 on 2026-08-29, with a
  contradiction pass and remaining freeze dated **2026-09-01**. Plan 02 had replaced plan 01. Plans 01
  and 02 remain in the repository until a later deletion pass; they are **not** current.
- Plan 01 closed fifteen blocking issues across Rounds 1–2 plus six Round-3 findings, in *spec*.
  Plan 02 closed Round-4 Pass A/B findings, then died as a *label factory* (coupled-cluster rung
  blocked on measurement). Plan 03 inherits those findings as a **map**, not as a stamp. The map is
  [`Inheritance_of_Reviews.md`](Inheritance_of_Reviews.md).
- **Do not re-litigate plan 01’s or plan 02’s closed issues** — unless the pivot to a local
  Maxwell–TDDFT stencil **broke** one, in which case say so loudly.
- **Calibration warning:** these documents were drafted largely by an AI assistant working with the
  student. Be alert to fluent, confident sentences that assert something no one measured. That
  failure mode is the specific reason you are being asked to do this.
- **Status is draft.** Do not treat a tidy folder as “complete as a plan.” Completeness waits on a
  review of *this* plan. There is no `Professor_Review_*` file for plan 03 yet; you are writing the
  first one.

## What to read

Repository: `https://github.com/thebreadishard/udacity-capstone-plan`

In this order:

0. Root `README.md` and `plans/README.md` — status banners only (must say plan 03 is **current and draft**, not complete)
1. `plans/03_presence-update-rule/README.md` — orientation
2. `plans/03_presence-update-rule/GoalGathering/Overarching_Goal.md` — the prime directive
3. `plans/03_presence-update-rule/GoalGathering/Frozen_Ladder_and_Tolerances.md`
4. `plans/03_presence-update-rule/GoalGathering/Compute_Budget_2026-09-01.md`
5. `plans/03_presence-update-rule/GoalGathering/Distilled_Project_Plan_and_Quality_Checks.md`
6. `plans/03_presence-update-rule/GoalGathering/Capstone_Mapping.md`
7. `plans/03_presence-update-rule/GoalGathering/Relevant_Scientific_Papers.md`
8. `plans/03_presence-update-rule/GoalGathering/Inheritance_of_Reviews.md` — itemised map of 01/02 issues
9. `plans/03_presence-update-rule/probes/README.md` — what is a script vs a result

Ignore for now:

- `plans/03_presence-update-rule/PATCH_plans_README.md` (applied 2026-09-01; argument of record, not a live proposal)
- `GoalGathering/Horizon/`
- `plans/01_*` and `plans/02_*` except as named in the inheritance table
- Any `Uitleg/` folder (Dutch study notes; not the English plan)

## The five questions

**1. Contradictions.** Where do two documents, or two sections of one document, state incompatible
things? Quote both. Likely classes (not an exhaustive list; find others):

- “draft / not complete” vs any leftover “complete as a plan”
- Q0 hashed in Module 05 vs any leftover “hash the grid in Module 02”
- teacher = Octopus Maxwell–TDDFT vs Poisson reconstruction of \(\mathbf{E}\) from \(\rho\)
- T0 / 840 h / 168 h / 80 h appearing with different owners or calendar dates
- inheritance **summary sentence** vs the named rows (this was Round 4 Pass A issue 3)

**2. Unsupported claims.** Which statements are presented as established but cite no measurement, no
source, and no probe? Distinguish *“stated without support”* from *“supported by a citation you
could not verify”*. In particular: any wall-clock, any Octopus timing, any voxel-dataset DOI that the
bibliography itself marks FAIL.

**3. Number drift.** Does any quantity appear with different values, units or definitions in
different places? Grid spacing (\(a_0\) vs Å), \(\Delta t\), P2 step count, kernel size, \(k\),
electron-count tolerances, 840 / 80 / 168 h, molecule lists.

**4. Loopholes.** This plan is built out of gates, ladders and pre-registrations whose purpose is to
prevent the author from declaring success without having earned it. **Try to defeat them.** Where
could a determined author pass a gate while the underlying work is bad, or quietly widen a criterion
without it being visible? Name the exact sentence that permits it.

**5. Unreadable without the author.** Which passages assume knowledge that exists only in the head
of whoever wrote them? Plan-01 issue numbers without the inheritance table, “Andrade 2020 family”
without a DOI, PATCH files a cold reader is told to ignore but that still sit in the tree.

## Output format

Match the earlier reviews in `plans/01_voxel-field-pes/GoalGathering/Professor_Review_*.md` and
`plans/02_coupled-cluster-anharmonic-ir/GoalGathering/Professor_Review_2026-08-25_Round4_PassA.md`.

```
Verdict: [one line — is this internally sound enough to proceed to Pass B?]

## Blocking findings
1. [Title]
   Where: [file, section]
   What: [what is wrong]
   Why it matters: [consequence if unfixed]
   Status: [open]

## Non-blocking findings
…

## What passed
…
```

Use **Round 5, Pass A, issues 1–N**. Do not continue plan 01’s 1–15 numbering in Pass A; those
numbers live in the inheritance table. Pass B will use Round 5 domain issues 1–N.

**Do not write Pass B in the same file.**
