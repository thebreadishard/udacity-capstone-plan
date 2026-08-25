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
> | §6 architecture and training | ⛔ pre-pivot |
> | §7 phased roadmap, §7.1 pre-registration | ⛔ pre-pivot |
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

## 6. Architecture & Training Details (final)
Workstream P1 and Module 05 **share this forward pass**. They must not diverge into a latent energy head on one molecule and a functional on the other.

### 6.1 Forward pass (implements \(E=\mathcal{E}[\rho,R]\))

**0. Reference split (not learned; resolves round-2 blocking issue 7).**

$$\rho_{\mathrm{tot}}(\mathbf{r};\mathbf{R})=\underbrace{\sum_A \rho^{\mathrm{atom}}_{Z_A}\!\big(|\mathbf{r}-\mathbf{R}_A|\big)}_{\rho_{\mathrm{ref}}\ \text{— analytic, frozen}}+\ \Delta\rho_\theta(\mathbf{r};\mathbf{R}),\qquad \rho^{\mathrm{atom}}_{Z}(u)=\sum_k c_{Z,k}\left(\frac{\alpha_{Z,k}}{\pi}\right)^{3/2}e^{-\alpha_{Z,k}u^2}$$

The per-element coefficients are fitted **once**, offline, to the spherically averaged free-atom ground-state density, then frozen. Every integral over \(\rho_{\mathrm{ref}}\) is closed form — Gaussian–point-charge is \(Z\,\mathrm{erf}(\sqrt{\alpha}\,r)/r\), Gaussian–Gaussian is an \(\mathrm{erf}\) of the reduced exponent — and analytically differentiable in \(\mathbf{R}_A\), so autograd forces stay exact. **Only \(\Delta\rho_\theta\) is ever discretized.**

**1. Nuclei → fields (not learned).**

- \(E_{nn}\) is **exact analytic point charges**, \(\sum_{A<B}Z_AZ_B/R_{AB}\). It is *not* read off a smeared grid: at \(\sigma=0.3\,\text{Å}\) the Gaussian–Gaussian O–H repulsion is short by a factor \(\mathrm{erf}(R/2\sigma)=0.976\), i.e. \(\approx0.1\,\)Ha of geometry-dependent error that \(\varepsilon_\theta\) would otherwise have to repair at the mHa level.
- Gaussian smearing \(\sigma\ge1.5\,\Delta x\) survives **only** as the grid kernel for terms that integrate \(\Delta\rho_\theta\) against a nuclear potential:

$$V^{\sigma}_{\mathrm{nucl}}(\mathbf{r})=-\sum_A Z_A\,\frac{\mathrm{erf}\!\big(|\mathbf{r}-\mathbf{R}_A|/\sqrt{2}\sigma\big)}{|\mathbf{r}-\mathbf{R}_A|}$$

which is finite and smooth at the nucleus. Smooth kernel × smooth \(\Delta\rho\) is the only regime in which \(0.2\,\text{Å}\) quadrature is defensible.

**2. Density encoder (NCA / optional FNO).** State on the grid: one real, **sign-changing** deformation channel plus latent NCA memory (hidden state, not physics). Local \(3\times3\times3\) NCA steps handle short range. An optional learned FNO is a non-local mixer **inside this encoder only**. Readout:

$$\Delta\rho_\theta(\mathbf{r};\mathbf{R})=s(\mathbf{r})-\frac{1}{V}\int s\,dV,\qquad \int\Delta\rho_\theta\,dV=0$$

No \(\mathrm{softplus}\), no renormalize-to-\(N_e\), no \(\rho_{Im}\), no EM channels. Total positivity \(\rho_{\mathrm{ref}}+\Delta\rho_\theta\ge0\) is a monitored diagnostic with a soft penalty, not a hard architectural constraint.

**3. Energy is a functional of the total density.** No second head:

$$E_\theta(\mathbf{R})=\sum_A E^{\mathrm{atom}}_{Z_A}+E_{\mathrm{es}}\big[\rho_{\mathrm{ref}}+\Delta\rho_\theta,\mathbf{R}\big]+\int\varepsilon_\theta\,dV$$

\(E_{\mathrm{es}}\) is expanded so that each piece is computed where it is accurate:

