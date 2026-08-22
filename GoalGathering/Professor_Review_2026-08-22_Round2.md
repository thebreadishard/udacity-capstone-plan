# Critical Professor Review — Round 2 (2026-08-22)

**Status:** No green light. Blocking issues **7–15** are open. This review continues the numbering of [Professor_Review_2026-08-22.md](Professor_Review_2026-08-22.md); issues 1–6 stand as closed-in-spec and are not re-litigated here.

**Scope reviewed:** [Overarching_Goal.md](Overarching_Goal.md), [Distilled_Project_Plan_and_Quality_Checks.md](Distilled_Project_Plan_and_Quality_Checks.md), [Capstone_Mapping.md](Capstone_Mapping.md), [Relevant_Scientific_Papers.md](Relevant_Scientific_Papers.md), [Papers/README.md](Papers/README.md), the module rubrics in [`../CapstoneProjects/`](../CapstoneProjects/), and repository hygiene.

**Why a round 2.** The six issues closed on 2026-08-22 were closed at the level of *governance* — who owns what, what may be claimed, which document wins. That work is genuine and it holds. The holes below are at the level of *physics and arithmetic*. Three of them would be discovered in month four, after the expensive data campaign — which is precisely the failure mode round 1 was written to prevent.

---

## What is not re-litigated

The discipline is real. Route A rejected, spectral loss deleted, D₂O demoted to sanity check, P1 and G1 given owners *and* failure modes, DOI-before-claim as a gate, a forbidden-quote list, the horizon exiled to Projects 10–12. The A/B/C/D tagging is honest and no module is busywork. Repository hygiene is clean — the scraped browser profile in `scraper/udacity_session/` is **not** tracked by git (56 tracked files, none of them session or credential data). That is a supervisable project.

The credit earned there is spent below.

---

## Blocking issues

### 7. The grid cannot represent the density being supervised, and Phase 0 never finds out

\(\Delta x \approx 0.20\)–\(0.25\,\text{Å}\) is fine for a *smeared nuclear* charge with \(\sigma \ge 1.5\Delta x\). It is not fine for an all-electron CCSD 1-RDM. The oxygen 1s cusp has a decay length \(\sim a_0/Z \approx 0.066\,\text{Å}\); the tightest cc-pVTZ oxygen s-primitive has an effective width near \(0.003\,\text{Å}\). On a \(0.378\,\text{bohr}\) grid that structure is not under-resolved — it is invisible.

Three consequences, all fatal if unaddressed:

- §8 item 9 requires \(\int\rho\,dV = N_e\) to \(0.01\%\). Unreachable for an all-electron density at this spacing. The softplus renormalization will then **redistribute the missing core charge into the valence region** — silently corrupting the one quantity IR intensities depend on.
- \(E_{\mathrm{es}}\) is dominated by core electron–nuclear attraction (tens of Hartree for O). Its absolute value on this grid is meaningless. Only its *change with* \(\mathbf{R}\) matters — and that change **is** the egg-box error, evaluated on a cusped density, not on smeared Gaussians.
- Therefore **Phase 0 validates the wrong object.** The egg-box sweep tests the Hockney–Eastwood kernel against a \(\sigma \ge 1.5\Delta x\) Gaussian, passes cleanly, and says nothing about the artifact that actually appears in Phase 1.

**Remedy (choose one, in writing, before engine code):** a promolecular / frozen-core decomposition \(\rho_\theta = \rho_{\text{pro}}(\mathbf{R}) + \Delta\rho_\theta\), with \(E_{\mathrm{es}}\) of the promolecular part evaluated **analytically in the Gaussian basis** so only the smooth deformation density touches a voxel; or ECP / valence-only density targets. This decides what \(E_{\mathrm{es}}\) *is*, so it cannot be deferred.

**Also add to Phase 0:** run the egg-box and grid-convergence sweep on a **real H₂O CCSD 1-RDM cube**, not only on analytic test functions. Report \(\int\rho\,dV\) error and the translational \(E_{\mathrm{es}}\) artifact. This doubles as a genuine second factor for Module 03.

