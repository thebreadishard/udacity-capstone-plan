# Restructure Proposal — pull Project 12's exit into Module 08

**Status:** Proposal, 2026-08-23. Not yet adopted. Nothing in
[Distilled_Project_Plan_and_Quality_Checks.md](Distilled_Project_Plan_and_Quality_Checks.md),
[Overarching_Goal.md](Overarching_Goal.md) or [Capstone_Mapping.md](Capstone_Mapping.md) has been
changed. This document is the argument; adoption is a separate decision.

**Brief given:** reshape the whole (not-yet-executed) project so that the end result of
[Project 12](Horizon/12_Astrophysical_PAH_Identification.md) is delivered inside
Module 08. Any design element may change, including the voxel/field approach. The only hard
constraint: at the end of the master's capstone, chemically precise IR spectra are predicted.

---

## 1. The constraint, made numerical before anything else

"Chemically precise IR spectra" has to be pinned down first, because the entire review history of
this repository is a record of that phrase being ambiguous and then being killed by a professor.
Three readings exist:

| Reading | What it means | Achievable in a master's? |
|---|---|---|
| **R1 — line lists** | ExoMol/POKAZATEL-grade rovibrational transitions, sub-cm⁻¹, \(I\propto\lvert\langle f\lvert\mu\rvert i\rangle\rvert^2\) | **No.** Not for a 3-atom molecule inside this budget, and not for any PAH by anyone. This is a career. |
| **R2 — band envelopes** | Band centers ±10–15 cm⁻¹, relative envelopes, classical MD + dipole ACF | Yes — this is the *current* plan's Module 08 exit. But it is also **already published at PAH scale** (see §4, Mai et al. 2025). Delivering it is not a contribution. |
| **R3 — anharmonic band families** | Quantum anharmonic (GVPT2-class) band centers within a **stated** cm⁻¹ of a named experimental standard, **plus** relative integrated intensities from a dipole moment surface, **plus** a four-term error budget | Yes, with the restructure below. This is exactly [Project 11](Horizon/11_Anharmonic_IR_and_Intensities.md)'s exit and it is what identification actually consumes. |

**This proposal adopts R3 and states it once, in the prime directive.** R3 is the strongest reading
that survives a defense. Promising R1 loses Module 09 in one question; delivering R2 in 2028 loses
it in a different question ("this was done in 2025, what did you add?").

Target numbers, to be frozen before any campaign, with the same claim-ladder discipline the plan
already uses for CCSD(T)/CBS(T,Q):

- Band centers: ≤ 10 cm⁻¹ vs gas-phase experiment where it exists; ≤ 15 cm⁻¹ vs matrix data **with**
  a stated, frozen matrix-shift model.
- Relative integrated intensities within a band family: ≤ 20 %, with charge-state intensity swaps
  reproduced qualitatively (neutral vs cation 6–9 μm / 11–12 μm reversal).
- Error budget separated into (A) ML/PES error vs the gold rung, (B) gold-rung electronic-structure
  error vs canonical CCSD(T), (C) nuclear-motion error (GVPT2 vs VCI or vs experiment),
  (D) environment error (matrix shift / excitation model).

A single pooled "we are within X cm⁻¹" number remains a fail, exactly as
[Project 11 §3.4](Horizon/11_Anharmonic_IR_and_Intensities.md) already demands.

---

## 2. Diagnosis — why the current plan cannot reach that endpoint

The plan is not slow because it is careless. It is slow because **it spends its entire budget
inventing the thing that carries the least precision.**