| Piece | How | Why there |
|---|---|---|
| \(E_{nn}\) | analytic point charges | exact and free |
| \(-\sum_A Z_A\!\int\rho_{\mathrm{ref}}/|\mathbf{r}-\mathbf{R}_A|\) | **analytic** | largest, sharpest e–n term; never voxelized |
| \(-\sum_A Z_A\!\int\Delta\rho_\theta/|\mathbf{r}-\mathbf{R}_A|\) | grid, against \(V^{\sigma}_{\mathrm{nucl}}\) | smooth × smooth |
| \(\tfrac12\langle\rho_{\mathrm{ref}}|\rho_{\mathrm{ref}}\rangle\) | **analytic** | dominant Hartree piece |
| \(\langle\rho_{\mathrm{ref}}|\Delta\rho_\theta\rangle\) | grid, against the analytic promolecular Hartree potential \(V_{\mathrm{ref}}\) (erf form, finite at the nucleus) | smooth × smooth |
| \(\tfrac12\langle\Delta\rho_\theta|\Delta\rho_\theta\rangle\) | **Hockney–Eastwood FFT** | the only term that needs the solver |

Because \(\int\Delta\rho_\theta\,dV=0\) exactly, the source handed to Hockney–Eastwood is charge-neutral and its potential decays at least as fast as a dipole — the zero-padding requirement gets *cheaper*, and Phase 0 finally validates the solver on the object it will actually be given.

**Anchoring of \(\varepsilon_\theta\) — named open fork, decided in Phase 0 / P1, not in Module 05.** The same core-domination disease afflicts \(\int\varepsilon_\theta\,dV\) (Thomas–Fermi kinetic density goes as \(\rho^{5/3}\)). Two candidate forms:

- **(i) Vanishing anchor:** \(\varepsilon_\theta\equiv\Delta\rho_\theta\cdot f_\theta(\rho_{\mathrm{ref}},\Delta\rho_\theta,|\nabla\Delta\rho_\theta|)\), identically zero at \(\Delta\rho=0\). Removes the core-dominated quadrature outright and cuts the dynamic range the learned term must span from \(\sim76\,\)Ha (round-2 issue 9) to the bonding remainder, \(\sim1\,\)Ha. Cost: it asserts that the promolecule's energy is \(\sum_A E^{\mathrm{atom}}_{Z_A}\) plus classical electrostatics, which omits the Pauli/exchange repulsion of overlapping atomic densities; the learned term must absorb that at physical geometries.
- **(ii) Difference form:** \(\varepsilon_\theta=g_\theta(\rho_{\mathrm{tot}},|\nabla\rho_{\mathrm{tot}}|)-g_\theta(\rho_{\mathrm{ref}},|\nabla\rho_{\mathrm{ref}}|)\). Keeps a genuine functional of \(\rho_{\mathrm{tot}}\), but each term is individually cusped and the cancellation is numerical rather than analytic.

**Decision rule:** measure the quadrature error of \(\int\varepsilon\,dV\) for both forms against a fine reference grid on the Phase 0 real cube, then on P1 H₂O. Pick one **before** the benzene campaign. Do not carry both into Module 05.

**Inputs to \(\varepsilon_\theta\) (resolves round-2 blocking issue 10).** \(\varepsilon_\theta\) is a tiny MLP / \(1\times1\times1\) conv on **density-derived local scalars only**: \(\rho_{\mathrm{ref}}\), \(\Delta\rho_\theta\), \(|\nabla\Delta\rho_\theta|\). It must **not** see \(Z_A\), one-hot elements, bond lists, or raw \(\mathbf{R}\) — **and it must not see \(\Phi\) or \(V_{\mathrm{nucl}}\)**. \(\Phi\) is the *external* potential; near a nucleus it is a direct readout of \(Z_A/|\mathbf{r}-\mathbf{R}_A|\), so feeding it hands the "functional" a channel through which it can learn part of \(E(\mathbf{R})\) without consulting the density — exactly the multi-head-regressor failure §4 forbids. **Required diagnostic:** freeze \(\Delta\rho_\theta\) at a deliberately wrong density and confirm the predicted energy degrades.

