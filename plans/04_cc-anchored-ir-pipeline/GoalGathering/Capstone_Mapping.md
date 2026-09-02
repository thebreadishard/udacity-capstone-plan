# Capstone mapping — Plan 04 CC-Anchored IR Pipeline

**Status.** Draft as of 2026-09-02. Passes 1–5 written; Pass 6 (module-by-module sign-off) not
done. Not complete as a plan.

Rubrics: [`Rubrics/`](../../../Rubrics/) at repo root, version **1.5.1**, treated as fixed.
**Read them through [`Rubrics/README.md`](../../../Rubrics/README.md):** the Module 03/04
"Accepted Sources" lists are *examples of public sources, not a closed gate*; a self-computed
corpus qualifies **if it is published and reachable before the module begins** (public GitHub or
Zenodo DOI); "not synthetic or AI-generated" forbids model-generated *training data*, not
computed ab initio data — and every report says so in one sentence.

Prime directive: [Overarching_Goal.md](Overarching_Goal.md). Opponents:
[Frozen_Lines_to_Beat.md](Frozen_Lines_to_Beat.md). Ladder:
[Frozen_Ladder_and_Tolerances.md](Frozen_Ladder_and_Tolerances.md). Caps:
[Compute_Budget_2026-09-02.md](Compute_Budget_2026-09-02.md).

---

## 0. The one rule of this mapping (2026-09-02, user directive)

