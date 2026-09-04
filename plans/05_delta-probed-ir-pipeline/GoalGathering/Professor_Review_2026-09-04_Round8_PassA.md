# Professor review — Round 8, Pass A (cold read of the patched set)

**Date.** 2026-09-04.
**Scope.** Plan 05 document set as it stands in this workspace, read in the brief's order and in
full: root `README.md`, `plans/README.md`, the plan-05 `README.md`, `Why_05_Supersedes_04.md`,
`Overarching_Goal.md`, `Research_Note_2026-09-03_Delta_Probing.md` (§§1–7 as written, §8 as the
part that wins), `Frozen_Lines_to_Beat.md`, `Frozen_Ladder_and_Tolerances.md`,
`Compute_Budget_2026-09-03.md`, `Distilled_Project_Plan_and_Quality_Checks.md`,
`Relevant_Scientific_Papers.md`, `probes/README.md`, `Capstone_Mapping.md`,
`Project_Proposal_2026-09-03.md`, `Side_Project_2026-09-04_ModeG_Gradients.md`, both Round-7
reviews (for what they asked to be closed), `Rubrics/README.md` and
`Rubrics/05_Deep_Learning_Systems.md`. No web fetch, no GitHub, no literature judgment; the
quantum chemistry and the ML are Pass B's. Plans 01–04 were not reviewed. Where a Round-7
closure is mentioned, I checked whether it survived the 2026-09-04 edits, not whether it was
right. No file other than this one was written or changed.

**Calibration.** The set is much tighter than the Round-7 Pass A found it. The 2026-09-03
patches (ρ\*/K_cap, Q8's fixed form, Δ₃/Δ₄ out, the R2 re-read, the two cost-sentence forms,
P4's sentences) all held. The 2026-09-04 edits are where the seams are: two of them — the
licence for the learned prior and the promotion of mode G from bonus to aimed-for route via a
side project — were made by find-and-replace and left the *operative* sentences (the mapping's
officer rule, the Distilled claim ladder, the pilot-note deviation rule, the Q6 scoping) saying
the old thing. The side project, added last, is also where the unsupported sentences now live.

**Verdict:** Not yet. The R0–R1 measurement programme is internally consistent and Pass B may
read it as it stands; the promised set beyond R1, as amended on 2026-09-04, says two different
things about the learned prior, two different things about what mode G is and when it can be
licensed, and one false thing about what the side project's failure costs — and one frozen
decision (the M05 corpus size) rests on a timing the plan itself declares invalid. Patch
blocking items 1–11, then Pass B.

---

## Blocking findings

### 1. The learned prior is admitted to promised rungs by the Goal and the Ladder, and still barred from them by the mapping's officer, the Distilled claim ladder, the Distilled §5 architecture sentence, the proposal's fit section and both glossaries
**Where:** [Overarching_Goal.md](Overarching_Goal.md) "Notation", "Scope boundaries" last bullet,
decision 4; [Frozen_Ladder_and_Tolerances.md](Frozen_Ladder_and_Tolerances.md) §3 licence
bullet; [Distilled_Project_Plan_and_Quality_Checks.md](Distilled_Project_Plan_and_Quality_Checks.md)
§3 "Structural prior", §5 first and third bullets, §9 item 8; [Capstone_Mapping.md](Capstone_Mapping.md)
§0, §2 (last paragraph), §3 M05, M07 (safeguards), M08; [Project_Proposal_2026-09-03.md](Project_Proposal_2026-09-03.md)
§12; plan-05 [README.md](../README.md) glossary.
**What:** The 2026-09-04 rule, stated identically in the Goal and the Ladder: "the learned prior
may enter a promised rung only under a **licence**: (i) P3 has demonstrated its saving … (ii) at
that rung the reference check … is computed prior-free and the prior-assisted recovery agrees
with it … (iii) the cost record says `prior = learned`". Goal decision 4: "With the licence
route, M05 is load-bearing for the cost record if P3 succeeds." Mapping §0: "adopted, with the
learned prior admitted to promised rungs under the Ladder §3 licence — load-bearing for the cost
record if P3 succeeds." Against that, in the same set:
- Mapping M07, the campaign officer's refusal list — the enforceable text: "no learned-prior run
  on R0–R3 or R6". That is the pre-directive rule verbatim. The officer as specified refuses the
  very run the licence permits, and the mapping's own M05 paragraph says the licence makes M05
  "load-bearing for K_off on R2–R3 and R6".
- Distilled §9 item 8: "P3 effect ≠ 0 → 'the learned prior buys X on the dry-run corpus'
  (bonus; never load-bearing)." Distilled §5, three bullets above the licence sentence:
  "**Promised pipeline component:** the sparse-recovery solver with the banded structural prior
  (classical convex optimisation; no neural network on the promised path)."
- Mapping M05, inside one paragraph: "on promised rungs the plan forbids it, so that the promised
  spectra never depend on a learned object. **The promised spectra do not need this module; the
  promised cost record may.** Under the 2026-09-04 inheritance ruling the learned prior can earn
  a licence to enter promised rungs". Mapping M08: M05 and M06 are "clearly labelled as not
  load-bearing for the promised spectra". Mapping §2: "Delete M05 or M06 and the **bonus**
  material stops". Proposal §12: the two modules are "kept off the promised path; the mapping
  says so rather than pretending otherwise".
- Goal "Notation": "**learned prior** = the Module-05 Transformer, a bonus." README glossary:
  "a bonus arm only."
The "spectra vs cost record" split that several of these sentences lean on is not available. On a
licensed rung there is one recovery: the prior-assisted one, at the K that the cost record
reports. The Δ₂ that enters that rung's scored spectrum is that recovery's Δ₂ — at R2–R3 the
prior-free check is a handful of direct blocks (issue 2), not a second full Δ₂. So if the licence
is ever used, a promised spectrum *does* depend on a learned object, and "no neural network on the
promised path" is false on that rung. The plan may decide that this is acceptable (the licence
says the prior-assisted Δ₂ agreed with the prior-free check) — but then M05/M08's labels, the
officer rule and the claim ladder must say so.
**Why it matters:** The document a grader reads for Module 07 specifies an agent that refuses what
the Goal permits; the document a grader reads for Module 08 labels as "not load-bearing" a
component the Goal calls load-bearing. A defence examiner who reads the Goal and then the mapping
finds the plan forbidding and permitting the same run.
**Status:** open

