# Capstone mapping — Plan 03 Presence-Update-Rule

**Status.** Draft as of 2026-09-01. Passes 1–5 written in this file. Not signed off (no Pass 6). Not complete as a plan.

Rubrics are [`Rubrics/`](../../../Rubrics/) at repo root, version **1.5.1**, treated as fixed.  
This map is how plan 03 *uses* each rubric rather than fighting it.

Prime directive: [`Overarching_Goal.md`](Overarching_Goal.md).  
Technical plan: [`Distilled_Project_Plan_and_Quality_Checks.md`](Distilled_Project_Plan_and_Quality_Checks.md).  
Caps: [`Compute_Budget_2026-09-01.md`](Compute_Budget_2026-09-01.md).

The clause “must not be synthetic or AI-generated” in Modules 02–06 is a **hard constraint**. Self-trained network samples are never a Module 02–06 dataset. Teacher cubes from Octopus are computational experiments; they are the *scientific* corpus from Module 05 upward, and they are **not** offered as the Module 02–04 CSV.

**DOI-before-claim (§5.5).** For every module that names a dataset in a report, a public landing page (DOI or portal URL) is recorded *before* the notebook source sentence. No “illustrative portals” brief.

---

## 0. Gap-filling tags

When a rubric has no 1:1 match with the thesis:

- **(A)** Natural fit — the module already produces a research artifact.
- **(B)** Bridge — a useful extra study that also satisfies the rubric.
- **(C)** Check / QA — verifies a previous gate.
- **(D)** Forward-looking — toward Horizon 10–12, never a Module 08 promise.

Every module below is tagged. Busywork is a mapping failure.

---

## 1. Rubric matrix (Pass 1)

Folder numbers, not the rubric’s internal “Project 1 = module 02” offset.

| # | Module | Technique | Dataset rules | Core deliverables | Landmines |
|---|---|---|---|---|---|
| 02 | AI Programming Foundations | No ML. Pandas/NumPy/plots, EDA | ≥200 rows, ≥5 cols, tabular, academic-safe | `data_workflow.ipynb`, summary PDF, `requirements.txt`, README, git history | Must not train |
| 03 | Statistical analysis | Descriptive + ≥1 hypothesis test, ≥3 labelled figures | Own dataset; must differ from 02 once 04’s reuse rule is in force | `analysis.ipynb`, summary PDF, dataset file | PLOS ONE Huebner + one more scholarly source |
| 04 | Applied ML | sklearn or PyTorch; supervised or unsupervised | **Kaggle / UCI / Data.gov / open-gov only.** Not 02 or 03. Not synthetic/AI-generated | `modeling.ipynb`, report PDF, CSV | Accepted-sources list has no “own data” carve-out |
| 05 | Deep learning | PyTorch; CNN **or** RNN **or** Transformer + one controlled comparison | Not reused from any prior module. Not synthetic/AI-generated | `deep_learning.ipynb`, report with ethics, access instructions | CNN-family must be explicit |
| 06 | Generative AI | GAN, VAE, diffusion, or Transformer | Not synthetic as a *dataset*; not reused | `generative_ai.ipynb`, ethics tied to *this* run | Do not ship samples as new molecules |
| 07 | Agentic | Agent, memory, ≥1 tool, logging, safeguards | No dataset | notebook/`.py`, report, **architecture diagram** | Ethics tied to this agent |
| 08 | Industry synthesis | Integrate ≥3 of 02–07 | Reuse by design | Artifact + 1,500–2,000 word paper | Trace the three modules in the paper |
| 09 | Defense | 15 min | — | Oral defense | Defend the *refusal* as well as the rule |

---

## 2. Research decomposition (Pass 2)

| Phase | Goal | Data | Owner |
|---|---|---|---|
| Public tables | Fluency with dipole-as-a-column; hygiene | QM9 (02), RODARE flatten (03), QM9 other-target (04) | M02–M04 |
| Q0 + teacher | Hash the grid; produce H / H₂ / H₂O Maxwell windows | Octopus cubes | Scientific corpus, **M05** (not M02) |
| Stencil | Learn one 3×3×3 rule on H₂ pairs | Teacher pairs | **M05 Task B** (thesis). Task A is the rubric shield |
| Generative | VAE on published density slices, new split | Same voxel *source* as M05 Task A, different hash | M06 |
| Agent | Fail-closed certificate | Frozen ladder + probes | M07 |
| Synthesis | Next-step service + refusal | Integrates M03, M05, M07 | M08 |
| Horizon 10–12 | Phase, pair density, scale | — | **Not scored** |

## 3. Module map (Pass 3)

### Module 02 — AI Programming Foundations

**Tag: (A)** with a (B) flavour (dipole fluency).

**Rubric.** Public tabular CSV, \(\ge 200\) rows, \(\ge 5\) columns, not synthetic, no model training.

**Dataset (frozen intent).** QM9 **property table** from a Kaggle dump. Pin the exact Kaggle dataset slug + version in the freeze file before `data_workflow.ipynb` names a source. Columns include dipole, polarizability, HOMO/LUMO, ZPVE, geometry-derived counts.