### 8. The Phase 0 gates and the Phase 1 force gate contradict each other by two orders of magnitude

Phase 0 admits an egg-box amplitude of \(10^{-4}\,\text{Hartree}\) over one cell. For a periodic artifact of period \(\Delta x = 0.2\,\text{Å}\), the implied force artifact is

$$\max\left|\frac{dE}{dx}\right| = \frac{\pi A}{\Delta x} = \frac{\pi\times 10^{-4}}{0.2}\ \text{Ha/Å} \approx 8.3\times10^{-4}\ \text{a.u.} \approx 43\ \text{meV/Å}.$$

That is \(83\times\) the Phase 0 force-consistency gate of \(10^{-5}\) a.u., and \(43\times\) the Phase 1 target of \(1\,\text{meV/Å}\).

Now apply §5.1 as written. The Phase 1 gate is \(\max(1\,\text{meV/Å},\,3\times\text{noise floor})\), and the noise floor **explicitly includes the egg-box force residual**. An engine passing Phase 0 exactly at threshold therefore sets the Phase 1 gate at \(\approx 128\,\text{meV/Å}\) — a gate a mediocre model passes, and one flatly incompatible with the \(5\,\text{cm}^{-1}\) harmonic-frequency criterion in the same table row.

Note also that the finite-difference check cannot rescue this: autograd and FD see the *same* corrupted energy surface and will agree beautifully on a wrong force.

**Fix:** specify every artifact tolerance **in force units**, and derive the egg-box *energy* tolerance backwards from the force gate actually needed (\(\sim10^{-6}\,\)Ha for a \(1\,\text{meV/Å}\) target). A gate that cannot be measured is not a gate — the plan's own words. A gate that self-loosens by \(100\times\) is worse than none.

### 9. The novelty check missed the field that already owns this idea

\(E = E_{\mathrm{es}}[\rho] + \int \varepsilon_\theta(\rho,|\nabla\rho|)\,dV\), with \(\rho\) predicted from \(\mathbf{R}\) and forces by autograd, **is machine-learned orbital-free DFT**. The 21-paper bibliography contains none of it. The lineage that must be cited and positioned against includes Snyder et al. (2012), **Brockherde et al. (2017)** — which maps \(\mathbf{R}\to\rho\), evaluates \(E[\rho]\), and *runs MD with it*, i.e. the Route B pipeline — Chandrasekaran et al. (2019), Kohn–Sham-as-regularizer (2021), and M-OFDFT (2024).

Two damages:

1. "Closest prior art is V2Rho-FNO" will not survive Module 09, where one question from a chemistry-literate mentor is answered by a 2017 *Nature Communications* paper.
2. Worse scientifically: that literature is a documented record of **why a semilocal functional of \((\rho,|\nabla\rho|)\) does not transfer**. Teller's theorem is the pathological limit; M-OFDFT needed non-local, basis-coefficient representations precisely because local features failed. The hypothesis "the field representation transfers better" is being tested with the one functional form the field knows transfers *worst*. That may still be defensible — training on a narrow manifold is not the universal-functional problem — but it must be argued explicitly, with a **pre-registered fallback** (non-local \(\varepsilon_\theta\)), not discovered in Phase 4.

Related magnitude problem: \(\varepsilon_\theta\) must supply the kinetic energy, \(\sim 76\,\)Ha for water, to \(\sim1\,\)mHa. A "tiny MLP on local density features" is being asked for \(10^{-5}\) relative accuracy on the largest term in the equation. Say how that is expected to work (energy differences on a narrow manifold, reference subtraction), or the number will be discovered empirically at the worst moment.

### 10. \(\Phi\) is a bypass channel, and it violates §4

