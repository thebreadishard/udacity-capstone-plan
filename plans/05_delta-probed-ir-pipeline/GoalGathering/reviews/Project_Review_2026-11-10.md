# Project review, 10 November 2026 — what is still needed to succeed

**Stamp:** 2026-11-10 11:0x. **Asked by the user:** "Doe een complete review van het project. Wat is er nog nodig om te slagen? Zet de
uitkomst in een file. Eerst een cold read, daarna inhoud. Wijzig nog niets."

**Status of this file.** It is the only thing this review wrote. Nothing else in the repository was changed: no TASKS row, no ledger
entry, no document corrected, no commit. Every finding below is therefore still open, and none has a row on the board yet.

## 1. The short answer

1. **The Udacity capstone is not yet passable, and the gap is in modules 08 and 09, not in the science.** Modules 02–07 are built and
   passed their dry runs on 18 October. Module 08's paper and notebook describe the system of 28 September–10 October; its own README
   says so. Module 08 has no submittable form and no presentation. Module 09 has nothing. Nothing has been submitted.
2. **Three of the four claims for 25 November stand; the first is open** and depends on two laptop runs (the v1.4 search and chain 42)
   that must both fit between 15 and 24 November with no room for a failed run.
3. **The documents a stranger opens first contradict the project.** The repository's front page and the plan's README say that no
   pipeline results exist; `REPRODUCE.md` stops at 27 September; the mapping to the Udacity modules is the draft of 3–4 September.
   The plan's stated method (probed local coupled-cluster energies) and its stated criterion (beat the best existing prediction per
   band against laboratory data) are not what was built or what decision 63 set, and no document says that the plan changed.
4. **The proof is a proof of method at DFT-proxy level.** That is what decision 63 decided, and it is a sound capstone result, but only
   if every entry document says it in its first paragraph. Today a cold reader takes the 2 cm⁻¹ numbers for accuracy against the truth
   and then finds that nothing supports that reading.
5. **The scarce resource from 15 November is one laptop.** The runs already promised to it exceed what a calendar has ordered
   (TASKS 192 is open); the cation fill alone is about 1,147 laptop hours of the roughly 2,520 wall hours to the end of February.

What is needed, in one line per date, is in section 4.6; the decisions that are the user's are in section 4.8.

## 2. Method, cost and limits

**Pass A, the cold read.** Two fresh readers with no knowledge of the project, each with a fixed list of files and an explicit budget.
Neither was given a hypothesis. Neither read one of the three large documents whole (the reading copy, the obstacle ledger; of the plan
README only lines 1–92), under the cost rule of `CLAUDE.md`.

| reader | role | read | cost |
|---|---|---|---|
| A1 | an outsider who wants to know what the project delivers and whether it has succeeded | thirteen documents: root `README.md`, plan `README.md` 1–92, `Projectvoorstel_2026-09-30.md`, `modules/PIPELINE.md`, `MODELS.md`, `ANCHORS.md`, `GLOSSARY.md`, the READMEs of modules 05 and 08, `REPRODUCE.md`, the data paper's README and supervisor outline, `docs/product_repo_design.md` | 131k tokens, 16 tool calls |
| A2 | a Udacity assessor holding rubrics 08 and 09 | `Rubrics/README.md`, rubrics 08 and 09, module 08's folder (README, checklist, standalone plan, pre-registration, provenance, backlog, `make_summary.py`), the READMEs of modules 02–07 | 159k tokens, 24 tool calls |

**Pass B, content.** My own reading of the task board (`tasks_board.py view`, the rows named below), `probes/state.sh`, the module
review of 17–18 October, `Capstone_Mapping.md`, and targeted greps of the ledger to test the cold readers' findings.

**Limits. A later reader may not build on more than this.**

- Modules 02–07 were **not** re-read against their rubrics today. Their state is the review of 17–18 October
  (`modules/REVIEW_2026-10-17.md`) and TASKS 20.
- No rendered PDF and no notebook was opened. Reader A2 could not open `Reflective_Synthesis_Paper.pdf` (no `pdftoppm`) and read the
  paper's text from its builder `make_summary.py`; layout and the current word count are unverified.
- The three large documents were not read whole. The Spectrum Atlas was not opened; no web check was made.
- Udacity's review turnaround, the order in which modules may be submitted and how module 09's session is booked were not verified.
- A cold reader's finding is a statement about what the documents say, not about what is true. Section 3.3 separates the two.

## 3. Part 1 — the cold read

Ranks are the readers' own: BLOCKING (stops the reader believing or passing it), SERIOUS, MINOR. Line numbers are theirs.

### 3.1 Reader A1 — the project as its documents present it

**What is delivered.** The reader found three different products in the documents:

