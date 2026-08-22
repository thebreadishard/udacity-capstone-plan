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

---

## 2. Central Research Question (final formulation)

> "Does a continuous 3D neural field representation of the electron density (FNO-NCA), via a hybrid Fourier Neural Operator – Neural Cellular Automaton, yield a more physically transferable, energy-conserving Potential Energy Surface (PES) than existing atomistic equivariant Graph Neural Networks — from which molecular vibrational/infrared bands emerge via classical molecular dynamics?"

This replaced the original, much broader claim ("can an AI find a universal CA update rule that predicts chemically precise IR lines of arbitrarily large PAHs"), which both professors judged too broad and not falsifiable enough for a master's thesis.

**Core hypothesis:** representing electrons as a continuous 3D field (rather than pairwise atom-centered distances, as in GNNs) should capture non-local charge delocalization and π-polarization more faithfully, giving better transferability to unseen vibrational modes.

---

## 3. What the Project IS

- **A differentiable molecular-dynamics simulator**: explicit classical nuclei (positions $\mathbf{R}_A$, velocities $\mathbf{V}_A$, mass $M_A$, charge $Z_A$) coupled to a continuous 3D electron-density field $\rho(\mathbf{r})$ living on the same grid.
- **Energy-first (Route B) architecture**: the *only* scalar energy is the functional in §6, $E_\theta(\mathbf{R})=\mathcal{E}[\rho_\theta(\mathbf{r};\mathbf{R}),\mathbf{R}]$. There is no second energy head. Forces are obtained by **exact automatic differentiation**, $\mathbf{F}_A = -\partial E_\theta/\partial \mathbf{R}_A$, which *guarantees* $\oint \mathbf{F}\cdot d\mathbf{R} = 0$ and $\nabla_\mathbf{R}\times\mathbf{F}=0$ (conservative forces), unlike the earlier density-first design. The 3D density is the argument of \(\mathcal{E}\) and a supervised target; it is not differentiated by itself to produce forces.
- **A hybrid FNO-NCA *density encoder***: local $3\times3\times3$ NCA convolutions handle short-range structure in \(\rho_\theta\); an optional learned FNO is a non-local mixer **inside the encoder only**. Long-range \(1/r\) electrostatics in the *energy* are **not** learned — they come from the fixed Hockney–Eastwood solver in \(E_{\mathrm{es}}\) (§6). A purely local CA would need ~60+ steps just to propagate charge information across one aromatic ring; that is why the encoder may use an FNO. It is not a reason to replace the Poisson kernel.
- **Isotope shift as the flagship physical proof**: because atomic mass $M_A$ enters only the classical Newtonian/Verlet integration step (not the learned network), the frozen, already-trained model must reproduce the H₂O → D₂O red-shift correctly with **zero retraining**, purely from $\mathbf{F}/M_A$.
- **Emergent spectroscopy, not trained spectroscopy**: the network is trained *only* on static configurations (energies, forces, Hessians, densities). Once trained and frozen, it runs forward-only classical MD for tens of picoseconds; the IR spectrum is obtained via FFT of the dipole autocorrelation function purely as a **blind post-hoc prediction**, never as a training signal.
- **Strictly non-DFT data** for every input and every target, end to end (see §5).
- **Rigorously phased**, with hard numerical Go/No-Go gates between phases (§7), scoped to what is achievable in a ~6–7 month master's thesis on local consumer hardware, with supercomputer time reserved only for later-phase scaling.
- **Grid/channel representation** (Born–Oppenheimer; real density only): $N\times N\times N$ voxel grid, $\Delta x \approx 0.20$–$0.25\,\text{Å}$.
  - **Keep:** one real, non-negative density channel \(\rho\ge 0\) with \(\int\rho\,dV=N_e\) on every forward pass; \(V_{\mathrm{nucl}}\) / \(\Phi\) as **computed** Hockney–Eastwood fields, not free learned channels; a handful of latent NCA memory channels, labeled as hidden state.
  - **Delete:** \(\rho_{Re},\rho_{Im}\) and \(E_x,E_y,E_z\). Those are fossils of the rejected Ehrenfest / photon / complex-wavefunction story. A BO PES has no EM grid and no imaginary density. The IR dipole is \(\boldsymbol{\mu}=\int\mathbf{r}\,(\rho_{\mathrm{nucl}}-\rho_\theta)\,dV\) from the same real \(\rho\).

---

## 4. What the Project is explicitly NOT

