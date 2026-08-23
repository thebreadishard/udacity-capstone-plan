# Udacity AI Mastery — Capstone Project Plan

> **This repository is a planning and coordination artifact.** It does not contain the
> implementation of the research itself. Its purpose is to design a coherent project plan
> that distributes an ambitious, multi-phase computational-chemistry research effort across
> the Udacity Master in AI capstone sequence (Modules 02–08), ensuring every module both
> advances the scientific goal *and* satisfies the school's rubric.

---

## The Overarching Goal

> **Pivot, 2026-08-23.** The prime directive was rewritten. The paragraph below is current; anything
> elsewhere in this repository that still describes a voxel field PES, own CCSD(T) volumetric
> campaigns, or H₂O band envelopes as the deliverable is **pre-pivot** and carries a banner saying so.
> Rationale and evidence: [`GoalGathering/Restructure_Proposal_2026-08-23_Project12_in_Module08.md`](GoalGathering/Restructure_Proposal_2026-08-23_Project12_in_Module08.md).

**This thesis (R3):** **anharmonic infrared band families and relative intensities for named PAH
sizes and charge states**, from a potential-energy surface anchored to a **measured** coupled-cluster
gold rung, with quantum nuclear motion (GVPT2-class) and a **four-term error budget** — ending in a
**pre-registered, fail-closed identification** against one frozen JWST/PAHdb product.

Precision is carried by the **theory ladder** and the **nuclear-motion method**, not by a novel neural
architecture. Established equivariant machine-learned potentials are fine-tuned and Δ-learned up to
the gold rung; the contribution is the anchor, the budget and the fail-closed rule.

Not claimed: rovibrational **line lists**, sub-wavenumber lines, or "any size" without the measured
stop rung attached. Classical MD + dipole-ACF FFT is a diagnostic, not the deliverable.

**There is no post-master's horizon.** Projects 10–12 are absorbed into Modules 03–08 and kept only as
provenance. Whatever R3 does not reach is a **limitation in Module 08**, never a queued project.

The actual implementation of this pipeline will be carried out across separate capstone
project repositories. This repo answers the question: *"How do we slice the **master's** research
program into 7 individually gradeable capstone projects that are each self-contained,
rubric-compliant, and collectively deliver R3 — without promising a PAH line list?"*

For full details see:

- [`GoalGathering/Overarching_Goal.md`](GoalGathering/Overarching_Goal.md) — the prime
  directive: R1/R2/R3, the four-term error budget, and the labels / spectra / identification split.
- [`GoalGathering/Restructure_Proposal_2026-08-23_Project12_in_Module08.md`](GoalGathering/Restructure_Proposal_2026-08-23_Project12_in_Module08.md)
  — why the plan changed, the alternatives weighed, the literature, and the module remap.
- [`GoalGathering/Distilled_Project_Plan_and_Quality_Checks.md`](GoalGathering/Distilled_Project_Plan_and_Quality_Checks.md)
  — the technical plan. **Currently mid-rewrite; read its banner first.**

---

## How the Plan Maps to Capstone Modules

> **PRE-PIVOT TABLE.** The mapping below is the voxel-era one. The proposed replacement is in
> [`Restructure_Proposal_2026-08-23_Project12_in_Module08.md`](GoalGathering/Restructure_Proposal_2026-08-23_Project12_in_Module08.md)
> section 7, and is deliberately **not** written here yet: the mapping is ratified only after the
> Distilled Plan rewrite and a Round-4 review, so that a rejected pivot does not cost two rewrites.

The research plan defines six execution phases (0–5) plus an outlook. These are distributed
across the seven gradeable Udacity capstone modules as follows:

| Module | Title | Research Phase | What It Delivers |
|--------|-------|----------------|------------------|
| **02** | AI Programming Foundations | *(Motivation)* | EDA on QM9 benchmark → documented justification for why custom CCSD(T) data is needed |
| **03** | Statistical Analysis | Phase 0 | Hypothesis tests on the differentiable-physics engine's numerical foundation (egg-box, grid convergence) |
| **04** | Applied ML | Phase 4 (partial) | Simple non-field NN baseline trained on the H₂O CCSD(T) **descriptor CSV** — one leg of the required three-way comparison |
| *(P1)* | *Ungraded workstream* | Phase 1 | H₂O hybrid FNO-NCA field PES (\(32^3\)) — research infra, not a Udacity module; must exist before Module 07 |
| **05** | Deep Learning Systems | Phase 5 | The flagship hybrid FNO-NCA architecture on benzene (CNN-family, with ablation study) |
| **06** | Generative AI | *(Bridge — B/D)* | VAE **representation learning** on a cheap **non-benzene** aromatic corpus (proposal only; not pipeline labels) |
| **07** | Agentic Workflows | Phases 2 & 3 | Computational-chemistry lab-assi: reliability-gated **small-molecule** IR emulation (JWST/PAH ID is horizon, not a built capability) |
| *(10)* | *Post-master’s* | Horizon | Size-extensive gold-anchored aromatic PES — not a Udacity module |
| *(11)* | *Post-master’s* | Horizon | GVPT2-class anharmonic bands + intensities — not a Udacity module |
| *(12)* | *Post-master’s* | Horizon | Fail-closed astrophysical identification — not a Udacity module
| **08** | Industry Synthesis | Phase 4 (full) | Integrates ≥ 3 prior projects under an industry frame (AI-accelerated spectral ID for astrochemistry) |

Each mapping is categorized as **(A)** natural fit, **(B)** bridge project, **(C)** QA
project, or **(D)** forward-looking value-add — and justified against both the rubric and
the research plan. See
[`GoalGathering/Capstone_Mapping.md`](GoalGathering/Capstone_Mapping.md) for the full
gap analysis, dataset assignments, dependency chain, and validation against project
non-negotiables.

---

## Repository Structure

```
CapstonePlan/
├── GoalGathering/               # Research planning artifacts
│   ├── Overarching_Goal.md      # Prime directive & audited precision rules
│   ├── Distilled_Project_Plan_and_Quality_Checks.md
│   │                            # Full technical plan: architecture, data,
│   │                            # phased roadmap (Phases 0–5), QA protocol
│   ├── Capstone_Mapping.md      # Module-by-module mapping (Passes 1–5 + P1),
│   │                            # gap analysis, dataset table, validation
│   ├── Relevant_Scientific_Papers.md
│   │                            # Annotated bibliography (15 key papers)
│   ├── Papers/                  # Reference PDFs (numbered to match bibliography)
│   └── AI_Chats/                # Full transcripts of planning sessions with
│                                # Gemini & Grok (used as "strict professors")
│
├── CapstoneProjects/            # Udacity rubric requirements (scraped & cleaned)
│   ├── 01_APA_Resources.md
│   ├── 02_AI_Programming_Foundations_Project.md
│   ├── 03_Conduct_a_Statistical_Analysis_Using_Python.md
│   ├── 04_Applied_Machine_Learning.md
│   ├── 05_Deep_Learning_Systems.md
│   ├── 06_Generative_AI_Applications.md
│   ├── 07_Design_of_Autonomous_and_Semi_Autonomous_Agentic_Workflows.md
│   ├── 08_Industry_Integrated_AI_Systems_Synthesis.md
│   ├── 09_Professional_Industry_Defense.md
│   ├── 10_Size_Extensive_Aromatic_PES.md      # post-master’s; not Udacity
│   ├── 11_Anharmonic_IR_and_Intensities.md    # post-master’s; not Udacity
│   └── 12_Astrophysical_PAH_Identification.md # post-master’s; not Udacity
│
├── scraper/                     # Tooling used to extract rubric content
│   ├── scraper.py               # Playwright-based Udacity classroom crawler
│   ├── generate_markdown_files.py
│   │                            # Converts scraped HTML → clean Markdown
│   ├── parser.py                # HTML parsing utilities
│   ├── parse_gemini_snapshot.py  # Extracts Gemini chat transcripts
│   ├── parse_grok_snapshot.py   # Extracts Grok chat transcripts
│   └── summarize.py             # Summarization helper
│
├── requirements.txt             # Python dependencies (Playwright, BS4, etc.)
├── .gitignore
└── README.md                    # ← You are here
```

---

## The Research Plan at a Glance

