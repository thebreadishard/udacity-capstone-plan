# Distilled Final Project Plan & Quality Checks

> **PRE-PIVOT — REWRITE IN PROGRESS (2026-08-23).**
> The prime directive changed on 2026-08-23: see [Overarching_Goal.md](Overarching_Goal.md) section 1 (**R3**)
> and [Restructure_Proposal_2026-08-23_Project12_in_Module08.md](Restructure_Proposal_2026-08-23_Project12_in_Module08.md).
>
> | Section | Status |
> |---|---|
> | §1 evolution log, §2 research question, §2.1 prior art, §2.2 demoted DMS question | ✅ **rewritten** |
> | §3 what the project IS, §4 what it is NOT | ✅ **rewritten** |
> | §5 data pipeline (§5.0 ladder → §5.8 derivative gate) | ✅ **rewritten** |
> | §6 architecture, training, nuclear motion (§6.1 → §6.7) | ✅ **rewritten** |
> | §7 roadmap G0–G6, §7.1 pre-registration | ✅ **rewritten** |
> | §8 QA protocol, §9 precision claims | ⛔ pre-pivot |
>
> **Sections marked ⛔ describe the voxel-era plan and must not be quoted as current.** They still
> assume a voxel field PES, own canonical-CCSD(T) volumetric campaigns, and classical MD + dipole-ACF
> FFT as the deliverable. The pre-pivot text stays in git history by design; §1 item 19 is where the
> change is recorded.

**Source material:** This document is distilled from the full, multi-round conversations in [gemini_chat_2.md](../../../AI_Chats/gemini_chat_2.md) and [grok_chat_2.md](../../../AI_Chats/grok_chat_2.md), cross-checked against the earlier exploratory conversations [gemini_chat_1.md](../../../AI_Chats/gemini_chat_1.md) and [grok_chat_1.md](../../../AI_Chats/grok_chat_1.md). It reconstructs the plan as it stood after the "strict professor" critique loop: the plan was drafted with Gemini, stress-tested by Grok, revised, re-submitted to Grok, and — after a final, very harsh 23-point external review (pasted into both chats) — reworked one last time. **Gemini's final response to that 23-point review is the most advanced, self-consistent version of the plan and is treated here as the definitive baseline.** Grok's conversation ends one step earlier (agreeing the 23 points must be addressed, without yet seeing the reworked plan), so where the two diverge, the later Gemini revision supersedes the earlier Grok-approved version.

---

## 1. Evolution of the Plan (why it looks the way it does)

