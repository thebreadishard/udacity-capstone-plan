# Capstone Mapping — Working Document

**Status:** DRAFT — Passes 1–5 complete (extraction + gap analysis + dataset mapping + non-negotiables validation). Professor-review blocking issues 1–6 resolved in spec (2026-08-22): Workstream P1 (§4.1); implementable \(E=\mathcal{E}[\rho,R]\) (Distilled Plan §6); data-generation method + cost pilot + shrink ladder (Distilled Plan §5.1); prime directive reconciled with Distilled Plan §9 ([Overarching_Goal.md](Overarching_Goal.md)); rubric landmines locked (§3 Module 06 rewrite, Pass 4 Module 03 \(\ge 500\) table, §5.5 DOI-before-claim); Workstream G1 (§4.2) owns the MACE baseline on the same splits. Horizon PAH work is post-master’s Projects 10–12, not Modules 02–09. Pass 6 (module-by-module sign-off) is the only remaining mapping step before this is treated as final.
**Purpose:** Single source of truth for dividing the FNO-NCA research plan ([Distilled_Project_Plan_and_Quality_Checks.md](Distilled_Project_Plan_and_Quality_Checks.md), [Overarching_Goal.md](Overarching_Goal.md)) across Udacity capstone modules 02–08 ([../CapstoneProjects](../CapstoneProjects)). Phase 1 of the Distilled Plan is **not** a Udacity module; it is owned by Workstream P1 (§4.1). Projects 10–12 are **not** Udacity modules.

---

## 0. Gap-Filling Philosophy (agreed 2026-08-20)

When a module's rubric has no clean 1:1 match with a research-plan phase, fill the gap using one of these four categories (in order of preference):

- **(A) Natural fit** — the module's required technique/deliverable is already produced by a research phase as-is.
- **(B) Bridge / invented sub-project** — a new, genuinely useful sub-study designed to satisfy the rubric's technique requirement *and* materially advance the pipeline (not busywork).
- **(C) Check / QA project** — a project whose deliverable is to verify, stress-test, or automate quality-assurance of a *previous* phase's output (e.g., automating the Phase 0 numerical-verification protocol, or the §8 quality checklist).
- **(D) Forward-looking / value-add project** — extends toward the horizon (chemically precise **labels**; later, PAH **band envelopes**) even if not strictly required by the current phase, e.g. transferability/generalization studies. “Chemically precise IR spectrum of arbitrarily large PAHs” is Projects 10–12, not a Module 02–08 category-D excuse.

Every gap-fill choice must be tagged with its category (A/B/C/D) and a one-line justification when we get to the mapping pass, so we can audit later whether we drifted into "busywork to satisfy a rubric" vs. genuine project value.

---

## 1. Rubric Requirements Matrix (Pass 1)

Numbering note: the rubric text internally calls module 02 = "Project 1", 03 = "Project 2", 04 = "Project 3", 05 = "Project 4", etc. (offset by one from the folder numbers). Using folder numbers below.