From [Capstone_Mapping §8.2](Capstone_Mapping.md#82-effort-estimates-and-owners), of the 840-hour
fixed-work baseline (which already excludes both PySCF campaigns and the HPC audit):

| Item | Human hours | Contributes to a spectrum? |
|---|---:|---|
| Phase 0a engine + artifact sweeps | 160–240 | No — it validates a discretization |
| P1 H₂O field PES | 120–160 | Indirectly, one 3-atom molecule |
| Module 05 (benzene field) | 120–160 | Indirectly, one molecule |
| Module 03 (statistics on egg-box sweeps) | 40–80 | No |
| **Subtotal spent on the representation** | **440–640** | |
| Phases 2–3 + Module 07 | 120–160 | Yes |
| Modules 02, 04, 06, 08, 09 | 240–360 | Partly |

Roughly **two thirds of the fixed budget goes into making a voxel grid behave**, and the payoff is a
verdict on a research question (§2 of the Distilled Plan) whose pre-registered outcome table already
contains "inconclusive" as a likely and publishable answer.

Three further structural blockers, each independently fatal to reaching Project 12's exit through
more of the same:

1. **The global \(N^3\) cube does not size-extend.** Cost grows with box volume, not atom count.
   [Project 10 §2](Horizon/10_Size_Extensive_Aromatic_PES.md) already says this. A
   64³ grid was the *benzene* long pole; coronene needs a box roughly an order of magnitude larger
   in volume.
2. **Canonical CCSD(T)/cc-pVTZ labels stop at benzene.** The plan's own shrink ladder anticipates
   that even benzene may not fit. There is no path from there to naphthalene, let alone a cation.
3. **Classical MD + dipole-ACF FFT is structurally incapable of R3.** No zero-point energy, no
   resonance treatment, no quantum intensities. Distilled Plan §9 is honest about this — which means
   the *current* Module 08 exit is R2 by construction, and R2 is the published state of the art.

Conclusion: reaching Project 12's exit is not a scheduling problem. **It requires moving the
precision out of the neural architecture and into the theory ladder and the nuclear-motion method.**

---

## 3. Alternatives considered

| # | Option | Verdict |
|---|---|---|
| **A** | Keep everything; run Phases 0–5 faster and add PAHs at the end | **Reject.** Blockers 1–3 above. Speed does not fix a representation that scales with box volume, labels that stop at 6 carbons, and a nuclear-motion method that cannot express ZPE. |
| **B** | Keep the field PES, but train it on DFT labels to reach PAH size | **Reject.** Violates Overarching_Goal §3.A, and lands on "DFT-IR in a nicer notebook" — [Project 10](Horizon/10_Size_Extensive_Aromatic_PES.md)'s own words. Also strictly worse than existing MLMD work. |
| **C** | Delete the field idea entirely; build a conventional MLIP + VPT2 pipeline | **Partly accept.** This is the productive core, but deleting the field idea outright throws away the one genuinely original element and the pre-registered §2 experiment, which is good science that is already paid for on paper. |
| **D** | Keep the field as the *production* PES, borrow everything else | **Reject.** Same blocker 1. Also loses rotational equivariance that the competitor gets for free (Distilled §8 item 13), which is exactly the wrong trade when transferring across molecule sizes. |
| **E** | **Invert the stack: borrow the representation, own the theory anchor and the nuclear motion; demote the field to a scoped, fail-closed comparison — and reassign it from the PES to the dipole surface** | **Recommended.** Detailed below. |
| **F** | Abandon PAHs; do R3 on small molecules only (H₂O/CO₂/benzene) at world-class quality | **Reject as the goal, keep as the floor.** This is the guaranteed-deliverable fallback if the ladder in §6 stops at rung 0. It must be written into the plan as the shrink-ladder destination, not discovered in month 14. |

---

## 4. What the 2020–2026 literature already settles

Verified via arXiv on 2026-08-23. These are new bibliography entries; none of them were in
[Relevant_Scientific_Papers.md](Relevant_Scientific_Papers.md) except items 12 and 14.

**The bad news first — what is no longer novel:**

- **Mai, Wang, Pan, Schörghuber, Kovács, Carrete & Madsen (2025)**, arXiv:2503.05120, MNRAS 541,
  3073. MLMD anharmonic IR spectra for **1,704 PAHs from NASA Ames PAHdb, up to 216 carbon atoms**,
  at several temperatures, scaling linearly with system size. *This is the current Module 08 method
  (MD + ACF) already executed at a scale far beyond anything this plan proposes.* Delivering R2 on
  benzene in 2028 is not a contribution.
- **Ji, Zhang, Zou, Jiang, Jiang, Luo & Hu (2025)**, arXiv:2510.04227. DetaNet universal deep force
  field trained on QMe14S (186,102 molecules with energies, forces, **dipoles and
  polarizabilities**); MLMD + RPMD IR/Raman spectra, benchmarked on PAHs, "near-experimental"
  accuracy, ~10³× faster than AIMD.
- **Chen, Li & Li (2026)**, arXiv:2607.20015, A&A. Anharmonic IR **cascade emission** of neutral,
  cationic and anionic cyanonaphthalenes, VPT2 on B3LYP/N07D, with a microcanonical sampling
  algorithm for environment-dependent emission. *The astrophysical excitation machinery Project 12
  §3.1 asks for already exists — at B3LYP.*
- **Wang (2026)**, arXiv:2602.12531, A&A. Random-forest classification of PAH size/charge from
  full IR spectra, F1 = 0.963 over 12 categories.

**The good news — what makes R3 reachable in a master's:**

- **Kumar, Neese & Valeev (2020)**, arXiv:2008.03237, JCP 153, 094105. Near-linear-scaling
  DLPNO-CCSD(T)-F12: **CBS-quality coupled-cluster energies for systems above 550 atoms and 5,000
  basis functions, on a single multi-core computer in under three days**, RMSD 0.3 kcal/mol vs
  extrapolated canonical CCSD(T). *A gold rung on PAH-sized aromatics is a workstation job today.*
  This single fact retires most of [Project 10 §3.1](Horizon/10_Size_Extensive_Aromatic_PES.md).
- **Sylvetsky, Banerjee, Alonso & Martin (2020)**, arXiv:2001.08641, JCTC 16, 3641. The necessary
  caveat: for **delocalized / static-correlation-prone π systems**, DLPNO-CCSD(T) needs TightPNO
  settings, and LNO-CCSD(T)/tight is required for sub-kcal agreement with canonical. *This is not a
  footnote; it is the measurement that has to be made before the gold rung may be called gold.*
- **Käser & Meuwly (2021–2023)**, arXiv:2103.05491 (JCTC), arXiv:2109.08407, arXiv:2303.11685 (JCP
  158). Transfer learning lifts an ML PES from a cheap level to CCSD(T)/CCSD(T)-F12 quality using
  **on the order of 100 high-level points**; "NN + VPT2" then reproduces experiment within 20 cm⁻¹
  for ~90 % of modes and within 10 cm⁻¹ for >60 %. *The label campaign becomes hundreds of points,
  not thousands of volumetric cubes.*
- **Kotaru, Qu, Nandi, Houston & Bowman (2026)**, arXiv:2604.20040. Released Fortran/Python software
  that builds a **quartic force field and runs VPT2 directly from a machine-learned potential**:
  21-atom aspirin, 32,509 unique cubic force constants, **~1 minute on a laptop**. Described by the
  authors as the first quantum anharmonic results for a molecule that size. *Naphthalene (18 atoms),
  anthracene/phenanthrene (24), pyrene (26) are inside this envelope.*
- **Dral et al. (2025)**, JPCL — already bibliography item 5. ANI-1ccx-gelu: the activation-function
  fix that removes the "wrinkly PES" pathology, which is what otherwise destroys numerically
  differentiated 3rd/4th derivatives. *Prerequisite for any MLP→QFF→VPT2 chain.*
- **Tang, Doktor, Jaganathan, Palotás, Oomens, Hornekær & Hammer (2025)**, arXiv:2504.11898, JCP
  163, 044304. MLIP-accelerated anharmonic IR of **cationic pyrene** and superhydrogenated
  derivatives vs gas-phase IRMPD action spectroscopy. *A named experimental standard for a cation at
  exactly the size this proposal targets.*

**The gap this leaves — and it is a real one:**

> Every anharmonic PAH spectrum in the astrophysical literature rests on **B3LYP** (scaled harmonic,
> or VPT2 on a DFT surface). Nobody has anchored PAH band families to a **measured** coupled-cluster
> rung, published the four-term error budget, and then used the result in a **pre-registered,
> fail-closed identification**. That is a defensible master's contribution, and it is Project 12's
> exit.

---

## 5. Recommended architecture (option E)

### 5.1 The inversion, in one line

> Old: novel representation → own CCSD(T) labels → MD+FFT envelope → H₂O.
> New: **borrowed representation → own gold anchor → quantum nuclear motion → named PAHs, fail-closed.**

Precision is carried by the **theory ladder** and the **nuclear-motion method**, not by the network.
This is not a retreat: [Overarching_Goal §6](Overarching_Goal.md) already states that "the ML
pipeline is a means" and that reinventing a wheel to avoid a comparison is forbidden.

### 5.2 Pipeline

```
      target list (pre-registered)            frozen observational product
              │                                          │
              ▼                                          ▼
 [1] theory ladder            [3] MLIP            [5] GVPT2 / VCI      [7] cascade +
   canonical CCSD(T)  ──▶      fine-tuned   ──▶     QFF from MLP   ──▶  fail-closed ID
   ↕ measured error         foundation model      + dipole surface        (agent, 07)
   DLPNO/LNO-CCSD(T)              ▲                      ▲
   = the GOLD RUNG                │                      │
              │              [2] Δ-ML / transfer    [6] DMS: field vs
              └──────────────────▶  correction          equivariant-tensor
                                     ▲                   (scoped comparison)
                                [4] active-learning proposal engine
```

**[1] Gold rung, measured not asserted.** Canonical CCSD(T)/cc-pVTZ (and CBS(T,Q) where affordable)
on benzene and naphthalene; DLPNO-CCSD(T)-F12 and/or LNO-CCSD(T) at Tight/TightPNO settings on the
same systems; publish the local-vs-canonical error **per band family and per charge state**. Only
after that measurement may the local method be used on larger rings. This replaces the current
§5.1 CBS(T,Q) audit and does the same job with the same claim ladder — but it also **unlocks the
ladder** instead of only certifying a wording.

**[2] Δ-ML / transfer learning carries the precision.** Learn \(E_{\text{gold}}-E_{\text{cheap}}\)
(or fine-tune from the cheap level) on a few hundred aromatic geometries. This is the mechanism the
literature says needs ~100–200 high-level points, not 5,000. It is also a textbook supervised-ML
deliverable, which makes it a clean Module 04.

**[3] Production PES = fine-tuned equivariant foundation model.** MACE-OFF / MACE-MP / AIMNet2 class,
retrained/fine-tuned on the Δ-corrected set, with smooth (GELU-class) activations so that third and
fourth derivatives are clean. Requirements: analytic or well-converged Hessians, size-extensivity by
construction, exact rotational equivariance.

**[4] Generative proposal + active learning.** A generative model over aromatic geometries and
substitution/charge patterns proposes configurations where the MLIP is uncertain; those — and only
those — are sent for gold labels. Preserves the existing rule that every proposed geometry is
re-labelled before it is trusted.

**[5] Nuclear motion = GVPT2 from an MLP-derived QFF.** Primary method. Escalation ladder,
pre-registered now:

1. GVPT2 with explicit resonance treatment (Fermi/Darling–Dennison).
2. Selected VCI for the congested 6–9 μm fingerprint region if GVPT2 resonance handling breaks.
3. If neither converges for a species, that species is reported **UNRESOLVED**, not quietly replaced
   by an MD envelope.

MLMD + dipole ACF is retained **only** as a temperature-dependence diagnostic appendix, per
Project 11 §3.1. Scaled-harmonic B3LYP (the PAHdb status quo) is retained as the **baseline that
must be beaten**, which is what makes the result interpretable.

**[6] Dipole moment surface — and this is where the voxel work is salvaged.** Intensities, not
positions, are the weak link in PAH IR: charge-state intensity swaps are the diagnostic astronomers
actually use. The plan's own round-2 issue 11 finding is that for a promolecular reference split,
\(\boldsymbol\mu=-\int\mathbf r\,\Delta\rho_\theta\,dV\) **exactly**. So the deformation-density
field is a natural DMS. Proposal: keep the FNO-NCA field model, but **reassign it from the energy to
the dipole surface**, and run the existing pre-registered comparison there:

| Leg | What it is |
|---|---|
| **DMS-field** | \(\boldsymbol\mu=-\int\mathbf r\,\Delta\rho_\theta\,dV\) from the FNO-NCA deformation-density field |
| **DMS-tensor** | Equivariant atom-centred dipole model (DetaNet/MACE-class vector head) |
| **DMS-charge** | Environment-dependent partial charges (the cheap classical baseline) |

Same discipline as Distilled §7.1: frozen splits, ≥3 seeds, tuning parity, pre-registered effect
size, "inconclusive" publishable. If DMS-field loses, it is dropped and the production DMS is the
winner — the spectra still ship. **The field idea survives as a scoped, falsifiable, on-topic
experiment instead of as a 600-hour critical-path dependency.**

**[7] Fail-closed identification.** The agent from Module 07 orchestrates
QFF → GVPT2 → intensities → cascade/excitation model → match metric, and refuses to emit a verdict
without citing measured value against the pre-registered threshold. Allowed verdicts, frozen before
the observational product is touched: **Supported / Rejected / Unidentified-degenerate**.

### 5.3 Why this is defensible at Module 09

The examiner's question is "what did you add that Mai 2025 and Chen 2026 did not?" The answer is one
sentence and it is true:

> They ran anharmonic nuclear motion on a **DFT** surface with an **unquantified** electronic-structure
> error, and matched spectra without a fail-closed rule. This work anchors the surface to a
> **measured** coupled-cluster rung, publishes the four-term error budget, and states in advance what
> would count as a failed identification.

---

## 6. Molecule and charge ladder, with a stop rule

Each rung is scored. The project stops at the first rung where measured error exceeds the §1 band
tolerance — that is what "any size" is allowed to mean.

| Rung | Species | Charge | Experimental standard | Why this rung |
|---|---|---|---|---|
| **0** | Benzene | neutral | NIST gas-phase FTIR (one frozen dataset) | Canonical CCSD(T) reachable ⇒ validates the whole chain against the best data available. **Guaranteed deliverable / fallback (option F).** |
| **1** | Naphthalene | neutral + cation | Gas-phase / He-tagged IR; PAHdb matrix + frozen shift model | First real transfer step. Cation = first open-shell gold-rung measurement. |
| **2** | Anthracene **and** phenanthrene | neutral + cation | PAHdb + gas-phase where available | **Isomer pair on purpose**: supplies Project 12 §3.4's "two species fit" degeneracy case for free. |
| **3** | Pyrene | neutral + cation | IRMPD action spectroscopy (Tang et al. 2025) | Named modern experimental standard at exactly this size. |
| **—** | Negative control (wrong charge or wrong size) | — | — | Required by Project 12 §7. Must fail. |

Band families scored: 3.3 μm C–H stretch, 6–9 μm C–C / C–H in-plane, 11–12 μm C–H out-of-plane.
Naming them in advance is what makes §3.2 pre-registration possible.

---

## 7. Module remap 02–09

Constraints preserved: datasets distinct across modules; no synthetic/AI-generated datasets; DOI
before the source sentence; Module 08 integrates ≥3 prior modules and **nothing debuts in 08**.

| Module | New content | Rubric fit |
|---|---|---|
| **02** Foundations | EDA on **NASA Ames PAHdb** (public, citable): quantify that the theoretical library is scaled-harmonic B3LYP, and where it disagrees with the experimental library. Motivates the entire thesis with the object Module 08 will later confront. | A — public dataset, clean EDA, better motivation than QM9 |
| **03** Statistics | Hypothesis tests on the **theory-ladder benchmark**: DLPNO/LNO settings vs canonical CCSD(T), by band family and charge state; and harmonic-scaling-factor residual structure. | A/C — and it now sits on the critical path *pointing at the deliverable*, instead of on egg-box sweeps |
| **04** Applied ML | The **Δ-ML / transfer-learning correction** \(E_{\text{gold}}-E_{\text{cheap}}\) on aromatic geometries. Small-data, cross-validated, error bars. Published with DOI. | A — this is the component that carries chemical precision |
| **05** Deep Learning | **Production MLIP**: fine-tuned equivariant foundation model on the Δ-corrected set. Controlled ablation = architecture/activation comparison and derivative quality (harmonic + cubic force constants vs reference). Optionally hosts the field-vs-GNN leg. | A — equivariant GNN is squarely deep learning; the ablation satisfies the "one changed variable" rule |
| **06** Generative AI | **Active-learning proposal engine**: generative model over aromatic structures / charge states / displaced geometries, selecting configurations by MLIP uncertainty for gold labelling. Genuinely load-bearing, not a bridge project. | B/D — generative, and every proposal is re-labelled before use |
| **07** Agentic | **Fail-closed spectroscopy and identification agent**: orchestrates QFF → GVPT2 → DMS intensities → cascade → match metric; refuses a verdict without measured-value-vs-threshold. | B/C — this *is* Project 12 §3.4 |
| **08** Synthesis | Integrates 04 + 05 + 06 + 07. Delivers: anharmonic band families and relative intensities for the §6 ladder, four-term error budget, and a **pre-registered fail-closed identification** against one frozen JWST/PAHdb product. Industry frame: astrochemical spectral identification with a reliability gate. | A — ≥3 prior modules, nothing debuts here |
| **09** Defense | Defend R3, the ladder rungs that fired, and the scope sentence. Two pre-written answers: "isn't this just fine-tuning MACE?" and "didn't Mai 2025 already do this?" | — |

**Compliance note.** PAHdb (02) and the B3LYP baseline are public reference data used for
motivation and baselining, formally outside the pipeline's train/val/test sets — the same boundary
[Capstone_Mapping §5.3](Capstone_Mapping.md#53-compliance-boundary-new-clarifies-4s-dataset-table)
already draws for QM9. Pipeline labels remain coupled-cluster.

---

## 8. Gates (replacing the Phase 0–5 table)

| Phase | Goal | Hard Go/No-Go |
|---|---|---|
| **G0 — Environment & baselines** | Reproduce the status quo before improving it | ORCA/MRCC (or equivalent) + MLIP + QFF/VPT2 toolchain installed; **scaled-harmonic B3LYP benzene and naphthalene spectra reproduced against PAHdb** to within the published scatter. If the baseline cannot be reproduced, nothing downstream is interpretable. |
| **G1 — Gold rung measured** | The word "gold" earns its place | Canonical CCSD(T) vs DLPNO/LNO on benzene + naphthalene: relative energies ≤ 1.0 kcal/mol RMSE, directional derivatives ≤ 1.0 meV/Å, **harmonic mode shifts ≤ 5 cm⁻¹**, reported per band family and per charge state. Fail ⇒ tighten PNO settings, then fall back to canonical-only rungs (option F). |
| **G2 — Δ-ML / PES quality** | The surface is worth differentiating four times | Held-out energy ≤ 1 kcal/mol, forces ≤ 1 meV/Å vs gold; **harmonic frequencies within 5 cm⁻¹** of the gold Hessian; **cubic force constants stable under step-size refinement** (the Dral 2025 smoothness test). Fail ⇒ more active-learning rounds, then smaller molecule ladder. |
| **G3 — Nuclear motion** | Anharmonicity is real, not fitted | GVPT2 on rung 0 (benzene) within **10 cm⁻¹ of gas-phase FTIR** for all scored band families; resonance treatment documented; VCI escalation declared where used. |
| **G4 — Intensities** | Relative intensities are earned, not assumed | \(d\boldsymbol\mu/dQ\) relative error < 5 % vs reference APT/DMS on held-out modes; CO₂-style forbidden-mode residual retained as a symmetry check; **DMS bake-off (field vs tensor vs charge) pre-registered and reported before it is used**. Fail ⇒ intensity claims withdrawn, positions still ship. |
| **G5 — Transfer** | The ladder actually climbs | Per rung: band centers inside §1 tolerance vs the named standard. First rung that fails is the stop rung and is reported as the measured limit. |
| **G6 — Identification** | Fail-closed, once | Pre-registration document **dated before** the observational product is opened: target list, band families, match metric, PASS/FAIL/UNIDENTIFIED rule, isomer-degeneracy rule. Negative control must fail. Test data touched once. |

The existing gate-unit discipline, error decomposition (§8 items 1–13) and the "engine artifact is a
bug with a ceiling, only label noise may loosen a gate" rule transfer unchanged.

---

## 9. What is preserved, and what dies

**Preserved — and this is the repository's most valuable asset.** The governance system is better
than most PhD projects and is entirely method-agnostic: pre-registration of comparisons, frozen
split files with hashes, ≥3 seeds with error bars, tuning parity, declared effect sizes,
"inconclusive is a publishable outcome", claim ladders, shrink ladders, fail-closed reporting,
four-way error decomposition, DOI-before-claim, measured-not-guessed budgets, re-estimation from
measured velocity. **The restructure changes what is governed, not how.**

Also preserved: the field/FNO-NCA idea (reassigned to the DMS, §5.2 item 6), the leave-one-mode-out
transfer test, the MACE comparator, the Module 07 fail-closed agent concept, and the entire
Overarching_Goal §3.A "labels are coupled cluster" rule.

**Dies:**

| Deleted | Why |
|---|---|
| Phase 0a voxel engine, egg-box sweeps, Hockney–Eastwood validation, grid-convergence campaign | The production PES is no longer a voxel grid. ~160–240 h released. |
| \(E=\mathcal E[\rho,R]\) as the **energy** functional; the local \(\varepsilon_\theta\) | Distilled §2.1 already concedes this is the functional form the literature found insufficient (Teller; M-OFDFT). Keeping it as the energy model is the single largest risk-to-value ratio in the plan. |
| The ≥2,000 H₂O / ≥5,000 benzene volumetric CCSD(T) campaigns | Transfer learning needs hundreds of points. This also removes the plan's largest compute and HPC dependency. |
| MD + dipole-ACF FFT **as the deliverable** | Published at 216-carbon scale in 2025. Demoted to diagnostic appendix. |
| H₂O / D₂O / CO₂ as flagship molecules | Demoted to unit tests of the toolchain. D₂O isotope check stays as a cheap sanity test. |
| Projects 10 / 11 / 12 as separate post-master's projects | Their load-bearing content moves into Modules 03–08. What remains post-master's is the genuine career-scale residue: line lists, universal PAH Hamiltonians, full JWST cube analysis. |

---

## 10. Effort arithmetic (the honest version)

| Removed | h | Added | h |
|---|---:|---|---:|
| Phase 0a engine + sweeps | 160–240 | Theory-ladder benchmark (G1) | 60–100 |
| P1 field PES | 120–160 | Δ-ML / transfer learning (04) | 60–100 |
| Module 05 voxel benzene campaign work | 60–100 | MLIP fine-tune + derivative QA (05) | 100–140 |
| Module 03 egg-box statistics | 40–80 | QFF → GVPT2 / VCI pipeline | 80–120 |
| Volumetric campaign setup/review | 60–120 | DMS + intensity gates (incl. bake-off) | 60–100 |
| | | Cascade model + pre-registration + ID (07/08) | 80–120 |
| **Total removed** | **440–700** | **Total added** | **440–680** |

**The restructure is roughly effort-neutral in human hours. It is not a shortcut.** What changes is
where those hours land: on Project 12's exit instead of on Project 2's. Two genuine savings do
appear, and both are in elapsed time rather than human hours:

- **Compute drops by orders of magnitude.** Hundreds of gold-rung single points and a workstation
  DLPNO job, instead of ~7,000 canonical CCSD(T) geometries with volumetric density export. The
  HPC-allocation dependency, which Round 3 flagged as an open blocker, largely disappears.
- **The critical path shortens.** Modules 02, 03 and 04 no longer wait on a bespoke engine passing
  a 0.1 meV/Å artifact ceiling; they wait on installing established software and running benchmarks.

The 10 h/week and re-estimation-after-20-hours rules from §8.6 apply unchanged, and this table is a
prior, not a measurement.

---

## 11. Risk register with pre-registered escalations

| # | Risk | Escalation, declared now |
|---|---|---|
| 1 | Local coupled cluster (DLPNO/LNO) error on delocalized aromatic π exceeds the budget (Sylvetsky & Martin 2020) | TightPNO → LNO-CCSD(T)/tight → Δ-ML on the local-vs-canonical difference → canonical-only ladder (stop at rung 1) |
| 2 | GVPT2 resonances break in the 6–9 μm congested region | Selected VCI for that family → report only 3.3 μm and 11–12 μm families → species marked UNRESOLVED. **Never** substitute more classical MD. |
| 3 | DMS quality dominates intensity error | Intensity claims withdrawn; band positions still ship (positions and intensities are gated separately, on purpose) |
| 4 | Open-shell cations: spin contamination, larger local-CC error | Measure it at G1 as a separate row; if it fails, cations become outlook and the ladder is neutrals-only |
| 5 | MLIP third/fourth derivatives too noisy for a QFF | Smooth-activation retrain (Dral 2025) → analytic-Hessian architecture (NewtonNet-class) → smaller molecules |
| 6 | Foundation-model licence / provenance unsuitable for a thesis artifact | Check before Module 05; fall back to training the same architecture from scratch on the Δ-corrected set |
| 7 | "This is just fine-tuning someone's model" | Answered by §5.3; the contribution is the anchor, the budget and the fail-closed rule — and it is stated in the abstract, not defended reactively |
| 8 | Rubric: modules 04/05/06 dataset eligibility | Unchanged from Round 3 issue 3 — **written mentor approval before generating expensive data.** Still open, still blocking. |
| 9 | Identification returns "unidentified/degenerate" for every species | Pre-authorised as a successful outcome, exactly as "inconclusive" already is for the §2 comparison |

---

## 12. Decisions required before this can be adopted

1. **ACCEPTED 2026-08-23.** Adopt R3 as the prime directive's definition of "chemically precise";
   rewrite [Overarching_Goal.md](Overarching_Goal.md) §1–§3 accordingly. R1 stays forbidden.
2. **ACCEPTED 2026-08-23.** The field/voxel model is demoted from production PES to the scoped
   dipole-moment-surface comparison (§5.2 item 6).
3. **ACCEPTED 2026-08-23.** Projects 10–12 fold into Modules 03–08. **There is no post-master's
   horizon if R3 is reached inside the master's** — the horizon files become provenance, not a
   roadmap. Whatever R3 does *not* reach (line lists, universal PAH Hamiltonian, full JWST cube
   analysis) is named as limitation in Module 08, not as a queued project.
4. **T.b.d.** Gold-rung software stack (ORCA DLPNO vs MRCC LNO vs both) — determines G1.
   Recommendation in §15.
5. **T.b.d.** MLIP family, and its licence. Recommendation in §16.
6. **Freeze the §6 ladder and the §1 tolerance numbers before any campaign.** Commit the molecule /
   charge ladder, the band families, the cm⁻¹ and intensity tolerances, and the stop rule to git
   with a date, *before* the first gold-rung job runs. Deciding afterwards means picking the number
   the result happened to achieve, which converts a test into a description.
7. **Reduced, not closed** (Round 3 issue 3, dataset eligibility). See §14.

---

## 13. Bibliography entries (merged into Relevant_Scientific_Papers.md on 2026-08-23)

Two of the papers that drove this pivot were **already in the bibliography** under summaries that
understated or misdescribed them; those entries were corrected rather than duplicated.

| # | Entry | Action taken |
|---|---|---|
| 4 | Käser, Boittier, Upadhyay & Meuwly (2021), *JCTC* — arXiv:2103.05491 | **Attribution corrected.** Was filed as "Nandi et al." with a paraphrased title; the stored PDF and `Papers/README.md` both say Käser. Found because the sweep re-added it as a duplicate. |
| 5 | Dral et al. (2025), ANI-1ccx-gelu | **Promoted** from remark to gate G2 (cubic-force-constant step-size stability) plus declared fallback. |
| 12 | Mai, Wang, Pan, Schörghuber, Kovács, Carrete & Madsen (2025), *MNRAS* 541, 3073 — arXiv:2503.05120 | **Re-weighted.** Was "brought MLMD to aromatic systems"; is in fact 1,704 PAHdb species up to 216 C — i.e. the pre-pivot Module 08 exit, already published at scale. |
| 14 | *ACS Omega* (2025), ML-corrected DFT scaling factors | **Re-weighted** as the status-quo baseline G0 must reproduce and R3 must beat (5 cm⁻¹ MAE). |
| 15 | Wang (2026), *A&A* — arXiv:2602.12531 | **Corrected.** The old summary ("identify the isotopic makeup of deep space PAHs") was wrong; it is size/charge *classification*, not named-species identification. |
| 16, 17, 19 | FNO, V2Rho-FNO, Growing NCA | **Re-scoped** to the dipole-surface leg only. |
| 18 | NASA Ames PAHdb (Boersma et al. 2014) | **Promoted** — now the Module 02 dataset, the status-quo source, and an identification-target candidate. |
| 26 | Kotaru, Qu, Nandi, Houston & Bowman (2026) — arXiv:2604.20040 | Added — QFF + VPT2 from an MLP; the enabler. |
| 27 | Käser & Meuwly (2021), *PCCP* — arXiv:2109.08407 | Added — formic acid; VPT2 on a transfer-learned PES, and where it strains. |
| 28 | Käser & Meuwly (2023), *JCP* 158 — arXiv:2303.11685 | Added — ~100 high-level points suffice for transfer learning. |
| 29 | Kumar, Neese & Valeev (2020), *JCP* 153, 094105 — arXiv:2008.03237 | Added — DLPNO-CCSD(T)-F12, 550+ atoms, open-shell, one workstation. |
| 30 | Sylvetsky, Banerjee, Alonso & Martin (2020), *JCTC* 16, 3641 — arXiv:2001.08641 | Added — the delocalized-π caveat that makes G1 a measurement. |
| 31 | Tang, Doktor, Jaganathan, Palotás, Oomens, Hornekær & Hammer (2025), *JCP* 163, 044304 — arXiv:2504.11898 | Added — cationic pyrene vs IRMPD; named standard for rung 3. |
| 32 | Ji, Zhang, Zou, Jiang, Jiang, Luo & Hu (2025), DetaNet — arXiv:2510.04227 | Added — archetype of the DMS-tensor leg. |
| 33 | Chen, Li & Li (2026), *A&A* — arXiv:2607.20015 | Added — the cascade-emission template, at B3LYP; names the gap R3 fills. |
| 34 | Batatia, Kovács, Simm, Ortner & Csányi (2022), *NeurIPS* | Added — MACE architecture (code MIT). |
| 35 | Kovács et al. (2023, rev. 2025), MACE-OFF — arXiv:2312.15211 | Added — foundation-model line; **neutral organics only**, so a fallback rather than the primary. ASL weights. |
| 36 | Batatia et al. (2026), MACE-POLAR-1 — arXiv:2602.19411 | Added — polarisable electrostatic foundation model on OMol25 with variable charge **and spin**; the DMS-tensor leg, and a genuine competitor to the voxel DMS rather than a strawman. |

PDFs for items 21–24 and 26–36 were retrieved into [`Papers/`](../../../Papers/) on 2026-08-23 (15 files, all
open-access arXiv, all signature-verified). Only item 25 (Teller 1962, pre-arXiv *RMP*) remains
without a local copy.

---

## 14. Dataset eligibility after the pivot (answers decision 7)

**Verbatim rubric rule**, identical in Modules 03, 04, 05 and 06: the dataset must "be publicly
available and appropriate for academic use", must "not be synthetic or AI-generated", and must not
repeat a dataset used in an earlier project. The *Accepted Sources* list (Kaggle, UCI, Data.gov,
FiveThirtyEight, open government portals) is illustrative and contains no "or your own data"
carve-out. Module 05 additionally states the rule inside its scored rubric row, not only in the
instructions.

**What changes under the pivot:**

| Module | Dataset | Eligibility risk |
|---|---|---|
| 02 | NASA Ames PAHdb (public, versioned, citable) | **None.** Third-party, published, academic. |
| 03 | Theory-ladder benchmark table (canonical vs local CC, per band family / charge state) | Self-computed — risk remains, but the table is *hours* of workstation time, not months. |
| 04 | Δ-ML correction set \(E_{\text{gold}}-E_{\text{cheap}}\) | Self-computed — risk remains. This *is* the contribution; it cannot come from Kaggle. |
| 05 | MLIP fine-tuning set | Self-computed — risk remains. |
| 06 | Aromatic structure corpus for the proposal engine | Can be sourced from PAHdb / public structure sets ⇒ **low**. |

**So the answer to "is it still necessary?" is yes — but the question it blocks has shrunk by two
orders of magnitude.** Round 3 called it blocking because a wrong answer would have wasted a
multi-thousand-geometry CCSD(T) campaign with volumetric density export and an HPC allocation.
Under the pivot the same wrong answer costs a few days of a single workstation. The mitigation
therefore inverts: **generate a small pilot set first, publish it with a Zenodo DOI, and ask the
mentor with the artifact in hand** rather than asking about a hypothesis.

**Fallback if the mentor rules self-computed data ineligible.** PAHdb is itself a tabular, public,
DOI-bearing dataset with thousands of rows (species × band position × intensity × charge × size) and
natural categorical grouping variables. It can carry Module 03 (scaling-factor residual statistics)
and Module 04 (predict anharmonic shift or band properties from structure) on its own. The
coupled-cluster work then lives in the **ungraded** research workstream and enters the degree
through Module 08, whose rubric has no Accepted-Sources clause at all. The old plan had no such
safety net; this one does.

**New risk this creates — disjointness.** Under the pivot, 03, 04 and 05 all draw on the same
aromatic campaign, which the rubrics forbid. They must be made genuinely distinct in molecules,
format and purpose before any of them is written — e.g. 03 on the benchmark molecules, 04 on a
disjoint Δ-ML set, 05 on the production fine-tuning set. Assign this in the Module remap, not later.

---

## 15. Recommendation for decision 4 — gold-rung software stack

**Proposal: ORCA as the single production stack, MRCC as the arbiter for one measurement.**
Not "both" in the sense of duplicated work — two distinct, non-overlapping roles.

**Primary — ORCA 6.1.x** (verified 2026-08-23: freely available for academic use; native
**Linux, Windows and macOS** builds; current release 6.1.1, Dec 2025; canonical coupled cluster and
DLPNO-CCSD(T) both in-package).

- One code, one basis convention, one convergence setting for **both** the canonical rung and the
  local rung. The G1 measurement is canonical-minus-local; running the two halves in different
  programs would inject a code-difference into the number the whole claim ladder rests on.
- Closed- **and** open-shell DLPNO ⇒ the cation rungs of §6 stay in the same stack.
- Properties (dipoles, polar tensors) come from the same run ⇒ the DMS reference labels inherit the
  same convention as the energies.
- **Side effect worth naming: the Windows build removes the Linux/WSL2 week-1 task** that
  [Capstone_Mapping §8.2](Capstone_Mapping.md#82-effort-estimates-and-owners) budgets at 20–40 hours,
  and that Distilled §5.1 flagged as "a cheap check with an expensive surprise".

**Arbiter — MRCC (LNO-CCSD(T), tight settings)**, academic-free, used **only** at G1 and only on the
hardest cases (benzene and naphthalene, neutral and cation). Justification is not preference but
measurement: Sylvetsky, Banerjee, Alonso & Martin (2020) showed that for delocalized /
static-correlation-prone π systems DLPNO-CCSD(T) needs TightPNO, and that **LNO-CCSD(T)/tight is
what reproduces canonical to sub-kcal**. Aromatics are precisely that regime. If ORCA-TightPNO and
MRCC-LNO agree inside the G1 budget, ORCA carries the whole campaign and MRCC is never run again.
If they disagree, that disagreement *is* error term (B) of the four-term budget and must be
published, not resolved by preference.

**Rejected:** Molpro / PNO-LCCSD(T) — commercial licence, no capability the two above lack for this
problem.

**Demoted:** PySCF. Under the pivot there is no volumetric density export, so PySCF is no longer on
the critical path. Keep it as an optional cross-check on one geometry; do not build the plan on it.

**Must be measured at G0, never assumed** (same discipline as Distilled §5.1 "code path is a
decision procedure"): whether the pinned ORCA version returns **analytic** DLPNO-CCSD(T) gradients
for the closed- and open-shell cases actually used. If it does, the Δ-ML set is force-rich and small.
If it does not, forces come from finite differences, the set becomes energy-heavy, and the Δ-ML
design in Module 04 must be re-sized *before* the campaign — not discovered during it. Fill this in
as a smoke-test table with numbers, exactly as §5.1 Step 1 already prescribes.

---

## 16. Recommendation for decision 5 — MLIP family and licence

**Proposal: the MACE family, three named checkpoints, chosen at G0 by a measured bake-off rather
than by argument.**

**Code licence: MIT** (`mace-torch`, verified 2026-08-23). float64 training is supported, which is
not cosmetic here — a QFF needs numerically stable third and fourth derivatives, and float32 is where
that quietly fails. Fine-tuning a foundation model is a first-class CLI workflow
(`--foundation_model`, `--E0s="estimated"`), so [3] in §5.2 is configuration, not new code.

| Role | Checkpoint | Why | Licence |
|---|---|---|---|
| **PES, primary** | **MACE-OMOL-0** (OMol25, ωB97M-VV10, "large") | Carries explicit **charge / spin embedding** and is released for molecules **and cations**. It is the only mainstream checkpoint that natively covers the neutral/cation pairs the §6 ladder requires — and cations are the astrophysically diagnostic case. | **ASL** (academic, non-commercial) |
| **PES, fallback** | MACE-OFF23 / OFF24 (SPICE, ωB97M-D3) | Mature, heavily benchmarked on neutral organic chemistry. **Neutral-only ⇒ fails the cation rungs**, so it is a fallback for rung 0–1 only. | ASL |
| **DMS-tensor leg** | **PolarMACE / MACE-Polar** (electrostatics foundation models, OMol25) | Turns the §5.2 DMS bake-off into field vs a **strong off-the-shelf** tensor baseline vs charges, instead of field vs something hand-built. A win against a weak baseline proves nothing. | ASL |
| **MIT-only escape hatch** | MACE architecture trained from scratch on the Δ-corrected set | If ASL ever becomes a problem, the *code* is MIT; only the weights are restricted. Costs more data, changes nothing structurally. | MIT |

**Licence consequence, stated once so it cannot surprise anyone at submission:** ASL is
academic/non-commercial. That is fine for a thesis and for publication, but the derived weights may
not be redistributed commercially. The **dataset** produced in Modules 03/04/05 is yours and is what
gets the Zenodo DOI; the model licence is disclosed in the artifact README and in the Module 05
report.

**The one thing that must be measured before this is locked (G2 gate):** MACE is smooth and
autograd-differentiable, but the QFF needs derivatives *above* second order. G2 must explicitly test
**step-size stability of the cubic force constants**, not just Hessian accuracy — this is the Dral
et al. (2025) "wrinkly PES" lesson, and it is the failure mode that would silently poison every VPT2
number downstream. Pre-registered fallback if MACE fails that test: the **ANI-1ccx-gelu / MLatom**
route, which was engineered specifically to fix it, accepting the loss of equivariance and charge
embedding.

**Coupled, separate decision — nuclear-motion software.** Two candidates, both to be run on H₂O and
benzene at G0 against known references before one is picked: **MLatom** (Dral; ships VPT2 workflows
and the ANI-1ccx-gelu models) and the **Kotaru/Qu/Nandi/Houston/Bowman (2026)** QFF + VPT2 release.
Do not carry both past G0.

**Why a bake-off rather than a decision now.** Both choices are nearly free to reverse today and
expensive to reverse after G2. One measured day at G0 — same molecule, same labels, same metric —
buys a defensible answer; three paragraphs of reasoning buys an opinion. That is the same rule the
plan already applies to the §6.1 anchoring fork.
