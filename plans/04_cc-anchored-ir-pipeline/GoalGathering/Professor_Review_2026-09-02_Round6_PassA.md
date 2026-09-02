# Professor review — Round 6, Pass A (cold read)

**Date.** 2026-09-02.
**Scope.** Plan 04 document set as it stands in this workspace. No GitHub fetch. Plans 01–03 not
fetched from history except where *this* tree already names a commit or filename. Pass B is not
in this file.

**Verdict:** No — not internally sound enough to proceed to Pass B until the blocking findings
are patched. The relative criterion, accuracy/reach split, three budgets, and null-row *intent*
are written down; they are not yet the same story in every file, and two asserted world-map
facts sit next to unpaid debts in the same folder.

---

## Blocking findings

### 1. Plan-03 tree status contradicts itself inside the banners the brief said to trust
**Where:** [README.md](../../../README.md) (banner vs table); [plans/README.md](../../README.md)
(prose vs table vs “Version 04” close); [plans/04_cc-anchored-ir-pipeline/README.md](../README.md)
status line.
**What:** The root banner says plan 03 “remains in the tree only until its scheduled removal.”
The root table on the same page says it was “**removed from the tree the same day**.”
`plans/README.md` repeats both: “03 stays in the tree only until its scheduled removal” and, in
the table, “**Removed from the tree on 2026-09-02**”; later, “it stays readable until its
scheduled removal.” Plan 04’s own README still says plan 03 “remains in the tree only until its
scheduled removal.” A directory listing of `plans/` contains only `04_cc-anchored-ir-pipeline/`
and `README.md`.
**Why it matters:** Pass A’s first instruction was to read those banners. A cold reader (or a
defence examiner) cannot tell whether 03 is present, scheduled, or gone. The set does not know
its own tree.
**Status:** open

### 2. The scientific question joins “beat … against laboratory spectra” to sizes with no lab
**Where:** [Overarching_Goal.md](Overarching_Goal.md) “The scientific question”; contrast
[Frozen_Ladder_and_Tolerances.md](Frozen_Ladder_and_Tolerances.md) §1.
**What:** The Goal asks whether the pipeline can “measurably beat scaled-harmonic DFT (PAHdb
v4.00) and DFT-ceiling MLMD (Mai 2025) **against laboratory spectra, and do so at sizes where
no anharmonic or CC-quality prediction exists at all**.” The ladder forbids the word “beat” on
reach rungs and forbids lab-scored claims where no lab exists. Distilled §2 repeats the crossing
in miniature: Mai’s row is “beat its *teacher*” while R4–R5 are theory-vs-theory.
**Why it matters:** This is the leftover absolute/relative and accuracy/reach mix the freeze
claimed to have split. If the prime directive’s one-sentence question already concatenates the
two claim types, Module 08 can quote the Goal and ignore the ladder.
**Status:** open

### 3. Q4 / §4 forbid lab values in any training artifact; Module 04 trains on lab residuals
**Where:** [Distilled_Project_Plan_and_Quality_Checks.md](Distilled_Project_Plan_and_Quality_Checks.md)
§4 bullet 3 and §7 Q4; [Capstone_Mapping.md](Capstone_Mapping.md) §3 Module 04.
**What:** Distilled §4: “Any lab scoreboard value entering training, validation, stopping, or
sampling decisions” is a forbidden deviation. Q4 pass condition: “no scoreboard value reachable
from any training artifact / prints 0.” Mapping M04: the training table *is* the paired
theory↔lab band match; the target is “per-band **error of scaled-harmonic DFT against the lab
band**.” M05 then says “The laboratory scoreboard is never a training, validation, or stopping
input” as if that were already true of the whole plan.
**Why it matters:** As written, M04 cannot pass Q4, and Q4 cannot mean what it says if M04 is
load-bearing. A later author will either drop the cheap line or quietly restrict Q4 to M05
without a dated note. That is a gate that does not close.
**Status:** open

### 4. Canonical CCSD(T) is both affordable at R1 and the wall that makes DLPNO necessary at R1
**Where:** Distilled §3 “Anchor points”; Frozen_Ladder §2 R1 row; Compute_Budget §4.
**What:** Distilled: “canonical CCSD(T) is affordable at R0–R1 — measured, plan 02.” Ladder R1:
“The measured canonical-(T) memory wall sits between R0 and R1 (plan 02); DLPNO becomes
necessary.” Budget: “Canonical (T) in-core wall: **fails at ~114 bf with 28 GB** — the R0/R1
boundary is a measured fact.” Benzene ~102 bf is the affordable point; naphthalene is the next
rung.
**Why it matters:** R1 is the license for every DLPNO anchor above it. If canonical does not
run at R1, the license is not a same-molecule check. The documents do not agree which of those
sentences is the freeze.
**Status:** open

