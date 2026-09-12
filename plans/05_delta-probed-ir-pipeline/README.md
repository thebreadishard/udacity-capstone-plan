# Plan 05 — Δ-Probed IR Pipeline

**Status (12 September 2026).** Folder created 2026-09-03; plan text frozen 2026-09-04 and changed since only by
dated notes that name a measurement or a decision (35 numbered decisions so far; the Ladder is the single binding
statement). Not complete as a plan until the pilot note and the mapping's Pass 6. **No rung has run: nothing here is a
pipeline result.** What has run are probes and modules: the DFT dry run of the Δ-recovery (benzene), the anchor
timings (benzene at two basis sets, one canonical gradient, one naphthalene energy at 11.5 h; the tighter-threshold
naphthalene energy is running), probe M1 on the frozen correlation spaces (cc-pVDZ and cc-pVTZ, tight and xtight),
the cheap basis line that put two basis terms into the anchor, and the first versions of Modules 02–05 in the
Udacity rubric form (`modules/`). The project proposal goes to the supervisor on 14 September. Supersedes plan 04;
all earlier plan folders stay in the tree as read-only records (decision 2). Plan 06, an idea plan beside this one,
feeds it only through this plan's dated notes (decision 34 is its first transfer).

**Promised deliverable (Module 08).** A pipeline: **any individual aromatic molecule in, an
infrared spectrum out** — plan 04's criterion, ladder, opponents, scoreboards and gates — with
the coupled-cluster anchor obtained as a **probed correction Δ₂ to the harmonic force
constants** rather than a learned per-molecule surface, from local-CC responses with frozen
spaces, and with the number of responses that correction needed measured per rung and printed
as a cost record beside every spectrum. Mode E (energies) is the guaranteed route; mode G
(gradients) is built in a pre-registered side project. Whether the probe count stops growing
with molecule size is a measured question (Q8) with a pre-registered losing condition, not a
promise. No coupled-cluster correction to anharmonic constants is promised. The largest
species is reached by fragment probing under a measured licence.

The sequence **ends at Module 09**. There is no `Horizon/` and there are no Projects 10–12. (Dated note
2026-09-12, decision 32: a named stand-out follow-up *outside* the sequence — a network trained on the
pipeline's own output — exists on paper, gated by measured conditions; proposal §6, mapping §"After
Module 09".)

## Glossary

Every symbol and term is defined once in the **Goal file's glossary** (reading-order item 3):
Δ₂; local CC and frozen spaces; mode E / mode G; pattern, q_s, response; ρ, ρ\*, f_h, K, K_off,
K_cap; structural prior, learned prior, the licence; τ, τ₇, d₇, r_c, r_max, ε₈, η₈, γ, σ_E, σ_g;
gates Q0–Q8 and P0–P5; rungs and claim types; budgets B1–B3; milestones M1–M5; reading 1 / 2;
the pilot note and the dated notes; CMA, CMA-0, CMA-2; GVPT2, MD-ACF, QFF, CPS, PNO/LNO. Read it
before anything else.

## Reading order

*Layout since 2026-09-12:* `GoalGathering/` holds the nine binding and living documents at top level; dated working notes are in `GoalGathering/notes/`, the review record (professor reviews, briefs, seam check, cold reads) in `GoalGathering/reviews/`. See [GoalGathering/README.md](GoalGathering/README.md). Moving the files changed no text; all links were rewritten and checked.

1. This file — orientation: status, reading order, review record, the decisions, the dated notes after the freeze, what is owed.
2. [GoalGathering/Why_05_Supersedes_04.md](GoalGathering/Why_05_Supersedes_04.md) — every
   change relative to plan 04, in one table (33 rows)
3. [GoalGathering/Overarching_Goal.md](GoalGathering/Overarching_Goal.md) — glossary (Δ₂, R_s, R_a, K, ρ\*, ρ\*_common, u_band, the fragment licence and every other
   symbol), prime directive, the two 2026-09-04 directives, the decision record
4. [GoalGathering/notes/Research_Note_2026-09-03_Delta_Probing.md](GoalGathering/notes/Research_Note_2026-09-03_Delta_Probing.md)
   — the source document as written that morning; §8 records what the Round-7 reviews
   corrected and §9 what the 2026-09-04 decisions changed; §§8–9 win over §§1–7
5. [GoalGathering/Frozen_Lines_to_Beat.md](GoalGathering/Frozen_Lines_to_Beat.md) — opponents
   and scoreboards (carried from plan 04)
6. [GoalGathering/Frozen_Ladder_and_Tolerances.md](GoalGathering/Frozen_Ladder_and_Tolerances.md)
   — sentence types, rungs, the two licences, what is frozen now vs at the pilot note, stops
7. [GoalGathering/Compute_Budget_2026-09-03.md](GoalGathering/Compute_Budget_2026-09-03.md)
   — three budgets; the classification rule; the order of timed probes
8. [GoalGathering/Distilled_Project_Plan_and_Quality_Checks.md](GoalGathering/Distilled_Project_Plan_and_Quality_Checks.md)
   — the Δ-probing object, gates Q0–Q8 / P0–P5, fail-closed sentences
9. [GoalGathering/Relevant_Scientific_Papers.md](GoalGathering/Relevant_Scientific_Papers.md)
   — bibliography with per-item verify status (items 23–60 new)
10. [probes/README.md](probes/README.md) — conventions and the probes owed
10a. [Uitleg/00_Leeswijzer.md](Uitleg/00_Leeswijzer.md) — Dutch, VWO-6 level, 18 chapters: the
    plan explained for a reader without AI or quantum-chemistry background, with the data
    structures of modules 04–08 and a checklist for mapping Pass 6 (not binding; the Ladder wins)
11. [GoalGathering/Capstone_Mapping.md](GoalGathering/Capstone_Mapping.md) — modules 02–09
    against Rubrics v1.5.1; Pass 6 (sign-off) not done
12. [GoalGathering/Project_Proposal_2026-09-06.md](GoalGathering/Project_Proposal_2026-09-06.md)
    — the supervisor proposal, one document, revised through 12 September: the *why* of the major decisions,
    the measurements, the calendar and what is asked of the supervisor; its cover note is in `notes/`; the 3–4 September
    text the review records cite as `Project_Proposal_2026-09-03.md` is in the git history
13. [GoalGathering/notes/Side_Project_2026-09-04_ModeG_Gradients.md](GoalGathering/notes/Side_Project_2026-09-04_ModeG_Gradients.md)
    — the pre-registered side project that builds frozen-space local-CC gradients (mode G):
    milestones M2–M5, kill criterion, budget bucket, what changes on success or failure
14. [modules/](modules/) — the course modules in rubric form: [02 opponent atlas](modules/02_opponent_atlas/README.md),
    [03 laboratory scoreboard](modules/03_lab_scoreboard/README.md), [04 calibrated-harmonic baseline](modules/04_calibrated_harmonic/README.md),
    [05 Δ₂-support predictor](modules/05_support_predictor/README.md); each with a recipe or pre-registration committed
    before its data, a notebook, a report in the APA template, `PROVENANCE.md` and `requirements.txt`
15. [GoalGathering/notes/](GoalGathering/notes/) — dated working notes: research notes (probe M1, dry run, P19, P24,
    scoreboard R0, opponent atlas), the decision memo on the compute route (P13), the pilot-note skeleton, the hardware
    note, the PDF request list, the cover note, and the **software-changes ledger** (every third-party patch and own layer,
    for possible upstream contributions)
16. [GoalGathering/reviews/](GoalGathering/reviews/) — the review record: professor reviews and briefs of rounds 7–10,
    the seam check, four cold reads of the proposal
17. [../06_equivalent-faster-mathematics/](../06_equivalent-faster-mathematics/README.md) — plan 06, the idea plan
    beside this one (equivalent-but-faster mathematics for the anchor's problem; experiments on this plan's sealed
    data; a Lean 4 / Mathlib project); it enters this plan only by dated notes here

## Review record

- **Round 7, Pass A** (cold read, 2026-09-03, fresh context):
  [Professor_Review_2026-09-03_Round7_PassA.md](GoalGathering/reviews/Professor_Review_2026-09-03_Round7_PassA.md)
  — not sound enough for Pass B until patched; 10 blocking + 11 non-blocking; **all 21
  addressed in spec the same day**. Brief: [Review_Brief_2026-09-03_Round7_PassA.md](GoalGathering/reviews/Review_Brief_2026-09-03_Round7_PassA.md).
- **Round 7, Pass B** (adversarial domain, 2026-09-03, fresh context, literature verified):
  [Professor_Review_2026-09-03_Round7_PassB.md](GoalGathering/reviews/Professor_Review_2026-09-03_Round7_PassB.md)
  — **conditional**: green light for the R0–R1 measurement programme once six blocking items
  were written in; no green light for the promised set *as then worded*. **All six written in
  the same day** (Q6 thresholds; banded prior; Δ₃/Δ₄ out; CMA cited; cost question re-anchored;
  Q8 on direct blocks) and non-blocking 7–13. Brief: [Review_Brief_2026-09-03_Round7_PassB.md](GoalGathering/reviews/Review_Brief_2026-09-03_Round7_PassB.md).
- **2026-09-04, user decisions 1–6 and two directives** (Goal, "Decisions of 2026-09-04";
  "The goal binds"; "Inheritance is not authority"); the side project opened.
- **Round 8, Pass A** (cold read of the patched set, 2026-09-04, fresh context):
  [Professor_Review_2026-09-04_Round8_PassA.md](GoalGathering/reviews/Professor_Review_2026-09-04_Round8_PassA.md)
  — "not yet": 11 blocking + 9 non-blocking, almost all seams left by the 2026-09-04
  find-and-replace edits plus three design holes. **All 20 addressed in spec the same day:**
  (1) the learned prior's rule made one rule everywhere — *earned on R2–R3 (both recoveries on
  the same responses, agreement within τ₇), spent on R4–R6*, R0–R3 scored spectra always
  structural, officer rule / claim ladder / M08 labels / glossaries aligned; (2) the licence's
  reference check made a full structural-vs-prior comparison per family, with η₈ as the block
  tolerance; (3) frozen-space code made main-project probe M1 under stop 1, so mode E is
  guaranteed *given M1* and the side project's failure (M2–M5) costs nothing; (4) the side
  project's engine hedged everywhere it is named ((T) snippet-grade; gradient code unlocated;
  §1.2 labelled reasoning); (5) K_cap(G) frozen from a gradient-mode DFT dry run for every
  rung, so licensing mode G never touches the pilot note; M5 added so a "run" exists at R3;
  (6) the pilot-note leak closed — smoothness scatter printed, means sealed; gradient probe
  run/no-run at equilibrium before the note; M2–M5 after it; M1 prints scatter without a
  verdict; (7) a mode-G noise line (σ_g ≤ 2.8·τ·q_s) and a "beat and noise" rule per mode;
  (8) the fragment licence given three parts — Q8 at R2–R3, the fragment-vs-whole comparison at
  R3 (and R4 where affordable), a direct-block probe on the R6 fragments — and the R6 sentences
  split into per-family withdrawal and all-families refusal; (9) "O(1)-class" removed and
  "-class" added to the forbidden list; (10) the M05 corpus size removed from frozen text
  (dated note after the B2 timing); (11) every decided-vs-open survivor swept, decisions 5–6
  added to the Goal's record, research note §9 appended; non-blocking 12–19 swept (stale
  banners; change table rows 9/10/16/17/18 rewritten and rows 25–27 added; debt lists; snippet
  labels; kill clock made calendar time with M1 booked to infrastructure; Q8-at-R0 as a Q7
  sub-item; Distilled §1/§2 for both modes; glossary moved into the Goal); (20) the QM9 /
  Foundations-module question raised as **open decision 7**. Brief:
  [Review_Brief_2026-09-04_Round8_PassA.md](GoalGathering/reviews/Review_Brief_2026-09-04_Round8_PassA.md).
