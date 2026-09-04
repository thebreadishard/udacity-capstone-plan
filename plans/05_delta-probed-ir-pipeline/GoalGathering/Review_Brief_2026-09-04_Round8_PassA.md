# Review brief — Round 8, Pass A: cold read of the patched set

**Give this to the reviewer first. Do not give Pass B until Pass A's findings are written down.**

---

## Your role

You are a careful, sceptical reader with no memory of Round 7. You are reading a plan that has
been patched twice in one day after two reviews, then amended five times the next day by user
decisions, then extended with a side project. That history is the reason you are here: text
that is edited that much drifts, and the last person who could see the drift is the one who
made the edits.

You are not judging the quantum chemistry or the ML. Pass B does that. Pass A asks one question:

> **Does this document set say what it thinks it says, and is any of it unsupported?**

## Context you need

- Master's capstone plan, one person, human hours uncapped by directive. The B2 machine is
  named (an 8-core laptop, 32 GB, no CUDA GPU). UvA cluster access is a decided collaboration,
  not an allocation. **Nothing has been executed under plan 05; no code of the side project
  exists.**
- **Plan 05** supersedes plan 04; **all five plan folders are in the tree** (01–04 read-only
  records, restored 2026-09-04). Plans 01–03 are not to be reviewed; they exist so a reader
  can open them.
- Plan 05's Round 7 record: Pass A (21 findings, all closed), Pass B (13 findings, conditional
  verdict, all six blocking items written in the same day). **Pass B's patches were never
  re-reviewed.** Then, on 2026-09-04, the user closed six open decisions and issued two
  general directives ("the goal binds; methods are means"; "inheritance is not authority"),
  and a pre-registered side project was added. Every one of those changes was made by
  find-and-replace across seven or more files. Expect seams.
- **Calibration warning:** drafted by an AI assistant with the student. Be alert to confident
  sentences that assert something no one measured; to old sentences that survived a patch and
  now contradict a new one; and to decisions recorded as "decided" in one file and still
  "open" in another.

## What to read (in this workspace; do not fetch GitHub)

In this order:

0. [README.md](../../../README.md) and [plans/README.md](../../README.md) — banners and tables
   (five plans in the tree; 05 current; 01–04 read-only)
1. [../README.md](../README.md) — orientation; the review record; the six decisions
2. [Why_05_Supersedes_04.md](Why_05_Supersedes_04.md) — the change table (24 rows)
3. [Overarching_Goal.md](Overarching_Goal.md) — prime directive, the two 2026-09-04 directives,
   the decision list
4. [Research_Note_2026-09-03_Delta_Probing.md](Research_Note_2026-09-03_Delta_Probing.md) — the
   source, with its §8 errata (§§1–7 are deliberately left as written; §8 wins)
5. [Frozen_Lines_to_Beat.md](Frozen_Lines_to_Beat.md)
6. [Frozen_Ladder_and_Tolerances.md](Frozen_Ladder_and_Tolerances.md) — sentence types, rungs,
   the two dated notes, frozen-now vs pilot-note (items 1–13), stop conditions
7. [Compute_Budget_2026-09-03.md](Compute_Budget_2026-09-03.md)
8. [Distilled_Project_Plan_and_Quality_Checks.md](Distilled_Project_Plan_and_Quality_Checks.md)
   — gates Q0–Q8, P0–P5, deviations, fail-closed sentences, claim ladder
9. [Relevant_Scientific_Papers.md](Relevant_Scientific_Papers.md) — items 1–49 and statuses
10. [../probes/README.md](../probes/README.md)
11. [Capstone_Mapping.md](Capstone_Mapping.md)
12. [Project_Proposal_2026-09-03.md](Project_Proposal_2026-09-03.md)
13. [Side_Project_2026-09-04_ModeG_Gradients.md](Side_Project_2026-09-04_ModeG_Gradients.md)
14. The Round-7 reviews, for what they asked to be closed:
    [Professor_Review_2026-09-03_Round7_PassA.md](Professor_Review_2026-09-03_Round7_PassA.md),
    [Professor_Review_2026-09-03_Round7_PassB.md](Professor_Review_2026-09-03_Round7_PassB.md)
15. [../../../Rubrics/README.md](../../../Rubrics/README.md) and the Module 05 rubric's dataset
    clauses (the mapping quotes them)

## The five questions

**1. Contradictions.** Quote both sides. Classes to look for, beyond the usual:

- **Decided vs open.** Six decisions were closed on 2026-09-04. Find every sentence in the set
  that still treats any of them as open, conditional or "the user may veto" — including inside
  tables, the proposal's §10/§13, the mapping's §5, the Ladder's licence cells, and the
  "Not yet done" lists.
- **Mode E vs mode G after decision 5.** The Goal now says mode E is *guaranteed* and mode G
  *aimed for*. Earlier patches called mode G a "bonus" in several places. Which survive, and
  do any of them still make a claim (e.g. "no size claim") that the side project's success
  clause contradicts?
- **The learned prior after the inheritance directive.** It was barred from promised rungs;
  now it may enter under a licence. Find every "never on a promised rung" that survived.
- **Fragment probing after decision 1.** Find any "if the user decides fragments in" or
  "either branch" wording that survived; check the fail-closed sentence for R6 in Distilled §8
  against the Ladder's dated note.
- **The change table vs the documents.** Why_05 now has 24 rows (numbered 1–23 plus a row 24
  inserted above row 23). Does every change of frozen intent made on 2026-09-04 appear there
  (the R2 set; the R6 form; the licence; the side project; the B2 machine; the M05 corpus)?
- **Debt lists**: Frozen_Lines §7 vs bibliography "Named debts" — still identical? And is the
  "Method debts" list complete against items 27–49?

**2. Unsupported claims.** Specific candidates:

- The side project's §1.2 ("the AD gradient with fixed spaces is the *exact* derivative of the
  frozen-domain surface") — the note calls it "this plan's own reasoning". Is it presented as
  reasoning everywhere it is repeated (Goal, proposal §5.3, Distilled §3)?
- The side project's claim that PySCFAD's LNO-CC gradient "exists" — the bibliography says the
  README does not mention it and M1 verifies where it lives. Does any sentence overstate this?
- pyscf-forge "LNO-CCSD(T)": the changelog names LNO-CCSD. Where is "(T)" asserted as available?
- Item 45's "~5 cm⁻¹" is snippet grade; the pilot-note expected-effect line quotes it — with the
  label?
- The laptop RAM (32 GB) — now from a screenshot; is anything still "16 or 32"?
- Any timing anywhere used as a budget (the plan forbids it).

**3. Number drift.** Pilot-note items (1–13) referenced consistently by number across Ladder,
Distilled, Budget, probes README? Q-gate numbering (Q0–Q8)? Bibliography item numbers cited in
text (23, 24, 30, 33, 42–49) point at the right rows? The 12-week side-project checkpoint vs
the 168 h machine checkpoint — never confused? Change-table row numbering.

**4. Loopholes.** Try to defeat:

- **The licence for the learned prior** (Ladder §3): can a prior-assisted recovery pass the
  "prior-free reference check" if the reference check itself is defined only at R0–R1 (Q7) and
  as a direct-block subset at R2–R3? What exactly is compared, and could the prior shape the
  parts the direct blocks do not cover?
- **The side project's kill criterion**: "12 weeks of B1 hours logged to its bucket" — can hours
  be logged elsewhere to keep the clock from running? Does the booking rule (one bucket per
  entry) close this?
- **Success clause of the side project**: "M3 passed: mode G is licensed on R1" — is the
  gradient's *smoothness* (Q6 noise line) required too, or only its correctness against finite
  differences of the same frozen energies (which would inherit any non-smoothness)?
- **Fragment probing under Q8**: the R6 certificate withdraws a family that fails Q8 at R2–R3.
  Is there any rung between R3 and R6 where Q8 is re-measured on the actual fragment scheme, or
  does R6 inherit a coronene-size verdict for a 432-atom flake without any measurement at R4?
- **Pilot-note timing**: the note is now written after four probes including the R1 smoothness
  probe; can any of those four leak a Δ₂ recovery result into the note?

**5. Unreadable without the author.** The set now uses: mode E/G, K/K_off/K_cap, ρ/ρ\*, τ₇/d₇,
r_c/r_max/ε₈/γ, f_h, structural vs learned prior, CMA/CMA-0/CMA-2, CPS, LNO/DLPNO/PNO, M1–M4,
B1/B2/B3, Q0–Q8, P0–P5, reading 1/2, "the licence", "the dated note". Is each defined before
its first use in the file where a cold reader meets it? Is the glossary in the plan README
complete against this list?

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

Use **Round 8, Pass A, issues 1–N**. Pass B will use Round 8 domain issues 1–N.

**Do not write Pass B in the same file.**