### 2. The licence's "prior-free reference check" at R2–R3 compares a handful of atom-pair blocks against a tolerance that is not an agreement tolerance; the mode-basis support the learned prior actually shapes is not among the compared quantities
**Where:** Ladder §3 licence bullet (ii) and Q8 bullet (a)–(b); Distilled Q8 and §3 "Structural
prior"; Mapping M05 "Why it is load-bearing"; Round-7 Pass B issue 6 (the origin of the
direct-block probe).
**What:** Licence (ii): "at that rung the reference check — Q7 at R0–R1, the direct-block Q8
check at R2–R3 — is computed prior-free and the prior-assisted recovery agrees with it within τ₇ /
ε₈." What the direct-block check contains, per Ladder §3 Q8(a): "at R2–R3 from the prior-free
direct-block probe (a deck-chosen set of atom pairs in the π system at near, mid and far
distances, each block measured by four-point finite differences …); the recovered Δ₂'s blocks are
printed beside them and a disagreement larger than ε₈ is a Q7-class breach." Pass B sized this
probe at "5 pairs ≈ 60 energies". What the learned prior does, per Distilled §3: it "replaces the
banded term by a Transformer-predicted support" — it decides which *mode-basis off-diagonals* are
free. Mapping M05 says the point of it is to "place explicit two-mode patterns where they matter".
Three things follow.
- Each 3×3 atom-pair block is one linear functional of the whole mode-basis Δ₂. Five pairs give at
  most 45 scalar constraints (fewer by symmetry) on M(M+1)/2 ≈ 5,000 unknowns at coronene. The
  support the prior predicts for mode pairs those functionals do not resolve is untested by the
  check. The held-out residual ρ cannot stand in: the held-out patterns come from the deck the
  prior helped design.
- ε₈ is defined (Ladder §3 Q8(a), item 12) as "a fraction ε₈ of Σ‖block‖²" — a locality share.
  "A disagreement larger than ε₈" between two 3×3 blocks has no unit, and "within τ₇ / ε₈" pairs
  a per-family RMS in cm⁻¹ (τ₇, item 11) with a dimensionless fraction. At R2–R3 τ₇ has no
  referent at all: there is no reference Δ₂ above R1 (Q7 is "at R0 and R1").
- Q8(b) is "computed with the direct far blocks substituted into the recovered Δ₂" — the far
  blocks are replaced, the near and mid blocks and everything else are the recovery's own.
So a prior-assisted recovery can pass licence (ii) at R2–R3 while the prior has shaped the
6.2/7.7 µm C–C block through mode pairs no direct block resolves. The plan closed Pass B issue 6
for the *structural* prior with this probe; re-using the same probe as the licence for a
*learned* prior that specifically edits the support is the brief's loophole, and it is open.
**Why it matters:** The licence is the only thing standing between "bonus arm" and "the
Transformer decided which Δ₂ elements exist in a promised spectrum". As written it is passable by
construction on the parts of Δ₂ that matter most.
**Status:** open

### 3. Mode E is "the guaranteed route", but the frozen-domain local-CC code it requires is a side-project deliverable — and the side project says its failure "costs the promised set nothing"
**Where:** Goal "Prime directive"; Ladder §3 "Frozen domains" bullet and §5 stop 1; Distilled §3
"Anchor level"; [Side_Project_2026-09-04_ModeG_Gradients.md](Side_Project_2026-09-04_ModeG_Gradients.md)
"Relation to the plan", §1.3, §2 (a), §3 kill criterion, §6, §8; README "Not yet done".
**What:** Goal: "The **guaranteed route is mode E**: K = 2M + K_off local-CC energies with frozen
domains". Ladder §3: "every local-CC probe evaluation … uses correlation domains, pair lists and
per-pair PNO counts frozen at the reference geometry. A code that cannot do this at the anchor
level is reported under stop condition 1 (as of 2026-09-03: ORCA documents it for DLPNO-MP2 only;
Psi4 documents no domain reuse)." So on the record no code freezes domains at the anchor level.
The side project then names the one that will: §1.3 "Psi4 cannot freeze domains; ORCA freezes
them for DLPNO-MP2 only. In PySCF/PySCFAD the fragment definitions and LNO vectors are Python
objects that can be stored … The same code therefore supplies mode E's frozen-domain energies
*and* mode G's gradients." §2 (a), first item **built**: "Frozen LNO spaces across displacements
in pyscf-forge's LNO-CCSD(T): store the fragment list … reuse the stored spaces." Distilled §3
has already adopted it: "**LNO-CCSD(T) in PySCF/PySCFAD is the preferred candidate** because it
is the one code in which domains can be frozen and gradients obtained (side project 2026-09-04)."
And yet: side project "Relation to the plan" — "every promise of plan 05 holds without this side
project"; §6 "What changes on failure — Nothing in the promised set"; Ladder §2 Bonus — "the
mode-G side project's success (its failure costs the promised set nothing)".
Both cannot be true. If the side project is killed before M1 passes (the kill criterion is on M3
within 12 weeks, so a project that never reaches M1 is killed too), the guaranteed route has no
frozen-domain code named anywhere in the set, and stop 1 fires at R0. M1 — "frozen LNO spaces
reproduce the reference energy" — is on the promised path, and the README already treats it so
("Side project milestone M1 … the first code of the project"). Distilled §3's "is the one code in
which domains can be frozen" states as a present fact what §2 (a) says will be built and §8 calls
"this plan's own reasoning … M1–M2 are the measurements that test it".
**Why it matters:** "Guaranteed" is the word the user's decision 5 turned on. A reader who takes
the side project's §6 at its word believes mode E survives any side-project outcome; the Ladder's
stop 1 says it does not. Either M1 is moved into the promised path (with its own bucket and a
stop-1 consequence if it fails), or another frozen-domain code is named for mode E.
**Status:** open

### 4. The side project's engine is described three different ways: hedged in its own §1.1 and in the bibliography, asserted as fact in the proposal, the Distilled plan, the budget, the change table and the method-debts list
**Where:** Side project §1.1, §1.2, §1.3, §2 (a), §8; bibliography items 33, 48, 49 and "Method
debts"; Proposal §5.3; Distilled §3 "Anchor level" and "Modes"; Budget §4 item 2; Why_05 row 24.
**What:** Distinguishing the classes the brief asked for:
- *Stated without support — "(T)" in pyscf-forge.* Item 48: "the entry names LNO-CCSD; whether
  the released code includes (T) is verified at side-project milestone M1." Item 49: the (T)
  variant is "at **snippet** level" — which the bibliography's own rule says is "*not* a cite".
  Asserted as available anyway: side project §2 (a) "in pyscf-forge's LNO-CCSD(T)"; §8
  "pyscf-forge LNO-CCSD(T): items 48–49"; Why_05 row 24 "builds frozen-domain LNO-CCSD(T)
  gradients in PySCFAD"; Distilled §3 "LNO-CCSD(T) in PySCF/PySCFAD"; Budget §4.2 "PySCFAD
  LNO-CCSD(T) — the last as extended by the side project"; Method debts "pyscf-forge's
  LNO-CCSD(T)". Only §1.1 carries the hedge.