- **Round 8, Pass B** (re-assessment, 2026-09-04, fresh context, literature and code verified):
  [Professor_Review_2026-09-04_Round8_PassB.md](GoalGathering/reviews/Professor_Review_2026-09-04_Round8_PassB.md)
  — verdict: **conditional** — green light for the pre-pilot-note programme and for R0–R1 once
  four in-spec items were written in; no green light yet for R2–R3 on two points; the side
  project may open with its M2 additions. Part 1: of Round 7's six closures, two closed, four
  re-worded. 8 blocking + 10 non-blocking. **All 18 addressed in spec the same day:** (1) Q6
  given one estimator — σ_E/σ_g as RMS residuals about low-order polynomial fits, the noise
  lines evaluated per grid step from that one σ, a totally symmetric mode added; (2) K given a
  noise-aware stopping rule (ρ\* = c·ρ_noise; χ² per point), c and K_cap taken from a
  noise-injected dry run, never the noiseless one; (3) η₈ made absolute (a fraction of the rung's
  coupling scale S, "at noise" pairs enter the fit with uncertainty) in Q7(iv), Q8 and both
  licences; (4) the fragment licence rebuilt — smallest passing radius at R3, a larger-molecule
  comparison at R4 promised conditional on B3, and a fragment-radius convergence test on the
  rung's own interior in place of the circular part (c); (5) the frozen-space object written
  once (mapped by maximal overlap, projected and orthonormalised, assignment printed; projection
  inside the graph), M1 given an assignment log along symmetric modes, M2 an FD reference that
  re-projects and a printed projection-term size; (6) decidability re-based on M03's measured
  band-centre uncertainty u_band (resolution, centroid, temperature term), the R2 C–C families
  pre-declared inconclusive by construction on the NIST hot-vapour source, the supervisor ask
  made load-bearing; (7) mode E runs on every rung R1–R3, mode G in addition where licensed,
  Q8(c) per mode; (8) the anchor basis fixed per rung and a one-point R0 canonical feasibility
  probe added before the note with a written fallback; non-blocking 9–18: M5 given both checks;
  resonance closure bounded to depth one; P3 reported on the PAH held-out tensors and the
  licence tied to the structural recovery's own Q8; M06's display criteria written and its
  training data separated from M05's test set, the M05 fallback made a named debt; the
  inheritance walk recorded in the Goal with the neutral-species rule re-justified; proposal
  staleness swept; engine facts confirmed by the author's own fetch (items 48–49 upgraded; item
  50–51 added); the direct probe re-specified as family-projected couplings at four energies
  per (pair, family) with a step h; M1 given its displaced-geometry columns; the alarm's early
  quietness stated. Brief: [Review_Brief_2026-09-04_Round8_PassB.md](GoalGathering/reviews/Review_Brief_2026-09-04_Round8_PassB.md).

- **Round 9, Pass A** (2026-09-04; cold read of the Round-8 Pass B patches, no web):
  [Professor_Review_2026-09-04_Round9_PassA.md](GoalGathering/reviews/Professor_Review_2026-09-04_Round9_PassA.md)
  — verdict "not yet"; 5 blocking + 23 non-blocking. **All 28 addressed in spec the same day:**
  (1) mode G's c and K_cap read at σ_g^assumed = 2.8·τ·q_s in the note, labelled, M2 printing its
  σ_g against it; "σ_g where a gradient runs" removed from every pre-note description;
  (2) the stopping rule closed with two guards — ρ\* < ρ_max = 0.5 or the rung-mode is "at
  noise" (K = NOT_RUN), and a minimum count (the 2M single-mode block consumed first in mode E;
  n_min(G) frozen in item 9) — and the cost record carrying σ, RMS_resp, ρ_noise, c, ρ(K);
  (3) σ_coupling = σ_E/(2h²) written out; (4) the canonical feasibility probe given two
  extrapolation targets (61-energy bias line; 72-gradient / 1,801-energy full reference Hessian),
  a "fits" rule (≤ 168 h and ≤ 31.3 GB per object) frozen before it runs, and the Q7(i)/(iv)
  fallback when only the bias line fits; (5) which r_f part (c) uses, run once, the passing
  radius in the certificate; (6) "means sealed" → fit coefficients; (7) 72 energies everywhere;
  (8) four Q6 modes in M4/M5; (9) the 2.8 constant derived beside 0.82; (10) ρ\* redefined in the
  glossary as computed, only c frozen; (11) change table rows 7/21/22 corrected, rows ordered,
  32 rows, "does not change" paragraph amended; (12) "three parts" survivors → four;
  (13) the seven pilot-note inputs in Budget §4, Proposal §7/§8; (14)–(15) K_cap(G) and the
  PySCFAD sentence corrected; (16) the proposal's "verified" → snippet grade; (17) "gas grid" →
  u_band; (18) Q6 grid not at R0, R1 fallback without a cross-basis protocol, M4 in the R2 deck
  basis; (19) the amplitude grid stated as a single test at q_s = 1.0; σ's rung index defined;
  (20) S per distance class with equal frozen counts; (21) K_prior < K_struct required, PAH
  effect size informational; (22) 28 GB explained; (23) the budget's supersede-only rule dropped
  (inheritance is not authority), probe numbering aligned; (24) entry-point banners, decision
  count and numbering; (25) note status line and §9 extended; (26) glossary terms and acronyms
  added; (27) Frozen_Lines criterion and §7 trailer; (28) proposal header, §5.3, §11 order.
  Brief: [Review_Brief_2026-09-04_Round9_PassA.md](GoalGathering/reviews/Review_Brief_2026-09-04_Round9_PassA.md).