**4. Forces.** \(\mathbf{F}_A=-\partial E_\theta/\partial\mathbf{R}_A\) via PyTorch autograd through the analytic \(\rho_{\mathrm{ref}}\) placement, through the nuclear kernel, **and** through \(\Delta\rho_\theta(\mathbf{R})\). Do not `stop_grad` on \(\Delta\rho\). Hellmann–Feynman alone is not exact for a learned density fitted to CCSD(T).

If this graph is implemented, \(E\) *is* \(\mathcal{E}[\rho,R]\) — \(\rho_{\mathrm{ref}}\) is a parameter-free deterministic function of \(\mathbf{R}\), so the split changes how the functional is evaluated, not what it is a functional of. A trunk that emits both \(\rho\) and a scalar \(E\) from pooled latents is a spec violation, not a variant.

### 6.2 Poisson vs FNO — two objects

| Object | Role | Who validates it |
|---|---|---|
| **Analytic Gaussian integrals** | Everything involving \(\rho_{\mathrm{ref}}\): \(E_{nn}\), the promolecular e–n attraction, \(\tfrac12\langle\rho_{\mathrm{ref}}|\rho_{\mathrm{ref}}\rangle\), and the analytic \(V_{\mathrm{ref}}\) evaluated at grid points. Closed form, no quadrature. | Phase 0 (against a fine-grid reference) |
| **Hockney–Eastwood** | Poisson for the **smooth, charge-neutral** \(\Delta\rho_\theta\) only. Embed \(N^3\) in a \(2N\times2N\times2N\) zero-padded box; cap the Coulomb kernel at the box radius. | Phase 0 |
| **Learned FNO** | Optional non-local block **in the density encoder** | Module 05 ablation |

Do **not** treat the FNO as a learned Poisson solver. Phase 0 would then validate something 05 immediately replaces, and the ablation would mix two physics stories.

**Module 05 controlled experiment:** same \(\mathcal{E}\), same \(E_{\mathrm{es}}\); encoder = local-NCA-only vs local-NCA+FNO. One changed variable. The question is whether the non-local encoder improves \(\rho\) and therefore \(E\) and \(\mathbf{F}\).

**Optional diagnostic (not the rubric ablation):** drop \(E_{\mathrm{es}}\) and keep only \(\int\varepsilon_\theta\). If that works as well, the field-functional story is weaker than claimed. Report it; do not train that way by default.

Do not invent a more exotic \(\mathcal{E}\) (orbital-free kinetic libraries, learned pair densities) until this one fails. This is the smallest object that makes the equation true.

### 6.3 Training loss (static configurations only — no spectral term)

**Production spectroscopy model:**

$$L_{train} = \lambda_E L_E + \lambda_F L_F + \lambda_H L_H + \lambda_\rho L_\rho + \lambda_\mu L_\mu$$

- $L_E$: MSE on total energy vs. CCSD(T).
- $L_F$: MSE on complete force vectors derived from the CCSD(T) energy surface, when available. For the §5.1 benzene directional fallback, replace this term row-wise with \(L_D=\lvert\nabla_{\mathbf R}E_\theta\cdot\mathbf v-D_{\mathbf v}E_{\mathrm{CCSD(T)}}\rvert^2\). Field and MACE receive the same derivative kind and direction for every `config_id`; analytic CCSD forces are never targets.
- $L_H$: Hessian supervision at the **counted** stationary points in §5.1 (1 H₂O + 1 benzene equilibrium Hessian first). Force-only supervision does **not** guarantee correct 2nd/3rd-order PES derivatives.
- $L_\rho$: MSE on the **deformation** density \(\Delta\rho=\rho_{\mathrm{QM}}-\rho_{\mathrm{ref}}\), where \(\rho_{\mathrm{QM}}\) is the §5.1 density target (default: relaxed CCSD 1-RDM, not a slogan “exact CCSD(T) density”). This supervises the *argument* of \(\mathcal{E}\); it is not an optional extra head and not the force source. Supervising \(\Delta\rho\) rather than \(\rho\) also removes the core domination that made a plain \(L_\rho\) nearly blind to the diffuse valence tail — the tail that sets \(\boldsymbol{\mu}\) (round-2 issue 11).
- $L_\mu$: MSE on the three standardized Cartesian components of \(\boldsymbol\mu_\theta\) against the analytic §5.1 dipole label. It is enabled from the first production run, not added after a failed gate. The fixed candidate grid is \(\lambda_\mu\in\{0.01,0.1,1,10\}\) after standardization by training-set component variance. Select on validation data by minimum dipole RMSE among models that pass the validation energy/derivative gates; freeze before the test set is touched. There is **no** \(L_{d\mu}\) and no spectral loss.