- *Supported by a citation not yet verified for the thing claimed — the gradient code.* Side
  project §1.1 heading: "**The gradient exists in one open code.**" Proposal §5.3: "extends the
  open PySCFAD implementation of LNO-CCSD(T) gradients by automatic differentiation — demonstrated
  by its authors to about 29 atoms". Item 33 (arXiv abstract) supports that the *paper* reports
  such gradients; item 49 says "the README does not mention LNO-CC; where that code lives is
  verified at M1". "Exists in one open code" and "the open PySCFAD implementation" are claims about
  released code that the bibliography says is unlocated.
- *The plan's own reasoning presented as fact — §1.2.* Side project §8: "The frozen-domain
  argument of §1.2 is this plan's own reasoning, not a published result." Proposal §5.3: "Two
  facts make this a realistic engineering project rather than new theory: … on that surface the
  automatic-differentiation gradient with fixed spaces is the exact derivative, so the response
  terms that make general local-CC gradients hard do not arise; and the LNO fragment structure
  lets the memory of reverse-mode differentiation scale with the largest fragment rather than the
  molecule." The first "fact" is §1.2's reasoning; the second is side-project item (b), a thing to
  be built ("so that peak memory scales with the largest fragment"). The Goal, to its credit, does
  not repeat the exactness claim (it says only that the route "no production code offers today").
- *Stated without support — §1.3.* "the fragment definitions and LNO vectors are Python objects
  that can be stored at the reference geometry and reloaded at every probe geometry" — this is
  what M1 tests, not something anyone has checked.
**Why it matters:** The supervisor's proposal — the document most likely to be read outside this
folder — presents as "two facts" what the side project's own §8 calls reasoning and what the
bibliography calls unlocated code with a snippet-grade "(T)". The plan's rule for this is
"never cite from recall"; the side project is the first plan-05 object that breaks it in a frozen
document.
**Status:** open