- **Round 9, Pass B** (2026-09-04; hostile domain re-examination, with web):
  [Professor_Review_2026-09-04_Round9_PassB.md](GoalGathering/reviews/Professor_Review_2026-09-04_Round9_PassB.md)
  — verdict **conditional**: R0–R1 green once four in-spec items landed; R2–R3 under those plus
  one; beyond R3 conditional on one in-spec item and on B3. Part 1: 17 of the 18 Round-8 closures
  held, one (M5's σ_g) was a re-wording. 6 blocking + 6 non-blocking. **All 12 addressed in spec
  the same day:** (1) the mode-E response symmetrised over ± pattern pairs — R_s = ½[ΔE(+p) +
  ΔE(−p)] − ΔE(0) — because the raw difference is dominated by the CC−DFT force term Δ₁·p; K
  counts energies (a pair counts 2); ρ, RMS_resp, ρ_noise on R_s; the dry run the same; (2) the
  frozen space transports both occupied and virtual vectors by projection — no localiser and no
  maximal-overlap assignment at displaced geometries — with M1 printing continuity diagnostics
  instead of a permutation; (3) only R0 scored unconditionally: naphthalene's NIST gas spectra
  are a 245 °C vapour spectrum and a GC-IRD entry (WebBook list opened by reviewer and author),
  so R1 is per family under u_band, the unpinned temperature term has a floor, and the hot-band
  references (items 52–53: Joblin 1995, not opened; Pirali 2009, Crossref-verified) are the first
  paid debt; (4) the fragment written once (ring-closed, H-capped, unrelaxed, radius in shells),
  (b) at coronene stated as one comparison at one shell with a "pending (b′)" outcome, part (c)
  classified as a probe batch by Budget §2 (of order 360 fragment energies at R6); (5) Q8(c) read
  from the stored ρ(n) curves at the common threshold max(ρ\*(R_n), ρ\*(R_{n+1})); (6) σ =
  √(SSR/(n − p)), pooled over the four modes per arm, studentised residuals printed; (7) M2–M5 at
  nine gradients per Q6 mode, σ_g pooled over 3N components, M4/M5 classified; (8) M1's raw
  displaced energies sealed; (9) the feasibility probe also runs one canonical gradient
  (`pyscf/grad/ccsd_t.py` fetched), the expected outcome written, the DZ bias line a lower bound;
  (10) distance classes by bond count with S_class printed; (11) the Goal's item 1 (c) carries
  the r_f rule; (12) the diagonal-cubic bonus counted as two extra energies per mode.
  Brief: [Review_Brief_2026-09-04_Round9_PassB.md](GoalGathering/reviews/Review_Brief_2026-09-04_Round9_PassB.md).

- **Round 10, Pass A** (2026-09-04; cold read of the Round-9 Pass B patches, no web):
  [Professor_Review_2026-09-04_Round10_PassA.md](GoalGathering/reviews/Professor_Review_2026-09-04_Round10_PassA.md)
  — verdict "not yet"; 7 blocking + 13 non-blocking. **All 20 addressed in spec the same day:**
  (1) ΔE(0) declared one shared reference per rung whose offset the recovery's fitted constant
  absorbs, so σ(R_s) = σ_E/√2 is the response σ and ρ_noise = σ(R_s)/RMS_resp everywhere (the √6
  of the Q6 line kept as the conservative threshold convention); (2) K counted in energies in
  every sentence, ρ(n) evaluated per complete pair, K_off ≥ 2, the dry-run script counting the
  same way; (3) the ± pair is the hold-out unit with one deck index; (4) the pooled σ per arm
  gates Q6, per-mode σ's informational with a 2× flag, q_s one number per rung and mode;
  (5) change-table row 31 restored (a literal `\1` from the Round-9 Pass B patch had replaced it);
  (6) "R0–R1 unconditional" removed from Mapping M08 and the root README; (7) the anthracene
  probe redefined as a direct-coupling probe with the count printed (133 was the diagonal-only
  count); (8) status lines and counts brought to Round 9/10; (9) the 360 arithmetic written and
  the B3 verdict labelled an expectation; (10) "one ring" → shell; (11) the 1 cm⁻¹ term labelled
  recalled and the no-stated-temperature default written (series documentation, else hot);
  (12) WebBook lists as items 54–55, both opened by the author too, and the Quantitative IR
  database paper as item 56 (Crossref-verified) — the benzene records state no temperature, so
  R0 is "expected unconditional" until M03 reads item 56; (13) the Δ₁·p size labelled recalled;
  (14) glossary entries for R_a, Δ₁, ρ\*_common, continuity diagnostics, shell, pending (b′),
  u_T, T_source, χ_max, χ_F, pooled σ; (15) "printed" → "passed" in the licence, "by the shell
  rule"; (16) proposal survivors (mode G in addition; the expected feasibility outcome; the
  u_band re-read in §8; §9 extended); (17) M2's FD check stated as Cartesian, 72 energies; M4
  given run/no-run; (18) item 20 pointed at items 52–53, the note's erratum re-pointed;
  (19) 61 / 72 / 1,801 with their arithmetic; (20) the ρ\*_common column NOT_RUN until Q8(c).
  Brief: [Review_Brief_2026-09-04_Round10_PassA.md](GoalGathering/reviews/Review_Brief_2026-09-04_Round10_PassA.md).
- **Round 10, Pass B** (2026-09-04; hostile domain re-examination, with web):
  [Professor_Review_2026-09-04_Round10_PassB.md](GoalGathering/reviews/Professor_Review_2026-09-04_Round10_PassB.md)
  — verdict **conditional, all conditions in-spec**: R0–R1 green once four items landed; R2–R3
  under the same four; beyond R3 green as worded, conditional on B3. Part 1: **all twelve
  Round-9 closures held** (Round-10 Pass A's twenty also checked). 4 blocking + 13 non-blocking.
  **All 17 addressed in spec the same day:** (1) the dry run injects noise **per energy** (with
  one shared ε₀ for the reference), its column indexed by σ_E, so c and K_cap are read at the
  real run's noise; (2) the shared reference energy's offset c₀ is **identified from the second
  amplitude on the scored modes**, not fitted — a fitted constant is collinear with a uniform
  diagonal shift and would have let c₀ shift every frequency the same way; the bonus's two extra
  energies are now mandatory on the scored modes; (3) **Δ₁ is load-bearing**: the scored harmonic
  part carries the first-order corrected-surface-minimum term Σ_j φ_iij^DFT δq_j, printed per
  band; the DFT cubic set gains the totally symmetric modes; no atom is moved (change table row
  33); (4) a **room-temperature 0.1 cm⁻¹ naphthalene spectrum exists** in the PNNL/NWIR database
  (Schneider 2024, item 57; Sharpe 2004, item 59 — Crossref-verified by the author), named now
  under the no-swap rule, so **R0 and R1 are both expected unconditional**; Pirali 2009 also a
  room-temperature source; Maltseva 2016 (item 58) named for the R2 C–H-stretch family;
  (5) u_296 per molecule (1 / 3 / 5 cm⁻¹, recalled) replaces the flat 1 cm⁻¹ term, the floor's
  form kept as conservative (item 60); (6) the frozen-space arms A / B / C written once — the
  pyscf-forge LNO class takes the localized set as input but rebuilds LNO spaces each call
  (opened), so arm A needs a pinned override and Q6's reference arm is B; (7) the quartic term a
  labelled bias removed on scored modes by the second amplitude; (8) a units paragraph in Budget
  §3; (9) the Q8(c) ratio also printed at ρ_ref = 0.3; (10) the 2× flag's false-positive rate
  stated; (11) the mode-G size sentence marked B3-conditional; (12) `max_memory` and peak RSS in
  the feasibility probe; (13) the DFT grid and thresholds as deck numbers, the DFT-arm floor
  printed, σ_E "both arms' noise"; (14) status residues, Goal "expected unconditional",
  Proposal §7; (15) Δ₁ at equilibrium noted as readable and not a note input; (16) fragment
  part (b) scored per family on the shift-carrying pairs; (17) (c)'s R4 instance may run under
  a pending licence without resolving it.
  Brief: [Review_Brief_2026-09-04_Round10_PassB.md](GoalGathering/reviews/Review_Brief_2026-09-04_Round10_PassB.md).

**Cold read 2026-09-06, literature focus** (fresh reader, no web; brief
[Review_Brief_2026-09-06_ColdRead_Literature.md](GoalGathering/reviews/Review_Brief_2026-09-06_ColdRead_Literature.md),
report [Cold_Read_2026-09-06_Literature.md](GoalGathering/reviews/Cold_Read_2026-09-06_Literature.md)):
4 blocking, 13 major, 12 minor; 31 spot checks against the texts on disk, 29 exact. **All 31
addressed the same day:** (1) Esposito 2024 struck as the CC/DFT allocation precedent in the
proposal, Goal, Distilled plan, bibliography and research note — its force field is DFT
throughout; the precedent rests on items 14 and 27 (27 unread); (2) the Ladder's expected-effect
line rewritten: benzene 5.45 cm⁻¹ MAD, read in full, no figure exists at R1 (Goal and Uitleg 09
aligned); (3) the proposal's reference list brought to the readings (Chu, Joblin 1995, Schneider;
Joblin 1994 added); (4) "Bowman 2024" struck; (5) "five" coronene bands → six in four files;
(6) Kitzmiller's ±28 cm⁻¹ qualified as pyridine, ≤ 5 cm⁻¹ on benzene-type rings (proposal,
Distilled); (7) bibliography statuses, both debt lists, Frozen Lines §7 debt 4 and two Uitleg
sentences brought to the 2026-09-06 readings; (8) Goal glossary: u_296 per family and χ_max 0.044
per the Ladder note; (9) CMA 2026 given item 65, the three descriptions reconciled; (10) Wang
2025 struck from the supervisor request; (11) Budget "33 selected off-diagonals" → "+33 % cost";
(12) the O1NumHess "polyene 6–12 cm⁻¹" phrase withdrawn in Budget and note until the PDF is read,
the CMA "~17 atoms / ±20–28" row re-worded from item 43; (13) Lam 2020 status: PDF held, abstract
read; (14) **"sealed" defined** (user decision 2026-09-06: files stay tracked): hash-committed,
readable, tamper-sealed, with an undertaking not to open before the pilot note — Ladder §3 and
proposal §11; (15) initials dropped from the three unfetched entries, the rule reworded;
(16) Käser, Boittier, Upadhyay & Meuwly; (17) PNNL temperature 25/50 °C and 0.112 cm⁻¹ in the
Ladder R1 row, Frozen Lines §5, Uitleg 08; the introduction's 50 °C framing added to the bib;
(18) "2–6 September"; (19) Brumfield/Zhang/Joblin 1994 aligned; (20) the four non-certified
regions named; (21) 0.112 cm⁻¹; (22) D₂h count attributed to the deck; (23) item 34/48 cited for
the MP2 correction; (24) the 495i artefact's source named; (25) `plans/README.md` layout
corrected; (26) `Papers/` duplicates noted under the PDF table; (27) journal records of items 13
and 16 marked unverified; (28) Bégué "0.8 %" labelled snippet in place; (29) the Chakraborty
correction appended to the R2 note; (30) Joblin 1994's 20 % qualified; (31) Uitleg counts and
source aligned. Left as history: the past `REPORT.md` files and the script comments keep the
word "sealed", now defined in the Ladder.

