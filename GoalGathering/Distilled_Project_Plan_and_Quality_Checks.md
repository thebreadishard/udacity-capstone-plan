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
- **Strictly non-DFT *energies and (default) forces*** for every pipeline target (see §5.1). The density target is the pinned 1-RDM recipe, not a slogan “exact CCSD(T) density.” A cheaper density proxy is allowed only via the §5.1 shrink ladder and must invoke the Overarching Goal escape clause.
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

**Step 0 — pin.** One PySCF version, one basis (`cc-pVTZ`), one SCF/CC convergence, one grid for exporting \(\rho\) (the §6 grid, not a mysterious default cube).

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

Every row in the campaign manifest gets: `theory_energy`, `theory_density`, `theory_force`, `rdm_relaxed|unrelaxed`, `pyscf_version`, `grid`, `wall_s`, `max_rss_gb`. If those fields are blank, it is not a dataset.

#### Shrink ladder (in the plan *before* the pilot)

Stop at the first rung that fits:

1. Cut benzene \(N\) (5000 → 2000 → 1000). Keep CCSD(T) energies and the density recipe above.
2. Store benzene \(\rho\) on \(32^3\) (or downsample after a finer QM cube). Training grid and QM cube may differ if the export method is written down.
3. **Density proxy, energy/force still CCSD(T):** \(\rho\) from HF or a documented DFT *density only*. This is a real precision exception and **must** use the Overarching Goal escape clause. Allowed only if the smoke test / pilot shows CCSD densities are the long pole. Module 06-style “it’s just sampling” does **not** cover this.
4. **Benzene field campaign becomes outlook.** Module 05 must then be remapped. Do not keep “≥5000 benzene CCSD(T) volumes” as a scored promise.

H₂O (2000 configs, \(32^3\), 3 atoms) is assumed cheaper. If the *H₂O* pilot already fails, the field thesis is locally infeasible: **stop before P1**, not after.

#### Force gate sits above noise

The Phase 1 force Go/No-Go is not a chat number. Force RMSE must be **below the greater of** \(1\,\text{meV/Å}\) **and** \(3\times\) the measured noise floor.

Noise floor is measured in Phase 0 / the pilot, not assumed:

- \(\lVert F_{\text{autograd}}-F_{\text{FD}}\rVert\) on the engine
- egg-box residual in force
- scatter of a 5-point repeated CCSD(T) (or FD) force on one H₂O geometry

