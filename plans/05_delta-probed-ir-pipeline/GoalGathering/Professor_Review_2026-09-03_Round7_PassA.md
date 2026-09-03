# Professor review — Round 7, Pass A (cold read)

**Date.** 2026-09-03.
**Scope.** Plan 05 document set as it stands in this workspace, read in the brief's order: the two
status READMEs, the plan-05 README, `Why_05_Supersedes_04.md`, `Overarching_Goal.md`, the
research note, `Frozen_Lines_to_Beat.md` (diffed against plan 04's), `Frozen_Ladder_and_Tolerances.md`,
`Compute_Budget_2026-09-03.md`, `Distilled_Project_Plan_and_Quality_Checks.md`,
`Relevant_Scientific_Papers.md`, `probes/README.md`, plan 04's Goal / Ladder / Distilled / both
Round-6 reviews, and `Rubrics/README.md`. No GitHub fetch, no web search, no literature judgment.
Plans 01–03 not fetched from history. Pass B is not in this file. Where I say "plan 04 says", I
read the plan-04 file in this tree, not the Round-6 review's paraphrase of it.

**Verdict:** No — not internally sound enough to proceed to Pass B until the blocking findings are
patched. The governance plan 04 earned is carried, and the honesty labels on literature figures
are mostly used well. But the one new object — K — is defined two incompatible ways across the
set (a number frozen in the pilot note, and a number measured per rung), the plan's *default*
recovery mode contradicts the prime directive's new second sentence by arithmetic the plan
itself writes down, the saturation criterion that would decide the whole bet has no fixed form,
and two gates (the learned-prior rule, the Δ₃/Δ₄ licence) have doors the text leaves open. The
"one thing changed" claim is also not what the diff shows.

---

## Blocking findings

### 1. The change list is not the change: Why_05 says the ladder, its claim types and the budgets are unchanged; the ladder adds a claim type and a promised item, the budget adds a currency, and the prime directive gains a sentence
**Where:** [Why_05_Supersedes_04.md](Why_05_Supersedes_04.md) "What plan 05 changes" / "What plan 05
does not change"; [Frozen_Ladder_and_Tolerances.md](Frozen_Ladder_and_Tolerances.md) §1, §2
"Promised", §3, §4, §5.1; [Compute_Budget_2026-09-03.md](Compute_Budget_2026-09-03.md) §1;
[Overarching_Goal.md](Overarching_Goal.md) "Prime directive";
[Distilled_Project_Plan_and_Quality_Checks.md](Distilled_Project_Plan_and_Quality_Checks.md) §1, P4(a).
**What:** Why_05 lists four "changes of *frozen intent*", "each recorded here so Pass A cannot
mistake them for drift", and then: "**What plan 05 does not change.** The ladder, its rungs and
its claim types; the opponents; the scoreboards; the tolerances; the three budgets and the hours
directive; the module skeleton 02–09; the no-transfer rule as plan 04 wrote it." Against that:
- Ladder §1 (plan 04 had two claim types): "**[05] Cost claims are a third kind of sentence**,
  allowed on any rung". Ladder §2: "**[05]** In addition, the promised set includes the **cost
  record**: K, mode and wall-clock per probe at every rung that ran, in one table." The claim
  types and the promised set changed.
- Budget §1: B2 is now "wall-clock hours on hardware the student owns (laptop; a GPU workstation
  if one is bought)" and B3 is "cluster node-hours **and rented GPU-hours**" with "a money cap
  where an allocation would stand". Plan 04's budget: B2 "laptop", B3 "cluster node-hours". A
  purchased workstation enters B2 with no precondition while rented time carries three. The
  budgets changed in kind, and the file's own heading "Three budgets, unchanged in kind" is not
  true of its table.
- Ladder §4 gains items 9 (r_c **and the Q8 decay criterion**), 10 (Q7 tolerance), 11 (f_h) and
  redefines item 5; Why_05 (iv) says only "the pilot note gains K and r_c and loses N_min".
- Ladder §3 resolution-floor controls changed from plan 04's "(test RMSE, DLPNO-threshold
  sensitivity)" to "(recovery residual, local-CC noise floor, threshold sensitivity)" —
  "tolerances" are claimed unchanged.
- Stop 1 changed from plan 04's "ORCA/DLPNO unavailable" to "Local-CC code unavailable at the
  anchor level, **or unable to freeze domains**" — a new stop trigger, not in the list.
- P4(a)'s null arm changed from plan 04's "Δ=0 (harmonic-only)" to "Δ = 0 (DFT harmonic + DFT
  anharmonic, no CC correction)" — a different null (see issue 9), not in the list.
- Goal: "**And do it at a coupled-cluster cost that does not grow with the molecule.** That second
  sentence is what plan 05 adds." Why_05: "One thing: **where the coupled-cluster budget is spent
  and how it is collected.**" README and both status banners: "the same criterion". A prime
  directive with a new sentence and a Distilled §1 claim that now ends "**together with the probe
  count K(R6) printed next to K(R3)**" is not the same criterion with a new method.
**Why it matters:** The document whose job is to let a reader separate inheritance from drift
undercounts the drift. A defence examiner who takes Why_05 at its word will be told "same ladder,
same budgets" and then find a third claim type, a new promised item and a new currency. Every
one of these may be a good change; none of them is recorded where the plan says all of them are.
**Status:** open

### 2. K is frozen in the pilot note *and* measured per rung; the residual that would reconcile the two is in no bin; and the note's own timing rule cannot supply the R1 data items 8–9 require
**Where:** Ladder §2 (R3 row, "Ordering"), §4 (opening, items 8–9), §5.2; Compute_Budget §2, §4.1;
Distilled Q0, Q7, Q8; [probes/README.md](../probes/README.md) items 1 and 4; plan-05 README
"Promised deliverable" and "Not yet done"; root README banner.
**What:** Two definitions of K coexist.
- *K is frozen before the rung runs.* Ladder §4.8: "**[05] K per rung and per mode** (E and G):
  the probe count at which the recovery is declared converged, with its justification (held-out
  residual curve from R0–R1), so the B2/B3 **classification rule** … is arithmetic." Budget §2:
  "With K for the rung frozen in the pilot note (Ladder §4.8) … `wall_clock_per_probe × K_rung`";
  "K may not be lowered to pass it (Ladder stop 2)". Stop 2: "shrinking K below the frozen value".
  Distilled §4: "lowering K below the frozen value" is a deviation.
