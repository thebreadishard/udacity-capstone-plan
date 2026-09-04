# Plan 05 — Δ-Probed IR Pipeline

**Status: draft, folder created 2026-09-03. Not complete as a plan. Nothing here is a result.**
Supersedes plan 04 (CC-Anchored IR Pipeline). All five plan folders are in the tree
(decision 2, 2026-09-04): 01–04 are superseded, read-only records; 05 is current.

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

The sequence **ends at Module 09**. There is no `Horizon/` and there are no Projects 10–12.

## Glossary

Every symbol and term is defined once in the **Goal file's glossary** (reading-order item 3):
Δ₂; local CC and frozen spaces; mode E / mode G; pattern, q_s, response; ρ, ρ\*, f_h, K, K_off,
K_cap; structural prior, learned prior, the licence; τ, τ₇, d₇, r_c, r_max, ε₈, η₈, γ, σ_E, σ_g;
gates Q0–Q8 and P0–P5; rungs and claim types; budgets B1–B3; milestones M1–M5; reading 1 / 2;
the pilot note and the dated notes; CMA, CMA-0, CMA-2; GVPT2, MD-ACF, QFF, CPS, PNO/LNO. Read it
before anything else.

## Reading order

1. This file — orientation. **Draft, not complete.**
2. [GoalGathering/Why_05_Supersedes_04.md](GoalGathering/Why_05_Supersedes_04.md) — every
   change relative to plan 04, in one table (33 rows)
3. [GoalGathering/Overarching_Goal.md](GoalGathering/Overarching_Goal.md) — glossary (Δ₂, R_s, R_a, K, ρ\*, ρ\*_common, u_band, the fragment licence and every other
   symbol), prime directive, the two 2026-09-04 directives, the decision record
4. [GoalGathering/Research_Note_2026-09-03_Delta_Probing.md](GoalGathering/Research_Note_2026-09-03_Delta_Probing.md)
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
11. [GoalGathering/Capstone_Mapping.md](GoalGathering/Capstone_Mapping.md) — modules 02–09
    against Rubrics v1.5.1; Pass 6 (sign-off) not done
12. [GoalGathering/Project_Proposal_2026-09-03.md](GoalGathering/Project_Proposal_2026-09-03.md)
    — the supervisor proposal: the *why* of the major decisions, the review status, and what
    was decided by whom
13. [GoalGathering/Side_Project_2026-09-04_ModeG_Gradients.md](GoalGathering/Side_Project_2026-09-04_ModeG_Gradients.md)
    — the pre-registered side project that builds frozen-space local-CC gradients (mode G):
    milestones M2–M5, kill criterion, budget bucket, what changes on success or failure

## Review record

- **Round 7, Pass A** (cold read, 2026-09-03, fresh context):
  [Professor_Review_2026-09-03_Round7_PassA.md](GoalGathering/Professor_Review_2026-09-03_Round7_PassA.md)
  — not sound enough for Pass B until patched; 10 blocking + 11 non-blocking; **all 21
  addressed in spec the same day**. Brief: [Review_Brief_2026-09-03_Round7_PassA.md](GoalGathering/Review_Brief_2026-09-03_Round7_PassA.md).
- **Round 7, Pass B** (adversarial domain, 2026-09-03, fresh context, literature verified):
  [Professor_Review_2026-09-03_Round7_PassB.md](GoalGathering/Professor_Review_2026-09-03_Round7_PassB.md)
  — **conditional**: green light for the R0–R1 measurement programme once six blocking items
  were written in; no green light for the promised set *as then worded*. **All six written in
  the same day** (Q6 thresholds; banded prior; Δ₃/Δ₄ out; CMA cited; cost question re-anchored;
  Q8 on direct blocks) and non-blocking 7–13. Brief: [Review_Brief_2026-09-03_Round7_PassB.md](GoalGathering/Review_Brief_2026-09-03_Round7_PassB.md).
- **2026-09-04, user decisions 1–6 and two directives** (Goal, "Decisions of 2026-09-04";
  "The goal binds"; "Inheritance is not authority"); the side project opened.
- **Round 8, Pass A** (cold read of the patched set, 2026-09-04, fresh context):
  [Professor_Review_2026-09-04_Round8_PassA.md](GoalGathering/Professor_Review_2026-09-04_Round8_PassA.md)
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
  [Review_Brief_2026-09-04_Round8_PassA.md](GoalGathering/Review_Brief_2026-09-04_Round8_PassA.md).