### 5. 15 cm⁻¹ is frozen *now* as a convention and also owed to the pilot note as a measurement
**Where:** Frozen_Ladder §3 vs §4; Capstone_Mapping §3 Module 03; Overarching “Scope boundaries.”
**What:** Ladder §3 (frozen now): “Ar-matrix comparisons carry a **15 cm⁻¹** shift tolerance
(plan-02 convention).” Ladder §4 (pilot note) does *not* list 15 cm⁻¹. Mapping M03: the
pre-registered matrix-vs-gas test “feeds §4 of the ladder: the pilot note’s band lists and the
**measured (not conventional) 15 cm⁻¹** tolerance.” Overarching treats ~15 cm⁻¹ as already
known. Two freeze bins, one number.
**Why it matters:** If M03 measures 8 cm⁻¹ or 22 cm⁻¹, nobody can tell whether the ladder’s
§3 number moves, stays, or is renamed. The “every number in exactly one bin” rule fails on the
tolerance the scoreboard is built around.
**Status:** open

### 6. C₃₈₄H₄₈ “only prediction on Earth” is asserted; the same folder marks the species check unpaid
**Where:** Overarching “Size and compute”; Frozen_Lines §1–§2 vs §7 item 5; bib Named debts item 6;
root README “current objective.”
**What:** Overarching (no “class” hedge): “For C₃₈₄H₄₈ the only existing prediction anywhere is
scaled harmonic B3LYP/4-31G.” Frozen_Lines §1: “For C₃₈₄H₄₈-class species the **only** prediction
on Earth is scaled harmonic B3LYP/4-31G.” Line A role: “the *only* opponent at C₃₈₄H₄₈.” The
evidential chain on file is: size bin 101–386 C, and NASA’s Orion Bar fit uses
`N_carbon,max = 384`. Frozen_Lines §7.5 and bibliography debt 6 both say whether **C₃₈₄H₄₈
itself** has a v4.00 entry is not done. Presence in a fit parameter is not a species entry.
**Why it matters:** R6’s opponent, the “first beyond-scaled-harmonic spectrum there” sentence
(Distilled §9.5), and the size promise all rest on a molecule that may not be in the library
the plan treats as its only opponent.
**Status:** open

### 7. The two debt lists claim to be the same list and are not
**Where:** Frozen_Lines §7; [Relevant_Scientific_Papers.md](Relevant_Scientific_Papers.md)
“Named debts (same list as Frozen_Lines §7, kept in sync).”
**What:** Frozen_Lines has **five** debts (Bos MAE; Mackie/Esposito; Mai/Mulas landings; Joblin
T-dependence; C₃₈₄H₄₈ per-species). The bibliography has **six**: the same four, then
**DLPNO/ORCA + Sylvetsky identifiers** as item 5, and C₃₈₄H₄₈ as item 6. The parenthetical
says they are kept in sync.
**Why it matters:** A cold reader who trusts the parenthetical will miss the unpaid method
citations that Distilled’s Q0 deck needs, or will think Frozen_Lines already owns them.
**Status:** open

### 8. The pilot note can be written after R0 pipeline-vs-lab numbers exist
**Where:** Frozen_Ladder §3 last bullet vs §4 opening; probes/README item 1; Distilled P2.
**What:** Ladder §4: numbers are written “after the R0 pilot and the lab-scoreboard re-read
probe have printed, and **before any pipeline-vs-line comparison is scored**.” Ladder §3:
windows “are fixed in the pilot note **before any pipeline number exists for that molecule**.”
probes/README: the R0 pilot *is* “geometry → Hessian → harmonic bands → **lab comparison**.”
Those two sentences cannot both be true for benzene. Nothing says the R0 lab comparison is
not a P2-class number, or that margins/effect sizes may not be read off it.
**Why it matters:** The gates exist to stop the author declaring success without earning it.
If beat margins, promised families, and (per Distilled) P3 effect size are filled after a
scored benzene table exists, the pilot note is a post-hoc protocol. No other sentence closes
this. Distilled §4 forbids re-windowing *after* a pipeline number exists — it does not forbid
choosing the windows after seeing the R0 table, which is the same act with a different name.
**Status:** open