If that floor is \(4\,\text{meV/Å}\), a \(1\,\text{meV/Å}\) gate is superstition. Publish the floor next to the gate.

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
- $L_F$: MSE on per-atom forces vs. the §5.1 force recipe (analytic CCSD(T) if the smoke test returns it; else analytic CCSD; else H₂O-only finite-difference of CCSD(T) energies).
- $L_H$: Hessian supervision at the **counted** stationary points in §5.1 (1 H₂O + 1 benzene equilibrium Hessian first). Force-only supervision does **not** guarantee correct 2nd/3rd-order PES derivatives.
- $L_\rho$: MSE on the 3D electron density vs. the §5.1 density target (default: relaxed CCSD 1-RDM, not a slogan “exact CCSD(T) density”). This supervises the *argument* of \(\mathcal{E}\); it is not an optional extra head and not the force source.

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
| **Fase 0 — Numerical foundation** | Validate the differentiable physics engine itself, with **no ML**; lock the §5.1 data recipe | Analytical/reference energy functional + 1-geometry smoke tests + **10-geometry H₂O and benzene cost pilots** | Energy drift $<10^{-5}$ Hartree/ps · egg-box amplitude $<10^{-4}$ Hartree · $\lVert\mathbf{F}_{autograd}-\mathbf{F}_{finite\text{-}diff}\rVert < 10^{-5}$ a.u. (closed-loop force conservation + finite-difference check) · Hockney FFT-Poisson solver validated · rigid-translation egg-box test across $\sigma/\Delta x \in \{1,1.5,2,2.5,3\}$ · grid-convergence study across $\Delta x \in \{0.40,\dots,0.15\}\,\text{Å}$ · box-size/boundary convergence for the Poisson solver · **filled smoke-test table** (energy / 1-RDM / analytic grad / Hessian for H₂O and benzene) · **measured** \(\bar t_{\mathrm{geom}}\), peak RAM, and export size · **published force noise floor** (engine FD, egg-box residual, 5-point repeated QM force on one H₂O) · if \(T_{\mathrm{campaign}}\) does not fit, **shrink ladder chosen in writing** before any 2000/5000-config run |
| **Fase 1 — H₂O PES training** | Learn $\mathbf{R}\to E,\mathbf{F},\rho$ | H₂O, ≥2,000 CCSD(T)/cc-pVTZ configs (per §5.1), $32^3$ grid | Force RMSE below the **greater of** \(1\,\text{meV/Å}\) **and** \(3\times\) the Phase 0 measured noise floor · harmonic frequencies within 5 cm⁻¹ of the CCSD(T) Hessian (the one equilibrium Hessian from §5.1, not a per-config Hessian) |
| **Fase 2 — Emergent IR (H₂O)** | Blind spectral prediction, weights frozen | 5×50 ps MD trajectories | $\nu_1,\nu_2,\nu_3$ band centers within 10–15 cm⁻¹ of experimental gas-phase FTIR envelopes — obtained with **no spectral fitting** |
| **Fase 3 — Physical hardness tests** | Prove the model learned real physics, not memorization | D₂O (mass-only swap, frozen weights); CO₂ (linear, symmetric) | D₂O per-mode isotope shift consistent with theory (≈1.35–1.39); CO₂ $\nu_1$ symmetric-stretch intensity ≈ 0 (correctly IR-inactive), $\nu_2/\nu_3$ correctly active |
| **Fase 4 — Baseline benchmark** | Prove the 3D field representation adds value | vs. equivariant atomistic ML PES, simple NN energy model, harmonic/finite-difference CCSD(T) | Comparative table: energy RMSE, force RMSE, vibrational error, MD stability, compute cost |
| **Fase 5 — Finale: benzene** | Aromatic generalization | C₆H₆, nominal $64^3$ / ≥5,000 configs **subject to the §5.1 pilot and shrink ladder**, 20 ps forward MD | Aromatic ring/C–H modes within 15 cm⁻¹ of one fixed gas-phase NIST FTIR dataset. If rung 4 of the shrink ladder fired, this phase is outlook — do not keep the nominal \(N\) as a scored promise |
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
10. **Do not treat compute budgets as fixed a priori** — the earlier "18–24 hours on one A100 for benzene" estimate was flagged as likely too optimistic. Two measured budgets are required, and neither is a guess:
    - **Data campaign** (§5.1): \(T_{\mathrm{campaign}}\approx N_{\mathrm{geom}}\times\bar t_{\mathrm{geom}}\) from the 10-geometry H₂O and benzene pilots. This is a Phase 0 **exit**. If it does not fit, take the shrink ladder *before* P1/05 training.
    - **MD inference** (this item, original intent): derive a realistic 20–50 ps trajectory cost only *after* a real 10-ps H₂O run on the frozen PES, then extrapolate memory/time. Do not quote A100 folklore.

---

## 9. Precision Claims — final, defensible wording

- ✅ "We predict vibrational band positions and relative IR spectral envelopes/intensities within a stated cm⁻¹ tolerance, for H₂O, D₂O, CO₂ and benzene."
- ✅ "The frozen model reproduces the H₂O→D₂O isotope shift and CO₂ symmetry-forbidden intensity with zero retraining."
- ❌ "We predict chemically precise, high-resolution IR spectral lines" (rovibrational-line-list precision) — not defensible with classical MD + FFT.
- ❌ "Chemical precision on large PAHs (C₄₈+)" — explicitly out of scope for the thesis; at most a discussion-chapter outlook via naphthalene. The post-master’s path is [Project 10](../CapstoneProjects/10_Size_Extensive_Aromatic_PES.md) (labels + size-extensivity) → [Project 11](../CapstoneProjects/11_Anharmonic_IR_and_Intensities.md) (GVPT2-class bands + intensities) → [Project 12](../CapstoneProjects/12_Astrophysical_PAH_Identification.md) (fail-closed identification). None of those is a Udacity module.