The technical plan (fully detailed in [`Distilled_Project_Plan_and_Quality_Checks.md`](GoalGathering/Distilled_Project_Plan_and_Quality_Checks.md))
proposes a **hybrid Fourier Neural Operator – Neural Cellular Automaton (FNO-NCA)**
architecture operating on continuous 3D electron-density fields. Key design choices:

- **Energy-first (Route B):** \(E=\mathcal{E}[\rho,R]\) — fixed Hockney–Eastwood
  electrostatics plus a learned remainder \(\varepsilon_\theta[\rho]\). No latent
  energy head. Forces come from autograd through \(\rho_\theta\).
- **Same-surface non-DFT energies and derivatives:** CCSD(T)/cc-pVTZ per
  Distilled Plan §5.1. Derivatives are complete gradients or seeded directional
  derivatives of that same energy; CCSD forces are never paired with CCSD(T)
  energies as targets. Density is the pinned 1-RDM recipe (default: relaxed CCSD),
  not a slogan “exact CCSD(T) density.” No library XC functionals in the pipeline
  unless the §5.1 shrink ladder fires. The Hohenberg–Kohn *shape* is the claim.
- **Frozen-weight spectroscopy without spectral fitting:** the production dipole surface
  is supervised on static dipoles, but spectra, peak positions, intensities and dipole
  derivatives are never training targets. Band positions and envelopes are evaluated
  post hoc from frozen-weight MD via dipole-autocorrelation FFT.
- **Phased roadmap with hard Go/No-Go gates:** H₂O → D₂O/CO₂ (zero-shot) → benzene,
  each with quantitative pass/fail thresholds.

---

## Current Status

The planning phase is substantially complete (Passes 1–5 of the mapping document are
done). Phase 1 is owned by ungraded Workstream P1 (mapping §4.1). Energy is an
implementable \(E=\mathcal{E}[\rho,R]\) (Distilled Plan §6). Data generation is a
method plus a measured cost pilot (Distilled Plan §5.1), not “CCSD(T) via PySCF.”
The prime directive matches Distilled Plan §9 (issue 4). Rubric landmines are
locked (issue 5: \(\ge 500\)-row Module 03 table, one Module 06 VAE story, DOI
before claim). The GNN baseline is Workstream G1 (issue 6): MACE on the same
P1/05 splits; Module 08 assembles only. Horizon PAH work is Projects 10–12.
Pass 6 remains open. All six professor-review *spec* issues are closed.

- **Pass 6:** Module-by-module sign-off — walk through each module's final specification
  and get explicit go-ahead.

---

## How This Repo Was Built

1. **Rubric extraction:** the Udacity capstone classroom was scraped using Playwright
   ([`scraper/scraper.py`](scraper/scraper.py)) and converted to clean Markdown
   ([`scraper/generate_markdown_files.py`](scraper/generate_markdown_files.py)).
2. **Goal gathering:** the overarching research goal was refined through multi-round
   adversarial planning sessions with Gemini and Grok (transcripts preserved in
   [`GoalGathering/AI_Chats/`](GoalGathering/AI_Chats/)), including a 23-point external
   review that forced a ground-up revision of the technical plan.
3. **Mapping:** the refined research plan was systematically decomposed and mapped onto
   the rubric requirements module by module, with gap-fill proposals categorized and
   justified ([`GoalGathering/Capstone_Mapping.md`](GoalGathering/Capstone_Mapping.md)).

---

## Key References

A curated bibliography of 15+ papers tracing the computational track record from foundational
quantum ML (QM9, SchNet) through CCSD(T)-precision anharmonic spectra to JWST-era
astrochemical PAH identification is maintained in
[`GoalGathering/Relevant_Scientific_Papers.md`](GoalGathering/Relevant_Scientific_Papers.md),
with corresponding PDFs in [`GoalGathering/Papers/`](GoalGathering/Papers/).

---

## Setup

This repo's Python dependencies are only needed if you want to re-run the scraping tools:

```bash
python -m venv .venv
.venv\Scripts\activate    # Windows
pip install -r requirements.txt
playwright install chromium
```

The planning documents themselves are plain Markdown and require no setup to read.