---

## Non-blocking findings

### 9. “~5 cm⁻¹ MAE” is labelled unread and then used
**Where:** Frozen_Lines §3 Bos paragraph; Distilled §2 Ethereal AI row.
**What:** “the MAE value recorded in plan 02 (~5 cm⁻¹) is **not re-read** … — re-read before
quoting a number.” The next sentence: “If ML-corrected scaling really delivers **~5 cm⁻¹ MAE**,
an anharmonic method that lands at 10 cm⁻¹ has not earned its cost.” Distilled does not quote
the 5, but makes M04 “reproduce” that line. The number is not used as a gate; it is used as a
cost-justification.
**Why it matters:** Fluent caution followed by use of the same figure is the failure mode this
pass is for. Harmless until someone cites Frozen_Lines §3 as if the MAE were fetched.
**Status:** open

### 10. “Reading 1” is decided; the rejected reading and the reuse rule are not on the page
**Where:** Capstone_Mapping §3 M04, §4, §5.1; [Rubrics/README.md](../../../Rubrics/README.md)
dataset rule.
**What:** Mapping says “reading 1” and never states reading 2. A cold reader cannot know what
was rejected. Rubrics/README’s *load-bearing* rule is public-before-start **and not reused from
an earlier capstone project**. The “Accepted Sources are examples” note is only about the
portal list. Mapping applies that note correctly to M03 (PAHdb/NIST not on the example list).
It then leans **further**: joining the M02 and M03 tables, adding a residual column and a new
DOI, is treated as satisfying non-reuse. That is a reuse-rule reading, not an Accepted-Sources
reading, and the rejected alternative (independent public vibrational benchmark) is named only
as a fallback if a grader objects later.
**Why it matters:** Distinctness is the M04 landmine the mapping itself lists. An examiner who
has only Rubrics/README will not reconstruct “reading 1.”
**Status:** open

### 11. M04 has no tuning-parity promise; promised families are not closed in the freeze-now bin
**Where:** Distilled §5–§6 (parity for Δ vs direct only); Frozen_Ladder §3 families vs §4.2
“promised family”; Mapping M04.
**What:** Δ/direct arms share splits, budget, ≥3 seeds. The sklearn M04 baseline has no HPO
budget, seed rule, or “do not strip features after the pilot note” sentence. “Promised
families” appear in the beat-margin rule; the closed list of families in §3 is a *reporting
unit*, not a P2 contract. A family that looks bad on R0 can fail to enter the pilot note’s
band list.
**Why it matters:** P2 can be made easier by weakening M04 or by dropping a family before the
note is dated. Neither is a dated-deviation trigger as written.
**Status:** open

### 12. P4 (Δ=0) does not bind bands, windows, or seeds to P2
**Where:** Distilled §7 P2 and P4(a).
**What:** Δ=0 “must lose P2 wherever the anharmonic claim is made.” P2’s bands, windows, and
seeds are not copied into P4. Two fail-closed sentences disagree: P4 table “the anharmonic
claim is void”; §7 last paragraph and §8 “explained by the harmonic baseline.”
**Why it matters:** A null that can be scored on a different family than the win is decoration.
The dual wording lets a later paper pick the softer sentence.
**Status:** open

### 13. Intensities are in the claim; P2 scores positions
**Where:** Overarching prime directive and scientific question; Distilled §1 and §3
“Intensities”; Distilled P2.
**What:** The pipeline “produces IR band positions **and intensities**” that beat the lines.
P2 is paired per-band |error| on lab **positions**. No P-gate scores intensities. Line A’s
table includes intensity; the beat protocol does not say they are out of scope.
**Why it matters:** Module 08 can ship a position win and still say the Distilled claim, which
includes intensities, was met.
**Status:** open

### 14. R2 is typed accuracy while one of its three molecules has no lab spectrum
**Where:** Frozen_Ladder §2 R2 row.
**What:** “pyrene C₁₆H₁₀ + the C₁₈H₁₂ trio (tetracene, chrysene; triphenylene has no lab
spectrum)” — type **A**. Triphenylene is inside an accuracy rung with a parenthetical that it
cannot be lab-scored. IRMPD “for cations (Tang 2025 class)” sits in the same lab-scoreboard
cell without saying the pipeline species are cations.
**Why it matters:** A mixed A/R row will be scored as A. Cation lab vs (unspecified) neutral
pipeline is a silent opponent swap.
**Status:** open

