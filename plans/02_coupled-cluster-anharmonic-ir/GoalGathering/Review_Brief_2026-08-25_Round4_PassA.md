# Review brief — Round 4, Pass A: cold read

**Give this to the reviewer first. Do not give Pass B until Pass A's findings are written down.**

---

## Your role

You are a careful, sceptical reader. You do **not** have the conversation that produced these
documents, and that is deliberate: the test is whether the plan stands up without its author present
to fill in gaps. That is also the situation at the thesis defense.

You are not being asked to judge the chemistry yet. Pass B does that. Pass A asks one question:

> **Does this document set say what it thinks it says, and is any of it unsupported?**

## Context you need

- This is a **master's capstone plan**, not a PhD proposal. One person, self-paced, roughly 10 hours
  of human attention per week, consumer hardware plus possibly a limited HPC allocation.
- **Nothing has been executed.** There are no results. Every number is either a target, a literature
  value, or an estimate.
- The plan you are reading (**plan 02**) replaced an earlier plan (**plan 01**) on 2026-08-23.
  Plan 01 survived three rounds of review and closed fifteen blocking issues. Plan 02 inherits
  twelve of those; the inheritance table is in `plans/02_coupled-cluster-anharmonic-ir/README.md`.
- **Do not re-litigate plan 01's closed issues** — unless the pivot broke one, in which case say so
  loudly.
- **Calibration warning:** these documents were drafted largely by an AI assistant working with the
  student. Be alert to fluent, confident sentences that assert something no one measured. That
  failure mode is the specific reason you are being asked to do this.

## What to read

Repository: `https://github.com/thebreadishard/udacity-capstone-plan`

In this order:

1. `plans/02_coupled-cluster-anharmonic-ir/README.md` — orientation and the inheritance table
2. `plans/02_coupled-cluster-anharmonic-ir/GoalGathering/Overarching_Goal.md` — the prime directive
3. `plans/02_coupled-cluster-anharmonic-ir/GoalGathering/Frozen_Ladder_and_Tolerances_2026-08-25.md`
4. `plans/02_coupled-cluster-anharmonic-ir/GoalGathering/Distilled_Project_Plan_and_Quality_Checks.md` — the technical plan, §1–§9
5. `plans/02_coupled-cluster-anharmonic-ir/GoalGathering/Restructure_Proposal_2026-08-23_Project12_in_Module08.md` — why the plan changed
6. `plans/02_coupled-cluster-anharmonic-ir/GoalGathering/Relevant_Scientific_Papers.md` — the bibliography

Ignore for now: `Capstone_Mapping.md` and `GoalGathering/Horizon/`. Both are marked as not yet
rewritten and are deliberately held until after this review.

## The five questions

**1. Contradictions.** Where do two documents, or two sections of one document, state incompatible
things? Quote both.

**2. Unsupported claims.** Which statements are presented as established but cite no measurement, no
source, and no probe? Distinguish *"stated without support"* from *"supported by a citation you
could not verify"*.

**3. Number drift.** Does any quantity appear with different values, units or definitions in
different places? Tolerances, counts, thresholds and molecule lists especially.

**4. Loopholes.** This plan is built out of gates, ladders and pre-registrations whose purpose is to
prevent the author from declaring success without having earned it. **Try to defeat them.** Where
could a determined author pass a gate while the underlying work is bad, or quietly widen a criterion
without it being visible? Name the exact sentence that permits it.

**5. Unreadable without the author.** Which passages assume knowledge that exists only in the head
of whoever wrote them?

## Output format

Match the earlier reviews in `plans/01_voxel-field-pes/GoalGathering/Professor_Review_*.md`.

```
Verdict: [one line — is this internally sound enough to proceed to Pass B?]

## Blocking findings
1. [Title]
   Where: [file, section]
   What: [what is wrong]
   Why it matters: [consequence if unfixed]

## Non-blocking findings
...

## Questions I could not resolve from the documents
...

## What passed
[Be specific. A review that finds only faults is not calibrated.]
```

## What not to do

- Do not propose a different thesis. The scope question is settled; you are reviewing *this* plan.
- Do not rewrite passages. Identify the problem and let the author fix it.
- Do not soften. "This is broadly fine" is not useful. If it is fine, say what specifically is fine
  and why.
- Do not assume a claim is true because it is well written.
- If you cannot verify something, say **"unverified"** rather than accepting or rejecting it.