§6.1 forbids \(\varepsilon_\theta\) from seeing \(Z_A\), one-hot elements, bond lists, or raw \(\mathbf{R}\) — then hands it \(\Phi\). If \(\Phi\) is (or contains) \(V_{\mathrm{nucl}}\), it is an analytic function of \(\{Z_A,\mathbf{R}_A\}\) alone. The functional can then learn a partial \(E(\mathbf{R})\) map that ignores \(\rho_\theta\) — exactly the "multi-head regressor with auxiliary density" that §4 calls a spec violation.

**Fix:** drop \(\Phi\), or feed only the *total* potential from \(\rho_{\text{nucl}}-\rho_\theta\) and say so — and add the diagnostic already invented for \(E_{\mathrm{es}}\): freeze \(\rho_\theta\) at a deliberately wrong density and confirm the energy degrades.

### 11. The IR observable is never trained, never validated, and its gate has no number

The deliverable is band envelopes and *relative intensities*. Those come from \(\boldsymbol{\mu}=\int\mathbf{r}(\rho_{\text{nucl}}-\rho_\theta)\,dV\) and its derivative \(d\boldsymbol{\mu}/d\mathbf{R}\). Yet:

- \(L_\rho\) is plain MSE on \(\rho\), numerically dominated by the core and near-blind to the diffuse valence tail that sets \(\boldsymbol{\mu}\). Minimizing it does not optimize the dipole.
- Nothing validates \(\boldsymbol{\mu}(\mathbf{R})\) or \(d\boldsymbol{\mu}/d\mathbf{R}\) against the QM reference **before** 50 ps of MD are spent.
- The Phase 3 CO₂ criterion is "\(\nu_1\) intensity \(\approx 0\)" — a gate without a number, in a plan whose own review says gates without numbers are superstition. On a voxel grid the \(D_{\infty h}\) symmetry is **broken by the lattice**; the residual will not be zero, and quantifying it *is* the experiment.

**Fix:** add a Phase 1 exit criterion — dipole RMSE and \(d\boldsymbol{\mu}/d\mathbf{R}\) RMSE vs the QM reference, with stated thresholds — plus a stated forbidden-mode residual tolerance for CO₂.

### 12. There is no invariance budget — and it is the mechanism by which G1 wins

A voxel-grid energy is neither rotationally nor translationally invariant. Consequences: \(\sum_A \mathbf{F}_A \ne 0\) and \(\sum_A \mathbf{R}_A\times\mathbf{F}_A \ne 0\) — spurious net force and torque, integrated over 40,000–100,000 steps. Rigid rotation/translation augmentation is a soft, data-level patch, not a guarantee. Neither residual appears in the §8 ten-point protocol.

This is not a detail. **MACE is exactly equivariant by construction.** If G1 beats the field model, the honest reading may be "grid discretization broke a symmetry the competitor gets for free" — a statement about voxels, not about representations.

**Fix:** pre-register that confound now, and add \(\lVert\sum_A\mathbf{F}_A\rVert\) and the torque residual as Phase 0/1 gates.

### 13. The central comparison is not yet an experiment

Distilled Plan §2 is falsifiable in wording only. Missing:

- number of random seeds;
- error bars on the leave-one-mode-out metric;
- hyperparameter-search **parity** between a bespoke architecture and a mature, author-tuned MACE recipe;
- a frozen split manifest file committed **before** either model trains;
- a pre-registered **effect size** that counts as "the field wins."

Without those, a \(10\%\) difference is a coin flip and a loss is indistinguishable from "we tuned ours worse." Two seeds and a stated margin cost almost nothing now and are unrecoverable later.

### 14. Module 03's frozen row count is arithmetically wrong, and its "repeats" have no noise model

[Capstone_Mapping.md](Capstone_Mapping.md) §4 freezes: \(5\times50\times2\times2 + 6\times50 = 800\). That is \(1000+300 = 1300\). The number presented as "honest, not padded" to close blocking issue 5 does not evaluate to itself. (Both readings clear \(\ge500\), so the rubric survives; the *credibility of a frozen number* does not.)