**§2 comparison cohort (round-3 issue 1):** three separately trained models use the same configurations, CCSD(T) energies, same-surface full or directional derivative labels, splits and seeds. To keep the information comparison clean, \(\lambda_H=0\) for all three comparison legs; the equilibrium Hessian remains an evaluation target.

| Leg | Training labels | Purpose |
|---|---|---|
| **MACE-EF** | \(E\) plus the accepted same-surface full/directional derivatives | Equivariant-GNN comparator |
| **Field-EF** | Identical energy/derivative labels, with \(\lambda_\rho=0\) | Primary equal-label representation test against MACE-EF |
| **Field-EFρ** | Identical energy/derivative labels plus \(\rho\) | Density-supervision ablation against Field-EF |

Field-EF and Field-EFρ have identical architecture, initialization seeds, optimizer schedule and fixed hyperparameters; only \(\lambda_\rho\) changes. Neither comparison leg receives \(L_\mu\); density and dipole errors are evaluation-only there. Passing them is not required for the equal-label force comparison, but failure means the internal field must not be described as a physical electron density. The full \(E/F/H/\rho/\mu\) production model is reported separately and may support the spectroscopy result, never the representation-only causal claim.

### 6.4 MD / frozen-weight spectroscopy protocol (run only after static-label training)

**Precondition (round-2 issue 11; round-3 issue 4).** Do not start a production trajectory until the §7 Phase 1 **dipole** gates have passed on untouched evaluation labels. \(I(\omega)\) is a functional of \(\boldsymbol{\mu}(t)\); 50 ps of MD cannot repair a wrong \(d\boldsymbol{\mu}/d\mathbf{R}\), it only spends compute on it. If either dipole gate fails, production MD is blocked and relative-intensity claims are withdrawn. Do not add \(L_\mu\) or \(L_{d\mu}\) after seeing the failure.

**Precondition (round-2 issue 12).** Report \(\lVert\sum_A\mathbf{F}_A\rVert\) and total linear/angular momentum drift over the trajectory. Projecting out net force and torque before integration is allowed **only** if the residual is already below the §7 engine-artifact ceiling — i.e. as cosmetics, never as a crutch that hides a broken engine.

- Timestep $\Delta t = 0.5\,\text{fs}$ (this was judged fine on its own — ~20 samples per C–H stretch period).
- Trajectory length **20–50 ps** (40,000–100,000 steps) — a deliberate, large increase from the earlier 0.5–1 ps, which was shown to give only ~33–67 cm⁻¹ Fourier resolution, incompatible with a 10–15 cm⁻¹ precision claim. 50 ps gives ≈0.67 cm⁻¹ resolution.
- Ensemble of **5–10 independent NVE trajectories** after NVT equilibration at $T=300\,\text{K}$ (a single trajectory from the equilibrium geometry is not treated as a full spectroscopic experiment).
- Spectrum via dipole autocorrelation with the standard harmonic quantum-correction factor:
    $$I(\omega) \propto \omega\cdot\tanh\!\left(\frac{\beta\hbar\omega}{2}\right)\int_{-\infty}^{\infty}\langle\boldsymbol{\mu}(0)\cdot\boldsymbol{\mu}(t)\rangle e^{-i\omega t}\,dt$$

---

## 7. Phased Roadmap with Go/No-Go Quality Gates