**Work.** Load; two documented cleaners (unit checks, impossible-dipole filter); EDA on dipole vs polarizability and on element counts; \(\ge 3\) figures. No ML.

**Why it is not a detour.** Module 08’s dipole diagnostic \(\boldsymbol\mu=-\int\mathbf{r}\,\Delta\rho\,dV\) needs fluency with dipole as a *column* before it is an integral.

**Not used here.** Any Octopus cube. Any network output. **Q0 is not a Module 02 artifact.**

**Required sentence.** “This table is a public DFT-level benchmark. It is not a teacher cube and not AI-generated.”

### Module 03 — Statistical analysis

**Tag: (A)** + **(C)** (time-axis discipline for later P-gates).

**Rubric.** Different public CSV, \(\ge 500\) rows, \(\ge 6\) columns, numeric + grouping, one hypothesis test. Huebner et al. PLOS ONE 2024 + one more scholarly source.

**Dataset (frozen intent).** Flatten HZDR RODARE record **3995** (“Dataset for Machine Learning Time Propagators for TDDFT”, 2,048 1-D trajectories) to rows = (system, time). Columns: integrated density moments, dipole, laser amplitude, **intensity / wavelength bin** as the grouping variable. Pin the record URL before the notebook source sentence. Verify-on-use: bibliography item 3.

**Hypothesis (pre-registered).** Dipole-response amplitude does not differ across two declared intensity bins (two-sample test on a frozen split). Inconclusive allowed.

**Fallback.** If RODARE packaging cannot be flattened to \(\ge 500\) honest rows, use a **QM7-X** public table (\(\ge 500\) rows), grouping = contains oxygen / not, test a dipole or HOMO shift. Still public. Still not a cube. Declare the fallback in a dated note; do not mix both as “the” M03 file.

**Required citations.** Huebner et al. PLOS ONE 19(1): e0295726; one TDDFT/density paper from `Relevant_Scientific_Papers.md` after Verify is filled.

**Required sentence.** “This CSV is a flatten of a published computational corpus. It is not synthetic and not the Module 02 QM9 table.”

### Module 04 — Applied machine learning

**Tag: (B)** hygiene, not the stencil.

**Rubric.** Dataset from **Kaggle, UCI, Data.gov, or open government portal only.** Tabular. Supervised or unsupervised. Not the M02 or M03 file. Not synthetic/AI-generated.

**Dataset (frozen intent).** A **Kaggle QM9 dump whose prediction target is not the M02 EDA focus.** Freeze **polarizability** (or \(C_v\) if that column is cleaner in the dump). The file hash must differ from M02. Mordred-featurised QM9 is allowed only if it is a *distinct Kaggle dump* with its own slug — verify before freezing.

**Model.** scikit-learn ridge or random forest. Composition + simple shape descriptors → frozen target. Split, leakage check, metric, bias. This module does **not** score the stencil.

**Bridge sentence (required).** “A bag-of-features predictor of a static molecular number is not a presence-update rule.”

**Required sentence.** “Source is the named Kaggle portal. This dataset is not AI-generated.”

### Module 05 — Deep learning systems

**Tag: (A)** Task B is the thesis. Task A is the rubric shield.

**Rubric.** PyTorch. CNN for images (declare CNN-family explicitly). One controlled comparison. Public, not-synthetic, not reused from 02–04.

**Q0 lives here.** Hash generator + \(0.20\,a_0\) + box + nuclear-refinement rule **before** any training window is cut. After that hash, the grid is a constant.

**Task A (rubric-shaped, public voxels).** 3-D electron-density volumes treated as image stacks. Pin the exact Zenodo/Figshare DOI of the QM9-density release (bibliography item 10) before the report source sentence. CNN on 2-D slices; auxiliary target **already in the public QM9 table** (e.g. a dipole component), not computed by us. **2026-09-01:** item 10 is still unpinned as a cube dump (DeepDFT is a model paper; item 13 is 1-D TDDFT). Do not write the Task A source sentence. The hard fallback below stays in force until a voxel DOI is recorded.

**Task B (thesis).** 3-D conv stencil on **H₂ teacher pairs** (Octopus RT-TDDFT + Maxwell). Controlled comparison: kernel **3×3×3 vs 5×5×5**, exactly that one axis. Metrics: P1; loss curves; P0 as pass/fail. Not an FNO unless Distilled §4.

**Hard fallback (pre-declared).** If a mentor treats self-run TDDFT cubes as “synthetic,” Module 05 **ships on Task A alone**. P1 waits for Module 08’s scientific appendix. Do not improvise a third dataset.

**Required sentences.** “Task A uses a published voxel corpus, not AI-generated, not reused from Modules 02–04.” “Task B cubes are computational experiments; they are not the graded Task A dataset.”

### Module 06 — Generative AI

**Tag: (B)** ethics of fabricated fields.

**Rubric.** VAE (frozen choice). Public data. Not reused as the M05 **training split**. Ethics tied to this run.

**Dataset.** Same published voxel *source* as M05 Task A, **new hash** (different split). Not teacher cubes. Not VAE samples used as later training data.