- **NOT a Graph Neural Network**: no discrete atom-nodes, bond types, or hard-coded per-element sub-networks (rejecting the SchNet/PhysNet/MLAtom/ANI-1 style architecture). One single universal update rule / energy functional must work for any element purely from local field values (charge density, potential gradients), the way physical law itself doesn't have separate equations per bond type.
- **NOT Density Functional Theory (DFT)**: no approximate exchange-correlation functionals (B3LYP, PBE, M06-2X, etc.), which are known to make systematic errors on dispersion and aromatic π-delocalization. This exclusion applies to every input and every target dataset, with no exceptions planned. The Hohenberg–Kohn *shape* \(E=\mathcal{E}[\rho]\) is the research claim, not a KS-DFT calculation: \(\varepsilon_\theta\) is a learned remainder, not a library XC functional, and no DFT data enter the pipeline.
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
| H₂O, CO₂ | Exact CCSD(T)/cc-pVTZ density, geometry, forces, Hessian via PySCF | ExoMol (POKAZATEL line list), HITRAN/HITEMP — used only for final blind spectral comparison, never as training loss |
| C₆H₆ (benzene) | Exact CCSD(T) density/forces/Hessian via PySCF (larger config set) | NIST Chemistry WebBook gas-phase FTIR (one specific dataset/resolution must be fixed as the benchmark) |
| Large PAHs (outlook only) | Atomic Density Superposition: pre-computed CCSD(T) C–H/C–C fragment densities from benzene, spatially superposed at target atom coordinates, renormalized to exact electron count, relaxed with one Poisson update | NASA PAHdb (matrix-isolated experimental FTIR, Ar/Ne, ~10 K) with an explicit matrix-shift correction (2–15 cm⁻¹, per Boersma et al.) — outlook/discussion only |

Training-set sizing (revised upward after the 150-configuration training set was judged "far too small" for a model that must reproduce density, forces, multiple modes, and MD stability): **≥2,000 configurations for H₂O**, **≥5,000 for benzene**, sampled via normal-mode displacements (harmonic and anharmonic amplitudes), random thermal displacements (100–600 K), and rigid rotations/translations (augmentation) — split by configuration, not by random points drawn from near-identical trajectories, and including leave-one-mode-out validation.

---

## 6. Architecture & Training Details (final)
Workstream P1 and Module 05 **share this forward pass**. They must not diverge into a latent energy head on one molecule and a functional on the other.

### 6.1 Forward pass (implements \(E=\mathcal{E}[\rho,R]\))

**1. Nuclei → fields (not learned).** Continuous Gaussian charge clouds, not point charges:

$$\rho_{\mathrm{nucl}}(\mathbf{r};\{\mathbf{R}_A\}) = \sum_A Z_A \left(\frac{1}{2\pi\sigma^2}\right)^{3/2}\exp\left(-\frac{|\mathbf{r}-\mathbf{R}_A|^2}{2\sigma^2}\right),\quad \sigma \geq 1.5\,\Delta x$$

\(V_{\mathrm{nucl}}\) is the Hockney–Eastwood potential of \(\rho_{\mathrm{nucl}}\). These are inputs.

**2. Density encoder (NCA / optional FNO).** State on the grid: one real, non-negative density channel plus latent NCA memory (hidden state, not physics). Local \(3\times3\times3\) NCA steps handle short range. An optional learned FNO is a non-local mixer **inside this encoder only**. Readout:

$$\rho_\theta(\mathbf{r};\mathbf{R})=\mathrm{softplus}(s(\mathbf{r})),\qquad \int\rho_\theta\,dV=N_e$$

(renormalize every forward pass). No \(\rho_{Im}\). No EM channels.

**3. Energy is a functional of that density.** No second head:

$$E_\theta(\mathbf{R})=E_{\mathrm{es}}[\rho_\theta,\mathbf{R}]+\int \varepsilon_\theta\!\big(\rho_\theta,|\nabla\rho_\theta|\big)\,dV$$

- \(E_{\mathrm{es}}\): classical electron–nuclear, Hartree, and nuclear–nuclear electrostatics, all from **one fixed Hockney–Eastwood solve** on \(\rho_{\mathrm{nucl}}-\rho_\theta\). Same kernel Phase 0 already validates. Not learned.
- \(\varepsilon_\theta\): a tiny MLP / \(1\times1\times1\) conv on **local density features only** (may see \(\rho\), \(|\nabla\rho|\), and \(\Phi\)). This is a learned kinetic+remainder functional, not B3LYP. It must **not** see \(Z_A\), one-hot elements, bond lists, or raw \(\mathbf{R}\).

**4. Forces.** \(\mathbf{F}_A=-\partial E_\theta/\partial\mathbf{R}_A\) via PyTorch autograd through the Gaussian nuclear placement **and** through \(\rho_\theta(\mathbf{R})\). Do not `stop_grad` on \(\rho\). Hellmann–Feynman alone is not exact for a learned \(\rho\) fitted to CCSD(T).