| # | Module | Required technique | Dataset rules | Core deliverables | Notable constraints |
|---|---|---|---|---|---|
| 02 | AI Programming Foundations | None (no ML) — Pandas/NumPy/Matplotlib/Seaborn data workflow, cleaning functions, EDA, ≥3 visualizations | Own choice or recommended (Titanic/Iris/Wine/Airbnb); own dataset must have ≥200 rows, ≥5 columns, tabular, "safe/appropriate for academic use" — **no reuse restriction stated** | `data_workflow.ipynb`, `module_summary.pdf` w/ citations, `requirements.txt`, `README.md`, GitHub repo w/ ≥1 extra branch + multiple commits | Must NOT train ML models here |
| 03 | Statistical Analysis | Descriptive stats + ≥1 hypothesis test (SciPy), ≥3 labeled visualizations | Own dataset — no explicit reuse restriction stated in this module itself (but see 04's rule below, which implies 03's dataset must differ from 02's) | `analysis.ipynb`, `module_summary.pdf` (Overview/Dataset/Methods/Results/Non-Technical Interpretation/Limitations/References), dataset file, `requirements.txt` | No ML models yet |
| 04 | Applied ML | sklearn or PyTorch; supervised (classification/regression) OR unsupervised (clustering) — student's choice | Own dataset; explicitly **must differ from Projects 1 & 2 (modules 02 & 03)**; from Kaggle/UCI/Data.gov/open-gov portals; **not synthetic/AI-generated** | `modeling.ipynb`, `Machine_Learning_Analysis_Report.pdf`, `requirements.txt`, dataset CSV | Evaluation-metric rigor over accuracy |
| 05 | Deep Learning Systems | PyTorch; CNN **or** RNN **or** Transformer (pick one) + ≥1 controlled comparison experiment (baseline vs. one changed variable) | Own dataset; **must NOT be reused from ANY previous capstone project**; not synthetic/AI-generated | `deep_learning.ipynb`, `Deep_Learning_Systems_Analysis_Report.pdf` (incl. **Ethical and Responsible Use** section), `requirements.txt`, dataset/access instructions | Must document ≥1 concrete behavior example (overfitting/instability/error case) |
| 06 | Generative AI | GAN, VAE, diffusion, **or** Transformer-based generation (image or text) | Own dataset/prompt source; not synthetic/AI-generated as a dataset; not reused from a prior capstone project | `generative_ai.ipynb`, `Generative_AI_Analysis_Report.pdf` (incl. **Ethical Considerations**), `requirements.txt` | Must show multiple generated samples + qualitative evaluation + ≥1 concrete generated-behavior/failure case, ethics tied to own outputs |
| 07 | Agentic Workflows | Agent/agentic workflow (OpenAI API or course-approved framework): reasoning/decision logic, limited memory/state, ≥1 tool/external function call, logging/safeguards | No dataset requirement — task-execution artifact, not a dataset-modeling one | `agentic_system.ipynb`/`.py`, `Agentic_AI_Systems_Analysis_Report.pdf`, **architecture diagram**, `requirements.txt` | Must show ≥1 concrete agent decision example; ethics tied to the specific agent |
| 08 | Industry Synthesis | None new — integrates ≥3 prior capstone projects (any of 02–07) into one industry-framed artifact | N/A (reuses prior artifacts by design) | Integrated artifact + `Reflective_Synthesis_Paper.pdf` (1,500–2,000 words), mentor presentation/defense (15 min) | Must explicitly trace how ≥3 prior projects informed the design; ≥3 sources cited |

---

## 2. Research-Plan Decomposition (Pass 2)

From [Distilled_Project_Plan_and_Quality_Checks.md](Distilled_Project_Plan_and_Quality_Checks.md) §7 (phased roadmap) and §8 (QA protocol).

| Phase | Goal | Dataset used | Nominal ML "genre" | Key artifact produced | Owner |
|---|---|---|---|---|---|
| **0 — Numerical foundation** | Validate the differentiable physics engine, no ML | None (analytical test functions) | N/A — numerical software verification | Energy-drift, egg-box, force finite-difference, Poisson-solver, grid-convergence reports | Module 03 (sweep write-up) + Phase 0 engine code |
| **1 — H₂O PES training** | Learn R → E, F, ρ | ≥2,000 H₂O configs from the §5.1 PySCF campaign (energy CCSD(T)/cc-pVTZ; \(\rho\)/\(F\)/\(H\) per the pinned recipe) | Supervised regression; custom energy-based hybrid FNO + local-conv ("NCA") architecture | Trained PES model, force RMSE / harmonic-frequency validation | **Workstream P1** (ungraded; §4.1) — *not* Modules 04/05/07 |
| **2 — Emergent IR (H₂O)** | Blind spectral prediction, frozen weights | 5×50 ps MD trajectories (simulation output, not a training dataset) | Inference-only / simulation, no training | FFT-derived IR spectrum vs. experimental FTIR | Module 07 (tool-use demo), on **P1's frozen weights** |
| **3 — Physical hardness tests** | Prove real physics learned, not memorization | D₂O (mass-swap), CO₂ — frozen weights, zero-shot | Zero-shot evaluation / physics validation | Isotope-shift and symmetry-selection-rule checks | Module 07 (tool-use demo), on **P1's frozen weights** |
| **4 — Baseline benchmark** | Prove the 3D field representation adds value | Same H₂O/benzene configs **and the same split manifests** | Simple non-field NN (§04) + **Workstream G1** MACE + field PES (P1 / 05) + harmonic/FD CCSD(T) | Comparative table: leave-one-mode-out transfer (primary), energy/force RMSE, harmonic error, MD stability, cost | **04 + G1 + P1/05 train;** Module 08 **assembles only** (§4.2) |
| **5 — Benzene finale** | Aromatic generalization | Nominal ≥5,000 benzene configs, 64³ grid — **per Distilled Plan §5.1**; \(N\) and grid are targets until the 10-geometry pilot exits Phase 0 | Same hybrid architecture, scaled up (flagship deep-learning training run) | Aromatic/C–H mode validation vs. NIST FTIR | Module 05 (graded CNN slot) |
| *(Outlook)* — Naphthalene | OOD zero-shot transfer, discussion only | Atomic-density superposition, no training | Zero-shot evaluation | Exploratory discussion, not a pass/fail milestone | Module 08 discussion only |

**Cross-cutting, not tied to one phase:** §8's 10-point QA/verification protocol (conservativity loop tests, force finite-difference checks, egg-box quantification, grid convergence, Poisson boundary convergence, 3-way error decomposition, energy-conservation metrics, spectral-quality metrics, charge/dipole sanity checks, compute-budget derivation) — currently unowned by any phase; a candidate for a **(C) Check/QA** bridge project.

---

## 3. Gap Analysis (Pass 3 — resolved 2026-08-20)

For each module, the assigned category (A/B/C/D), the concrete proposal, why it satisfies the rubric, why it is genuinely valuable (not busywork), and open risks/mitigations.

### Module 02 — AI Programming Foundations
**Category: (A) natural fit, with a (D) flavor.**

- **Proposal:** EDA-only notebook on a QM9 (or ANI-1ccx) subset — the exact small-molecule benchmark [Overarching_Goal.md](Overarching_Goal.md) names as an acceptable starting point. Cleaning functions remove QM9's documented ~3,054 flagged/erroneous geometries; EDA + ≥3 visualizations explore property distributions (atom counts, dipole moment, HOMO–LUMO gap, energies).
- **Why it satisfies the rubric:** pure data workflow, no ML, ≥200 rows/≥5 cols easily met, publicly available, no reuse conflict (nothing else uses QM9).
- **Why it's genuinely valuable:** the written summary explicitly concludes that QM9/ANI-1ccx-level data is DFT-level (or lower), not CCSD(T), and therefore does **not** meet the project's chemical-precision bar — this becomes the documented motivation for why Phase 0/1 must generate custom CCSD(T) data instead of reusing an existing benchmark. Real project justification, not a throwaway exercise.

### Module 03 — Statistical Analysis
**Category: (A) natural fit + (C) check/QA.**

- **Proposal:** descriptive stats + hypothesis test(s) run directly on **Phase 0 numerical-foundation sweep data** — e.g., $H_0$: egg-box artifact amplitude is independent of the $\sigma/\Delta x$ ratio (§8 point 3), tested across the required sweep $\sigma/\Delta x \in \{1,1.5,2,2.5,3\}$ with repeated rigid-translation trials as rows; or a grid-convergence correlation test (§8 point 4) across $\Delta x \in \{0.40,\dots,0.15\}\,\text{Å}$. The CSV is rubric-legal **by spec** (see Pass 4 row): \(\ge 500\) rows, \(\ge 6\) columns, `sigma_over_dx` stored as a **categorical** factor, Zenodo DOI **before** the notebook claims a source (§5.5). Do not swap this for a Kaggle toy table.
- **Why it satisfies the rubric:** genuine hypothesis test with clearly stated $H_0$/$H_1$, own dataset distinct from Module 02's QM9 table, ≥3 visualizations of the sweep results, \(\ge 500\) rows / \(\ge 6\) cols / grouping variable / public DOI.
- **Why it's genuinely valuable:** this *is* the required §8 QA protocol output (egg-box quantification / grid-convergence study), formally statistically validated instead of eyeballed — directly strengthens Phase 0's Go/No-Go evidence.

### Module 04 — Applied ML
**Category: (A) natural fit.**

- **Proposal:** train the **"simple non-field NN energy model"** (or a classical regressor — Kernel Ridge Regression / Gaussian Process Regression on a Coulomb-matrix/SOAP descriptor, in the spirit of Rupp et al.) that Phase 4 explicitly requires as one of the three mandatory baselines, using the H₂O CCSD(T) **descriptor CSV** sliced from the same PySCF campaign that feeds Workstream P1. Module 04 does **not** train the field PES; that is P1 (§4.1).
- **Why it satisfies the rubric:** supervised regression, sklearn or PyTorch, own dataset distinct from Modules 02/03, appropriate metrics (energy/force RMSE vs. CCSD(T)).
- **Why it's genuinely valuable:** it's not an invented side-task — it is literally one of the three required baseline comparisons in Phase 4 (§7), without which the plan's own "prove the field representation adds value" claim (§4, last bullet) has no evidence.
- **Risk/mitigation:** Module 04's "Accepted Sources" list names Kaggle/UCI/Data.gov/open-gov portals only, with no explicit "or your own" carve-out (unlike Module 02). **§5.5 gate:** Zenodo DOI **before** `modeling.ipynb` claims a source. Do not write a legal brief that the list is “illustrative.” DOI + required sentence.

### Module 05 — Deep Learning Systems
**Category: (A) natural fit.**

- **Proposal:** the actual flagship **hybrid FNO-NCA architecture on benzene (Phase 5)**, using the Distilled Plan §6 forward pass (energy is \(\mathcal{E}[\rho,R]\); no latent energy head). The local $3\times3\times3$ NCA update *is* a 3D-CNN-family architecture (voxel-grid convolutions). The required controlled comparison (Task 4) is **same \(\mathcal{E}\), same fixed Hockney–Eastwood \(E_{\mathrm{es}}\); encoder = local-NCA-only vs local-NCA+FNO**. The FNO is a non-local mixer in the density encoder, **not** a learned Poisson replacement.
- **Why it satisfies the rubric:** PyTorch, explicit CNN-family architecture, genuine controlled experiment with a clearly stated "what changed / what stayed the same," own dataset (benzene volumetric, disjoint from Module 04's H₂O CSV) — satisfying the "not reused from ANY previous capstone project" rule. Nominal size is ≥5,000 / 64³ **per Distilled Plan §5.1**, not an unconditional promise.
- **Why it's genuinely valuable:** this is the actual thesis centerpiece (§7 Phase 5) — no invention needed, just correct framing/justification of the architecture as "CNN-family" for the rubric.
- **Risk/mitigation:** must explicitly justify the CNN framing in the report (cite the local-convolution structure) so a grader doesn't view a physics-simulation architecture as evading the CNN/RNN/Transformer requirement. Module 05 is the **benzene scale-up**, not the first time the hybrid architecture is trained: Workstream P1 is the H₂O \(32^3\) rehearsal and must start before 05 training if the engine/architecture is not yet stable (§4.1). Compute: the §5.1 10-geometry benzene pilot is a Phase 0 exit; if \(T_{\mathrm{campaign}}\) does not fit, take the shrink ladder (including remapping 05 at rung 4) rather than fail the module mid-run.

### Module 06 — Generative AI Applications
**Category: (B) bridge project, with a (D) flavor.**

- **Proposal (frozen; deletes the old “VAE on CCSD(T) benzene” sentence):** **VAE for representation learning over geometries** (3D or internal coordinates) on a **new, independent cheap corpus** — \(\sim\)1000–2000 ground-state + normal-mode-displaced geometries across 5–8 small aromatics **that are not benzene** (toluene, pyridine, aniline, phenol, styrene, furan, pyrrole), at **HF/6-31G or B3LYP/6-31G\*** only. The rubric menu is GAN / VAE / Transformer; VAE + representation learning is the fit. Diffusion may be discussed in the report, not implemented as the scored model. The notebook **shows** generated geometry samples. Generated geometries are a **proposal mechanism only**: they **never** enter P1 / 04 / 05 train/val/test, or any pipeline set, without a fresh Distilled Plan §5.1 CCSD(T) label.
- **Why it satisfies the rubric:** required VAE task in the rubric’s own words; own dataset (not reused from 02–05); public or clearly documented (§5.5 DOI); multiple samples + qualitative evaluation + a concrete failure case (unphysical bonds).
- **Why it's genuinely valuable:** a validated generative sampler can later expand sampling beyond hand-designed normal modes (Project 10+), without pretending the cheap corpus is pipeline data.
- **Ethics angle (non-generic):** an unvalidated sample that silently poisons a PES. That sentence is only honest if the report states the samples were **not** used as labels.

### Module 07 — Design of Agentic Workflows
**Category: (B)/(C) bridge project.**

- **Proposal:** a "computational-chemistry lab assistant" agent that automates the §7 Go/No-Go phase-gate decisions and the §8 ten-point QA protocol. Tools: invoke PySCF for a new CCSD(T) calculation, invoke **Workstream P1's frozen H₂O PES** for inference, run a force finite-difference check, produce a convergence plot. Memory/state: persisted log of which phase-gate checks have already run and their pass/fail status. Reasoning: given a phase's numeric Go/No-Go thresholds (§7 table), decide PASS/FAIL/NEEDS-MORE-DATA, and if borderline, decide what additional check to run next. The agent does **not** train the Phase 1 model; it only gates and runs tools against P1 (and Phase 0) artifacts.
- **Why it satisfies the rubric:** real reasoning/decision logic, real tool use (PySCF, inference, finite-difference), real memory/state (phase-gate history), architecture diagram of agent ↔ tools ↔ log.
- **Why it's genuinely valuable:** automates tedious, error-prone manual verification (§8) that the plan explicitly requires "throughout, not just at Phase 0" — reduces the risk of a human silently skipping a required check.
- **Ethics angle (non-generic):** the specific, concrete risk is an autonomous agent falsely declaring a Go decision without having actually executed the required numeric check — a real correctness/safety concern for *this* system, addressed by a hard safeguard: the agent must refuse to output PASS without citing the exact measured value against the exact threshold it checked. If P1 missed its Phase 1 gates, that refusal is the correct demo, not a failed module (§4.1 failure mode).

### Module 08 — Industry-Integrated AI Systems Synthesis
**Category: (A) natural fit** (by design — depends on 04–07 being built first).

- **Proposal:** integrate ≥3 of {04 baseline model, 05 benzene FNO-NCA model, 06 generative augmentation model, 07 QA agent} under an industry frame of **reliability-gated spectral emulation for small molecules**. JWST / PAH identification ([Relevant_Scientific_Papers.md](Relevant_Scientific_Papers.md) item 15) is **why anyone would care later** (Projects 10–12), not a capability Module 08 built. 05 is the predictive engine, 07 is the fail-closed gate layer, 06 is a proposal mechanism, 04 is the cheap non-field leg. The field-PES leg comes from P1 / 05. The **GNN leg comes from Workstream G1** (§4.2), already trained on the same splits. 08 **assembles** the table; it does **not** debut MACE training. If P1 or G1 is missing, 08 reports the field-vs-GNN claim as **incomplete** and does **not** substitute 04's MLP for MACE (§4.1, §4.2).
- **Why it satisfies the rubric:** integrates ≥3 prior projects explicitly and intentionally, industry-specific framing, reflective paper can honestly trace how each prior artifact informed the design (because it's true, not fabricated for the assignment).

### Cross-cutting open risk (applies to Modules 04–06)

Modules 04–06 forbid "synthetic/AI-generated" datasets. CCSD(T)-computed configurations are legitimate first-principles ab initio scientific data (produced by a deterministic quantum-chemistry solver, PySCF, not by a generative AI/ML model), but every report should include one explicit sentence pre-empting misreading, e.g.: "This dataset was computed via ab initio coupled-cluster [CCSD(T)] quantum chemistry using PySCF, a first-principles numerical method — not an AI/ML-generated synthetic dataset."

---

## 4. Final Module → Dataset/Deliverable Mapping (Pass 4 — resolved 2026-08-20)

| Module | Exact dataset | Format & size | Key deliverable files | Depends on |
|---|---|---|---|---|
| 02 | QM9 properties table (Ramakrishnan et al. 2014), random subset of ~5,000–10,000 molecules, minus the ~3,054 QM9-flagged "uncharacterized" geometries | Single CSV, rows = molecules, columns = SMILES, atom count, μ, α, HOMO, LUMO, gap, ZPVE, U₀, Cᵥ, etc. (≫5 cols, ≫200 rows) | `data_workflow.ipynb`, `module_summary.pdf`, `README.md`, `requirements.txt`, GitHub repo | None |
| 03 | Phase 0 numerical-foundation sweep results (own-generated, not QM9) | CSV, **\(\ge 500\) rows, \(\ge 6\) columns**, one numeric + one **categorical** grouping variable. Frozen columns: `trial_id`, `molecule` (categorical), `sigma_over_dx` (**categorical** factor: `1.0`/`1.5`/`2.0`/`2.5`/`3.0`), `delta_x_angstrom`, `box_pad_factor`, `translation_step`, `energy_hartree`, `force_error`, `egg_box_amplitude`. Frozen count (honest, not padded): \(5\,(\sigma/\Delta x)\times 50\text{ translations}\times 2\text{ molecules}\times 2\text{ repeats} + 6\,(\Delta x)\times 50\text{ translations} = 800\). A cheaper product is allowed only if it is written as a number \(\ge 500\), never “several hundred.” | `analysis.ipynb`, `module_summary.pdf`, sweep-results CSV **in the submission folder**, `requirements.txt` | **Phase 0 engine must already be built.** **§5.5:** Zenodo DOI **before** the notebook claims a source. Do not replace this with a UCI toy table. |
| 04 | H₂O **descriptor CSV** from the Distilled Plan §5.1 campaign (same geometries as P1; not the volumetric tensors) | CSV, one row per config: `config_id, r_OH1, r_OH2, theta_HOH, energy_hartree, fx_O, fy_O, fz_O, fx_H1, …` plus the §5.1 theory tags (`theory_energy`, `theory_force`, `pyscf_version`, …). Bond-length/angle descriptor → energy/forces; deliberately *not* the 3D density grid. CSV **copy in the submission folder** (`df.head`). | `modeling.ipynb`, `Machine_Learning_Analysis_Report.pdf`, `requirements.txt`, dataset CSV | H₂O campaign per Distilled Plan §5.1. Same geometries may also feed P1; only this CSV is the Module 04 dataset. **§5.5:** Zenodo DOI **before** the source sentence. |
| 05 | Benzene configuration set (Phase 5), **nominal** ≥5,000 configs, 64³ grid — **per Distilled Plan §5.1** | Volumetric tensors (`.npz`/HDF5), one file per config: nuclear positions, target ρ(r) from the pinned 1-RDM recipe, E, F, selected Hessian entries — plus an indexing manifest CSV with the §5.1 theory tags; **not CSV-only**; **not** the 04 CSV and **not** P1 tensors | `deep_learning.ipynb`, `Deep_Learning_Systems_Analysis_Report.pdf`, `requirements.txt`, dataset **hosted externally with access instructions** | Phase 5 benzene campaign — **the single biggest compute bottleneck**. \(N\) and grid are **targets until the 10-geometry pilot exits Phase 0**. If the shrink ladder fires to rung 4, 05 must be remapped. Prefer P1 architecture-stable before 05 training starts (§4.1). **§5.5:** Zenodo DOI **before** the source sentence. |
| 06 | New, independent corpus: ~1,000–2,000 geometries across 5–8 small aromatics **that are not benzene** (toluene, pyridine, aniline, phenol, styrene, furan, pyrrole), **HF/6-31G or B3LYP/6-31G\*** only. Task: **VAE, representation learning over geometries.** | XYZ/`.npz` + manifest CSV | `generative_ai.ipynb`, `Generative_AI_Analysis_Report.pdf`, `requirements.txt`, geometry corpus | None (parallel with 04/05). **Not** benzene CCSD(T). **Not** a pipeline label source. **§5.5:** DOI before the source sentence. |
| 07 | No new dataset — operates as a tool-using agent over the **real logged results of Phases 0–3** (Phase 0 sweep, **P1** H₂O field training, Phase 2 emergent-IR run, Phase 3 D₂O/CO₂ zero-shot hardness tests), invoking PySCF/inference/finite-difference as tools | Agent transcript/log (JSON or similar) + architecture diagram | `agentic_system.ipynb`/`.py`, `Agentic_AI_Systems_Analysis_Report.pdf`, architecture diagram, `requirements.txt` | **Workstream P1 must exist as an artifact** (weights + gate report), even if it failed its numeric gates. Phases 2 & 3 are demoed here on P1's frozen weights; if P1 failed, 07 still ships and must refuse PASS (§4.1). |
| 08 | No new dataset — integrates artifacts from ≥3 of {04, 05, 06, 07} plus **G1 gate report** (ungraded) | Reflective_Synthesis_Paper.pdf + integrated artifact | `Reflective_Synthesis_Paper.pdf`, integrated artifact/diagrams | 04, 05, 06, 07 (needs ≥3). Field leg = P1 / 05. GNN leg = **G1**. 08 does not train either. |

### Notes arising from consolidation

- **Phase 4's comparison has three trainers and one assembler.** Module 04 delivers the simple non-field NN. **G1** (§4.2) delivers MACE on the **same** P1/05 split manifests. P1/05 deliver the field PES. Module 08 **assembles** the table. It does not train the competitor.
- **Module 06 precision question:** its training corpus is deliberately *not* CCSD(T)-level — resolved in Pass 5 as *not* a deviation (proposal only). Pass 3 no longer contradicts this: the benzene-CCSD(T) VAE sentence is **deleted**.
- **Distinctness check:** 02 (QM9 properties), 03 (Phase 0 sweep), 04 (H₂O descriptors), 05 (benzene volumetric), 06 (independent small-aromatic corpus) are all disjoint *graded* sources/formats/molecules — no dataset-reuse violations across 02–06. P1's H₂O volumetric tensors are research infrastructure, never submitted as a module dataset.
- **Dependency chain is now explicit:** Phase 0 engine **and** §5.1 smoke tests + 10-geometry cost pilots (→03 sweep write-up; pilots are a Phase 0 *exit*) → H₂O campaign per §5.1 (→04 descriptor CSV **and** P1 volumetric tensors) → **P1 H₂O field PES** in parallel with **G1 H₂O MACE** (same split manifest) → Phase 5 benzene campaign **at the \(N\)/grid the pilot allows** (→05, the long pole) → **G1 benzene MACE** after the 05 split freeze → Phases 2/3 on P1 weights (→07) → 08 (needs ≥3 of 04/05/06/07 **and** the G1 gate report to claim §2). Module 06's corpus has no dependency and can be produced any time in parallel. If the H₂O pilot fails, stop before P1/G1. If the benzene pilot fails, take the shrink ladder before promising 05.

### 4.1 Workstream P1 — H₂O FNO-NCA PES (resolves professor-review blocking issue 1)

**Decision (2026-08-22):** Phase 1 is not crammed into Modules 04, 05, or 07. It is an explicit **ungraded research workstream** with the same seriousness as a module row. 04 stays the tabular non-field baseline; 05 stays the graded CNN-family benzene scale-up; 07 stays a tool-user over logged results. See [Professor_Review_2026-08-22.md](Professor_Review_2026-08-22.md) blocking issue 1.

| | |
|---|---|
| **Name** | Workstream P1 — H₂O FNO-NCA PES |
| **Not a module** | No Udacity notebook, no rubric credit, never submitted as a module dataset |
| **Owner** | The research repo (same codebase as the Phase 0 engine) |
| **Inputs** | Phase 0 engine (must pass its numerical gates **and** the §5.1 smoke-test / 10-geometry H₂O pilot); H₂O campaign per Distilled Plan §5.1 that also emits Module 04's descriptor CSV |
| **What it trains** | Distilled Plan §6 forward pass: Route B \(E=\mathcal{E}[\rho,R]\) (fixed Hockney–Eastwood \(E_{\mathrm{es}}\) + learned \(\varepsilon_\theta[\rho]\); NCA ± FNO encoder) on H₂O volumetric fields, \(32^3\), \(\ge 2000\) configs **if the H₂O pilot allows**. No latent energy head. Density target is the §5.1 1-RDM recipe, not “exact CCSD(T) density.” |
| **Deliverables** | Frozen weights; force/energy/harmonic-frequency report vs Distilled Plan §7 Phase 1 gates; config-level split manifest |
| **Who consumes it** | Module 07 (Phases 2–3 and Go/No-Go tools); Module 05 (architecture already working before benzene scale-up); **G1** (same H₂O split manifest); Module 08 (field leg of the assembled table) |
| **When** | After Phase 0 and the H₂O PySCF campaign; **before** Module 07. Start before Module 05 training, not after |
| **Graded datasets stay disjoint** | 04 = H₂O descriptor CSV; 05 = benzene volumetric; P1 tensors are research infra |

Same §5.1 geometries may feed 04 (bond/angle + \(E,F\)) and P1 (\(\rho, E, F, H\)). That is **one data campaign, two products**. Only the CSV is the Module 04 dataset. Recipe, cost pilot, and shrink ladder live in Distilled Plan §5.1, not in this table.

**What this workstream is not**

- Not Module 04: 04's rubric requires a tabular CSV and a simple supervised model. Flattening \(32^3\) cubes, or stretching “other tabular format,” is rejected.
- Not Module 05: 05 is the one graded CNN slot and must stay on benzene to keep datasets disjoint from 04 and to avoid debuting the hybrid architecture on the most expensive run.
- Not Module 07: the agent must not “invoke training” as a way of owning Phase 1. Training is this workstream; the agent only gates it.
- Not Module 08: synthesis may not debut the H₂O field training campaign.

**Failure mode (required — otherwise P1 is still a ghost task)**

If P1 misses the Distilled Plan §7 Phase 1 gates, or slips the calendar:

- **Module 07 still ships.** The agent's job is to run the checks, cite measured value vs threshold, and **refuse PASS**. A blocked gate is a valid agent demo. A fake PASS is not.
- **Phases 2–3 are marked blocked**, not silently skipped and not faked with a benzene model.
- **Module 05 may still run** only if the *architecture* (not the H₂O accuracy gate) is stable enough to scale. If P1 failed because the engine/architecture is broken, 05 does not start.
- **Module 08** reports the field-vs-GNN / field-vs-simple-NN claim as incomplete if P1 failed. It does not substitute the Module 04 baseline for the field model.

Module 07 must not assume “Phase 1 exists and passed.” It assumes “P1 produced a gate report,” which may be FAIL.

### 4.2 Workstream G1 — equivariant atomistic PES (resolves professor-review blocking issue 6)

**Decision (2026-08-22):** The comparison that tests Distilled Plan §2 is **not** Module 05’s encoder ablation and is **not** debuted in Module 08. It is an explicit **ungraded research workstream** with the same seriousness as P1. 04 stays the cheap non-field baseline. 05 stays local-NCA vs local-NCA+FNO. 08 **assembles** a table whose GNN numbers already exist.

| | |
|---|---|
| **Name** | Workstream G1 — equivariant atomistic PES |
| **Not a module** | No Udacity notebook, no rubric credit, never submitted as a module dataset |
| **Primary package** | **MACE, trained from scratch** on **our** Distilled Plan §5.1 labels. Not a DFT-pretrained MACE-OFF (or similar) checkpoint — wrong theory, not a fair test. |
| **Fallback** | NequIP, **only** if MACE cannot be installed. One scored package, not both as co-equal models. |
| **Inputs** | P1 H₂O **split manifest** and, if 05 runs, the 05 benzene **split manifest**. Geometry + \(E,F\) only. Same `config_id`s. **No new sampling.** |
| **Not inputs** | Densities; Module 04’s descriptor CSV as a *different* split; Module 06 VAE samples |
| **What it trains** | One atomistic equivariant PES per molecule campaign (H₂O; benzene if the §5.1 pilot allows 05). Same train/val/test IDs as the field model. |
| **Deliverables** | Frozen weights; same-split metrics; wall-clock and parameter count; one-page gate report |
| **Primary metric (the §2 test)** | Leave-one-mode-out (or held-out mode-family) energy/force error on the **same** split for field and GNN — H₂O first; benzene if 05 exists |
| **Secondary** | In-domain \(E/F\) RMSE; harmonic frequencies vs the **one** §5.1 equilibrium Hessian; frozen-weight MD stability; train/inference cost |
| **Not flagship** | D₂O mass-only swap (Phase 3 **sanity**). H₂O→CO₂ zero-shot (field hardness test, unfair as a GNN bake-off). Naphthalene (outlook). |
| **Who consumes it** | Module 08 **only assembles**. Module 07 does **not** own G1 and does not “invoke GNN training.” |
| **When** | H₂O G1 **in parallel with P1** (after the H₂O campaign and the P1 split freeze). Benzene G1 **after** the benzene campaign and its split freeze, **before** 08 writes the claim. |
| **Graded datasets stay disjoint** | G1 is not a fourth graded dataset. It reuses P1/05 **labels and IDs**, not 04/05 submission folders. |

**What this workstream is not**

- Not Module 04: 04 is SOAP/KRR or a small MLP on a descriptor CSV. MACE is not that model.
- Not Module 05: 05’s controlled comparison is already frozen (same \(\mathcal{E}\), same Hockney–Eastwood, encoder on/off). A GNN is a different representation, not one changed variable.
- Not Module 07: the agent does not train the competitor.
- Not Module 08: synthesis may not debut the GNN training campaign.

**Failure mode (required — otherwise G1 is another ghost)**

If G1 is not trained, or does not share the P1/05 split manifests:

- **Module 08 must not claim field-vs-GNN.** Report the comparison **incomplete**.
- Do **not** substitute 04’s MLP for MACE.
- **Escape (written, last resort):** rewrite Distilled Plan §2 and Overarching Goal §2 down to field vs simple-NN + encoder ablation. That is a weaker thesis. It is better than a fake MACE run in the last week of 08.

A GNN **win** on the pre-registered transfer split is a valid thesis. A missing G1 is not.

---

## 5. Validation Against Non-Negotiables (Pass 5 — resolved 2026-08-20)

### 5.1 Overarching_Goal.md checklist

| Requirement | Applies to | Status |
|---|---|---|
| Train/Validation/Test sets must be chemically precise **labels** (CCSD(T)/cc-pVTZ per Distilled Plan §5.1). Sub-cm⁻¹ is a **spectrum** claim and is forbidden for this thesis (Distilled Plan §9; Overarching Goal §3). | 04 (H₂O descriptors), **P1** (H₂O volumetric field PES), **G1** (same \(E,F\) IDs), 05 (benzene) — the actual pipeline's ML data | **Compliant on energy (and default forces)** — CCSD(T)/cc-pVTZ per Distilled Plan §5.1. Density is the pinned 1-RDM recipe (default: relaxed CCSD), a documented density-level gap, not a slogan “exact CCSD(T) density.” A cheaper density proxy is **not** compliant unless the §5.1 shrink ladder fires and the Overarching Goal escape clause is invoked. P1 and G1 are ungraded infrastructure, not extra graded datasets. |
| Deviation only with "absolutely no other technical solution" + "extremely compelling, well-documented reason" | 06 (cheaper-level corpus) | **Reclassified — no deviation needed at all** (see §5.3 below), not merely an accepted exception. |
| Small molecules (QM9/ANI-1ccx) OK for validating pipeline *mechanics* | 02 | **Compliant, with a scope caveat**: Module 02's QM9 use is EDA-only, not a mechanics test of the real pipeline code — see required disclaimer in §5.4. |
| Leverage latest architectures, don't reinvent the wheel | 04 (KRR/GPR precedent), 05 (FNO/NCA hybrid), **G1 (MACE; NequIP fallback)**, 06 (VAE representation learning; diffusion discussion-only), 07 (standard agent/tool-use pattern) | **Compliant** — all use established architecture families, nothing bespoke-for-its-own-sake. |

### 5.2 Distilled Plan §4 ("what the project is NOT") checklist

| Constraint | Applies to | Status |
|---|---|---|
| NOT a GNN (no discrete atom-nodes/bond types) | 04, P1, 05 | **Compliant for the *field* models.** 04 uses a descriptor/kernel regressor; P1 and 05 have no atom-graph structure. **G1 is the GNN *baseline*** — it is allowed *because* §4 forbids the *thesis model* from being a GNN, not because baselines are forbidden. |
| NOT DFT, no exceptions for pipeline data | 04, P1, 05 (the real pipeline) | **Compliant by default** — energies (and default forces) are CCSD(T). DFT/HF-level data appears *only* in 02 and 06, plus **rung 3 of the §5.1 shrink ladder** (density proxy only), which is a real exception and must invoke the escape clause. Hohenberg–Kohn *shape* \(E=\mathcal{E}[\rho]\) is the claim, not KS-DFT / library XC. |
| NOT purely local CA — FNO is encoder-only; Poisson is fixed Hockney–Eastwood | P1, 05 | **Compliant by design.** Module 05 ablates encoder = local-NCA vs local-NCA+FNO; \(E_{\mathrm{es}}\) stays the Phase 0 kernel. |
| NOT a multi-head regressor with auxiliary density | P1, 05 | **Compliant by spec** (Distilled Plan §6). Implementation must not add a latent \(E\) head that can ignore \(\rho\). |
| NOT density-first / Route A for forces | P1, 05 | **Action item:** P1 implementation and the Module 05 report must explicitly state Route B: forces are \(-\partial\mathcal{E}[\rho_\theta,R]/\partial R_A\), autograd through \(\rho_\theta\). |
| NOT trained on spectral loss | P1, 05 | **Action item:** P1 and Module 05 losses must be the multitask $L_E+L_F+L_H+L_\rho$ only; any Phase 2 MD/FFT spectrum shown (e.g., in Module 07's agent demo) must be presented as a frozen-weight, post-hoc *evaluation*, never as a training signal. |
| NOT periodic/naive Poisson solver | 03 (Phase 0 validation), 05 | **Compliant** — Module 03's sweep explicitly tests the Hockney–Eastwood solver. |
| NOT claiming egg-box elimination, only control | 03 | **Action item:** report wording must say "reduced/controlled as a function of σ/Δx," never "eliminated." |
| NOT quantum computing | — | Not touched by any module; no action needed. |
| NOT claiming chemical precision for large PAHs as core deliverable | 08 (synthesis paper) | **Action item:** any mention of scaling beyond benzene must be framed as outlook / Projects 10–12 only, per §9 and the rewritten Overarching Goal. Module 08 sells reliability-gated small-molecule emulation, not a PAH spectrometer. |
| NOT quantum-mechanical rovibrational line-list precision | 05, 07 (if Phase 2 spectra shown), 08 | **Action item:** all spectral claims must use §9's approved wording ("band positions and relative envelopes/intensities within a stated cm⁻¹ tolerance"), never "chemically precise spectral lines." |
| NOT naphthalene as a pass/fail milestone | 08 | **Action item:** if mentioned at all, explicitly labeled exploratory/outlook, matching the Distilled Plan's own treatment. |
| NOT requesting supercomputer time up front | 05 | **Note, not a violation:** Module 05's benzene *campaign* is the plan's biggest compute bottleneck. Scope it for local/consumer hardware first. The Distilled Plan §5.1 10-geometry pilot is the kill switch: if local \(T_{\mathrm{campaign}}\) does not fit, take the shrink ladder (including remapping 05) rather than apply for HPC on day one. |
| NOT skipping baseline comparisons | 04, P1, **G1**, 05, 08 | **Compliant** — 04 = simple-NN; G1 = MACE on the same splits; P1/05 = field; 08 assembles. If P1 or G1 failed/missing, 08 must say the comparison is incomplete (§4.1, §4.2). |

### 5.3 Compliance boundary (new, clarifies §4's dataset table)

DFT/HF-level data appears in exactly two places — **Module 02's QM9 subset** and **Module 06's small-aromatic corpus** — and in both cases it is formally outside the actual research pipeline's train/validation/test sets:

- **Module 02** is pure EDA on a public benchmark; its conclusion (QM9 isn't precise enough) is *why* the real pipeline doesn't use it. It never feeds Phase 0–5.
- **Module 06's generative model is a sampling/proposal mechanism, not a data source.** This is functionally identical to the Distilled Plan's own already-approved sampling schemes in §5 (normal-mode displacement, random thermal displacement, rigid rotation/translation) — none of *those* are "chemically precise" processes either; they're just ways of proposing candidate geometries, which only become training data once evaluated at CCSD(T). A learned VAE proposal distribution is the same kind of thing. **Every candidate the Module 06 model generates must be re-computed at full CCSD(T) (§5.1) before it is ever used anywhere in the actual pipeline.** Under this framing, Module 06 does **not** need to invoke the Overarching Goal's deviation/escape clause at all — reclassified from "exception" to "compliant by construction." This must be stated explicitly in the Module 06 report to preempt a grader or reviewer reading it as a precision compromise.

### 5.4 Resolved risks (carried over from Pass 3/4)

- **Module 04 "Accepted Sources" risk — RESOLVED as a gate, not a hope:** see §5.5. DOI before the notebook’s source sentence. No legal brief that the four named portals are “illustrative.”
- **Module 02 disclaimer — action item:** the report must state plainly that QM9 is used solely for this module's no-ML EDA requirement, is *not* part of the actual research pipeline's data, and its own precision level is the explicit motivation for why the real pipeline uses custom CCSD(T) data instead.
- **Module 06 Pass 3/4 contradiction — RESOLVED:** Pass 3 no longer says “VAE on CCSD(T) benzene.” Task is VAE representation learning on the cheap non-benzene corpus.

### 5.5 Rubric publication gates (resolves professor-review blocking issue 5)

These are **submission gates**, not notes to self. Order is mandatory: **DOI exists before the notebook claims a source.** No embargo-until-after-grade.

| Module | Dataset | Gate | Required report sentence (do not improvise a chemistry lecture) |
|---|---|---|---|
| **03** | Phase 0 sweep CSV | Zenodo DOI + public GitHub; CSV **also** in the submission folder. \(\ge 500\) rows, \(\ge 6\) cols, `sigma_over_dx` categorical. | This table is numerical output of a **deterministic classical physics engine** (Gaussian nuclei, Hockney–Eastwood, autograd), not an AI-generated or GAN-simulated dataset. |
| **04** | H₂O descriptor CSV | Zenodo DOI **before** Task 1; CSV copy in the zip for `df.head`. | Computed with **PySCF** under Distilled Plan §5.1 (ab initio CCSD(T)/cc-pVTZ energy; forces per the pinned recipe) — first-principles numerical data, **not** an AI/ML-generated synthetic dataset. |
| **05** | Benzene volumes | Zenodo (or versioned record) **before** the report; access instructions in the notebook. Not the 04 CSV; not P1 tensors. | Same PySCF / §5.1 sentence as 04, plus: this volumetric set is **not reused** from any prior capstone project. |
| **06** | Cheap non-benzene geometry corpus | Zenodo DOI **before** the source sentence. | The **dataset** is QM at HF/6-31G or B3LYP/6-31G\* (not AI-generated as a dataset). VAE **outputs** are generated samples the rubric requires showing; they are **not** pipeline labels unless recomputed at §5.1. |

Do **not** argue with the grader that coupled-cluster is “not AI.” Put the link that works. Do **not** replace Module 03 with UCI wine. GitHub release is extra; a citable **DOI** is the source line.

---

## 6. Next Steps

- [x] **Pass 3:** Formal gap analysis session — go tension-by-tension above, decide A/B/C/D category, sketch what the bridge/check project would concretely contain.
- [x] **Pass 4:** Draft full module→phase mapping table (one row per module 02–08), consolidating Pass 3's proposals into final form (dataset names, exact deliverable filenames, explicit dependency order since 08 depends on 04–07).
- [x] **Pass 5:** Validate draft against Overarching_Goal.md non-negotiables and Distilled Plan §4 ("what the project is NOT"). Module 04/03/05/06 publication is a **§5.5 gate** (DOI before claim), Module 06 precision question reclassified as compliant-by-construction (not a deviation), several report-wording action items identified (§5.2).
- [x] **Professor review, blocking issue 1:** Phase 1 assigned to ungraded Workstream P1 (§4.1), 2026-08-22.
- [x] **Professor review, blocking issue 2:** Distilled Plan §6 now specifies implementable \(E=\mathcal{E}[\rho,R]\); leftover \(\rho_{Im}\)/EM channels deleted; Hockney–Eastwood vs learned FNO jobs split.
- [x] **Professor review, blocking issue 3:** Distilled Plan §5.1 is now a method (1-RDM, force recipe, counted Hessians, 10-geometry cost pilot as Phase 0 exit, shrink ladder, noise-floor force gate). Mapping 04/P1/05 datasets are “per §5.1,” not “CCSD(T) everything.” Closed as a *spec*. Closed as *science* only when the smoke-test table and 10-geometry numbers exist.
- [x] **Professor review, blocking issue 4:** [Overarching_Goal.md](Overarching_Goal.md) rewritten (labels vs spectra; §9 adopted in the prime directive; Module 08 product named). README and this checklist no longer say “sub-cm⁻¹” as a dataset rule. Horizon path is post-master’s Projects 10–12.
- [x] **Professor review, blocking issue 5:** Rubric landmines locked — Module 03 \(\ge 500\) / 800-row product + categorical `sigma_over_dx`; Pass 3 Module 06 is VAE representation learning on cheap non-benzene aromatics (benzene CCSD(T) sentence deleted); §5.5 DOI-before-claim + “not AI-generated dataset” sentences.
- [x] **Professor review, blocking issue 6:** Workstream G1 (§4.2) owns MACE (NequIP fallback) on the **same** P1/05 split manifests. 05 stays the encoder ablation. 08 assembles; it does not train. D₂O stays Phase 3 sanity, not the flagship. Closed as a *spec*. Closed as *science* only when G1 weights and the leave-one-mode-out table exist.
- [ ] **Pass 6:** Module-by-module sign-off, one at a time — walk through each module's final spec (dataset, deliverables, action items from §5.2/§5.4/§5.5) and get explicit go-ahead before implementation begins.

---

## 7. Post-master’s horizon (Projects 10–12) — not Udacity, not Pass 6

These files live in [`../CapstoneProjects/`](../CapstoneProjects/) next to the scraped rubrics so the horizon is as visible as the degree. They are **not** gradeable modules. Module 08 must not claim them.

| # | File | Wall | Exit (short) |
|---|---|---|---|
| 10 | [10_Size_Extensive_Aromatic_PES.md](../CapstoneProjects/10_Size_Extensive_Aromatic_PES.md) | Labels + size-extensivity | Gold-anchored PES transfers to the next ring; representation fork decided from the master’s field-vs-GNN test |
| 11 | [11_Anharmonic_IR_and_Intensities.md](../CapstoneProjects/11_Anharmonic_IR_and_Intensities.md) | Nuclear motion + intensities | GVPT2-class band families + relative intensities; four-term error budget; MD+FFT is diagnostic only |
| 12 | [12_Astrophysical_PAH_Identification.md](../CapstoneProjects/12_Astrophysical_PAH_Identification.md) | Excitation + fail-closed ID | Pre-registered match to one frozen JWST/PAHdb product; “any size” means until measured error exceeds the band tolerance |

Order is mandatory: 10 then 11 then 12. A single extra project, if only one exists, is 10.
