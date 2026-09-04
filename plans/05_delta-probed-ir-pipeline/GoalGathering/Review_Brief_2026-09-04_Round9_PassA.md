# Review brief — Round 9, Pass A: cold read after the Round-8 Pass B patches

**Give this to the reviewer first. Do not give Pass B until Pass A's findings are written down.**

---

## Your role

A careful, sceptical reader with no memory of Rounds 7 and 8. The set was patched twice
yesterday and three times today; the last patch (after Round-8 Pass B) rewrote the ladder, the
distilled plan and the side-project note and touched every other file. Your question is the
same as every Pass A:

> **Does this document set say what it thinks it says, and is any of it unsupported?**

You are not judging the chemistry. Pass B does that.

## Context you need

- Master's capstone plan, one person, human hours uncapped. The B2 machine is a named laptop
  (8 cores, 32 GB, no CUDA GPU). UvA cluster access is a collaboration, not an allocation.
  **Nothing has been executed; no code exists.** All seven user decisions are closed (Goal,
  "Decisions of 2026-09-04"); nothing is open.
- **Plan 05** is current; plans 01–04 are read-only records in the tree. Do not review them.
- Review history: Round 7 A (21 closed), Round 7 B (conditional; 13 closed), Round 8 A (20
  closed), Round 8 B (conditional; 18 closed). Each closure list is in the plan README's review
  record. **Round-8 Pass B's patches were never re-read**; that is why you are here.
- **Calibration warning:** drafted by an AI assistant with the student; the last patch
  introduced several new objects at once — an estimator for σ, a noise-aware stopping rule with
  a constant c, an absolute η₈ with a scale S, a four-part fragment licence with r_f, a
  frozen-space definition with a printed assignment, u_band, a canonical feasibility probe.
  New objects introduced by find-and-replace across nine files are where seams live.

## What to read (in this workspace; do not fetch GitHub), in order

0. [README.md](../../../README.md), [plans/README.md](../../README.md)
1. [../README.md](../README.md) — review record; decisions; "Not yet done"
2. [Overarching_Goal.md](Overarching_Goal.md) — the glossary first
3. [Why_05_Supersedes_04.md](Why_05_Supersedes_04.md) — rows 1–32
4. [Frozen_Ladder_and_Tolerances.md](Frozen_Ladder_and_Tolerances.md)
5. [Distilled_Project_Plan_and_Quality_Checks.md](Distilled_Project_Plan_and_Quality_Checks.md)
6. [Compute_Budget_2026-09-03.md](Compute_Budget_2026-09-03.md)
7. [../probes/README.md](../probes/README.md)
8. [Side_Project_2026-09-04_ModeG_Gradients.md](Side_Project_2026-09-04_ModeG_Gradients.md)
9. [Frozen_Lines_to_Beat.md](Frozen_Lines_to_Beat.md)
10. [Relevant_Scientific_Papers.md](Relevant_Scientific_Papers.md) (items 1–51, statuses)
11. [Capstone_Mapping.md](Capstone_Mapping.md)
12. [Project_Proposal_2026-09-03.md](Project_Proposal_2026-09-03.md)
13. [Research_Note_2026-09-03_Delta_Probing.md](Research_Note_2026-09-03_Delta_Probing.md)
    (§§8–9 win over §§1–7)
14. [Professor_Review_2026-09-04_Round8_PassB.md](Professor_Review_2026-09-04_Round8_PassB.md)
    — for what it asked to be closed (its 18 findings), so you can check each closure is in the
    text and consistent across files

## The five questions

**1. Contradictions.** Quote both sides. Look especially for:

- The **new objects** used inconsistently: σ_E/σ_g (per-point scatter vs residual about a fit —
  the estimator is defined once in Ladder §3; does every other mention match it, including the
  side project's M2 and the probes README?); **ρ\*** (still "frozen in the pilot note" anywhere,
  vs ρ\* = c·ρ_noise with c the frozen number?); **K_cap** ("from the dry run" vs "from the
  noise-injected dry run"); **η₈** (relative vs absolute, "blocks" vs "couplings", η₈ vs η₈·S);
  **the fragment licence** (three parts vs four parts; (b′) present everywhere it is promised?
  "direct-block probe on the R6 fragments" vs "fragment-radius convergence test"); **r_max vs
  r_f**; **mode E on every rung** (any survivor of "elsewhere mode E runs" or "mode G is the
  route on licensed rungs" without "in addition"?); **M5** (run/no-run vs both checks);
  **decidability** ("measured grid" vs u_band anywhere?); **the anchor basis** (cc-pVTZ at
  R0–R1 stated everywhere the basis is mentioned? the side project says cc-pVTZ for M2–M4 and
  "the R3 deck basis" for M5 — consistent with Ladder §3?).
- **Decision 7** closed today: any text still calling it open, or treating M02 as possibly
  submitted, or the M05 reuse exposure as pending?
- **Pilot-note inputs**: the list of what precedes the note now has seven items (Ladder §4
  opening); do Budget §4, probes README and the README's "Not yet done" list the same seven?
- **Pilot-note item numbering** 1–13: item 8 is now "the stopping constant c" — does every
  reference to "item 8 (ρ\*)" elsewhere say c? Item 12 now includes h and the pair list; item 9
  now "per mode, noise-injected".
- Why_05 rows 28–32 vs the documents they cite; the "does not change" paragraph.
- The two debt lists (Frozen_Lines §7 vs bibliography); the "Method debts" list vs items 48–51.

**2. Unsupported claims.** Candidates:

- Engine facts now stated as fetched (items 48–49): is the *author's* fetch recorded, and is
  any remaining sentence still hedging in the old way ("(T) to be verified at M1", "code
  unlocated") or, conversely, claiming more than a directory listing shows (e.g. that (T) is
  differentiated end-to-end — item (a) of the side project says that is verified there; check
  no document says it is already known)?
- The Round-8 reviewer's **recalled** numbers that entered documents: QM9 ≤ 9 heavy atoms; the
  cc-pVTZ function counts and per-fragment GB sizing; lightpipe temperatures; the SRD 35
  8 cm⁻¹ statement (snippet). Each must carry its grade where it appears (Goal, Distilled §6,
  Mapping M05, Ladder R2 row, side project §4, Frozen_Lines §5, item 50).
- The noise-line constants 0.82 and 2.8 — is their derivation traceable (note §8; Round-8 Pass
  B) and is the "one fewer power of q_s" sentence for σ_g stated as arithmetic, not as a
  measurement?
- Any timing used as a budget (the plan forbids it), including the "hours/days" language in
  Ladder §3's anchor-basis bullet and Budget §4.

**3. Number drift.** Nine points / four modes / ≈ 40 energies for the R1 smoothness probe
(Ladder R1 row says "three modes plus one totally symmetric"; Distilled Q6 "four modes"; Budget
"~40"; probes README "≈ 40"; the side project's M1 grid "three benzene modes" — consistent?).
Energies per direct coupling (four per pair per family) and the "≈ 12 energies per pair"
survivors. M3's 28 GB cap vs the 32 GB machine. Change-table row numbering and the README's
row count. Bibliography numbers cited in text (48–51 new).

**4. Loopholes.** Try to defeat:

- **The stopping rule**: ρ_noise uses RMS_resp of the rung's *own* held-out responses — can a
  pattern set with large-amplitude responses lower ρ_noise and so lower K? Is q_s pinned before
  RMS_resp is seen (the amplitude comes from the Q6 grid — yes?), and is c fixed before any
  local-CC response exists (item 8 — yes?)? Say whether the rule is closed.
- **The absolute η₈**: S = √(Σ direct²/n_pairs) is dominated by the near pairs; can a deck with
  many near pairs make every mid pair pass? Is the pair list frozen before responses (item 12)?
- **The fragment licence part (c)**: "r_f + one ring" — is r_f defined for a rung where part (b)
  never ran (R6 uses coronene's r_f?) — say which r_f R6 uses.
- **The learned-prior licence**: P3 "reported on the PAH held-out tensors as well" — is a
  threshold attached to that report, or only to the corpus number? Can a prior that fails on
  PAHs but passes on QM9 be licensed?
- **The pilot-note seal**: the smoothness probe now seals *fit coefficients*; the σ it prints
  is the residual about that fit. Is σ itself free of Δ₂ information? (It is — say so if you
  agree, or say why not.)
- **The canonical feasibility probe**: one energy, extrapolated to a Hessian count — who fixes
  the extrapolation factor and the "fits / does not fit" threshold, and when?

**5. Unreadable without the author.** With the Goal's glossary as the single definition point:
does every file use only glossary terms, and does the glossary contain every term the files use
(u_band, S, r_f, c, ρ_noise, (b′), "resolved pair", "at noise", "closure depth one", "assignment
permutation", "re-projected")? Any acronym used before the glossary defines it? Any pointer to
"the dated note" that is ambiguous now that Ladder §2 has two dated notes plus an addendum?

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

Use **Round 9, Pass A, issues 1–N**. **Do not write Pass B in the same file.**