Worse: **the engine is deterministic.** What varies between "2 repeats"? If nothing, those are duplicate rows, and a hypothesis test on a noiseless generator is a category error a statistics grader is entitled to notice.

**Fix:** declare a genuine source of variation — random molecular orientation, random sub-voxel offset, thermally sampled geometries — in the sweep design, and recompute the count. This is also better science: it turns the egg-box study from a curve into a distribution.

### 15. There is no calendar, and the second graded submission sits behind the hardest unfunded work

Round-1 stamp condition 1 required Phase 1 assigned "with a date and a failure mode." [Capstone_Mapping.md](Capstone_Mapping.md) §4.1 delivers an excellent failure mode and **no date**. Nowhere in the repository is there a month, a deadline, or an effort estimate.

The dependency chain makes this urgent: **Module 03 — the second graded submission — is gated on a working differentiable physics engine** with Hockney–Eastwood electrostatics, autograd forces, and validated sweeps. Meanwhile the ungraded critical path (Phase 0 engine + two PySCF campaigns + P1 + G1) plausibly exceeds the graded work in total effort, inside a \(\sim\)6–7 month window.

**Fix:** one page — phase, calendar weeks, owner, and the drop-dead date after which the shrink ladder fires *automatically* rather than by judgment.

---

## Not blocking, but fix before it costs something

- **Smeared nuclei corrupt \(E_{nn}\).** At \(\sigma=0.3\,\text{Å}\), O–H Gaussian–Gaussian repulsion errs by \(\sim2.4\%\), i.e. \(\sim0.1\,\)Ha, geometry-dependent — a systematic error \(\varepsilon_\theta\) must repair to 1 mHa. \(E_{nn}\) for point charges is analytic and free: use the exact value, and smear only for the grid-based electron–nuclear term.
- **"NOT Density Functional Theory."** The project builds an orbital-free DFT with a learned functional. §4's prose now says the right thing, but the heading is a free kill for an examiner in Module 09. Rename it to what is meant: *no library XC functionals, no DFT-quality labels.*
- **Module 09 has no owner.** It is a live 15-minute defense of exactly the honest-scope narrative six issues were spent constructing. It deserves a preparation artifact — a one-page "what we claim / what we did not build / what we would do next" — not improvisation.
- **Get written mentor pre-approval for self-generated datasets in 03/04/05 *before* generating them.** A Zenodo DOI makes data public; it does not pre-empt a grader who reads "output of my own simulator" as synthetic. §5.5 forbids the UCI fallback on principle, which is admirable and leaves no recovery if the ruling goes the other way. Asking first is free.

---

## What would earn the stamp

A **conditional green light to write the Phase 0 engine only**, granted the moment one short addendum exists:

1. The density-representation decision from issue 7, in writing, with \(E_{\mathrm{es}}\) redefined accordingly. **Must precede engine code**, or Phase 0 validates a caricature.
2. All artifact tolerances restated in force units, with the egg-box energy tolerance derived backwards from the Phase 1 force gate (issue 8).
3. Invariance residuals (\(\sum\mathbf{F}\), torque) and dipole / \(d\boldsymbol{\mu}/d\mathbf{R}\) accuracy added as numbered gates (issues 11, 12).
4. \(\Phi\) removed from \(\varepsilon_\theta\), or its role justified with an equation plus a bypass diagnostic (issue 10).
5. ML-OF-DFT literature added to the bibliography, with one paragraph positioning this work against Brockherde-style pipelines and one pre-registered fallback if the semilocal \(\varepsilon_\theta\) stalls (issue 9).
6. Module 03's sweep design fixed: correct arithmetic **and** a declared stochastic factor (issue 14).
7. One page of dates (issue 15).

None of that requires compute. All of it is cheaper than discovering it in Module 05.

This project is honest enough that these criticisms are possible to state precisely. That is the compliment. Close these seven, and Phase 0 gets stamped — and the pilot numbers must be on the table before anyone touches 5,000 benzene configurations.
