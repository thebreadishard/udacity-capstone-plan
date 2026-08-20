# Capstone Mapping — Working Document

**Status:** DRAFT — Passes 1–5 complete (extraction + gap analysis + dataset mapping + non-negotiables validation). Pass 6 (module-by-module sign-off) is the only remaining step before this is treated as final.
**Purpose:** Single source of truth for dividing the FNO-NCA research plan ([Distilled_Project_Plan_and_Quality_Checks.md](Distilled_Project_Plan_and_Quality_Checks.md), [Overarching_Goal.md](Overarching_Goal.md)) across Udacity capstone modules 02–08 ([../CapstoneProjects](../CapstoneProjects)).

---

## 0. Gap-Filling Philosophy (agreed 2026-08-20)

When a module's rubric has no clean 1:1 match with a research-plan phase, fill the gap using one of these four categories (in order of preference):

- **(A) Natural fit** — the module's required technique/deliverable is already produced by a research phase as-is.
- **(B) Bridge / invented sub-project** — a new, genuinely useful sub-study designed to satisfy the rubric's technique requirement *and* materially advance the pipeline (not busywork).
- **(C) Check / QA project** — a project whose deliverable is to verify, stress-test, or automate quality-assurance of a *previous* phase's output (e.g., automating the Phase 0 numerical-verification protocol, or the §8 quality checklist).
- **(D) Forward-looking / value-add project** — extends toward the ultimate goal (arbitrary-size aromatic molecule → chemically precise IR spectrum) even if not strictly required by the current phase, e.g. transferability/generalization studies.

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

| Phase | Goal | Dataset used | Nominal ML "genre" | Key artifact produced |
|---|---|---|---|---|
| **0 — Numerical foundation** | Validate the differentiable physics engine, no ML | None (analytical test functions) | N/A — numerical software verification | Energy-drift, egg-box, force finite-difference, Poisson-solver, grid-convergence reports |
| **1 — H₂O PES training** | Learn R → E, F, ρ | ≥2,000 CCSD(T)/cc-pVTZ H₂O configs (PySCF-generated) | Supervised regression; custom energy-based hybrid FNO + local-conv ("NCA") architecture | Trained PES model, force RMSE / harmonic-frequency validation |
| **2 — Emergent IR (H₂O)** | Blind spectral prediction, frozen weights | 5×50 ps MD trajectories (simulation output, not a training dataset) | Inference-only / simulation, no training | FFT-derived IR spectrum vs. experimental FTIR |
| **3 — Physical hardness tests** | Prove real physics learned, not memorization | D₂O (mass-swap), CO₂ — frozen weights, zero-shot | Zero-shot evaluation / physics validation | Isotope-shift and symmetry-selection-rule checks |
| **4 — Baseline benchmark** | Prove the 3D field representation adds value | Same H₂O/benzene configs | Explicitly requires training **a simple non-field NN energy model** + comparison vs. equivariant atomistic ML PES (MACE/NequIP/Allegro-style) + finite-difference CCSD(T) | Comparative table: energy/force RMSE, vibrational error, MD stability, compute cost |
| **5 — Benzene finale** | Aromatic generalization | ≥5,000 CCSD(T) benzene configs, 64³ grid | Same hybrid architecture, scaled up (flagship deep-learning training run) | Aromatic/C–H mode validation vs. NIST FTIR |
| *(Outlook)* — Naphthalene | OOD zero-shot transfer, discussion only | Atomic-density superposition, no training | Zero-shot evaluation | Exploratory discussion, not a pass/fail milestone |

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

