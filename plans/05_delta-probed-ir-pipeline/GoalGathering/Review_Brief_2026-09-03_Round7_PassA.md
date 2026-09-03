# Review brief — Round 7, Pass A: cold read

**Give this to the reviewer first. Do not give Pass B until Pass A's findings are written down.**

---

## Your role

You are a careful, sceptical reader. You do **not** have the conversations or the research
session that produced these documents, and that is deliberate: the test is whether the plan
stands up without its author present to fill in gaps. That is also the situation at the
thesis defense.

You are not judging the quantum chemistry or the ML yet. Pass B does that. Pass A asks one
question:

> **Does this document set say what it thinks it says, and is any of it unsupported?**

## Context you need

- This is a **master's capstone plan**, not a PhD proposal. One person, self-paced. Human hours
  are **uncapped by user directive** (2026-09-03) — check that no document quietly reintroduces
  a cap or a deadline as a gate. A laptop is the default machine (being replaced; GPU
  unknown); UvA supercomputer access is a *decided collaboration* but **not a formalised
  allocation** — the plan claims to treat it that way; check that it does.
- **Nothing has been executed under plan 05.** No probes exist in its folder. Every number is a
  checkpoint, a literature figure, a plan-02-era measurement labelled provenance, or an
  assertion labelled assertion. Check the labels.
- This is **plan 05** (Δ-Probed IR Pipeline), created 2026-09-03. It supersedes **plan 04**,
  whose folder is **still in the tree** (`plans/04_cc-anchored-ir-pipeline/`) by design, pending
  a user decision. Plans 01–03 are git history only; do not fetch them. Plan 05 claims to carry
  plan 04's criterion, ladder, opponents, gates and both Round-6 reviews' closures **verbatim in
  substance**, and to change exactly one thing (how the CC anchor is obtained). **Verify both
  claims against plan 04's files, which you can read.**
- **Calibration warning:** these documents were drafted by an AI assistant working with the
  student, in one session, on the same day the idea was found. Be alert to fluent, confident
  sentences that assert something no one measured, and to literature figures (probe counts,
  GPU timings) drifting into budget language.
- **Status is draft.** A tidy folder is not "complete as a plan." There is no
  `Professor_Review_*` file for plan 05 yet; you are writing the first one.

## What to read

Read the files **in this workspace**. Do not fetch GitHub.

In this order:

0. [README.md](../../../README.md) and [plans/README.md](../../README.md) — status banners
   (must say plan 05 is **current and draft**, plan 04 superseded and kept, plans 01–03 removed;
   the body text below the banners was patched — check nothing still says 04 is current)
1. [../README.md](../README.md) — orientation and reading order
2. [Why_05_Supersedes_04.md](Why_05_Supersedes_04.md) — the one-table change list
3. [Overarching_Goal.md](Overarching_Goal.md) — prime directive
4. [Research_Note_2026-09-03_Delta_Probing.md](Research_Note_2026-09-03_Delta_Probing.md) — the
   source document; its §6 lists what was fetched and what was only seen in search snippets
5. [Frozen_Lines_to_Beat.md](Frozen_Lines_to_Beat.md) — claims to be plan 04's file unchanged
   in substance; diff it against `../../04_cc-anchored-ir-pipeline/GoalGathering/Frozen_Lines_to_Beat.md`
6. [Frozen_Ladder_and_Tolerances.md](Frozen_Ladder_and_Tolerances.md) — rungs, the **[05]**
   additions, pilot-note items 1–11, stop conditions
7. [Compute_Budget_2026-09-03.md](Compute_Budget_2026-09-03.md) — three budgets, the
   classification rule, the NOT_RUN table
8. [Distilled_Project_Plan_and_Quality_Checks.md](Distilled_Project_Plan_and_Quality_Checks.md)
   — gates Q0–Q8, P0–P5, deviations, claim ladder
9. [Relevant_Scientific_Papers.md](Relevant_Scientific_Papers.md) — verify statuses; items 23–41
   are new; the status vocabulary distinguishes fetched from search-snippet
10. [../probes/README.md](../probes/README.md) — probes owed
11. Plan 04's Goal, Ladder, Distilled and both Round-6 reviews
    (`../../04_cc-anchored-ir-pipeline/GoalGathering/`) — the inheritance claim
12. [../../../Rubrics/README.md](../../../Rubrics/README.md) — the mapping is not yet written
    for plan 05; note anything in the plan-05 documents that pre-commits a module to something
    the rubric reading there would not allow

## The five questions