### 5. Mode G cannot be licensed on a promised rung without amending the pilot note, which the deviation rule forbids; and the mode-G size sentence needs a "yes" at R3 that no probe is scheduled to print
**Where:** Ladder §4 opening and item 9; Budget §2 and §4 items 2, 5, 6; Distilled §4 second
bullet; Side project §3 ("What success means"), §5, "Relation to the plan"; Ladder §3 Q8(c);
Mapping §6.
**What:** The gradient-availability probe is a pilot-note input (Ladder §4: written after "(c) the
gradient-availability probe"; Budget §4 order: item 2 of the five pre-note steps). Its answer is
now defined by the side project: Budget §4.2 "The side project's M2/M3/M4 *are* this probe's
'yes' at R0/R1/R2." The note then freezes item 9: "K_cap(G) reads NOT_RUN for any rung where the
gradient-availability probe printed 'no'" — Budget §2 adds "and mode G is unavailable". After the
note, R0 responses are computed at once (Budget §4.6), and Distilled §4 forbids "Writing or
amending the pilot note after any local-CC Δ₂ response … exists." The side project nevertheless
writes: "M3 passed: mode G is licensed on R1 … On each rung where mode G is licensed, the pilot
note's K_cap(G) is filled from the dry run and the cost record carries `mode G`." Filling
K_cap(G) after the note is the forbidden amendment. Nothing orders the pilot note to wait for
M3: the side project has a 12-week checkpoint on its own clock, Mapping §6 says it "runs in
parallel with 02–03", and Budget §4 places the gradient probe before the smoothness probe with no
dependency on the side project's milestones. So either (a) the pilot note silently waits on the
side project (unstated, and it entangles the note with the 12-week clock), or (b) the note is
committed with K_cap(G) = NOT_RUN and mode G is unlicensable on R1–R3 by the plan's own rule,
whatever the side project achieves — in which case "if it succeeds, mode G becomes the primary
route on R1–R3 by dated note" (side project) is not available either, since a dated note cannot
touch a frozen pilot-note item after responses exist.
Separately: Ladder §3 Q8(c) allows the mode-G form "only if the gradient probe printed 'yes' at
all three rungs" (R1, R2, R3). The probe runs "at R0, then at naphthalene/cc-pVTZ, then at pyrene
if the machine allows" (Budget §4.2; probes README 3); M4 is pyrene; R3 is "classified by the rule
with the measured wall-clock" (side project §3) — classified, not probed. No step prints a "yes"
at coronene. The side project's "the size sentence becomes earnable" is therefore not earnable
as scheduled in the mode-G form.
**Why it matters:** Decision 5's whole content is that mode G is built *so that it can be used on
promised rungs*. The pre-registration machinery, as it stands, makes that use a deviation.
**Status:** open

### 6. The pilot note's input rule is breached by two of its own inputs: the R1 smoothness probe prints three diagonal Δ₂ elements, and the side project's M2/M3 print Δ₂ columns — all before ρ\*, K_cap, τ₇ and the margins are written
**Where:** Ladder §3 "Order of the pilot inputs" and §4 opening; Distilled Q6 noise line; probes
README item 5; Research note §8 (noise-floor paragraph); Round-7 Pass B issue 1; Side project §1.4,
§3 (M1, M2, M3); Budget §4.2.
**What:** Ladder §3: "No local-CC Δ₂ number exists when ρ\*, K_cap, the Q7 tolerance or the beat
margins are written; the smoothness probe is second differences along single modes, not a Δ₂
recovery, and its use is confined to item 13 and the amplitude rule." But the plan's own formula
(note §8, from Pass B issue 1) is: "For a diagonal Δ₂ element by central second differences at
dimensionless step q_s …" — the central second difference of ΔE along mode i *is* Δ₂,ii (Pass B:
"The diagonal Δ₂ element in mode E is the central second difference of ΔE(q)"). The probe runs on
"a C–C stretch, a C–H stretch, a CH-oop" (Distilled Q6) — one mode from each scored family — nine
points each, with and without frozen data. Its scatter is item 13's input; its *mean* is three
local-CC Δ₂ diagonal elements at R1 on the scored families, in hand when item 2 (margins, and the
expected-effect line "literature scale of Δ₂ at R1 is ≈ 5 cm⁻¹") and item 11 (τ₇, "no larger than
the smallest beat margin") are written. "Not a Δ₂ recovery" is true and beside the point; the
rule says "no local-CC Δ₂ *number*".
The second breach comes from issue 5's coupling: M2/M3 are the gradient probe's "yes", i.e. a
pilot-note input, and their pass condition is "AD gradient with frozen spaces vs central finite
differences of the frozen-space energy" — energies at displaced geometries, and gradients there. A
local-CC gradient at a geometry displaced along mode i is a column of the CC Hessian (side project
§5: "a gradient gives 3N responses per pattern"); with the DFT Hessian in hand, that is a column
of Δ₂ — every off-diagonal with mode i — at R0 (M2) and R1 (M3), before the note. Side project
§1.4 even says M3 will reuse "energies the R1 smoothness probe produces anyway".
And M1's pass condition — "second-difference scatter under the Q6 noise line at q_s = 0.5" — needs
τ, which is item 2/13 of the note; M1 is "the first code of the project" (README). The condition
cannot be printed when M1 runs.
**Why it matters:** Round-7 Pass A issues 2 and 21 were about exactly this ("the residual curve is
not a lab number, so choosing K from it is legal; it is also a curve against the very reference
Q7 will then be scored on"). The 2026-09-03 patch moved the smoothness probe *before* the note on
Pass B's advice and wrote a sentence saying it leaks nothing; it leaks the diagonal of the object
the note's tolerances are about to bound, and the side project adds columns. The fix is cheap
(print scatter only and seal means; run M2/M3 after the note, with the gradient probe reduced to
a run/no-run at the equilibrium geometry before it; or write the note before the smoothness probe
and accept a two-stage amplitude rule) — but it has to be written.
**Status:** open

### 7. "Beat" language on a mode-G rung has no noise gate: every Q6-noise consequence is scoped to mode E, and the side project's success condition is agreement with finite differences of the same energies
**Where:** Ladder §1 (last sentence of the cost-sentence bullet), §2 "Promised", §5.4; Distilled §4
"'Beat' language" bullet, Q6 row, P2 row; Side project §1.2, §3 (M1, M3, "What success means").
**What:** Ladder §1: "A rung where mode E's Q6 noise gate did not pass carries a cost record but no
'beat' language." Ladder §2: "'beat' language on a **mode-E** rung requires the Q6 noise gate to
have passed." Distilled §4: forbidden is "'Beat' language … on a **mode-E** rung whose Q6 noise gate
did not pass." Distilled P2: "mode-E rungs only where Q6-noise passed." And the escape hatch,
Ladder §5.4: "Q6-noise breach at a size class: mode E carries no 'beat' language there; the rung
continues as a cost record and, **if mode G or CPS exists, under that**." Q6's noise line is
defined on energies only ("second-difference scatter σ_E of frozen-domain ΔE"); there is no
gradient-noise line anywhere. The side project licenses mode G on R1 by M3: "AD gradient with
frozen spaces vs central finite differences of the frozen-space energy … max component deviation
≤ 10⁻⁵ E_h/bohr" — agreement with finite differences of the very energies whose second
differences Q6 just found too noisy. If the frozen-space surface is not smooth, its finite
differences are not smooth and the AD gradient — "the **exact** derivative of the surface being
probed" (§1.2) — agrees with them exactly. M3 passes; mode G is licensed; the rung's "beat"
sentence is ungated by noise. M1's one-mode benzene smoothness check at q_s = 0.5 is the only
smoothness anywhere in the licence, and (issue 6) its threshold does not exist when it runs.
**Why it matters:** The plan built Q6 with frozen formulas so that noise could stop a "beat"
claim (Pass B issue 1, the first blocking item). Decision 5 opened a route to the same claim on
the same surface that bypasses the gate. Exactness is not smoothness; the licence must require
the rung's Q6 noise verdict — or a mode-G analogue — regardless of mode.
**Status:** open

### 8. Between R3 and R6 nothing binding measures the fragment scheme: the R4 comparison is Bonus, the Goal says fragment use is decided by R2–R3 "and by nothing else", and the Distilled §8 R6 sentence fires per family where the Ladder withdraws per family
**Where:** Goal "The goal binds; methods are means" items 1 and 3; Ladder §2 R4 and R6 rows,
"Bonus" list, dated note on the R6 form; Ladder §3 Q8(a) (r_max); Distilled §4 last bullet, P5,
§8 R6 sentence.
**What:** Goal item 1: "Whether it is *used* at R4–R6 is decided by measurement — Q8(a/b) on
directly measured blocks at R2 and R3 for the scored families — **and by nothing else**." Ladder
R4: "**fragment probing exercised here first**, its certificate compared with whole-molecule
probing where the size still allows both"; Ladder §2 Bonus list: "the whole-molecule vs fragment
comparison at R4". Ladder R6: "**fragment-probed Δ₂ only** (decided 2026-09-04, licensed by Q8 at
R2–R3)". P5's evidence line: "the fragment-locality evidence from R2–R3 if fragments were used".
So the one place the fragment scheme could be tested against a whole-molecule Δ₂ (R4) is a bonus
with no pass condition, and by the Goal's own words an R4 disagreement is *not permitted* to
withdraw fragments ("and by nothing else"). Q8(a)'s r_max is bounded by the R3 molecule's own
diameter; the R6 flake's interior pairs lie at distances coronene cannot contain, and the note's
§5 sentence that its interior "looks like every other large flake's interior" is an assertion the
plan never measures. R6's certificate therefore rests entirely on a locality verdict for a
molecule smaller than the fragment.
The fail-closed sentence does not match the withdrawal rule either. Distilled §8: "R6 is not
reached: Q8 failed on direct blocks at R2–R3 for [families] / B3 did not exist". Ladder dated
note: "families that fail Q8 are withdrawn from the R6 certificate with their measured long-range
share." Goal item 3: "if it fails for all scored families, R6 is reported with the fail-closed
sentence of Distilled §8". As written the §8 sentence declares R6 not reached when *some*
families fail; the Ladder and Goal say R6 is reached minus those families.
**Why it matters:** Decision 1's justification is "decided by measurement". The measurement that
decides is taken at coronene and never repeated on the object it licenses; the one probe that
could catch a fragment scheme failing (R4 whole-vs-fragment) has been written out of the decision
by the directive's own wording. Make the R4 comparison binding where affordable (an ε₈-class pass
on fragment-vs-whole blocks), add a direct-block probe on the R6 fragments themselves, and change
"and by nothing else" to name those two. Fix the §8 sentence to "for all scored families".
**Status:** open

### 9. The Goal's prime directive writes the forbidden cost adjective again: "at O(1)-class probe counts" — the Round-7 Pass A issue 10 closure has regressed
**Where:** Goal "Prime directive" second paragraph and "Forbidden quotes"; Ladder §1; Side project
"Relation to the plan"; Proposal §5.3 (and §3, §5.3 last paragraph).
**What:** Goal, prime directive: "**The aimed-for route is mode G** — Δ₂ from analytic local-CC
gradients with frozen domains, **at O(1)-class probe counts**". Goal, forbidden quotes, the same
file: "**'Size-independent', 'O(1)', 'does not grow with the molecule', 'saturates', or any cost
adjective** — cost is reported as the printed record (Ladder §1) and … never as an adjective."
Ladder §1: "The adjectives 'size-independent', 'O(1)', 'saturates', 'does not grow' are forbidden
everywhere, including the Module 08 paper." Side project: "at O(1)-class probe counts". Round-7
Pass A issue 10 was that the Goal — "the file that wins on drift" — contained cost adjectives
Module 08 could quote; Pass B recorded the closure ("the Goal's second sentence is conditional on
mode G"). The 2026-09-04 rewrite of that paragraph put "O(1)" back, this time as the description
of the route the plan is *building toward*. The proposal says the adjectives "are forbidden
everywhere, including this proposal" (§5.3) and then asks "whether its off-diagonal part
saturates" three sentences later; §3's "saturates around a hundred" is a literature description
and is defensible, the §5.3 one is about this plan's quantity.
**Why it matters:** Module 08 will quote the prime directive as the project's stated aim. "-class"
does not turn an adjective into a measurement.
**Status:** open

### 10. The M05 corpus size is derived from an old-laptop timing, which the plan declares invalid for exactly this use
**Where:** Distilled §6 first bullet; Mapping §3 M05 "Dataset"; Budget §3 (last paragraph) and §5;
Goal decision 4.
**What:** Distilled §6: "B3LYP/6-31G\* Hessians recomputed on an **aromatic-heavy subset** (benzene
derivatives and conjugated rings over-represented; several thousand molecules; B2 work under the
168 h checkpoint — plan-02 provenance: 3.3 min per benzene Hessian on the old laptop)". Mapping
M05: "several thousand molecules, B2 work under the 168 h checkpoint". Budget §5: "A timing quoted
anywhere but a `probes/` script output is invalid." Budget §3: the plan-02 numbers "remain
provenance only … Every one is re-timed on the B2 laptop named in §1 before use (the plan-02
numbers come from an older machine)." Three thousand molecules at 3.3 min is 165 h: "several
thousand" *is* the old timing divided into the checkpoint, on a machine the set says is not the
B2 machine, for molecules that are not benzene. Goal decision 4 fixes the corpus as "an
aromatic-heavy subset" without a size — correctly; the two downstream documents supplied one from
the forbidden number.
**Why it matters:** This is the one 2026-09-04 decision whose frozen text contains a budget
figure, and its only support is a timing the plan's own rule voids. The size belongs in a dated
note after the B2 Hessian timing (the zero-CC dry run prints it), not in the Distilled plan.
**Status:** open

### 11. Sentences that still treat the six closed decisions as open, or describe the pre-decision promised set, survive in the proposal, the change table, the mapping, the budget, both glossaries and the research note's winning section
**Where:** Proposal §5.2 (R6 row), §9, §10 heading and list, §12; Why_05 rows 9, 16, 17, 18;
Goal "Open decisions" heading and list; plan-05 README "Reading order" items 11–12, "Green light"
paragraph, "Not yet done", glossary; Mapping "Status", §3 M05, M09, §4 table row 05; Budget §3
table (row "Gradients for a full Hessian"); Research note §8.
**What:** Quoted, so the sweep can be checked off:
- Proposal §5.2, R6 row: "fragment-probed only, **if the student decides fragments in**; otherwise
  a refusal" — vs §4 and §10.1 of the same file ("decided 4 September 2026").
- Proposal §9: "the re-worded promised set — … the largest species dependent on the fragment
  decision — … **Whether to adopt that re-worded set is the student's decision (§10)**, and this
  proposal is written for it." — vs §10.4 ("decided … in two parts").
- Proposal §10 is still headed "Decisions the student has **not yet** made", lists five (all
  struck), and omits decision 6 (the machine), which the README lists.
- Proposal §12: "the first of them is one of the decisions in §10" (M05, decided).
- Why_05 row 16: "the target itself is **open decision 4**". Row 18: "mode G is **a bonus** on the
  verified 2026-09-03 gradient landscape". Row 9: "mode E is the promised route" (the Goal now
  says "guaranteed", with mode G "aimed-for"). Row 17: "DFT Hessians on GPU where the deck names
  one" — Budget §1, after decision 6: "**every GPU DFT Hessian is B3** (rented)". Row 10 still
  reads "B2 = the machine the student owns" without the named laptop.