- **Proposal:** descriptive stats + hypothesis test(s) run directly on **Phase 0 numerical-foundation sweep data** — e.g., $H_0$: egg-box artifact amplitude is independent of the $\sigma/\Delta x$ ratio (§8 point 3), tested across the required sweep $\sigma/\Delta x \in \{1,1.5,2,2.5,3\}$ with repeated rigid-translation trials as rows; or a grid-convergence correlation test (§8 point 4) across $\Delta x \in \{0.40,\dots,0.15\}\,\text{Å}$.
- **Why it satisfies the rubric:** genuine hypothesis test with clearly stated $H_0$/$H_1$, own dataset distinct from Module 02's QM9 table, ≥3 visualizations of the sweep results.
- **Why it's genuinely valuable:** this *is* the required §8 QA protocol output (egg-box quantification / grid-convergence study), formally statistically validated instead of eyeballed — directly strengthens Phase 0's Go/No-Go evidence.

### Module 04 — Applied ML
**Category: (A) natural fit.**

- **Proposal:** train the **"simple non-field NN energy model"** (or a classical regressor — Kernel Ridge Regression / Gaussian Process Regression on a Coulomb-matrix/SOAP descriptor, in the spirit of Rupp et al.) that Phase 4 explicitly requires as one of the three mandatory baselines, using the H₂O CCSD(T) configuration dataset (Phase 1).
- **Why it satisfies the rubric:** supervised regression, sklearn or PyTorch, own dataset distinct from Modules 02/03, appropriate metrics (energy/force RMSE vs. CCSD(T)).
- **Why it's genuinely valuable:** it's not an invented side-task — it is literally one of the three required baseline comparisons in Phase 4 (§7), without which the plan's own "prove the field representation adds value" claim (§4, last bullet) has no evidence.
- **Risk/mitigation:** Module 04's "Accepted Sources" list names Kaggle/UCI/Data.gov/open-gov portals only, with no explicit "or your own" carve-out (unlike Module 02). Self-computed CCSD(T) data must be made genuinely **publicly available** (e.g., published to GitHub/Zenodo alongside code) to defensibly satisfy "publicly available and appropriate for academic use" under a literal reading of the rubric.

### Module 05 — Deep Learning Systems
**Category: (A) natural fit.**

- **Proposal:** the actual flagship **hybrid FNO-NCA architecture on benzene (Phase 5)** — the local $3\times3\times3$ NCA update *is* a 3D-CNN-family architecture (voxel-grid convolutions). The required controlled comparison (Task 4) is **local-CNN-only vs. full hybrid FNO+CNN**, i.e., with/without the spectral Poisson layer — a real, scientifically meaningful ablation, not an arbitrary hyperparameter tweak.
- **Why it satisfies the rubric:** PyTorch, explicit CNN-family architecture, genuine controlled experiment with a clearly stated "what changed / what stayed the same," own dataset (benzene, ≥5,000 configs) distinct from Module 04's H₂O set — satisfying the "not reused from ANY previous capstone project" rule.
- **Why it's genuinely valuable:** this is the actual thesis centerpiece (§7 Phase 5) — no invention needed, just correct framing/justification of the architecture as "CNN-family" for the rubric.
- **Risk/mitigation:** must explicitly justify the CNN framing in the report (cite the local-convolution structure) so a grader doesn't view a physics-simulation architecture as evading the CNN/RNN/Transformer requirement.

### Module 06 — Generative AI Applications
**Category: (B) bridge project, with a (D) flavor.**

- **Proposal:** train a VAE (or small diffusion model) over the manifold of already-computed CCSD(T) benzene configurations (positions, possibly energies) to **generate new candidate displaced geometries**, as a learned alternative/supplement to the deterministic normal-mode + thermal-displacement + rigid-rotation sampling scheme in §5. Generated configurations are validated by running real PySCF CCSD(T) on a sample of them (ground-truth check), evaluated by: physical plausibility of bond lengths/angles, energy-distribution overlap vs. the training configs, and explicit discussion of failure cases (e.g., generated geometries with unphysical bond lengths).
- **Why it satisfies the rubric:** real generative model (VAE/diffusion), own dataset (not reused), qualitative + quantitative evaluation of generated samples, concrete failure-case discussion.
- **Why it's genuinely valuable:** a validated generative sampler is a legitimate mechanism for expanding/diversifying the training set beyond hand-designed normal-mode sampling — directly useful for later scaling to larger PAHs (§4, large-PAH outlook), where hand-crafted sampling schemes become impractical.
- **Ethics angle (non-generic):** the concrete, system-specific risk is a generative model silently producing subtly-wrong/hallucinated geometries that poison downstream CCSD(T)-labeled training data if not validated — a real data-integrity risk unique to this pipeline, not generic "AI bias" boilerplate.