If this graph is implemented, \(E\) *is* \(\mathcal{E}[\rho,R]\). A trunk that emits both \(\rho\) and a scalar \(E\) from pooled latents is a spec violation, not a variant.

### 6.2 Poisson vs FNO — two objects

| Object | Role | Who validates it |
|---|---|---|
| **Hockney–Eastwood** | Isolated-molecule electrostatics in \(E_{\mathrm{es}}\) and \(V_{\mathrm{nucl}}\). Embed \(N^3\) in a \(2N\times2N\times2N\) zero-padded box; cap the Coulomb kernel at the box radius. | Phase 0 |
| **Learned FNO** | Optional non-local block **in the density encoder** | Module 05 ablation |

Do **not** treat the FNO as a learned Poisson solver. Phase 0 would then validate something 05 immediately replaces, and the ablation would mix two physics stories.

**Module 05 controlled experiment:** same \(\mathcal{E}\), same \(E_{\mathrm{es}}\); encoder = local-NCA-only vs local-NCA+FNO. One changed variable. The question is whether the non-local encoder improves \(\rho\) and therefore \(E\) and \(\mathbf{F}\).

**Optional diagnostic (not the rubric ablation):** drop \(E_{\mathrm{es}}\) and keep only \(\int\varepsilon_\theta\). If that works as well, the field-functional story is weaker than claimed. Report it; do not train that way by default.

Do not invent a more exotic \(\mathcal{E}\) (orbital-free kinetic libraries, learned pair densities) until this one fails. This is the smallest object that makes the equation true.

### 6.3 Training loss (static configurations only — no spectral term)

$$L_{train} = \lambda_E L_E + \lambda_F L_F + \lambda_H L_H + \lambda_\rho L_\rho$$

- $L_E$: MSE on total energy vs. CCSD(T).
- $L_F$: MSE on per-atom forces vs. CCSD(T).
- $L_H$: Hessian supervision at selected stationary points (explicitly added because force-only supervision does **not** guarantee correct 2nd/3rd-order PES derivatives, contrary to an earlier claim in the plan).
- $L_\rho$: MSE on the 3D electron density vs. CCSD(T). This supervises the *argument* of \(\mathcal{E}\); it is not an optional extra head and not the force source.

### 6.4 MD / emergent spectroscopy protocol (run only after training, weights frozen)

- Timestep $\Delta t = 0.5\,\text{fs}$ (this was judged fine on its own — ~20 samples per C–H stretch period).
- Trajectory length **20–50 ps** (40,000–100,000 steps) — a deliberate, large increase from the earlier 0.5–1 ps, which was shown to give only ~33–67 cm⁻¹ Fourier resolution, incompatible with a 10–15 cm⁻¹ precision claim. 50 ps gives ≈0.67 cm⁻¹ resolution.
- Ensemble of **5–10 independent NVE trajectories** after NVT equilibration at $T=300\,\text{K}$ (a single trajectory from the equilibrium geometry is not treated as a full spectroscopic experiment).
- Spectrum via dipole autocorrelation with the standard harmonic quantum-correction factor:
    $$I(\omega) \propto \omega\cdot\tanh\!\left(\frac{\beta\hbar\omega}{2}\right)\int_{-\infty}^{\infty}\langle\boldsymbol{\mu}(0)\cdot\boldsymbol{\mu}(t)\rangle e^{-i\omega t}\,dt$$

---

## 7. Phased Roadmap with Go/No-Go Quality Gates