**Every module artifact is a load-bearing part of the pipeline.** No module exists to
demonstrate a known conclusion (no "EDA on QM9 to learn that DFT-level data is not
CC-precision" — that lesson is already paid for). If a rubric cannot be satisfied by something
the pipeline genuinely needs, the mapping **stops and the options go back to the user** — the
gap is not papered over with busywork. Tags below name each module's contribution to the end
goal, not a rubric category.

## 1. Rubric matrix (Pass 1)

Folder numbers (the rubric's internal "Project 1" = module 02).

| # | Module | Technique bar | Dataset bar | Landmines |
|---|---|---|---|---|
| 02 | AI Programming Foundations | No ML; pandas/NumPy EDA, ≥3 figures | public tabular, ≥200 rows, ≥5 cols ("or use your own") | must not train anything |
| 03 | Statistical analysis | descriptive + ≥1 hypothesis test | public **before module starts**, ≥500 rows, ≥6 cols, numeric + grouping; not the 02 file | sources list = examples, not a gate (per Rubrics/README); pre-register the test |
| 04 | Applied ML | sklearn or PyTorch; supervised/unsupervised | public before start; **not the 02 or 03 dataset** | distinctness is the real bar, not the portal name |
| 05 | Deep learning | PyTorch; CNN **or** RNN **or** Transformer; one controlled comparison | benchmark or curated real-world; not reused from 02–04 | declare the model family explicitly |
| 06 | Generative AI | GAN/VAE/diffusion/Transformer | public or clearly documented; not reused as the 05 training split | generated samples are never a dataset |
| 07 | Agentic | agent + memory + ≥1 tool + logging + safeguards + diagram | none | ethics tied to *this* agent |
| 08 | Industry synthesis | integrate ≥3 of 02–07; 1,500–2,000 word paper | reuse by design | trace the integrated modules explicitly |
| 09 | Defense | 15 min oral | — | defend the refusals and the accuracy/reach split |

## 2. The pipeline's own needs (Pass 2)

What the end goal requires, independent of any rubric:

| Need | Where it lands |
|---|---|
| A machine-readable **opponent table** (line A's predictions, queryable) | M02 |
| A **lab scoreboard** with measured tolerances (matrix vs gas shifts, per family) | M03 |
| The strongest **fair cheap baseline** + a per-band error model of scaled-harmonic DFT | M04 |
| The **anharmonic ML correction** on CC-anchored points (the thesis) | M05 |
| **Sampling efficiency** for the DLPNO point factory (node-hours are the scarce currency) | M06 |
| A **campaign officer** that runs multi-day queues and refuses ungated claims | M07 |
| The assembled pipeline, the R0–R3 comparisons, the R6 reach, the paper | M08 |

Every row above must exist for the pipeline to work. That is the anti-busywork proof: delete
any module's artifact and a later rung stops.

## 3. Module map (Pass 3)

### Module 02 — the opponent atlas

**Contribution.** The beat-comparison's right-hand side. Parse the public PAHdb v4.00
theoretical library (XML download, astrochemistry.org) into a tidy band table: species uid,
formula, charge, size, band position, intensity, scale factor applied, basis (6-31G* vs 4-31G).
EDA (no ML): coverage by size/charge/band family; where the 4-31G regime starts; which ladder
rungs (R0–R6) have entries and how many isomers sit at C₃₈₄H₄₈-class — the input to the R6
target choice.

**Rubric fit.** Public tabular data (≥10⁴ species → ≥10⁵ band rows), documented cleaning,
figures, no training. Module 02 explicitly allows "or use your own dataset"; this one is
NASA-public.

**Required sentence.** "This table is parsed from the public NASA Ames PAHdb v4.00 computed
library (DOI 10.3847/1538-4365/ae1c38). It is computed science data, not AI-generated, and it
is the *opponent* of this project's pipeline, not its training data."

### Module 03 — the scoreboard and the measured tolerance

**Contribution.** The lab truth the whole plan is scored against, plus the number the ladder
currently only asserts: the **matrix tolerance**. Dataset: PAHdb *experimental* libraries
(v3.10 matrix, 84 species; gas-phase v1.00) plus NIST WebBook JCAMP gas-phase spectra (working
parser + cache recipe: plan-02 `probes/verify_oop_bands_2026-08-27.py`; band reads with
recorded uids: plan-02 `probes/pahdb_experimental_2026-08-28.py` — both git history,
regenerated under this plan's hash per probes/README item 2). Descriptive statistics per band
family; **pre-registered hypothesis test** (form frozen before the data is joined): *matrix-to-gas
band shift is zero* per band family — two-sided, declared α, inconclusive allowed. Output
feeds §4 of the ladder: the pilot note's band lists and the measured (not conventional)
matrix tolerance (pilot-note item 4).

**Rubric fit.** Public before start (both sources are public downloads today); ≥500 rows
(84 species × bands), ≥6 columns, numeric + grouping (band family / phase / charge); distinct
from M02 (laboratory measurements vs computed predictions — different provenance, different
physical quantity). Sources are not on the example list; per Rubrics/README that list is not a
gate — the report cites the DOIs and says so.

**Required sentence.** "These are laboratory measurements from the public PAHdb experimental
libraries and NIST WebBook. Not synthetic, not AI-generated, not the Module 02 dataset."

### Module 04 — the cheap line, built in-house

**Contribution.** The strongest *fair* baseline the thesis must beat, plus the uncertainty
layer for reach rungs. Supervised sklearn model: molecular/band descriptors (size, charge,
adjacency-class counts, boundary-edge statistics) → per-band **error of scaled-harmonic DFT
against the lab band** (the Ethereal-AI-class approach, our own implementation). Two uses:
(1) a calibrated harmonic baseline — if the anharmonic pipeline cannot beat *corrected*
harmonic DFT, that is the honest headline; (2) the per-band uncertainty estimate attached to
R4–R6 reach spectra, where no lab exists.

**Dataset — distinctness DECIDED (user, 2026-09-02): reading 1 of two.** The rubric bar in
play is the **reuse rule** ("not the same dataset used in Projects 1 or 2"), not the
Accepted-Sources note — that note only covers portal names. The training table is the *paired*
theory↔lab band match (M02 opponent atlas joined to the M03 scoreboard), published as its own
versioned release (Zenodo DOI) **before Module 04 starts**. *Reading 1 (adopted):* the pair
table is distinct — new DOI, new columns (the residual), new unit of analysis (matched pair) —
and the report carries one explicit provenance paragraph saying exactly that. *Reading 2
(rejected for now):* a derived join is reuse; under that reading Module 04 would need an
independent public vibrational benchmark, found and verified at that moment — none is named
here from recall. Mentor pre-approval is **not** sought in advance (user decision, same date);
if a grader or mentor later applies reading 2, the fallback above executes.

**Q4 exception, declared.** This module trains on lab residuals *by design* and is therefore
the single declared exception to the Distilled §4 lab-leak rule: it is evaluated strictly
leave-molecule-out, its recipe (features, tuning budget, seeds) is frozen in the pilot note
(Ladder §4.6), and its outputs never enter the pipeline's training or its spectra — they
appear in exactly two report roles: an opponent column in P2, and the labelled empirical
component of the reach-rung error budget (P5). Those two roles are use (1) and use (2) above,
and there is no third.

**Required sentence (reading 1).** "The training table is a published derived dataset (DOI …)
matching public computed bands to public laboratory bands; its provenance and distinctness
from the Module 02/03 datasets are described in §…; it is not AI-generated."

### Module 05 — the thesis: CC-anchored anharmonic correction

**Contribution.** The object the whole plan exists for. Per-molecule ML surface / correction
trained on self-generated DLPNO-CCSD(T) points (geometries along normal modes and short MD),
with the R1 DLPNO-vs-canonical check as the anchor's license — a **conditional** license: if
canonical (T) cannot run at R1 on the new machine, it downgrades to R0-only plus a declared
cross-basis protocol (Ladder §2 R1), and every anchor claim says so.

**Dataset.** Own computed corpus, **published (Zenodo DOI, deck hashes) before Module 05
starts** — that publication step is a blocking precondition, exactly the plan-03 A1/A2/A3
lesson, except the corpus is ours and the timeline is ours.

**Model family (declare explicitly, rubric requires CNN/RNN/Transformer).** Frozen intent:
**Transformer-family** (attention over atom/internal-coordinate tokens — the DetaNet-class
choice). If distillation later argues for a non-Transformer architecture, that is a rubric
conflict and it goes back to the user *before* training, not after.

**Controlled comparison (one axis, frozen).** **Δ-learning vs direct-learning:** DFT-baseline
+ learned Δ-to-DLPNO against a direct DLPNO fit, same splits, same budget, ≥3 seeds. This axis
*is* the thesis question (what does the CC anchor buy?), so the rubric's required comparison
and the scientific claim are the same experiment.

**Required sentences.** "The training corpus is a published computational dataset generated by
the named decks (DOI …, hashes …); computed ab initio data, not AI-generated." "The laboratory
scoreboard is never a training, validation, or stopping input."

### Module 06 — generative sampling for the point factory

**Contribution.** Node-hours are the scarce currency (budget B3), and sampling error is a
named risk in the prime directive. A generative model (frozen intent: **VAE** over
displacement/internal-coordinate space, trained on the published geometry corpus from R0–R2
sampling) proposes candidate geometries scored by an acquisition rule; every accepted
candidate gets a **real** DLPNO/DFT label before it enters any training set. Success metric,
pre-registered: label-efficiency — fit quality at matched point count vs normal-mode/MD
sampling alone. If the VAE does not beat plain sampling, that result is published as the
honest outcome; the rubric is satisfied either way.

**Dataset.** The published geometry corpus (own Zenodo release), **new split hash**, never the
Module 05 label set itself. Generated geometries are model *output* and are never shipped as
data; only their subsequently computed labels are.

**Ethics (tied to this run).** Fabricated geometries entering science if the always-label rule
is skipped; a surrogate's samples mistaken for physical configurations; energy cost of
sampling vs the node-hours saved.

### Module 07 — the campaign officer

**Contribution.** R2+ runs are multi-day unattended queues (plan-02 machinery, git history)
across two machines and, later, a cluster. The agent is the governance made executable:
persona = conservative lab officer. Tools: `queue_submit` (wraps the batch runner),
`check_deck_hash`, `check_budget` (reads the three-budget doc; refuses cluster submission
unless the §3 preconditions of the budget file are met), `run_probe`, `write_certificate_or_refuse`.
Memory: the frozen ladder, the budget caps, the pilot note. Safeguards: may not emit a
"beat" sentence without the pilot note hash + the paired-comparison probe output; may not
start a reach rung before R3 is scored. Observed failure case for the report: poisoned deck
hash → refusal, logged.

**Rubric fit.** Single agent, memory, tools, logging, architecture diagram, one concrete
decision (submit R2 batch / refuse cluster job). No dataset.

### Module 08 — the pipeline, assembled and scored

**Contribution.** The end goal itself. Integrates (frozen three, trace in the paper): **M03**
(scoreboard + measured tolerance), **M05** (anharmonic correction), **M07** (officer running
the campaigns); M04's baseline appears inside every comparison table. Artifact: a small CLI /
service — molecule identifier in → spectrum + per-band error budget + certificate out, **or a
refusal naming the rung/cap/gate that blocked it**. Runs: R0–R3 accuracy comparisons under
the pilot note; R6 reach demonstration; tier-1 emission post-processing via the published
cascade model, labelled inherited. Paper (1,500–2,000 words): industry frame per the
Overarching Goal; the accuracy/reach split stated; losses and inconclusives reported as such.

### Module 09 — defense

Defend: the relative-and-measured criterion (why "beat the named lines" is stronger science
than "chemical precision"); the accuracy/reach split at C₃₈₄H₄₈; the refusals (cluster
preconditions, reach-before-R3 ban); and the expected question "isn't this just Mai 2025 with
extra steps?" — answer: Mai's ceiling is its DFT teacher; this pipeline's anchor is
R1-checked local-CC, and the Δ-learning comparison measures exactly what that buys.

## 4. Distinctness and DOI-before-claim (Pass 4)

| Module | Dataset | Source class | Published before start? | Reused? |
|---|---|---|---|---|
| 02 | PAHdb v4.00 computed band table | NASA public download | yes (public today) | no |
| 03 | PAHdb experimental v3.10 + gas v1.00 + NIST JCAMP | NASA/NIST public | yes (public today) | no — measurements, not the 02 predictions |
| 04 | paired theory↔lab table, own versioned release | derived, Zenodo DOI | must be, before M04 | distinct per reading 1 — **decided by user 2026-09-02**; provenance paragraph required |
| 05 | own DLPNO corpus, deck hashes | computed, Zenodo DOI | must be, before M05 | no |
| 06 | own geometry corpus, new split hash | computed, Zenodo DOI | must be, before M06 | source shared with 05 pipeline, split disjoint by hash |
| 07 | — | — | — | — |
| 08 | — | integrates 03, 05, 07 (+04 baseline) | — | reuse by design |

DOI-before-claim: no notebook writes its source sentence before the identifier exists in
[Relevant_Scientific_Papers.md](Relevant_Scientific_Papers.md) or a dated freeze note.
"Not AI-generated" sentences required in 02, 03, 04, 05, 06 as written above.

## 5. Open items — all three RESOLVED by the user on 2026-09-02 (Pass 5)

1. **Module 04 distinctness reading — DECIDED: reading 1** (derived pair table is distinct;
   own DOI + provenance paragraph). See §3 M04.
2. **Module 05 model family — NOTED.** Transformer-family stands as frozen intent; any
   architecture outside CNN/RNN/Transformer is a rubric conflict that returns to the user
   *before* training.
3. **Mentor pre-approval — NOT REQUIRED in advance** (user decision). The plan proceeds; an
   unexpected "no" later is handled when it happens, with the declared fallbacks. This
   supersedes the carried plan-01/02/03 recommendation to seek written approval first.

## 6. Ordering and hours (structure)

02 → 03 → 04 (each feeds the next: atlas → scoreboard → baseline). R0 pilot may run in
parallel with 02–03 (it is probe work, budget B2). M05 blocked on: R1 check + corpus DOI.
M06 blocked on: geometry corpus DOI. M07 may start as soon as the ladder + one probe exist;
it must refuse everything it cannot certify. M08 assembles; it trains nothing new. Human
hours per bucket: see the budget file (B1 table); this file adds no numbers.

Pass 6 (module-by-module sign-off) is **not** done. This mapping is a draft.
