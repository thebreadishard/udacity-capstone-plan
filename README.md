# Udacity AI Mastery — Capstone Project Plan

> **This repository is a planning and coordination artifact.** It does not contain the
> implementation of the research itself. Its purpose is to design a coherent project plan
> that distributes an ambitious, multi-phase computational-chemistry research effort across
> the Udacity Master in AI capstone sequence (Modules 02–08), ensuring every module both
> advances the scientific goal *and* satisfies the school's rubric.

---

## The Overarching Goal

**Acquire chemically precise anharmonic infrared spectra for arbitrarily sized Polycyclic
Aromatic Hydrocarbons (PAHs).**

The leading strategy is a machine-learning pipeline that maps molecular geometry directly
to a potential energy surface (PES), from which IR spectra emerge via classical molecular
dynamics — but the ML pipeline is only a means to an end. Any approach that reliably and
efficiently yields chemically precise spectra (< 1 kcal/mol error, sub-wavenumber
precision, grounded in CCSD(T) or complete-basis-set-limit calculations) is a valid path.

The actual implementation of this pipeline will be carried out across separate capstone
project repositories. This repo answers the question: *"How do we slice this research
program into 7 individually gradeable capstone projects that are each self-contained,
rubric-compliant, and collectively build toward the end goal?"*

For full details see:

- [`GoalGathering/Overarching_Goal.md`](GoalGathering/Overarching_Goal.md) — the prime
  directive and precision requirements.
- [`GoalGathering/Distilled_Project_Plan_and_Quality_Checks.md`](GoalGathering/Distilled_Project_Plan_and_Quality_Checks.md)
  — the complete technical plan (architecture, data pipeline, phased roadmap, QA protocol).

---

## How the Plan Maps to Capstone Modules

The research plan defines six execution phases (0–5) plus an outlook. These are distributed
across the seven gradeable Udacity capstone modules as follows:

| Module | Title | Research Phase | What It Delivers |
|--------|-------|----------------|------------------|
| **02** | AI Programming Foundations | *(Motivation)* | EDA on QM9 benchmark → documented justification for why custom CCSD(T) data is needed |
| **03** | Statistical Analysis | Phase 0 | Hypothesis tests on the differentiable-physics engine's numerical foundation (egg-box, grid convergence) |
| **04** | Applied ML | Phase 4 (partial) | Simple non-field NN baseline trained on the H₂O CCSD(T) **descriptor CSV** — one leg of the required three-way comparison |
| *(P1)* | *Ungraded workstream* | Phase 1 | H₂O hybrid FNO-NCA field PES (\(32^3\)) — research infra, not a Udacity module; must exist before Module 07 |
| **05** | Deep Learning Systems | Phase 5 | The flagship hybrid FNO-NCA architecture on benzene (CNN-family, with ablation study) |
| **06** | Generative AI | *(Bridge — B/D)* | VAE/diffusion model for generating candidate molecular geometries to augment training data |
| **07** | Agentic Workflows | Phases 2 & 3 | Computational-chemistry lab-assistant agent automating Go/No-Go QA checks and phase-gate decisions |
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
│   ├── Overarching_Goal.md      # Prime directive & precision requirements
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
│   └── 09_Professional_Industry_Defense.md
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
- **Strictly non-DFT *data*:** all training targets are CCSD(T)/cc-pVTZ, with no
  library XC functionals (B3LYP/PBE/…). The Hohenberg–Kohn *shape* is the claim.
- **Emergent spectroscopy:** IR spectra are *not* trained on — they emerge as blind
  predictions from frozen-weight MD simulations via dipole-autocorrelation FFT.
- **Phased roadmap with hard Go/No-Go gates:** H₂O → D₂O/CO₂ (zero-shot) → benzene,
  each with quantitative pass/fail thresholds.

---

## Current Status

The planning phase is substantially complete (Passes 1–5 of the mapping document are
done). Phase 1 of the research plan is owned by ungraded Workstream P1 (see the mapping
§4.1), not by a Udacity module. The remaining mapping step before implementation begins:

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