### 15. Stale layout and a broken “owed” link
**Where:** plans/README.md “Layout”; Capstone_Mapping §4 DOI-before-claim sentence;
Rubrics/README.md “What is not here”; AI_Chats/README.md grok_chat_4 row.
**What:** plans/README still describes GoalGathering as only Overarching_Goal + Frozen_Lines,
and Papers as indexed by “plan 03’s bibliography.” Mapping links
`[Relevant_Scientific_Papers](Frozen_Lines_to_Beat.md)` and still says “bibliography file
owed” — the bibliography file exists beside it. Rubrics/README says documents 10–12 “now live
in `plans/<plan>/GoalGathering/Horizon/`”; plan 04 has no Horizon and claims that as a virtue.
AI_Chats/README summarises grok_chat_4 as the HAVO walkthrough ending at “why a full CC surface
fails for coronene,” which is only the first half of the 360-line file; the DLPNO/ORCA recipe
is in the same transcript.
**Why it matters:** Cold-reader navigation fails; the named source conversation is
under-described in the dump that is supposed to be the primary source.
**Status:** open

### 16. Acronyms and plan-02 artefacts assume the author
**Where:** plan 04 README Provenance (DLPNO on first use); Overarching method skeleton (DLPNO,
VPT2); bib item 15 (TightPNO); Frozen_Lines §5–§6 and Mapping M03 (uids, NIST parser).
**What:** DLPNO, VPT2, and PNO are never expanded in this tree. Frozen_Lines does name
`pahdb_experimental_2026-08-28.py` and commit `800f3aa` — that is checkable. Mapping M03 only
says “parser exists in plan-02 probes, git history” with no filename. Distilled §3 still says
canonical is “measured, plan 02” without a probe path in *this* folder (probes/README: no
probes exist yet).
**Why it matters:** The defence audience does not have git history in their head. The plan
claims plan-02 lessons are structural; the citations to the measurements still live off-tree.
**Status:** open

### 17. P3 effect size is owed to the pilot note in Distilled and missing from Ladder §4’s list
**Where:** Distilled P3; Frozen_Ladder §4 items 1–3; plan 04 README “Not yet done.”
**What:** Distilled: effect size “in the pilot note.” Ladder §4’s closed list is band list,
beat margin, P-gate numbers (imaginary-frequency tolerance, scale-factor policy). README owes
“P3 effect size” to the same note. Three files, two inventories.
**Why it matters:** A number with no bin can be written when convenient. Same class as
issue 5, smaller blast radius.
**Status:** open

### 18. B1 module ownership overlaps; not a number clash
**Where:** Compute_Budget §2; Capstone_Mapping §6.
**What:** 840 h and the five bucket sizes appear once. Mapping adds no hours. Module 05 sits
in the 200 h infrastructure bucket *and* the 240 h thesis bucket; Module 08 sits in thesis
*and* generative/agentic/synthesis. That is overlapping assignment, not 160 vs 200 drift.
168 h is clearly B2 per rung-pilot (one calendar week), not a leftover plan-03 teacher total.
Scale factors 0.964 / 0.979 / 0.975 agree between Frozen_Lines §2 and bib item 1.
**Why it matters:** Hours can be booked twice without crossing a cap. Recorded so Pass B does
not have to rediscover it; not a contradiction of values.
**Status:** open

### 19. Source-conversation risks are mostly carried; the ~1 cm⁻¹ bind is not
**Where:** grok_chat_4 (full file); Overarching method skeleton; Frozen_Ladder §5.4; Compute_Budget §3.
**What:** DLPNO roughness, sampling/fit erasing the CC advantage, per-molecule (no transfer)
scope, and the “thousands of node-hours / assertion not a budget” cost are in the plan and
labelled. Jet-cooled + test RMSE as the honesty check is thinned to “lab scoreboard” plus an
error-budget bullet. The chat’s “~1 cm⁻¹ only if experiment and the controls allow it” is not
a sentence in the freeze; lab-facing claims “may be finer if the measurement supports it”
(Ladder §3) is weaker.
**Why it matters:** Not a dropped opponent; a dropped stop. Easy to over-claim on benzene
against NIST without the chat’s bind.
**Status:** open

---

## What passed

- **Plan 04 is current and draft** in the three READMEs that matter; nothing in this tree is
  labelled a plan-04 *result*. Completeness is explicitly withheld pending this review and Pass B.
