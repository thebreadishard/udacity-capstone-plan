# Capstone mapping — Plan 05 Δ-Probed IR Pipeline

**Status.** Draft as of 2026-09-03, revised 2026-09-04 after the user's decisions, Round-8 (A, B),
Round-9 (A, B) and Round-10 (A, B), for the promised set as decided (Δ₂ only; mode E guaranteed, mode G built in the side
project; R6 fragment-probed under the fragment licence). Passes 1–5 written; Pass 6
(module-by-module sign-off) not done (the user asked to wait with it, 2026-09-04); text otherwise
frozen 2026-09-04 with the rest of the plan-05 set; decision 7 closed 2026-09-04, so nothing blocks it. Not complete as a
plan.
Where plan 05 inherits plan 04's module design unchanged, this file says "carried" and does
not re-argue it; plan 04's mapping (in its folder) is the argument of record for those parts.

Rubrics: [`Rubrics/`](../../../Rubrics/) at repo root, version **1.5.1**, treated as fixed.
**Read them through [`Rubrics/README.md`](../../../Rubrics/README.md):** the Module 03/04
"Accepted Sources" lists are *examples of public sources, not a closed gate*; a self-computed
corpus qualifies **if it is published and reachable before the module begins** (public GitHub
or Zenodo DOI); "not synthetic or AI-generated" forbids model-generated *training data*, not
computed ab initio data — and every report says so in one sentence.

Prime directive: [Overarching_Goal.md](Overarching_Goal.md). Opponents:
[Frozen_Lines_to_Beat.md](Frozen_Lines_to_Beat.md). Ladder:
[Frozen_Ladder_and_Tolerances.md](Frozen_Ladder_and_Tolerances.md). Gates:
[Distilled_Project_Plan_and_Quality_Checks.md](Distilled_Project_Plan_and_Quality_Checks.md).
Costs: [Compute_Budget_2026-09-03.md](Compute_Budget_2026-09-03.md).

---

## 0. The one rule of this mapping (2026-09-02 user directive, carried)

**Every module artifact is a load-bearing part of the pipeline.** No module exists to
demonstrate a known conclusion. If a rubric cannot be satisfied by something the pipeline
genuinely needs, the mapping **stops and the options go back to the user** — the gap is not
papered over with busywork. Tags below name each module's contribution to the end goal.

Plan 05 had one module where this rule bit and was escalated rather than papered over:
**Module 05**. The user decided it on 2026-09-04 (§3 M05; Goal decision 4): adopted, with the
learned prior **earning a licence on R2–R3 and spending it on R4–R6** (Ladder §3) — on the
reach rungs it is load-bearing for the spectrum and the cost record; on R0–R3 the scored
spectra are always structural. Everything else is load-bearing for the promised spectra or for
the promised cost record.

## 1. Rubric matrix (Pass 1; carried from plan 04, checked against the rubric files 2026-09-03)