- *K is measured by running the rung.* Ladder R3 row: "**the saturation test**: K(R3) vs K(R2) vs
  K(R1) printed side by side." Q8: "K(R1), K(R2), K(R3) side by side **at the frozen residual**."
  Plan-05 README: "a number of local-CC evaluations K that the plan **measures rung by rung**."
  Root README: "probe count **measured per rung**". probes/README item 1: "print K needed to
  reach a declared held-out residual" — K is an output there.
If K(R2) is a number written into the pilot note before R2 runs, "K(R2) measured" is not a
measurement and the saturation test compares three numbers the author chose. If K is the count
at which a frozen residual is reached, then the thing that must be frozen is the **residual
target** — and no §4 item freezes it: item 8 says "declared converged" without saying what
convergence is; Q0's deck lists "K, f_h, r_c", not a residual; Budget §4.1 and probes item 1 say
"a declared residual" without saying where it is declared. The number that defines K has no bin.

The timing does not close either. Ladder §4 opening: numbers are "Written into a dated pilot note
after (a) the **R0 pilot** … and (b) the **scoreboard re-read probe**." README "Not yet done":
"The pilot note (after the R0 pilot, the zero-CC dry run, the Q7 reference and the scoreboard
re-read …)". Yet item 8's justification is the "held-out residual curve from **R0–R1**" and item 9
takes r_c "from the **R1 read**". Either the note is written after R1's probes (then §4's stated
trigger is wrong and the note is written with R1's recovered-vs-reference curve in hand), or it is
written after R0 (then items 8–9 cannot contain what they say they contain). And in both readings
Q7 at R0 — "recovered Δ₂ (uninformed prior, **frozen K**) vs a directly computed reference Δ₂" —
is evaluated at a K chosen after the R0 probe batch and the R0 reference (probes item 4: "then
the R0 probe batch … and the **Q7 reference**") already exist. That is the brief's loophole 2:
the residual curve is not a lab number, so choosing K from it is legal; it is also a curve
against the very reference Q7 will then be scored on.
**Why it matters:** K is the entire content of plan 05 ("if it does not saturate, the size claim
is withdrawn"). A quantity that is simultaneously an input to a rule and the output of a test can
be made to pass either by picking the bin that suits the moment. The classification rule and the
saturation test need *different* frozen objects (a K cap; a residual target) and the text
provides one word for both.
**Status:** open

### 3. Q8's saturation criterion has no fixed form: "does not grow faster than the pilot-note criterion" names a pilot-note item that does not exist
**Where:** Distilled Q8 pass column; Ladder §4.9; Goal "The scientific question — Reach";
Ladder R6 row; Distilled §1 and §9.7; Ladder §5.4; Goal "Forbidden quotes".
**What:** Q8 passes if "decay printed; **K does not grow faster than the pilot-note criterion**".
The only pilot-note item about Q8 is §4.9: "r_c, the locality length, and the **Q8 decay
criterion** (the functional form and threshold **below which a Δ₂ element is treated as zero**)"
— a per-element locality threshold, not a rule for how K may grow with size. Elsewhere the same
test is worded four other ways: Goal — "at a probe count measured to be **of the same order** as
at R3"; Ladder R6 — "**K(R6) reported against K(R3)** in the same sentence as the spectrum"
(reported, no threshold); Distilled §1 / §9.7 — "printed next to K(R3)" / "at K(R6) probes against
K(R3)" (printed, no threshold); Stop 4 — "K not saturating between R1, R2 and R3" (undefined);
Goal forbidden quote — allowed once "K printed at **≥ 2 rungs** of different size" (two rungs,
against Q8's three). "Same order" is undefined (factor 3? 10?).
**Why it matters:** This is the brief's loophole 8 and it is open: the growth criterion can be
written after K(R1), K(R2), K(R3) are known — and, per issue 4, a "K/M stays constant" criterion
would make the plan's default mode pass by construction. The bet the plan says it will lose
honestly has no pre-registered losing condition.
**Status:** open

### 4. The plan's default recovery mode contradicts the prime directive's new sentence by the plan's own arithmetic, and nothing says the cost claim is conditional on mode G
**Where:** Goal "Prime directive", "Method skeleton" step 2 and "Known risks";
[Research_Note_2026-09-03_Delta_Probing.md](Research_Note_2026-09-03_Delta_Probing.md) §1, §4.1;
Distilled §3 "Δ-probing"; Compute_Budget §3 table; Ladder §2 "Promised"; bibliography items 31–32.
**What:** Goal: "**And do it at a coupled-cluster cost that does not grow with the molecule.**"
Research note §4.1: "Until a timed probe shows a working gradient at the rung's size, the plan's
default is **energy-only recovery** … (K ≈ 2M for the diagonal Δ₂ plus a frozen number of
multi-mode probes for the off-diagonal part; M = number of modes)." Distilled §3: "**Modes:** E
(energies only; K ≈ 2M + K_off) or G (gradients; K expected O(1))". Budget §3: "Energy-only
diagonal Δ₂ in the DFT mode basis | arithmetic: 2M points". Research note §1 gives M: "coronene
102, C₃₈₄H₄₈-class ≈ 1,290". So in the default mode K(R6)/K(R3) ≥ 1,290/102 ≈ 12.6 before K_off —
not "the same order" (Goal, Reach) by any reading, and a cost that grows linearly with the
molecule. The Goal's own "Known risks" admits the mechanism ("mode E's probe count is 2M-plus
rather than O(1)") but the prime directive above it is unqualified, and the gradient the O(1)
route needs is, per the plan's own verification, not on offer: Research note §4.1 "**no analytic
DLPNO-CCSD(T) gradient is advertised**"; bib 32 (Psi4) "gradients not mentioned". No sentence in
Goal, Ladder or Distilled says: the second sentence of the prime directive, the saturation bet,
and the promised "cost record" hold only if mode G exists at the rung; Ladder §2 lists the cost
record in the promised set unconditionally.
**Why it matters:** As written, either stop 4 (Q8 breach → size claim withdrawn) fires at R6 by
arithmetic in the mode the plan says it will use, or the Q8 criterion (issue 3) is shaped so that
it does not. A cold reader cannot tell which sentence wins: "does not grow" (Goal, wins on drift)
or "2M-plus" (Goal, five paragraphs later). The Goal must say which, and the promised set must
say what it promises when only mode E runs.
**Status:** open

### 5. The learned prior's back door is open at R6: the Goal forbids it "on a promised rung", the operative sentences forbid it only on a "promised *accuracy* rung"
**Where:** Goal "Scope boundaries" last bullet; Ladder §3 last **[05]** bullet; Distilled §4
(learned-prior bullet), §5; Ladder §2 "Promised" (R6) and §1 (cost-sentence form); Q8.
**What:** Goal: the M05 learned Δ-prior "**never replaces probes on a promised rung**." Ladder §3:
"The learned Δ-prior (M05) may reduce K only on rungs where the P3 saving was demonstrated on
held-out probes at the previous rung, and never on a promised **accuracy** rung's scored
spectrum." Distilled §4 (the deviation list, i.e. the enforceable text): forbidden is "Using the
learned Δ-prior on a promised **accuracy** rung's scored spectrum; using it to lower K without a
P3 result on held-out probes at the previous rung." R6 is promised ("R6 reached as a reach rung,
conditional on B3") and is not an accuracy rung. Its "previous rung" is R5 (bonus, may not run)
or, in practice, R3. So the Ladder and Distilled permit exactly what the Goal forbids: a
prior-assisted K(R6). The cost sentence form (Ladder §1) — "K = n probes at this rung, mode E/G,
wall-clock w per probe" — has no field for the prior, and Q8's side-by-side K(R1..R3) are
uninformed-prior numbers only because Q7's wording says so; nothing pins K(R6) to the same prior
as K(R3) in the sentence that compares them. Distilled §5 "The promised spectra never depend on
its outcome" is then false for R6's cost record.
**Why it matters:** Loophole 5 of the brief is not closed by "read Ladder §3 and Distilled §4
together" — read together they are the *narrower* rule. K(R6) "of the same order as K(R3)" can be
bought by the Transformer prior, which is the one thing the plan says is never load-bearing.
**Status:** open

### 6. Δ₃/Δ₄ first enter a scored spectrum at R2 and no gate ever licenses them; R0–R1 are scored with a different pipeline from the one the claim describes
**Where:** Goal "The scientific question — Accuracy" and "Reach"; Distilled §1, §3 "Δ-probing",
§9.2; Ladder R2 row ("what it licenses" cell), §2 "Ordering"; Q7.
**What:** Goal (accuracy, R0–R3): "a **probed** coupled-cluster correction to the force constants
(**Δ₂ on all modes; Δ₃/Δ₄ on the scored band families**)". Distilled §1: the same. Goal (reach):
"Can the **same pipeline, unchanged**, produce …". Ladder R2 licence cell: "Δ₃/Δ₄ probing on the
promised families **for the first time**." Ordering: "Q7 must pass at R0 and R1 before any Δ
enters a scored spectrum." Q7 checks only Δ₂: "recovered Δ₂ … vs a directly computed reference
Δ₂"; Distilled §9.2 likewise ("the probed Δ₂ reproduces a direct CC force-constant correction").
Distilled §3 gives Δ₃/Δ₄ "least squares for the targeted Δ₃/Δ₄" — no hold-out, no reference, no
gate, no pilot-note tolerance. So: R0–R1, the rungs where a direct CC reference is affordable, are
scored with a Δ₂-only pipeline; R2 — a promised accuracy rung — adds a component that has never
been compared to anything, at a size where the plan says a reference is not affordable; and the
pipeline is not "unchanged" between R1 and R2.
**Why it matters:** Ladder §2's ordering rule says no Δ enters a scored spectrum unlicensed. Δ₃/Δ₄
do. Either Q7 (or a Q7′) must cover Δ₃/Δ₄ at R0–R1 — where cubic references *are* computable — or
the claim sentence must say R0–R1 are Δ₂-only and R2 introduces an unlicensed term. Right now the
claim describes one pipeline and the ladder runs two.
**Status:** open

### 7. The R2 row was "carried verbatim" from plan 04, but plan 04's own last measurement had already falsified its reasoning: triphenylene *has* gas-phase IR, tetracene does not
**Where:** Ladder §2 R2 row and §3 "Gas-phase preferred"; Frozen_Lines §5 NIST row; probes/README
"Probes that exist"; plan 04's Ladder R2 row and plan 04's `probes/README.md`.
**What:** Plan 05 Ladder R2: "pyrene C₁₆H₁₀; tetracene, chrysene C₁₈H₁₂ (A-scored set);
**triphenylene computed and reported, not scored**"; lab cell "PAHdb experimental (uids 334, 282,
291)". Plan 04's R2 row gave the reason: "triphenylene C₁₈H₁₂ is computed and **reported, not
scored — it has no laboratory spectrum**." Plan 05 deleted the reason and kept the exclusion.
Meanwhile plan 05's Frozen_Lines §5 records the coverage probe: "gas IR present for benzene,
naphthalene, **pyrene, chrysene, triphenylene**; **tetracene solid-only**; coronene absent", and
probes/README carries the same result "as provenance". Ladder §3: "Gas-phase preferred over matrix
wherever both exist." So the A-scored set contains the one C₁₈H₁₂ isomer with no NIST gas
spectrum and excludes the one that has it; the R2 lab cell names only matrix uids for pyrene and
chrysene, which the probe says have gas data — and under the gas-preferred rule those two
families would not even be M03-gated. The plan-04 probes README's caveat ("the R2 gas grids are
~4 cm⁻¹") did not travel either.
**Why it matters:** This is the inheritance claim failing on the one rung where plan 04's Round-6
Pass B finding 1 (matrix scoreboard cannot decide R2–R3) lived. The ladder was carried from a
version of plan 04 that predates plan 04's own measurement. A cold reader sees an exclusion with
no reason and a scoreboard cell that contradicts the file two links away.
**Status:** open

### 8. Search-snippet records are used as facts where they justify frozen intent, and the load-bearing premise (Δ is short-ranged) is asserted as fact in the argument of record
**Where:** [Relevant_Scientific_Papers.md](Relevant_Scientific_Papers.md) status rule and items 25,
27, 28, 30, 36–38, 41; Research note §1, §2, §3, §4.3, §4.4; Goal "What is scored" and "Method
skeleton" step 1; Distilled §3 "DFT anharmonic constants" and "Intensities"; Why_05 "The block
plan 04 could not lift" and the method table.
**What:** The bibliography's own rule: "**record (search 2026-09-03)** = seen only in web-search
result snippets on that date — *not* a cite." Then:
- *Cited-but-unverified, used to change frozen intent.* Item 27 (Bégué et al.?): "**record (search
  2026-09-03)** — **author list not verified**". Research note §4.4 quotes its number as the
  reason for the harmonic-first allocation — "CCSD(T) quadratic + B3LYP cubic/quartic gives mean
  deviations under 0.8 %" — and says "This is a change of frozen intent relative to plan-04
  Distilled §3". Why_05's table: "harmonic Δ₂ first (where the hybrid-QFF literature says CC pays
  most)". Item 14 (Boese/Klopper/Martin) is at least a plan-02 record; item 27 is a snippet with
  an unverified author list carrying a quantitative claim into a design decision.
- *Cited-but-unverified, used as the reason for a scope rule.* Item 30 (Madriaga & Crawford):
  "record (search 2026-09-03) — PMC fetch blocked". Research note §4.3 states from it that "PNO
  domain changes of order 1 μE_h in energy produce errors above 100 % in finite-difference field
  derivatives". Goal: "no CC correction to dipoles is promised (local-correlation discontinuities
  corrupt finite-difference field properties — bibliography item 30)". Distilled §3: "(bib 30 —
  PNO discontinuities corrupt field derivatives)". Conservative decision, snippet-grade support,
  quoted as fact in two frozen documents.
- *Snippet quoted as fact.* Item 41 REST is "record (search 2026-09-03)"; Research note §1: "The
  only Rust electronic-structure code found (REST, 2025) **has no local coupled cluster**." Item 25
  GPU4PySCF: the bibliography says the timing was "seen in a search snippet only"; Research note
  §3 calls it an "assertion from the **vendor paper**". Items 37, 38 (Ruth; Zhou) appear in §4.1
  and §2 with specific content ("learned it from few points"; "recover cubic and quartic force
  constants of solids from a modest number of randomly displaced DFT configurations"). Item 28
  (Fusè) is the sole support for Distilled §3's "reduced-dimensionality" choice.
- *Stated as fact where the gate treats it as the bet.* Why_05: "the CC anchor's only new
  information is the CC−DFT difference, **which is small, smooth and short-ranged**." Research
  note §2: "**Short-ranged in real space** — the correlation-energy error of DFT is a local
  quantity." Goal: "Known risks, named now: **Δ may not be local enough (Q8)**." Why_05's own
  closing section: "If, at R1–R3, the Δ₂ elements between atoms do **not** decay with distance
  (Q8) … plan 05 has no size advantage." The supporting items (35 OK — energies in condensed
  phase; 36 snippet — correlation energies; DLPNO itself — energies) are citations for *other
  quantities*; none is a curvature on a PAH. That is "supported by a citation not yet verified
  for this quantity", and the argument of record writes it without the hedge the Goal uses.
**Why it matters:** The research note's §6 blanket ("Everything else … seen in search result
snippets only … re-fetch before any scored use") covers the note. It does not cover Goal, Distilled
and Why_05, which re-quote the same items as reasons. The plan's rule is that a record item is
not a cite; two of the plan's frozen-intent decisions cite nothing else.
**Status:** open

### 9. The Δ=0 null's one "non-negotiable" sentence attributes the outcome to a different arm than the one tested; P4(c) has no consequence sentence at all
**Where:** Distilled §7 P4(a)–(c) and the paragraph after the P table; §8 third sentence; §4 M04
exception; Goal "Known risks".
**What:** P4(a): "**Δ = 0** (DFT harmonic + DFT anharmonic, no CC correction) … must lose that
comparison — else the CC claim is void and reported as '**explained by the calibrated harmonic
baseline**'." §8: "The coupled-cluster correction did not improve on Δ=0 at Rn; the claim is void
and the result is reported as explained by the calibrated harmonic baseline." But the Δ=0 arm is
*DFT anharmonic*, and the "calibrated harmonic baseline" is M04 — by §4 "the single declared
exception … trains on lab residuals by design … outputs appear only as a P2 opponent column".
If Δ=0 passes, what explains the result is DFT anharmonicity, not M04. In plan 04 the null was
"harmonic-only", so the wording matched; plan 05 changed the arm (issue 1) and kept the
sentence. The Goal repeats the conflation: "the harmonic-first allocation of CC may still lose to
**calibrated harmonics** on some families (**P4's Δ=0 null row** remains mandatory …)" — losing
to M04 is a P2 outcome, not the P4 null. "Must lose that comparison" is also ambiguous: P2
compares the pipeline to line A, M04 and line B; the text does not say whether Δ=0 must lose *to
the pipeline* or must *fail to beat the lines* (a Δ=0 that beats the lines while the full pipeline
beats them by more is "void" under the second reading and "clean" under the first).
P4(c): "the **shuffled-probe null** of Q7 must fail Q7" — and then nothing. The post-table paragraph
and §8 only handle P4(a). The case is not hypothetical: with the promised ℓ₁ near-diagonal prior
and a family whose true |Δ₂| is below the Q7 tolerance (§4.10: "no larger than the smallest beat
margin"), a shuffled recovery collapses toward zero and passes Q7 by construction; the plan has
no sentence for that outcome. P4(b) is in the same position, as it was in plan 04.
**Why it matters:** The Round-6 fix was "one fail-closed sentence, identical in P4, §7 and §8". It
is identical — and now says the wrong thing. A Module 08 author can truthfully say M04 did *not*
explain the result and treat the sentence as inapplicable.
**Status:** open

### 10. What licenses a cost sentence is stated three incompatible ways, and the Goal itself writes cost sentences the Ladder forbids
**Where:** Ladder §1 (third sentence type), §6 last bullet, R6 row; Goal "Prime directive", "The
scientific question — Accuracy", "Forbidden quotes"; Distilled §3 "Modes"; plan-05 README
"Provenance".
**What:** Ladder §1: cost claims are allowed "**only** in the form 'K = n probes at this rung, mode
E/G, wall-clock w per probe, printed by `probes/…`'. A cost sentence without a probe file is
forbidden, including in the Module 08 paper." Ladder §6: "No cost sentence ('size-independent',
'O(1)', 'a few hundred points') **outside the form of §1's third sentence type**." Goal forbidden
quotes: "'The coupled-cluster cost is size-independent' **unless** Q8 printed the decay and K
printed at ≥ 2 rungs of different size" — i.e. permitted, after two rungs. Ladder R6 requires a
sentence that is not in the §1 form: "**K(R6) reported against K(R3)** in the same sentence as the
spectrum." Three rules for one sentence. Meanwhile the Goal — the file that "wins on drift" —
contains: "at a coupled-cluster cost that **does not grow with the molecule**" (prime directive);
"recovered from a **size-independent** number of local-CC evaluations" (inside the *accuracy*
question, R0–R3, as a presupposition, not the thing asked); and the README's Provenance says
"a **size-independent** pattern set". Distilled §3: "K expected **O(1)**". The Goal's disclaimer
("It is not a claim; it is the measured quantity K") does not stop Module 08 quoting the prime
directive as the project's stated aim. The Goal also says the efficiency question "is answered by
measurement … never by the literature figures that motivated it" and then embeds the literature's
answer in the accuracy question — the accuracy/efficiency concatenation is the same shape as the
accuracy/reach concatenation Round 6 Pass A issue 2 closed.
**Why it matters:** Brief loophole 9, open. The one sentence plan 05 exists to earn can be written
in Module 08 by citing the prime directive, and the three documents disagree on when it is earned.
**Status:** open

---

## Non-blocking findings

### 11. "MD-ACF on a DFT-plus-Δ potential" survives from plan 04, whose potential was the deleted learned surface; plan 05 never says what the MD runs on
**Where:** Goal "Method skeleton" step 3 and "Temperature and emission" tier 2; Distilled §3
"Anharmonic machinery"; Ladder §4.7.
**What:** Plan 04 Distilled §3: "ML surface on sampled geometries … → spectra via … (b) **MD-ACF
only**"; tier 2: "If the per-molecule ML surface exists, MD at chosen internal energy". Plan 05
keeps the route — "GVPT2 on DFT-plus-Δ, or **MD-ACF on a DFT-plus-Δ potential**", "temperature-
dependent shifts from MD on a DFT-plus-Δ potential" — but the plan-05 object is a set of force
constants near equilibrium (Δ₂ all modes, Δ₃/Δ₄ on scored families), not a potential one can
propagate MD on. Whether "DFT-plus-Δ potential" means a truncated QFF, a DFT-trained potential
plus Δ (Distilled §3 permits one "if named in the deck"), or something else is not written.
**Why it matters:** The pilot note may choose MD-ACF for a rung (item 7). If it does, it chooses an
undefined object. Non-blocking only because GVPT2 is the other option; blocking the day MD-ACF is
named.
**Status:** open

### 12. The held-out set's *membership* is not hashed, and "residual" is never defined
**Where:** Distilled §3 "Hold-out", Q0, Q3; Ladder §4.11; Goal step 4; probes/README item 1.
**What:** Distilled §3: "a fraction f_h of probes never enters the recovery and yields the residual
that goes into the error budget." Q0 hashes "pattern set, solver settings, K, f_h, r_c" — the
fraction, not which probes. Q3 ("split overlap (molecule and probe batch)") governs the ML splits.
Nothing says the hold-out assignment is drawn by a seeded rule fixed in the deck before responses
exist; an author can choose which probes to hold out after seeing which ones the recovery fits.
"Residual" itself — of what (held-out energies? gradients? Δ₂ elements?), in what norm, relative
or absolute — is defined nowhere, although it is the error-budget term (Goal step 4), the P3
metric (§5 "lower the held-out residual at fixed K"), the K justification (§4.8) and the Q8
anchor ("at the frozen residual").
**Why it matters:** The residual is the only pipeline-internal honesty number plan 05 adds. As
written it can be shaped twice — by choosing its members and by choosing its definition.
**Status:** open

### 13. Q7's reference shares the frozen-domain approximation with the thing it checks; only R0's canonical arm is independent, and that is not said
**Where:** Distilled Q7; Ladder R0/R1 licence cells and §5.4; Q6.
**What:** Q7: "recovered Δ₂ … vs a directly computed reference Δ₂ (full numerical local-CC Hessian
minus DFT Hessian, **same frozen domains**; at R0 also canonical)". A bias introduced by freezing
domains at the reference geometry is present in both sides at R1 and invisible to Q7 there; the
canonical arm exists only at R0, and at R1 only if the conditional canonical run succeeds (R1
row). Q6 measures noise "with and without frozen domains", not bias. No sentence says "Q7 at R1
tests the recovery, not the freezing". Separately, stop 4's Q7-breach fallback — "best-level
harmonic + declared-provenance correction, labelled" — is plan 04's hybrid wording; in plan 05,
if Δ failed Q7, what the "declared-provenance correction" is has no referent.
**Why it matters:** Brief loophole 3. Not a contradiction; an unstated limit on what the probing
licence can license, at the rung that licenses everything above it.
**Status:** open

### 14. The two debt lists again claim to be identical and are not
**Where:** Frozen_Lines §7 heading and item 5; bibliography "Named debts" heading, item 5, and the
"Plan-05-specific debts" paragraph.
**What:** Frozen_Lines §7: "(… **identical to the bibliography's list**)". Bibliography: "(**same
list as Frozen_Lines §7, kept in sync**)". Item 5 differs: Frozen_Lines names "DLPNO-CCSD(T) /
LNO-CCSD(T) / ORCA / Psi4 / MRCC"; the bibliography names "DLPNO (ORCA, Psi4), LNO (MRCC,
**PySCFAD**) — items 17, 32, 33, 34". The bibliography then adds a paragraph of "Plan-05-specific
debts (not in the frozen-lines list …)" — item 27's author list, items 25/28/30/34–38 to fetch,
the O1NumHess licence — so the two files' debt inventories differ by a paragraph while both say
they are the same. Round 6 Pass A issue 7 was this finding; the closure was carried in form and
drifted again in content.
**Why it matters:** Small, but the sentence that says "kept in sync" is the one a reader trusts
instead of diffing.
**Status:** open

### 15. Motivational sentences assert measurements that were never made
**Where:** Why_05 "The block plan 04 could not lift" (last paragraph); Ladder §5.4 (Q8 breach);
Research note opening paragraph.
**What:** Why_05: "A method whose cost grows with the size of the surface **cannot reach
C₃₈₄H₄₈-class species on any allocation this project will hold**." No allocation exists, no probe
ran; the inputs on file are two labelled assertions (grok_chat_4 lines 352–360 — checked, the
lines say what the note says; and the "many, many hours" report). Ladder stop 4: "the plan does
not fall back to a point factory **it has already shown it cannot afford**." Nothing has been
shown; plan 04 never ran a timed local-CC point. These read as results. (The research note's
framing "fit into roughly a year of computing" is the user's question, not a cap, and no document
turns it into a gate — that part passed.)
**Why it matters:** The brief's calibration warning in one sentence: fluent, confident, unmeasured.
Both are in files a reader will quote.
**Status:** open

### 16. Notation and acronyms assume the research session; the Round-6 acronym closure did not travel
**Where:** Why_05 method table; Goal "The scientific question" and step 2; Research note §2;
Ladder §1 and §3; Distilled §3; plan-05 README "Provenance"; plan 04 README "Provenance".
**What:** Δ₂/Δ₃/Δ₄ are used in Why_05 (reading-order item 2) and the Goal (item 3) and defined only
in the research note §2 (item 4). "mode E / mode G" is defined in the Goal — good — but Ladder §1
writes "mode E/G" as if standard. "Uninformed prior" (Ladder §3, first use) is never defined; the
promised route in Distilled §3 has a structural prior ("near-diagonal prior; ℓ₁-regularised, with
an off-diagonal low-rank term") that is "uninformed" only relative to the learned one — and that
distinction is the P3 comparison arm. DLPNO, LNO, PNO, TightPNO/NormalPNO, GVPT2, VPT2, MD-ACF,
QFF and THC (Research note §6) are not expanded anywhere in the plan-05 folder; the plan-04 README
expanded DLPNO as the closure of Round-6 Pass A issue 16, and plan 05's README Provenance, which
replaces it, does not. "Goal, tier 3" in the Ladder R4 row collides with the Goal's emission "tier
3 — not promised". Distilled §5–§6 cite "the mapping" ("Module 04's applied-ML object only if the
mapping needs it there"; "The M06 generative pattern-proposer (mapping)") for a file that does
not exist.
**Why it matters:** The defence audience reads the Goal before the research note and has no
session in its head.
**Status:** open

### 17. Stale status text after the 04→05 patch
**Where:** root README "Repository layout" paragraph on documents 10–12 and "Conventions";
[Rubrics/README.md](../../../Rubrics/README.md) "What is not here"; plan-05 README "Review record"
and "Not yet done"; plans/README "Layout".
**What:** Root README: documents 10–12 "sit in its `GoalGathering/Horizon/` **until that folder's
removal**" — the same file says the plan-03 folder was removed on 2026-09-02. Root README
"Conventions" links "[plan 04 conventions](…04…/probes/README.md)" although plan 05 has its own
probes README with a **[05]** addition. Rubrics/README: "plan 04 has no horizon documents by
design" — plan 05 unmentioned. Plan-05 README: "Round 7, Pass A … Brief: … (**to be written**
before the review)" and "Not yet done: Round-7 Pass A brief" — both Round-7 briefs exist in the
folder. plans/README: "`Uitleg/` is not started for plan 04 or 05" — `Uitleg/` is defined nowhere
in the tree. The plan-04 tree status itself (superseded, kept pending the user's decision) is
consistent across every banner and table — that passed.
**Why it matters:** Navigation only; recorded so the next patch sweeps them.
**Status:** open

### 18. Rubric pre-commit: Module 05's dataset is pre-declared as the self-generated Δ corpus, which the dataset rule may treat as reuse
**Where:** Distilled §5 (model family), §6 first bullet; Rubrics/README "Dataset rule";
`Rubrics/05_Deep_Learning_Systems.md` lines 472–474 and 685.
**What:** Distilled §6: "The probed-Δ corpus is published (Zenodo DOI, deck hashes) **before Module
05 starts**." §5: the Transformer prior is "trained on the published corpus of probed Δ tensors
from earlier rungs." Rubrics/README's load-bearing rule: "publicly available before that project
starts … **not reused from an earlier capstone project**"; the Module-05 rubric itself: "Not be
reused from any previous capstone project." The Δ corpus will be produced as project work in an
earlier module (which one, the unwritten mapping decides). Round 6 Pass A issue 10 / Pass B issue
10 flagged exactly this "distinctness landmine" for M04; plan 05 walks M05 onto it in a frozen
document before the mapping exists. Also: by Module 05 only R0–R1 can plausibly have run, so the
corpus is two molecules and Q3's "splits by molecule" is a two-way split — a mapping question,
noted here so it is not discovered there.
**Why it matters:** Not a contradiction; a pre-commitment in the Distilled plan that the rubric
reading in this tree does not obviously allow, made before the document that is supposed to make
that call.
**Status:** open

### 19. Small number and provenance nits
**Where:** Research note §1 and §5; Ladder R0 row vs Budget §3; Ladder R1 row vs Budget §4.4;
bibliography item 26.
**What:** (a) "C₃₈₄H₄₈-class ≈ 1,290" modes: the atom count (432 for that formula) is not stated,
and "class" makes the mode count indefinite; the same file gives coronene's 102 without the
36 atoms either. (b) TeraChem "arXiv:2512.01055, **Feb 2026**" — a 2512 arXiv number is December
2025; the bibliography gives JPCA 2026 with "DOI from search". (c) Ladder R0 "~20 s/point" vs
Budget "19.6 s" — same number, both labelled old-laptop provenance; fine. (d) Ladder R1: "the first
R1 probe measures **whether** canonical (T) runs on the new machine" vs Budget §4.4: "R1 … same,
**plus the canonical reference for Q6/Q7**" — the budget's probe order assumes the outcome the
ladder says is conditional. (e) Research note §2 says of Sanders et al. "Not extended to coupled
cluster or to anharmonic constants **by its authors**" — a claim about a decade of later work
drawn from one 2015 full text; and the plan-05 README's "that **no one had applied** to a CC−DFT
difference … as of that search" is fact-form with a trailing hedge, where Frozen_Lines §1 gets it
right ("that absence is a search result, not a fact").
**Why it matters:** None changes a decision; (d) is the only one that pre-empts a probe.
**Status:** open

### 20. Mode may change between rungs; the side-by-side K comparison does not say it is same-mode
**Where:** Goal step 2 ("decided per rung by a timed probe"); Distilled §3 "Modes … both K values
printed"; Q8; Budget §2 ("Both modes are classified separately"); Ladder §4.8.
**What:** Mode is chosen "per rung" by the gradient-availability probe. Q8 compares "K(R1), K(R2),
K(R3) side by side at the frozen residual" without saying the three are the same mode. If
gradients run at naphthalene (PySCFAD "medium-sized molecules", bib 33) and not at coronene, the
saturation test compares an O(1)-class K(R1) with a 2M-class K(R3), or — if the author prefers —
the reverse. Ladder §4.8 also asks the pilot note for "K per rung and per mode (E and G)" justified
from R0–R1 curves; if the gradient probe says "no" at R0, K(G) has no curve to be justified from,
and the text does not say the item reads NOT_RUN.
**Why it matters:** The saturation claim is a ratio; the ratio needs matched numerators.
**Status:** open

### 21. Q7 tolerance and the beat margin are bound together in one direction only
**Where:** Ladder §4.10; §4.2; Distilled Q7.
**What:** Item 10 fixes the Q7 tolerance "no larger than the smallest beat margin" — good, one bin,
one bound. But the beat margins (item 2) and the Q7 tolerance (item 10) are written in the same
note by the same author, and nothing prevents raising the smallest beat margin so that a Q7
result already in hand (issue 2: the R0 reference comparison exists before the note) clears the
tolerance. Plan 04's rule that margins come from "the lab side and the opponent side only" still
holds for the margin; the tolerance is new and is bounded by a number chosen at the same sitting.
**Why it matters:** A minor variant of loophole 2; recorded because the tolerance is what licenses
Δ into every scored spectrum.
**Status:** open

---

## What passed

- **Plan 05 is current and draft; plan 04 superseded and kept; plans 01–03 git history** — the
  same story in the root README banner and table, plans/README banner, prose, table, "Version 05"
  and "Version 04" sections, the plan-05 README, Why_05, and the Distilled §2 row. Nothing in the
  tree calls plan 05 complete or any plan-05 number a result. Round 6 Pass A issue 1 stayed closed.
- **No hour cap or deadline re-entered.** Goal "Hours", Budget B1 ("uncapped, logged"), Ladder
  stop 2 ("Human hours are never a stop condition"), Why_05 ("human hours uncapped"). The research
  note's "roughly a year of computing" is the user's question, not a gate.
- **UvA is a collaboration, not an allocation**, everywhere: Goal "escalate to UvA supercomputer
  access or rented GPU time … under [the budget]"; Budget B3 "no number until … (a) access — an
  allocation, or a dated spend cap"; Ladder stop 3. Consistent with each other.
- **Frozen_Lines is carried in substance.** The diff against plan 04's file shows: the same
  opponents, versions, DOIs, scale factors (0.964 / 0.979 / 0.975, one place), scoreboards,
  measured floor (7.1 / −36 / −49 / 60.2 cm⁻¹, labelled plan-02 / `800f3aa` / script), and six
  debts; the edits are provenance (Mulas arXiv re-verified by the Round-6 Pass B reviewer; the
  NIST coverage probe result; "the only predictions **found**" replacing "on Earth"; the 2026-09-03
  search recorded as "a search result, not a fact"). The Bos MAE stays unquoted (Round 6 issue 9
  closed).
- **The bibliography's status vocabulary is honest where it is used as vocabulary.** Fetched
  (23, 24, 26, 29, 31, 32, 33, 35, 39, 40) vs snippet (25, 27, 28, 30, 34, 36–38, 41) is marked
  item by item, including partial fetches ("JCTC DOI from the arXiv/ACS listing, landing not
  opened"; "JPCA DOI from search"). The research note §6 says what was fetched and what was not.
  Issue 8 is about re-quoting, not about the marks.
- **Literature figures stay out of the budget slots.** Budget §3 puts O1NumHess "~100–124", Sanders
  "30 %", GPU4PySCF "~30 min", TeraChem "~8 h" and the grok_chat_4 "tens of minutes to hours" in a
  column headed "Literature figure (not this project's)" with every plan-05 slot reading NOT_RUN;
  Budget §5 keeps "A timing quoted anywhere but a `probes/` script output is invalid." The plan-02
  laptop timings are labelled provenance and "re-timed on the new machine before use". No timing
  in the set is used as a budget.
- **"No analytic DLPNO-CCSD(T) gradient advertised"** is stated with what was checked (ORCA 6.1
  change log, ORCA 6.0 gradient page, Psi4 manual, dated) and never hardened to "does not exist";
  Goal says "may not exist"; the gradient-availability probe is owed first. Same for frozen
  domains: "documented for DLPNO-MP2, not for DLPNO-CCSD(T)", with a stop condition if no code can.
- **Round-6 closures carried (checked against plan 04's files):** Goal question split per claim
  type (with the new accuracy/efficiency wrinkle in issue 10); Q4/M04 exception and the
  leave-molecule-out check; R1 canonical licence conditional; matrix tolerance in one bin
  (15 cm⁻¹ working, M03-measured binding, pilot-note item 4); 10 cm⁻¹ astronomical floor and the
  ~1 cm⁻¹ scoreboard bind in both Goal and Ladder; C₃₈₄H₄₈ hedged to "class" with debt 6; pilot
  note inputs restricted and the R0 pilot producing no pipeline-vs-lab number; positions scored /
  intensities reported, in the prime directive and Distilled §1; R2 A-set separated from
  triphenylene and the neutral-charge rule; Tang demoted to "context only"; tier 2 blocked on
  debt 4; Sylvetsky pinned; P3 effect size binned (item 5); the booking rule; resonance-explicit
  routes with raw VPT2 forbidden on promised families; Q6 anchor-licence probes as stop 4;
  R6 conditional on B3 with an "explicitly an extrapolation" label and "never beat"; M04 fallback
  datasets (bib 21–22). Round 6 Pass B's five blocking findings each have a corresponding sentence
  in plan 05.
- **The Δ=0 null is pinned to DFT anharmonic constants** — "DFT harmonic + DFT anharmonic, no CC
  correction" — so the null is the honest no-CC arm, and P4(a) is bound to P2's script, bands,
  windows, seeds and aggregation. Issue 9 is about the sentence that follows, not the arm.
- **The pattern set is hashed before the first probe** (Ladder §3, Q0), and adding, removing or
  re-weighting patterns after the residual is known is a named §4 deviation; M06 proposals must
  enter the hashed set "before the recovery for that rung runs, never after". The loophole that
  remains is the hold-out membership (issue 12), not the pattern set.
- **Gate numbering is consistent**: plan 05 uses Q0–Q8 and P0–P5 throughout; every cross-reference
  to a pilot-note item (§4.4 matrix tolerance, §4.5 P3 effect size, §4.8 K, §4.10 Q7 tolerance)
  resolves to the right item; no reference to plan 04's Distilled §9.5 or Q6-as-last-gate survives.
- **Old-plan vocabulary is gone from the promised path.** N_min appears only as "Replaces plan
  04's N_min"; "10⁴" and "point factory" appear only as plan 04's labelled assertion or in the
  refusal to fall back to one; "learned surface" appears only as the thing removed (the DFT-trained
  potential option in Distilled §3 is at DFT level and deck-gated; issue 11 is the related gap).
- **Plan-02 / plan-04 provenance is checkable**: script name and commit for the measured floor,
  `probes/nist_cache/` for the coverage probe, grok_chat_4 line numbers for the cost assertion
  (checked: lines 352–360 say what the note says they say).

---

## Round 7, Pass A — issue index

| # | Class | Blocking? |
|---|---|---|
| 1 | Contradiction (inheritance vs change list) | yes |
| 2 | Contradiction + number bin + loophole (K frozen vs measured; residual unbinned; pilot-note timing) | yes |
| 3 | Loophole (Q8 saturation criterion has no form) | yes |
| 4 | Contradiction (mode E default vs "does not grow"; cost record unconditional) | yes |
| 5 | Loophole (learned prior at R6; Goal vs Ladder/Distilled wording) | yes |
| 6 | Loophole / contradiction (Δ₃/Δ₄ unlicensed; two pipelines) | yes |
| 7 | Contradiction (R2 row vs the coverage probe; inheritance) | yes |
| 8 | Unsupported (record-search items as justifications; locality asserted) | yes |
| 9 | Loophole (P4(a) sentence misattributed; P4(c) no consequence) | yes |
| 10 | Contradiction + loophole (cost-sentence licence stated three ways; Goal leak) | yes |
| 11 | Unreadable / inheritance gap (MD-ACF potential undefined) | no |
| 12 | Loophole (hold-out membership; "residual" undefined) | no |
| 13 | Unstated limit (Q7 reference shares frozen domains; fallback referent) | no |
| 14 | Contradiction (debt lists "in sync") | no |
| 15 | Unsupported (motivational sentences as measurements) | no |
| 16 | Unreadable (notation, acronyms, "uninformed prior", mapping refs) | no |
| 17 | Stale text (Horizon sentence, links, README review record) | no |
| 18 | Rubric pre-commit (M05 dataset = self-generated corpus) | no |
| 19 | Number / provenance nits | no |
| 20 | Loophole (mixed modes in the saturation ratio) | no |
| 21 | Loophole (Q7 tolerance bound to a margin chosen at the same sitting) | no |

Do not treat this file as Pass B. Whether Δ is local on PAH curvatures, whether mode G can exist
at the anchor level, and whether compressed sensing survives local-CC noise are domain questions
for a separate review after these patches, or after an explicit decision to proceed with issues
still open.