Plan 04's Round-6 findings and their closures bind plan 05 and are not re-litigated.

## Decisions

Decisions 1–6 of 2026-09-04 are closed and recorded in the Goal ("Decisions of
2026-09-04"): 1 fragment probing as a method under the fragment licence; 2 all plan folders
stay; 3 the R2 re-read stands; 4 Module 05 adopted; 5 the promised set — Δ₂ only, mode E
guaranteed, mode G built in the side project; 6 the B2 laptop named.

**Decision 7 (closed 2026-09-04):** nothing has been submitted to the school; the draft
Foundations project on QM9 in the user's GitHub account was never submitted and will be renamed
or archived to make room for the plan's Module 02. M02 is a plan, not a record; M05's Hessian-QM9
corpus carries no module-02 reuse exposure (Goal, decision 7).

**Decision 8 (closed 2026-09-06):** P1 of the dry-run note accepted — in mode E, ρ, ρ_noise and the
stopping rule are computed on the off-diagonal residual R_s,off (Ladder §3 dated amendment;
Distilled §3 row updated).

**Decision 9 (closed 2026-09-06):** P2 accepted — the stopping threshold is ρ\* = max(1.1·ρ_dry,
c·ρ_noise), ρ_dry the noiseless dry run's model floor per rung and mode (Ladder §3 dated amendment;
Distilled §3 K row).

**Decision 10 (closed 2026-09-06):** P3 accepted — the Q6 report prints RMS_off and the implied
off-diagonal σ_E ceiling per rung beside the mode-E noise line; a local-CC σ_E above the ceiling at
R1 makes the mode-G side project load-bearing for the off-diagonal Δ₂ (Ladder §3 dated amendment;
Distilled pointer).

**Decision 11 (closed 2026-09-06):** P4 accepted — the structural prior becomes the symmetry prior
(different-representation elements zero, same-representation elements free, ℓ₁/low-rank only where
the point group leaves too many free elements), entering the deck after the naphthalene dry run
reproduces the direct Δ₂ within τ₇ with it; the banded rule stands until then (Ladder §3 dated
amendment; Distilled rows).

**Decision 12 (closed 2026-09-06):** P5 accepted — the dry run's fixed "declared ρ = 0.1" is retired;
c (pilot-note item 8) is read on ρ_off under the P2 threshold from the noise-injected column (Ladder
item 8 dated amendment; probes README item 1; script prints the P1+P2 reading).

**Decision 13 (closed 2026-09-06):** P6 accepted — mode E is budgeted at K_off ≈ M(M−1)/2 energies
where no prior bites and at the symmetry prior's free-element count where it applies; R1 mode E
without a prior is B3; the size sentence is expected, if at all, through the prior (Budget §3 dated
note; Ladder §1 amendment). **All six dry-run proposals are decided.**

**Decision 14 (closed 2026-09-06):** P7 accepted — the frozen-space object's transported active
blocks are semicanonicalised at the displaced geometry (a rotation inside the frozen space; the
words are in the Ladder §3 object bullet).

**Decision 15 (closed 2026-09-06):** P8 accepted — the energy the object evaluates is the composite
E_LNO-CCSD(T) + [E_MP2(full) − E_MP2(LNO)], every arm on that footing, the bare energy kept sealed
beside it; the Q6 bias line judges the composite (Ladder §3 object bullet and bias line).

**Decision 16 (closed 2026-09-06):** P9 accepted — the cc-pVTZ tight scan with its canonical truth line
runs (started 2026-09-06 07:31, ≈ 2.5 days); the R0 pilot's deck gains a number of canonical two-mode
points from which arm A's off-diagonal bias is read before the pilot note. **All nine proposals of
2026-09-05 are decided (decisions 8–16).**

**Decision 17 (closed 2026-09-06):** module 07's agent runs on **LangGraph** (user, 2026-09-05) with the
**Anthropic API** as model endpoint, model id logged in every run (confirmed by the user 2026-09-06).

**Decision 18 (closed 2026-09-06):** intensities are scored on R0 and R1 as a second quantity
(integrated band intensity, GVPT2 from DFT dipole derivatives, against the NIST Quantitative and
PNNL records); positions stay the primary claim; no CC dipole correction promised; probe M1-μ
measures whether the frozen-space object removes item 30's discontinuity (Goal, Distilled, Ladder §3,
probes README 2b, mapping M03, Uitleg §1.3, proposal §15).

**Decision 19 (closed 2026-09-06):** silent-only coupling blocks are measured per rung — the deck
prints their count, the rung's DFT dry run recovers with and without them, and they are dropped only
where every scored family's position moves by less than τ₇; default keep (Ladder §3 structural-prior
dated note).

