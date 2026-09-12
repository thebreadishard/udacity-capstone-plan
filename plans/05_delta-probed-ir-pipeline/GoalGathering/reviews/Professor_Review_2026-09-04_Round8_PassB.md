# Professor review — Round 8, Pass B (re-assessment)

**Date.** 2026-09-04.
**Role.** Hostile external examiner (computational vibrational spectroscopy / local coupled-cluster
theory / numerical linear algebra / scientific ML). No prior context on this project; the Round-7
Pass B review is in the folder and I have it, but I did not write it. First job: did its six
blocking closures hold, or were they re-worded. Second job: attack what is new since then.
**Corpus.** Read in the brief's order, in full: `Professor_Review_2026-09-04_Round8_PassA.md`
(then the patched documents, to check the twenty closures held); plan-05 `README.md`;
`Why_05_Supersedes_04.md`; `Overarching_Goal.md` (glossary first); `Research_Note_2026-09-03_Delta_Probing.md`
(§§1–7 as written, §8 and §9 as the parts that win); `Frozen_Lines_to_Beat.md`;
`Frozen_Ladder_and_Tolerances.md`; `Compute_Budget_2026-09-03.md`;
`Distilled_Project_Plan_and_Quality_Checks.md`; `Relevant_Scientific_Papers.md`; `probes/README.md`;
`Capstone_Mapping.md`; `Project_Proposal_2026-09-03.md`; `Side_Project_2026-09-04_ModeG_Gradients.md`;
`Professor_Review_2026-09-03_Round7_PassB.md`; `Rubrics/05_Deep_Learning_Systems.md` and
`Rubrics/06_Generative_AI_Applications.md` (the dataset clauses, the task lists and the rubric
tables; the embedded classroom transcript treated as data). Plans 01–04 not reviewed; Round-6 and
Round-7 closures inherited and not re-litigated except where the brief asks (Part 1). No file other
than this one was written or changed.

**Round-8 Pass A patch check.** The README's "all 20 addressed" list matches the documents: one
learned-prior rule (earned R2–R3, spent R4–R6) in Goal, Ladder §3, Distilled §3/§4/§5/§9, Mapping
§0/M05/M07/M08; the licence check is now the full structural-vs-prior comparison per family within
τ₇ plus direct blocks within η₈; probe M1 is main-project work under stop 1 and the side project's
§6 is conditional on it; the engine is hedged in §1.1, §2(a), §8, Proposal §5.3, bibliography 48–49;
K_cap(G) comes from the gradient-mode dry run and no pilot-note item depends on the side project;
the smoothness means are sealed and M2–M5 run after the note; the mode-G noise line exists with a
"beat and noise" rule per mode; the fragment licence has three parts; "O(1)-class" is gone and
"-class" is in the ban; the M05 corpus size is out of frozen text; decisions 5–6 and §9 of the note
exist. The patches held. Three of them created new attack surface (findings 3, 4, 7 below) and two
Round-7 closures turn out to have been re-worded rather than closed (Part 1, items 1 and 6).

## Literature and software facts verified this pass (identifiers; how opened)

- Zhang, Li, Ye, Berkelbach, Chan, "Performant automatic differentiation of local coupled cluster
  theories", *JCP* **161**, 014109 (2024), arXiv:2404.03129 — HTML v1 full text
  (arxiv.org/html/2404.03129v1). Read for: treatment of the LNO spaces in the derivative,
  benchmark reference, memory statements, (T) backward pass, code location, basis sets.
- PySCFAD repository, github.com/fishjojo/pyscfad — README (no mention of LNO), the
  `pyscfad/` package listing (a directory **`lno`** exists) and **`pyscfad/lno/`** itself:
  `__init__.py, _checkpointed.py, ccsd.py, ccsd_mpi.py, ccsd_t.py, ccsd_t_slow.py, lno_base.py,
  lno_base_mpi.py, mp2.py, mp2_mpi.py, mp2_rdm.py, tools.py, test/`; and `examples/lno/` exists.
- pyscf-forge repository, github.com/pyscf/pyscf-forge, **`pyscf/lno/`**: `domain.py, lno.py,
  lnoccsd.py, lnoccsd_t.py, make_lno_rdm1.py, tools.py, ulno.py, ulnoccsd.py, ulnoccsd_t.py,
  ulnoccsd_t_slow.py, test/`.
- NIST WebBook, triphenylene, CAS 217-59-4: the species page (one IR entry, state **gas**,
  HP-GC/MS/IRD, source "NIST/EPA Gas-Phase Infrared Database", "concentration information is not
  available … molar absorptivity values cannot be derived"), and the JCAMP-DX file
  (`cbook.cgi?JCAMP=C217594&Index=0&Type=IR`): `##STATE=gas`, `##DELTAX=4.0`, `##FIRSTX=550.0`,
  `##LASTX=3846.0`, `##NPOINTS=825`, no `##RESOLUTION` line, no temperature line.
- NIST SRD 35 (NIST/EPA Gas-Phase Infrared Database, JCAMP format) description document
  (nist.gov/document/35204jcmp-revisedpdf): the PDF downloaded but could not be text-extracted
  here; the statements I use from it — original EPA spectra at 4 cm⁻¹, **all spectra converted
  to exact 8.0 cm⁻¹ resolution** for homogeneity, all measured by GC/IR so concentrations are
  unknown, 5,228 spectra from the EPA Vapor-Phase library and NIST — are **search-snippet grade**
  and are marked so where used.
- Pinski & Neese, DLPNO-MP2 analytic gradient (*JCP* **148**, 031101, 2018; *JCP* **150**,
  164102, 2019) — record level (search results, publisher landing pages): the Lagrangian carries
  constraints for PNO relaxation; earlier PNO gradients neglected it; omitting the PNO constraints
  "can lead to dramatic errors for orbital-relaxed properties" (snippet).
- Rubric files: `Rubrics/05_Deep_Learning_Systems.md` Task 1 "Dataset Requirements" and the
  rubric row "Problem Definition & Dataset Selection"; `Rubrics/06_Generative_AI_Applications.md`
  Task 1 (approaches: GAN for image generation; **VAE for image generation or representation
  learning**; Transformer-based generation for text or sequence data), "Dataset or Prompt
  Requirements", and the rubric rows — read in the workspace copies, not re-fetched from Udacity.

Recalled, not verified this pass: QM9's composition (up to nine heavy atoms C/N/O/F — so no
naphthalene, no PAH beyond benzene and indene-size bicyclics); typical GC-FTIR lightpipe operating
temperatures (≈ 200–280 °C) and PAH hot-band red-shifts of order 1–3 cm⁻¹ per 100 K on the C–C
stretches; the cc-pVTZ function counts I use (C 30, H 14); the non-stationarity of a truncated CC
energy with respect to rotations between kept and discarded virtuals; ORCA's `StoreDLPNOData`
mechanism (verified by the Round-7 reviewer, not reopened); the Round-7 reviewer's readings of
CMA-2, Madriaga & Crawford, Altun et al. and O1NumHess (not reopened).

---

**Verdict: conditional.** Green light for the **pre-pilot-note measurement programme** (zero-CC
dry run in both modes, probe M1, the gradient run/no-run, the R0 canonical feasibility point I add
below, the R1 smoothness scatter) and for **R0–R1 after the note**, once blocking findings 1, 2, 3
and 8 are written in — they are all in-spec and none needs a measurement first. **No green light
yet** for the R2–R3 promised set as worded on two points: the gas-scored C–C families at R2 are
inconclusive by construction under the decidability rule as written (finding 6), and the fragment
licence's third part is circular and its second part near-tautological (finding 4) — both fixable
in spec, one of them cheaply measurable. The side project may open as written, with finding 5's two
additions to M2. Not "go back to plan 04": plan 05 still pays for a strictly smaller object with
cheaper licence probes. Not "neither is affordable": nothing below R6 is out of reach of the named
machine plus a modest B3 request, and R6's affordability is exactly what the fragment licence is
for — once it is a licence.