Folder numbers (the rubric's internal "Project 1" = module 02).

| # | Module | Technique bar | Dataset bar | Landmines |
|---|---|---|---|---|
| 02 | AI Programming Foundations | No ML; pandas/NumPy EDA, ≥3 figures | public tabular, ≥200 rows, ≥5 cols ("or use your own dataset as long as it meets the project requirements") | must not train anything |
| 03 | Statistical analysis | descriptive + ≥1 hypothesis test | public **before module starts**, ≥500 rows, ≥6 cols, numeric + grouping; not the 02 file | sources list = examples, not a gate; pre-register the test |
| 04 | Applied ML | sklearn or PyTorch; supervised/unsupervised | public before start; **not the 02 or 03 dataset** | distinctness is the real bar |
| 05 | Deep learning | PyTorch; "CNN, RNN, or Transformer"; problem domain "image, text, or sequence"; ≥1 **controlled** comparison ("state what changed and what stayed the same"); "High accuracy is not required" | "publicly available … not synthetic or AI-generated … **Not be reused from any previous capstone project**"; "standard benchmark datasets or curated real-world datasets" | declare the model family and the domain explicitly; the reuse clause |
| 06 | Generative AI | GAN/VAE/diffusion/Transformer | public or clearly documented; not reused as the 05 training split | generated samples are never a dataset |
| 07 | Agentic | agent + limited memory + ≥1 tool + logging/safeguards + architecture diagram; "tools you already know" | none | ethics and safeguards tied to *this* agent |
| 08 | Industry synthesis | integrate ≥3 of 02–07; paper | reuse by design | trace the integrated modules explicitly |
| 09 | Defense | oral | — | defend the refusals, the accuracy/reach split, and the cost record |

## 2. The pipeline's own needs (Pass 2)

What the end goal requires, independent of any rubric:

| Need | Where it lands | Changed from plan 04? |
|---|---|---|
| A machine-readable **opponent table** (line A's predictions, queryable) | M02 | no |
| A **lab scoreboard** with measured tolerances (matrix vs gas shifts; **the measured band-centre uncertainty u_band per band** that the decidability rule consumes) | M03 | extended |
| The strongest **fair cheap baseline** + a per-band error model of scaled-harmonic DFT (the M04 calibrated harmonic, the opponent column and the reach-rung uncertainty layer) | M04 | no |
| The **Δ₂ recovery solver** (banded structural prior; classical convex optimisation) — the promised object on R0–R3 | pipeline infrastructure, exercised by the R0 dry run; **not a module's ML artifact** | new |
| A **frozen-space local-CC code** (probe M1) | pipeline infrastructure, main project, under Ladder stop 1 | new |
| A learned **Δ₂-support predictor** that earns a licence on R2–R3 and is spent on R4–R6 (the P3 arm) | M05 | replaces the learned surface |
| **Pattern-proposal efficiency** for the probe batches (K_off is the scarce quantity) | M06 | replaces geometry sampling |
| A **campaign officer** that runs multi-day probe queues, enforces the classification rule and the two cost-sentence forms, and refuses ungated claims | M07 | extended |
| The assembled pipeline, the R0–R3 comparisons, the cost records, the fragment-probed R6 or its measured refusal, the paper | M08 | extended |

Delete M02, M03, M04, M07 or M08 and a promised rung stops. Delete M05 and the R4–R6 reach
rungs lose their licensed prior (they still run, structurally, at higher cost); delete M06 and
pattern efficiency beyond the deterministic deck stops. That asymmetry is stated, not hidden
(§3 M05, M06).

## 3. Module map (Pass 3)

### Module 02 — the opponent atlas (carried from plan 04)

**Contribution.** The beat-comparison's right-hand side. Parse the public PAHdb v4.00
theoretical library into a tidy band table: species uid, formula, charge, size, band position,
intensity, scale factor applied, basis (6-31G* vs 4-31G). EDA (no ML): coverage by size,
charge and band family; where the 4-31G regime starts; which rungs have entries; **which
C₃₈₄H₄₈-class species exist** (frozen-lines debt 6) — the input to the R6 target choice and,
to the count of symmetry-unique local environments the fragment-probed R6 needs (decided
2026-09-04).

**Rubric fit.** Public tabular data (≥10⁴ species → ≥10⁵ band rows), documented cleaning,
figures, no training. Module 02 allows "or use your own dataset"; this one is NASA-public.

**Required sentence.** "This table is parsed from the public NASA Ames PAHdb v4.00 computed
library (DOI 10.3847/1538-4365/ae1c38). It is computed science data, not AI-generated, and it
is the *opponent* of this project's pipeline, not its training data."

### Module 03 — the scoreboard, the measured tolerance, and u_band (carried, extended)

**Contribution.** The lab truth the whole plan is scored against, plus two numbers the ladder
only asserts until this module measures them: the **matrix tolerance** (pilot-note item 4) and
the **measured band-centre uncertainty u_band per gas-phase band** (the decidability rule of
Ladder §2: the source's stated resolution — the NIST/EPA GC-IRD spectra are homogenised to
8 cm⁻¹ at snippet grade, item 50, never the 4 cm⁻¹ point spacing — the centroid precision from
the signal-to-noise, and a temperature term for hot-vapour sources with the Ladder §2 floor or a
pinned hot-band correction, items 52–53; the source class, temperature and resolution printed as
columns; printed per family before the pilot note, with the verdict *gas-decidable /
matrix-gated / inconclusive by construction*; the R2 C–C families are expected in the last class unless the correction is pinned;
R1 is expected decidable throughout on the PNNL/NWIR room-temperature record, its hot WebBook
entries scored as labelled hot columns). Dataset: PAHdb
*experimental* libraries (v3.10 matrix, 84 species; gas-phase v1.00) plus the PNNL/NWIR naphthalene record (items 57, 59), the jet-cooled band lists for tetracene and coronene (items 61–62, labelled cold columns; Ladder §2 dated note 2026-09-05) and NIST WebBook JCAMP
gas-phase spectra (plan-02 parser and cache recipe, git history; plan-04 coverage probe and
`nist_cache/`). Descriptive statistics per band family; **pre-registered hypothesis test**
(form frozen before the data is joined): *matrix-to-gas band shift is zero* per band family —
two-sided, declared α, inconclusive allowed. Output feeds pilot-note items 1, 2 and 4. M03 is also where the supervisor's help with
gas-phase or jet-cooled sources (Proposal §13.3) becomes load-bearing: without such a source the
R2 C–C families cannot be decided on gas data.

**Rubric fit.** Public before start; ≥500 rows; ≥6 columns; numeric + grouping (band family /
phase / charge); distinct from M02 (measurements vs computed predictions). Sources are not on
the example list; per Rubrics/README that list is not a gate — the report cites the DOIs and
says so.

**Required sentence.** "These are laboratory measurements from the public PAHdb experimental
libraries and NIST WebBook. Not synthetic, not AI-generated, not the Module 02 dataset."

### Module 04 — the cheap line, built in-house (carried from plan 04, with its decided reading)

**Contribution.** The strongest *fair* baseline the thesis must beat, plus the uncertainty
layer for reach rungs. Supervised sklearn model: molecular/band descriptors → per-band **error
of scaled-harmonic DFT against the lab band** (the Ethereal-AI-class approach, our own
implementation). Two uses: (1) the calibrated harmonic opponent column in P2 — Round-7 Pass B
issue 7 says out loud what this column does: it absorbs the *mean* of a ~5 cm⁻¹ harmonic
CC−DFT difference per family, so Δ₂ has to buy the per-family scatter; (2) the per-band
uncertainty estimate attached to R4–R6 reach spectra.

**Dataset — reading 1 (decided by the user 2026-09-02 for plan 04; carried).** The paired
theory↔lab band table (M02 atlas joined to the M03 scoreboard), published as its own versioned
release (Zenodo DOI) **before Module 04 starts**, with a provenance paragraph stating its
distinctness from the M02/M03 datasets. Fallback if a grader applies reading 2: **NIST CCCBDB**
(bib 21), second option **VIBFREQ1295** (bib 22). Mentor pre-approval not sought in advance
(user decision, carried).

**Q4 exception, declared (carried).** Trains on lab residuals by design; leave-molecule-out;
recipe frozen in the pilot note (item 6); outputs appear only as the P2 opponent column and the
P5 empirical uncertainty layer.

**Required sentence (reading 1).** "The training table is a published derived dataset (DOI …)
matching public computed bands to public laboratory bands; its provenance and distinctness
from the Module 02/03 datasets are described in §…; it is not AI-generated."

### Module 05 — the Δ₂-support predictor (the P3 arm; decided by the user 2026-09-04)

**Contribution.** The efficiency experiment plan 05 keeps off the promised path on purpose
(Ladder §3; Distilled §5). A **Transformer** (equivariant attention over atom / DFT-mode
tokens) predicts the **support of Δ₂ in the DFT normal-mode basis** — which off-diagonal blocks
between which DFT modes are large — from DFT-level features (mode frequencies, compositions,
atomic environments). That is the Concordant Mode Approach's Level-C diagnostic (bib 43)
learned instead of computed. Its output is a **learned prior** for the recovery: scored on the dry-run corpus (P3);
**earned** on R2 and R3 by running both recoveries on the same responses and agreeing with the
structural Δ₂ per family within τ₇ (direct couplings within η₈·S); **spent** on R4–R6, where a
prior-assisted recovery may be the only full recovery and the certificate says the spectrum
depends on it (Ladder §3) — user directive 2026-09-04: inheritance is not authority.

**Why it is load-bearing, and for which rungs.** K_off is the guaranteed route's open cost
quantity. A predictor that names the large off-diagonal blocks before any local-CC response
exists lets the deck place explicit two-mode patterns where they matter — the one lever on
K_off that costs no CC energies. On **R0–R3 the scored spectra are always the structural
recovery**; there the prior is measured (P3 on the dry-run corpus; the licence-earning
comparison on real responses at R2 and R3) and never load-bearing. On **R4–R6**, once the
licence is earned at both R2 and R3, the prior-assisted recovery may be the only full recovery:
there M05 is load-bearing for the spectrum and the cost record, and the certificate says so.
Rule 0 therefore holds in the strong form for the reach rungs and in the weak form for the
accuracy rungs. That conditional was escalated as decision 4 and **decided on 2026-09-04:
adopted**, with the three specifications below (aromatic-heavy subset; licence as the success
criterion; reading 1 with the reading-2 fallback).

**Dataset (Round-7 Pass B issue 9; Distilled §6; decided 2026-09-04).** Seven probed local-CC
Δ₂ tensors by R3 is not a deep-learning corpus. The corpus is therefore DFT-vs-DFT at scale:
the public **Hessian QM9** set (bib 47: 41,645 molecules, ωB97x/6-31G* Hessians) plus
**B3LYP/6-31G* Hessians recomputed on an aromatic-heavy QM9 subset** — benzene derivatives and
conjugated rings over-represented; **the subset's size is fixed by a dated note after the
zero-CC dry run has printed the B2 laptop's per-molecule Hessian timing** (no size appears
here; Round-8 Pass A issue 10) — giving Δ₂ = ωB97x − B3LYP per molecule with the exact-exchange contrast the dry run needs.
QM9 molecules have at most nine heavy atoms (recalled by the Round-8 reviewer; verified when
the corpus is built), so the corpus contains no PAH larger than benzene and is off-distribution
from every rung: the PAH dry-run tensors and the probed tensors from the rungs that have run are
a **held-out test set only**, and P3's effect size is reported on them as well as on the corpus. Published as its own release (Zenodo DOI, deck hashes) **before
Module 05 starts**.

**Problem domain and model family (rubric).** Domain: **sequence** (a molecule as a sequence of
DFT-mode tokens with atomic-environment features; the target a per-token-pair label). Model:
**Transformer**. Both declared explicitly; anything outside CNN/RNN/Transformer returns to the
user before training.

**Controlled comparison (rubric; frozen in Distilled §5).** **Learned prior vs structural
prior at matched K**, on the dry-run corpus: same patterns, same held-out set, same solver, ≥3
seeds; what changed = the prior; what stayed the same = everything else. Metric: ρ at fixed K,
and K to reach ρ\*. Effect size: pilot-note item 5. **The success criterion is the licence, not
accuracy**: does the prior save patterns on the corpus, and does the prior-assisted recovery on
a real rung agree with the prior-free check? "High accuracy is not required" — the outcome is
publishable either way.

**Distinctness — the reuse clause, reading 1 (confirmed by the user 2026-09-04 under decision
4).** The rubric's bar is "not be reused from any previous capstone
project" and "publicly available … before this project starts". Hessian QM9 is public today.
**Decision 7 (2026-09-04) closes the QM9 question**: no capstone module has been submitted; the
student's draft Foundations repository on QM9 was never submitted and will be renamed or
archived, so Hessian QM9's parent set carries no module-02 reuse exposure. The reading-2 fallback
(a different public Hessian source) stays a named debt as ordinary insurance, to be searched and
verified before Module 05 starts; none is named from recall. The recomputed B3LYP side is new computed data produced for
this module. The derived Δ₂ tensors are a new quantity with their own DOI. Under reading 1 the
corpus is distinct; the report carries a provenance paragraph saying exactly that and stating
that the PAH dry-run tensors were computed under plan 05's `probes/` and appear in no earlier
module's dataset. Under reading 2 (any corpus containing data computed for another module is
reuse), the PAH dry-run tensors are dropped from the M05 training set and kept only as a
labelled test set; Hessian QM9 plus the recomputed B3LYP side alone satisfies every clause.
Both readings are executable mid-module.