**Decision 20 (closed 2026-09-08):** P10 (b) — the anchor-basis curvature bias of the frozen arm
(+0.47 / +0.03 / +0.79 cm⁻¹ composite frequency bias at cc-pVTZ tight, research note §2.2c; halved 2026-09-10, see the note's erratum) is **measured against a
larger frozen space before anything else is decided**: the same benzene scan at thresholds one decade
tighter, frozen arm only, against the existing cc-pVTZ truth line (started 2026-09-08 17:56; note P10
records why the threshold form was chosen over the union form). The Ladder is unchanged; what the
result decides is written in the note.

**Decision 21 (closed 2026-09-08):** P11 (a) — a resolved room-temperature fundamental (Pirali et
al. 2009, item 53: sixteen naphthalene bands at 0.005 cm⁻¹ with the hot bands resolved away) is
scored with u_T = 0 plus a 0.5 cm⁻¹ head-to-origin term (labelled upper bound from the paper's
figures); other room-temperature sources keep the floor (Ladder dated note 2026-09-08; probes README
2a). **Open since the proposal cold read of 2026-09-08** ([Cold_Read_2026-09-08_Proposal.md](GoalGathering/reviews/Cold_Read_2026-09-08_Proposal.md)):
**P12** the anchor's basis-set error in the error budget (finding 4) — **accepted by the user 2026-09-08 (decision 26), form (a) + (c)**: a **basis-set line** enters the anchor licence and the per-band error budget, fed by (i) the measured cc-pVDZ → cc-pVTZ change of the canonical harmonic curvature per benzene mode, printed from the two existing truth lines (no new runs; a lower bound), (ii) the literature distance of CCSD(T)/cc-pVTZ from the basis-set limit for benzene once the reference is read (Esselman et al. 2023 on the reading list), and (iii) a canonical cc-pVQZ diagonal line at benzene (61 energies) in the cluster request, which replaces (i)–(ii) when it prints; the expected-effect line is restated as an upper bound at the anchor's level; no F12 — neither CCSD(T)-F12 nor the in-testing MP2-F12 of PySCF is usable here (checked 2026-09-08); **Input (i) printed the same evening** (note §2.2d): the canonical curvature along the three benzene modes changes by +67 / −33 / −73 cm⁻¹ from cc-pVDZ to cc-pVTZ (frequency; the first print gave the curvature change, twice this — corrected 2026-09-10), two thirds of it SCF, and full-space MP2 captures 65–109 % of the correlation part — so the next measurement is the same 27 points at DF-RHF and DF-MP2 in cc-pVQZ/5Z (cheap, planned 2026-09-09 after the naphthalene timing), and a **P18** (anchor redefined as a composite with SCF and MP2 basis corrections) is drafted for the user once it prints; **P13** R1's energy route as
B3 work or as a dated multi-week laptop job (finding 6) — **deferred by the user on 2026-09-08 until
one naphthalene LNO-CCSD(T)/cc-pVTZ energy has been timed** (planned 2026-09-09, after the xtight
run; needs a quick DFT geometry first, the naphthalene dry run not having run); **P14** the benzene
rehearsal rerun under the symmetry prior (finding 15) — **accepted by the user 2026-09-08 (decision 22) — run 2026-09-10** (`dryrun_symmetry_prior.py`, from the cached stage-B responses, no new DFT energy): all 30 benzene modes assigned in D₆h (2a1g, a2g, a2u, 2b1u, 2b2g, 2b2u, e1g, 3e1u, 4e2g, 2e2u; the accidental a1g/b1u near-degeneracy at 1020 cm⁻¹ handled as a mixed block), **57 free off-diagonal elements of 435** (11 within degenerate pairs; 12 with a two-mode pattern in the 200 cm⁻¹ deck), **K_off = 210 energies at ρ_off ≤ 0.3 against 388 with the banded prior**, family errors equal or better (dry-run note §6); the P14 wording that follows is the plan as it stood before the run:, after the naphthalene timing; needs the deck's full-point-group irrep assignment of the DFT modes (D₆h; decision 11's wording) added to `dryrun_dft_delta_recovery.py`, then the existing benzene surrogate rerun with the prior and K_off printed against the free-element count; **P15** a null on symmetry-forbidden
couplings of the frozen-space object (finding 16) — **accepted by the user 2026-09-08 (decision 23)** — **measured 2026-09-10 in the DFT surrogate** (same script): forbidden couplings ≤ 2.0 µE_h in the direct Δ₂ and ≤ 1.6 µE_h from the two-mode responses, against 424 µE_h for the largest allowed one — zero to the Hessians' noise; the frozen-space version at benzene follows with the R0 probe batch; the wording that follows is the plan as it stood: at benzene (and naphthalene when its noise run exists) a few symmetry-forbidden pairs are fitted free from two-mode points and their magnitude is printed in the anchor's smoothness record; the prior keeps them at zero in the recovery, and the wording "exact, not assumed" becomes "exact for the canonical surface; measured for the frozen-space one"; **P16** the jet-cooled coronene bands as the
primary cold truth (finding 27) — **accepted by the user 2026-09-08 (decision 24)**: jet-cooled band primary with the FEL bandwidth as uncertainty, hot-extrapolated position a second labelled column, inconclusive only on opposite verdicts (Ladder §2 note of 2026-09-06 (iii) superseded in place; proposal §5.2; probes README 2a; bibliography); **P17** the R2 3 µm column not promised until its scoring rule
exists (finding 21) — **accepted by the user 2026-09-08 (decision 25)**: the R2 C–H accuracy claim covers the out-of-plane bands on hot gas; the 3 µm jet-cooled column is shown, not promised, until a polyad scoring rule is agreed with the source's authors (Ladder §2 dated note; proposal §5.2; Frozen Lines §5); and the calendar (finding 25) — **in the proposal §12 since 2026-09-09 (12 Sep 2026 → 21 May 2027, two scenarios, from the measured first-week pace)**. **Closures 2026-09-10** (proposal patched; closure table appended to the cold-read file): all 43 findings addressed except **P13 / finding 6** (the naphthalene R1 cost sentence now says "being measured" and is rewritten when the timing prints) and the pending inputs of **P12 / finding 4** (the QZ/5Z SCF+MP2 line and the Esselman reading; the budget row already carries the basis-set line with the measured DZ→TZ figures). Finding 22 (side-project M2 memory) was closed by ordering M2 at cc-pVDZ first with the cc-pVTZ repeat as M3's first item and a memory-only failure recorded, not killing — the one closure that changes a side-project rule without a user decision, flagged for the user. **Recheck the same day** ([Cold_Read_2026-09-10_Proposal_Recheck.md](GoalGathering/reviews/Cold_Read_2026-09-10_Proposal_Recheck.md)): 29 held, 13 partial, 1 not held, 13 new (6 major, numeric) — all closed in the text the same afternoon; the numeric ones (mode order of the cc-pVTZ bias, the 57 = 54 + 3 benzene pair count, the R1 deck of 474 energies beside K ≈ 220–380, four formulas in the anchor gate, the MNRAS letter in §14) verified against the measurement files first. **P19 (2026-09-08, from the user's statement that the large PAHs are the goal):** a pre-registered test of whether Δ₂ is transferable per band family across size (a per-family constant or one-parameter size law, leave-one-molecule-out over R0–R3 plus anthracene, winning/losing conditions against τ_F), run before any R6 probe; if a family wins, line A's library is corrected by the rule with its error bar and R6 becomes a direct check of the rule — [Research_Note_2026-09-08_P19_Transferability.md](GoalGathering/notes/Research_Note_2026-09-08_P19_Transferability.md); parked by the user on 2026-09-08 ("I am not that far yet"); **unparked and accepted 2026-09-10 = decision 27**, after the question "at which point could a professor trust this pipeline as a training-data generator" — the answer being Module 08 only with the transferability test and a calibration check in the path: Q9 in Ladder §6 (dated amendment) and §4 item 14, Goal glossary and gate list, Distilled gate table, Mapping M08 product, proposal §6/§10/§12 (pre-registration 15 Jan 2027; evaluation with R2/R3). The product sentence for the large PAHs follows the note's §5 (corrected line-A library with LOMO error bars for winning families; the R6 flake as the check).

**Decision 28 (closed 2026-09-08, P20 — the criterion per rung, user's statement: benzene is a tool,
not a goal; "beating" existing benzene values is not what is taken to the supervisor):**
**R0 (benzene) is an agreement rung**: for every scored band, |predicted − laboratory| must lie
within the laboratory band uncertainty combined with the pipeline's own error budget (noise,
freezing bias, basis-set line, locality); the same for the R0 intensities of decision 18 against
the source's stated intensity uncertainty. Passing licenses the anchor and the recovery; failing
means the budget is incomplete and nothing moves up the ladder. The comparison with the opponents
is still printed at R0 but is not a claim. **R1 (naphthalene) does both**: agreement required (the
local-CC licence rung), and per family a reported answer to whether the coupled-cluster correction
adds accuracy over DFT, on the PNNL column and Pirali's resolved fundamentals (decision 21).
**R2–R3**: "beat" per family where the laboratory can decide it, as before. **R4–R6**: P19's
transferred rule, if it passes, checked on one large PAH. The word "beat" leaves §1 of the proposal
and every benzene sentence; the proposal opens with the question — can a measured coupled-cluster
correction, licensed where the truth is known, mean anything for the PAHs where none exists.
**Written 2026-09-09** (commit 5c1bafb): Ladder §1 amendment and the R0/R1 rows, Goal, proposal §1, §5.2, §7 rows and terms, Mapping M08, Distilled plan.

**Decision 29 (closed 2026-09-10, P21 — the temperature term at R0/R1, user: "advies overgenomen"):**
on the room-temperature licence rungs u_T is the pipeline's own computed 0 → T_source shift per
scored band from the DFT anharmonic constants (Σ_k X_ik n̄_k), applied as a correction with ±30 % of
itself as its uncertainty, in place of the 2.55 cm⁻¹ floor the Bose rule with the floor slope gives
at benzene; pre-registered, printed by probe 2a before any CC number; floor printed and labelled until
the X_ik exist (Ladder §2 dated note 2026-09-10; scoreboard note §3; probes README 2a).

**Decision 30 (closed 2026-09-10, P22 — which scale factors are line A):** the PAHdb theoretical
library **as served** (its v3.00 factors 0.9794 / 0.9691 / 0.9597, the file every user receives) is
line A; the column at the v4.00 paper's refit (0.964 / 0.979 / 0.975) is printed beside it, labelled,
and claims nothing (Frozen_Lines §2 dated note; atlas note §2; Module 02 report §5).