- **Plans 01–02 are git history only** in those READMEs (plan 03’s *wording* is issue 1; the
  filesystem matches “removed”).
- **Relative criterion vs “chemically precise.”** Overarching forbids the absolute phrase as a
  Module 08 result. Distilled claim language is “beat the frozen lines” / fail-closed sentences.
  No leftover “chemically precise” promise in the plan-04 GoalGathering set.
- **Accuracy vs reach, where it is not concatenated.** Ladder §1, P2 vs P5 language table, M07
  “may not emit a beat sentence without the pilot note hash,” M08 “never beat” on P5, stop
  “reach rungs may not start before R3 is scored” — these are written and consistent *with each
  other*. Issue 2 is the Goal (and Distilled §2) failing to obey them.
- **Three budgets, not mixed.** B1 840 h human, B2 168 h/rung-pilot laptop, B3 no number until
  (a) written UvA access (b) timed probe (c) dated cap. Collaboration decided, allocation not a
  fact — stated as such. Plan-02 timings labelled provenance. Caps “not estimates.”
- **Null-row intent is structural.** P4(a) Δ=0 and P4(b) noise are in the Distilled gate table,
  not a footnote. P0-fails-then-P2-uninterpreted is stated. (Issue 12 is that P4 is still
  defeatable, not that it is missing.)
- **World-map fetch marks are mostly honest** when read in the bibliography: Ricca 2026 full
  text OK; Mai arXiv abstract OK, MNRAS landing unpaid; Bos Crossref OK, MAE unpaid; Mulas
  “record”; Mackie/Esposito NOT FETCHED. Frozen_Lines table “Verified how” matches those marks
  except for the C₃₈₄H₄₈ assertion (issue 6).
- **Plan-02 measured floor** (quartet mean |err| 7.1 cm⁻¹, solo −36, duo −49) is labelled
  plan-02 / git `800f3aa` / script name, not a plan-04 probe. That is the right provenance
  label; probes/README correctly says the scoreboard must be regenerated under this plan’s hash.
- **Rule 0 (load-bearing modules)** is stated; the Pass-2 needs table is a pipeline, not a
  QM9-style detour. Mapping does not invent a busywork module in this draft. Pass 6 is honestly
  “not done.”
- **User decisions** (M04 reading 1, Transformer noted, no mentor pre-approval) are recorded as
  decisions, not as rubric text. Three “open items” are not left silently open.
- **UvA supercomputer** is not treated as a frozen allocation. Ladder stop 3 and Budget §3.1
  agree.
- **Opponent swap after scoring** is forbidden in Goal, Lines, Distilled §4. Line A/B/C names
  and versions agree across Frozen_Lines and the bibliography working identifiers.

---

## Round 6, Pass A — issue index

| # | Class | Blocking? |
|---|---|---|
| 1 | Contradiction (status banners / tree) | yes |
| 2 | Contradiction (accuracy vs reach in the Goal) | yes |
| 3 | Contradiction / loophole (Q4 vs M04) | yes |
| 4 | Contradiction (R1 canonical affordability) | yes |
| 5 | Number bin (15 cm⁻¹ now vs pilot note) | yes |
| 6 | Unsupported claim (C₃₈₄H₄₈ in PAHdb) | yes |
| 7 | Contradiction (debt lists “in sync”) | yes |
| 8 | Loophole (pilot-note timing vs R0 lab comparison) | yes |
| 9 | Unsupported / used-unread (~5 cm⁻¹ MAE) | no |
| 10 | Unreadable + rubric lean (reading 1 / reuse) | no |
| 11 | Loophole (M04 parity; promised families) | no |
| 12 | Loophole (P4 bands/seeds; dual fail-closed wording) | no |
| 13 | Loophole (intensities claimed, positions gated) | no |
| 14 | Contradiction (R2 type A includes no-lab / cations) | no |
| 15 | Unreadable (stale layout, broken “owed” link) | no |
| 16 | Unreadable (acronyms; off-tree probes) | no |
| 17 | Number bin (P3 effect size) | no |
| 18 | Number ownership (B1 overlap, not drift) | no |
| 19 | Translation gap from grok_chat_4 (~1 cm⁻¹ bind) | no |

Do not treat this file as Pass B. Domain attacks (whether the science can work) wait for a
separate review after these patches, or after an explicit decision to proceed with issues
still open.