**Work.** VAE on density slices / local stencils. Show samples. Evaluate reconstruction of \(\rho_-\); flag samples with \(N<0\) or a net plus in vacuum. One concrete failure case.

**Ethics.** Fabricated densities as fake laboratory fields; a surrogate read as a measurement; ownership of teacher trajectories from academic codes.

**Forbidden.** Shipping VAE samples as “new molecules.”

**Required sentence.** “The training images are a public voxel corpus. Generated samples are model output, not a dataset for Modules 02–05.”

### Module 07 — Agentic workflows

**Tag: (C)** governance executed.

**Rubric.** Single agent, memory, \(\ge 1\) tool, logging, safeguards, architecture diagram, one concrete decision.

**Plan 03 use.** Fail-closed **teacher-and-hash agent**. Tools: `check_grid_hash`, `load_split`, `refuse_if_water_in_h2_train`, `run_p0_probe`, `write_claim_or_stop`. Persona: conservative lab officer. Memory: the frozen ladder file.

**Safeguard.** If P0 fails, the agent may not emit a P2 claim.

**Observed failure case.** Deliberately poisoned hash → refuse.

No new dataset.

### Module 08 — Industry synthesis

**Tag: (A)** assembly.

**Industry.** Scientific-software / digital-twin vendors (attosecond labs, radiation-chemistry codes, TCAD-adjacent EM-matter coupling). Problem: a full TDDFT step is too slow for ensemble work; an uncertified neural step is too dangerous.

**Integrate (frozen three).** M03 (pre-registered test language), M05 (conv-stencil), M07 (fail-closed agent).

**Artifact.** A small service: hashed grid state in → next field **and** a certificate (P0 last-passed, seed, split hash) **or** a refusal.

**Paper.** 1,500–2,000 words. Mean-field limit in public language. No JWST, no C₃₈₄H₄₈, no anharmonic IR.

### Module 09 — Defense

Defend the *rule*, the *gates*, and the *refusal* to spend the thesis on a grid or a PAH spectrum. Expected question: “is this just TDDFT with extra steps?” Answer: the contribution is a certified local surrogate with a frozen evaluation contract, not a new functional.

---

## 4. Distinctness (Pass 4)

| Module | Molecule / rows | Format | Source class | Reused? |
|---|---|---|---|---|
| 02 | QM9 properties, \(\ge 200\) rows | CSV | Kaggle table | No |
| 03 | RODARE 3995 flatten (fallback QM7-X) | CSV | Public computational table | No — not QM9 |
| 04 | QM9, **other target**, other file hash | CSV | Kaggle table | No — not the M02 file |
| 05 Task A | Published QM9 **voxels**, pinned DOI | volumes / slices | Zenodo/Figshare | No — not a CSV from 02–04 |
| 05 Task B | H₂ teacher pairs | cubes | Own Octopus | Scientific corpus; not the graded Task A set |
| 06 | Same voxel *source* as 05 A, **new split hash** | slices | Zenodo/Figshare | Split must not overlap 05 A train |
| 07 | — | — | — | No dataset |
| 08 | — | — | Integrates 03, 05, 07 | Reuse by design |

02 and 04 may both be “QM9” **only** if file hashes and prediction targets differ. If they do not, 04 must take a different Kaggle molecular set. That check is a freeze-file line, not a memory.

---

## 5. Non-negotiables (Pass 5)

### 5.5 DOI-before-claim

Before any notebook source sentence:

| Module | What must exist first |
|---|---|
| 02 | Kaggle slug + version (or Figshare DOI) |
| 03 | RODARE 3995 landing URL, or QM7-X DOI if fallback fired |
| 04 | Kaggle slug + version, hash \(\neq\) M02 |
| 05 A | Zenodo/Figshare DOI of the voxel dump |
| 05 B | Hash of Octopus deck + Q0 grid hash |
| 06 | Same DOI as 05 A + new split hash |

### “Not AI-generated” sentences

Required in 02, 03, 04, 05 A, 06 as written above. Teacher cubes are **computational experiments**, never offered as the 02–04 CSV, and only as 05 B with the Task A shield.

### Mentor fallback

Self-run cubes rejected as data → 05 ships on Task A; P1 in M08 appendix. Pre-declared.

---

## 6. Calendar and 840 h (structure only)

T0 is the date Module 02 starts, not a calendar date in this draft. Human 840 h from Overarching Goal. Wall-clock 168 h for the promised teacher set from the compute-budget file.

| Bucket | Hours | Modules |
|---|---|---|
| Frozen grid + teacher I/O | 80 | 05 B decks, Q0 |
| Public-rubric datasets | 160 | 02, 03, 04 |
| Learned stencil + P0–P4 | 320 | 05 B, probes, 8 h P1 pilot |
| Generative + agentic + synthesis | 200 | 06, 07, 08 |
| Contingency / reviews | 80 | 09 + drift |

Ordering rules: 02 before 03 before 04 (reuse). Q0 before any 05 B window. 07 may run as soon as Q0 and a P0 script exist; it must not claim P2 without P0. 08 assembles; it does not train a new stencil.

Pass 6 (module-by-module sign-off) is **not** done. This mapping is a draft.