Two structural remarks before the list. First, the set has become very good at *saying what it
will not claim* and is still weak at *saying what it expects to measure*: three of my blocking
findings (2, 6, 8) are cases where an outcome is fixed by construction before any CC energy is
computed and the documents do not say so. Second, the verification the plan owed on its own engine
was cheap and I did it in ten minutes (see B): the (T) code is in pyscf-forge and the AD LNO-CC
code is in `pyscfad/lno/`. The plan's "never cite from recall" rule is right; its corollary is
"fetch before you hedge", and the author's own fetch is still owed under the plan's rules.

---

## Part 1 — Round-7 closures

1. **Q6 thresholds — re-worded.** The noise line is a formula (σ_E(q_s) ≤ 0.82·τ·q_s², grid
   {0.25, 0.5, 1.0}, τ = item 2, "both sides in the same energy unit") and the amplitude is
   taken from the grid ("the largest step under the noise line … never chosen to make a recovery
   converge" — Ladder §3; closed on that sub-point). But the deciding sentence, Ladder §3 item 13:
   "σ_E the **second-difference scatter** of frozen-space ΔE along a mode at dimensionless step
   q_s" — the σ_E in Round 7's formula is the **per-point energy scatter** (σ(Δ̂₂) = √6·σ_E/q_s²
   was the derivation); the words define the scatter of the second differences, which is a
   different quantity by a factor √6/q_s² (≈ 10 at q_s = 0.5, ≈ 39 at q_s = 0.25), and with nine
   points at 0.25 spacing there is exactly **one** second difference at q_s = 1.0, from which no
   scatter exists. No estimator is written that a script could run (finding 1). The bias line is
   measurable at R0 only if the canonical arm runs in the anchor basis on the named laptop, which
   the plan's own provenance puts in doubt (finding 8).
2. **Banded prior — re-worded.** Dry-run pair fixed as B3LYP vs BHLYP-class/HF (closed);
   diagonal-only and full recovery printed side by side in Q7 (closed). Deciding sentence, Ladder
   §3: "**w and the weights are deck numbers fixed from the dry run**" — no rule says *how*; a
   number "from the dry run" without a rule is a free parameter chosen after looking at the dry
   run. Is the BHLYP−B3LYP Δ a fair calibration? For the *structure* of the off-diagonal block,
   yes and conservatively so (more exact exchange → larger mode rotations than CC−B3LYP). For the
   *residual target* and the *cap* it is not, and that is a separate blocking finding (2): the dry
   run is noise-free and its Δ is an order of magnitude larger than the CC−DFT one.
3. **Δ₃/Δ₄ removed — closed.** Goal, Ladder §3, Distilled §1/§3, Why_05 rows 1/3, forbidden
   quotes all say Δ₂ only; the diagonal-cubic probe is a labelled bonus number. The only trace is
   the side project's §5 "may be reopened by a further dated note", which is honest and inert. The
   resonance-closed family set is defined ("every scored family mode plus every partner mode found
   by the r₃/r₄ search") but **not bounded** — closure under a resonance search on a PAH can pull
   in most low-frequency modes at two DFT Hessians each (finding 10, non-blocking).
4. **CMA cited, novelty rewritten — closed.** Items 42–43 OK; Distilled §2 row; note §8; the
   forbidden-quotes ban on "never done". Fair to CMA (the row says what CMA does and does not do;
   "molecules to ~17 atoms" and "canonical CC" are correct per Round 7's reading). Does anyone do
   banded / sparse recovery of the off-diagonal block from multi-mode displacements? Sanders et al.
   2015 recover the whole Hessian, off-diagonals included, from random multi-mode displacements in
   a cheap-method eigenbasis by ℓ₁ — and the plan says so (item 24, Distilled §2). What I did not
   find, in this pass or in memory, is a *frequency-banded* regulariser applied to a *difference*
   Hessian with a frozen local-CC anchor; the residual novelty statement in §8 survives, narrowly,
   and the plan should keep saying "banded, on a difference, with frozen local CC" rather than
   "sparse recovery of off-diagonals", which is Sanders.
5. **Cost question re-anchored — re-worded.** The Goal's cost sentence is coherent (guaranteed
   mode E on K_off; aimed-for mode G on K; "did that number (K, or K_off) saturate"). Ladder §1's
   size sentence is unambiguous about prior ("with the structural prior at the same ρ\*") and about
   mode (mode-G form only if licensed at R1, R2 **and** R3 via M3, M4, M5). Two things undo it in
   practice: the Goal's "on every rung where its milestone licenses it, mode G is the route …
   **elsewhere mode E runs**" makes both Q8(c) ratios NOT_RUN whenever mode G is licensed on a
   strict subset of R1–R3 — the plan's own "NOT_RUN if modes differ" rule guarantees it (finding
   7); and M5's pass condition is a run/no-run without the two checks the licensing rule requires
   (finding 9).
