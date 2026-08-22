# Distilled Final Project Plan & Quality Checks

**Source material:** This document is distilled from the full, multi-round conversations in [gemini_chat_2.md](AI_Chats/gemini_chat_2.md) and [grok_chat_2.md](AI_Chats/grok_chat_2.md), cross-checked against the earlier exploratory conversations [gemini_chat_1.md](AI_Chats/gemini_chat_1.md) and [grok_chat_1.md](AI_Chats/grok_chat_1.md). It reconstructs the plan as it stood after the "strict professor" critique loop: the plan was drafted with Gemini, stress-tested by Grok, revised, re-submitted to Grok, and — after a final, very harsh 23-point external review (pasted into both chats) — reworked one last time. **Gemini's final response to that 23-point review is the most advanced, self-consistent version of the plan and is treated here as the definitive baseline.** Grok's conversation ends one step earlier (agreeing the 23 points must be addressed, without yet seeing the reworked plan), so where the two diverge, the later Gemini revision supersedes the earlier Grok-approved version.

---

## 1. Evolution of the Plan (why it looks the way it does)

1. **Origin idea** ([gemini_chat_1.md](AI_Chats/gemini_chat_1.md)): predict IR spectra of large aromatic molecules using an AI-discovered cellular-automaton update rule, applicable to any molecule, trained/validated/tested only on chemically precise (non-DFT) data. First framed as a Graph Cellular Automaton (GNCA) reading out a Hessian.
2. **Grid over graph** ([gemini_chat_2.md](AI_Chats/gemini_chat_2.md)): switched to a continuous 3D spatial grid (voxels), because free-space photon propagation and continuous electron density don't map naturally onto a graph.
3. **First full plan** submitted to Grok as "strict professor": **rejected**. Fatal flaw — the architecture only propagated the *electron density* over a *static* nuclear grid, which produces electronic (UV/Vis) dynamics, not vibrational IR dynamics.
4. **Revision 1 — dynamic nuclei**: added explicit classical point-nuclei with Velocity-Verlet integration, coupled to the electron-density grid (Grid-to-Particle / Ehrenfest-like coupling). Grok gave **conditional green light**, then tightened it further into a formal energy/force-consistency requirement (Born-Oppenheimer/adiabatic choice, Gaussian nuclear densities, analytic Hellmann-Feynman-consistent forces). Grok then gave **unconditional green light** — followed immediately by a literature check confirming the combination is novel (closest prior art: V2Rho-FNO, which only maps geometry→density, with none of the MD/force/spectral machinery).
5. **The harsh 23-point external review** (pasted into both chats verbatim): identified that the "conditional green light" plan still had a fundamental gap — a network that only learns density does **not** automatically yield a conservative force field/PES — plus ~22 other concrete methodological weaknesses (spectral resolution too short, egg-box not eliminated, periodic Poisson boundary artifacts, too little training data, spectral loss risks reward-hacking the spectrum instead of the physics, no baseline comparison, naphthalene zero-shot oversold, etc.).
6. **Final revision** (end of [gemini_chat_2.md](AI_Chats/gemini_chat_2.md)): a ground-up restructuring that resolves all three non-negotiables the reviewer (and both AI "professors") converged on. Sections 1–9 below reconstruct that baseline.
7. **Architecture lock (2026-08-22):** professor-review blocking issue 2 required an *implementable* \(E=\mathcal{E}[\rho,R]\) (not a slogan), deletion of leftover complex-density / EM channels, and a split of jobs between the fixed Hockney–Eastwood solver and the learned FNO. That lock is written into §3, §4, and §6 below. The Gemini baseline remains the source for everything else.
8. **Data-generation method (2026-08-22):** professor-review blocking issue 3 required replacing “exact CCSD(T) density/forces/Hessian via PySCF” with a recipe (which 1-RDM, which force, how many Hessians), a measured 10-geometry cost pilot as a Phase 0 exit, a shrink ladder if the campaign does not fit local hardware, and a Phase 1 force gate that sits above the measured noise floor. That lock is written into §5.1 and §7 below.
9. **Goal lock (2026-08-22):** professor-review blocking issue 4 required the prime directive to stop promising “chemically precise spectral lines” / “sub-wavenumber” as a this-thesis claim. [Overarching_Goal.md](Overarching_Goal.md) now splits **labels** (CCSD(T)/cc-pVTZ per §5.1) from **spectra** (§9 band envelopes). Horizon PAH work is post-master’s Projects 10–12, not Module 08.
10. **Baseline lock (2026-08-22):** professor-review blocking issue 6 required the GNN competitor to live on the critical path, not in Module 08. Mapping [§4.2 Workstream G1](Capstone_Mapping.md#42-workstream-g1--equivariant-atomistic-pes-resolves-professor-review-blocking-issue-6) trains MACE from scratch on the **same** P1/05 split manifests. Module 08 **assembles**. D₂O (Phase 3) is a **sanity check**, not the flagship proof that the field representation learned physics. The §2 test is leave-one-mode-out transfer vs G1.
11. **Density-representation lock (2026-08-22):** [round-2](Professor_Review_2026-08-22_Round2.md) blocking issue 7 showed the grid cannot carry an all-electron density at \(\Delta x\approx0.2\,\text{Å}\), and issue 10 showed \(\Phi\) was a nuclear-identity bypass channel in \(\varepsilon_\theta\). §3, §5.1, §6.1, §6.2, §6.3, §7 and §8 below now specify a **reference split**: an analytic promolecular density carries the cusps, only the smooth deformation density \(\Delta\rho_\theta\) touches the voxel grid, and \(\varepsilon_\theta\) sees density-derived local scalars only.
12. **Gate lock (2026-08-22):** round-2 blocking issue 8 showed the Phase 0 tolerances (quoted in Hartree) and the Phase 1 acceptance gate (quoted in meV/Å) were mutually inconsistent by two orders of magnitude, and that feeding engine artifacts into the Phase 1 “noise floor” made that gate **self-loosening**. §5.1 and §7 now derive every artifact tolerance *from* the acceptance gate, in force units, and admit only irreducible **label** scatter into the noise floor.
13. **Observable and invariance lock (2026-08-22):** round-2 blocking issues 11 and 12 — the IR observable (\(\boldsymbol{\mu}\), \(d\boldsymbol{\mu}/d\mathbf{R}\)) was never trained or validated and the CO₂ gate had no number; and no gate covered the fact that a voxel grid is neither translation- nor rotation-invariant. §6.4, §7 and §8 now carry dipole gates before any production MD, a numeric CO₂ forbidden-mode gate, and an explicit invariance budget.
14. **Prior-art and pre-registration lock (2026-08-22):** round-2 blocking issue 9 — the novelty check missed the machine-learned orbital-free DFT lineage that this architecture belongs to; §2.1 now positions against it and pre-registers a fallback if the local \(\varepsilon_\theta\) stalls. Round-2 blocking issue 13 — the §2 comparison was falsifiable in wording only; §7.1 now fixes splits, seeds, tuning parity, effect size and confounds **before** any leg trains.

---

## 2. Central Research Question (final formulation)

> "Does a continuous 3D neural field representation of the electron density (FNO-NCA), via a hybrid Fourier Neural Operator – Neural Cellular Automaton, yield a more physically transferable, energy-conserving Potential Energy Surface (PES) than existing atomistic equivariant Graph Neural Networks — from which molecular vibrational/infrared bands emerge via classical molecular dynamics?"

This replaced the original, much broader claim ("can an AI find a universal CA update rule that predicts chemically precise IR lines of arbitrarily large PAHs"), which both professors judged too broad and not falsifiable enough for a master's thesis.

**Core hypothesis:** representing electrons as a continuous 3D field (rather than pairwise atom-centered distances, as in GNNs) should capture non-local charge delocalization and π-polarization more faithfully, giving better transferability to unseen vibrational modes.

### 2.1 Prior art this thesis must be positioned against (resolves round-2 blocking issue 9)

The original novelty check was run inside two chatbot conversations and returned V2Rho-FNO as the closest prior art. That was wrong, and the error is structural rather than bibliographic: \(E=E_{\mathrm{es}}[\rho]+\int\varepsilon_\theta\,dV\) with \(\rho\) predicted from \(\mathbf{R}\) **is machine-learned orbital-free DFT**, a field with a fifteen-year record. See [Relevant_Scientific_Papers.md](Relevant_Scientific_Papers.md) items 21–25.

**The closest functional prior art is Brockherde et al. (2017)**, not V2Rho-FNO. They learn the density–potential *and* energy–density maps and then reproduce energies across MD-generated geometries — \(\mathbf{R}\to\rho\to E\) plus dynamics, at DFT label quality. A Module 09 examiner needs one question to reach that paper. Own it first.

**What is therefore *not* novel here:** an ML functional of \(\rho\) (2012); bypassing the KS equations with a learned \(\mathbf{R}\to\rho\) map (2017); running MD on such a model (2017); size-extrapolation of a density-based functional (M-OFDFT, 2024).

**What is left, stated plainly:** the *combination* of (a) CCSD(T)/cc-pVTZ labels rather than DFT labels, (b) a conservative field PES with forces by autograd through \(\rho_\theta\) rather than a fitted energy map, (c) IR band envelopes as a frozen-weight emergent readout, and (d) a **pre-registered** field-vs-equivariant-GNN transfer test (§7.1). If a reviewer removes (d), what remains is an incremental variation on a populated field. That is the honest framing, and it is still a thesis.

**The transferability risk this literature makes explicit.** Teller's theorem (1962) says molecules do not bind at all in pure Thomas–Fermi theory — a purely *local* functional of \(\rho\). Semilocal gradient corrections improve this without resolving it, and M-OFDFT (2024) reports that **essential non-locality** had to be built into the functional, via density expansion coefficients in an atomic basis, to reach KS-DFT accuracy on molecules. The Distilled Plan proposes to test “field representations transfer better” using \(\varepsilon_\theta(\rho,\lvert\nabla\rho\rvert)\) — precisely the functional form the field knows transfers worst.

This is defensible, but only with the argument written down: \(\varepsilon_\theta\) here is **not** a universal KEDF. It is an interpolator over a narrow manifold (one molecule, thermally accessible geometries, \(\ge2000\) configurations), where systematic errors largely cancel between nearby geometries. The §6.1 reference split reduces what it must supply from \(\sim76\,\)Ha to the bonding remainder, \(\sim1\,\)Ha. Those two facts are the whole defense; if either fails, so does the form.

**Pre-registered fallback (declare now, not after Phase 4).** If the local \(\varepsilon_\theta\) misses the Phase 1 gates, the correct inference is *“this functional form is insufficient”*, **not** *“the field hypothesis is falsified”*. Escalate in this order, and record which rung was used in every downstream claim:

1. Local \(\varepsilon_\theta(\rho_{\mathrm{ref}},\Delta\rho_\theta,\lvert\nabla\Delta\rho_\theta\rvert)\) — the §6.1 default. Smallest object that makes the equation true.
2. Switch the §6.1 anchoring fork (vanishing anchor ↔ difference form) before adding capacity.
3. **Non-local \(\varepsilon_\theta\):** let the functional see non-local density features (the encoder's FNO block, or attention over density descriptors). This is the M-OFDFT lesson, applied.
4. Atomic-basis expansion coefficients as the density representation instead of voxels. This is a different thesis and is **outlook**, not a rung to be taken quietly in month five.

Only after rung 3 fails may the §2 claim be reported as negative for field representations. A negative result at rung 1 is a result about \(\varepsilon_\theta\), and must be reported as such.

---

## 3. What the Project IS

- **A differentiable molecular-dynamics simulator**: explicit classical nuclei (positions $\mathbf{R}_A$, velocities $\mathbf{V}_A$, mass $M_A$, charge $Z_A$) coupled to a continuous 3D electron-density field $\rho(\mathbf{r})$ living on the same grid.
- **Energy-first (Route B) architecture**: the *only* scalar energy is the functional in §6, $E_\theta(\mathbf{R})=\mathcal{E}[\rho_\theta(\mathbf{r};\mathbf{R}),\mathbf{R}]$. There is no second energy head. Forces are obtained by **exact automatic differentiation**, $\mathbf{F}_A = -\partial E_\theta/\partial \mathbf{R}_A$, which *guarantees* $\oint \mathbf{F}\cdot d\mathbf{R} = 0$ and $\nabla_\mathbf{R}\times\mathbf{F}=0$ (conservative forces), unlike the earlier density-first design. The 3D density is the argument of \(\mathcal{E}\) and a supervised target; it is not differentiated by itself to produce forces.
- **A hybrid FNO-NCA *density encoder***: local $3\times3\times3$ NCA convolutions handle short-range structure in \(\rho_\theta\); an optional learned FNO is a non-local mixer **inside the encoder only**. Long-range \(1/r\) electrostatics in the *energy* are **not** learned — they come from the fixed Hockney–Eastwood solver in \(E_{\mathrm{es}}\) (§6). A purely local CA would need ~60+ steps just to propagate charge information across one aromatic ring; that is why the encoder may use an FNO. It is not a reason to replace the Poisson kernel.
- **Isotope shift as a required sanity check, not the flagship representation proof**: because atomic mass $M_A$ enters only the classical Newtonian/Verlet integration step (not the learned network), the frozen, already-trained model must reproduce the H₂O → D₂O red-shift correctly with **zero retraining**, purely from $\mathbf{F}/M_A$. Almost any vaguely correct PES will do this. The test that answers §2 is **leave-one-mode-out transfer vs Workstream G1** (same splits), not D₂O.
- **Emergent spectroscopy, not trained spectroscopy**: the network is trained *only* on static configurations (energies, forces, Hessians, densities). Once trained and frozen, it runs forward-only classical MD for tens of picoseconds; the IR spectrum is obtained via FFT of the dipole autocorrelation function purely as a **blind post-hoc prediction**, never as a training signal.
- **Strictly non-DFT *energies and (default) forces*** for every pipeline target (see §5.1). The density target is the pinned 1-RDM recipe, not a slogan “exact CCSD(T) density.” A cheaper density proxy is allowed only via the §5.1 shrink ladder and must invoke the Overarching Goal escape clause.
- **Rigorously phased**, with hard numerical Go/No-Go gates between phases (§7), scoped to what is achievable in a ~6–7 month master's thesis on local consumer hardware, with supercomputer time reserved only for later-phase scaling.
- **Grid/channel representation** (Born–Oppenheimer; real density only): \(N\times N\times N\) voxel grid, \(\Delta x \approx 0.20\)–\(0.25\,\text{Å}\), carrying the **deformation** density only (see the reference split below).
  - **Keep:** one real, *sign-changing* deformation channel \(\Delta\rho_\theta\) with \(\int\Delta\rho_\theta\,dV=0\) enforced by mean subtraction on every forward pass; total positivity \(\rho_{\mathrm{ref}}+\Delta\rho_\theta\ge0\) as a **monitored diagnostic plus soft penalty**, not a hard constraint; a handful of latent NCA memory channels, labeled as hidden state.
  - **Delete:** \(\rho_{Re},\rho_{Im}\) and \(E_x,E_y,E_z\). Those are fossils of the rejected Ehrenfest / photon / complex-wavefunction story. A BO PES has no EM grid and no imaginary density. The IR dipole \(\boldsymbol{\mu}=\int\mathbf{r}\,(\rho_{\mathrm{nucl}}-\rho_{\mathrm{tot}})\,dV\) reduces **exactly** to \(\boldsymbol{\mu}=-\int\mathbf{r}\,\Delta\rho_\theta\,dV\), because a promolecule of neutral spherical atoms has identically zero dipole. The graded observable is therefore a direct integral of the object that is actually supervised, not a residue of two much larger numbers (physical cancellation ratio \(\approx7\times\) for H₂O). Under the old representation it was worse than a cancellation problem: the grid density carried \(+1.14\,e\) of net charge, so the “dipole” was not even origin-independent ([probes/issue11_12_observable_and_invariance.py](../probes/issue11_12_observable_and_invariance.py)).
  - **Also deleted:** \(\mathrm{softplus}\)-and-renormalize-to-\(N_e\). That scheme is what pushed the unrepresentable core charge into the valence region. A deformation density is negative in depleted regions; \(\mathrm{softplus}\) is the wrong sign structure.
- **Reference split (resolves round-2 blocking issue 7):** the physical density is \(\rho_{\mathrm{tot}}=\rho_{\mathrm{ref}}+\Delta\rho_\theta\), where \(\rho_{\mathrm{ref}}(\mathbf{r};\mathbf{R})=\sum_A\rho^{\mathrm{atom}}_{Z_A}(|\mathbf{r}-\mathbf{R}_A|)\) is a **promolecular** superposition of spherically averaged free-atom ground-state densities, fitted once per element to a short sum of spherical Gaussians and then frozen. \(\rho_{\mathrm{ref}}\) carries the core cusps and is integrated **analytically**; the grid never sees it. This is not a convenience: measured on an all-electron H₂O model density ([probes/issue07_grid_representability.py](../probes/issue07_grid_representability.py)), putting \(\rho_{\mathrm{tot}}\) on a \(0.20\,\text{Å}\) grid gives an \(11\%\) electron-count error (§8 item 9 demands \(0.01\%\)) and a rigid-translation energy artifact of \(3.8\,\text{Hartree}\) per grid cell; the same measurement on \(\Delta\rho\) alone gives \(3\times10^{-10}\,e\) and \(1.2\times10^{-9}\,\text{Hartree}\).

---

## 4. What the Project is explicitly NOT

- **NOT a Graph Neural Network**: no discrete atom-nodes, bond types, or hard-coded per-element sub-networks (rejecting the SchNet/PhysNet/MLAtom/ANI-1 style architecture). One single universal update rule / energy functional must work for any element purely from local field values (charge density, potential gradients), the way physical law itself doesn't have separate equations per bond type.
  - **Stated concession (round-2 issue 7):** the promolecular reference \(\rho_{\mathrm{ref}}\) *is* element-specific. It is not a learned per-element sub-network — it is a physical constant of nature (the free-atom ground-state density), entering on the same footing as \(Z_A\), which this plan already allows. All **learned** content (\(\Delta\rho_\theta\), \(\varepsilon_\theta\)) still sees only fields. Extending to a new element costs one atomic calculation, not retraining. Say this in the Module 05 report and in the Module 09 defense rather than leaving it to be discovered.
- **NOT Kohn–Sham DFT, and NOT DFT-quality labels**: no approximate exchange-correlation functionals (B3LYP, PBE, M06-2X, etc.), which are known to make systematic errors on dispersion and aromatic π-delocalization. This exclusion applies to every input and every target dataset, with no exceptions planned. Note the distinction the heading now makes explicit (round-2 issue 9): \(E=\mathcal{E}[\rho]\) with a learned \(\varepsilon_\theta\) *is* a density-functional theory — an orbital-free one — and §2.1 positions it in that literature. What is excluded is **library XC functionals** and **DFT-level labels**, not the Hohenberg–Kohn *shape*, which is the research claim. Do not let the old “NOT DFT” slogan reach a Module 09 examiner; it is a free kill.
- **NOT a purely local Cellular Automaton**: a plain $3\times3\times3$ convolution cannot resolve long-range structure in \(\rho\) in a trainable number of steps — the density encoder may use a learned FNO. Isolated-molecule \(1/r\) electrostatics in the energy are still the **fixed** Hockney–Eastwood kernel, not a learned Poisson layer.
- **NOT a multi-head regressor with auxiliary density**: the network must not emit a scalar \(E\) from pooled latents that can ignore \(\rho\), with \(L_\rho\) as a regularizer. That tests "3D CNN vs SOAP," not the field-functional hypothesis. There is no energy head that can see \(Z_A\), one-hot elements, bond lists, or raw \(\mathbf{R}\) except through the fields in §6.
- **NOT density-first / density-as-force-source (Route A, rejected)**: the density network is *not* differentiated by itself to obtain forces. Forces are \(-\partial\mathcal{E}[\rho_\theta,\mathbf{R}]/\partial\mathbf{R}_A\). That earlier approach cannot guarantee conservative forces and was identified as the single biggest conceptual flaw in the pre-final version of the plan.
- **NOT trained on a spectral loss**: the earlier Wasserstein-distance-on-spectrum training loss was **deliberately removed**. Training only on energy/force/Hessian/density supervision prevents the network from "cheating" — learning a dynamics that superficially matches peak positions via compensating errors rather than a physically correct PES.
- **NOT a periodic/naive FFT-Poisson solver**: standard periodic $4\pi/k^2$ Poisson solving would make an isolated molecule spuriously interact with its periodic images. An explicit open/isolated boundary treatment (Hockney–Eastwood truncated Coulomb kernel with zero-padding) is required.
- **NOT claiming elimination of the egg-box effect, only its control**: Gaussian nuclear smearing (width $\sigma \geq 1.5\,\Delta x$) *reduces* grid-discretization artifacts; it does not eliminate them, and must be empirically verified (§7, Phase 0), not assumed.
- **NOT a quantum-computing project**: quantum computing was explicitly investigated (see [grok_chat_1.md](AI_Chats/grok_chat_1.md) and the corresponding discussion in [gemini_chat_2.md](AI_Chats/gemini_chat_2.md)) and rejected as a dead end **in the current NISQ hardware era** — noise, limited qubit counts, and shallow achievable circuit depth make it strictly worse than classical HPC (PySCF/PyTorch on GPU) for every relevant sub-task today. This is a "not now," not a permanent architectural objection.
- **NOT claiming chemically precise spectra for large PAHs as the core deliverable.** The original ambition (arbitrarily large PAHs, e.g. up to C₄₈–C₆₀, at chemical precision) was explicitly downgraded after Grok called it "a PhD proposal disguised as a master's thesis." Large PAHs are, at most, a discussion-chapter outlook.
- **NOT claiming quantum-mechanical rovibrational line-list precision.** Comparing an FFT of a classical MD dipole trajectory directly against a line list like ExoMol/POKAZATEL (which encodes true quantum rovibrational transition intensities, $I_{i\to f}\propto|\langle f|\mu|i\rangle|^2$) is explicitly rejected as "apples-to-oranges." The only defensible claim is reproduction of **vibrational band positions and relative spectral envelopes/intensities**, not individual high-resolution quantum lines.
- **NOT treating naphthalene (or anything beyond benzene) as a success criterion.** Naphthalene via atomic-density superposition is kept **only** as an exploratory, out-of-distribution (OOD) zero-shot transferability test to discuss, never as a pass/fail milestone — because it requires modeling fused-ring π-delocalization the model was never trained on.
- **NOT requesting supercomputer (Snellius/UvA) time up front.** All architecture development and the H₂O/D₂O/CO₂/benzene phases are done locally; an HPC application is only justified retroactively, once the local proof-of-concept demonstrably works — this was an explicit, deliberate project-management choice, not a fallback.
- **NOT skipping baseline comparisons.** The plan explicitly requires benchmarking against (1) a conventional equivariant atomistic ML PES (e.g. MACE/NequIP/Allegro-style), (2) a simple non-field NN energy model, and (3) harmonic Hessian/finite-difference CCSD(T) — otherwise there is no evidence the 3D density field buys anything over cheaper atomistic methods.

---

## 5. Data Pipeline (strictly non-DFT)

| Molecule(s) | $t=0$ input generation | Target / validation data |
|---|---|---|
| H₂O, CO₂ | One PySCF campaign per §5.1: CCSD(T)/cc-pVTZ **energy**; density and forces from the pinned recipe (not “exact CCSD(T) everything”); Hessian only at selected stationary points | ExoMol (POKAZATEL line list), HITRAN/HITEMP — used only for final blind spectral comparison, never as training loss |
| C₆H₆ (benzene) | Second PySCF campaign per §5.1. Nominal target **≥5,000** configs on a **64³** export grid — a target, not a promise, until the 10-geometry cost pilot exits Phase 0 | NIST Chemistry WebBook gas-phase FTIR (one specific dataset/resolution must be fixed as the benchmark) |
| Large PAHs (outlook only) | Atomic Density Superposition: pre-computed CCSD(T) C–H/C–C fragment densities from benzene, spatially superposed at target atom coordinates, renormalized to exact electron count, relaxed with one Poisson update | NASA PAHdb (matrix-isolated experimental FTIR, Ar/Ne, ~10 K) with an explicit matrix-shift correction (2–15 cm⁻¹, per Boersma et al.) — outlook/discussion only |

Training-set sizing (revised upward after the 150-configuration training set was judged "far too small" for a model that must reproduce density, forces, multiple modes, and MD stability): **≥2,000 configurations for H₂O**, **≥5,000 for benzene** as *nominal* campaign sizes, sampled via normal-mode displacements (harmonic and anharmonic amplitudes), random thermal displacements (100–600 K), and rigid rotations/translations (augmentation) — split by configuration, not by random points drawn from near-identical trajectories, and including leave-one-mode-out validation. Rigid rotations/translations augment **inputs**; they are not extra QM jobs and do **not** count toward the 2000/5000 CCSD(T) budget. If the §5.1 pilot says the nominal \(N\) does not fit, take the shrink ladder — do not keep the number as a scored promise.

### 5.1 Data-generation method (resolves professor-review blocking issue 3)

A level of theory plus a count is not a method. This subsection is the method. Code-path cells are filled after a one-geometry smoke test; scientific defaults are locked now.

**One campaign, two products (H₂O).** The same H₂O geometries feed Module 04 (descriptor CSV: \(R,E,F\)) and Workstream P1 (volumetric \(\rho,E,F\), selected \(H\)). Benzene is a **second** campaign for Module 05. Module 06 stays off this path.

#### Scientific defaults (lock now)

| Quantity | Default | Why |
|---|---|---|
| Energy | **CCSD(T)/cc-pVTZ**, frozen-core, one geometry convention (Å vs Bohr) everywhere | This is the precision claim. |
| Density target \(\rho\) | **Relaxed CCSD 1-RDM**, mapped onto the same real-space grid as §6, renormalized to \(N_e\) | A unique CCSD(T) density is often not what the code returns. Supervising \(\rho\) on a CCSD relaxed density while \(E\) is CCSD(T) is a **documented density-level gap**, not a silent DFT sneak-in. If a verified CCSD(T) density path exists in the *pinned* PySCF, use it and write that in the manifest. If only an *unrelaxed* CCSD 1-RDM is available, that is the fallback — the manifest must say **unrelaxed**. Never write “exact CCSD(T) density” unless the smoke test produced one. |
| Forces | **Analytic CCSD(T) gradients if the smoke test returns them.** Else analytic **CCSD** gradients (energy still CCSD(T)). Else **central finite-difference of CCSD(T) energies**, H₂O only. | Benzene finite-difference forces (12 atoms × 2 × \(E_{\mathrm{CCSD(T)}}\)) are the thing most likely to kill Module 05. Do not plan them as the default. |
| Hessians | **Not per config.** Equilibrium geometry only at first: **1 H₂O** + **1 benzene** Hessian, by finite-difference of the *same* force recipe used above. Add more stationary points only if the first Hessian is cheap enough that \(L_H\) is not the long pole. | “Selected stationary points” now has a count. |

#### Code path is a decision procedure, not a wish

**Step 0 — pin.** One PySCF version, one basis (`cc-pVTZ`), one SCF/CC convergence, one grid for exporting the density (the §6 grid, not a mysterious default cube), and **one frozen set of per-element atomic reference fits** (§6.1 step 0), each accepted only if \(\int\lvert\rho^{\mathrm{fit}}_Z-\rho^{\mathrm{atom}}_Z\rvert\,dV\,/\,Z<10^{-3}\). The campaign exports \(\Delta\rho=\rho_{\mathrm{QM}}-\rho_{\mathrm{ref}}\), **not** raw \(\rho\); the raw cube is retained for one geometry per molecule as a Phase 0 diagnostic, never as the training target.

**Step 1 — one-geometry smoke test (H₂O, then benzene).** For each molecule, record pass/fail for: energy, 1-RDM, analytic gradient, Hessian. This table lives in the campaign manifest and is filled with numbers, not “via PySCF.”

**Step 2 — 10-geometry cost pilot (benzene and H₂O).** This is a **Phase 0 exit criterion**, before P1 training and before promising Module 05 \(N=5000\). Measure, per geometry:

- wall time and peak RAM for \(E\), \(\rho\), \(F\)
- whether analytic \(F\) existed
- export size of one \(64^3\) (and \(32^3\)) tensor

Then write the only budget that counts:

\[
T_{\text{campaign}} \approx N_{\text{geom}}\times \bar t_{\text{geom}}
\]

No A100 folklore. If \(T\) does not fit local hardware on a calendar that can be lived with, do **not** start the 5000-config run. Take the shrink ladder.

Every row in the campaign manifest gets: `theory_energy`, `theory_density`, `theory_force`, `rdm_relaxed|unrelaxed`, `pyscf_version`, `grid`, `ref_fit_id`, `wall_s`, `max_rss_gb`. If those fields are blank, it is not a dataset.

#### Shrink ladder (in the plan *before* the pilot)

Stop at the first rung that fits:

1. Cut benzene \(N\) (5000 → 2000 → 1000). Keep CCSD(T) energies and the density recipe above.
2. Store benzene \(\rho\) on \(32^3\) (or downsample after a finer QM cube). Training grid and QM cube may differ if the export method is written down.
3. **Density proxy, energy/force still CCSD(T):** \(\rho\) from HF or a documented DFT *density only*. This is a real precision exception and **must** use the Overarching Goal escape clause. Allowed only if the smoke test / pilot shows CCSD densities are the long pole. Module 06-style “it’s just sampling” does **not** cover this.
4. **Benzene field campaign becomes outlook.** Module 05 must then be remapped. Do not keep “≥5000 benzene CCSD(T) volumes” as a scored promise.

H₂O (2000 configs, \(32^3\), 3 atoms) is assumed cheaper. If the *H₂O* pilot already fails, the field thesis is locally infeasible: **stop before P1**, not after.

#### Density-representation ladder (round-2 issue 7)

Separate from the cost ladder. Fires if the Phase 0 real-cube test shows \(\Delta\rho\) is still not grid-representable — i.e. if its narrowest feature is sharper than \(\approx1.25\,\Delta x\), which the [issue-7 probe](../probes/issue07_grid_representability.py) measures as the point where the translation artifact crosses \(1\,\text{meV/Å}\). Stop at the first rung that works:

1. \(\Delta x\to0.15\,\text{Å}\) for the \(\Delta\rho\) grid only.
2. Add a per-element **core-relaxation** term: one extra spherical Gaussian per atom whose coefficient is learned. Integrals stay analytic; the grid stays smooth.
3. Small-core **ECP**, valence-only density. Labels become CCSD(T)/cc-pVTZ-PP — a real change to the label level, so this rung **requires the Overarching Goal escape clause**.
4. H₂O-only field model; the benzene field becomes outlook. (Same destination as rung 4 of the cost ladder above — if either ladder reaches its last rung, Module 05 is remapped.)

#### Force gate sits above *label* noise, not above engine bugs (revised, round-2 issue 8)

The Phase 1 force Go/No-Go is not a chat number — and it is not a number that may be relaxed by the engine's own defects. Two categories, never mixed:

| Category | Examples | Status |
|---|---|---|
| **Engine artifact** | egg-box residual, autograd-vs-FD mismatch, Poisson boundary error, quadrature error | A **bug with a ceiling**. Fix it. It never enters the noise floor. |
| **Label noise** | scatter of a 5-point repeated CCSD(T) (or FD) force on one fixed H₂O geometry | Irreducible property of the data. **Only this** may loosen the gate. |

The original formulation — \(\max(1\,\text{meV/Å},\,3\times\text{noise floor})\) with the egg-box residual *inside* the noise floor — is circular: a worse engine buys a looser gate. Arithmetic in [probes/issue08_gate_consistency.py](../probes/issue08_gate_consistency.py): the old \(10^{-4}\,\)Ha egg-box tolerance implies a \(42.7\,\text{meV/Å}\) force artifact, which would have set the effective Phase 1 gate at \(128\,\text{meV/Å}\) — \(128\times\) looser than the stated target, and irreconcilable with the \(5\,\text{cm}^{-1}\) harmonic gate in the same table row.

**Replacement, derived rather than asserted.** A cell-periodic artifact of peak-to-peak amplitude \(A\) and period \(\Delta x\) implies a peak force artifact \(\pi A/\Delta x\). Requiring the total engine artifact to sit a factor of 10 below the acceptance gate gives:

- **Engine artifact ceiling:** \(<0.1\,\text{meV/Å}\) \((1.9\times10^{-6}\,\text{a.u.})\), which back-converts to an egg-box energy tolerance of \(2.3\times10^{-7}\,\)Ha at \(\Delta x=0.20\,\text{Å}\) — \(427\times\) tighter than the old number.
- **Phase 1 acceptance gate:** force RMSE \(<\max\big(1\,\text{meV/Å},\ 3\times\text{label noise floor}\big)\).

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

$$L_{train} = \lambda_E L_E + \lambda_F L_F + \lambda_H L_H + \lambda_\rho L_\rho$$

- $L_E$: MSE on total energy vs. CCSD(T).
- $L_F$: MSE on per-atom forces vs. the §5.1 force recipe (analytic CCSD(T) if the smoke test returns it; else analytic CCSD; else H₂O-only finite-difference of CCSD(T) energies).
- $L_H$: Hessian supervision at the **counted** stationary points in §5.1 (1 H₂O + 1 benzene equilibrium Hessian first). Force-only supervision does **not** guarantee correct 2nd/3rd-order PES derivatives.
- $L_\rho$: MSE on the **deformation** density \(\Delta\rho=\rho_{\mathrm{QM}}-\rho_{\mathrm{ref}}\), where \(\rho_{\mathrm{QM}}\) is the §5.1 density target (default: relaxed CCSD 1-RDM, not a slogan “exact CCSD(T) density”). This supervises the *argument* of \(\mathcal{E}\); it is not an optional extra head and not the force source. Supervising \(\Delta\rho\) rather than \(\rho\) also removes the core domination that made a plain \(L_\rho\) nearly blind to the diffuse valence tail — the tail that sets \(\boldsymbol{\mu}\) (round-2 issue 11).

### 6.4 MD / emergent spectroscopy protocol (run only after training, weights frozen)

**Precondition (round-2 issue 11).** Do not start a production trajectory until the §7 Phase 1 **dipole** gates have passed. \(I(\omega)\) is a functional of \(\boldsymbol{\mu}(t)\); 50 ps of MD cannot repair a wrong \(d\boldsymbol{\mu}/d\mathbf{R}\), it only spends compute on it. A model may pass every energy and force gate and still produce meaningless intensities.

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
| **Fase 0 — Numerical foundation** | Validate the differentiable physics engine itself, with **no ML**; lock the §5.1 data recipe | Analytical/reference energy functional + 1-geometry smoke tests + **10-geometry H₂O and benzene cost pilots** | **Total engine artifact \(<0.1\,\text{meV/Å}\)** \((1.9\times10^{-6}\,\text{a.u.})\), which at \(\Delta x=0.20\,\text{Å}\) means egg-box amplitude \(<2.3\times10^{-7}\,\)Hartree · \(\lVert\mathbf{F}_{autograd}-\mathbf{F}_{finite\text{-}diff}\rVert<0.05\,\text{meV/Å}\) \((10^{-6}\,\text{a.u.}, \text{float64})\) — a check of the autograd graph, **not** of discretization · closed-loop force conservation · energy drift over the **production trajectory length** \(<1\%\) of \((3N-6)k_BT\) (H₂O / 50 ps / 300 K: \(6\times10^{-7}\,\)Hartree/ps) · Hockney FFT-Poisson solver validated · rigid-translation egg-box test across \(\sigma/\Delta x \in \{1,1.5,2,2.5,3\}\) **and across \(x\), \(y\), \(z\) and a body diagonal**, reported as the max · grid-convergence study across \(\Delta x \in \{0.40,\dots,0.15\}\,\text{Å}\) · box-size/boundary convergence for the Poisson solver · **filled smoke-test table** (energy / 1-RDM / analytic grad / Hessian for H₂O and benzene) · **measured** \(\bar t_{\mathrm{geom}}\), peak RAM, and export size · **published label noise floor** (5-point repeated QM force on one H₂O geometry) · **per-element atomic reference fits** accepted at \(\int\lvert\rho^{\mathrm{fit}}-\rho^{\mathrm{atom}}\rvert dV/Z<10^{-3}\) · **real-cube representability**: on one real H₂O CCSD 1-RDM, \(\lvert\int\Delta\rho\,dV\rvert<10^{-4}\,e\) and grid-vs-analytic \(E_{ne}\), \(E_H\) agreement \(<0.1\,\)mHa · **egg-box re-measured on that real cube and reported in force units** (not Hartree) · **rigid-rotation sweep** about the nuclear centroid (the translation sweep does not cover it), residual reported as a force-equivalent \(\tau_{\max}/r_{\max}\) against the same \(0.1\,\text{meV/Å}\) ceiling · **\(\varepsilon_\theta\) anchoring fork (i) vs (ii) decided in writing** from the same cube · if \(T_{\mathrm{campaign}}\) does not fit, **shrink ladder chosen in writing** before any 2000/5000-config run |
| **Fase 1 — H₂O PES training** | Learn $\mathbf{R}\to E,\mathbf{F},\rho$ | H₂O, ≥2,000 CCSD(T)/cc-pVTZ configs (per §5.1), $32^3$ grid | **Two independent conditions.** (a) Phase 0's engine-artifact ceiling still holds \((<0.1\,\text{meV/Å})\) — an engine artifact is a bug to be fixed, never a floor that licenses a looser gate. (b) Force RMSE below the **greater of** \(1\,\text{meV/Å}\) and \(3\times\) the measured **label** noise floor · harmonic frequencies within 5 cm⁻¹ of the CCSD(T) Hessian (the one equilibrium Hessian from §5.1, not a per-config Hessian) · **the force and frequency gates must be reconciled empirically once the model exists** — report both; a model that passes one and fails the other means the *pair* is mis-specified, and the pair gets fixed before Phase 2 · **dipole gates (round-2 issue 11), all three required before any production MD:** (i) \(\lVert\boldsymbol{\mu}_\theta-\boldsymbol{\mu}_{\mathrm{QM}}\rVert<0.01\,e a_0\) (\(\approx0.025\,\)D, \(\approx1.4\%\) of the H₂O dipole) on held-out configs; (ii) relative error in \(d\boldsymbol{\mu}/d\mathbf{R}\) \(<5\%\), since \(I\propto\lvert d\boldsymbol{\mu}/dQ\rvert^2\) and the §9 claim is *relative* envelopes at the \(\sim10\%\) level; (iii) grid artifact in \(\boldsymbol{\mu}\) under rigid translation \(<0.1\%\) of \(\lvert\boldsymbol{\mu}\rvert\) |
| **Fase 2 — Emergent IR (H₂O)** | Blind spectral prediction, weights frozen | 5×50 ps MD trajectories | $\nu_1,\nu_2,\nu_3$ band centers within 10–15 cm⁻¹ of experimental gas-phase FTIR envelopes — obtained with **no spectral fitting** |
| **Fase 3 — Physical hardness tests** | Sanity + hardness, **not** the §2 bake-off | D₂O (mass-only swap, frozen weights); CO₂ (linear, symmetric) | D₂O per-mode isotope shift consistent with theory (≈1.35–1.39) — **necessary, not flagship**; CO₂ forbidden-mode gate with a **number**: \(I(\nu_1)/I(\nu_3)<10^{-2}\), and the measured ratio must be consistent with \(\delta^2\), where \(\delta\) is the independently measured relative \(d\boldsymbol{\mu}/dQ\) error from Phase 1. A voxel grid breaks \(D_{\infty h}\), so the residual is **not** zero and “\(\approx0\)” was never a gate; if the ratio greatly exceeds \(\delta^2\) the model has learned an asymmetric density and the failure is physical, not numerical. \(\nu_2/\nu_3\) correctly active |
| **Fase 4 — Baseline benchmark** | Answer §2: field vs atomistic GNN on the **same** splits | Same H₂O/benzene `config_id`s as P1/05 | **Owners:** 04 trains simple NN; **G1** trains MACE from scratch (NequIP fallback); P1/05 are the field legs; **08 assembles only**. **§7.1 pre-registration is a precondition** — frozen split hash, \(\ge3\) seeds, tuning parity and a declared effect size, all committed before any leg trains. **Primary gate:** leave-one-mode-out (or held-out mode-family) \(E/F\) vs G1. Secondary: in-domain RMSE, harmonic error vs the one §5.1 Hessian, MD stability, cost. If G1 is missing, the phase is **incomplete** — do not substitute 04 for MACE. |
| **Fase 5 — Finale: benzene** | Aromatic generalization | C₆H₆, nominal $64^3$ / ≥5,000 configs **subject to the §5.1 pilot and shrink ladder**, 20 ps forward MD | Aromatic ring/C–H modes within 15 cm⁻¹ of one fixed gas-phase NIST FTIR dataset. If rung 4 of the shrink ladder fired, this phase is outlook — do not keep the nominal \(N\) as a scored promise |
| *(Outlook only, not scored)* | OOD transferability discussion | Naphthalene (C₁₀H₈) via atomic density superposition, zero-shot | Discussed as an exploratory result in the thesis, explicitly **not** a pass/fail milestone |

**Gate unit discipline (round-2 issue 8).** Every artifact tolerance above is quoted in **force units**, because that is the unit the acceptance gates are in. An artifact quoted in Hartree is a force tolerance in disguise: a cell-periodic energy artifact of peak-to-peak amplitude \(A\) and period \(\Delta x\) implies a peak force artifact \(\pi A/\Delta x\). The conversion, and the derivation of each number from the Phase 1 acceptance gate, is in [probes/issue08_gate_consistency.py](../probes/issue08_gate_consistency.py) — re-run it rather than re-deriving by hand if \(\Delta x\), the trajectory length, or the acceptance gate ever changes. Energy drift is likewise budgeted over the **production trajectory length** against \((3N-6)k_BT\), not quoted as a rate in isolation: the old \(10^{-5}\,\)Hartree/ps allowed the 50 ps H₂O run to lose 18% of the vibrational energy it is supposed to be holding.

### 7.1 Pre-registration of the §2 comparison (resolves round-2 blocking issue 13)

§2 is currently falsifiable in wording only. A comparison between a bespoke architecture and a mature, author-tuned package is not an experiment until the following are fixed **in a commit that predates any leg of the comparison being trained**. All of it is free; none of it is recoverable afterwards.

**1. Frozen splits.** One file per campaign, `splits/{molecule}_{version}.json`, containing train / validation / test `config_id`s and the held-out mode family for the leave-one-mode-out test. Committed and tagged; its hash appears in every gate report from P1, 05, G1 and 04. Every leg reads that file — nobody re-splits.

**2. Seeds and error bars.** Minimum **3 seeds per model per split**. The primary metric is reported as mean ± SD across seeds. A single-seed number is not a result.

**3. Tuning parity.** Equal hyperparameter budget: same number of trials and same wall-clock budget for the field model and for G1, tuned on the **validation** split only. MACE starts from its authors' recommended recipe as trial 0 — an untuned competitor is a straw man and a reviewer will say so. The field model starts from its §6.1 default. Trial count and budget go in the gate report.

**4. Pre-registered effect size.** Primary metric: the ratio \(r=\mathrm{RMSE}^{F}_{\text{field}}/\mathrm{RMSE}^{F}_{\text{GNN}}\) on the held-out mode family. Declared in advance:

| Outcome | Condition |
|---|---|
| field wins | \(r<1-\Delta\) with non-overlapping \(\pm1\) SD |
| GNN wins | \(r>1+\Delta\) with non-overlapping \(\pm1\) SD |
| **inconclusive** | otherwise |

\(\Delta\) is provisionally \(0.10\) and is finalized as \(3\times\) the measured within-model seed scatter **on the validation split**, before either model is evaluated on the held-out mode family. Setting \(\Delta\) from validation scatter is legitimate; setting it after seeing the comparison is not. **“Inconclusive” is a publishable outcome and must be reported as such** — the thesis question is whether the field representation transfers better, and “we could not tell” is an honest answer to it.

**5. Confounds registered in advance.** Named now so they cannot be discovered as excuses later: (a) MACE is exactly rotation-equivariant and the field model is not (§8 item 13 — both invariance residuals published **before** the bake-off); (b) tuning-maturity asymmetry; (c) equal training-data volume and identical labels; (d) which §6.1 anchoring fork and which §2.1 fallback rung the field model used; (e) whether the §5.1 shrink ladder fired.

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
   - (B) electronic-structure error = CCSD(T)/basis-set vs. a higher-level reference;
   - (C) spectroscopic/nuclear-motion error = classical MD vs. the true quantum rovibrational result.
7. **Extended energy-conservation metrics** beyond drift alone: $\Delta E_{max}$, $\Delta E_{RMS}$, force-consistency ($\lVert\nabla_\mathbf{R}\times\mathbf{F}\rVert$), and timestep-convergence. Drift is budgeted **over the production trajectory length** as a fraction of \((3N-6)k_BT\) (§7 gate unit discipline), never as a bare Hartree/ps figure.
8. **Extended spectral-quality metrics**: peak-position error, integrated-intensity error, relative-intensity error, forbidden-mode residual intensity, linewidth, and convergence with trajectory length.
9. **Charge/dipole sanity check**: numerically verify $\int\rho(\mathbf{r},t)\,d^3r = N_e$ stays within 0.01% throughout a run (a corrupted charge integral at $t=0$ was flagged early as poisoning all downstream gradients).
10. **Do not treat compute budgets as fixed a priori** — the earlier "18–24 hours on one A100 for benzene" estimate was flagged as likely too optimistic. Two measured budgets are required, and neither is a guess:
    - **Data campaign** (§5.1): \(T_{\mathrm{campaign}}\approx N_{\mathrm{geom}}\times\bar t_{\mathrm{geom}}\) from the 10-geometry H₂O and benzene pilots. This is a Phase 0 **exit**. If it does not fit, take the shrink ladder *before* P1/05 training.
    - **MD inference** (this item, original intent): derive a realistic 20–50 ps trajectory cost only *after* a real 10-ps H₂O run on the frozen PES, then extrapolate memory/time. Do not quote A100 folklore.
11. **Reference-split validation** (round-2 issue 7) — a standing check, not a one-off. For \(\ge20\) geometries per molecule, compare the grid pipeline's \(E_{ne}\) and \(E_H\) against their **exact analytic values in the Gaussian basis**, which PySCF returns for free. Report max and RMS deviation. Any drift in this number over the campaign means the export grid, the reference fit, or the smearing width changed without anyone noticing.
12. **Observable validation** (round-2 issue 11) — the graded deliverable is band positions **and relative intensities**, so \(\boldsymbol{\mu}\) and \(d\boldsymbol{\mu}/d\mathbf{R}\) are first-class validated quantities, not by-products. Report \(\boldsymbol{\mu}\) error, \(d\boldsymbol{\mu}/d\mathbf{R}\) relative error, and the translational grid artifact in \(\boldsymbol{\mu}\), against the §7 Phase 1 gates. Note that \(L_\rho\) does **not** optimize the dipole even after the reference split — it is an unweighted MSE and the dipole is a first moment, so a model can lower \(L_\rho\) while worsening \(\boldsymbol{\mu}\). If gate (ii) fails, add a \(\boldsymbol{\mu}\) term to \(L_{train}\) rather than hoping.
13. **Invariance budget** (round-2 issue 12) — a voxel-grid energy is neither translation- nor rotation-invariant, and neither residual was previously gated:
    - **Translation:** \(\lVert\sum_A\mathbf{F}_A\rVert\) is \(-\partial E/\partial(\text{rigid shift})\), i.e. the egg-box force in a different costume. It is *not* a new gate — it is bounded by the same \(0.1\,\text{meV/Å}\) ceiling, and it is a cheap **online** monitor of that ceiling during production MD.
    - **Rotation:** \(\lVert\sum_A\mathbf{R}_A\times\mathbf{F}_A\rVert\) is **not** covered by any translation sweep and must be measured with its own rigid-rotation scan, reported as \(\tau_{\max}/r_{\max}\) in meV/Å against the same ceiling. Measured on the model density, the reference split gives \(3\times10^{-5}\,\text{meV/Å}\) against \(1.7\times10^{3}\,\text{meV/Å}\) for the full density on the grid — but that ordering was not knowable in advance, which is exactly why it is a gate and not an assumption.
    - **Pre-registered confound:** rotation is the symmetry an equivariant GNN satisfies *by construction*. Both residuals must be published **before** the Phase 4 bake-off, so that a G1 win can be read correctly — “the field representation is worse” and “our discretization broke a symmetry the competitor gets for free” are different conclusions, and only pre-registered numbers can tell them apart.

---

## 9. Precision Claims — final, defensible wording

- ✅ "We predict vibrational band positions and relative IR spectral envelopes/intensities within a stated cm⁻¹ tolerance, for H₂O, D₂O, CO₂ and benzene."
- ✅ "The frozen model reproduces the H₂O→D₂O isotope shift and CO₂ symmetry-forbidden intensity with zero retraining."
- ❌ "We predict chemically precise, high-resolution IR spectral lines" (rovibrational-line-list precision) — not defensible with classical MD + FFT.
- ❌ "Chemical precision on large PAHs (C₄₈+)" — explicitly out of scope for the thesis; at most a discussion-chapter outlook via naphthalene. The post-master’s path is [Project 10](../CapstoneProjects/10_Size_Extensive_Aromatic_PES.md) (labels + size-extensivity) → [Project 11](../CapstoneProjects/11_Anharmonic_IR_and_Intensities.md) (GVPT2-class bands + intensities) → [Project 12](../CapstoneProjects/12_Astrophysical_PAH_Identification.md) (fail-closed identification). None of those is a Udacity module.
