# Critical Professor Review — Round 1 (2026-08-22)

**Status:** No green light yet. Blocking issues 1–6 are closed **in spec** (separate commits). Pass 6 and the Phase 0 measured addendum remain. Round 2 adds blocking issues 7–15: see [Professor_Review_2026-08-22_Round2.md](Professor_Review_2026-08-22_Round2.md).

**Scope reviewed:** [Overarching_Goal.md](Overarching_Goal.md), [Distilled_Project_Plan_and_Quality_Checks.md](Distilled_Project_Plan_and_Quality_Checks.md), [Capstone_Mapping.md](Capstone_Mapping.md), and the module rubrics in [`../../../Rubrics/`](../../../Rubrics/). Pass 6 of the mapping is still open; that matches this judgment.

This is a serious plan, not a costume. It is worth supervising. It is not yet stamped ready to execute.

---

## What already meets a high bar

The intellectual hygiene is unusually good for a master’s-scale proposal.

The plan survived a real critique loop and kept the scars. Route A (density-as-force-source), spectral training loss, periodic Poisson, “egg-box eliminated,” rovibrational line-list claims, naphthalene as a scored milestone, and large-PAH chemical precision are all explicitly forbidden. That is how a thesis stays honest.

The research question in Distilled Plan §2 is now falsifiable: does a 3D field PES beat an atomistic equivariant GNN on transferability, from which IR bands emerge? That is a thesis. “Universal CA for arbitrary PAHs” was not.

Energy-first Route B with autograd forces is the correct physical constraint. Emergent spectroscopy with frozen weights is the correct scientific constraint. The §8 QA list and the three-way error decomposition (ML vs electronic-structure vs nuclear-motion) are what a methods chapter should demand.

The capstone mapping is not busywork theater. QM9 as a negative control, Phase 0 as the statistics project, the non-field baseline as Module 04, local-CNN vs FNO as a real ablation, and the agent as a phase-gate tool rather than a chatbot are all defensible. The A/B/C/D tags and the report-wording action items show an understanding of how this dies: not in the math, but in one sloppy sentence to a grader.

The project deserves a high standard because the *standards already on the page* are those of a careful computational chemist. The remaining problems are not taste. They are holes that will break either the science or the degree if coding starts now.

---

## Blocking issues

### 1. Phase 1 has no owner