**Decision 31 (closed 2026-09-10, P23 — calibration of the error budget, Q10):** for every scored
band on R0–R3 the pipeline prints whether the laboratory value lies inside k·u_total (k = 1, 2) and
reports the coverage per rung, family and overall against 68 % / 95 %; pass thresholds fixed in the
pilot note (Ladder §4 item 15); a short budget is declared incomplete and its deficit reported, never
widened. Reason: for training labels the error bars must be true, not just the errors small.

**Decision 32 (2026-09-12 — the network as named stand-out work, outside the sequence):** a model
trained on the pipeline's own Δ₂ blocks and certified bands is named as the project's stand-out
ambition, placed outside the module sequence (which still ends at Module 09; rubrics v1.5.1 carry no
stand-out criterion), gated by the measured range at R2–R3 and the Q10 coverage table, with its
losing condition pre-written (proposal §6; mapping "After Module 09"; Goal dated note).

**Decision 33 (2026-09-12, P18 — the anchor as a composite with basis corrections):** the anchor
energy per point is E_LNO-CCSD(T)(xtight, TZ) + [MP2(full) − MP2(LNO)] at TZ + [MP2/QZ − MP2/TZ] +
[SCF/5Z − SCF/TZ], every term a difference of computed energies at one geometry, no fitted parameter,
under 1 % of an LNO point in cost (DF-MP2/QZ 9 s, DF-RHF/5Z 35 s per benzene point). Named by the
cheap basis line printed the same day (TZ → QZ/5Z change of 1–8 cm⁻¹ on the probed modes, against a
frozen-space bias of 0.1–0.2 cm⁻¹ at xtight); the licence comparison is unaffected because the basis
terms are common to arm and canonical reference; the CCSD(T)−MP2 remainder's basis change stays the
open term of decision 26. Ladder §3 words added; measured effect on benzene's three probed harmonic
frequencies from the two basis terms: +2.8 / −5.2 / −11.1 cm⁻¹ (CH-oop, CH-ip-bend, C–C stretch;
sum of the TZ → 5Z SCF and TZ → QZ MP2 rows of `results_m1/BASIS_LINE_scf_mp2.md`).

**Decision 34 (2026-09-12, P24 accepted — substitution probing pre-registered as a second measurement layer):**
plan 06's triangular-substitution scheme (Powell & Toint 1979 as characterised by Coleman & Moré 1984; verified on the
benzene dry-run tensor: 6 products, exact recovery, noise magnification 1.4–1.5× in band positions) enters plan 05 as
two pre-registered items of the R0 pilot and nothing else: (1) one Hessian–vector product along one colour-class vector
of the stored X1c colouring, measured in the frozen-space arm at the reference geometry the cheapest way the engine
then has (energies, 4 points per component, if M2 has not licensed gradients; two gradients if it has), printing its
cost in energies and the noise of its components against σ_E; (2) on the R0 pilot deck, Δ₂ reconstructed from the six
products beside the deck's Δ₂, compared in band positions. **Winning condition:** agreement within the R0 noise budget
*and* fewer energies than the deck; **losing condition:** either fails. Honest cost table: with energies only a
second-order product costs ≈ 4M, so 6 products ≈ 720 energies > K = 448 — the layer pays only with gradients (side
project M2, then 12·g energy-equivalents). Success adds a per-rung licensed second layer beside the deck by a dated
Ladder note; failure closes S5 for plan 05 at the energies-only level. No change to the deck, the licence tests, the
tolerances or the calendar (`GoalGathering/notes/Research_Note_2026-09-12_P24_Substitution_Probing.md`).