1. **Origin idea** ([gemini_chat_1.md](../../../AI_Chats/gemini_chat_1.md)): predict IR spectra of large aromatic molecules using an AI-discovered cellular-automaton update rule, applicable to any molecule, trained/validated/tested only on chemically precise (non-DFT) data. First framed as a Graph Cellular Automaton (GNCA) reading out a Hessian.
2. **Grid over graph** ([gemini_chat_2.md](../../../AI_Chats/gemini_chat_2.md)): switched to a continuous 3D spatial grid (voxels), because free-space photon propagation and continuous electron density don't map naturally onto a graph.
3. **First full plan** submitted to Grok as "strict professor": **rejected**. Fatal flaw — the architecture only propagated the *electron density* over a *static* nuclear grid, which produces electronic (UV/Vis) dynamics, not vibrational IR dynamics.
4. **Revision 1 — dynamic nuclei**: added explicit classical point-nuclei with Velocity-Verlet integration, coupled to the electron-density grid (Grid-to-Particle / Ehrenfest-like coupling). Grok gave **conditional green light**, then tightened it further into a formal energy/force-consistency requirement (Born-Oppenheimer/adiabatic choice, Gaussian nuclear densities, analytic Hellmann-Feynman-consistent forces). Grok then gave **unconditional green light** — followed immediately by a literature check confirming the combination is novel (closest prior art: V2Rho-FNO, which only maps geometry→density, with none of the MD/force/spectral machinery).
5. **The harsh 23-point external review** (pasted into both chats verbatim): identified that the "conditional green light" plan still had a fundamental gap — a network that only learns density does **not** automatically yield a conservative force field/PES — plus ~22 other concrete methodological weaknesses (spectral resolution too short, egg-box not eliminated, periodic Poisson boundary artifacts, too little training data, spectral loss risks reward-hacking the spectrum instead of the physics, no baseline comparison, naphthalene zero-shot oversold, etc.).
6. **Final revision** (end of [gemini_chat_2.md](../../../AI_Chats/gemini_chat_2.md)): a ground-up restructuring that resolves all three non-negotiables the reviewer (and both AI "professors") converged on. Sections 1–9 below reconstruct that baseline.
7. **Architecture lock (2026-08-22):** professor-review blocking issue 2 required an *implementable* \(E=\mathcal{E}[\rho,R]\) (not a slogan), deletion of leftover complex-density / EM channels, and a split of jobs between the fixed Hockney–Eastwood solver and the learned FNO. That lock is written into §3, §4, and §6 below. The Gemini baseline remains the source for everything else.
8. **Data-generation method (2026-08-22):** professor-review blocking issue 3 required replacing “exact CCSD(T) density/forces/Hessian via PySCF” with a recipe (which 1-RDM, which force, how many Hessians), a measured 10-geometry cost pilot as a Phase 0 exit, a shrink ladder if the campaign does not fit local hardware, and a Phase 1 force gate that sits above the measured noise floor. That lock is written into §5.1 and §7 below.
9. **Goal lock (2026-08-22):** professor-review blocking issue 4 required the prime directive to stop promising “chemically precise spectral lines” / “sub-wavenumber” as a this-thesis claim. [Overarching_Goal.md](Overarching_Goal.md) now splits **labels** (CCSD(T)/cc-pVTZ per §5.1) from **spectra** (§9 band envelopes). Horizon PAH work is post-master’s Projects 10–12, not Module 08.
10. **Baseline lock (2026-08-22):** professor-review blocking issue 6 required the GNN competitor to live on the critical path, not in Module 08. Mapping [§4.2 Workstream G1](Capstone_Mapping.md#42-workstream-g1--equivariant-atomistic-pes-resolves-professor-review-blocking-issue-6) trains MACE from scratch on the **same** P1/05 split manifests. Module 08 **assembles**. D₂O (Phase 3) is a **sanity check**, not the flagship proof that the field representation learned physics. The §2 test is leave-one-mode-out transfer vs G1.
11. **Density-representation lock (2026-08-22):** [round-2](../../01_voxel-field-pes/GoalGathering/Professor_Review_2026-08-22_Round2.md) blocking issue 7 showed the grid cannot carry an all-electron density at \(\Delta x\approx0.2\,\text{Å}\), and issue 10 showed \(\Phi\) was a nuclear-identity bypass channel in \(\varepsilon_\theta\). §3, §5.1, §6.1, §6.2, §6.3, §7 and §8 below now specify a **reference split**: an analytic promolecular density carries the cusps, only the smooth deformation density \(\Delta\rho_\theta\) touches the voxel grid, and \(\varepsilon_\theta\) sees density-derived local scalars only.
12. **Gate lock (2026-08-22):** round-2 blocking issue 8 showed the Phase 0 tolerances (quoted in Hartree) and the Phase 1 acceptance gate (quoted in meV/Å) were mutually inconsistent by two orders of magnitude, and that feeding engine artifacts into the Phase 1 “noise floor” made that gate **self-loosening**. §5.1 and §7 now derive every artifact tolerance *from* the acceptance gate, in force units, and admit only irreducible **label** scatter into the noise floor.
13. **Observable and invariance lock (2026-08-22):** round-2 blocking issues 11 and 12 — the IR observable (\(\boldsymbol{\mu}\), \(d\boldsymbol{\mu}/d\mathbf{R}\)) was never trained or validated and the CO₂ gate had no number; and no gate covered the fact that a voxel grid is neither translation- nor rotation-invariant. §6.4, §7 and §8 now carry dipole gates before any production MD, a numeric CO₂ forbidden-mode gate, and an explicit invariance budget.
14. **Prior-art and pre-registration lock (2026-08-22):** round-2 blocking issue 9 — the novelty check missed the machine-learned orbital-free DFT lineage that this architecture belongs to; §2.1 now positions against it and pre-registers a fallback if the local \(\varepsilon_\theta\) stalls. Round-2 blocking issue 13 — the §2 comparison was falsifiable in wording only; §7.1 now fixes splits, seeds, tuning parity, effect size and confounds **before** any leg trains.
15. **Representation-identifiability lock (2026-08-23):** round-3 blocking issue 1 showed that a density-supervised field model versus an \(E/F\)-only MACE does not isolate representation; it compares unequal label information. §2, §6.3, §7 and §7.1 now make the equal-label **Field-EF vs MACE-EF** result primary, add a controlled **Field-EFρ vs Field-EF** density-supervision ablation, and reserve the full \(E/F/H/\rho\) model for the operational spectroscopy result rather than the representation-only claim.
16. **Same-surface label lock (2026-08-23):** round-3 blocking issue 2 showed that CCSD(T) energies paired with CCSD force targets do not define one conservative PES. §5.1 now forbids that mixture, requires a measured directional-derivative consistency pilot, uses full finite-difference CCSD(T) gradients for H₂O, and permits seeded CCSD(T) directional derivatives for benzene only when complete gradients fail the measured budget. §6.3 and §7 evaluate every model against derivatives of the same CCSD(T) energy surface.
17. **Dipole-supervision lock (2026-08-23):** round-3 blocking issue 4 showed that “add \(L_\mu\) if the dipole gate fails” was post-hoc model selection and contradicted the frozen training loss. §5.1 and §6.3 now require analytic dipoles from the pinned density target for every density-labelled configuration and enable \(L_\mu\) from the first production run. Dipole derivatives have fixed evaluation-only counts; there is no \(L_{d\mu}\) rescue. Band positions remain emergent from the static PES, while relative intensities are explicitly described as coming from a statically supervised dipole surface and frozen-weight dynamics.
18. **Label-accuracy audit lock (2026-08-23):** round-3 blocking issue 5 showed that naming CCSD(T)/cc-pVTZ does not demonstrate chemical precision. §5.1 now freezes an HPC-backed CCSD(T)/CBS(T,Q) reference audit over counted H₂O, CO₂ and benzene geometries, with energy, derivative and curvature thresholds plus a fail-closed claim ladder. “Chemically precise” is conditional on this audit; an unaffordable or failed audit leaves only the method-defined phrase “CCSD(T)/cc-pVTZ-level.”
19. **R3 pivot (2026-08-23):** a literature sweep run while scoping Module 08 found that **this plan's own deliverable had already been overtaken**. Mai et al. (2025) — bibliography item **12**, sitting in this repository since goal-gathering under a summary that understated it — computed anharmonic IR spectra by machine-learning MD for **1,704 PAHdb species up to 216 carbon atoms**. Chen, Li & Li (2026) had built the astrophysical cascade-emission machinery [Project 12](Horizon/12_Astrophysical_PAH_Identification.md) §3.1 specified. At the same time the walls those horizon projects existed to describe had partly dissolved: Kumar, Neese & Valeev (2020) put CBS-quality **open-shell** DLPNO-CCSD(T)-F12 on 550-atom systems within reach of one workstation; Käser & Meuwly showed transfer learning to CCSD(T) needs on the order of **100** high-level points, not thousands; Kotaru et al. (2026) released software that runs **VPT2 from a machine-learned potential** for a 21-atom molecule in about a minute.

    Three consequences, structural rather than incremental. (a) Delivering classical-MD band envelopes for H₂O and benzene in 2028 would not have been a contribution. (b) The budget that made that the ceiling was being spent on making a voxel grid behave — roughly two thirds of the fixed 840-hour baseline, none of it producing a spectrum. (c) What is still genuinely missing in the literature is not another anharmonic PAH spectrum but a **measured coupled-cluster anchor** underneath one, with a published error budget and a fail-closed identification rule.

    The plan was therefore **inverted: borrow the representation, own the theory anchor and the nuclear motion.** [Overarching_Goal.md](Overarching_Goal.md) was rewritten to **R3**; Projects 10–12 were absorbed into Modules 03–08; the FNO-NCA field was reassigned from the **energy** to the **dipole surface**, where \(\boldsymbol\mu=-\int\mathbf r\,\Delta\rho\,dV\) holds exactly and the object is small enough to be falsified cheaply. The full argument, six weighed alternatives, the literature evidence and the effort arithmetic are in [Restructure_Proposal_2026-08-23_Project12_in_Module08.md](Restructure_Proposal_2026-08-23_Project12_in_Module08.md).

    Recorded here, not hidden: locks 7, 8, 10, 11 and 12 above were engineering achievements on an object this plan no longer builds as its PES. They were not wasted — locks 11 and 12 (the exact dipole identity, the grid artifact budget) transfer intact to the dipole-surface leg, and the discipline the other locks produced is what made the pivot decidable rather than a matter of taste. **A plan that cannot survive its own literature check was never a plan.**

---

## 2. Central Research Question (R3 formulation, 2026-08-23)

> "Does anchoring a transferable machine-learned potential to a **measured** coupled-cluster rung — rather than to DFT — produce anharmonic IR band positions and relative intensities for named PAH sizes and charge states that are accurate enough, with a published error budget, to support a **fail-closed** identification against a frozen astrophysical product?"

This replaces the previous formulation ("under equal \(E/F\) supervision, does a continuous 3D neural field transfer better to unseen vibrational modes than an atomistic equivariant GNN"). That question was well-posed and pre-registered, but it was a question about **representations**, and answering it — including answering it "inconclusive", which its own outcome table admitted was likely — would have produced no spectrum of anyone's interest. It survives, demoted and re-aimed, as the §2.2 dipole-surface comparison.

**The question decomposes along the four-term error budget**, so that a failure is attributable rather than merely disappointing:

| Sub-question | Measures | Budget term | Where it is answered |
|---|---|---|---|
| **Q1 — Is the cheap gold real?** How large is the local-CC-vs-canonical-CCSD(T) error on aromatics, **per band family and per charge state**? | electronic structure | **(B)** | Module 03, gate G1 |
| **Q2 — Does the anchor buy accuracy?** Do gold-anchored anharmonic band centers and relative intensities beat the scaled-harmonic / DFT-VPT2 status quo against **named** experimental standards? | PES + nuclear motion | **(A)**, **(C)** | Modules 04/05, gates G2–G3, G5 |
| **Q3 — Is the budget small enough to decide anything?** Under a pre-registered match rule and excitation model, does identification return **Supported** or **Rejected** rather than always **Unidentified-degenerate**? | everything + environment | **(D)** | Modules 07/08, gate G6 |

**Core hypothesis.** The dominant error in current large-PAH IR predictions is electronic-structure error, not nuclear-motion error — and it is invisible because nobody quantifies it. If that is right, replacing a DFT surface with a gold-anchored one improves band positions and, more sharply, **relative intensities**, which depend on the dipole surface and are where DFT is least controlled.

**The hypothesis is falsifiable in a way that matters.** Tang et al. (2025) already report that harmonic-plus-empirical-scaling reproduces the experimental band profile of pristine and partially superhydrogenated pyrene cations, and that anharmonic treatment becomes *mandatory* only in the fully superhydrogenated case. If gate G1 finds the local-vs-canonical error is small **and** gate G5 finds gold-anchoring does not move band centers outside the scaled-harmonic scatter, then the honest result is: *for these band families, at these sizes, the electronic-structure rung is not the limiting term.* That is a publishable, useful negative result, it is pre-registered here, and it must not be rescued by quietly switching to a metric that flatters the method.

**What is explicitly not the question.** Whether a novel architecture is better than MACE. Whether voxels beat graphs. Whether more MD helps. The ML model is an interpolator between gold-rung points, and §6 of this plan is now about how to build a *reliable* one, not a *new* one.

### 2.1 Prior art this thesis must be positioned against (rewritten 2026-08-23)

The pre-pivot §2.1 positioned this work against machine-learned orbital-free DFT (Snyder 2012, Brockherde 2017, M-OFDFT 2024, Teller 1962). **That positioning is no longer the important one** — it applies only to the §2.2 dipole-surface leg, and is retained there. Under R3 the neighbours are different and closer.

**The deliverable's closest prior art — own it in the first paragraph of the thesis.**

- **Mai et al. (2025), item 26/12.** MLMD anharmonic IR for 1,704 PAHdb species up to C₂₁₆, temperature-resolved, linear scaling. *If this thesis produces classical-MD band envelopes for PAHs, it has reproduced this at smaller scale.* Its labels are DFT and its nuclear motion is classical; both are where R3 differs.
- **Chen, Li & Li (2026), item 33.** VPT2 anharmonic properties plus optimised microcanonical sampling producing environment-dependent IR **cascade emission** for neutral, cationic and anionic cyanonaphthalenes. This is the excitation machinery [Project 12](Horizon/12_Astrophysical_PAH_Identification.md) §3.1 demanded — already built, at **B3LYP/N07D**.
- **Kovács et al. (2020), Meng et al. (2023), Wang (2026)** — items 8, 10, 15. ML *on* PAH spectra: fingerprint regression, fragment attribution, and size/charge classification at F1 = 0.963. These predict or classify spectra without a PES. They are the branch this thesis explicitly does **not** join, and [Project 10](Horizon/10_Size_Extensive_Aromatic_PES.md) §5 already forbids treating spectral matching as a substitute for a potential.
- **The NASA Ames PAHdb theoretical library** (item 18) and **ML-corrected scaling factors** (item 14, ~5 cm⁻¹ MAE). The status quo, and the baseline gate G0 must reproduce before anything downstream is interpretable.

**What is therefore *not* novel here:** anharmonic IR spectra of large PAHs (2025); VPT2 on a machine-learned potential (2021, and at 21 atoms in 2026); transfer learning a PES to CCSD(T) quality (2021–2023); IR cascade emission models for astrophysical PAHs (2026); local coupled cluster on large aromatics (2020); ML classification of PAH spectra (2020–2026).

**What is left, stated plainly.** Every anharmonic PAH spectrum in the astrophysical literature rests on DFT with an **unquantified** electronic-structure error. The residual contribution is the *combination* of (a) a **measured** gold rung — canonical CCSD(T) versus local CCSD(T), reported per band family and per charge state, rather than a local method assumed to be gold; (b) a Δ-learned / transfer-learned MLIP carrying that anchor to sizes where canonical CC cannot go; (c) the **four-term error budget** published next to every cm⁻¹ claim; and (d) a **pre-registered fail-closed identification** with a negative control and an isomer-degeneracy rule. Remove (a) and (c) and what remains is a re-run of Mai 2025 with extra steps. That is the honest framing, and it is still a thesis.

**The transferability risk this literature makes explicit.** Two, and they are different in kind from the pre-pivot one.

1. **The gold may not be gold.** Sylvetsky, Banerjee, Alonso & Martin (2020, item 30) show that for delocalized, static-correlation-prone π systems DLPNO-CCSD(T) — and even DLPNO-CCSD(T1) — carry significant error unless TightPNO cutoffs are used, with LNO-CCSD(T)/tight required for sub-kcal agreement. Aromatics are exactly that regime. This is why G1 is a **measurement with an arbiter code**, not a citation.
2. **The anchor may not survive differentiation four times.** R3 needs third and fourth derivatives of the ML surface. Dral et al. (2025, item 5) document the "wrinkly PES" pathology that destroys numerically differentiated high-order derivatives; Käser et al. (item 4) show that an MP2-quality surface produces VPT2 outliers up to 150 cm⁻¹ even when the fit looks good. A surface can pass an energy and force gate and still be useless for a quartic force field.

**Pre-registered escalation ladders (declare now, not after gate G5).** Which rung fired is reported in every downstream claim.

*Electronic structure (term B):*

1. Canonical CCSD(T) where computable — benzene, naphthalene. The reference, not a rung to be skipped.
2. DLPNO-CCSD(T) at TightPNO, error measured against rung 1 per band family and charge state.
3. LNO-CCSD(T)/tight as arbiter where rung 2 misses the G1 budget.
4. Δ-ML on the local-vs-canonical difference itself, validated on a held-out **medium** molecule.
5. Stop the molecule ladder at the last size where rung 1 or 2 holds, and report that size as the measured limit. **Stopping is a result, not a failure.**

*Nuclear motion (term C):*

1. GVPT2 with explicit Fermi / Darling–Dennison resonance treatment. The default.
2. Selected VCI for the congested 6–9 μm fingerprint region where resonance handling breaks.
3. Report only the band families that converged; mark the species **UNRESOLVED** for the rest.
4. **Running longer classical trajectories is not on this ladder.** MD+FFT is a temperature diagnostic. Substituting it for a failed VCI is the single most tempting way to lose this thesis, and it is forbidden here so that it cannot be rediscovered as a good idea in month fourteen.

A failure at rung 1 of either ladder is a result **about that rung**, and must be reported as such — not as evidence that gold-anchored anharmonic PAH IR is impossible.

### 2.2 Demoted question: what representation should carry the dipole surface?

The pre-pivot central question survives here, scoped to the object where the field model is still the natural choice and cheap to falsify. Because a promolecular reference has identically zero dipole, \(\boldsymbol\mu=-\int\mathbf r\,\Delta\rho_\theta\,dV\) **exactly** (round-2 issue 11), so a deformation-density field is a dipole moment surface without further machinery.

Three legs, pre-registered under the §7.1 rules — frozen splits, ≥3 seeds, tuning parity, declared effect size, "inconclusive" publishable:

| Leg | Representation |
|---|---|
| **DMS-field** | FNO-NCA deformation-density field, \(\boldsymbol\mu=-\int\mathbf r\,\Delta\rho_\theta\,dV\) |
| **DMS-tensor** | Equivariant atom-centred vector head (MACE-POLAR-1 class, item 36) |
| **DMS-charge** | Environment-dependent partial charges — the cheap classical baseline |

This is a fair fight, which is the point of demoting it rather than deleting it: MACE-POLAR-1 is itself a learned electron-density model with variable charge and spin and interpretable spin-resolved densities, so a win against it would mean something and a loss is informative. **It is never on the critical path.** If DMS-field loses, it is dropped and the spectra ship on the winner. The machine-learned orbital-free DFT lineage (items 21–25) is the correct prior art *for this leg*, and Teller's theorem and the M-OFDFT non-locality lesson still apply to any claim that a local functional of the density suffices.

---

## 3. What the Project IS

- **A gold-anchored anharmonic IR prediction pipeline for named PAHs.** Seven components, in dependency order: (1) a **measured** electronic-structure ladder; (2) a Δ-learned / transfer-learned correction carrying that anchor; (3) a fine-tuned equivariant MLIP as the production surface; (4) an active-learning proposal engine feeding (1); (5) a quartic force field and **GVPT2** nuclear motion; (6) a gated dipole moment surface for intensities; (7) an excitation/cascade model and a **fail-closed** identification layer.
- **A project whose precision lives in the theory and the nuclear motion, not in the network.** The MLIP is an interpolator between gold-rung points. Every architectural choice is made for *reliability of high-order derivatives*, not for novelty.
- **A reproduce-before-improve project.** Gate G0 reproduces the published scaled-harmonic B3LYP status quo for benzene and naphthalene against PAHdb, to within the published scatter, **before** anything is improved. A number that cannot be compared to the status quo cannot be interpreted, and a pipeline that cannot reproduce a known answer has not been debugged.
- **A project that gates positions and intensities separately, on purpose.** Band centers come from the PES through the QFF; relative intensities come from the dipole moment surface. A DMS failure withdraws intensity claims and leaves positions standing. Fusing the two gates would make one bad component silently sink a good one.
- **A molecule ladder with a stop rule, not a size promise.** Benzene → naphthalene (neutral + cation) → anthracene **and** phenanthrene (the deliberate isomer pair, which supplies the degeneracy case the identification rule needs) → pyrene (neutral + cation). Climbing stops at the first rung where measured error exceeds the §9 band tolerance, and that rung is published as the measured limit.
- **A project with an experimental standard named per claim.** Gas-phase FTIR where it exists; IRMPD action spectroscopy for cations; PAHdb matrix data only with a stated, frozen matrix-shift model. Never a mixture of corrected and uncorrected numbers in one table.
- **Strictly coupled-cluster labels.** Canonical CCSD(T) where computable; local CCSD(T) beyond that, **with its measured error against canonical published per band family and per charge state**. Energies and supervised derivatives describe the same surface. DFT appears only as the cheap half of a Δ-learning pair, as the reproduced baseline, and in public reference libraries used for motivation — never as a pipeline label.
- **No spectral training, and now it matters more.** No spectrum, peak position or intensity is ever a training target or a hyperparameter-selection criterion. PAHdb, NIST, IRMPD and JWST products are **blind checks**. With identification as the endpoint, training on the thing you intend to identify would not be a methodological wobble; it would be the whole result, fabricated.
- **A demoted, falsifiable representation experiment (§2.2).** The FNO-NCA field survives as one of three dipole-surface legs, pre-registered, never on the critical path.
- **Rigorously phased**, with hard numerical Go/No-Go gates G0–G6 (§7), for a self-paced master's beginning 2026-09-01 at 10 human hours/week. Compute is local-first and now genuinely modest: hundreds of gold-rung single points and a workstation local-CC job, not thousands of volumetric CCSD(T) geometries. Copilot and compute may run outside the human-attention window; their output still requires human validation.
- **A project that treats "inconclusive" and "stopped at rung 2" as publishable outcomes.** Both are pre-registered here (§2, §7.1) precisely so that neither can be quietly converted into a more flattering claim later.

---

## 4. What the Project is explicitly NOT

- **NOT an architecture-novelty project — and this is a retraction, not a rephrasing.** The pre-pivot plan's first entry here read *"NOT a Graph Neural Network: no discrete atom-nodes, bond types, or hard-coded per-element sub-networks… one single universal update rule must work for any element purely from local field values, the way physical law itself doesn't have separate equations per bond type."* **That principle is withdrawn.** The production surface is now a fine-tuned equivariant message-passing GNN with atom-centred features, chosen deliberately.

    The withdrawal is not opportunism, and the argument should be given in full in the Module 09 defense rather than defended reactively. The aesthetic claim — physical law has no per-bond equations — was true about *physics* and false about *interpolators*. Nothing in this plan ever claimed \(\varepsilon_\theta\) was a universal functional; §2.1 conceded before the pivot that it was "an interpolator over a narrow manifold." Once that is admitted, the argument for voxels collapses: an interpolator should be judged on transfer, cost, exact symmetry and derivative quality, and on all four an equivariant GNN wins by construction. It is exactly rotation-equivariant, where the voxel model needed a gate and an error budget for the same property. It scales with atom count, where the voxel model scales with box volume — fatal at PAH size. And R3 needs *third and fourth* derivatives, where a discretized field is at its weakest.

    A reviewer will ask whether this was principle or convenience. The answer on record: the principle was never load-bearing, the measurement (round-2 issue 12: \(3\times10^{-5}\) vs \(1.7\times10^{3}\) meV/Å rotation residual) showed what the discretization cost, and the literature check showed the destination was already reachable without it.
- **NOT Kohn–Sham DFT labels.** No B3LYP/PBE/M06-2X energies, forces or curvatures in the pipeline's train/validation/test sets — the systematic errors on dispersion and aromatic π-delocalization are precisely what R3 exists to quantify. **Three permitted appearances, all outside the label set:** the cheap half of a Δ-learning pair; the reproduced status-quo baseline (G0); and public reference libraries (PAHdb, QM9-class) used for motivation and EDA. Note the old "NOT DFT" slogan is retired for a second reason now: the selected foundation checkpoints are *pre-trained* on hybrid DFT (ωB97M-VV10 / ωB97M-D3). Fine-tuning from DFT-pre-trained weights toward coupled-cluster labels is exactly what Δ-learning is, and pretending otherwise to a Module 09 examiner is a free kill.
- **NOT trained on any spectral quantity.** No spectral loss, no peak-position loss, no Wasserstein-on-FTIR, no PAHdb matching as an objective, and **no spectral quantity used for model selection or early stopping**. This was already the rule; with identification as the endpoint it becomes the rule that protects the entire result.
- **NOT delivering classical MD + dipole-ACF FFT.** That is R2, it was published at C₂₁₆ scale in 2025 (§2.1), and here it is a **temperature-dependence diagnostic in an appendix**. Escalating a failed GVPT2 or VCI by running longer trajectories is forbidden (§2.1 nuclear-motion ladder rung 4).
- **NOT claiming rovibrational line-list precision.** \(I_{i\to f}\propto|\langle f|\mu|i\rangle|^2\) catalogues in the ExoMol/POKAZATEL sense are out of scope. The claim is anharmonic band **families** with relative integrated intensities and a four-term budget.
- **NOT claiming "any size".** The ladder stops where measured error exceeds the band tolerance, and the stop rung is published. A universal PAH Hamiltonian is not this thesis; it is a career.
- **NOT an astronomical survey project.** One frozen observational product, chosen and cited before it is opened, with a pre-registered target list. No shopping for a survey that matches, no JWST data as training input, no "consistent with PAHs" without a species list.
- **NOT treating the identification result as guaranteed.** **Unidentified-degenerate** is a pre-authorised outcome and is the *expected* one for several rungs. A negative control that must fail is part of the deliverable.
- **NOT a quantum-computing project.** Investigated in [grok_chat_1.md](../../../AI_Chats/grok_chat_1.md) and rejected as a dead end **in the current NISQ era** — noise, qubit counts and achievable circuit depth make it strictly worse than classical hardware for every relevant sub-task. A "not now", not a permanent objection.
- **NOT treating HPC as unmeasured production capacity.** The pivot removes most of the HPC dependency: local coupled cluster on aromatics is a workstation job (§2.1). Canonical CCSD(T) on naphthalene may still need an allocation, and if so it requires its own measured pilot, written allocation confirmation and a schedule update before submission — otherwise the electronic-structure ladder stops at the last affordable rung.
- **NOT skipping baseline comparisons — and the baselines have changed.** Required: (1) **scaled-harmonic B3LYP / PAHdb**, the status quo, reproduced at G0 and beaten or not at G5; (2) **DFT-based VPT2**, the like-for-like nuclear-motion comparison that isolates the value of the gold anchor; (3) **harmonic** frequencies from the gold rung itself, to show what anharmonicity actually buys. Without all three, an improvement cannot be attributed to the anchor rather than to the method.
- **NOT allowed to skip the "was it worth it" question.** Tang et al. (2025) found scaled harmonic sufficient for pristine pyrene cations. If the gold anchor does not move band centers outside the status-quo scatter for a given band family, that must be reported as the finding, not buried under the families where it did.

---

## 5. Data Pipeline (coupled-cluster labels; DFT only as the Δ-learning baseline)

### 5.0 The molecule ladder and its blind standards

Every rung is scored. Climbing **stops** at the first rung where measured error exceeds the §9 band
tolerance, and that rung is published as the measured limit.

| Rung | Molecule(s) | Charge | Electronic-structure work | Blind validation standard |
|---|---|---|---|---|
| **0** | Benzene | neutral | Canonical CCSD(T) **and** local CC (the gate-G1 pair); Δ-ML set; equilibrium Hessian; DMS labels | One frozen NIST gas-phase FTIR dataset, resolution fixed in writing |
| **1** | Naphthalene | neutral **+ cation** | Canonical CCSD(T) if the cost pilot permits (G1 pair); local CC in production | Gas-phase / He-tagged IR where it exists; else PAHdb **with** the frozen matrix-shift model |
| **2** | Anthracene **and** phenanthrene | neutral + cation | Local CC, carrying the rung-0/1 measured error | PAHdb. The isomer pair is deliberate: it supplies the degeneracy case §3.C needs |
| **3** | Pyrene | neutral + cation | Local CC | IRMPD action spectroscopy (item 31) |
| **—** | Negative control: one wrong size or wrong charge state | — | Identical treatment | Must **fail** the identification, or the fail-closed rule is untested |

**Toolchain unit tests, not flagship science.** H₂O, D₂O and CO₂ are retained because they are cheap,
have exactly known answers, and break the pipeline loudly when it is wrong: H₂O for canonical
CCSD(T) and the same-surface derivative check, D₂O for the mass-only isotope shift with zero
retraining, CO₂ for the symmetry-forbidden intensity residual. They are **regression tests**. No R3
claim rests on them, and no chapter is built from them.

**PAHdb and JWST products are blind checks.** They are never a training input, never a
hyperparameter-selection criterion, and never an early-stopping signal. With identification as the
endpoint, this is not hygiene — it is the rule that protects the entire result.

### 5.1 Three data products, and only three

The pre-pivot plan had one campaign per molecule producing everything. That coupled the cheap
products to the expensive ones. Under R3 the products have different sizes, different theory levels
and different consumers, so they are specified separately.

| | Product | Size | Consumer | May it ever train a model? |
|---|---|---|---|---|
| **P-A** | **Gold-rung benchmark**: canonical CCSD(T) vs local CC on the same geometries | Counted, frozen before results are seen | Gate **G1**; error term **(B)** | **No.** Audit only. |
| **P-B** | **Δ-ML / transfer-learning set**: cheap-level and coupled-cluster energies (plus derivatives where the code returns them) on the same geometries | Order **10²** per molecule class, grown by active learning | The production MLIP | Yes — this is the training set |
| **P-C** | **Evaluation-only sets**: dipoles and dipole derivatives, held-out complete gradients, equilibrium Hessians | Counted per §5.3 | Gates G2–G4; the DMS bake-off | **No.** Touched once, at the end. |

**Sizing is an output of the pilot, not an input to the plan.** The pre-pivot numbers — ≥2,000 H₂O
and ≥5,000 benzene configurations with volumetric density export — are withdrawn, not reduced. The
literature that replaces them is specific: Käser & Meuwly reach CCSD(T) quality by transfer learning
from on the order of **100** high-level points, and Qu et al. built a Δ-ML acetylacetone PES that
matched the LCCSD(T) barrier to 0.05 kcal/mol from **430** training energies. The design target is
therefore **order 10², not order 10³**, with active learning (§6) deciding where the next point goes
rather than a pre-declared grid.

If the pilot says even that does not fit, take the §5.5 shrink ladder. Do not keep a number as a
scored promise.

**Split discipline, unchanged from the pre-pivot plan because it was right.** Split by
configuration, never by random points drawn from near-identical trajectories. One frozen split file
per campaign, committed and hash-referenced in every gate report. Leave-one-mode-out validation.
Rigid rotations and translations augment **inputs** only; they are not extra quantum-chemistry jobs
and do not count toward any budget.

### 5.2 Scientific defaults (locked now)

| Quantity | Default | Why |
|---|---|---|
| **Reference energy** | **Canonical CCSD(T)/cc-pVTZ**, frozen-core, one geometry convention (Å vs Bohr) everywhere | The meterstick. Computed only where computable — that is the point of measuring rather than assuming. |
| **Production energy** | **DLPNO-CCSD(T)-F12 at TightPNO** (ORCA), with **LNO-CCSD(T)/tight** (MRCC) as the G1 arbiter on the hardest cases | Sylvetsky & Martin (item 30): for delocalized π, looser PNO settings carry real error. Aromatics are that regime. |
| **Cheap baseline** | One pinned DFT level, declared per molecule class, used **only** as the lower half of the Δ-learning pair | This is the one permitted DFT contact in the label path, and it is named rather than smuggled. The MLIP's pre-training level (ωB97M-VV10 for MACE-OMOL-0) is disclosed alongside it. |
| **Energy derivatives** | **Same-surface rule.** Analytic gradients if the pinned code returns and validates them; otherwise central finite differences **of the same energy expression**. Never a CCSD force against a CCSD(T) energy. | Method mismatch is systematic bias, not label noise, and a conservative model cannot fit both. Unchanged from the pre-pivot plan; it was one of its best rules. |
| **Hessians** | **Reference Hessians only at the G1 audit geometries**, to score the ≤5 cm⁻¹ mode-shift gate. Production Hessians, cubic and semidiagonal quartic constants come from the **MLIP**, not from coupled cluster. | This is the structural change R3 forces. A quartic force field for a 24-atom PAH has tens of thousands of constants; computing them ab initio is the thing the ML surface exists to avoid. |
| **Density \(\rho\)** | **Only where the DMS-field leg is trained** (rungs 0–1), from a pinned 1-RDM recipe, exported as the deformation density \(\Delta\rho=\rho_{\mathrm{QM}}-\rho_{\mathrm{ref}}\). Default relaxed CCSD 1-RDM; the manifest says **relaxed** or **unrelaxed** and never "exact CCSD(T) density". | Density labels are no longer a pipeline-wide requirement — they serve one demoted comparison (§2.2). If the DMS-field leg is dropped, this product disappears entirely and nothing downstream notices. |
| **Dipole \(\boldsymbol\mu\)** | **Every P-B configuration.** Analytic AO-basis expectation from the pinned 1-RDM plus the nuclear term, three Cartesian components, one frozen origin convention. | Intensities are half the R3 deliverable. A grid integral is a model prediction and a diagnostic, never the reference label. |
| **Dipole derivatives** | **Evaluation only, never a training loss.** Complete atomic polar tensor at equilibrium for the unit-test molecules; \(d\boldsymbol\mu/dQ_k\) over the scored normal modes for each ladder rung. | These gate the relative-intensity claim. Training on them would train on the gate. |

### 5.3 Code path is a decision procedure, not a wish

**Step 0 — pin.** One ORCA version; one basis (`cc-pVTZ`, plus the F12 auxiliary sets); one SCF/CC
convergence; one PNO setting (**TightPNO**) with the arbiter setting named separately; frozen-core
convention; one geometry convention (Å vs Bohr) everywhere. For the DMS-field leg only: the export
grid and the frozen per-element atomic reference fits, each accepted at
\(\int\lvert\rho^{\mathrm{fit}}_Z-\rho^{\mathrm{atom}}_Z\rvert\,dV/Z<10^{-3}\).

**Platform note — this changed, and in the cheap direction.** The pre-pivot plan budgeted a week-1
Linux/WSL2 task because PySCF publishes no native Windows wheels. ORCA ships **native Windows, Linux
and macOS** builds and is free for academic use, so that task disappears from the critical path.
PySCF survives as an optional cross-check on one geometry. Stand the toolchain up on day one
regardless: a cheap check with an expensive surprise.

**Step 1 — smoke test, per molecule *and per charge state*.** Record pass/fail with numbers, never
"via ORCA", for: canonical CCSD(T) energy; DLPNO-CCSD(T)-F12 energy; **whether an analytic gradient
exists and validates** at each level; numerical Hessian; analytic AO dipole. Open-shell rows are
**separate rows** — a closed-shell pass says nothing about a cation, and the cations are the
astrophysically diagnostic species.

**Step 2 — 10-geometry cost pilot, per rung.** Measure wall time and peak RAM for canonical and
local coupled cluster *separately*, plus the cost of one complete finite-difference gradient. The
only budget that counts:

\[
T_{\text{rung}} \approx N_{\text{geom}}\times \bar t_{\text{geom}},\qquad\text{computed per rung, canonical and local separately.}
\]

No folklore, no borrowed benchmarks. The pilot decides three things **in writing before any
production run**: (i) how far up the §5.0 ladder canonical CCSD(T) actually reaches; (ii) which
derivative rung §5.4 selects; (iii) whether the §5.5 shrink ladder fires.

**Manifest columns.** Every row gets: `config_id`, `molecule`, `charge`, `multiplicity`,
`ladder_rung`, `theory_energy`, `pno_setting`, `basis`, `frozen_core`, `error_vs_canonical`
(null where canonical was not computed, and **never silently null**), `derivative_kind`
(`analytic_gradient|fd_full_gradient|fd_directional`), `derivative_theory`, `fd_step_bohr`,
`direction_seed`, `direction_vector`, `derivative_uncertainty`, `dipole_theory`, `dipole_origin`,
`dipole_x_e_bohr`, `dipole_y_e_bohr`, `dipole_z_e_bohr`, `rdm_relaxed|unrelaxed` (DMS-field leg
only), `orca_version`, `wall_s`, `max_rss_gb`. If the applicable fields are blank, it is not a
dataset.

### 5.4 Dipole and dipole-derivative protocol

Intensities are half of R3, so \(\boldsymbol\mu\) and \(d\boldsymbol\mu/d\mathbf{R}\) are first-class
labels rather than an afterthought. Reference dipoles are evaluated **analytically** from the pinned
1-RDM in the AO basis; any grid or model integral is a prediction to be scored, never the reference.
Every P-B configuration receives \(\boldsymbol\mu_{\mathrm{QM}}\); only the training partition enters
the dipole loss.

Dipole derivatives are frozen **evaluation sets**, generated by central differences of those analytic
dipoles, and **never** enter training or hyperparameter selection:

- **Unit-test molecules (H₂O, CO₂):** complete \(3\times9\) atomic polar tensor at equilibrium, with
  \(\pm h\) and \(\pm h/2\) step-convergence checks — 36 displaced dipole calculations each.
- **Each scored ladder rung:** \(d\boldsymbol\mu/dQ_k\) over the normal modes belonging to the three
  scored band families (3.3 μm, 6–9 μm, 11–12 μm), at \(\pm h\), with \(\pm h/2\) convergence added
  for a fixed subset of mode ranks chosen from the harmonic frequencies **before** any dipole is
  inspected. Counts are fixed per rung in the observable manifest at freeze time.
- **Cations get their own set.** Neutral-to-cation intensity swaps in the 6–9 μm and 11–12 μm
  families are the diagnostic astronomers actually use; inheriting neutral derivatives would erase
  exactly the signal being claimed.
- **D₂O:** no new electronic calculations. Isotopic substitution changes masses, not the electronic
  dipole surface at fixed geometry.

The accepted \(h\), mode vectors, phase convention and derivative uncertainty are stored in the
observable manifest. Derivative uncertainty must sit below one third of the applicable acceptance
threshold.

### 5.5 The gold-rung audit — error term (B), in two parts

"Coupled cluster" is a declared method, not a demonstration of accuracy. Term (B) is measured, and it
has **two** components that the pre-pivot plan conflated into one:

| | Component | Measured how | Where it is affordable |
|---|---|---|---|
| **B1** | **Local vs canonical.** DLPNO/LNO-CCSD(T) against canonical CCSD(T), same basis, same convergence | Paired calculations on the frozen audit geometries | Every rung where canonical CC is computable — this is what the ladder's reach is *defined* by |
| **B2** | **Basis-set convergence.** Canonical CCSD(T)/cc-pVTZ against CCSD(T)/CBS(T,Q) | \(E_{\mathrm{ref}}=E_{\mathrm{HF},Q}+\dfrac{4^3E_{\mathrm{corr},Q}-3^3E_{\mathrm{corr},T}}{4^3-3^3}\) | **Unit-test molecules and benzene only.** Not affordable at naphthalene and above, and that is a stated limitation, not a gap to be quietly ignored |

Freeze the audit set by `config_id`, coordinates, normal-mode vectors, thermal seeds and hashes
**before** any reference result is seen. Audit results are audit-only: they never enter training,
hyperparameter selection or split construction. Mode selection uses the production-level equilibrium
Hessian; for each named band family take the mode nearest the pre-registered region centre, ties to
the lower index. **Do not replace a difficult geometry after seeing its error.**

**Pre-registered acceptance thresholds**, applied to B1 and B2 separately:

| Quantity | Pass condition |
|---|---|
| Relative energy, after subtracting each molecule's equilibrium energy | RMSE \(\le1.0\,\mathrm{kcal/mol}\) and maximum absolute error \(\le2.0\,\mathrm{kcal/mol}\) |
| Directional derivative | RMSE \(\le1.0\,\mathrm{meV/Å}\) |
| Audited harmonic modes | absolute frequency shift \(\le5\,\mathrm{cm}^{-1}\) |

The mode-shift threshold is the one that matters most: it is **half** the R3 band tolerance, so an
electronic-structure error at the gate consumes half the budget before nuclear motion has been
attempted at all.

Report **per molecule, per charge state and per band family**. A pooled pass may not hide a cation
failure or a fingerprint-region failure — that is the whole reason the error is resolved this finely.

**Claim ladder — what the result licenses:**

1. All gates pass for a molecule and charge state ⇒ *"local-CCSD(T) labels for [species] are accurate
   to [measured value] against canonical CCSD(T) over the audited domain, and canonical/cc-pVTZ is
   converged to [measured value] against CBS(T,Q) where that was computable."*
2. Only the energy gate passes ⇒ accuracy is claimed for relative energies only; derivatives and
   curvatures are reported by method level and measured discrepancy.
3. The energy gate fails ⇒ the wording drops to *"local-CCSD(T)-level labels with a measured
   discrepancy of [value]"*. Nothing is called chemically accurate.
4. The audit could not be completed for a rung ⇒ that rung's precision claim is **unverified**, and
   the molecule ladder stops there. **Missing reference data never counts as a pass.**

**Compute gate.** Before committing to a rung, run one job at that rung's most expensive setting —
canonical CCSD(T) on the largest species, or the QZ reference where B2 applies — and record wall
time, peak RAM, scratch and core count. Extrapolate the full job count and confirm in writing that it
fits. If it does not, reduce nothing silently: take the §5.6 shrink ladder or claim-ladder rung 4.



### 5.6 Same-surface derivative decision

The scalar energy and every supervised derivative must describe the **same** surface. Never minimize
an energy loss against CCSD(T) while minimizing a force loss against analytic CCSD forces. A
conservative model cannot in general satisfy both, and the mismatch must not be relabelled as
irreducible noise. **This rule is inherited unchanged from the pre-pivot plan.** It was one of its
best, and Δ-learning makes it sharper rather than looser: a Δ-model learns
\(E_{\mathrm{gold}}-E_{\mathrm{cheap}}\), so *both* halves of that difference must be
self-consistent, and a derivative taken at one level against an energy at the other corrupts the
correction itself.

**Pilot measurement.** At each pilot geometry, draw at least three normalized directions \(\mathbf v\)
from committed seeds and compute

\[
D_{\mathbf v}E \approx \frac{E(\mathbf R+h\mathbf v)-E(\mathbf R-h\mathbf v)}{2h},
\]

at \(h\) and \(h/2\); their difference is the numerical-uncertainty estimate. Report
\(D_{\mathbf v}E_{\mathrm{CCSD(T)}}+\mathbf F_{\mathrm{CCSD}}\cdot\mathbf v\) as a **method-consistency
diagnostic only** — that discrepancy is systematic bias and never enters the label noise floor.

**Decision ladder — stop at the first rung that fits the measured calendar:**

1. Analytic gradients at the production level, if the pinned implementation returns **and validates**
   them. Validate separately for closed and open shell.
2. Complete central finite-difference gradients, where the pilot cost permits.
3. Seeded random directional derivatives, three per configuration, floor one. Every model in a
   comparison receives the **identical** directions and projected-derivative loss.
4. Energy-only training for that rung, with derivatives reserved entirely for evaluation. Permitted
   only if a held-out complete-gradient set of at least five geometries still exists for scoring.
5. If even rung 4 does not fit, the rung is dropped from the ladder. **Do not substitute a
   lower-theory force label.**

Reserve, at every rung, a held-out set with **complete** gradients that never enters training. For
every finite difference, step-size and electronic convergence must keep `derivative_uncertainty`
below one third of the applicable force gate. A label that misses this is recomputed or discarded; it
does not loosen the gate.

### 5.7 Shrink ladder, declared before the pilot

Stop at the first rung that fits. Which rung fired is reported in every downstream claim.

1. **Shrink P-B.** Cut the Δ-ML set and lean harder on active learning; the literature floor is order
   10², not order 10³.
2. **Cheapen the Δ-learning baseline**, keeping the coupled-cluster upper half untouched. The
   correction gets harder to learn; the label level does not move.
3. **Reduce the workhorse basis** for production while keeping the canonical reference at cc-pVTZ, and
   carry the resulting basis error explicitly in term (B).
4. **Stop the molecule ladder one rung earlier.** This is the preferred rung, not a defeat: §5.0 is
   built to stop, and a measured limit is a result.
5. **Neutrals only.** Cations become outlook. This costs the charge-state intensity swap, which is the
   most astrophysically diagnostic part of the claim — so it ranks below stopping early.
6. **Benzene and naphthalene only.** R3 then covers two species with a full error budget. That is a
   smaller claim, honestly stated, and still more than a DFT-anchored spectrum of ten species.

**No rung of this ladder is allowed to lower the label level below coupled cluster.** The pre-pivot
plan had a rung that swapped in a DFT density; there is no equivalent here, because the coupled-cluster
anchor *is* the contribution. If the anchor cannot be afforded at a rung, the rung is dropped.

### 5.8 The derivative-quality gate sits above *label* noise, not above model defects

Inherited from the pre-pivot plan's issue-8 analysis, with the artifact category re-aimed. Two
categories, never mixed:

| Category | Examples, post-pivot | Status |
|---|---|---|
| **Model artifact** | MLIP high-order derivative noise, step-size instability in the cubic force constants, non-smooth activations, float32 round-off in a QFF | A **bug with a ceiling**. Fix it. It never enters the noise floor. |
| **Label numerical uncertainty** | finite-difference step-size and electronic-convergence sensitivity on the *same* energy surface | Irreducible property of the accepted data. **Only this** may loosen a gate. Method bias between theory levels is excluded. |

The original circularity is worth restating because it is easy to reinvent: a gate of the form
\(\max(\text{floor},\,3\times\text{noise})\) that counts the model's own defects as "noise" means **a
worse model buys a looser gate**. The [issue-8 probe](../probes/issue08_gate_consistency.py) measured
what that cost in the pre-pivot plan — a stated \(10^{-4}\) Ha tolerance implied a \(42.7\,\text{meV/Å}\)
force artifact and an effective gate \(128\times\) looser than intended, irreconcilable with the
\(5\,\text{cm}^{-1}\) frequency gate sitting in the same table. Re-run that probe rather than
re-deriving by hand whenever a tolerance changes.

**Gates, in the units the claim is made in:**

- **Force RMSE** against the gold rung: \(<\max\big(1\,\text{meV/Å},\ 3\times\text{label noise floor}\big)\).
- **Harmonic frequencies** from the MLIP Hessian against the reference Hessian: \(\le5\,\text{cm}^{-1}\).
- **Cubic force constants**: stable under step-size refinement to within a pre-registered tolerance.
  This gate has no pre-pivot ancestor and is the one most likely to fail silently — Käser et al.
  report VPT2 outliers up to \(150\,\text{cm}^{-1}\) from surfaces whose energies and forces looked
  acceptable. A model can pass every gate above and still be useless for a quartic force field.

Publish the measured label floor next to each gate, and the measured artifact next to each ceiling.



That ceiling is reachable *only because of* the §6.1 reference split: measured on the model density, the deformation-only scheme sits at \(1.7\times10^{-3}\,\text{meV/Å}\) (\(57\times\) headroom), while putting the full \(\rho\) on the grid missed it by \(10^{7}\). Publish the label floor next to the gate, and publish the measured artifact next to the ceiling.

---

## 6. Architecture, Training and Nuclear Motion

Every choice below is made for **reliability of high-order derivatives**, not for novelty. The
surface exists to be differentiated four times; that is the only requirement that matters, and it is
the one that a good energy/force fit does not automatically satisfy.

### 6.1 The production surface: a fine-tuned equivariant interatomic potential

**Starting checkpoint.** MACE-OMOL-0 (OMol25, ωB97M-VV10) as primary, because it carries explicit
**charge and spin embedding** and therefore handles the cation rungs that the whole astrophysical
claim rests on. MACE-OFF23/24 is the fallback for neutrals only. If the ASL licence ever becomes a
problem, the escape hatch is training the same architecture from scratch on the Δ-corrected set —
the *code* is MIT and only the weights are restricted.

**Two ways to attach the coupled-cluster anchor. Choose by measurement at G2, not by argument:**

| | Design | Inference cost | Risk |
|---|---|---|---|
| **(a) Δ-model** | A separate model learns \(E_{\mathrm{gold}}-E_{\mathrm{cheap}}\); the prediction is baseline + correction | Both models evaluated every step | The correction inherits the baseline's roughness; two surfaces must both be smooth |
| **(b) Fine-tune** | Continue training the foundation weights directly on coupled-cluster labels | One model | Catastrophic forgetting: the pretrained surface can degrade away from the fine-tuning data, which is exactly where a QFF probes |

Both are standard; neither is obviously right here. The tiebreaker is the §5.8 cubic-force-constant
stability test, not the energy RMSE — a design can win on energies and lose on third derivatives.

**Non-negotiable numerical requirements.**

- **float64 throughout.** Not cosmetic: a semi-numerical quartic force field differentiates the
  surface repeatedly, and float32 round-off is indistinguishable from anharmonicity.
- **Smooth activations** (GELU-class). Dral et al. (item 5) document the "wrinkly PES" pathology
  that destroys numerically differentiated high-order derivatives while leaving energies and forces
  looking fine. This is a requirement, not a preference.
- **Exact rotational equivariance and size-extensivity by construction.** Both were gated properties
  in the pre-pivot plan and are free here.

**One transferable model, not one model per molecule.** The ladder's entire point is transfer to an
unseen ring count, which a per-molecule PES cannot test. A single model is trained across the
aromatic set and evaluated on the next rung **zero-shot** before any of that rung's data is added.
Per-rung fine-tuning is permitted only as a declared fallback, reported separately, and never
substituted for the zero-shot number.

**What the model may never see.** No spectral quantity, at any stage: not as a label, not as a
selection criterion, not as an early-stopping signal, and not as a reason to hand-tune a
hyperparameter for one molecule. With identification as the endpoint, a spectral leak would not be a
methodological wobble — it would fabricate the result.

### 6.2 Training loss (static labels only)

$$L = \lambda_E L_E + \lambda_F L_F + \lambda_\mu L_\mu \;\;(+\;\lambda_\rho L_\rho\ \text{for the DMS-field leg only})$$

- \(L_E\): energy against the accepted coupled-cluster level for that rung.
- \(L_F\): complete force vectors where §5.6 rung 1–2 applies. Under rung 3 it is replaced row-wise
  by the projected-derivative loss
  \(L_D=\lvert\nabla_{\mathbf R}E_\theta\cdot\mathbf v-D_{\mathbf v}E\rvert^2\), with **every model in
  a comparison receiving the identical directions** for every `config_id`.
- \(L_\mu\): the three standardized Cartesian dipole components against the §5.4 analytic label.
  Enabled from the first production run, never added after a failed gate.
- \(L_\rho\): deformation density, **only** for the §2.2 DMS-field leg. It does not exist in the
  production PES.

Loss weights come from a fixed candidate grid, selected on **validation** data among models that
already pass the validation energy and derivative gates, and frozen before the test set is touched.

**There is no Hessian loss, and that is a deliberate consistency choice.** §5.5 makes the reference
Hessians **audit-only**; training on them would destroy the ≤5 cm⁻¹ gate that licenses the whole
claim. Machine-learned potentials routinely recover harmonic frequencies from energies and forces
alone, and the gate is there to check it rather than assume it.

**Pre-registered escalation if the ≤5 cm⁻¹ frequency gate fails:** generate a **new, separate**
curvature-label set, disjoint from the audit geometries and declared before it is computed, and add
a Hessian term. Reusing audit Hessians as training data is forbidden — it would convert the gate
into a training-set score, which is the same category of error as training on spectra.

### 6.3 Active learning: where the next expensive point goes

The Δ-ML set is order 10², so *which* geometries get gold-rung labels matters more than how many.

- **Uncertainty from a committee.** The ≥3 seeds already required by §7.1 double as the ensemble;
  disagreement in predicted **forces** is the selection signal, because forces are what the QFF
  consumes.
- **Proposal pool** from the Module 06 generative model plus normal-mode and thermal displacements.
  Proposals are candidates, never data.
- **Every selected geometry is labelled at the accepted coupled-cluster level before it is
  trusted.** No self-training, no pseudo-labels, no model-generated energies entering the training
  set. This is the same rule the pre-pivot plan applied to its Module 06 corpus, and it survives
  unchanged.
- **Stopping rule, declared in advance:** stop when a round of new points fails to move validation
  force RMSE by more than the seed scatter, or when the rung's compute budget is spent — whichever
  comes first.
- **Bookkeeping hazard.** Active learning mutates the training set, so the frozen split file gets a
  **round index**, and every gate report names the round it was computed at. A comparison across
  different active-learning rounds is not a comparison.

### 6.4 Nuclear motion: quartic force field, GVPT2, and the escalation ladder

This is where R3 is actually delivered, and it is the part the pre-pivot plan did not have.

**Quartic force field from the MLIP.** Built in normal coordinates around each optimized structure,
semidiagonal in the quartic terms, using the released MLIP→QFF→VPT2 tooling (item 26). Step sizes
are converged and **reported**, and the cubic-constant stability check of §5.8 is run here — a QFF
whose constants move with the step size is not a QFF.

**GVPT2, with the resonance treatment declared before results are seen.** Plain VPT2 diverges
whenever two states are near-degenerate, and PAH fingerprint regions are full of such pairs.
Required: explicit identification of Fermi and Darling–Dennison resonances by a **pre-registered
threshold**, deperturbation of the resonant terms out of the perturbative sum, and variational
treatment of the resulting polyads. Choosing the resonance threshold after inspecting the spectrum
is the anharmonic equivalent of metric shopping.

**Escalation ladder (from §2.1, restated here because this is where it fires):**

1. GVPT2 with explicit resonance treatment — the default.
2. **Selected VCI** over the affected polyads, for the congested 6–9 μm region.
3. Report only the band families that converged; mark the species **UNRESOLVED** for the rest.
4. **Longer classical trajectories are not on this ladder.** Substituting MD for a failed VCI is the
   single most tempting way to lose this thesis.

**What classical MD is still for.** Temperature dependence — band shifts and broadening as a
function of internal energy, which VPT2 does not give directly. It lives in a diagnostic appendix,
is labelled as such, and never carries a band-position claim.

**Tooling decision, made at G0 by measurement.** MLatom and the Kotaru/Bowman release are both run
on H₂O and benzene against known references; one is kept. Do not carry both past G0.

### 6.5 The dipole moment surface and relative intensities

Intensities are half of R3 and are where DFT-based work is least controlled, so the DMS gets its own
gates rather than riding on the PES gates.

**Three legs, pre-registered under §7.1** — frozen splits, ≥3 seeds, tuning parity, declared effect
size, "inconclusive" publishable:

| Leg | Representation | Note |
|---|---|---|
| **DMS-tensor** | Equivariant atom-centred vector head, MACE-POLAR-1 class (item 36) | Handles variable charge and spin natively; a strong baseline, not a strawman |
| **DMS-field** | \(\boldsymbol\mu=-\int\mathbf r\,\Delta\rho_\theta\,dV\), which holds **exactly** for a promolecular reference | The salvaged voxel model (§2.2) |
| **DMS-charge** | Environment-dependent partial charges | The cheap classical floor |

**The DMS must be differentiable to the order the intensity formula needs.** VPT2 intensities
require first *and* second dipole derivatives with respect to normal coordinates; a DMS that only
reproduces \(\boldsymbol\mu\) well is not sufficient, and that distinction is exactly what §5.4's
evaluation-only derivative sets exist to expose.

**Gates, all on untouched evaluation labels, all before any intensity is published:**

- \(\lVert\boldsymbol\mu_\theta-\boldsymbol\mu_{\mathrm{QM}}\rVert\) below the per-molecule threshold
  fixed at freeze time.
- Relative error in \(d\boldsymbol\mu/dQ\) **< 5 %**, because \(I\propto\lvert d\boldsymbol\mu/dQ\rvert^2\)
  and the R3 intensity claim is at the 20 % level.
- **CO₂ forbidden-mode residual** as a symmetry regression test: \(I(\nu_1)/I(\nu_3)<10^{-2}\), and
  the measured ratio consistent with \(\delta^2\) where \(\delta\) is the independently measured
  relative dipole-derivative error.
- **Neutral-to-cation intensity swap reproduced qualitatively** in the 6–9 μm and 11–12 μm families.
  This is the diagnostic astronomers actually use; failing it while passing the others means the
  model is right about positions and wrong about the thing being claimed.

If a DMS gate fails, **intensity claims are withdrawn and band positions still ship.** The gates are
separate on purpose (§3).

### 6.6 Excitation and environment model — error term (D)

A laboratory absorption spectrum and an astrophysical emission spectrum are different observables,
and comparing one to the other without a model is the error that would invalidate §3.C.

- **Against laboratory standards** (NIST gas-phase FTIR, IRMPD, PAHdb): absorption, compared
  directly. PAHdb matrix data requires the **frozen** matrix-shift model, applied identically to
  every species. Corrected and uncorrected numbers never appear in the same table.
- **Against an astrophysical product**: isolated-PAH emission follows UV photon absorption and
  vibrational cascade, not a 300 K thermal population. The model is a **microcanonical cascade**
  following the Chen/Li/Li template (item 33), with the internal-energy distribution stated.
- **Frozen before the observational product is opened**, together with the target list, band
  families, match metric and verdict rule (§3.C). Retuning the excitation model to improve a match
  is a fail.
- Its residual is error term **(D)** and appears in the budget beside (A), (B) and (C) — never
  folded into them.

### 6.7 The DMS-field leg: what survives from the voxel model, and what got simpler

The field model is no longer an energy functional. As a **dipole** surface it keeps the parts of the
pre-pivot design that were measured to work, and sheds the parts that existed only to make an energy
out of a grid.

**Kept — the reference split.** The physical density is
\(\rho_{\mathrm{tot}}=\rho_{\mathrm{ref}}+\Delta\rho_\theta\), with
\(\rho_{\mathrm{ref}}=\sum_A\rho^{\mathrm{atom}}_{Z_A}(|\mathbf r-\mathbf R_A|)\) a **promolecular**
superposition of spherically averaged free-atom densities, fitted once per element to a short sum of
Gaussians and frozen. Only the smooth \(\Delta\rho_\theta\) is ever discretized, with
\(\int\Delta\rho_\theta\,dV=0\) enforced by mean subtraction on every forward pass. The
[issue-7 probe](../probes/issue07_grid_representability.py) measured why this is not a convenience:
putting \(\rho_{\mathrm{tot}}\) on a 0.20 Å grid gives an 11 % electron-count error and a 3.8 Ha
per-cell translation artifact, while \(\Delta\rho\) alone gives \(3\times10^{-10}\,e\).

**Kept — the exact observable.** Because a promolecule of neutral spherical atoms has identically
zero dipole,

$$\boldsymbol\mu=\int\mathbf r\,(\rho_{\mathrm{nucl}}-\rho_{\mathrm{tot}})\,dV=-\int\mathbf r\,\Delta\rho_\theta\,dV\quad\text{exactly.}$$

The graded observable is therefore a direct integral of the object that is actually supervised, not
the residue of two much larger numbers. This identity — found while closing round-2 issue 11 — is
the entire reason the field model is still in this plan.

**Kept — the measured artifact budgets.** The translational artifact in \(\boldsymbol\mu\) (< 0.1 % of
\(\lvert\boldsymbol\mu\rvert\)) and the rigid-rotation residual both transfer unchanged from
[the issue-11/12 probe](../probes/issue11_12_observable_and_invariance.py). They matter more here than
they did for the energy: an equivariant tensor DMS satisfies these symmetries by construction, so
any field-leg loss must be reported alongside its symmetry residual or the comparison is
uninterpretable (§7.1 confound (a)).

**Dropped, and the plan is smaller for it:**

| Removed | Why it is no longer needed |
|---|---|
| \(\varepsilon_\theta\) and the anchoring fork (vanishing anchor vs difference form) | There is no learned energy functional to anchor |
| \(E_{\mathrm{es}}\), the analytic Gaussian integral table, \(E_{nn}\) as point charges | No energy is computed from the field |
| **The Hockney–Eastwood open-boundary Poisson solver** | It existed to evaluate \(\tfrac12\langle\Delta\rho\vert\Delta\rho\rangle\). A dipole is a first moment: no Poisson solve, no zero-padded \(2N\) box, no boundary-convergence study |
| Autograd forces through the density; the conservativity machinery | Forces come from the MLIP |
| The Φ-bypass prohibition (round-2 issue 10) | \(\varepsilon_\theta\) is gone, so there is nothing to bypass |

**What remains to build** is therefore a density encoder — local \(3\times3\times3\) convolutions
with an optional non-local FNO mixer — plus one first-moment integral. That is a far smaller object
than the pre-pivot design, which is exactly why it can be run as a falsifiable side-comparison
instead of a critical-path dependency.

**Leg-specific gates.** Grid convergence of \(\boldsymbol\mu\) with \(\Delta x\); translation and
rotation residuals against the §6.5 thresholds; and the frozen-wrong-density diagnostic — feed a
deliberately incorrect \(\Delta\rho\) and confirm the predicted dipole degrades. If this leg cannot
pass its own gates it is dropped, and §6.5's tensor or charge leg carries the intensities.

---

## 7. Roadmap: gates G0–G6

Seven gates replace the pre-pivot Phases 0a–5. Each is a **measurement with a written verdict**, not
a milestone. A gate that cannot be evaluated is a failed gate; missing data never counts as a pass.

| Gate | Goal | Scope | Hard criteria | Unblocks |
|---|---|---|---|---|
| **G0 — Environment and baseline reproduction** | Reproduce the status quo before improving it | ORCA + MRCC + MLIP + QFF/VPT2 toolchain; benzene and naphthalene | Toolchain installed and executing end to end · **scaled-harmonic B3LYP spectra of benzene and naphthalene reproduced against PAHdb to within the published scatter** · nuclear-motion tooling bake-off (MLatom vs the Kotaru/Bowman release) run on H₂O and benzene against known references, **one selected in writing** · a pipeline that cannot reproduce a known answer has not been debugged | Everything |
| **G1 — The gold rung, measured** | Earn the word "gold" | §5.5 frozen audit set, per molecule **and charge state** | Smoke-test table filled with numbers, closed- and open-shell as separate rows · cost pilot per rung, canonical and local separately · **B1** local-vs-canonical and **B2** basis convergence both reported per molecule, charge state **and band family** · relative energy RMSE ≤ 1.0 kcal/mol (max ≤ 2.0) · directional derivative RMSE ≤ 1.0 meV/Å · **harmonic mode shift ≤ 5 cm⁻¹** · derivative rung (§5.6) and shrink-ladder rung (§5.7) selected **in writing before any production run** · claim-ladder rung recorded | The Δ-ML campaign |
| **G2 — Surface quality** | A surface worth differentiating four times | Δ-ML set; both attachment designs from §6.1 | Held-out energy ≤ 1 kcal/mol and forces ≤ 1 meV/Å against the gold rung · harmonic frequencies within **5 cm⁻¹** of the reference Hessian · **cubic force constants stable under step-size refinement** — the gate with no pre-pivot ancestor and the one most likely to fail silently · Δ-model vs fine-tune decided on that stability test, **not** on energy RMSE · zero-shot next-rung error reported **before** that rung's data is added | Nuclear motion |
| **G3 — Nuclear motion** | Anharmonicity that is real, not fitted | Benzene (rung 0) | GVPT2 band centres within **10 cm⁻¹** of the one frozen gas-phase FTIR dataset, for all three scored band families · resonance treatment documented and its threshold **shown to have been pre-registered** · any VCI escalation declared · **compared against both baselines**: scaled-harmonic and DFT-VPT2, so an improvement is attributable to the anchor rather than to the method | Intensities |
| **G4 — Intensities** | Earn the second half of R3 | DMS bake-off, all three legs | \(\lVert\boldsymbol\mu_\theta-\boldsymbol\mu_{\mathrm{QM}}\rVert\) below the frozen per-molecule threshold · relative error in \(d\boldsymbol\mu/dQ\) **< 5 %** · CO₂ forbidden-mode residual \(I(\nu_1)/I(\nu_3)<10^{-2}\), consistent with \(\delta^2\) · **neutral-to-cation intensity swap reproduced qualitatively** · **failure withdraws intensity claims and leaves band positions standing** | The ladder |
| **G5 — Transfer** | Find the measured limit | §5.0 ladder, rung by rung | Per rung: band centres inside the §9 tolerance against that rung's **named** standard · the **four-term error budget published per rung**, never pooled · the first rung that fails is the **stop rung** and is published as the measured limit · stopping is a result, and climbing past a failed rung is misconduct | Identification |
| **G6 — Fail-closed identification** | Confront one observation, once | One frozen JWST/PAHdb product | Pre-registration document **dated before the product is opened**: target list, band families, match metric, PASS/FAIL/UNIDENTIFIED rule, isomer-degeneracy rule · excitation model (§6.6) frozen in the same commit · **negative control must fail** · test evaluated **once** · verdicts limited to **Supported / Rejected / Unidentified-degenerate** | Module 09 |

**Ordering rules.**

1. **G0 blocks everything.** Nothing downstream is interpretable without the reproduced baseline.
2. **G1 and G2 are not interchangeable.** G1 measures the *labels*; G2 measures the *model*. A model
   that fits bad labels beautifully passes G2 and is worthless.
3. **G3 and G4 gate different halves of the claim** and are evaluated independently, so that an
   intensity failure cannot silently sink band positions.
4. **G5's target list feeds G6's pre-registration.** Restricting the identification list to species
   that passed G5 is legitimate, because G5 never touches the observational product. Restricting it
   *after* opening that product is a fail.
5. **Nothing debuts at G6.** Every component has already passed its own gate.

**Gate unit discipline, inherited and re-aimed.** Every tolerance above is quoted in the unit the
claim is made in — cm⁻¹ for positions, per-cent for relative intensities, meV/Å for forces,
kcal/mol for energies. A tolerance quoted in a convenient unit is a tolerance nobody can check
against the deliverable. The conversion arithmetic and the anti-circularity derivation live in
[probes/issue08_gate_consistency.py](../probes/issue08_gate_consistency.py); re-run it rather than
re-deriving by hand whenever a tolerance changes.

### 7.1 Pre-registration

Three comparisons in this plan can be gamed after the fact, and none is an experiment until it is
fixed **in a commit that predates the first result**. All of this is free now and unrecoverable
later.

**Common machinery, applied to all three.** One frozen split file per campaign, with an
active-learning **round index** (§6.3), committed and hash-referenced in every gate report — nobody
re-splits. Minimum **3 seeds** per model; a single-seed number is not a result, and the primary
metric is reported as mean ± SD. **Tuning parity**: equal trial count and equal wall-clock budget,
tuned on validation only, with each competitor starting from its authors' recommended recipe as
trial 0 — an untuned competitor is a straw man and a reviewer will say so. The analysis, aggregation
and plot are specified before test evaluation. **The test set is touched once**, and any
re-evaluation is disclosed with its reason.

**P1 — Anchor attachment (gate G2).** Δ-model versus fine-tune, §6.1.

| Outcome | Condition |
|---|---|
| Δ-model | cubic-constant stability better by more than the pre-registered margin, with non-overlapping ±1 SD |
| fine-tune | the same, reversed |
| **inconclusive** | otherwise — in which case take the cheaper design and say so |

The primary metric is **step-size stability of the cubic force constants**, declared here so it
cannot later be swapped for the energy RMSE that happens to look better.

**P2 — Dipole moment surface (gate G4).** DMS-field vs DMS-tensor vs DMS-charge, §6.5. Primary
metric: relative error in \(d\boldsymbol\mu/dQ\) on the held-out modes. Effect size \(\Delta\)
finalised as **3× the measured within-model seed scatter on the validation split**, before any leg is
evaluated on held-out modes. Setting \(\Delta\) from validation scatter is legitimate; setting it
after seeing the comparison is not.

| Result | Defensible conclusion |
|---|---|
| DMS-field beats DMS-tensor | Evidence that a real-space density representation carries dipole derivatives better, under equal labels |
| DMS-tensor wins or ties | No demonstrated advantage for the field representation; it is dropped and the tensor leg carries intensities |
| DMS-charge is not beaten by either | The expensive legs bought nothing — report it plainly |
| Any comparison inside \(\Delta\) | **Inconclusive**, which is publishable |

**"Inconclusive" is a pre-authorised outcome.** It was in the pre-pivot plan for the same reason and
must survive here: the honest answer to "did the field representation help?" may be "we could not
tell", and a plan that cannot say that will find a way to say something else.

**P3 — Identification (gate G6).** The pre-registration *is* the experiment. Frozen before the
observational product is opened: the target species and charge states (drawn only from rungs that
passed G5), the scored band families, the match metric, the PASS/FAIL/UNIDENTIFIED thresholds, the
rule for when two isomers both fit, and the negative control that must fail. Changing any of these
after seeing the data is a fail, and "we identified something else instead" is not a result.

**Confounds registered in advance**, so that they cannot be discovered as excuses later:

| | Confound |
|---|---|
| (a) | The DMS-tensor leg is exactly equivariant and the field leg is not. **Both symmetry residuals are published before the P2 bake-off**, so that a field-leg loss can be read correctly — "worse representation" and "broken discretization" are different conclusions. |
| (b) | Tuning-maturity asymmetry: the tensor leg is a released foundation model, the field leg is bespoke. |
| (c) | Which §5.7 shrink-ladder rung fired. |
| (d) | Which §2.1 escalation rung fired, for electronic structure and for nuclear motion separately. |
| (e) | The active-learning round index each result was computed at. |
| (f) | Whether canonical coupled cluster was available at that rung, or only the local method with its measured error. |

---

## 8. Additional Quality-Assurance / Verification Protocol

These checks were raised piecemeal across both conversations (mostly in the 23-point review) and apply throughout, not just at Phase 0:

1. **Conservativity verification**: test $\oint\mathbf{F}\cdot d\mathbf{R}$ over dozens of random closed loops in configuration space, not just one molecule/one path.
2. **Force finite-difference check**: $F_i \stackrel{?}{=} -\dfrac{E(\mathbf{R}+\delta\mathbf{e}_i)-E(\mathbf{R}-\delta\mathbf{e}_i)}{2\delta}$, in float64, targeting \(<0.05\,\text{meV/Å}\) \((10^{-6}\,\text{a.u.})\). **This check cannot see the egg-box**: autograd and finite differences read the same discretized \(E\) and will agree beautifully on a wrong force. It validates the autograd graph, and nothing else.
3. **Egg-box quantification**: rigidly translate a molecule across a full grid cell in small steps and plot $E(\delta)$, $F(\delta)$ for several $\sigma/\Delta x$ ratios **and along \(x\), \(y\), \(z\) and a body diagonal**; report the residual artificial periodicity **in force units**, as the max over directions, against the \(0.1\,\text{meV/Å}\) engine-artifact ceiling. Never report it in Hartree alone.
4. **Grid-convergence study**: report vibrational frequency, energy, and force as a function of $\Delta x$ (e.g. 0.40 → 0.15 Å) so that ML error is not confounded with grid discretization error.
5. **Poisson boundary-condition convergence**: show convergence of results with increasing padding/box size for the isolated-molecule electrostatics.
6. **Error decomposition** — explicitly separate and report three distinct error sources rather than conflating them into one "accuracy" number:
   - (A) ML error = model vs. CCSD(T);
  - (B) electronic-structure error = production CCSD(T)/cc-pVTZ vs. the frozen §5.1 CCSD(T)/CBS(T,Q) audit, reported by molecule and quantity; residual post-CCSD(T), core-correlation and relativistic effects remain limitations;
   - (C) spectroscopic/nuclear-motion error = classical MD vs. the true quantum rovibrational result.
7. **Extended energy-conservation metrics** beyond drift alone: $\Delta E_{max}$, $\Delta E_{RMS}$, force-consistency ($\lVert\nabla_\mathbf{R}\times\mathbf{F}\rVert$), and timestep-convergence. Drift is budgeted **over the production trajectory length** as a fraction of \((3N-6)k_BT\) (§7 gate unit discipline), never as a bare Hartree/ps figure.
8. **Extended spectral-quality metrics**: peak-position error, integrated-intensity error, relative-intensity error, forbidden-mode residual intensity, linewidth, and convergence with trajectory length.
9. **Charge/dipole sanity check**: numerically verify $\int\rho(\mathbf{r},t)\,d^3r = N_e$ stays within 0.01% throughout a run (a corrupted charge integral at $t=0$ was flagged early as poisoning all downstream gradients).
10. **Do not treat compute budgets as fixed a priori** — the earlier "18–24 hours on one A100 for benzene" estimate was flagged as likely too optimistic. Two measured budgets are required, and neither is a guess:
    - **Data campaign** (§5.1): \(T_{\mathrm{campaign}}\approx N_{\mathrm{geom}}\times\bar t_{\mathrm{geom}}\) from the 10-geometry H₂O and benzene pilots. This is a Phase 0 **exit**. If it does not fit, take the shrink ladder *before* P1/05 training.
    - **MD inference** (this item, original intent): derive a realistic 20–50 ps trajectory cost only *after* a real 10-ps H₂O run on the frozen PES, then extrapolate memory/time. Do not quote A100 folklore.
11. **Reference-split validation** (round-2 issue 7) — a standing check, not a one-off. For \(\ge20\) geometries per molecule, compare the grid pipeline's \(E_{ne}\) and \(E_H\) against their **exact analytic values in the Gaussian basis**, which PySCF returns for free. Report max and RMS deviation. Any drift in this number over the campaign means the export grid, the reference fit, or the smearing width changed without anyone noticing.
12. **Observable validation** (round-2 issue 11; round-3 issue 4) — the graded deliverable is band positions **and relative intensities**, so \(\boldsymbol{\mu}\) and \(d\boldsymbol{\mu}/d\mathbf{R}\) are first-class quantities. Report held-out \(\boldsymbol{\mu}\) error, evaluation-only \(d\boldsymbol{\mu}/d\mathbf{R}\) relative error, and the translational grid artifact in \(\boldsymbol{\mu}\), against the §7 Phase 1 gates. \(L_\mu\) is pre-registered in the production loss because \(L_\rho\) alone does not optimize a first moment. If either gate fails, block production MD and withdraw relative-intensity claims; do not add a new loss after observing the test result.
13. **Invariance budget** (round-2 issue 12) — a voxel-grid energy is neither translation- nor rotation-invariant, and neither residual was previously gated:
    - **Translation:** \(\lVert\sum_A\mathbf{F}_A\rVert\) is \(-\partial E/\partial(\text{rigid shift})\), i.e. the egg-box force in a different costume. It is *not* a new gate — it is bounded by the same \(0.1\,\text{meV/Å}\) ceiling, and it is a cheap **online** monitor of that ceiling during production MD.
    - **Rotation:** \(\lVert\sum_A\mathbf{R}_A\times\mathbf{F}_A\rVert\) is **not** covered by any translation sweep and must be measured with its own rigid-rotation scan, reported as \(\tau_{\max}/r_{\max}\) in meV/Å against the same ceiling. Measured on the model density, the reference split gives \(3\times10^{-5}\,\text{meV/Å}\) against \(1.7\times10^{3}\,\text{meV/Å}\) for the full density on the grid — but that ordering was not knowable in advance, which is exactly why it is a gate and not an assumption.
    - **Pre-registered confound:** rotation is the symmetry an equivariant GNN satisfies *by construction*. Both residuals must be published **before** the Phase 4 bake-off, so that a G1 win can be read correctly — “the field representation is worse” and “our discretization broke a symmetry the competitor gets for free” are different conclusions, and only pre-registered numbers can tell them apart.

---

## 9. Precision Claims — final, defensible wording

- ✅ "From a static-label-trained PES and dipole surface, frozen-weight dynamics predict vibrational band positions and relative IR spectral envelopes/intensities within a stated cm⁻¹ tolerance for H₂O, D₂O, CO₂ and benzene. No spectra, peak positions or intensities are training targets."
- ✅ "The frozen model reproduces the H₂O→D₂O isotope shift and CO₂ symmetry-forbidden intensity with zero retraining."
- ❌ "We predict chemically precise, high-resolution IR spectral lines" (rovibrational-line-list precision) — not defensible with classical MD + FFT.
- ❌ "Chemical precision on large PAHs (C₄₈+)" — explicitly out of scope for the thesis; at most a discussion-chapter outlook via naphthalene. The post-master’s path is [Project 10](Horizon/10_Size_Extensive_Aromatic_PES.md) (labels + size-extensivity) → [Project 11](Horizon/11_Anharmonic_IR_and_Intensities.md) (GVPT2-class bands + intensities) → [Project 12](Horizon/12_Astrophysical_PAH_Identification.md) (fail-closed identification). None of those is a Udacity module.