**Status (2026-08-22):** Addressed in mapping — ungraded [Workstream P1](Capstone_Mapping.md#41-workstream-p1--h₂o-fno-nca-pes-resolves-professor-review-blocking-issue-1). Not closed as a scientific issue until P1 actually exists as code; the *ownership* hole is closed.

This is the structural failure.

The Distilled Plan’s first real ML result is an H₂O field PES (Phase 1). Phases 2 and 3 — emergent IR, D₂O isotope shift, CO₂ selection rules — are defined on **that** frozen model.

The mapping does something else:

- Module 04 trains the **simple non-field baseline** on H₂O descriptors.
- Module 05 trains the **hybrid FNO-NCA on benzene**.
- Module 07 *assumes* “Phase 1 H₂O training” already exists.

So the model that justifies the flagship physical proofs is extra-curricular. Either Phase 1 is a large ungraded software project hiding between 04 and 07, or 07 will demo gates on a model nobody was assigned to train. A roadmap whose critical path is off the map does not get a green light.

### 2. The energy is not yet a functional of the field

**Status (2026-08-22):** Addressed in the Distilled Plan — implementable forward pass in §6.1, fossils deleted in §3, Hockney–Eastwood vs FNO split in §6.2. Not closed as a scientific issue until P1/05 code matches that graph; the *spec* hole is closed.

Route B is written as

\[
E_\theta(\mathbf{R})=\mathcal{E}[\rho_\theta(\mathbf{r};\mathbf{R}),\mathbf{R}].
\]

That equation is the hypothesis. The implementation sketch does not enforce it. If energy is a separate head that can ignore \(\rho\), the result is a voxelized regressor with an auxiliary density loss. That does **not** test “continuous 3D neural field vs atomistic GNN.” It tests “3D CNN energy model vs SOAP/KRR,” which is a weaker and already crowded question.

Until \(\mathcal{E}\) is specified — a learned functional of \(\rho\), a physics-inspired functional of \(\rho\), or an explicit hybrid — the architecture is still a slogan.

Related leftover: Distilled Plan §3 still carries \(\rho_{Re},\rho_{Im}\) and \(E_x,E_y,E_z\) photon channels from the rejected Ehrenfest/photon story. A Born–Oppenheimer PES has a real, non-negative density. Those channels are not conservative-mechanics. Delete them or justify them with an equation. Do not leave fossils in the spec.

Same ambiguity for the long-range piece: is Hockney–Eastwood a **fixed** isolated-molecule Poisson layer, or is the FNO a **learned** replacement? Phase 0 validates the former; Module 05 ablates the latter. Pick one primary object and say what the other one is for.

### 3. The data-generation claim is not yet a method

**Status (2026-08-22):** Addressed in spec — Distilled Plan [§5.1](Distilled_Project_Plan_and_Quality_Checks.md#51-data-generation-method-resolves-professor-review-blocking-issue-3) is now a method (which 1-RDM, which force, how many Hessians), with a 10-geometry cost pilot as a Phase 0 exit, a shrink ladder, and a Phase 1 force gate that sits above a measured noise floor. Mapping 04/P1/05 now say “per §5.1,” not “CCSD(T) everything via PySCF.” Not closed as a scientific issue until the smoke-test table and the 10-geometry numbers exist; the *methods* hole is closed.

“Exact CCSD(T)/cc-pVTZ density, forces, Hessian via PySCF” for \(\ge 2000\) H₂O and \(\ge 5000\) benzene configs is written as if it were a download.

It is not. The plan needs, in writing:

- which 1-RDM (relaxed vs unrelaxed) is the density target, and which code path produces it;
- whether forces are analytic CCSD(T) gradients or finite-difference, and the cost of each;
- where Hessians actually come from (selected stationary points only — say how many);
- a **measured** cost model after a 10-geometry benzene pilot, not a hope that local hardware will suffice.

Not applying for HPC on day one is correct. Treating 5000 benzene CCSD(T) volumetric fields as a scheduling footnote is not. That is the long pole of the entire degree. If the pilot says it is impossible locally, the plan must shrink **now** (fewer configs, smaller grid, H₂O-only field model, density from a cheaper but documented proxy with CCSD(T) energies/forces only) rather than fail in Module 05.

The Phase 1 force gate of \(<1\,\text{meV/Å}\) is also tighter than is acceptable as a Go/No-Go until it is shown to sit above the numerical noise floor (CCSD(T) gradient accuracy, egg-box residual, grid error). A gate that cannot be measured is not a gate.

### 4. Two governing documents still disagree

**Status (2026-08-22):** Addressed in spec — [Overarching_Goal.md](Overarching_Goal.md) rewritten. Labels (CCSD(T)/cc-pVTZ per Distilled Plan §5.1) are split from spectra (Distilled Plan §9 band envelopes). “Sub-wavenumber” is no longer a dataset requirement. Module 08’s product is named: reliability-gated small-molecule IR emulation plus a yes/no on the representation hypothesis. Horizon PAH work is post-master’s [Projects 10–12](Horizon/10_Size_Extensive_Aromatic_PES.md), not a slogan in the prime directive. Not closed as a *cultural* issue until Module 08 drafts stop quoting the old title; the *document* hole is closed.

[Overarching_Goal.md](Overarching_Goal.md) still promises “chemically precise anharmonic infrared **spectral lines**” and “sub-wavenumber precision.” Distilled Plan §9 correctly forbids that claim for classical MD + FFT.

That is not a wording nit. It is the prime directive versus the methods chapter. A reader — or a later Module 08 draft — will quote the older sentence. Update the goal document to §9’s defensible language, or treat the project as not yet self-consistent.

### 5. Three rubric landmines are still live

**Status (2026-08-22):** Addressed in spec — mapping Pass 3 Module 06 rewritten; Pass 4 Module 03 is \(\ge 500\) (target 800) with categorical `sigma_over_dx`; §5.5 makes Zenodo DOI a **gate** before the source sentence for 03/04/05/06. Not closed as a *submission* issue until the DOIs exist; the *spec* hole is closed. The GNN half of the original stamp item 5 is **issue 6** (closed in spec via G1).

These are not “remember to phrase it nicely.” They can fail a module even if the science is good.

**Module 03.** The rubric needs \(\ge 500\) rows, \(\ge 6\) columns, a categorical/grouping variable, public source, and “not synthetic.” The planned sweep table is “several hundred” rows. That may already fail the count. Self-generated numerical QA data is also the easiest thing for a grader to call synthetic. Zenodo-before-submission is necessary here, not only for Module 04. Encode a real grouping factor (e.g. \(\sigma/\Delta x\) as a categorical factor) and commit to \(\ge 500\) rows in the spec.

**Module 06.** Pass 3 still says “VAE on CCSD(T) benzene configs.” Pass 4/5 says a cheap independent aromatic corpus. Those cannot both be true. The rubric also frames VAE as image/representation learning. A 3D-coordinate VAE can be defended, but only if the task is frozen as **representation learning over geometries**, samples are shown, and generated geometries never enter the real train/val/test set without a fresh CCSD(T) label. The Pass 3/4 contradiction must be deleted, not “understood privately.”

**Module 04/05 “public, not synthetic.”** Publishing H₂O CCSD(T) with a DOI is the right mitigation. Do it **before** the notebook claims a source link. Do not argue with the grader that PySCF is “not AI.” Put the sentence in the report and put the files on the internet.

### 6. The comparison that tests the thesis is in the wrong module

**Status (2026-08-22):** Addressed in spec — [Workstream G1](Capstone_Mapping.md#42-workstream-g1--equivariant-atomistic-pes-resolves-professor-review-blocking-issue-6) owns MACE (NequIP fallback) on the same P1/05 split manifests. Distilled Plan §7 Phase 4 primary gate is leave-one-mode-out vs G1. Module 08 assembles; it does not train. D₂O stays Phase 3 sanity. Not closed as a scientific issue until G1 weights exist; the *ownership* hole is closed.

The scientific claim is field vs atomistic GNN. Module 05 only compares local CNN vs CNN+FNO on benzene. That is a good ablation of **this** architecture. It does not answer the research question.

MACE/NequIP vs FNO-NCA is deferred to Module 08, where it will be rushed and under-trained if it is treated as synthesis narrative. Either the GNN baseline is a first-class experiment with the same splits and the same H₂O/benzene labels, or the central question must be weakened. Transferability superiority cannot be claimed from an ablation that never trained the competitor.

Also be modest about D₂O: \(F/m\) isotope shifts are almost automatic for any vaguely correct PES. It is a necessary sanity check, not the flagship proof that the field representation learned physics.

---

## What is not blocking, but will be if handled sloppily

- CNN-family framing for 3D local convolutions is acceptable. Write it once, clearly, in the Module 05 report.
- JWST/PAH “industry” framing is acceptable as motivation. It is not acceptable as a capability that was built. Module 08 must sell **reliability-gated spectral emulation for small molecules**, with PAH identification as future work.
- Leave-one-mode-out and configuration-level splits are correct. Do not later “augment” by sampling nearby points from the same MD trajectory and call it i.i.d.
- Consumer-hardware-first is a good management choice only if the benzene pilot can kill the 64³ / 5000-config design without shame.

---

## What would earn a stamp

A **conditional green light to begin Phase 0 only** after a short addendum (one document, not another chat) that does all of the following:

1. Assign Phase 1 to a named workstream: either it is in-scope for a module (and the mapping says so), or it is an explicit ungraded prerequisite with a date and a failure mode.
2. Write \(E=\mathcal{E}[\rho,R]\) as an implementable functional; remove or justify \(\rho_{Im}\) and EM channels; state whether Poisson is fixed Hockney–Eastwood or learned FNO.
3. ~~Replace “CCSD(T) densities/forces/Hessians via PySCF” with a methods paragraph plus a 10-geometry benzene cost pilot as a Phase 0 exit criterion.~~ **Done in spec** (Distilled Plan §5.1, 2026-08-22). Still needs measured pilot numbers before it is closed as science.
4. ~~Reconcile [Overarching_Goal.md](Overarching_Goal.md) with Distilled Plan §9.~~ **Done in spec** (Overarching Goal rewrite + README/mapping satellites, 2026-08-22). Horizon remainder is Projects 10–12, not Module 08.
5. ~~Fix the Module 03 row count/source rule and collapse the Module 06 dataset contradiction.~~ **Done in spec** (mapping Pass 3/4 + §5.5, 2026-08-22). Still needs live DOIs before it is closed as a submission.
6. ~~Put the GNN baseline on the critical path rather than in the synthesis appendix.~~ **Done in spec** (mapping §4.2 Workstream G1 + Distilled Plan §7 Phase 4, 2026-08-22). Still needs G1 weights and the leave-one-mode-out table before it is closed as science.

The six *spec* holes in this stamp list are closed. **Pass 6** (module-by-module sign-off) is still open. **No green light** to start the expensive parts until Pass 6 and the Phase 0 addendum (smoke-test table + 10-geometry numbers) exist. The project is good enough to deserve that standard. It is not yet good enough to start the expensive parts.