**Decision 35 (2026-09-12 — how the R1 smoothness σ of pilot prerequisite (f) is measured):** at the anchor's xtight
thresholds a 27-point M1 scan at naphthalene is ≈ 50 laptop-days (tonight's timing: ≈ 2 days per energy), so the
prerequisite is met by **σ at tight thresholds, 9 points, one mode** (the mode family with the largest σ at benzene,
the C–C stretch), launched right after the naphthalene timing on the checkpointed chain, ≈ 4–5 days at 11.5 h per
energy; σ(tight) stands in for σ(xtight) with a label, justified by benzene, where σ did not change between the two
(0.003–0.044 µE_h at both) while the bias did — and the bias is not a pilot input. It requires the naphthalene DFT
dry run first (prerequisite (a); hours of psi4) and `m1_frozen_spaces.py` taking `--molecule`. σ(xtight) at R1 is
re-measured on the first machine that can afford it (P13) and the pilot note's item 8 is re-read then if it differs.
Ladder item 8 reads c "at the σ_E the R1 smoothness probe printed"; this note names which probe that is
(`GoalGathering/notes/Pilot_Note_Skeleton_2026-09-12.md` §D, option 1).

## Dated notes after the freeze

- **2026-09-12 (evening) — decisions 34 and 35, the compute-route memo, the pilot-note skeleton, engine layer 3, the
  software ledger.** *Decision 34* accepts P24 (`notes/Research_Note_2026-09-12_P24_Substitution_Probing.md`): plan 06's
  substitution probing enters the R0 pilot as one measured Hessian–vector product and one pre-registered six-products-vs-deck
  comparison, honestly priced (energies only ≈ 720 > K = 448; pays only with the side project's gradients). *Decision 35*
  fixes how the R1 smoothness σ is measured (tight thresholds, 9 points, one mode, ≈ 4.8 laptop-days) after tonight's
  timing put a 27-point xtight scan at ≈ 50 laptop-days. *P13 memo* (`notes/Decision_Memo_2026-09-12_P13_Compute_Route.md`):
  the routes repriced at xtight — laptop 1.3–3 years, desktop 4–16 months, Snellius weeks and 200,000–660,000 SBU for the
  474-energy R1 deck; recommendation to split the decision (cluster request in October; desktop after two more facts); not
  decided. *Pilot-note skeleton* (`notes/Pilot_Note_Skeleton_2026-09-12.md`): the fifteen items of Ladder §4 with the
  measured inputs filled in and the user's choices collected. *Engine layer 3* (`probes/lno_checkpoint.py`): per-fragment
  checkpointing for LNO-CCSD(T), tested exact on benzene, after the xtight naphthalene timing was lost at 16:14 to host memory
  exhaustion caused by a Windows-side Lean build (rule since: nothing above ≈ 1 GB beside an anchor job); the timing was
  relaunched at 16:50 with it; the same layer is wired into `m1_frozen_spaces.py` (built, untested). *Q10 script*
  (`probes/q10_coverage.py`) pre-registered with a 47-row readiness table; *item 50* read (SRD 35 documents no measurement
  temperature; the 250 °C is a labelled assumption). *Software_Changes_Ledger.md* opened in `notes/` on the user's request.
  Plan 06 the same day: X1b–X1d, X5, T1a–T1c proved in Lean, Coleman & Moré 1984 read, S1/S3 reading notes, conjecture T3.
- **2026-09-12 — three modules scaffolded in the Udacity rubric form, Hessian QM9 in, plan 06 opened, GoalGathering
  reorganised.** *Module 03* (`modules/03_lab_scoreboard/`, commits 5d946d2 → efb2c41): a pre-registered
  matrix–gas test committed before the join; 63 primary pairs of naphthalene, anthracene, pyrene and chrysene against
  the WebBook GC-IRD records; six families reject a zero offset (median +3.3 to +5.9 cm⁻¹, matrix above hot gas), two
  inconclusive by construction; Ladder dated note. *Module 04* (`modules/04_calibrated_harmonic/`, 4dfdb50): recipe
  committed before training; 2,477 matrix↔computed pairs of 83 molecules; leave-one-molecule-out MAE 6.49 cm⁻¹ as
  served vs 6.40 best, R² ≤ 0.01 — the calibrated baseline is line A on this table. *Module 05*
  (`modules/05_support_predictor/`, 260dc16 → 0e1e4c7): recipe, PyTorch SupportTransformer, smoke test; **Hessian QM9
  downloaded with the user's permission and verified** (41,645 molecules; only 66 with an all-carbon aromatic
  six-ring, 6,055 with a planar conjugated ring — the "aromatic-heavy subset" is really a conjugated one; mapping
  dated note); **corpus factory** prepared, not run (layers A 45 / A′ 868 / B 4,353 / C 6,055; start-stop queue,
  refuses to run beside an anchor job; the user adopted the own layers as the candidate). *Plan 06*
  (`plans/06_equivalent-faster-mathematics/`, idea plan beside 05, not a successor): orientation, X0 reading note
  (QMA-hardness closes general E1; class-restricted E1/E2 open), X1/X2 on the benzene tensor (6 of 435 off-diagonal
  pairs move a position > 0.5 cm⁻¹; S4 alive, S5 parked), Uitleg. *Housekeeping:* GoalGathering split into top level /
  `notes/` / `reviews/` with every link rewritten (b6c89ed); QZ/5Z line and the xtight read-in script prepared;
  cover-note draft for the supervisor. **Decision 20 closed at 11:48:** the xtight arm-A rescan (27 points)
  brings the composite frequency bias from +0.47 / +0.03 / +0.79 to **+0.11 / −0.01 / +0.23 cm⁻¹** with
  the smoothness unchanged — the residual at tight was local-correlation truncation; the anchor runs at
  the tighter thresholds, cost factor ≈ 2 at benzene, the naphthalene xtight timing owed (Budget dated
  note; proposal §3.3, §10 item 20, §11; M1 note). QZ/5Z SCF+MP2 line launched 11:54. Decision 32 the
  same day (the network as named stand-out work outside the sequence). Next: plan-06 X3b, proposal to
  the supervisor in the afternoon.
- **2026-09-11 05:15 — naphthalene timing printed** (`probes/results_timing/naphthalene_cc-pvtz_tight.json`): one
  LNO-CCSD(T)/cc-pVTZ tight energy = 41,375 s (11.5 h), 24 fragments, peak RSS 19.83 GB against the 22 GB ceiling; the
  R1 deck of 474 energies is 5,450 laptop-hours; P13 (cluster / desktop / both) is now decidable and the proposal's
  §8 and §13 item 5 say so; pyrene will not fit this laptop. Tight LNO kept 92–100 % of the active occupied and ≈ 56 %
  of the virtual orbitals per fragment (plan-06 X3a).
- **2026-09-11 — R1 Pirali column printed (Module 03).** Probe 2a gained a transcribed-table mode; Pirali
  2009's Table 1 (sixteen naphthalene fundamentals, 300 K, 0.005 cm⁻¹, Q-branch heads) is transcribed in
  `probes/scoreboards/naphthalene/pirali2009_table1.json` and scored under decision 21: u_band
  0.50–0.71 cm⁻¹ per band, u_T = 0, no intensities; ν45's table/text discrepancy (959.04 / 959.5) flagged.
  Cold-read closures 4 and 6 updated with the naphthalene timing.

- **2026-09-10 (evening) — prior art read; the two-sentence statement in the proposal.** §1 of the
  proposal now carries the two sentences for the supervisor (what is new; on whose shoulders). Read in
  full: Käser et al. 2021 (transfer learning to CCSD(T): 262–632 CC points with gradients on 7–9-atom
  molecules, no aromatic) and Lam et al. 2020 (QM//ML anharmonic corrections, 37 molecules incl. benzene
  and naphthalene, RMSD 21 cm⁻¹, harmonic part at DFT). Crossref-verified but closed (AIP/ACS 403):
  Mata & Werner 2006, Russ & Crawford 2004, Subotnik & Head-Gordon 2005, Esselman 2023 — asked of the
  supervisor (PDF request D, items 24–27); Nagy & Kállay 2019 abstract read, PDF for the user (item 28);
  the three DLPNO method papers' records verified (item 17). Novelty table and reference list updated.

- **2026-09-10 — the R0 scoreboard printed (Module 03 begun early, while the naphthalene timing
  runs).** `probes/m03_band_uncertainty.py` on the NIST QUANT-IR benzene record at 1.929 cm⁻¹:
  peaks 672.86 / 1036.54 / 1481.93 / 3046.39 cm⁻¹, u_band 3.2 cm⁻¹ on every family (of which
  u_296 = 2.55 by the frozen Bose rule with the floor slope — **P21** proposes the pipeline's own
  computed 296 K correction with ±30 % instead), intensities 104.6 / 8.2 / 15.7 (non-certified) /
  74.2 km/mol. Note: [Research_Note_2026-09-10_Scoreboard_R0.md](GoalGathering/notes/Research_Note_2026-09-10_Scoreboard_R0.md).
  The 0.125 cm⁻¹ boxcar record (WebBook Index 7) was fetched the same evening with the user's
  permission and printed too: peaks 673.90 / 1037.73 / 1483.41 / 3047.17, u_band 2.55 (the temperature
  term alone; 0.125 without it), intensities agreeing with the 1.929 record to ≤ 1.3 %. No frozen rule
  changed.
- **2026-09-10 — Module 02 begun (opponent atlas), while the timing runs.** `modules/02_opponent_atlas/`:
  parser `build_opponent_atlas.py` for the PAHdb XML libraries (schema read from the AmesPAHdbPythonSuite
  parser and its cut-down test file; tested on a synthetic two-species fixture), README with the
  sources and how each is obtained. The PAHdb files (theoretical 4.00, anharmonic 1.00, experimental
  3.10) come through the site's form — e-mail address plus citation agreement — which the user fills;
  the Mai 2025 spectra are a 102 MB Zenodo archive (CC BY-NC-SA); Bos 2025's ML-scaled spectra are
  in ACS Supporting Information. **Bos 2025 re-read** (Europe PMC, debt 1 paid): MAE 5.07 / max
  13.17 cm⁻¹ against 10.41 / 23.49 for conventional scaling, on Ar-matrix bands with an instance-level
  80/20 split (Frozen_Lines §3). Mai 2025's data record read (B3LYP/4-31G teacher; 50/300/600 K).
  **Same evening, files in hand:** all three libraries parsed —
  [Research_Note_2026-09-10_Opponent_Atlas.md](GoalGathering/notes/Research_Note_2026-09-10_Opponent_Atlas.md):
  line A has **no benzene**; stored scale factors 0.9794 / 0.9691 / 0.9597 (not the paper's
  0.964 / 0.979 / 0.975 — **re-read the same evening: the file carries the v3.00 factors of
  Bauschlicher 2018, the v4.00 refit is in the paper only; **P22 decided the same evening = decision 30: line A as served, paper-factor column printed and labelled**); 4-31G from n_C = 212; **debt 6 paid** (C₃₈₄H₄₈ uid 617
  neutral, 4447 dication); line B = 45 species, on the ladder benzene, naphthalene, pyrene, tetracene.
  Dated notes in Frozen_Lines §2/§3/§7 and Ladder §2. **Later the same evening:** line C (Mai 2025,
  1,705 species, positions only) and the cheap line (Bos 2025 SI, 81 species) read in; the EDA
  notebook (five figures) and `modules/02_opponent_atlas/REPORT.md` written — Module 02 is a
  complete first version fifteen days before its calendar date, pending the student's own pass.
- **2026-09-11 — Module 02 reshaped to the Udacity rubric (Rubrics/02) after reading module 01's APA
  pages.** Deliverables now named as the rubric names them: `notebook/data_workflow.ipynb` (Setup,
  Ingestion, Cleaning with two documented functions, one EDA function, five titled and labelled figures,
  Summary; the tabular dataset `species_pahdb_theoretical_4.00.csv` beside it), a short `README.md` with
  run instructions and the four reflection answers, `requirements.txt` by `pip freeze`, and
  `module_summary.docx` / `.pdf` built into the Udacity APA 7 template (stored as
  `Rubrics/APA7_template.docx`) with the prescribed sections, author–year citations, the required Danchev
  (2022) article and a References list of exactly the cited sources (records verified in Crossref).
  Project notes moved to `PROVENANCE.md`; the long-form `REPORT.md` gained the same References and an
  AI-assistance statement. Work committed on branch `module-02-opponent-atlas` and merged (the rubric
  asks for a branch beyond master).
- **2026-09-10 — engine incident and patch 1.** The naphthalene cc-pVTZ tight timing died after
  4 h 26 min on a pyscf 2.14.0 / pyscf-forge 1.1.1 signature mismatch in the DF vvvv path (taken only
  when a fragment's vvvv block does not fit in memory — benzene never took it); patched locally
  (`probes/patches/`, Compute_Budget §3), relaunched 17:45 with the LNO fragment loop logging and the
  hourly heartbeat. **Result 2026-09-11 05:15: 41,375 s = 11.5 h per naphthalene energy, 24 fragments, peak RSS 19.83 GB** (P13 input: the R1 deck of 474 energies is 5,450 laptop-hours ≈ 227 days; cluster work on the measured number). The xtight arm-A rescan (decision 20) was resumed detached at 05:16 the same morning, 22 points remaining.

- **2026-09-05 — R2/R3 gas-phase sources.** An exhaustive search
  ([Research_Note_2026-09-05_R2_GasPhase_MidIR_Sources.md](GoalGathering/notes/Research_Note_2026-09-05_R2_GasPhase_MidIR_Sources.md))
  found no room-temperature 6–15 µm gas spectrum for any R2/R3 species; it found jet-cooled band
  lists for tetracene (item 61) and coronene (item 62) and one cold pyrene band (item 63), added
  as labelled cold columns by the dated note in Ladder §2. The expected R2 C–C verdict is
  unchanged. Files touched: Ladder §2, bibliography (61–64), Frozen_Lines §5, Mapping M03,
  probes README 2a.

- **2026-09-05 — machine and software facts** (Budget §3 dated note): the plan-02 timings were
  measured on this laptop, not an older one (provenance until a plan-05 probe re-prints them);
  the laptop has psi4 1.11 in the conda environment `qc` but no pyscf, no PyTorch and no WSL, so
  probe M1 and every local-CC probe need WSL or the cluster. DFT-only work runs now.

- **2026-09-05 — the R0 dry run ran** ([Research_Note_2026-09-05_DryRun_Benzene.md](GoalGathering/notes/Research_Note_2026-09-05_DryRun_Benzene.md)):
  mode E recovers benzene's off-diagonal Δ₂ with the full deck (family errors ≤ 0.43 cm⁻¹ vs
  7 cm⁻¹ diagonal-only), mode G from 60 gradients; but the raw held-out ρ is blind to the
  off-diagonals (2.4 % of the response), the frozen stopping rule is unreachable below a model
  floor of 0.005, the large couplings are same-symmetry pairs 170–450 cm⁻¹ apart (not a frequency
  band), and mode E needs σ_E ≲ 2 µE_h for the off-diagonals — ten times stricter than the Q6
  line. **Six proposals (P1–P6) await the user's decision; no frozen rule changed.**

- **2026-09-05 — WSL and the anchor-code environment installed** (Budget §3 dated note): Ubuntu
  26.04 under WSL 2 with `~/qc05` (Python 3.12: pyscf 2.14.0, pyscf-forge 1.1.1, pyscfad 0.3.3, jax
  0.10.2); the LNO modules import; 28 GB given to WSL. Probe M1 is unblocked.

- **2026-09-05 — probe M1 ran** ([Research_Note_2026-09-05_Probe_M1.md](GoalGathering/notes/Research_Note_2026-09-05_Probe_M1.md)):
  benzene, cc-pVDZ, three modes × nine points, three arms, against a canonical CCSD(T) truth line on
  the same 27 geometries. The frozen-space object exists, round-trips (0.0000 µE_h) and **reloads**
  from file (+0.0000 µE_h). **Arm A is smooth to 0.002–0.06 µE_h where the re-selecting arms B and C
  carry 7–11 µE_h of LNO discontinuity**; its bias is a clean q² term — 5–28 cm⁻¹ on the bare
  LNO-CCSD(T) energy, **0.5–2.6 cm⁻¹ on the composite with the MP2 correction** (at tight thresholds,
  finished 2026-09-06 02:07: 0.18–0.95 bare, **0.015–0.18 cm⁻¹ composite** (halved 2026-09-10)). One implementation
  fact cost a run: the transported blocks must be semicanonicalised at the displaced geometry.
  **Proposals P7–P9 await the user; no frozen rule changed.** Also measured: a canonical CCSD(T)
  gradient costs ≈ 50 energies and 13.9 GB at cc-pVDZ (72-gradient branch B3 on this laptop); and the
  WSL VM was torn down once by host memory pressure (Budget §3 incident note: 22 GB ceiling, one
  anchor job at a time).

## Not yet done (owed, in order; rewritten 2026-09-12 evening)

**The proposal e-mail (planned Monday 14 September 08:00) is held by the user** pending the evidence ladder below;
when it goes: the user's own read of the cover note, §1, §3.3 and the repriced §12 row.

**On the machine, in this order, once the naphthalene xtight timing has finished** (one anchor job at a time; nothing
above about 1 GB on the Windows side beside it):
1. smoke-test of the checkpointed frozen-space chain (`m1_frozen_spaces.py`, benzene cc-pVDZ normal; minutes) — built
   2026-09-12, untested;
2. the Lean build of plan 06's T1d (Windows, 8 GB; a quarter of an hour, no job running);
3. the corpus factory's five-molecule timing test (`modules/05_support_predictor/corpus/run_corpus.py --max-molecules 5
   --grid-check`), then the dated note fixing the subset size;
4. plan 06's X6 (script ready since 12 September evening, `experiments/x6_pi_cas_share.py`, cc-pVDZ, minutes; the user put it first) and X7;
5. the naphthalene DFT dry run (two functionals, psi4; hours) — prerequisite (a) of the pilot note and the mode table
   Module 03 and plan 06 need; **found 12 September evening:** plan 02's `results_dft_locality/naphthalene.npz` (git `57a7910`) is a
   B3LYP/6-31G* Hessian at a geometry identical to `results_dryrun/naphthalene/geometry.json` within 5 × 10⁻⁴ bohr, so the
   B3LYP half exists and only the BHHLYP Hessian must be run (anthracene and pyrene B3LYP Hessians are in the same commit);
6. `m1_frozen_spaces.py --molecule naphthalene`, then the **R1 smoothness σ run of decision 35** (tight, 9 points, the
   C–C stretch mode; ≈ 4.8 laptop-days) — prerequisite (f) of the pilot note.

**The evidence ladder "does plan 06 make plan 05 cheaper?" (the user, 12 September evening; the Monday e-mail is
held until this is clearer):** step 1 done — item 33 read for the gradient/energy ratio g: **not printed** in the paper
(`notes/Reading_Note_2026-09-12_Item33_PySCFAD_Gradient_Cost.md`); step 2 — X1c/X1d counts on the naphthalene tensor
(after the naphthalene DFT dry run): does the products-to-deck ratio improve with size — **model form done the same evening (plan 06 X8):** no connectivity pattern is band-accurate at benzene (dropped blocks move bands 15–32 cm⁻¹; 74 of 78 Cartesian blocks needed for 0.5 cm⁻¹), so the step stays a tensor measurement, with the script and the licence rule (dropped blocks < 0.5 cm⁻¹) ready; step 3 — decision 34's item 1 in
the real engine at benzene cc-pVDZ tight (one product by energies ≈ 120 energies ≈ 6 h; the six-product reconstruction
≈ 36 h against a 22 h deck): exactness and noise in the frozen arm, not yet savings; step 4 — g measured (side project
M2, in PySCFAD, with frozen spaces at benzene cc-pVDZ, where the paper's symmetry-breaking outlier should vanish): the
only step that can show savings. Steps 2–3 fit in the machine queue below after the naphthalene items; step 4 is
software work of weeks and the user decides when. **Priced lever by lever the same evening:** plan 06's `GoalGathering/Cost_Ladder_2026-09-12_Network_Data.md` (thresholds, X10's free pair rule, substitution or full Hessians with gradients, engine levers, locality), with the order in which the missing numbers arrive.

**Decisions for the user, when their inputs are in:** P13 in two halves (the cluster request now, the desktop after
Monday's xtight factor and the corpus timing; memo in `notes/`); the pilot note's choices (skeleton §C); whether to
publish blog post 3 (draft pushed, unrendered).

**Module debts:**
- Module 02: the student's pass before 25 September; the C₃₈₄H₄₈ symmetry-unique local-environment count.
- Module 03: the PNNL naphthalene record (R1's room-temperature source; licensed, the user); the jet-cooled tetracene
  and coronene cold columns (items 61–62); R2/R3 columns; the intensities of decision 18; the ±30 % corrected form of
  the hot columns (pilot note); family labels by DFT mode vector once the naphthalene dry run exists; the student's
  pass before 2 October.
- Module 04: the Zenodo release of the training table (the user); pilot-note item 6 adopts or amends the recipe; the
  student's pass.
- Module 05: after the timing test — the corpus run itself (desktop-days), the Zenodo release of the corpus, the
  reading-2 fallback source, the notebook and report filled from the skeletons, the label threshold θ (pilot-note
  item 5).

**Other:** the PDF request to the supervisor (items 21, 24–29; 29 = Powell & Toint 1979, added 12 September); the
capstone mapping's Pass 6 (the user asked to wait; Uitleg ch. 16 is the checklist); the pilot note itself, from the
skeleton, once prerequisites (a) and (f) are met; the R0 pilot deck (after the pilot note), which now includes
decision 34's substitution items; blog post 3 when the user releases it.

## Provenance

Plan 05 is based on the research note of 2026-09-03 (item 4 above), which answered the user's
question *what single idea would make the plan-04 pipeline fast enough for super-large PAHs
without losing accuracy*. The answer — probe the local CC−DFT correction to the force constants
with a hashed pattern set instead of learning a surface — rests on published O(1)-gradient and
compressed-sensing Hessian recovery (bibliography items 23–24) and, as Round-7 Pass B
established, on the Concordant Mode Approach (items 42–43) for its diagonal part. What remains
proposed is stated in the research note's §8. The plan-04 source conversation
(`AI_Chats/grok_chat_4.md`) remains the provenance for the CC-anchor idea itself.

## What survives from plans 01–04

Method-agnostic governance, carried because each rule serves the goal: measured-not-asserted
arithmetic in `probes/`; never cite from recall; pre-registration, frozen splits with hashes,
≥3 seeds, tuning parity; declared effect size, **inconclusive is publishable**; escalation
ladders declared in advance, stopping is a result; fail-closed reporting; deviations only as
dated notes committed before the number is known. From plan 04 specifically: everything except
the learned surface.