- Goal: the heading "Open decisions for the user (not part of the promised set until decided)"
  lists decisions 1–4 only. Decisions 5 (the promised set; mode E guaranteed / mode G built) and 6
  (the machine) are absent from the file that "wins on drift"; the README lists six, the proposal
  five, the mapping three.
- README reading-order item 11: "M05's rule-0 escalation is **open decision 4**"; item 12: "the
  decisions the student has **not yet made**"; "Green light": "whether that re-worded set is
  adopted is the **user's decision**, together with **open decisions 1, 3 and 4** below"; "Not yet
  done": "the **five** decisions of 2026-09-04" (six are listed twenty lines above); glossary:
  "mode G = … (a bonus on the 2026-09-03 landscape)", "learned prior = … a bonus arm only".
- Mapping "Status": written "for the **Pass-B re-worded promised set** (Δ₂ only; mode E primary;
  R6 **per open decision 1**)"; §4 row 05: "distinct per reading 1 (**proposed; user to confirm
  under open decision 4**)"; M05: "**If the user will not accept it**, M05 is a demonstration and
  the report defends it as one"; M09: "why mode E is the promised route on the 2026-09-03 gradient
  landscape" (the defence now has a side project to explain).
- Budget §3: "K(G) per rung — NOT_RUN; **mode G is a bonus** on the 2026-09-03 landscape".
- Research note §8 — the section the file says "wins" and "the frozen documents follow": "**Mode E
  is the promised route; mode G is a bonus.**"; "the user **may veto** a DFT–DFT target (**open
  decision 4**)"; "the user's **open decision 1** is made before the pilot note". There is no
  2026-09-04 addendum. A reader who follows the README's reading order (item 4, before the Ladder)
  gets the 2026-09-03 state as the winning text.