**Q3/Q4.** Splits by molecule (meaningful at 10⁴ molecules), hashed. No lab data anywhere in
the corpus, so Q4 is trivially clean.

**Required sentences.** "The training corpus is the public Hessian QM9 set (arXiv:2408.08006)
plus B3LYP Hessians recomputed by the named decks (DOI …, hashes …); computed ab initio data,
not AI-generated; not used in any earlier capstone module (decision 7: none submitted)." "The laboratory scoreboard is
never a training, validation, or stopping input." "On R0–R3 every scored spectrum is the structural recovery; the learned prior is spent only on
R4–R6 under the licence of Ladder §3, and every cost record says which prior it used."

### Module 06 — generative pattern proposal (the CC-free efficiency arm)

**Contribution.** K_off is the scarce quantity and the deterministic deck (O1NumHess-class
completion patterns plus dry-run-flagged two-mode patterns) is the promised way to spend it. A
generative model (frozen intent: **VAE** over the space of two-mode displacement patterns,
conditioned on the DFT mode structure of the molecule) proposes candidate patterns scored by
an acquisition rule (expected reduction of ρ under the structural prior); every accepted
pattern enters the **hashed, ordered deck before any response for that rung is computed** —
the plan's own rule (Distilled §6) — and is then evaluated by a real calculation like any
other pattern. Success metric, pre-registered: **pattern efficiency at zero CC cost** — on the
dry-run corpus, K_off to reach ρ\* with VAE-proposed patterns in the deck vs the deterministic
deck alone, matched everything else. If the VAE does not beat the deterministic deck, that is
the published outcome; the rubric is satisfied either way. On promised rungs the proposer may
add patterns to the deck *before the hash* (they are then ordinary patterns); it may never
touch the deck after any response exists.