**1. Contradictions.** Where do two documents, or two sections of one, state incompatible
things? Quote both. Likely classes (find others):

- **inheritance vs change**: plan 05 says it carries plan 04 "verbatim in substance" *and*
  lists changes of frozen intent; is every change listed in `Why_05_Supersedes_04.md`, and is
  anything changed that is not listed there?
- the tree status of plan 04 across all banners and tables;
- **K vs N_min**: plan 04's pilot note had N_min; plan 05 replaces it with K. Any leftover
  N_min, "point factory", "10⁴ points" or "learned surface" language on the promised path?
- the two debt lists (Frozen_Lines §7 vs bibliography "Named debts") — in sync?
- the "promised route uses the uninformed prior" rule vs any sentence that lets the learned
  prior lower K on a promised rung;
- "frozen now" vs "frozen at the pilot note" — is every new number (K, r_c, f_h, Q7
  tolerance, Q8 criterion, P3 effect size) in exactly one bin?
- mode E vs mode G: the Goal says the cost "does not grow with the molecule"; the Research
  note and budget say mode E is 2M-plus. Which sentence wins, and does the Goal admit it?

**2. Unsupported claims.** Which statements are presented as established but cite no
measurement, no fetched source, and no probe? Distinguish *stated without support* from
*supported by a citation not yet verified* (check the status marks are used honestly, and
that **record (search 2026-09-03)** items are never quoted as facts). Specific candidates:

- "no one has applied this to a CC−DFT difference" — the note says it is a search result;
  does every other file repeat it as a search result or as a fact?
- the O1NumHess "~100–124 gradients" and Sanders "30 % of columns" figures — DFT-level results
  on other systems; where do they appear, and are they ever used as if they were K?
- the GPU4PySCF timing (search snippet only) — used anywhere as a budget?
- "no analytic DLPNO-CCSD(T) gradient advertised" — what exactly was checked, and does any
  document overstate it as "does not exist"?
- the locality of Δ — asserted from other fields' locality (DLPNO itself, srΔML, MOB-ML);
  does any sentence treat it as established for PAH curvatures rather than as the Q8 bet?
- every timing (all are old-laptop provenance, vendor figures, or assertions — verify labels).

**3. Number drift.** Same quantity, different values/units/definitions anywhere: 168 h; 10 vs
15 cm⁻¹ and what each governs; the ~1 cm⁻¹ bind; scale factors 0.964/0.979/0.975; rung species;
mode counts (coronene 102; C₃₈₄H₄₈-class "≈1,290" — from what atom count, and is that count
stated?); dates (2026-09-02 vs -03); gate numbering (plan 04 had Q0–Q6, plan 05 Q0–Q8 — any
cross-reference still pointing at the old numbering?).

**4. Loopholes.** The gates exist to stop the author declaring success without earning it.
**Try to defeat them.** Candidates:

- the **pattern set**: can patterns be added after a poor recovery residual is seen? What
  sentence prevents it, and is the residual defined before or after the hash?
- can **K** be chosen after seeing which K gives a good spectrum at R0? The pilot note freezes
  K from "the held-out residual curve" — is that curve itself a pipeline-vs-lab number?
- the **Q7 reference**: computed with the same frozen domains as the probes — can a
  domain-freezing bias hide by being present in both? Is that stated?
- the **shuffled-probe null**: can it be made to fail trivially (e.g., by a prior that
  dominates the solution)? Does the promised route's "uninformed prior" close that?
- the **learned prior**: can it enter a promised rung through the back door ("K reduced
  because P3 succeeded at the previous rung")? Read Ladder §3 and Distilled §4 together.
- the **Δ=0 null**: does it use DFT anharmonic constants (so that it is the honest "no CC"
  arm), and is that pinned?
- **Q8's criterion**: "K does not grow faster than the pilot-note criterion" — is the form of
  that criterion fixed now, or can it be chosen after K(R2) is known?
- can a cost sentence ("size-independent") leak into Module 08 via the Goal's second sentence?

**5. Unreadable without the author.** Which passages assume knowledge that lives only in the
research session or the author's head? Δ₂/Δ₃/Δ₄ notation, "mode E / mode G", "off-diagonal
low rank", "pattern", "held-out residual", "uninformed prior" — is each defined before use, in
the file where it is first used? Any acronym (DLPNO, LNO, PNO, GVPT2, MD-ACF, THC) used before
defined? Plan-02/04 probe references without a path a cold reader can check?

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

Use **Round 7, Pass A, issues 1–N**. Pass B will use Round 7 domain issues 1–N.

**Do not write Pass B in the same file.**