| Phase | Goal | Molecule(s)/Grid | Hard Go/No-Go Criteria |
|---|---|---|---|
| **Fase 0 — Numerical foundation** | Validate the differentiable physics engine itself, with **no ML** | Analytical/reference energy functional | Energy drift $<10^{-5}$ Hartree/ps · egg-box amplitude $<10^{-4}$ Hartree · $\lVert\mathbf{F}_{autograd}-\mathbf{F}_{finite\text{-}diff}\rVert < 10^{-5}$ a.u. (closed-loop force conservation + finite-difference check) · Hockney FFT-Poisson solver validated · rigid-translation egg-box test across $\sigma/\Delta x \in \{1,1.5,2,2.5,3\}$ · grid-convergence study across $\Delta x \in \{0.40,\dots,0.15\}\,\text{Å}$ · box-size/boundary convergence for the Poisson solver |
| **Fase 1 — H₂O PES training** | Learn $\mathbf{R}\to E,\mathbf{F},\rho$ | H₂O, ≥2,000 CCSD(T)/cc-pVTZ configs, $32^3$ grid | Force RMSE $<1\,\text{meV/Å}$ · harmonic frequencies within 5 cm⁻¹ of the CCSD(T) Hessian |
| **Fase 2 — Emergent IR (H₂O)** | Blind spectral prediction, weights frozen | 5×50 ps MD trajectories | $\nu_1,\nu_2,\nu_3$ band centers within 10–15 cm⁻¹ of experimental gas-phase FTIR envelopes — obtained with **no spectral fitting** |
| **Fase 3 — Physical hardness tests** | Prove the model learned real physics, not memorization | D₂O (mass-only swap, frozen weights); CO₂ (linear, symmetric) | D₂O per-mode isotope shift consistent with theory (≈1.35–1.39); CO₂ $\nu_1$ symmetric-stretch intensity ≈ 0 (correctly IR-inactive), $\nu_2/\nu_3$ correctly active |
| **Fase 4 — Baseline benchmark** | Prove the 3D field representation adds value | vs. equivariant atomistic ML PES, simple NN energy model, harmonic/finite-difference CCSD(T) | Comparative table: energy RMSE, force RMSE, vibrational error, MD stability, compute cost |
| **Fase 5 — Finale: benzene** | Aromatic generalization | C₆H₆, $64^3$ grid, ≥5,000 configs, 20 ps forward MD | Aromatic ring/C–H modes within 15 cm⁻¹ of one fixed gas-phase NIST FTIR dataset |
| *(Outlook only, not scored)* | OOD transferability discussion | Naphthalene (C₁₀H₈) via atomic density superposition, zero-shot | Discussed as an exploratory result in the thesis, explicitly **not** a pass/fail milestone |

---

## 8. Additional Quality-Assurance / Verification Protocol

These checks were raised piecemeal across both conversations (mostly in the 23-point review) and apply throughout, not just at Phase 0:

1. **Conservativity verification**: test $\oint\mathbf{F}\cdot d\mathbf{R}$ over dozens of random closed loops in configuration space, not just one molecule/one path.
2. **Force finite-difference check**: $F_i \stackrel{?}{=} -\dfrac{E(\mathbf{R}+\delta\mathbf{e}_i)-E(\mathbf{R}-\delta\mathbf{e}_i)}{2\delta}$, targeting agreement at the $10^{-6}$–$10^{-4}$ Hartree/Bohr level.
3. **Egg-box quantification**: rigidly translate a molecule across a full grid cell in small steps and plot $E(\delta)$, $F(\delta)$ for several $\sigma/\Delta x$ ratios; report the residual artificial periodicity explicitly rather than assuming it is negligible.
4. **Grid-convergence study**: report vibrational frequency, energy, and force as a function of $\Delta x$ (e.g. 0.40 → 0.15 Å) so that ML error is not confounded with grid discretization error.
5. **Poisson boundary-condition convergence**: show convergence of results with increasing padding/box size for the isolated-molecule electrostatics.
6. **Error decomposition** — explicitly separate and report three distinct error sources rather than conflating them into one "accuracy" number:
   - (A) ML error = model vs. CCSD(T);
   - (B) electronic-structure error = CCSD(T)/basis-set vs. a higher-level reference;
   - (C) spectroscopic/nuclear-motion error = classical MD vs. the true quantum rovibrational result.
7. **Extended energy-conservation metrics** beyond drift alone: $\Delta E_{max}$, $\Delta E_{RMS}$, force-consistency ($\lVert\nabla_\mathbf{R}\times\mathbf{F}\rVert$), and timestep-convergence.
8. **Extended spectral-quality metrics**: peak-position error, integrated-intensity error, relative-intensity error, forbidden-mode residual intensity, linewidth, and convergence with trajectory length.
9. **Charge/dipole sanity check**: numerically verify $\int\rho(\mathbf{r},t)\,d^3r = N_e$ stays within 0.01% throughout a run (a corrupted charge integral at $t=0$ was flagged early as poisoning all downstream gradients).
10. **Do not treat compute budgets as fixed a priori** — the earlier "18–24 hours on one A100 for benzene" estimate was flagged as likely too optimistic; the plan now requires deriving a realistic compute budget only *after* running a real 10-ps benchmark on H₂O and extrapolating from measured memory/time, not guessing upfront.

---

## 9. Precision Claims — final, defensible wording

- ✅ "We predict vibrational band positions and relative IR spectral envelopes/intensities within a stated cm⁻¹ tolerance, for H₂O, D₂O, CO₂ and benzene."
- ✅ "The frozen model reproduces the H₂O→D₂O isotope shift and CO₂ symmetry-forbidden intensity with zero retraining."
- ❌ "We predict chemically precise, high-resolution IR spectral lines" (rovibrational-line-list precision) — not defensible with classical MD + FFT.
- ❌ "Chemical precision on large PAHs (C₄₈+)" — explicitly out of scope for the thesis; at most a discussion-chapter outlook via naphthalene.