- **A** (root `README.md:102-105`, plan `README.md:14-23`): a pipeline whose coupled-cluster correction is *probed* from local-CC
  energies, which must beat the best prediction available anywhere per band against laboratory data (`README.md:106-109`) and reach
  101–386 carbons (`README.md:114`); a network is "follow-up work outside the sequence" (`README.md:118-119`).
- **B** (`Projectvoorstel:8-13`): the same pipeline plus a network that learns the CC correction, "in 2027".
- **C** (`PIPELINE.md:3,25-28`, module 08 `README.md:24`, `product_repo_design.md:93-97`): what exists — SMILES in, B3LYP/6-31G*, a
  network (v1.3) that moves the Hessian toward ωB97X/6-31G*, a harmonic spectrum and a certificate; neutral closed-shell molecules,
  trained on 8–30 atoms; nothing claimed at coupled-cluster level.

No document the reader saw gives a submission date for any Udacity module.

**BLOCKING**

| # | finding | where |
|---|---|---|
| A1-1 | The entry documents say there are no results: "It contains **no pipeline results**", "**No rung has run**". The pipeline has certificates and a version 0.9. The two documents are dated 25 and 12 September. | root `README.md:7,80`; plan `README.md:5` against `PIPELINE.md:11`, module 08 `README.md:5`, module 05 `README.md:5` |
| A1-2 | The stated method is absent from what was built: no CC step, no probe and no probe count in the pipeline; the anchors are canonical CCSD(T) Hessians plus an MP2 basis step. The plan's title names a method the pipeline does not use. | root `README.md:103-104`, plan `README.md:19` against `PIPELINE.md:11`, `ANCHORS.md` |
| A1-3 | The stated criterion is to beat the best existing prediction per band against laboratory data. No document shows one pipeline band against one laboratory band or against PAHdb. The only laboratory number (1.2 cm⁻¹ RMS, three naphthalene bands) belongs to a B97-1 VPT2 route that is not in the pipeline. | root `README.md:106-109`, `Projectvoorstel:8-9`; `REPRODUCE.md:38` |
| A1-4 | Every accuracy number of the product is a distance to ωB97X/6-31G*. Nothing read shows that this target is nearer coupled cluster or the laboratory than B3LYP is. The documents themselves show a reference can be worse than the starting point (the cc-pVDZ anchor: 24.9 against 14.1 cm⁻¹). | module 05 `README.md:5,63` |
| A1-5 | `REPRODUCE.md` covers the package of 25 September, extended 27 September. It has no row for chain 35's training, the hold-out reads, the composite anchors, the pipeline certificates or the licence. A stranger "could not reproduce a single number of the carried network or of the pipeline". | `REPRODUCE.md:1-3` |

**SERIOUS**

| # | finding | where |
|---|---|---|
| A1-6 | All eleven carried anchors are "VALID" by "chain 33c's promotion rule"; the rule and its threshold are stated nowhere the reader saw. Two VALID rows cite soft modes within 19 and 38 cm⁻¹ of ωB97X (a DFT counterpart for a CC anchor); azulene's symmetry spread is 1.9e-03, about fifty times the other rows. | `ANCHORS.md:9,15,23,39` |
| A1-7 | E8's "98 %" reads `probes/results_m1/e8_benzene_ccpvdz/`, the Hessian `ANCHORS.md:30` marks invalid (lambda incident). No document the reader saw says it was read again. | module 05 `README.md:52`, `REPRODUCE.md:46` |
| A1-8 | T3's CC transfer (in-plane 5–6 against 25 cm⁻¹; out-of-plane 17–35) was read against the cc-pVDZ anchor, which the project later demoted. The only CC transfer number stands against a withdrawn reference. | module 05 `README.md:61,63`, `ANCHORS.md:31` |
| A1-9 | Module 08's README quotes 0.30 → 0.13 as the pipeline's accuracy; the source is a chain 34 file, which `MODELS.md:9` lists as superseded and `MODELS.md:3` calls "not evidence". | module 08 `README.md:17`, module 05 `README.md:64` |
| A1-10 | v1.3's 'other' on hold-out (a) is 3.62; its predecessor's was 3.35, and a candidate is carried only when "worse on neither hold-out". The hold-out went from ten to eight molecules in between; no document reconciles the two. | module 05 `README.md:5,63`, `PIPELINE.md:15` |
| A1-11 | The licence line is 3 cm⁻¹, read on eight molecules, without a spread. The answer moves by 2.9–10 cm⁻¹ with atom order and by 1.22 cm⁻¹ between a reused and a computed run; the composite anchors sit 3.3–4.6 cm⁻¹ from full CC on the one molecule where that can be checked. "Tier TZ" covers both full CC/TZ and those composites. | `PIPELINE.md:12,15,16`, `product_repo_design.md:73-74`, `ANCHORS.md:3,29,33` |
| A1-12 | The proposal's October–November lines have no outcome in the documents: 40 anchors in October, a hundred a month on a workstation, the CC learning curve, the hot-band test. Eleven anchors exist; the documents still say "laptop". | `Projectvoorstel:42,44,50-55` |
| A1-13 | Three contradictions on the product's shape: the network is "follow-up work outside the sequence" and "the heart of the end product"; anharmonicity is reported, left to others, and "no anharmonic shift yet"; the website is "nothing built" and "built 23–24 September". | root `README.md:74-75,118-119`, `GLOSSARY.md:23,65`, `Projectvoorstel:31`, `PIPELINE.md:25`, module 08 `README.md:11` |
| A1-14 | Reach: trained on 8–30 atoms, "about 40 atoms", against 101–386 carbons; "any individual aromatic molecule" against the refusal of ions, open shells and other elements. The baseline shown (B3LYP/6-31G* with PAHdb's factors) is not the opponent named (PAHdb's B3LYP/4-31G). | `PIPELINE.md:11,21,22`, `product_repo_design.md:95`, root `README.md:3-4,114-115` |
| A1-15 | Terms that carry the argument are never defined where a reader meets them: ΔH (H_CC − H_DFT in the proposal, H(ωB97X) − H(B3LYP) in module 05), hold-outs (a) and (b), "chain". About twenty pointers go to "TASKS nnn"; the reasons sit there. | `Projectvoorstel:10`, module 05 `README.md:19`, `MODELS.md:9`, `PIPELINE.md:7-19` |
| A1-16 | Unfinished and visible: the data paper is "Draft v0.1: skeleton" and its supervisor letter is unsent and names six anchors; of the product repository "nothing is built now". | data paper `README.md:12-14`, `OUTLINE_supervisor_2026-10-08.md:1,13`, `product_repo_design.md:5,62,78` |
| A1-17 | The environment: three interpreters and two unnamed conda environments, psi4 under Windows and pyscf under WSL, an unexplained `CORPUS_QC_PYTHON`, requirements that are `pip freeze` output, psi4 1.11 in one document and 1.10.2 in another; inputs stated to be local or on a rented host. | `REPRODUCE.md:8-9,28,47,63-68`, `product_repo_design.md:57-58`, module 08 `README.md:32,37` |