- **Round 8, Pass B** (re-assessment, 2026-09-04, fresh context, literature and code verified):
  [Professor_Review_2026-09-04_Round8_PassB.md](GoalGathering/Professor_Review_2026-09-04_Round8_PassB.md)
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
  quietness stated. Brief: [Review_Brief_2026-09-04_Round8_PassB.md](GoalGathering/Review_Brief_2026-09-04_Round8_PassB.md).

- **Round 9, Pass A** (2026-09-04; cold read of the Round-8 Pass B patches, no web):
  [Professor_Review_2026-09-04_Round9_PassA.md](GoalGathering/Professor_Review_2026-09-04_Round9_PassA.md)
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
  Brief: [Review_Brief_2026-09-04_Round9_PassA.md](GoalGathering/Review_Brief_2026-09-04_Round9_PassA.md).
- **Round 9, Pass B** (2026-09-04; hostile domain re-examination, with web):
  [Professor_Review_2026-09-04_Round9_PassB.md](GoalGathering/Professor_Review_2026-09-04_Round9_PassB.md)
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
  Brief: [Review_Brief_2026-09-04_Round9_PassB.md](GoalGathering/Review_Brief_2026-09-04_Round9_PassB.md).

- **Round 10, Pass A** (2026-09-04; cold read of the Round-9 Pass B patches, no web):
  [Professor_Review_2026-09-04_Round10_PassA.md](GoalGathering/Professor_Review_2026-09-04_Round10_PassA.md)
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
  Brief: [Review_Brief_2026-09-04_Round10_PassA.md](GoalGathering/Review_Brief_2026-09-04_Round10_PassA.md).
- **Round 10, Pass B** (2026-09-04; hostile domain re-examination, with web):
  [Professor_Review_2026-09-04_Round10_PassB.md](GoalGathering/Professor_Review_2026-09-04_Round10_PassB.md)
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
  Brief: [Review_Brief_2026-09-04_Round10_PassB.md](GoalGathering/Review_Brief_2026-09-04_Round10_PassB.md).

Plan 04's Round-6 findings and their closures bind plan 05 and are not re-litigated.

## Decisions

Decisions 1–6 of 2026-09-04 are closed and recorded in the Goal ("Decisions of
2026-09-04"): 1 fragment probing as a method under the fragment licence; 2 all plan folders
stay; 3 the R2 re-read stands; 4 Module 05 adopted; 5 the promised set — Δ₂ only, mode E
guaranteed, mode G built in the side project; 6 the B2 laptop named.

**Decision 7 (closed 2026-09-04):** nothing has been submitted to the school; the draft
Foundations project on QM9 in the user's GitHub account was never submitted and will be renamed
or archived to make room for the plan's Module 02. M02 is a plan, not a record; M05's Hessian-QM9
corpus carries no module-02 reuse exposure (Goal, decision 7). **No decision is open.**

## Not yet done (owed, in order)

- **Round 11** (optional, the user's call): a cold read of the Round-10 Pass B patches (the
  per-energy noise injection, the c₀ identification, the Δ₁ geometry term, the PNNL source, the
  A/B/C arms touched the Goal, Ladder, Distilled plan, Budget, probes README and bibliography).
- **The first paid literature debts**: items 52–53 (hot-band slopes), 56–57 and 59 (the R0 and R1
  source conditions), 60 — read before M03 prints u_band.
- **The first paid literature debt**: items 52–53 (PAH hot-band shift rates) read before M03
  prints u_band.
- Capstone mapping Pass 6 (module-by-module sign-off).
- **Probe M1** (frozen LNO spaces reproduce the reference energy) — the first code of the
  project, main-project work.
- **The pilot note** (after the R0 pilot, the two-mode zero-CC dry run with its
  noise-injection column, M03's u_band table, the canonical feasibility probe, the gradient
  run/no-run at equilibrium, probe M1 and the R1 smoothness probe's σ with fits sealed; before
  any local-CC Δ₂ number is readable): band lists with decidability verdicts, margins and the
  expected-effect line, P-gate numbers, matrix tolerance, P3 effect size, M04 recipe, resonance
  route and the depth-one family set, the stopping constant c and K_cap per mode, f_h and seed,
  τ₇ and d₇, Q8 numbers (r_max, ε₈, η₈, γ, h) and direct-coupling pairs, Q6 numbers and the
  pattern amplitude.

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