6. **Q8 on direct blocks — re-worded.** Which pairs: deferred to pilot-note item 12 ("the
   direct-block pair list per rung") — acceptable as form-now/numbers-then. How many: not said.
   What displacement: not said (no Cartesian step h anywhere). How the 3×3 block is extracted:
   "four-point finite differences of ΔE along paired atomic displacements, ≈ 12 energies per
   pair" — four-point mixed differences give **one** element per four energies; a 3×3 block is
   nine elements, i.e. 36 energies, or ≈ 30 with a shared-direction stencil; twelve energies yield
   three elements (finding 16). Real check or tautology: real for the *mid* pairs near r_max,
   where prior and physics can disagree; **vacuous for far pairs the prior zeroes**, and worse than
   vacuous as written, because the agreement metric is a *relative* Frobenius disagreement, which
   on a far block that the recovery sets to exactly zero and the probe measures as noise reads
   100 % and breaches η₈ by construction (finding 3).

Six-word summary: **re-worded, re-worded, closed, closed, re-worded, re-worded.**

---

## Blocking findings

### 1. Q6's σ_E has no estimator, is mis-labelled as a second-difference scatter, and the nine-point grid yields one sample at q_s = 1.0

**Where:** Ladder §3 item-13 bullet ("σ_E the second-difference scatter of frozen-space ΔE …");
Distilled Q6 row ("second-difference scatter σ_E … nine points each at q ∈ [−1, 1] … against
σ_E ≤ 0.82·τ·q_s² on the grid q_s ∈ {0.25, 0.5, 1.0}"); probes README item 5; Budget §4.5;
Research note §8 (the formula's origin); Round-7 Pass B issue 1.
**What.** Round 7 derived σ_E ≤ 0.82·δω̃·q_s² for σ_E = the **per-point** uncorrelated energy
error, from σ(Δ̂₂) = √6·σ_E/q_s². The plan wrote the formula down and then defined σ_E as "the
second-difference scatter". Those differ by √6/q_s²: a script that computes the scatter of second
differences and compares it to 0.82·τ·q_s² is off by a factor ≈ 10 at q_s = 0.5 and ≈ 39 at
q_s = 0.25 — in the direction of *failing* good data. Separately, nine points at 0.25 spacing on
[−1, 1] give seven central second differences at step 0.25, five at 0.5 and **one** at 1.0; the
scatter at q_s = 1.0 — the step Round 7 argued is admissible for a difference and the one that
buys the most noise headroom — cannot be estimated from this grid at all. And the second
differences at different centres differ by the genuine variation Δ₂(q_c) ≈ Δ₂(0) + Δ₃·q_c + …,
so "scatter across centres" mixes the diagonal cubic correction (which the plan measures elsewhere
as a bonus) into the noise estimate.
**Evidence.** The three documents above; the Round-7 derivation (issue 1, quoted in note §8).
**Why it matters.** Q6-noise is the first gate, the one that decides whether mode E may ever
carry "beat" language and the one the pattern amplitude is read from. As written it cannot be
evaluated reproducibly, and two honest implementers would get verdicts differing by an order of
magnitude.
**What would close it (in spec).** Define σ_E as the RMS residual of ΔE(q) about a least-squares
polynomial of declared degree (4 is enough at q ≤ 1 for a difference) over the nine points, per
mode and per space-freezing arm; compare *that* to 0.82·τ·q_s² for each grid step (the same σ_E
serves all three steps; the formula, not the data, supplies the q_s dependence). If the plan
prefers a direct second-difference test, state the line for the second-difference scatter itself,
σ(Δ̂₂) ≤ 2τ in frequency units, and extend the grid to 17 points at 0.125 spacing or drop
q_s = 1.0 from the grid. Say which in Ladder §3, Distilled Q6 and probes README 5, identically.

### 2. ρ\* and K_cap are transferred from a noise-free dry run whose Δ is an order of magnitude larger than the CC−DFT one; under the measured noise floor "Δ₂ not recovered at cap" is the default outcome by construction

**Where:** Ladder §3 "K is a measurement" bullet; Ladder §4 items 8–9 ("Derived from the dry run
by the rule stated in the note"; "derived from the two-mode dry-run K … by a factor stated in the
note"); Distilled §3 "Hold-out and residual ρ", "K", "Dry run"; Budget §4.1; Ladder §5.4 ("ρ not
reaching ρ\* by K_cap … 'not recovered at cap'"); Distilled §8 penultimate sentence.
**What — the arithmetic.** ρ is dimensionless: RMS held-out residual ÷ RMS held-out response. A
response in mode E at a pattern of dimensionless amplitude q_s along one mode is ½·Δ₂,ii·q_s²; for
the expected-effect scale the plan itself writes into the note (≈ 5 cm⁻¹ per mode, item 45) that
is 0.6 cm⁻¹ ≈ 2.8 µE_h at q_s = 0.5 and 2.5 cm⁻¹ ≈ 11 µE_h at q_s = 1. The Q6 noise line at
those steps is 4.7 and 18.6 µE_h (τ = 5 cm⁻¹). So **at the noise line the per-response signal is
below the per-point noise** — by design, since the line was set so that a *second difference of
three points* resolves 2τ, not so that a single response is clean. Multi-atom patterns sum several
modes' contributions, but their total normal-coordinate amplitude is bounded by anharmonicity
(Σq_i² of order a few), so a typical response is a few cm⁻¹ ≈ 10–20 µE_h against a floor of the
same size. Then ρ for a *perfect* Δ₂ is ≈ σ_E / RMS(response) ≈ 0.3–1, and no K exists at which
ρ ≤ ρ\* for any ρ\* below that. The dry run that fixes ρ\* has zero noise and a Δ (BHLYP−B3LYP,
frequency differences of tens of cm⁻¹) ten times larger; its residual curves will go to 10⁻³, and
a ρ\* "derived from the dry run" — by whatever factor — will sit far below the floor unless the
rule explicitly contains σ_E. Nothing in the frozen documents says it does. The consequence is
mechanical: at every rung, ρ never reaches ρ\*, K reads K_cap, the rung's Δ₂ is "not recovered at
cap", the §5.4 fallback (DFT-only) is scored, and the cost record says the maximum. That is not a
measurement of the recovery; it is a measurement of the definition.
**Evidence.** Distilled §3's definition of ρ; the Round-7 numbers now in note §8; item 45's
5 cm⁻¹ scale in Ladder §4 item 2.
**Why it matters.** "K is a measurement, not a choice" is the plan's central honesty device and
the whole content of the cost record. As written, K is a choice made by whoever picks the ρ\*
rule — and if they pick it from the noiseless dry run, K is K_cap everywhere.
**What would close it (in spec; no measurement first).** Fix the *form* of the ρ\* rule now, as
Ladder §4 says forms are: ρ\*(mode, rung) = max(ρ_dry, c·σ_E(q_s)/RMS_resp), with σ_E from the
R1 smoothness probe (scatter is printed before the note — allowed), RMS_resp the RMS of the
*dry-run responses rescaled to the expected-effect line* (item 2 supplies the scale; no local-CC
Δ₂ is read), and c a declared constant (c = 1 means "stop when the residual is at the noise
floor"). Equivalently and more cleanly: define K as the first count at which the held-out
residual's χ² per point, with σ_E as the per-point σ, falls to 1 ± d — a noise-aware stopping
rule that needs no ρ\* transfer at all. Either way, add to the dry run a **noise-injection column**:
the same recovery with Gaussian noise of the measured σ_E added to every dry-run response, K and
ρ printed — at zero CC cost this tells the author before the note whether any K short of K_cap
exists at the measured floor. Record in Ladder §3, §4.8, Distilled §3 and Budget §4.1.

### 3. η₈ is a relative per-block Frobenius disagreement; on far pairs it breaches by construction, and it sits in three licences

**Where:** Ladder §3 Q8(a) ("a relative Frobenius disagreement larger than η₈ is a Q7-class
breach"); Ladder §3 learned-prior licence ("the direct blocks must agree with the prior-assisted
blocks within η₈") and fragment licence part (c) ("agreeing with the fragment-probed blocks within
η₈"); Distilled Q8 pass column; Distilled Q7 (iv) ("agrees within … η₈ (blocks)"); Ladder §5.4.
**What.** The direct-block pair list is "near, mid and far". The recovery, under either prior,
sets far blocks to (near) zero — that is what a locality prior does and what Q8(b) wants to
confirm. The direct probe measures the same far block as noise of size σ_block ≈ σ_E/(2h²) per
component (four-point formula). Relative disagreement = ‖0 − n‖/‖n‖ = 1, i.e. 100 %, for every
far pair, at any noise level, for any η₈ < 1. Conversely, if the recovery leaves a small nonzero
far block and the probe's noise happens to be of the same size, the ratio is O(1) at random. The
metric is ill-posed exactly where the pair list was designed to look. The same object is the
agreement test of the learned-prior licence and of fragment licence part (c), so a learned prior
can be *refused* a licence it deserves, and a fragment scheme *refused* one it deserves, by a
0/0.
**Evidence.** The wording above; my noise arithmetic: with σ_E = 1 µE_h and h = 0.1 Å
(0.19 bohr), σ_block ≈ 1.4×10⁻⁵ E_h/bohr² per component; a bonded C–C Δ block for a 5 cm⁻¹
correction on a 1,500 cm⁻¹ stretch is ≈ 2.8×10⁻³ E_h/bohr² (δk/k = 2δω/ω on k ≈ 0.42
E_h/bohr²) — so near blocks are resolved to 0.5 % and far blocks are pure noise, which is the
right regime for an *absolute* test and the wrong one for a relative one.
**Why it matters.** Three licences and Q7(iv) hinge on η₈; as written the pass/fail of the far
pairs is decided by the metric, not by the physics, in both directions.
**What would close it (in spec).** Normalise every block disagreement by the **largest direct
block of that rung** (or by √(Σ‖direct block‖²/n_p)), so that η₈ is a fraction of the block scale
and a far pair at noise passes when the recovered block is also small; state a floor: a pair whose
direct block is below 3σ_block is reported as "at noise" and enters Q8(a)'s fit with its
uncertainty, not as a pass/fail. Same sentence in Ladder §3 (three places), Distilled Q7(iv) and
Q8.

### 4. The fragment licence's third part is circular as written, and its second part is near-tautological at coronene; nothing in the promised set measures a fragment against anything larger than itself

**Where:** Goal "The goal binds" item 1 and Reach question; Ladder §3 fragment licence (a)–(c);
Ladder §2 R3/R4/R6 rows; probes README 13–14; Budget §4.12–13; Distilled §4 last bullet, P5.
**What.** Part (c): "a direct-block probe **on the fragments of the rung itself** (deck-chosen
interior and edge pairs), agreeing with the fragment-probed blocks within η₈." If the direct block
is computed on the same capped fragment that the fragment probing used, it is the same truncated
electronic structure differenced two ways: it tests the recovery's arithmetic, not whether the
fragment's interior is the flake's interior. Only a direct block computed on the **whole flake** —
432 atoms, TZ, twelve-plus frozen-space local-CC energies per pair — is independent, and nobody
has costed that; it is a B3 object of unknown size. Part (b): coronene (36 atoms, radius ≈ 3.7 Å
to the outer carbons) "recovered from capped fragments of radius r_max". Q8(a)'s r_max is bounded
by the R3 molecule's own diameter, and a plausible r_max for a π-conjugated correction (three to
four bonds, 4–6 Å) makes the "fragment" essentially the whole molecule plus caps. Agreement within
τ₇ is then expected whatever the physics; disagreement would mean the caps are wrong, not that
locality failed. Between R3 and R6 the only test that is not one of these two is the R4
whole-vs-fragment comparison, which is "where whole-molecule probing is classified affordable" —
circumcoronene whole in mode E is ≥ 2×210 = 420 frozen-space local-CC energies of a 72-atom
molecule at TZ, i.e. B3 in all likelihood. So under the goal-binds directive the licence for using
fragments on a 432-atom interior rests on (a) a locality verdict at coronene, (b) a self-agreement
at coronene, and (c) a self-agreement on the fragment — none of which sees an environment with no
edge within r_max.
**Evidence.** The Ladder wording; Pass A issue 8 (which asked for (b) and (c) and got them in a
form that does not do the work); the geometry of coronene.
**Why it matters.** Decision 1's whole justification is "decided by measurement". As written the
measurement cannot fail for the reason that matters (interior ≠ measured environment), which makes
the R6 certificate's licence decorative — the same criticism Round 7 made of Q8 before the
direct-block probe existed.
**What would close it (in spec, and the cheapest science).** Re-specify part (c) as a
**fragment-radius convergence test on the R6 interior**: for the deck-chosen interior pairs,
compute the direct block from fragments of radius r_max and 1.5·r_max (or r_max + one ring)
carved from the R6 flake's own DFT geometry, and require agreement within the (fixed, absolute)
η₈ of finding 3 — this costs fragment-size calculations only, is the standard convergence check of
every local method, and is the one test that can fail because the interior is different. Keep the
whole-flake direct block as the gold check where B3 allows. For part (b), report r_max against the
molecule's radius and require the R3 comparison to be run at the **smallest** radius that passes,
so that the fragment is genuinely smaller than coronene; if no radius smaller than the molecule
passes, say so — that is a result. Under "the goal binds", promise the R4 whole-vs-fragment
comparison conditional on B3 classification (not "bonus"), since it is the only measurement on a
fragment that is not the whole molecule. Edit Goal item 1's list, Ladder §3 (c), probes README 14.

### 5. The side project has not said what "frozen spaces" are as a differentiable object; the maximal-overlap mapping is piecewise constant and can switch along symmetric modes of the two D₆h rungs; M2's finite-difference reference must be the re-projected energy or it tests nothing

**Where:** Side project §1.2, §1.3, §2 (c), §3 M1/M2, §7 risk 3; Ladder §3 "Frozen spaces"; probes
README 1b ("reloads them at displaced geometries by maximal overlap"); Proposal §5.3; item 33.
**What — the object.** At a displaced geometry the AO basis moves with the nuclei; the stored
LNO coefficient vectors are no longer orthonormal, no longer orthogonal to the new occupied space,
and no longer span a subspace of the new virtual space. Three things could be "held fixed": (i)
the AO-basis coefficient matrix — ill-defined without a projection; (ii) the LNO rotation in the
new geometry's canonical-MO basis — gauge-dependent (degenerate canonical orbitals of D₆h
benzene and coronene rotate arbitrarily between geometries), hence not smooth; (iii) the stored
vectors **projected onto the new geometry's virtual space and re-orthonormalised**, after mapping
localized occupied orbitals by maximal overlap — ORCA's DLPNO-MP2 mechanism and the only
well-defined one. The plan's documents say (iii) in words ("map localized orbitals by maximal
overlap and reuse the stored spaces") but never write the projection down, and §1.2 speaks of
"coefficient vectors in the moving AO basis", which is (i).
**Smoothness.** With (iii), E_frozen(x) is smooth *between* assignment switches: the projection
and Löwdin orthonormalisation are analytic while the projected vectors stay linearly independent.
The maximal-overlap **assignment** is discrete. In benzene (R0) and coronene (R3), symmetry-
equivalent localized σ and π orbitals have overlaps that cross along totally symmetric and
degenerate modes; when the assignment flips, E_frozen jumps by the difference between using
orbital A's stored LNO space for orbital B and vice versa — a µE_h-class discontinuity of exactly
the type Q6 is built to catch, and one that free spaces do not have. Naphthalene (R1, D₂h) is the
least exposed of the four; the two D₆h rungs are the most. Q6 as specified runs its smoothness
grid at R1 and "the R2-size family"; the M1 scatter print is along "one benzene mode". Neither is
guaranteed to cross a switch.
**The derivative.** If the projection P(x) is inside the JAX graph, the AD gradient is the exact
derivative of E_frozen — §1.2's claim holds. If P is done in NumPy or under `stop_gradient`, the AD
gradient misses (∂E/∂V)·(dP/dx)·V₀, the response of the energy to the geometry dependence of the
projected space. That term is **not** zero: a CC energy truncated to a virtual subspace is not
stationary with respect to rotations between kept and discarded virtuals — this is why general
PNO/LNO gradients need Lagrangian constraints for space relaxation, and why Pinski & Neese report
"dramatic errors" when PNO constraints are omitted for relaxed properties (record/snippet grade).
Size at q_s ≈ 0.5–1: the LNO truncation error at Nagy–Kállay-class thresholds is of order 10⁻³–
10⁻⁴ of the correlation energy (recalled), i.e. ≈ 0.1–1 mE_h for naphthalene; if its geometry
modulation across a 0.1–0.2 Å displacement is 1–5 %, the missing term is 10–50 µE_h over
≈ 0.2 bohr, i.e. 5×10⁻⁵–2.5×10⁻⁴ E_h/bohr — above M2's 10⁻⁵ threshold. So **M2 as written would
catch a projection-outside gradient**, but only if its finite-difference reference is built from
energies that **re-project at every displaced geometry**; if the reference reuses the stored
vectors without re-projection (which cannot even produce a valid energy) or is built with a
different mapping, the comparison is between two different surfaces. The brief's worry — AD and
FD agreeing while both are wrong relative to the smooth surface — is real in a different place:
both are derivatives of E_frozen, and E_frozen's Hessian differs from the relaxed-LNO Hessian by
the freezing bias. M2 cannot see that; only Q6's bias line (frozen vs canonical, R0 and pyrene
diagonal) can, and only where the canonical arm runs (finding 8).
**What PySCFAD actually does (verified today).** The paper differentiates the orbital
localization by implicit differentiation, states that the LNO cutoff "neither yields a continuous
energy function across the potential energy surface, nor preserves the molecular point-group
symmetry", says the resulting errors in gradients "tend to be small, provided that the correlation
domains are properly converged", and benchmarks its LNO-CCSD(T) gradients **against canonical
CCSD(T) AD gradients on the Baker set (3–29 atoms, cc-pVDZ)** — never against finite differences
of its own LNO energy. So the published code's gradient is already a gradient of a discontinuous
surface with the space response's treatment unstated; M2 would be the first AD-vs-FD check of a
frozen LNO surface anywhere. That is a point in the side project's favour scientifically and a
warning about what "the exact derivative" can mean.
**Why it matters.** "Exactness" is the side project's whole physics claim and mode G's route to
"beat" language on R1–R3. A gradient that is exact for a surface with assignment jumps is exactly
as noisy as the energies, which Pass A issue 7 already noted; a gradient that is *not* exact
because the projection is outside the graph is wrong by an amount the plan has not bounded and
that M2 only catches if its FD reference is specified.
**What would close it (in spec; measurements inside M1–M2).** (i) Write the frozen-space object
once, in Ladder §3: stored localized occupied orbitals and per-fragment LNO vectors in the AO
basis; at a displaced geometry, occupied orbitals mapped by maximal overlap (assignment printed),
LNO vectors projected onto the new virtual space and Löwdin-orthonormalised; that projected space
is "the frozen space". (ii) M1 prints, at each displaced benzene geometry, the assignment
permutation and E(frozen) − E(fresh); add one **totally symmetric** and one **degenerate** mode to
M1's grid so that a switch can be seen; a switch in the assignment is a printed event and the
Q6 smoothness probe at R1 and the R2 family must include the molecule's symmetric modes. (iii) M2
states that its finite-difference reference is E_frozen with re-projection at every displaced
geometry, and adds a **third printed number**: the AD gradient with the projection inside the
graph minus the AD gradient with `stop_gradient` on the projection, at one displaced naphthalene
geometry per Q6 mode — that difference *is* the size of §1.2's hole, printed, and it costs two
gradient evaluations. (iv) Record in §8 that the PySCFAD paper validated against canonical
gradients only.

### 6. R2's gas-scored C–C families are inconclusive by construction: the decidability rule compares the point spacing, not the band-centre uncertainty, and the NIST/EPA GC-IRD spectra are 8 cm⁻¹-resolution hot-vapour spectra scored against a 0 K prediction

**Where:** Ladder §2 R2 row ("grids ~4 cm⁻¹ per the plan-04 coverage probe") and "Decidability
per family" ("decidable if the measured gas grid … is smaller than the family's beat margin");
Frozen_Lines §5 NIST row; Mapping M03; Goal prime directive ("gas-scored families decidable by
their measured grid"); Proposal §5.2; Ladder §4 items 1–2.
**What — verified.** Triphenylene has a gas-phase IR entry in the WebBook (HP-GC/MS/IRD,
NIST/EPA Gas-Phase Infrared Database); its JCAMP has `##DELTAX=4.0` over 550–3846 cm⁻¹, 825
points, and **no resolution or temperature line**. The SRD 35 description (snippet grade; the PDF
would not text-extract here) says the EPA spectra were taken at 4 cm⁻¹ and **all spectra were
converted to an exact 8.0 cm⁻¹ resolution** for homogeneity, and that all were measured by GC/IR
so concentrations are unknown — which the species page confirms ("molar absorptivity values cannot
be derived"). Pyrene and chrysene are in the same database. So the plan's "~4 cm⁻¹" is the point
spacing of a spectrum whose resolution is 8 cm⁻¹, and the decidability rule as written compares
the wrong number with the margin.
**What — recalled.** GC-FTIR lightpipes run hot (≈ 200–280 °C for PAHs of this volatility); PAH
C–C stretches red-shift with temperature by of order 1–3 cm⁻¹ per 100 K through hot-band
population, and the bands broaden. The plan scores "0 K absorption against laboratory data".
**Arithmetic.** A band centre from an 8 cm⁻¹-resolution, 4 cm⁻¹-sampled, moderately noisy
absorbance band is good to perhaps ±2–3 cm⁻¹ by centroiding; add an unmodelled temperature shift
of a few cm⁻¹ of unknown sign per family; the scoreboard's own uncertainty on a C–C band is then
≈ 4–6 cm⁻¹. The expected Δ₂ effect after the opponents' fitted factors absorb its mean is the
*scatter* of a ≈ 5 cm⁻¹ MAD — a few cm⁻¹. A beat margin must exceed the scoreboard uncertainty
to be decidable and must be smaller than the effect to be winnable; there is no number that does
both here. For the CH-oop families (bigger errors in the harmonic lines, Frozen_Lines §6: 7.1 cm⁻¹
mean, solo −36, duo −49) the margins are larger and gas scoring can still decide; for the
6.2/7.7/8.6 µm C–C families — the ones the astronomy and Round 7's issue 2 care about — R2 gas
scoring is inconclusive by construction, and the plan's Goal currently promises them as
"decidable by their measured grid".
**Why it matters.** The plan pre-declares inconclusive as publishable (good) but promises R2–R3
scoring per family as if the outcome were open; on the C–C families at R2 it is not, and the
defence should know that before the pilot note rather than at P2. It also bears on the R2 set
decision (3): triphenylene "joins on its gas families" — which families those are, once the rule
is corrected, is the question.
**What would close it (in spec + M03).** (i) Replace "measured gas grid" by a **measured
band-centre uncertainty** per molecule and family in the decidability rule (Ladder §2, Goal prime
directive, Mapping M03): resolution (from the JCAMP or the database description, not DELTAX),
centroid precision from the SNR, and a **temperature term** — either a declared hot-band
correction per family from the literature (a debt to name) or an explicit "hot-vapour scoreboard,
0 K prediction" label with its estimated shift added to the uncertainty. (ii) M03 prints the
three numbers per band and the decidability verdict *before* the pilot note; the pilot note's
item 1 records per family "gas-decidable / matrix-gated / inconclusive by construction". (iii) Write
into the expected-effect line that the R2 C–C families are expected to be undecidable on the NIST
scoreboard and that decidable C–C scoring at R2 needs a source the plan does not yet have (the
PAHdb gas-phase v1.00 five spectra, jet-cooled or low-temperature gas cells — Proposal §13.3
already asks the supervisor for exactly this; make the ask load-bearing). (iv) Note that the NIST
metadata settles rule E's "intensities reported, not scored" on a measurement (below).

### 7. "Elsewhere mode E runs" makes both size-sentence forms and the promised Q8(c) answer NOT_RUN by construction whenever mode G is licensed on a strict subset of R1–R3

**Where:** Goal prime directive ("On every rung where its milestone licenses it, mode G is the
route … elsewhere mode E runs") and Cost question; Ladder §1 size sentence; Ladder §3 Q8(c) ("If
the modes differ between two rungs, Q8(c) for that pair reads NOT_RUN"); Distilled Q8 pass
column; Side project §3 "What success means", §5.
**What.** The likely trajectory by the side project's own milestone table: M3 passes on the laptop
(R1 licensed), M4 passes on B3 or not (R2), M5 is "B3 by expectation" (R3). Any outcome other than
"all three" or "none" — the two least likely — leaves R1→R2 or R2→R3 with different modes, and the
plan's own rule then prints NOT_RUN for that ratio. The Goal's Cost question ("did that number …
saturate between R1, R2 and R3") is a **promised** question, not a bonus; its answer is then
"NOT_RUN by construction". The cure is trivial and absent: mode E is the guaranteed route and its
2M + K_off energies are affordable wherever mode G is; nothing says mode E runs *as well* on a
mode-G rung.
**Why it matters.** Decision 5 was made so that the size question could be answered on K; as
scheduled it more probably removes the K_off answer without supplying the K one.
**What would close it (in spec).** Goal: "Mode E runs on every rung R1–R3 that runs; on rungs
where mode G is licensed it runs in addition, and the cost record carries both." Ladder §1: the
mode-E form is always earnable from the mode-E record; the mode-G form additionally where licensed
on all three. Q8(c): computed per mode over the rungs that mode ran. Budget: the classification
rule already classifies both modes separately, so no new slot is needed.

### 8. The R0 canonical arm — the only reference independent of the freezing and the whole of Q6's bias line — is assumed affordable against the plan's own provenance, with no feasibility probe and no fallback

**Where:** Ladder §2 R0 row ("canonical CCSD(T) affordable (plan-02 measured 19.6 s/point on the
old machine, provenance only) … the canonical arm is the only one that licenses the space
freezing"); Budget §3 last paragraph ("canonical (T) fails at ~114 bf with 28 GB"); Distilled Q6
bias, Q7(i); Side project M2 ("cc-pVTZ"); Distilled §3 ("basis per rung").
**What.** The 19.6 s/point figure is CCSD(T)/6-31G\* benzene (102 functions) on the old machine;
the same provenance line says canonical (T) **failed at ≈ 114 functions with 28 GB** — that is
cc-pVDZ benzene. The anchor basis is not fixed anywhere in the frozen documents ("basis per
rung"); the side project runs everything at cc-pVTZ (264 functions for benzene). The bias line
|Δ₂(frozen) − Δ₂(canonical)| must compare like with like — same basis — and needs a canonical
CCSD(T) Hessian of benzene: ≈ 61 energies by second differences along modes, or ≈ 72 canonical
gradients. On a 31.3 GB laptop, canonical CCSD(T)/cc-pVTZ benzene is doable in PySCF only with
AO-direct or out-of-core handling of the vvvv block (243⁴ × 8 B ≈ 28 GB in-core) at hours per
point, i.e. days for the Hessian — plausible but **unmeasured**, and the plan's rule is that an
unmeasured affordability is not a fact. The R1 canonical arm is already declared conditional
("the first R1 probe measures whether canonical (T) runs"); the R0 arm is treated as certain
although the only datum on file says it failed at a smaller basis.
**Why it matters.** If the R0 canonical Hessian does not run in the anchor basis, there is **no
bias line anywhere** and the space freezing is never licensed against anything but itself; Q7 at
R0 loses the "only reference independent of the freezing"; and the pyrene diagonal check (two
canonical energies per mode) is even less certain.
**What would close it (in spec + one probe before the note).** Fix the anchor basis per rung in
the deck now (Distilled §3) — the freezing bias and the noise floor are basis-dependent and the
smoothness probe must be run in the production basis. Add to Budget §4 (before the note) and
probes README a **one-point R0 canonical feasibility probe**: one canonical CCSD(T) energy of
benzene in the anchor basis on the B2 laptop, wall-clock and peak memory printed, extrapolated to
the Hessian count. Write the fallback: if it does not fit, the bias line is measured in the largest
basis that does (cc-pVDZ) with the frozen arm re-run in that basis for the comparison, labelled;
or the R0 canonical Hessian is the first B3 request. Ladder R0 row: replace "affordable" by
"expected affordable; measured by probe X before the note".

---

## Non-blocking findings

### 9. M5 licenses R3 with a run/no-run while the licensing rule requires two checks
**Where:** Side project §3 (M5 row vs "What success means"); Ladder §1 mode-G form ("M3, M4,
M5"); Budget §4.12; probes README 13.
**What.** "Mode G is licensed on a rung when (i) the milestone for that rung's molecule passed
**both checks** (… M5 → R3)". M5's pass condition: "one gradient at coronene/cc-pVTZ with frozen
spaces; run/no-run, wall-clock and peak memory printed." No correctness check, no σ_g line at
coronene size. Either M5 gets the two checks (an FD reference at coronene is 2 × 3N = 216 energies
per gradient component check — expensive; a *partial* FD on the three Q6 modes is 6 energies and
is enough) or R3 is never mode-G-licensed and the mode-G size sentence is unearnable, which the
plan should then say.
**What would close it.** M5: "run/no-run, plus AD-vs-FD along the three Q6 modes (six frozen-space
energies) and σ_g on those modes at the R3 size class".

### 10. The resonance-closed family set has no bound; at coronene its cost can exceed the machine checkpoint
**Where:** Goal "Where CC is spent" last sentence; Distilled §3 row 2 ("every partner mode found by
the r₃/r₄ resonance search"); Ladder §4 item 7; Round-7 Pass B issue 3 (its origin).
**What.** Closure under a resonance search is transitive: a partner's own resonances pull in its
partners. On coronene the 1,100–1,650 cm⁻¹ C–C manifold is dense with CH-oop overtone and
combination partners; a closure with generous r₃/r₄ thresholds can reach most of the 102 modes at
two DFT Hessians each — on the plan's own provenance (176 min per coronene frequency job on the
old machine) that is of order 200–300 h, over the 168 h checkpoint before any CC energy is spent.
**What would close it.** Item 7 freezes, with the thresholds, a **closure depth** (one generation
of partners; partners' diagonal anharmonicity from their own 1-D cut only) and the polyad cap as
the bound; the pilot note prints the closed set's size and Hessian count per rung.

### 11. The learned-prior licence is now a real check on the quantity that matters, with three residual weaknesses
**Where:** Ladder §3 learned-prior bullet; Distilled §3 "Learned prior", §5, §6; Mapping M05;
Goal decision 4; Pass A issue 2.
**What.** (a) The reference at R2–R3 is the structural recovery on the same responses — itself
unlicensed by any direct reference above R1 (Q7 is R0–R1). Two recoveries sharing patterns,
hold-out and noise can agree while both are wrong in the same way; the direct blocks (now with an
absolute η₈, finding 3) are the only independent anchor and they do not resolve the mode-basis
C–C block. (b) The corpus: QM9 contains molecules of up to nine heavy atoms (recalled) — benzene
and indene-size bicyclics are its largest π systems; naphthalene is not in it. The "aromatic-heavy
subset" therefore contains no PAH, and the P3 saving "on the dry-run corpus" is measured
off-distribution from every rung. The PAH dry-run tensors are the held-out test set, which is the
right place; P3's effect size (item 5) should be reported on that test set as well as on the
corpus, and the licence should cite the test-set number. (c) On a spent rung (R4–R6) the prior
predicts the support of a molecule two to ten times larger than any it was licensed on; the
certificate says so (good) — it should also carry the rung's direct-block agreement as the only
prior-independent number.
**What would close it.** Item 5 reports P3 on the PAH held-out tensors; the licence at R2–R3 adds
"and the structural recovery's own Q8(a/b) on direct blocks passed at that rung" so that the
reference is at least locality-checked; Mapping M05's dataset paragraph states QM9's size range.

### 12. Rubric fit after the decisions — what a grader sees for M05 and M06
**Where:** Mapping §1 rows 05–06, §3 M05 ("Problem domain … sequence"), M06; §4 table;
Rubrics 05 Task 1 and rubric row; Rubrics 06 Task 1 and "Dataset or Prompt Requirements".
**What — M05.** The rubric's dataset clauses (read in the workspace copy): "publicly available and
appropriate for academic use; not synthetic or AI-generated; not reused from any previous capstone
project; you may use standard benchmark datasets or curated real-world datasets". A grader reading
literally sees: Hessian QM9 (public, a benchmark) plus a self-computed B3LYP half published on
Zenodo, combined into a derived quantity. The Rubrics/README reading that a self-computed,
pre-published corpus qualifies is the *plan's* reading; the rubric text itself names benchmarks and
curated real-world sets. "Not synthetic" — ab initio Hessians are computed, not AI-generated; the
mapping's required sentence handles it. The real exposure is decision 7: if the Foundations module
was submitted on QM9, "not reused from any previous capstone project" is arguable for Hessian QM9
(same molecules, different authors, different property) and a strict grader can go either way; the
mapping already names the reading-2 fallback ("a different public Hessian source, named and
verified at that moment") — name it now, so the fallback is executable on the day. The "sequence"
domain (a molecule as a sequence of DFT-mode tokens) is a stretch a grader may or may not accept as
"text or sequence modeling"; the notebook should show sequences as the rubric's Task 2 asks
("display representative samples such as … sequences"). "High accuracy is not required" — the
licence-as-success framing fits.
**What — M06.** The rubric's three approaches are GAN for images, **VAE for image generation or
representation learning**, and Transformer generation for text/sequences. A VAE over two-mode
displacement patterns is "representation learning" in the rubric's own words — defensible, not a
stretch. The stretch is in Task 4: "multiple generated examples; a qualitative evaluation of output
quality; discussion of strengths and failure cases" — a displacement pattern is not an image or a
sentence; the notebook needs a rendering (arrows on the molecular frame) and a qualitative rubric
the mapping does not yet describe. Dataset: the PAH dry-run tensor corpus and pattern-response
records are "own computed" (fine); but the **same PAH dry-run tensors are M05's held-out test set
and M06's training data** — under reading 2 that is cross-module reuse; the mapping says "distinct
from M05's QM9-derived corpus" and is silent on the tensors. And the required "not synthetic … as a
dataset" sentence must be careful: the M06 *dataset* (responses) is computed, the *outputs*
(patterns) are model-generated and never shipped as data — the mapping says so; keep it.
**What would close it.** Name the M05 reading-2 fallback source now; add a "generated pattern
rendering and qualitative criteria" paragraph to M06; either drop the PAH dry-run tensors from
M06's training set or record the overlap and the reading-2 consequence in §4's table.

### 13. "Inheritance is not authority" — the walk the brief asked for
**Where:** Goal (the directive and "What is inherited"); Why_05 "What plan 04 got right";
Distilled §3 rows "Scale factors", "Intensities", "Anharmonic machinery"; Ladder §2 "Charge",
"Decidability"; Ladder §3 "Matrix tolerance"; Ladder §6.
**What.** Classified as the directive requires (measurement / goal / habit):
- *No scale factor on anharmonic output* — **goal**: the criterion is "natively, without any
  generic scale factor" (expectations tier 2, a user directive), and a scaled anharmonic spectrum
  scored against fitted opponents would be a fit-vs-fit contest with no CC content. Keep.
- *Positions scored, intensities reported* — **measurement**, and now a verified one: the NIST/EPA
  gas-phase spectra carry no concentration ("molar absorptivity values cannot be derived", species
  page), and item 30 (full text) bars a CC dipole correction. The Goal's "scored only where the
  pilot note names a gas-phase intensity scoreboard" is the right form; record the NIST fact as
  its basis. Keep.
- *Neutral species only* — **habit**, with a tool-availability gloss that is weaker than the plan
  thinks: pyscf-forge's `pyscf/lno/` contains `ulnoccsd.py` and `ulnoccsd_t.py` (verified today),
  so open-shell LNO-CCSD(T) energies exist in the candidate code; the remaining reasons (B3LYP
  spin contamination for radical cations, doubled canonical-reference cost, matrix-only lab data
  for most cations) are real but nowhere written as the rule's basis, and PAH cations are the
  species the JWST motivation is mostly about. Under the directive this rule is unsupported as
  written: either re-justify it in the Goal with those three reasons and a per-rung deck override
  (the Ladder's "unless a rung's pilot note names a charge state" already allows it), or drop it
  and let the pilot note decide charge per rung. Not blocking because nothing promised depends on
  it.
- *No tier-2 pre-registration before references* — **goal** (the pre-registration principle: a
  protocol without a pinned scoreboard cannot be scored; debt 4 unpaid). Keep.
- *Matrix–gas gate* — **measurement**: plan-02's 7.1 cm⁻¹ floor and 60 cm⁻¹ lab spread, and
  M03's forthcoming measured shift; the per-family form is Round 7's improvement. Keep — and
  finding 6 asks for its gas-side twin.
- *No motif transfer* — **measurement** (plan-02: tens of cm⁻¹), clarified to spectra and band
  positions; fragment probing is a different object and is now licensed by measurement. Keep.
- Two rules the brief did not list but the directive covers: *B3LYP-class baseline DFT* — **goal**
  (P1's harmonic cross-check against line A's unscaled values and P2's comparability need the same
  functional; say so in Distilled §3, it is not written); *the 10 cm⁻¹ astronomical floor and the
  ~1 cm⁻¹ bind* — goal and measurement respectively (scoreboard uncertainty). Keep.
**What would close it.** One paragraph in the Goal under the directive listing these
classifications; the neutral-species rule re-justified or made per-rung; the B3LYP-class reason
written.

### 14. Proposal and change-table staleness after the Round-8 patches
**Where:** Proposal §1, §5.1 step 1, §5.2 R4–R5 row, §7, §11 risk 6; Why_05 row 25; Side project
§1.1; bibliography items 48–49.
**What.** Proposal §5.1: "analytic, **on a GPU where the deck names one**" — decision 6 says the
laptop has no CUDA GPU and every GPU Hessian is B3; the Goal and Distilled were fixed, the
proposal was not. §5.2 R4–R5: "the learned-prior experiment" — it is now the spent licence. §11
risk 6: "an alarm that forces a written review if its hours outgrow the **three data modules
combined**" — the side project's §4 now says "exceeds the pipeline-infrastructure bucket at any
4-weekly review"; the two triggers differ. §7: the pilot note is written with "a DFT-only dry run …
the noise-floor measurement and single-point timings in hand — and nothing else" — the Ladder's
list also has probe M1 and the gradient run/no-run. §1: "harmonic force constants corrected to
**coupled-cluster quality**" — the Ladder's own phrase is "local-CC, R1-checked"; "quality" is the
kind of adjective the plan bans for cost and should avoid for accuracy. Why_05 row 25 and item 48
say the released code is LNO-CCSD; see finding 15.
**What would close it.** One sweep of the proposal against Goal decision 6, Ladder §3/§4 and the
side project's §4.

### 15. The engine facts the plan hedged are settled by a fetch, and the hedges are now the inaccurate statements
**Where:** Side project §1.1, §2 (a), §7 risk 4, §8; bibliography items 33, 48, 49 and "Method
debts"; Distilled §3 anchor row ("released as LNO-CCSD, (T) to be verified at probe M1"); Why_05
row 25; Proposal §5.3 ("the released energy code is listed as CCSD").
**What — verified today.** (a) pyscf-forge `pyscf/lno/` contains `lnoccsd_t.py`, `ulnoccsd_t.py`
and `ulnoccsd_t_slow.py`: the released energy code **includes (T)**, closed- and open-shell; the
changelog line "LNO-CCSD" the plan quotes is a summary, not the contents. (b) PySCFAD's package has
a **`pyscfad/lno/`** directory — `lno_base.py`, `ccsd.py`, `ccsd_t.py`, `_checkpointed.py`, MPI
variants — and an `examples/lno/` directory; the README does not mention it, which is why the
plan's fetch missed it. There is no separate "gradient file" because in PySCFAD the gradient is
`jax.grad` of the differentiable energy; `_checkpointed.py` is where the paper's recomputation
strategy will live. (c) The paper (full text) says the (T) backward pass is manually optimised and
computed on the fly "without storing any intermediate quantities except for the singles and
doubles amplitudes", that memory is dominated by ⟨ov|vv⟩ with `jax.checkpoint` recomputation, that
fragments are MPI-distributed, that Baker-set benchmarks are cc-pVDZ (3–29 atoms) and the
hydrogenase model def2-TZVP; it gives **no GB figures** and **no gradient-vs-energy wall-clock**.
**Why it matters.** The plan's rule is "never cite from recall"; the same rule means "do not
freeze a hedge you could have resolved". Every sentence that says "(T) to be verified" or "code
unlocated" is now the sentence a reader will find false in five minutes. The author's own fetch is
still owed under the plan's rules; this review does not substitute for it.
**What would close it.** Items 48–49 upgraded with the directory listings and date; side project
§1.1/§2(a)/§8, Distilled §3, Why_05 row 25, Proposal §5.3 re-worded to "present in the released
code (fetched 2026-09-04); its behaviour with frozen spaces is M1/M2's measurement". Add the
paper's memory statements to item 33 with the note that no GB figures exist.

### 16. The direct-block probe cannot yield a 3×3 block from twelve energies, and has no step
**Where:** Ladder §3 Q8(a); Distilled Q8; probes README 12; note §8; Round-7 issue 6.
**What.** A four-point mixed second difference gives one element per four energies; nine elements
need 36, or ≈ 30 with a stencil of six single-direction and nine combined-direction second
differences (which also yields both atoms' self-blocks). "≈ 12 energies per pair" is three
elements — probably the α = α ones — or one element for three families. The plan should say
**which components** it measures: for Q8(b) what is needed is the block's projection onto the
scored family's mode directions at the two atoms (one scalar per pair per family, four energies
each), not the full block. The Cartesian step h is unspecified; my arithmetic (finding 3) says
h ≈ 0.1 Å per atom is needed for near blocks at 0.5 % and that far blocks are at noise at any
admissible step — which is fine for an absolute test and must be said.
**What would close it.** Ladder §3 and probes README 12: the measured quantity per pair is the
family-projected coupling ∂²ΔE/∂u_A∂u_B for u the family mode's local direction at each atom,
four energies per (pair, family), h a deck number ≈ 0.1 Å; the full block only for the deck's
near pair at each rung as a check.

### 17. M1's only quantitative pass condition is an identity
**Where:** Side project §3 M1; Budget §4.2; probes README 1b.
**What.** "E(reference geometry, reloaded spaces) − E(reference geometry, fresh spaces) = 0 to
10⁻⁹ E_h" tests that a file round-trips. The informative M1 numbers are at displaced geometries:
E(displaced, frozen) − E(displaced, fresh) — the freezing bias in µE_h along the mode, which is
what Q6's bias line will later see against canonical — and the assignment log of finding 5. Both
are printed without a verdict (the plan's rule) and neither is a Δ₂ number.
**What would close it.** Add the two printed columns to M1; keep the identity as the sanity check.

### 18. Also-worth items, disposed
- **The plan-01 alarm.** The side project's trigger is now "the side-project bucket exceeds the
  pipeline-infrastructure bucket at any 4-weekly review" — measurable from day one, since both
  buckets exist from the first logged hour. The proposal still carries the old trigger (finding
  14). Booking M1 to infrastructure makes the infrastructure bucket large early and the alarm
  correspondingly quiet; acceptable, but say it.
- **Round-7 Pass A's pilot-note-inputs item.** Holds. The R1 smoothness probe prints σ_E per mode
  and step and seals the means; M1 prints scatter; the gradient run/no-run at equilibrium yields
  Δ₁ (the CC−DFT force at the DFT minimum), not a Δ₂ number; the dry run is DFT–DFT. The one
  residual is procedural: the script that computes σ_E must fit the curve whose coefficients are
  the Δ₂ diagonal — the seal is a discipline of the script and the commit hash, which is what the
  plan says. Closed, with finding 1's estimator making the seal well-defined.
- **The proposal's honesty.** §9 states the conditional verdict and its conditions, §10 says who
  decided what and lists the open item, §5.3 hedges the engine (now over-hedged, finding 15) and
  §11 names the side project as the plan-01 failure mode. Honest; stale in the places finding 14
  lists.

---

## Attack-by-attack disposition (brief order)

| # | Attack | Lands? | Disposition |
|---|---|---|---|
| A | Frozen-space AD gradient is "exact" | **Partly — blocking, finding 5** | Exact for E_frozen only if the projection is inside the graph and only between maximal-overlap assignment switches; the two D₆h rungs are where switches are likeliest; the projection-outside hole is ≈ 10⁻⁵–10⁻⁴ E_h/bohr (inference) and M2 catches it *if* its FD reference re-projects; M2 cannot see the freezing bias — Q6's bias line can, where the canonical arm runs (finding 8). PySCFAD's own gradient (full text) was validated against canonical CCSD(T) only. |
| B | Side-project feasibility | **Does not land as an objection; the plan's hedges are stale — finding 15** | The AD LNO-CC code is at `pyscfad/lno/` (with `ccsd_t.py`, MPI, checkpointing); pyscf-forge's `pyscf/lno/` has `lnoccsd_t.py` and open-shell variants. Paper: (T) backward pass manual and on-the-fly; memory dominated by ⟨ov|vv⟩ with recomputation; **no GB numbers**; Baker set 3–29 atoms at cc-pVDZ, def2-TZVP for the 549-orbital model. Per-fragment sizing at cc-pVTZ (recalled function counts): naphthalene 412 functions, ⟨ov|vv⟩ per fragment ≈ 8 GB — M3 on 32 GB plausible; pyrene 620 functions, ≈ 30 GB — B3, as M4 says; coronene 888 — B3. Twelve calendar weeks for M1–M3 concurrent with modules 02–03 is tight, not fantasy, *because* the code exists; the risk is JAX memory and finding 5's discontinuities, and the kill criterion is the right instrument. |
| C | Learned-prior licence passable while wrong in the mode-basis block | **Closed by the Round-8 patch; residuals non-blocking, finding 11** | The reference is now the structural recovery per family within τ₇ on the same responses — the right quantity; residuals: the reference is itself unlicensed above R1; QM9 has no PAH; P3 should be reported on the PAH held-out tensors. |
| D | Fragment probing licensed on a molecule smaller than the fragment | **Yes — blocking, finding 4** | Part (c) is circular; part (b) is near-tautological at coronene; the cheapest licence for fragments on a fragment is a fragment-radius convergence test on the R6 interior (fragment-size cost) — promise it; promise the R4 whole-vs-fragment comparison conditional on B3. |
| E | Inherited rules under "inheritance is not authority" | **One rule unsupported — finding 13** | Neutral-only is habit (open-shell LNO-CCSD(T) exists in the candidate code — verified); the other five rest on the goal or on measurements, one of them newly verified (NIST intensities). |
| F | R2 decidability after the re-read | **Yes — blocking, finding 6** | Triphenylene gas IR exists (verified); `DELTAX=4.0`; SRD 35 (snippet) says all spectra were homogenised to 8 cm⁻¹; GC-IRD is hot vapour; the rule compares point spacing to the margin; the R2 C–C families are inconclusive by construction on this scoreboard and the plan should say so before the note. |
| G | Rubric fit of M05/M06 | **Stretch, not failure — finding 12** | M05: derived corpus half public, half self-computed and pre-published; a literal grader may want the reading-2 fallback named; decision 7 is the real exposure. M06: VAE for "representation learning" is in the rubric's own words; the stretch is the display/qualitative evaluation of generated patterns; the PAH dry-run tensors are shared between M05 test and M06 train. |

---

## What would settle it

In the order they decide things; every one fail-closed; the first five cost no coupled-cluster
energy at a displaced geometry, or almost none.

1. **One canonical CCSD(T) point of benzene in the anchor basis on the B2 laptop** (finding 8):
   wall-clock and peak memory. Decides whether a bias line exists at R0 and in which basis. Hours.
2. **M1 at displaced geometries with the assignment log** (findings 5, 17): E(frozen) − E(fresh)
   in µE_h along one totally symmetric, one degenerate and one non-symmetric benzene mode; the
   maximal-overlap permutation printed per point. Decides whether E_frozen is smooth on a D₆h
   molecule at all. Tens of frozen-space energies of benzene.
3. **The noise-injection column of the zero-CC dry run** (finding 2): the dry-run recovery with
   Gaussian noise at a grid of σ_E values added to every response; K and ρ printed per σ_E. Zero
   CC cost; tells the author, before the note, at which noise floor any K short of K_cap exists,
   and fixes the ρ\* rule's form with numbers the R1 scatter will later select from.
4. **M03's band-centre uncertainty for the NIST R2 spectra** (finding 6): resolution, centroid
   precision and a temperature term per band, and the decidability verdict per family — printed
   before the pilot note. Zero CC cost. Decides which R2 families can ever be "beat" on gas data.
5. **The R1 smoothness probe with finding 1's estimator** (≈ 30 energies, as planned), followed by
   Round 7's items in Round 7's order: diagonal-only vs full recovery at R1; the anthracene
   direct-block Hessian; the pyrene canonical diagonal check.
6. **M2 with the stop_gradient difference printed** (finding 5): two extra gradient evaluations at
   one displaced naphthalene geometry per Q6 mode; the printed number is the size of §1.2's hole.
7. **Fragment-radius convergence of an interior block** (finding 4), first on circumcoronene's
   central ring at r_max and r_max + one ring (fragment-size cost, laptop or small B3), then on the
   R6 flake's interior. Decides whether fragments are a licence or a hope, before any R6 job.

Until 1–4 have printed, the R0–R1 programme is a green light and nothing above R1 is a promise
the plan can make about its own outcome. Do not go back to plan 04. Do not describe the R2 C–C
families as decidable on the NIST scoreboard. Do not call anything on the R6 interior "licensed"
until a fragment has been compared with something larger than itself.

---

*Pass B complete. No frozen document was edited. Facts verified this pass are listed at the top
with how they were opened; the SRD 35 resolution statement and the Pinski–Neese sentence are
snippet grade and are marked so wherever used; the QM9 size range and the lightpipe temperatures
are recalled. Verify-on-use still applies to everything here before it enters a scored document.*