### Module 07 — Design of Agentic Workflows
**Category: (B)/(C) bridge project.**

- **Proposal:** a "computational-chemistry lab assistant" agent that automates the §7 Go/No-Go phase-gate decisions and the §8 ten-point QA protocol. Tools: invoke PySCF for a new CCSD(T) calculation, invoke the trained PES model for inference, run a force finite-difference check, produce a convergence plot. Memory/state: persisted log of which phase-gate checks have already run and their pass/fail status. Reasoning: given a phase's numeric Go/No-Go thresholds (§7 table), decide PASS/FAIL/NEEDS-MORE-DATA, and if borderline, decide what additional check to run next.
- **Why it satisfies the rubric:** real reasoning/decision logic, real tool use (PySCF, inference, finite-difference), real memory/state (phase-gate history), architecture diagram of agent ↔ tools ↔ log.
- **Why it's genuinely valuable:** automates tedious, error-prone manual verification (§8) that the plan explicitly requires "throughout, not just at Phase 0" — reduces the risk of a human silently skipping a required check.
- **Ethics angle (non-generic):** the specific, concrete risk is an autonomous agent falsely declaring a Go decision without having actually executed the required numeric check — a real correctness/safety concern for *this* system, addressed by a hard safeguard: the agent must refuse to output PASS without citing the exact measured value against the exact threshold it checked.

### Module 08 — Industry-Integrated AI Systems Synthesis
**Category: (A) natural fit** (by design — depends on 04–07 being built first).