| Phase | Goal | Molecule(s)/Grid | Hard Go/No-Go Criteria |
|---|---|---|---|
| **Fase 0a — Engine and artifact sweeps** (no ML, **no QM**) | Validate the differentiable physics engine itself and produce the Module 03 sweep | Analytic/reference densities + per-element atomic reference fits | **Total engine artifact \(<0.1\,\text{meV/Å}\)** \((1.9\times10^{-6}\,\text{a.u.})\), which at \(\Delta x=0.20\,\text{Å}\) means egg-box amplitude \(<2.3\times10^{-7}\,\)Hartree · \(\lVert\mathbf{F}_{autograd}-\mathbf{F}_{finite\text{-}diff}\rVert<0.05\,\text{meV/Å}\) \((10^{-6}\,\text{a.u.}, \text{float64})\) — a check of the autograd graph, **not** of discretization · closed-loop force conservation · energy drift over the **production trajectory length** \(<1\%\) of \((3N-6)k_BT\) (H₂O / 50 ps / 300 K: \(6\times10^{-7}\,\)Hartree/ps) · Hockney FFT-Poisson solver validated · egg-box across \(\sigma/\Delta x \in \{1,1.5,2,2.5,3\}\) over **randomly drawn rigid poses** (which subsumes the \(x/y/z\)/diagonal requirement), reported as a distribution in force units · **rigid-rotation residual** as \(\tau_{\max}/r_{\max}\) against the same ceiling · grid-convergence study across \(\Delta x \in \{0.40,\dots,0.15\}\,\text{Å}\) · box-size/boundary convergence · **per-element atomic reference fits** accepted at \(\int\lvert\rho^{\mathrm{fit}}-\rho^{\mathrm{atom}}\rvert dV/Z<10^{-3}\) · **the 800-row sweep CSV exists** ([Capstone_Mapping.md](Capstone_Mapping.md) §4) | **Unblocks Module 03.** |
| **Fase 0b — QM foundation, cost and label audit** (needs PySCF + limited HPC) | Lock the §5.1 recipe and precision wording with **measured** numbers | 1-geometry smoke tests + **10-geometry H₂O and benzene cost pilots** + one real H₂O CCSD 1-RDM cube + frozen CBS(T,Q) audit | **Filled smoke-test table** (energy / 1-RDM / analytic CCSD(T) gradient / analytic AO dipole / Hessian for H₂O and benzene) · AO dipole agrees with the real-cube/reference-split reconstruction within the grid-artifact budget · **same-surface derivative pilot passed:** at least 3 seeded directions per pilot geometry, \(h\) vs \(h/2\) convergence reported, CCSD-vs-CCSD(T) discrepancy reported as method bias · **derivative rung selected in writing** with measured complete-gradient and directional costs · derivative uncertainty \(<1/3\) of the Phase 1 threshold · **CBS(T,Q) audit complete** for the frozen 19 H₂O / 13 CO₂ / 12 benzene geometries, with molecule-specific energy/derivative/curvature verdict and claim-ladder rung · benzene QZ HPC resource pilot and allocation arithmetic published · **measured** \(\bar t_{\mathrm{geom}}\), peak RAM, export size · **real-cube representability**: \(\lvert\int\Delta\rho\,dV\rvert<10^{-4}\,e\) and grid-vs-analytic \(E_{ne}\), \(E_H\) agreement \(<0.1\,\)mHa · **egg-box re-measured on that real cube**, in force units · **\(\varepsilon_\theta\) anchoring fork (i) vs (ii) decided in writing** from the same cube · if \(T_{\mathrm{campaign}}\) does not fit, **shrink ladder chosen in writing** before any 2000/5000-config run | **Unblocks the H₂O campaign** and freezes the allowed precision wording. |
| **Fase 1 — H₂O PES training** | Learn $\mathbf{R}\to E,\mathbf{F},\rho$ | H₂O, ≥2,000 CCSD(T)/cc-pVTZ configs (per §5.1), $32^3$ grid | **Two independent conditions.** (a) Phase 0's engine-artifact ceiling still holds \((<0.1\,\text{meV/Å})\) — an engine artifact is a bug to be fixed, never a floor that licenses a looser gate. (b) Force RMSE below the **greater of** \(1\,\text{meV/Å}\) and \(3\times\) the measured **label** noise floor · harmonic frequencies within 5 cm⁻¹ of the CCSD(T) Hessian (the one equilibrium Hessian from §5.1, not a per-config Hessian) · **the force and frequency gates must be reconciled empirically once the model exists** — report both; a model that passes one and fails the other means the *pair* is mis-specified, and the pair gets fixed before Phase 2 · **dipole gates (round-2 issue 11), all three required before any production MD:** (i) \(\lVert\boldsymbol{\mu}_\theta-\boldsymbol{\mu}_{\mathrm{QM}}\rVert<0.01\,e a_0\) (\(\approx0.025\,\)D, \(\approx1.4\%\) of the H₂O dipole) on held-out configs; (ii) relative error in \(d\boldsymbol{\mu}/d\mathbf{R}\) \(<5\%\), since \(I\propto\lvert d\boldsymbol{\mu}/dQ\rvert^2\) and the §9 claim is *relative* envelopes at the \(\sim10\%\) level; (iii) grid artifact in \(\boldsymbol{\mu}\) under rigid translation \(<0.1\%\) of \(\lvert\boldsymbol{\mu}\rvert\) |
| **Fase 2 — Frozen-weight IR (H₂O)** | Spectral prediction with no spectral fitting | 5×50 ps MD trajectories | $\nu_1,\nu_2,\nu_3$ band centers within 10–15 cm⁻¹ of experimental gas-phase FTIR envelopes; the dipole surface was trained only on static dipoles, never on spectra or intensities |
| **Fase 3 — Physical hardness tests** | Sanity + hardness, **not** the §2 bake-off | D₂O (mass-only swap, frozen weights); CO₂ (linear, symmetric) | D₂O per-mode isotope shift consistent with theory (≈1.35–1.39) — **necessary, not flagship**; CO₂ forbidden-mode gate with a **number**: \(I(\nu_1)/I(\nu_3)<10^{-2}\), and the measured ratio must be consistent with \(\delta^2\), where \(\delta\) is the independently measured relative \(d\boldsymbol{\mu}/dQ\) error from Phase 1. A voxel grid breaks \(D_{\infty h}\), so the residual is **not** zero and “\(\approx0\)” was never a gate; if the ratio greatly exceeds \(\delta^2\) the model has learned an asymmetric density and the failure is physical, not numerical. \(\nu_2/\nu_3\) correctly active |
| **Fase 4 — Baseline benchmark** | Answer §2 under equal labels, then quantify density supervision | Same H₂O/benzene `config_id`s as P1/05 | **Owners:** 04 trains simple NN; **G1** trains MACE-EF from scratch (NequIP fallback); P1/05 train Field-EF and Field-EFρ; **08 assembles only**. **§7.1 pre-registration is a precondition** — frozen split hash, \(\ge3\) seeds, tuning parity and a declared effect size, all committed before any leg trains. **Primary gate:** leave-one-mode-out Field-EF vs MACE-EF on identical CCSD(T) energies and identical same-surface full or directional derivatives. **Controlled ablation:** Field-EFρ vs Field-EF, differing only in \(\lambda_\rho\). The full \(E/F/H/\rho\) production result is reported separately. Secondary: complete-gradient force RMSE on the held-out §5.1 set, in-domain error, harmonic error vs the one §5.1 Hessian, MD stability, cost. If G1 or Field-EF is missing, the representation test is **incomplete** — do not substitute 04 or the density-supervised production model. |
| **Fase 5 — Finale: benzene** | Aromatic generalization | C₆H₆, nominal $64^3$ / ≥5,000 configs **subject to the §5.1 pilot and shrink ladder**, 20 ps forward MD | Aromatic ring/C–H modes within 15 cm⁻¹ of one fixed gas-phase NIST FTIR dataset. If rung 4 of the shrink ladder fired, this phase is outlook — do not keep the nominal \(N\) as a scored promise |
| *(Outlook only, not scored)* | OOD transferability discussion | Naphthalene (C₁₀H₈) via atomic density superposition, zero-shot | Discussed as an exploratory result in the thesis, explicitly **not** a pass/fail milestone |