**MINOR** (23 items in the reader's report; the ones that recur): corpus size given as 244, 224, "ruim vijfhonderd", 847, 1,046, 1,230
and 289 with no current dated count; "35 numbered decisions" and "Fifty" while decisions 55–65 are cited; three supervisor dates; the
line for success "≤ 3,3 cm⁻¹" (`Projectvoorstel:41`) against "within 3 cm⁻¹" (`PIPELINE.md:27`); the same word for different things
(rung, ladder, licence, anchor, P1/P2, M1–M5); v1.1 = chain 34, v1.2 = chain 36, v1.3 = chain 35 unexplained; stale present tense
("is running", "tonight", "expected to finish around 26 September"); the AI statement's "between September and October 2026" against
work of 3 November; module 05's README opens with the Transformer's result table although the carried network is another architecture.

### 3.2 Reader A2 — modules 08 and 09 as an assessor would read them

**Verdict: module 08 would not pass today; module 09 cannot be assessed and nothing is prepared for it.**

Rubric 08, criterion by criterion: **met** — cross-domain integration, industry problem definition, trade-offs and constraints,
ethical considerations. **Partly** — integrated system, execution, design rationale, responsible deployment, paper quality,
evidence-based reflection, citations, portfolio value, documentation and reproducibility. **Not met** — mentor presentation and
defense.

**BLOCKING**

| # | finding | where |
|---|---|---|
| A2-1 | Paper and notebook are not about the system in the README. The paper says no family is licensed and the verdict falls at 1,200 molecules; the README says ring in-plane, C–H stretch and C–H out-of-plane are licensed under decision 65, and that paper and notebook "still describe the licence of 28 September". `results.json` is the state of 10 October with a licence block of 27 September. Design rationale, responsible deployment and evidence-based reflection all rest on it. | `make_summary.py:116,148-150,167`; module 08 `README.md:5` |
| A2-2 | No presentation for module 08's Task 7 and none for module 09. Rubric 09 demands a live 30-minute mentor session in English, 15 minutes of presentation and 15 of defense, slides "strongly recommended", seven required sections: industry context; system overview; integration of at least three prior projects; technical decisions and trade-offs; ethics; evaluation, limitations and risks; professional relevance and next steps. No `09_*` folder, no slide file. | `RUBRIC_CHECKLIST_2026-09-28.md:19` |
| A2-3 | No submittable form. `snapshot/`, `m08/paths.py`, `m08/make_snapshot.py` and `SUBMISSION.txt` are planned and absent; there is no Repository section in the README (modules 02–07 have both). Inputs sit outside the folder (`website/export/out`, modules 03/05/06/07, `src/dpir`); module 06's weights are not in git. | `STANDALONE_PLAN_2026-10-18.md:14-24` |

**SERIOUS**

| # | finding | where |
|---|---|---|
| A2-4 | The artifact is two halves that do not meet: the request officer of 28 September and the pipeline of 29 October. The officer "refuses and names the pipeline today". The paper describes only the first half. The only architecture diagram is the 27 September design (FastAPI, OAuth, a rented worker), none of which was built. The rubric asks for "intentional system design rather than a collection of disconnected components". | `PIPELINE_BACKLOG.md:9`; `DESIGN_2026-09-27.md` §3 |
| A2-5 | Which modules are integrated in code differs: four (03, 05, 06, 07) in the README, five with 04 in the paper and checklist, "03, 04, 07 … 05" in the design note. Rubric 09 requires each project's contribution "accurately described". | module 08 `README.md:20`; `make_summary.py:109`; checklist line 5 |
| A2-6 | "The eight pre-registered scenarios … (8 of 8)": the eight that passed are five registered and three added; registered S5–S7 are counted apart. The paper says S6 "was not run"; the registration records it run, failed, fixed and passing on 11 October, six days before the paper was rebuilt. | `make_summary.py:103,150-151,170`; `PRE_REGISTRATION.md:44,62-76` |
| A2-7 | Anchors: 5 printed from results, "two anchors and one validated molecule" in the text, "four CC anchors" in the checklist. The live worker is promised "when a licence exists" in the paper and "no longer promised" in the standalone plan; a licence now exists and the officer still refuses. | `make_summary.py:103,148,169`; `STANDALONE_PLAN_2026-10-18.md:7-8` |
| A2-8 | The central safeguard is described as "a pre-registered verdict and not an opinion"; the licence in force is a different rule (decision 65) and no registration of it is in the module's folder. | `make_summary.py:139` |
| A2-9 | Reproducibility files lag the code: `requirements.txt` dates from 28 September and has no pyscf and no psi4, which pipeline steps 2–3 need; the second environment `CORPUS_QC_PYTHON` is specified nowhere; `PROVENANCE.md` describes the 28 September build only. | module 08 `README.md:31`; `PROVENANCE.md` |
| A2-10 | The sections "Integration of Prior Projects" and "Technical Design Decisions" carry no citation, although the rubric's citation expectations demand them there. | `make_summary.py:108-133` |
| A2-11 | The synthesis is thin beyond the "at least three" bar. 03 is carried with numbers. 05 is carried with the wrong ones (the rung-B ratios 0.61 / 0.64 / 0.70 of 27 September; v1.3's 1.77 / 1.19 / 2.17 / 3.62 and 2.12 / 2.50 / 2.70 / 3.89 cm⁻¹ are not in the paper). 07's counts are stale (32 rules and 8 scenarios against 41 and 17). 06 is one SMILES string. 04 is one qualitative sentence. 02 is named once. | `make_summary.py`; READMEs of 02–07 |

**Formal requirements.** Satisfied: the exact file name `Reflective_Synthesis_Paper.pdf`, the nine sections of the submission list,
at least three sources with one scholarly, the author's name, new work. Probably satisfied: 1,500–2,000 words (the script refuses
outside that range; 1,852 recorded on 28 September; not recounted). Not satisfied: Task 6's "Evaluation and Reflection" has no
counterpart (the rubric contradicts itself here), the 15-minute presentation, the submission form, a clean folder (`.pid`, `.exit`,
run logs, `timer.dat`, `__pycache__/`, `.ruff_cache/` beside the deliverables). Cannot tell: "no new technologies" beyond earlier
projects (psi4, pyscf, an Astro website and axe-core appear); APA deviations in the title block, italics and the References heading
if APA is enforced.

**MINOR.** Catalogue size 11,321, 13,714 and 843; `rules_v1.json` against `rules_v2.json`; "three hold-outs" then "the two
hold-outs"; "measured this week" for a September price; files named for 28 September and 11 October with a modification time of
2 November while the registration says nothing changes after the run; the checklist of 28 September marks every item done.

### 3.3 Which cold-read findings hold when checked

A cold reader sees only the documents handed over. Checked today against the board and the ledger:

| finding | check | result |
|---|---|---|
| A1-1, A1-5, A2-1, A2-3 | the files' own dates and statements | **Hold as stated.** The entry documents and `REPRODUCE.md` are six weeks behind; module 08's README itself says its paper and notebook are superseded. |
| A1-2, A1-3 (method and criterion) | decision 63 (17 Oct), TASKS 140 | **Hold as a documentation failure, not as a failure of the project.** Decision 63 set the end point: a proxy proof between two DFT levels plus the existing CC anchors as the bridge. The plan's method and criterion were replaced by a decision that lives in the ledger and on the board, and no entry document says so. A grep of TASKS for a laboratory comparison of a pipeline spectrum finds no row. |
| A1-4 (the proxy target is not shown nearer the truth) | TASKS 140, claim 4 | **Holds, and it is the weakest joint of the argument.** The proof never needed ωB97X to be nearer the truth: it shows that a correction between two levels of theory can be learned and carried. What ties it to the truth is the bridge, and the bridge today reads: C–H out-of-plane 6.25 cm⁻¹ on the original anchors, T3's ≤ 3 cm⁻¹ not claimed, and the anchors themselves uncertain out of plane by about 5 cm⁻¹ (pyridine's composite 6.62 from CC/TZ; benzene's TZ 5.40 from QZ, both read 10 Nov). |
| A1-7 (E8 on an invalid Hessian) | ledger, 29 Sep 23:4x | **Partly answered.** E8 was re-read on the corrected Hessian that evening (locality verdict again "between"; pattern residual 0.09, ring coupling ratio 0.79). `REPRODUCE.md:46` still points at the old folder. Whether module 05's "98 %" is the old or the re-read number was **not** checked. |
| A1-10 (3.62 against 3.35) | TASKS 129 and the engine-check row | **Answered on the board, not in the module.** 3.35 → 3.35 is chain 34 against chain 35 on the same 862 analytic targets of the ten-molecule hold-out; 3.62 is the read on the eight clean molecules after the leak of two B-twins was removed (30 Oct). The module's README gives both numbers without the sentence that joins them. |
| A1-6 (the promotion rule) | grep of `ANCHORS.md`, `GLOSSARY.md`, TASKS, ledger | **Holds.** The ledger says anchors were "promoted by chain 33c's rule"; the rule's text and threshold were not found by grep in any of the four. It exists in code or in an older entry; a reader cannot find it. |
| A1-12 (the proposal's milestones) | decision 63; TASKS 191 | **Holds as a documentation failure.** The proposal of 30 September was overtaken by decision 63 (no new CC anchors before July 2027) and the workstation is a question for 25 November. No document closes the proposal's lines. |
| A1-11 (the 3 cm⁻¹ licence on eight molecules) | TASKS 149, `product_repo_design.md` | **Holds.** The atom-order spread is known and v1.5 is its registered answer; the licence has no stated spread over molecules or seeds in the documents a reader sees. |
| A1-8, A1-9 (T3's counterpart; chain 34 numbers in module 08) | not checked beyond the reader's lines | **Open.** Both are stale numbers in a module document; both go in the rewrite. |
| A2-4 … A2-11 | module 08's own files | **Hold as stated**, with the limit that the rendered PDF was not seen. |

## 4. Part 2 — content: what "succeed" means and what it still takes

### 4.1 Three levels of success

| level | what it is | who judges | when |
|---|---|---|---|
| 1 | The Udacity capstone: modules 02–09 pass their rubrics (v1.5.1) | Udacity reviewers and a mentor | submission 1 Jan–30 Jun 2027; the aim is end of February 2027 |
| 2 | The proxy proof of decision 63: four claims read, shown with the pipeline demo (decision 64) | the supervisor | Wed 25 November 2026 (pencilled) |
| 3 | The mandate's goal and the handover: paper D draft, paper C outline, the product repository `aromir` v0, the runbook | the supervisor; later readers and users | writing phase December–February; buffer March–June 2027 |

Only level 1 has a formal pass or fail. Level 2 is where the project's claim is tested by someone who knows the field. Level 3 decides
whether the work outlives the capstone.

### 4.2 Level 1 — the Udacity capstone

**Where it stands.**

- Modules 02–07: built; each has its named report and notebook and a `SUBMISSION.txt`; reviewed against their rubrics on 17–18 October;
  standalone dry runs passed on 18 October. Their checklists are dated 22 September–3 October.
- Module 08: an executed notebook (24 cells, last re-executed 10 October), the paper (PDF of 17 October), pipeline 0.9 running end to
  end on the laptop, the show at `out/pipeline_show.html`. Not passable today (section 3.2).
- Module 09: nothing exists (TASKS 189).
- Nothing has been submitted. No calendar says which module is submitted when.

**What is still needed.**

| # | what | why | when |
|---|---|---|---|
| U1 | **Module 08's paper and notebook rewritten on the system as it stands**: the pipeline's six steps, decision 65's licence, the carried network's numbers on both hold-outs, the current rule and scenario counts, S6's true record, one count of anchors. `results.json` regenerated from current records, so that `make_summary.py` injects current numbers. | A2-1; three rubric criteria rest on it | after the last reads (≈ 19 Nov) fix the model version; December |
| U2 | **One system**: the officer hands a licensed request to the pipeline, or the paper describes the two as one flow and says which part is live. A diagram of the system as built, in the paper. | A2-4 | December |
| U3 | **One account of which modules are integrated**, the same in README, paper, checklist and slides, with a number carried from each of 03, 04, 05, 06, 07 and a sentence on 02. | A2-5, A2-11 | with U1 |
| U4 | **The standalone snapshot**: `m08/paths.py`, `m08/make_snapshot.py`, `snapshot/`, `SUBMISSION.txt`, a Repository section; requirements for both environments (pyscf and psi4 included, `CORPUS_QC_PYTHON` specified); `PROVENANCE.md` for the pipeline's files; a clean folder; a clean-clone run. | A2-3, A2-9 | January |
| U5 | **Citations** in "Integration of Prior Projects" and "Technical Design Decisions"; the "8 of 8 pre-registered" sentence corrected; the safeguard described as the rule in force; "Evaluation and Reflection" answered by name. | A2-6, A2-8, A2-10 | with U1 |
| U6 | **The presentation**: slides in rubric 09's seven sections, a 15-minute time plan, a rehearsal with questions; the same deck serves module 08's Task 7. Three questions an assessor will ask from the repository itself: where is the probe the plan is named for; what is the accuracy against measurement; what does the licence mean at 3 cm⁻¹ on eight molecules. | A2-2; A1-2, A1-3, A1-11 | January–February |
| U7 | **Modules 02–07's last items** (TASKS 20; the review of 17 October): the user's own lay read; module 06's Markdown summary, quoted samples, two unsupported claims and the seed-2 reproduction (its weights are not in git); module 07's extra headings and its LLM run (waits for a Vocareum key); clean-clone runs for 05 and 06; `pip freeze` with `notebook` at submission; a dev branch for 06–08. | each is a rubric line or a reproducibility line | December–January |
| U8 | **A submission calendar**: which module on which date. Modules 02–07 do not wait for v1.4 or for module 08; each can be frozen at a stated date and submitted early, so that a returned review costs days in January and not in June. | nothing has been tested against a real reviewer yet | to be agreed |
| U9 | **The mapping** (`GoalGathering/Capstone_Mapping.md`) brought to what was built, or marked superseded: it is the draft of 3–4 September, its Pass 6 "is not done", and it describes module 05 as the Δ₂-support predictor. Modules 05 and 06 still carry planned Zenodo releases that were never discussed again. | a reader who starts from the mapping meets another project | December |

### 4.3 Level 2 — the proof and 25 November

**Where it stands (TASKS 140).**

| claim | state | number and counterpart |
|---|---|---|
| 1. The network has learned and carries to larger molecules | **open** | chain 41 on analytic labels carries (q5 = 1.06); the deciding reads are v1.4 (TASKS 129) and chain 42, the size test at 34–60 atoms (TASKS 49) |
| 2. A few examples move a pretrained network | stands | whole head, C–H out-of-plane 6.55 → 2.82 cm⁻¹ from k = 5 to 200 |
| 3. The number of anchors per accuracy, with prices | stands | ring in-plane and C–H stretch within 3 cm⁻¹ at 100 anchors, C–H out-of-plane at 167 (153–177), 'other' not by 200; ≈ €729–3,026 |
| 4. The eleven CC anchors as the bridge | stands, with its limit | C–H out-of-plane 6.25 cm⁻¹ on the originals; T3's ≤ 3 cm⁻¹ not claimed; pyridine's composite within 6.62 of CC/TZ, benzene's TZ 5.40 from QZ |

Against decision 53's targets: T1 is not met ('other' 3.35 on hold-out (a), 3.62 on its eight clean molecules, 3.89 on (b)); T3 is not
claimed. Under decision 65 three families are licensed at DFT-proxy level and 'other' is not; no licence exists at CC level.

**What is still needed.**

| # | what | why | when |
|---|---|---|---|
| P1 | **Everything off the servers before Sunday 15 November**, each fetched whole and checked before the user deletes it: s2b1, s2b2, routea, the labels hosts (D8A, fd222). The fd222 labels will not all fit before the stop (TASKS 171): what is computed is fetched, what is missing is written down. | paid compute stops; "Gooi niets van de servers weg voordat we dubbelcheckt hebben dat we het lokaal hebben staan" | by 15 Nov |
| P2 | **The S2b and route A reads** (TASKS 53/178) under the route rule registered 4 November. The pipeline's positions are harmonic; S2 reached 3.0 cm⁻¹ in no family. Whatever the read, the pipeline's page says in one sentence what the positions are. | the anharmonic step is the first thing a spectroscopist asks about | ≈ 10–12 Nov |
| P3 | **Claim 1's two runs on one laptop**: D8A's relabel ends → HBC and D8A merged → chain 42; the 222's merge (≈ 15 Nov) → the v1.4 search (≈ 78 laptop hours). One training at a time under 13 GB. Between 15 and 24 November there are about 216 wall hours; the search takes 78 of them; chain 42's laptop hours are not on the rows read today. A failed search cannot be repeated in the window. | claim 1 is the only open claim | 15–19 Nov |
| P4 | **The fallback sentence for claim 1**, written before the reads: what is said on 25 November if v1.4 or chain 42 is not read or does not carry. The evidence in hand is chain 41 on analytic labels. | a claim decided on the day is decided under pressure | before 16 Nov |
| P5 | **The demo rehearsed** (decision 64): the supervisor picks an unseen molecule of at most 30 minutes. The rehearsal runs on molecules the pipeline has never seen, including one it must refuse (an ion, another element) and one with 'other' modes that carry weight, and under two atom orders (the answer moves by up to 2.9 cm⁻¹, more under arbitrary orders, until v1.5). The rebuild is ≈ 24 November (TASKS 146, 154). | a live run on a stranger's molecule fails where no test has been | 20–24 Nov |
| P6 | **One page that says what the proof is**: a method proof between two DFT levels; what ties it to CC is the anchor bridge and its price curve; what is not shown is accuracy against measurement. The user decided there is no note for the meeting; the page is for the front of the repository and for module 08, and it is the answer to A1-2, A1-3 and A1-4. | section 3.3 | before 25 Nov if the supervisor will open the repository; otherwise December |
| P7 | **A descriptive table: pipeline bands against laboratory gas-phase bands and against the scaled-B3LYP baseline**, for the few molecules where measurement exists. Not a claim and not a target: harmonic positions will not win it. It answers the stated criterion with a number in place of silence, and it shows what the anharmonic step and the CC level are for. No row for it exists on the board. | A1-3 | the user's decision; cheap, no compute |

### 4.4 Level 3 — the handover

| item | state | needed |
|---|---|---|
| Paper D (the data paper) | Draft v0.1, a skeleton with `\todo{}` notes; numbers injected by `make_paper.py`; the outline for the supervisor has waited since 8 October and names six anchors (TASKS 30) | the outline brought to eleven anchors and discussed on 25 November; the draft in the writing phase |
| Paper C | undefined (TASKS 190) | its question and outline, after 25 November |
| The product repository `aromir` | design decided 1 November, nothing built; v1.5 (atom-order-free) is a release condition; `src/dpir` holds `provenance.py` and `qff.py` only (TASKS 73) | v1.5 trained and read; the engine check's deciding read; the build of v0 |
| The runbook | not written (TASKS 93) | written from the runspecs and the watch, in the writing phase |
| The workstation and funding | the question for 25 November (TASKS 191) | the supervisor's answer; it decides whether CC anchors resume in July 2027 |
| The cations | 384 rows; the fill is ≈ 1,147 laptop hours (TASKS 121); the pipeline refuses ions today | the fill on the calendar, or a dated decision on what part of it the capstone carries |

### 4.5 The one resource: the laptop

From 15 November every run shares one laptop, 13 GB for all runs together, one training at a time. From 15 November to 28 February
there are 105 days, about 2,520 wall hours (my arithmetic). Already promised to it: the v1.4 search (≈ 78 h), chain 42, the demo
rebuild, the cation fill (≈ 1,147 h, 46 % of all wall hours by itself), TASKS 164's checks, module 06's seed-2 reproduction, v1.5's
training, module 08's clean-clone run, and whatever TASKS 194 (the MP2 QZ step) and the engine check add. The writing phase also
needs the laptop to re-execute notebooks. TASKS 192 says it: "No calendar orders them yet." Without one, the first thing to slip is
whichever run has no date, and the cation fill has none.

### 4.6 What is needed, by date

| by | needed |
|---|---|
| **Sun 15 Nov** | P1 every server fetched and checked; P2 the S2b and route A reads; the laptop calendar agreed (TASKS 192) with claim 1's two runs first; P4 the fallback sentence for claim 1 |
| **≈ 19 Nov** | P3 the v1.4 search and chain 42 read; the model version for the demo and for module 08 fixed on that date |
| **Tue 24 Nov** | P5 the demo rebuilt and rehearsed on unseen molecules; paper D's outline at eleven anchors; the list of what is asked on the day (funding, the workstation, the closed-access papers of TASKS 144) |
| **Wed 25 Nov** | the meeting and the demo |
| **December** | the entry documents brought to the present (root README, plan README, `REPRODUCE.md`, the mapping); P6's page; U1–U3 and U5, module 08's rewrite; U7 and U8, modules 02–07 frozen and the first of them submitted |
| **January** | U4, module 08's snapshot and clean-clone run; v1.5 and the engine check; `aromir` v0; paper D's draft; the remaining modules of 02–07 submitted |
| **February** | U6, the slides and the rehearsal; module 08 submitted; module 09's session booked; paper C's outline; the runbook |
| **March–June 2027** | the buffer: returned reviews, the defense if it falls in May, the handover |

### 4.7 Risks, in the order I would rank them

1. **Module 08 and 09 are written last and are the only parts that can fail the capstone.** Everything in the plan puts them in
   January–February, after a November of runs and a meeting. They need no compute. A first rewrite in December takes them off the
   critical path.
2. **No module has met a real reviewer.** All eight could come back with requirements at once in March. Submitting 02–07 early turns
   that into information.
3. **The front of the repository contradicts the project** (A1-1, A1-2, A1-5). An assessor or the supervisor who opens the public
   repository reads "no pipeline results" first. This is a few hours of writing and no compute, and it is the cheapest large gain here.
4. **Claim 1 has no slack** (P3). Two runs, one laptop, nine days, a demo rebuild at the end.
5. **The proof is read as an accuracy claim** (A1-3, A1-4). Stated as a method proof with a priced bridge, it stands. Stated as
   "2 cm⁻¹", it invites the question it cannot answer. The 'other' family is unlicensed and the bridge's own uncertainty out of
   plane is about 5 cm⁻¹; both belong in the first paragraph, where they read as care and not as a hole.
6. **The live demo on a molecule nobody chose.** Refusals, 'other' modes, atom order and a run past 30 minutes are all possible.
7. **The licence rests on eight molecules and three seeds** (A1-11). It is a registered rule and it was applied as written; a reader
   still asks for its spread. v1.5 answers the atom-order part; nothing yet answers the sample-size part.
8. **The laptop** (section 4.5): one machine, no calendar, and a hardware failure would stop both the runs and the writing. The
   nightly backup covers the data; nothing covers the hours.
9. **Stale numbers inside the modules**: the chain 34 numbers in module 08's README (A1-9), T3's counterpart (A1-8), E8's pointer
   (A1-7), the corpus counts. Each is small; together they are what a defense is probed on.
10. **The handover has four deliverables and none is past a skeleton** (section 4.4). They compete with level 1 for the same weeks of
    writing. Level 1 goes first; which of the four is the minimum for February is a decision.

### 4.8 Decisions that are the user's

1. **What "slagen" is measured on**, so that the documents can say it: the three levels of 4.1 in this order, or another.
2. **The front-page statement of the proof** (P6): a method proof at DFT-proxy level with a priced CC bridge, and the plan's original
   method and criterion marked as replaced by decision 63. This changes the root README, the plan README and module 08's paper.
3. **The laboratory table** (P7): yes or no. It costs no compute and it will show no win.
4. **The laptop calendar** (TASKS 192): the order of v1.4 and chain 42 before 25 November, and where the cation fill's 1,147 hours go.
5. **Claim 1's fallback wording** (P4), before the reads.
6. **The submission calendar** (U8): whether modules 02–07 are submitted from December on, and in which order.
7. **Whether module 08's rewrite starts in December** against the model fixed on ≈ 19 November, with v1.4 or v1.5 entering later as
   numbers only.
8. **Officer and pipeline** (U2): joined in code, or described as one flow with the officer's live part named.
9. **The handover's minimum for February** (4.4): which of paper D's draft, paper C's outline, `aromir` v0 and the runbook must exist
   by then.
10. **Still waiting from before this review**: TASKS 194 (the MP2 QZ step), TASKS 193, and the order of the free tasks 164 and 185.
11. **What happens with this review's findings**: rows on the board (none were made, on the user's word), and whether the two cold
    readers' full reports are filed beside this one.

### 4.9 The order I would propose

1. This week, with the servers: P1 and P2, then the calendar and the fallback sentence. Nothing else competes with 15 November.
2. Between runs, at the desk: the front of the repository (root README, plan README, the page of P6). It needs decisions 1 and 2 only.
3. 15–24 November: claim 1's runs, the demo's rebuild and rehearsal, paper D's outline.
4. From 26 November: `REPRODUCE.md` and the mapping; module 08's rewrite; modules 02–07 frozen and submitted one by one.
5. January–February: the snapshot, v1.5, `aromir` v0, the slides, module 09.

## 5. Not done in this review

- No re-read of modules 02–07 against their rubrics; no PDF or notebook opened; the Atlas not opened.
- Module 05's "98 %" and T3's counterpart not traced to their records (section 3.3).
- Chain 42's laptop hours not looked up; Udacity's turnaround and booking rules not verified.
- The two cold readers' full reports are in the session's scratchpad, outside the repository; this file carries their findings, not
  their full text.
- Nothing was corrected. Every finding above is open.
- A1-14, 19 Nov, 08:1x (TASKS 247, merge 2f923471): the baseline shown now uses PAHdb's 6-31G* factors (0.979 / 0.969 / 0.960, Bauschlicher et al. 2018, Table 2); until pipeline 0.13 it used the 4-31G row. The point that it is not the opponent named (PAHdb's own B3LYP/4-31G spectra) stands.