- **Proposal:** integrate ≥3 of {04 baseline model, 05 benzene FNO-NCA model, 06 generative augmentation model, 07 QA agent} under an industry frame tying back to the project bibliography's own culminating application ([Relevant_Scientific_Papers.md](Relevant_Scientific_Papers.md) item 15, JWST/astrochemical PAH detection): "AI-accelerated infrared spectral identification for atmospheric/astrochemical sensing," where 05 is the predictive engine, 07 is the reliability/deployment-gate layer, 06 is the mechanism for extending coverage to new molecules, and 04 is the evidence justifying the field-based approach over simpler baselines.
- **Why it satisfies the rubric:** integrates ≥3 prior projects explicitly and intentionally, industry-specific framing, reflective paper can honestly trace how each prior artifact informed the design (because it's true, not fabricated for the assignment).

### Cross-cutting open risk (applies to Modules 04–06)

Modules 04–06 forbid "synthetic/AI-generated" datasets. CCSD(T)-computed configurations are legitimate first-principles ab initio scientific data (produced by a deterministic quantum-chemistry solver, PySCF, not by a generative AI/ML model), but every report should include one explicit sentence pre-empting misreading, e.g.: "This dataset was computed via ab initio coupled-cluster [CCSD(T)] quantum chemistry using PySCF, a first-principles numerical method — not an AI/ML-generated synthetic dataset."

---

## 4. Final Module → Dataset/Deliverable Mapping (Pass 4 — resolved 2026-08-20)

| Module | Exact dataset | Format & size | Key deliverable files | Depends on |
|---|---|---|---|---|
| 02 | QM9 properties table (Ramakrishnan et al. 2014), random subset of ~5,000–10,000 molecules, minus the ~3,054 QM9-flagged "uncharacterized" geometries | Single CSV, rows = molecules, columns = SMILES, atom count, μ, α, HOMO, LUMO, gap, ZPVE, U₀, Cᵥ, etc. (≫5 cols, ≫200 rows) | `data_workflow.ipynb`, `module_summary.pdf`, `README.md`, `requirements.txt`, GitHub repo | None |
| 03 | Phase 0 numerical-foundation sweep results (own-generated, not QM9) | CSV, one row per sweep trial: `trial_id, sigma_over_dx, delta_x_angstrom, translation_step, energy_hartree, force_error, egg_box_amplitude` — 5 σ/Δx ratios × ~50 translation steps + grid-convergence rows ⇒ several hundred rows | `analysis.ipynb`, `module_summary.pdf`, sweep-results CSV, `requirements.txt` | **Phase 0 engine must already be built** (Gaussian nuclear density, Hockney–Eastwood Poisson solver, autograd forces) — a real code dependency, not just a scheduling one |
| 04 | H₂O CCSD(T)/cc-pVTZ configuration set (Phase 1), ≥2,000 configs | CSV, one row per config: `config_id, r_OH1, r_OH2, theta_HOH, energy_hartree, fx_O, fy_O, fz_O, fx_H1, …` (bond-length/angle descriptor → energy/forces; deliberately *not* the 3D density grid, since Phase 4's baseline is explicitly "non-field") | `modeling.ipynb`, `Machine_Learning_Analysis_Report.pdf`, `requirements.txt`, dataset CSV **published to a public GitHub/Zenodo release** | Phase 1 H₂O CCSD(T) generation pipeline (PySCF) |
| 05 | Benzene CCSD(T) configuration set (Phase 5), ≥5,000 configs, 64³ grid | Volumetric tensors (`.npz`/HDF5), one file per config: nuclear positions, target ρ(r), E, F, selected Hessian entries — plus an indexing manifest CSV (`config_id → file path → summary scalars`); **not CSV-only**, since Module 05 has no tabular-format requirement (deep-learning modules commonly use non-tabular data) | `deep_learning.ipynb`, `Deep_Learning_Systems_Analysis_Report.pdf`, `requirements.txt`, dataset **hosted externally (Zenodo) with documented access instructions**, per the rubric's explicit allowance | Phase 5 benzene CCSD(T) generation — **the single biggest compute bottleneck in the whole plan**, flag as a scheduling risk |
| 06 | New, independent corpus: ~1,000–2,000 ground-state + normal-mode-displaced geometries across 5–8 small aromatic/substituted-benzene molecules (toluene, pyridine, aniline, phenol, styrene, furan, pyrrole), computed at a **cheaper, consistent level (e.g. HF/6-31G or B3LYP/6-31G\*)** | XYZ/`.npz` geometry files + manifest CSV | `generative_ai.ipynb`, `Generative_AI_Analysis_Report.pdf`, `requirements.txt`, geometry corpus | None (can run in parallel with 04/05) — **but see precision exception below** |
| 07 | No new dataset — operates as a tool-using agent over the **real logged results of Phases 0–3** (Phase 0 sweep, Phase 1 H₂O training, Phase 2 emergent-IR run, Phase 3 D₂O/CO₂ zero-shot hardness tests), invoking PySCF/inference/finite-difference as tools | Agent transcript/log (JSON or similar) + architecture diagram | `agentic_system.ipynb`/`.py`, `Agentic_AI_Systems_Analysis_Report.pdf`, architecture diagram, `requirements.txt` | Phases 0–3 must have real results to operate on; **Phases 2 & 3 (currently unassigned to any module) get their natural home here** — the agent's demoed tool-use tasks *are* the Phase 2 MD/FFT run and the Phase 3 D₂O/CO₂ checks |
| 08 | No new dataset — integrates artifacts from ≥3 of {04, 05, 06, 07} | Reflective_Synthesis_Paper.pdf + integrated artifact | `Reflective_Synthesis_Paper.pdf`, integrated artifact/diagrams | 04, 05, 06, 07 (needs ≥3 of these complete first) |

### Notes arising from consolidation

- **Phase 4's full 3-way baseline comparison** (simple NN vs. equivariant atomistic ML PES vs. finite-difference CCSD(T)) doesn't need to be crammed entirely into Module 04 — Module 04 only needs to deliver *one* leg (the simple non-field NN baseline) to satisfy its own rubric. The full comparison table naturally belongs in **Module 08's synthesis paper**, using 04's and 05's results as direct inputs — this also strengthens 08's "genuinely integrates ≥3 prior projects" requirement rather than just narrating them side by side.
- **Module 06 precision question:** its training corpus is deliberately *not* CCSD(T)-level — flagged here for formal re-check in Pass 5 (see §5 below, where this is resolved as *not* actually a deviation from the precision mandate).
- **Distinctness check:** 02 (QM9 properties), 03 (Phase 0 sweep), 04 (H₂O descriptors), 05 (benzene volumetric), 06 (independent small-aromatic corpus) are all disjoint sources/formats/molecules — no dataset-reuse violations across 02–06.
- **Dependency chain is now explicit and mostly linear:** Phase 0 code (→03) → Phase 1 H₂O data (→04) → Phase 5 benzene data (→05, the long pole) → Phases 2/3 results (→07, alongside 04/05's outputs) → 08 (needs 04/05/06/07). Module 06's corpus has no dependency and can be produced any time in parallel.

---

## 5. Validation Against Non-Negotiables (Pass 5 — resolved 2026-08-20)

### 5.1 Overarching_Goal.md checklist

| Requirement | Applies to | Status |
|---|---|---|
| Train/Validation/Test sets must be chemically precise (CCSD(T)/CBS, sub-cm⁻¹) | 04 (H₂O), 05 (benzene) — the actual pipeline's ML data | **Compliant.** Both are explicitly CCSD(T)/cc-pVTZ per §5 of the Distilled Plan. |
| Deviation only with "absolutely no other technical solution" + "extremely compelling, well-documented reason" | 06 (cheaper-level corpus) | **Reclassified — no deviation needed at all** (see §5.3 below), not merely an accepted exception. |
| Small molecules (QM9/ANI-1ccx) OK for validating pipeline *mechanics* | 02 | **Compliant, with a scope caveat**: Module 02's QM9 use is EDA-only, not a mechanics test of the real pipeline code — see required disclaimer in §5.4. |
| Leverage latest architectures, don't reinvent the wheel | 04 (KRR/GPR precedent), 05 (FNO/NCA hybrid), 06 (VAE/diffusion), 07 (standard agent/tool-use pattern) | **Compliant** — all use established architecture families, nothing bespoke-for-its-own-sake. |

### 5.2 Distilled Plan §4 ("what the project is NOT") checklist

| Constraint | Applies to | Status |
|---|---|---|
| NOT a GNN (no discrete atom-nodes/bond types) | 04, 05 | **Compliant.** 04 uses a descriptor/kernel regressor (not a graph net); 05's grid/voxel CNN+FNO has no atom-graph structure. |
| NOT DFT, no exceptions for pipeline data | 04, 05 (the real pipeline) | **Compliant** — both CCSD(T). DFT/HF-level data appears *only* in 02 and 06, which are formally outside the pipeline's train/val/test sets (§5.3). |
| NOT purely local CA — needs FNO/global Poisson layer | 05 | **Compliant by design**, and directly demonstrated by 05's own required controlled experiment (local-only vs. +FNO). |
| NOT density-first / Route A for forces | 05 | **Action item:** report must explicitly state Route B (energy-first, autograd forces) is used — add to Module 05 report checklist. |
| NOT trained on spectral loss | 05 | **Action item:** Module 05's loss must be the multitask $L_E+L_F+L_H+L_\rho$ only; any Phase 2 MD/FFT spectrum shown (e.g., in Module 07's agent demo) must be presented as a frozen-weight, post-hoc *evaluation*, never as a training signal. |
| NOT periodic/naive Poisson solver | 03 (Phase 0 validation), 05 | **Compliant** — Module 03's sweep explicitly tests the Hockney–Eastwood solver. |
| NOT claiming egg-box elimination, only control | 03 | **Action item:** report wording must say "reduced/controlled as a function of σ/Δx," never "eliminated." |
| NOT quantum computing | — | Not touched by any module; no action needed. |
| NOT claiming chemical precision for large PAHs as core deliverable | 08 (synthesis paper) | **Action item:** any mention of scaling beyond benzene must be framed as outlook/future work only, per §9's defensible-claims list. |
| NOT quantum-mechanical rovibrational line-list precision | 05, 07 (if Phase 2 spectra shown), 08 | **Action item:** all spectral claims must use §9's approved wording ("band positions and relative envelopes/intensities within a stated cm⁻¹ tolerance"), never "chemically precise spectral lines." |
| NOT naphthalene as a pass/fail milestone | 08 | **Action item:** if mentioned at all, explicitly labeled exploratory/outlook, matching the Distilled Plan's own treatment. |
| NOT requesting supercomputer time up front | 05 | **Note, not a violation:** Module 05's benzene training is the plan's biggest compute bottleneck (already flagged in §4). Scope it for local/consumer hardware first, per the plan's own explicit choice; only revisit HPC access if the local run genuinely can't complete. |
| NOT skipping baseline comparisons | 04, 08 | **Compliant** — 04 supplies the simple-NN baseline; 08 assembles the full 3-way comparison. |

### 5.3 Compliance boundary (new, clarifies §4's dataset table)

DFT/HF-level data appears in exactly two places — **Module 02's QM9 subset** and **Module 06's small-aromatic corpus** — and in both cases it is formally outside the actual research pipeline's train/validation/test sets:

- **Module 02** is pure EDA on a public benchmark; its conclusion (QM9 isn't precise enough) is *why* the real pipeline doesn't use it. It never feeds Phase 0–5.
- **Module 06's generative model is a sampling/proposal mechanism, not a data source.** This is functionally identical to the Distilled Plan's own already-approved sampling schemes in §5 (normal-mode displacement, random thermal displacement, rigid rotation/translation) — none of *those* are "chemically precise" processes either; they're just ways of proposing candidate geometries, which only become training data once evaluated at CCSD(T). A learned (VAE/diffusion) proposal distribution is the same kind of thing. **Every candidate the Module 06 model generates must be re-computed at full CCSD(T) before it is ever used anywhere in the actual pipeline.** Under this framing, Module 06 does **not** need to invoke the Overarching Goal's deviation/escape clause at all — reclassified from "exception" to "compliant by construction." This must be stated explicitly in the Module 06 report to preempt a grader or reviewer reading it as a precision compromise.

### 5.4 Resolved risks (carried over from Pass 3/4)

- **Module 04 "Accepted Sources" risk — RESOLVED (mitigation planned):** publish the H₂O CCSD(T) dataset to a public GitHub release / Zenodo DOI before submission, and cite it in the report as the dataset source. Self-generated ab initio data alongside open-sourced generation code is standard practice in computational chemistry and satisfies "publicly available and appropriate for academic use" even though it isn't drawn from the four named example sources (which are illustrative, not exhaustive, for domain-specific capstones).
- **Module 02 disclaimer — action item:** the report must state plainly that QM9 is used solely for this module's no-ML EDA requirement, is *not* part of the actual research pipeline's data, and its own precision level is the explicit motivation for why the real pipeline uses custom CCSD(T) data instead.

---

## 6. Next Steps

- [x] **Pass 3:** Formal gap analysis session — go tension-by-tension above, decide A/B/C/D category, sketch what the bridge/check project would concretely contain.
- [x] **Pass 4:** Draft full module→phase mapping table (one row per module 02–08), consolidating Pass 3's proposals into final form (dataset names, exact deliverable filenames, explicit dependency order since 08 depends on 04–07).
- [x] **Pass 5:** Validate draft against Overarching_Goal.md non-negotiables and Distilled Plan §4 ("what the project is NOT"); Module 04 publication risk resolved via mitigation, Module 06 precision question reclassified as compliant-by-construction (not a deviation), several report-wording action items identified (§5.2).
- [ ] **Pass 6:** Module-by-module sign-off, one at a time — walk through each module's final spec (dataset, deliverables, action items from §5.2/§5.4) and get explicit go-ahead before implementation begins.