**Gate unit discipline (round-2 issue 8).** Every artifact tolerance above is quoted in **force units**, because that is the unit the acceptance gates are in. An artifact quoted in Hartree is a force tolerance in disguise: a cell-periodic energy artifact of peak-to-peak amplitude \(A\) and period \(\Delta x\) implies a peak force artifact \(\pi A/\Delta x\). The conversion, and the derivation of each number from the Phase 1 acceptance gate, is in [probes/issue08_gate_consistency.py](../probes/issue08_gate_consistency.py) — re-run it rather than re-deriving by hand if \(\Delta x\), the trajectory length, or the acceptance gate ever changes. Energy drift is likewise budgeted over the **production trajectory length** against \((3N-6)k_BT\), not quoted as a rate in isolation: the old \(10^{-5}\,\)Hartree/ps allowed the 50 ps H₂O run to lose 18% of the vibrational energy it is supposed to be holding.

### 7.1 Pre-registration of the §2 comparison (resolves round-2 blocking issue 13)

§2 is currently falsifiable in wording only. A comparison between a bespoke architecture and a mature, author-tuned package is not an experiment until the following are fixed **in a commit that predates any leg of the comparison being trained**. All of it is free; none of it is recoverable afterwards.

**1. Frozen splits.** One file per campaign, `splits/{molecule}_{version}.json`, containing train / validation / test `config_id`s and the held-out mode family for the leave-one-mode-out test. Committed and tagged; its hash appears in every gate report from P1, 05, G1 and 04. Every leg reads that file — nobody re-splits.

