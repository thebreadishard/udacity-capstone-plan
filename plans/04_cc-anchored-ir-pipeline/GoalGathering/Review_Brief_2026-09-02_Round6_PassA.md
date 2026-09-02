# Review brief — Round 6, Pass A: cold read

**Give this to the reviewer first. Do not give Pass B until Pass A's findings are written down.**

---

## Your role

You are a careful, sceptical reader. You do **not** have the conversations that produced these
documents, and that is deliberate: the test is whether the plan stands up without its author
present to fill in gaps. That is also the situation at the thesis defense.

You are not judging the quantum chemistry or the ML yet. Pass B does that. Pass A asks one
question:

> **Does this document set say what it thinks it says, and is any of it unsupported?**

## Context you need

- This is a **master's capstone plan**, not a PhD proposal. One person, self-paced, ~10 hours of
  human attention per week. A laptop is the default machine; UvA supercomputer access is a
  *decided collaboration* but **not yet a formalized allocation** — the plan claims to treat it
  that way; check that it does.
- **Nothing has been executed.** No probes exist. Every number is a cap, a literature value, a
  plan-02-era measurement labelled provenance, or an assertion labelled assertion. Check the
  labels.
- This is **plan 04** (CC-Anchored IR Pipeline), created 2026-09-02. Plans 01 (voxel PES),
  02 (CC anharmonic IR), 03 (presence-update rule) are **git history only**; do not fetch them.
  Plan 03 died under Round-5 Pass B (no green light: double scope on one clock). Plan 04 claims
  its hard-won lessons are *structural* now (mandatory null rows, three separated budgets,
  accuracy/reach split). **Verify that claim against the documents, not against the claim.**
- **Calibration warning:** these documents were drafted largely by an AI assistant working with
  the student. Be alert to fluent, confident sentences that assert something no one measured.
  That failure mode is the specific reason you are being asked to do this.
- **Status is draft.** A tidy folder is not "complete as a plan." There is no
  `Professor_Review_*` file for plan 04 yet; you are writing the first one.

## What to read

This review runs in a **VS Code chat on the CapstonePlan workspace**. Read the files **in this
workspace**. Do not fetch GitHub; the remote is a public copy and may lag.

In this order:

0. [README.md](../../../README.md) and [plans/README.md](../../README.md) — status banners
   (must say plan 04 is **current and draft**; plans 01–03 removed)
1. [../README.md](../README.md) — orientation and reading order
2. [Overarching_Goal.md](Overarching_Goal.md) — prime directive
3. [Frozen_Lines_to_Beat.md](Frozen_Lines_to_Beat.md) — the opponents and scoreboards
4. [Frozen_Ladder_and_Tolerances.md](Frozen_Ladder_and_Tolerances.md) — rungs, claim types, stops
5. [Compute_Budget_2026-09-02.md](Compute_Budget_2026-09-02.md) — the three budgets
6. [Capstone_Mapping.md](Capstone_Mapping.md) — modules 02–09, rule 0, the three user decisions
7. [Distilled_Project_Plan_and_Quality_Checks.md](Distilled_Project_Plan_and_Quality_Checks.md) — gates
8. [Relevant_Scientific_Papers.md](Relevant_Scientific_Papers.md) — verify statuses and debts
9. [../probes/README.md](../probes/README.md) — what is a script vs a result
10. [../../../Rubrics/README.md](../../../Rubrics/README.md) and the rubric files it governs —
    the mapping leans on this file's "Accepted Sources are examples" reading; check the mapping
    never leans further than that file actually goes

Also in scope as a primary source: [../../../AI_Chats/grok_chat_4.md](../../../AI_Chats/grok_chat_4.md)
— the named source conversation. The plan claims to carry its risks (DLPNO roughness, sampling
cost, "per molecule" scope); check nothing was dropped in translation.

## The five questions

**1. Contradictions.** Where do two documents, or two sections of one, state incompatible
things? Quote both. Likely classes (find others):

- the **relative** criterion ("beat the named lines") vs any leftover absolute
  "chemically precise" language;
- **accuracy vs reach** language crossing rungs (any "beat" near R4–R6, any lab-scored claim
  where no lab data exists);
- the two debt lists (Frozen_Lines §7 vs bibliography "Named debts") — they claim to be in
  sync; are they?
- budget owners: 840 h buckets in the budget file vs module assignments in the mapping;
- "frozen now" vs "frozen at the pilot note" — is every number in exactly one of those bins?

**2. Unsupported claims.** Which statements are presented as established but cite no
measurement, no fetched source, and no probe? Distinguish *stated without support* from
*supported by a citation not yet verified* (the bibliography marks these — check the marks are
used honestly). Specific candidates:

- the world-map ceilings (C₃₈₆ / C₂₁₆ / C₁₈–C₂₄) and what was actually fetched for each;
- the inference that **C₃₈₄H₄₈-class species are in PAHdb** from "N_carbon,max = 384 in NASA's
  Orion Bar fit" — presence in a fit parameter is not presence of a species entry, and the
  plan's own debts list admits the per-species check is not done;
- the "~5 cm⁻¹ MAE" of the cheap line — the plan says it never re-read the number; is it
  nevertheless *used* anywhere as if read?
- every timing (all are old-laptop plan-02 provenance or a chat assertion; the documents claim
  to label them as such — verify).

**3. Number drift.** Same quantity, different values/units/definitions anywhere: 840 h buckets,
168 h (per rung pilot here — plan 03 used it as a teacher-set total; any leftover?), 10 vs
15 cm⁻¹ and what each governs, scale factors 0.964/0.979/0.975, rung molecule lists, dates.

**4. Loopholes.** The gates exist to stop the author declaring success without earning it.
**Try to defeat them.** Candidates:

- the **pilot note**: can its numbers (margins, band lists, effect size) be written *after*
  pipeline output for those molecules exists? What sentence prevents it, exactly?
- can the M04 baseline be quietly weakened (fewer features, less tuning) so P2 is easier?
  The distilled plan promises tuning parity for the Δ/direct arms — does anything promise
  parity for the *baseline*?
- can a lost band family be dropped from the "promised families" between pilot note and P2?
- can a reach-rung theory-vs-theory table drift into "beat" language in the Module 08 paper?
- does the Δ=0 null (P4) have an escape — e.g. scoring it on different bands or seeds?

**5. Unreadable without the author.** Which passages assume knowledge that lives only in git
history or in the author's head? Plan-02 probe references ("uids recorded", "NIST parser
exists") without a path a cold reader can check; "reading 1" in the mapping without the
rejected reading spelled out; any acronym (DLPNO, VPT2, PNO) used before defined.

## Output format

```
Verdict: [one line — internally sound enough to proceed to Pass B?]

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

Use **Round 6, Pass A, issues 1–N**. Pass B will use Round 6 domain issues 1–N.

**Do not write Pass B in the same file.**