**Dataset.** The **pattern-response records of the QM9-subset dry runs** (own computed corpus,
its own Zenodo release, **new split hash**) — distinct from M05's QM9-derived Δ₂ corpus in
quantity (responses to patterns, not Hessians) and, because the PAH dry-run tensors are M05's
held-out test set and are **excluded from M06's training data**, without cross-module overlap.
Generated patterns are model *output*, never shipped as data; only their computed responses
are.

**Display and qualitative evaluation (rubric Task 4).** A displacement pattern is neither an
image nor a sentence; the notebook renders generated patterns as displacement arrows on the
molecular frame beside deterministic-deck patterns, and evaluates them qualitatively against
three stated criteria: symmetry consistency with the molecule's point group, locality (the
pattern's atoms lie within r_max of each other), and non-redundancy with patterns already in
the deck; failure cases (patterns that duplicate the deck, or that displace atoms with no
shared family mode) are shown.

**Ethics (tied to this run).** A proposed pattern entering a deck after responses exist (the
pre-registration leak the hash rule prevents); a surrogate's proposals mistaken for a
measurement; the energy cost of proposal versus the node-hours it saves.

### Module 07 — the campaign officer (carried, extended for the cost record)

**Contribution.** R1+ probe batches are multi-day unattended queues across the laptop and,
later, B3 machines. The agent is the governance made executable: persona = conservative lab
officer. Tools: `queue_submit` (wraps the batch runner; refuses a batch whose deck hash does not
match Q0), `check_deck_hash`, `check_budget` (reads the classification rule with K_cap and
c_CPS; refuses B3 submission unless the budget file's preconditions are met), `run_probe`,
`print_cost_record` (emits Ladder §1's record form and nothing else), `write_certificate_or_refuse`.
Memory: the frozen ladder, the budget rules, the pilot note, the Q8 verdicts per family, the
two licences' status.
Safeguards, each a refusal with a logged reason: no "beat" sentence without the pilot-note
hash and the P2 probe output; no "decidable" verdict without M03's u_band for that family; no
rung R1–R3 batch without mode E; no "beat" from a mode whose Q6 noise line did not pass at the
rung's size class; no size sentence without Q8(c) output in both required ratios; **no cost
adjective anywhere** (a regex over the report draft is part of the tool); no learned prior in
an R0–R3 scored spectrum, and none on R4–R6 without the licence earned at both R2 and R3; no
reach rung before R3 is scored; no R6 job other than fragment-probed, and none before the
fragment licence's four parts (a), (b), (b′), (c) have passed ((b) passed or resolved by (b′)); no local-CC probe before probe M1 has passed; no
displaced-geometry local-CC gradient before the pilot note.
Observed failure cases for the report: a poisoned deck hash → refusal; a draft sentence
containing "size-independent" → refusal with the Ladder §1 citation.

**Rubric fit.** Single agent, limited memory, tools, logging, architecture diagram, concrete
decisions (submit the R2 batch / refuse the R6 job / strike a sentence). No dataset. Built
with the course's tools only.

### Module 08 — the pipeline, assembled and scored

**Contribution.** The end goal. Integrates (trace in the paper) **M02** (opponent atlas),
**M03** (scoreboard, matrix tolerance, u_band), **M04** (calibrated harmonic column and the
reach uncertainty layer) and **M07** (officer running the campaigns) — four, all on the
promised path; **M05** appears as the P3 experiment on R0–R3 and, if its licence was earned, as the
load-bearing prior of the R4–R6 certificates; **M06** as the pattern-efficiency experiment;
both labelled exactly so. Artifact: a small
CLI / service — molecule identifier in → spectrum + per-band error budget + **cost record** +
certificate out, **or a refusal naming the rung/cap/gate that blocked it**. Runs: R0–R1
expected unconditional under the pilot note (room-temperature sources named); R2–R3 per family
under the decidability rule and the per-mode Q6 noise gate; the fragment-probed R6 under its
four-part licence, or its measured refusal;
tier-1 emission post-processing via the published cascade model, labelled inherited. Paper:
industry frame per the Goal; the accuracy/reach split; the cost record table across rungs
with, if earned, the numeric size sentence; losses and inconclusives reported as such.

### Module 09 — defense

Defend: the relative-and-measured criterion; the accuracy/reach split; the refusals; the
cost record as a scientific deliverable (a database keeper can price a species); the decision
to promise Δ₂ only (the hybrid-QFF argument and the φ_ijk arithmetic); why mode E is the
promised route on the 2026-09-03 gradient landscape; and the expected questions "isn't this
CMA?" (answer: CMA is the diagonal part, cited; the off-diagonal recovery, frozen local CC at
PAH sizes, and the measured locality are the thesis), "why is mode E the guaranteed route?"
(answer: no production local-CC(T) gradient existed on 2026-09-03; the side project built one
or reported why not) and "isn't this just Mai 2025 with extra steps?" (answer: Mai's ceiling is
its DFT teacher).

## 4. Distinctness and DOI-before-claim (Pass 4)

| Module | Dataset | Source class | Published before start? | Reused? |
|---|---|---|---|---|
| 02 | PAHdb v4.00 computed band table | NASA public download | yes (public today) | no |
| 03 | PAHdb experimental v3.10 + gas v1.00 + NIST JCAMP | NASA/NIST public | yes (public today) | no — measurements, not the 02 predictions |
| 04 | paired theory↔lab table, own versioned release | derived, Zenodo DOI | must be, before M04 | distinct per reading 1 — decided by the user 2026-09-02 (carried); provenance paragraph required |
| 05 | Hessian QM9 + recomputed B3LYP Hessians → Δ₂ tensors; PAH dry-run tensors as labelled test set | public benchmark + own computed, Zenodo DOI | Hessian QM9 is; the release must be, before M05 | distinct per reading 1 (decision 4); decision 7 removes the module-02 exposure; reading-2 fallback a named debt |
| 06 | pattern-response records of the QM9-subset dry runs, own release, new split hash (PAH dry-run tensors excluded — they are M05's test set) | computed, Zenodo DOI | must be, before M06 | distinct from 05's QM9-derived Δ₂ corpus; no overlap with 05's test set; split disjoint by hash |
| 07 | — | — | — | — |
| 08 | — | integrates 02, 03, 04, 07 (+05, 06 as bonus reports) | — | reuse by design |

DOI-before-claim: no notebook writes its source sentence before the identifier exists in
[Relevant_Scientific_Papers.md](Relevant_Scientific_Papers.md) or a dated freeze note.
"Not AI-generated" sentences required in 02, 03, 04, 05, 06 as written above.

## 5. Open items (Pass 5)

Carried as decided for plan 04 (user, 2026-09-02): M04 reading 1; mentor pre-approval not
required in advance. New for plan 05, all routed to the Goal's open-decision list:

1. ~~M05 target and corpus~~ — decided by the user 2026-09-04: adopted as specified in §3
   M05 (aromatic-heavy subset; licence as success criterion; reading 1 with fallback).
2. ~~Open decision 7~~ — closed 2026-09-04: nothing submitted; the draft QM9 Foundations
   repository will be renamed or archived; M02 stands as planned. The M02 report's provenance
   paragraph mentions the renamed draft so no grader mistakes it for a submission.
3. ~~Fragment probing~~ — decided by the user 2026-09-04: a permitted method, licensed by Q8
   at R2–R3; M08 ships the fragment-probed R6 spectrum or its measured refusal.
4. ~~The R2 A-scored set~~ — decided by the user 2026-09-04 (re-read stands); M03's R2 band
   list covers pyrene, chrysene, triphenylene (gas) and tetracene (matrix).

## 6. Ordering and hours (structure)

02 → 03 → 04 (atlas → scoreboard → baseline), unchanged. The R0 pilot, the zero-CC dry run,
the gradient-availability probe and the R1 smoothness probe run in parallel with 02–03 (probe
work, budget B2) and must be printed before the pilot note; the pilot note is committed before
M04's opponent column is used in any comparison. M05 blocked on: the Hessian QM9 + B3LYP
corpus release. M06 blocked on: the dry-run corpus release. M07 may start as soon as the
ladder and one probe exist; it must refuse everything it cannot certify. M08 assembles; it
trains nothing new. Probe M1 (frozen spaces) is pipeline infrastructure and precedes every local-CC probe. The
mode-G side project (2026-09-04) starts after the pilot note, on its own B1 bucket with a
calendar 12-week checkpoint; it belongs to no module and its milestones M2–M5 are the
gradient-availability probe's answers at R0–R3. Human hours are **logged, never capped** (budget doc; user directive);
this file adds no numbers.

Pass 6 (module-by-module sign-off) is **not** done. This mapping is a draft.