**Why it matters:** This is the brief's "decided vs open" class, and every one of these is in a
sentence a supervisor or grader reads for orientation. The proposal in particular still asks the
supervisor (§13.2) about decisions it elsewhere says are made, and its ladder table promises R6 on
a condition that no longer exists.
**Status:** open

---

## Non-blocking findings

### 12. Navigation-grade stale text after the 2026-09-04 edits
**Where:** root [README.md](../../../README.md) banner and table; [plans/README.md](../../README.md)
banner, prose, table, "Layout", "Version 05"; plan-05 README status line, reading order; Goal
"Status"; Ladder §5 stop 1 and §2 "Ordering"; probes README item 8; Why_05 "Status"; Rubrics/README
"What is not here".
**What:** Root README: "Plan 04's folder stays in the tree until the user decides on its removal"
(decision 2 closed the same day the banner above it was written); table row 04 "kept in the tree
pending the user's removal decision"; row 05 "**Round-7 reviews not yet run**" (twice in the set:
also plans/README row 05, "Layout" — "Round-7 review record (not yet run)", "Round 7 not yet run",
"Plan 05's completeness waits on its Round-7 reviews", "its Round-7 reviews have not run",
"Plan 04 … is **not yet removed**: its folder stays until the user decides"). The root README's
table has rows for 03–05 only under a banner that says five plan folders are in the tree.
Plan-05 README: "whose folder stays in the tree until the user decides to remove it"; reading
order item 2 "(23 rows)" (there are 24); item 9 "(items 23–47 new)" (23–49). Goal "Status": "kept
in the tree until the user removes plan 04". Ladder stop 1: "or the **new laptop** underperforms";
probes README item 8: "canonical feasibility on the **new machine**" — decision 6 says B2 is the
current laptop and the commit that swept "new machine" missed these two. Goal "Size" bullet:
"(decided 2026-09-04; **recorded in** the pilot note)" and Ladder "Ordering": "**is recorded in**
the pilot note" — present tense for a note that does not exist (Ladder §4 and Budget §4.5 have
the correct future form). Why_05's status line records the 2026-09-03 revisions and none of the
2026-09-04 ones although rows 5, 19, 24 and the "does not change" paragraph were edited that day.
Rubrics/README: "Plan 03 kept them in its `GoalGathering/Horizon/` (git history since 2026-09-02)"
— the folder is back in the tree.
**Why it matters:** None changes a decision; recorded so one sweep catches them all.
**Status:** open

### 13. The change table misses three 2026-09-04 changes of frozen intent and carries four stale rows
**Where:** Why_05 table rows 9, 10, 16, 17, 18, 24; Distilled §3 "Anchor level"; Budget §1.
**What:** Not in the table: (a) the anchor-code preference — plan 04 said ORCA/DLPNO; Distilled
§3 now says "LNO-CCSD(T) in PySCF/PySCFAD is the preferred candidate" (row 12 records the stop-1
change, not the code change); (b) "every GPU DFT Hessian is B3 (rented)" and the CPU path as the
B2 default (Budget §1) — row 17 says the opposite; (c) the prime directive's third rewrite (mode E
guaranteed, mode G aimed-for and built) — row 9 still says "mode E is the promised route". Stale
rows 16 and 18 are quoted in issue 11. Row 24 sits above row 23; harmless, but the README calls
the table "23 rows".
**Why it matters:** Why_05's job is to let a reader separate inheritance from drift; the
2026-09-04 drift is half-recorded.
**Status:** open