**2. Models, seeds and error bars.** The comparison cohort is frozen as MACE-EF, Field-EF and Field-EFρ (§6.3), with minimum **3 seeds per model per split**. The primary metric is reported as mean ± SD across seeds. A single-seed number is not a result. The full \(E/F/H/\rho\) production model is outside this causal cohort and is labeled separately in every table.

**3. Tuning parity.** Equal hyperparameter budget: same number of trials and same wall-clock budget for Field-EF and MACE-EF, tuned on the **validation** split only. MACE starts from its authors' recommended recipe as trial 0 — an untuned competitor is a straw man and a reviewer will say so. Field-EF starts from its §6.1 default. After those hyperparameters are frozen, Field-EFρ reuses the selected Field-EF architecture and training schedule; only \(\lambda_\rho\) is enabled, so the density ablation does not become a second unequal search. Trial count and budget go in the gate report.

**4. Pre-registered effect size.** Primary metric: the ratio \(r=\mathrm{RMSE}^{F}_{\text{Field-EF}}/\mathrm{RMSE}^{F}_{\text{MACE-EF}}\) on the held-out mode family. Declared in advance:

| Outcome | Condition |
|---|---|
| field wins | \(r<1-\Delta\) with non-overlapping \(\pm1\) SD |
| GNN wins | \(r>1+\Delta\) with non-overlapping \(\pm1\) SD |
| **inconclusive** | otherwise |

\(\Delta\) is provisionally \(0.10\) and is finalized as \(3\times\) the measured within-model seed scatter **on the validation split**, before either model is evaluated on the held-out mode family. Setting \(\Delta\) from validation scatter is legitimate; setting it after seeing the comparison is not. **“Inconclusive” is a publishable outcome and must be reported as such** — the thesis question is whether the field representation transfers better, and “we could not tell” is an honest answer to it.

The density-supervision effect is the matched ratio \(r_\rho=\mathrm{RMSE}^{F}_{\text{Field-EFρ}}/\mathrm{RMSE}^{F}_{\text{Field-EF}}\), reported with the same seeds and held-out family. It is secondary and does not replace the primary equal-label test.

**Allowed conclusions are frozen:**

| Result | Defensible conclusion |
|---|---|
| Field-EF beats MACE-EF | Evidence supporting the field-representation hypothesis under equal \(E/F\) supervision |
| Field-EF does not beat MACE-EF, but Field-EFρ does | The density-supervised field pipeline wins; representation alone is not established |
| Neither field leg beats MACE-EF | No demonstrated transfer advantage over the equivariant GNN |
| Any comparison lies within the effect-size margin | Inconclusive |

The full production model may be the best spectroscopic system, but its result is never substituted into the first row.

**5. Confounds registered in advance.** Named now so they cannot be discovered as excuses later: (a) MACE is exactly rotation-equivariant and the field model is not (§8 item 13 — both invariance residuals published **before** the bake-off); (b) tuning-maturity asymmetry; (c) equal training-data volume and identical \(E/F\) labels for the primary test; (d) density supervision is privileged information and appears only in the explicitly secondary Field-EFρ ablation; (e) which §6.1 anchoring fork and which §2.1 fallback rung the field model used; (f) whether the §5.1 shrink ladder fired.

**6. Analysis frozen.** Metric, aggregation over seeds, and the comparison plot are specified before test evaluation. No post-hoc metric shopping.

**7. The test set is touched once.** The held-out mode family is evaluated once per model, at the end. Any re-evaluation must be disclosed with its reason in the gate report.

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