### 14. The two debt lists are identical again (good) and both stale on item 5; the method-debts list contradicts the bibliography on item 30 and omits item 46
**Where:** Frozen_Lines §7 item 5; bibliography "Named debts" item 5, "Method debts", items 30, 32,
33, 34, 44, 46; Goal "What is scored"; Distilled §3 "Intensities"; note §8.
**What:** Debt 5 in both lists: "items 17, 32, 33, 34; Sylvetsky pinned; the rest unpaid." The
status column says items 32, 33 and 34 are **OK** (manual page; arXiv abstract; Crossref) — only 17
is NOT FETCHED. Method debts: "Full texts of items 27, 28, 30, 37 **before any number from them is
quoted anywhere**" — item 30's numbers ("~1 μE_h, largest 6.09 μE_h", "fixing the per-pair PNO
dimensions did **not** remove them") are quoted in the bibliography row itself (status "OK …
Crossref + PMC full text"), in note §8 ("full text now read"), in the Goal ("item 30, full
text") and in Distilled §3 ("bib 30, full text"). Either the debt is paid and should leave the
list, or the numbers are quoted against the rule. Item 46 (mode-tracking, "content at snippet
level") is named prior art in Why_05 row 20 and the Distilled §2 neighbour table and has no
debt line; items 42–43 got an "re-read by the author, not only by the Pass B reviewer" debt,
item 44 (quoted from the same reviewer's reading) did not.
**Why it matters:** Small; Round-7 Pass A issue 14 was the same shape and the "identical" claim
now holds, which is progress — the content behind it drifted instead.
**Status:** open

### 15. The item-45 "~5 cm⁻¹" figure travels without its snippet label in two places; one "certainly affordable"
**Where:** Mapping §3 M04 "Contribution"; Proposal §11.4 and §8; Ladder §4 item 2 and Goal "Known
risks" (correct).
**What:** Ladder item 2 has it right: "(item 45, snippet, verify-on-use)"; so does the Goal:
"(item 45, snippet; a P2 outcome)". Mapping M04: "it absorbs the *mean* of a ~5 cm⁻¹ harmonic
CC−DFT difference per family" — attributed to "Round-7 Pass B issue 7 says out loud", no grade.
Proposal §11.4: "the opponents' fitted scale factors already absorb the mean of a ~5 cm⁻¹
harmonic difference" — no grade. Proposal §8: benzene is "the only rung where a canonical
coupled-cluster Hessian is **certainly** affordable" — the only datum is plan-02's 19.6 s/point at
6-31G\* on the old machine, which the budget labels provenance.
**Why it matters:** The proposal is the document that leaves the folder.
**Status:** open

### 16. The side project's kill clock can be kept from running by booking, and "12 weeks of hours" has no conversion
**Where:** Side project §3 (kill criterion), §4; Budget §1 B1 row.
**What:** "The side project stops … if **M3 is not reached within 12 weeks of B1 hours logged to its
bucket**". Human hours are uncapped with no hours-per-week anywhere, so "12 weeks of hours" is
either calendar time (then say "12 weeks from the date of this note") or an effort figure with no
definition. The booking rule ("one bucket per entry") stops double-counting, not attribution: by
the side project's own §1.3 its item (a), frozen LNO spaces, "supplies mode E's frozen-domain
energies" — legitimately main-project infrastructure (issue 3) — and item (c), the probe interface,
is pipeline plumbing. Both can be booked outside the bucket in good faith, and the M3 clock never
starts. The alarm ("If its bucket exceeds the sum of the M02–M04 buckets at any **monthly
review**") refers to a monthly review defined nowhere else in the set.
**Why it matters:** The proposal's risk 6 says the side project is "the failure mode that ended
plan 01" and points at this clock as the mitigation.
**Status:** open

### 17. Whether Q8 is read at R0 is said three ways
**Where:** Ladder §3 Q8 bullet; Ladder §2 R0 row and "Ordering"; Distilled Q8 pass column and Q7
(iv).
**What:** Ladder §3: "at R0–R1 the blocks come from the reference Hessian"; Distilled Q8: "on the
reference Hessian at R0–R1" but its pass column: "(a), (b) per rung **R1–R3**"; Ladder
"Ordering": "Q8(a/b) must be printed at **R1** (on the reference), R2 and R3"; the R0 licence cell
lists no Q8; Q7 (iv) runs "Q8(a/b) computed on the reference Δ₂ and on the recovered Δ₂ side by
side" at R0 and R1. If R0's Q8 is a Q7 sub-item and not a rung read, say so once.
**Why it matters:** Number drift only; Q0–Q8 numbering itself is consistent.
**Status:** open

### 18. The Distilled claim and question are written for mode E alone
**Where:** Distilled §1, §2 question; Mapping M09.
**What:** Distilled §1: "recovered from K local-CC energies (mode E) with frozen correlation
domains"; §2: "how many coupled-cluster energies did that correction need, per rung, in its
off-diagonal part?" After decision 5 a licensed rung runs mode G and its cost record reports K,
not K_off (Goal "Cost" question covers both). Not a contradiction — the Goal wins — but the
sentence a grader reads first names the guaranteed route as if it were the only one.
**Why it matters:** Cosmetic today; load-bearing the day a rung is licensed.
**Status:** open

### 19. Definitions before first use, and the glossary against the brief's list
**Where:** plan-05 README "Glossary"; Goal (scope boundaries, "The goal binds" §2, Reach question,
decision 4, method skeleton, known risks); Why_05 rows 5, 7, 10; Mapping throughout; Side project
§3, §7; Ladder §2 (two dated notes).
**What:** The README glossary lacks: ρ/ρ\*, τ₇/d₇, r_c/r_max/ε₈/γ, f_h, CMA-0/CMA-2 (CMA is
there), M1–M4, B1/B2/B3, Q0–Q8, P0–P5, reading 1/2, "the licence", "the dated note" — and its
mode-G and learned-prior lines are stale (issue 11). In the Goal a cold reader meets τ₇ / ε₈
("within τ₇ / ε₈", scope boundaries), r_max ("The goal binds" §2), B3 (Reach question), P2/P3/P4,
Q6–Q8, CMA-0 / CMA-2 (method skeleton, known risks) and "reading 1, reading-2 fallback"
(decision 4) without definition; the Goal is reading-order item 3 and the file that defines
notation for the others. Why_05 uses d₇ (row 7), P3 (row 5) and B2/B3 (row 10) undefined. The
mapping uses ρ, ρ\*, K_off, P2/P3/P5, Q3/Q4 without definition and defines reading 2 ("any corpus
containing data computed for another module is reuse") but never states reading 1 positively —
it is inherited by pointer to plan 04's mapping. The side project uses q_s, "the Q6 noise line",
B1–B3 and K_cap(G) by reference only. "The dated note" is ambiguous: Ladder §2 now has two (R2
re-read; R6 form) and Frozen_Lines §5's "dated note there" means the first. The proposal is
self-contained and passes.
**Why it matters:** The defence audience reads the Goal before the Ladder and the mapping before
the Distilled plan.
**Status:** open

### 20. The rubric folder carries a classroom transcript in which the student names QM9 as the Foundations-project dataset; the mapping's M02 and M05 rows do not address it
**Where:** `Rubrics/02_AI_Programming_Foundations_Project.md` (Marvin transcript, lines ~837–870 and
again ~1099–1132) and the same transcript embedded in `Rubrics/05_Deep_Learning_Systems.md`
(lines ~804–866); Mapping §3 M02, M05 "Distinctness", §4 table.
**What:** The scraped page contains the student's own words: "Okay, I will use another dataset,
QM9, for the Foundations Project." and the account's repository list shows
`ai-programming-foundations-project`. Mapping M02 assigns module 02 the PAHdb v4.00 atlas; Mapping
M05 argues "Hessian QM9 is public today and **belongs to no earlier module**" and offers reading 2
("any corpus containing data computed for another module is reuse") as the fallback. Nothing in
the set says whether module 02 has already been submitted and with what. If it was submitted on
QM9, the M02 row is a record rather than a plan, rule 0's "atlas" contribution moves, and M05's
reading-2 exposure includes the parent set of Hessian QM9. (Observed content, treated as data: I
am reporting what the file says, not acting on it.)
**Why it matters:** One sentence in the mapping — "module 02 [has / has not] been submitted; if
so, on dataset X" — settles it before Pass 6.
**Status:** open

---

## What passed

- **Round-7 Pass A closures that survived the 2026-09-04 edits:** K as a measurement with ρ\*
  and K_cap in separate bins (Ladder §3, §4.8–9; Budget §2; Q0) — no sentence anywhere writes K
  before it is measured; Q8's fixed three-part form with item 12, the direct-block probe and the
  NOT_RUN rule for mixed modes (issue 20); the two cost-sentence forms defined once (Ladder §1)
  and obeyed by every cost record sentence I could find outside the Goal's regression (issue 9);
  Δ₃/Δ₄ out of the promised set and out of Q7 in Goal, Ladder, Distilled, Why_05 rows 1/3, with
  the side project reopening it only "by a further dated note"; the R2 re-read consistent across
  Ladder §2 (row and note), Frozen_Lines §5, probes README, Mapping M03/§5, Proposal §5.2; P4(a)
  attributed to DFT-level anharmonicity with P4(b)/(c) consequence sentences identical in §7 and
  §8; MD-ACF's object defined and deck-gated; hold-out membership seeded and ρ defined
  dimensionlessly; Q7's "tests the recovery, not the freezing" sentence present in Q7 and probes
  README 8; the motivational assertions of issue 15 now hedged ("whose affordability no plan has
  measured").
- **Round-7 Pass B closures that survived:** Q6 with three frozen formulas and pilot-note item 13,
  the amplitude taken *from* the step grid; the banded structural prior with the high-exchange
  dry-run pair stated identically in Ladder §3, Distilled §3 and Budget §4.1; CMA cited as prior
  art in Goal, Why_05, Distilled §2, Frozen_Lines §1 and the forbidden-quotes list; the anthracene
  probe as a dated bonus with the same energy count (≈133) in note §8, Budget §4.8, probes README
  9 and Proposal §8; R6 DFT Hessian as B3 in Goal step 1, Budget §3, Distilled §3 and Proposal §8;
  B97-1 for Mulas in Frozen_Lines §3 and item 6.
- **Fragment-probing "either branch" wording is gone from the frozen documents.** The only
  survivors are the research note's §5 (deliberately left as written) and the proposal's §5.2 row
  (issue 11). The Goal, Ladder, Distilled §1/§4/P5, Mapping M02/M07/M08 and Why_05 row 19 all say
  the same thing: fragment-probed R6, conditional on Q8 at R2–R3 and B3, whole-molecule not
  promised. No "never on a promised rung" for the learned prior survives in the Goal or Ladder;
  the survivors are the ones listed in issue 1.
- **Number drift checked and clean:** pilot-note items 1–13 are cited by the same numbers in
  Ladder §3/§4, Distilled §3/§5/Q0/Q6/Q7, Budget §2/§4, probes README 1 and 5, Mapping M03/M04
  (items 8, 9, 13 for the dry run; 13 for the amplitude; 7 for resonance; 5 for P3; 4 for the
  matrix tolerance; 6 for the M04 recipe; 11 and 12 for τ₇/d₇ and the Q8 numbers). Q0–Q8 and
  P0–P5 are used consistently. Bibliography numbers cited in text (23, 24, 30, 33, 42–49; also 7,
  13, 14, 21, 22, 25–28, 31–32, 34, 44–47) all point at the right rows. The 168 h machine
  checkpoint and the 12-week side-project checkpoint are never confused: B1 vs B2, hours vs
  wall-clock, in Budget §1, Side project §4 and Proposal §8/§11.
- **The laptop is one machine everywhere.** 32 GB DDR5 (Budget §1, README decision 6), 28 GB
  peak-memory cap for M3 and "a 32 GB laptop" in the side project, "8-core Ryzen 7 260 …
  no CUDA-class GPU" in Goal and Proposal §8. No "16 or 32" remains. GPU Hessians are B3 in Budget
  §1/§3 and README decision 6 (Why_05 row 17 is the one stale place, issue 13).
- **Timings stay out of the budget slots** except for issue 10: Budget §3 keeps every literature
  figure in a column labelled "not this project's" with NOT_RUN in the plan-05 slot; the plan-02
  figures are labelled provenance; the side project quotes no timing.
- **Hours uncapped, UvA a collaboration:** Goal "Hours", Budget B1, Ladder stop 2, Side project §4
  ("not a cap on the project"), Proposal §8 — consistent; B3 has "no number until three things
  exist in writing" in Budget §1 and Ladder stop 3 and Proposal §8.
- **Frozen_Lines is unchanged in substance** and its §7 list is now character-identical to the
  bibliography's "Named debts" (issue 14 is about the content of item 5, not the sync).
- **The bibliography's status vocabulary is honest where it is vocabulary:** items 48–49 are
  labelled with exactly the hedges the side project's §1.1 repeats; the failure (issue 4) is in
  the documents that re-quote them.
- **The M05 decision is stated consistently in the four places that define it** (Goal decision 4,
  README decision 4, Distilled §6, Mapping M05): support of Δ₂; Hessian QM9 plus recomputed B3LYP
  on an aromatic-heavy subset; PAH tensors held-out test only; success = the P3 saving and the
  licence; reading 1 with an executable reading-2 fallback. The seams are in the sentences around
  it (issues 1, 10, 11), not in the decision text.
- **The side project's milestone-to-rung map is consistent** across Side project §3, Ladder §1,
  Distilled §3 "Modes" and Budget §4.2 (M3 → R1, M4 → R2); the gap is R3 (issue 5).

---

## Round 8, Pass A — issue index

| # | Class | Blocking? |
|---|---|---|
| 1 | Contradiction (learned prior: licence vs officer rule, claim ladder, M08 labels, glossaries) | yes |
| 2 | Loophole (licence reference check at R2–R3: compared object, tolerance units, τ₇ referent) | yes |
| 3 | Contradiction (mode E "guaranteed" depends on side-project M1; "failure costs nothing") | yes |
| 4 | Unsupported (side-project engine: "(T)" snippet-grade; gradient code unlocated; §1.2 reasoning as "fact") | yes |
| 5 | Contradiction + number gap (K_cap(G) NOT_RUN vs licensing after the note; no R3 "yes") | yes |
| 6 | Loophole (pilot-note inputs leak Δ₂ diagonals and columns; M1 threshold does not exist yet) | yes |
| 7 | Loophole (mode-G "beat" has no noise gate) | yes |
| 8 | Loophole + contradiction (fragment scheme never measured R4–R6; "by nothing else"; §8 R6 sentence) | yes |
| 9 | Regression (Goal writes "O(1)-class"; Round-7 A-10 reopened) | yes |
| 10 | Unsupported / rule breach (M05 corpus sized from an old-laptop timing) | yes |
| 11 | Decided vs open survivors that alter the promised set (proposal, change table, mapping, budget, note §8) | yes |
| 12 | Stale navigation text | no |
| 13 | Change table incomplete for 2026-09-04 | no |
| 14 | Debt lists: item 5 stale; item 30 debt vs quoted numbers; item 46 missing | no |
| 15 | Snippet label missing on "~5 cm⁻¹" in mapping and proposal; "certainly affordable" | no |
| 16 | Loophole (side-project kill clock: booking and "12 weeks of hours") | no |
| 17 | Number drift (Q8 at R0) | no |
| 18 | Mode-E-only wording in Distilled §1/§2 | no |
| 19 | Unreadable without the author (definitions; glossary) | no |
| 20 | Rubric transcript names QM9 as the module-02 dataset; mapping silent | no |

Do not treat this file as Pass B. Whether a frozen-space AD gradient is smooth where the energy
is not, whether five direct blocks can constrain a learned support, and whether coronene's r_max
says anything about a 432-atom interior are domain questions for the Round-8 Pass B, after these
patches or after an explicit decision to proceed with issues still open.
