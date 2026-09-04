# Professor Review — 2026-08-23, Round 3

**Verdict: conditional green light for Phase 0a and Module 02 only. No approval yet for QM campaigns, P1, or Modules 04–08.**

## Blocking Findings

1. **The central experiment does not isolate representation.**  
   The field model receives additional CCSD density supervision through $L_\rho$; MACE receives only energies and forces. Therefore, the proposed comparison tests a *density-supervised field pipeline versus MACE*, not whether the field representation itself transfers better. Either weaken the research claim or add a field-model ablation without density supervision. See [Distilled_Project_Plan_and_Quality_Checks.md](Distilled_Project_Plan_and_Quality_Checks.md#L254-L264).

   **Status (2026-08-23): Addressed in spec.** The primary representation test is now equal-label **Field-EF vs MACE-EF**. A matched **Field-EFρ vs Field-EF** ablation measures the benefit of density supervision, and the fully supervised production model is reported separately from the causal representation claim. See the Distilled Plan §2, §6.3, §7 and §7.1. Not closed as science until the frozen comparison cohort has been trained and evaluated.

2. **Energy and force labels may be mutually inconsistent.**  
   The fallback combines CCSD(T) energies with CCSD forces. A conservative model cannot generally fit forces that are not derivatives of its energy labels, especially at the proposed $1\,\mathrm{meV/Å}$ threshold. Phase 0b needs an explicit gate comparing chosen force labels against finite differences of CCSD(T) energies. See [Distilled_Project_Plan_and_Quality_Checks.md](Distilled_Project_Plan_and_Quality_Checks.md#L115-L120).

   **Status (2026-08-23): Addressed in spec.** The Distilled Plan §5.1 now forbids mixed CCSD(T)-energy/CCSD-force labels. H₂O receives complete same-surface CCSD(T) gradients; benzene receives complete gradients when affordable or pre-seeded CCSD(T) directional derivatives under the measured fallback ladder. Phase 0b measures derivative consistency before campaign release. Not closed as science until that pilot passes.

3. **Modules 04–06 have unresolved dataset eligibility risk.**  
   Module 04 explicitly lists Kaggle, UCI, Data.gov, and government portals as accepted sources. Modules 04–06 prohibit *synthetic* data, not merely AI-generated data. Publishing self-computed QM data on Zenodo does not itself prove eligibility. Obtain written mentor approval before generating expensive datasets. See [04_Applied_Machine_Learning.md](../../../Rubrics/04_Applied_Machine_Learning.md#L438-L456), [05_Deep_Learning_Systems.md](../../../Rubrics/05_Deep_Learning_Systems.md#L459-L469), and [06_Generative_AI_Applications.md](../../../Rubrics/06_Generative_AI_Applications.md#L468-L478).

   **Status (2026-08-23): Open.** No wording change, repository publication or technical result substitutes for written mentor approval. Expensive dataset generation remains blocked on that approval.

4. **Dipole supervision remains internally unfinished.**  
   The plan acknowledges that $L_\rho$ need not reproduce dipoles, then conditionally adds $L_\mu$ only after failure. That conflicts with the otherwise frozen four-term training specification. Define now how many QM dipoles and dipole derivatives are generated, at what theory level, and whether $L_\mu$ is pre-registered. See [Distilled_Project_Plan_and_Quality_Checks.md](Distilled_Project_Plan_and_Quality_Checks.md#L338-L343).

   **Status (2026-08-23): Addressed in spec.** Analytic AO-basis dipoles from the pinned 1-RDM are now required for every density-labelled configuration, and $L_\mu$ is enabled from the first production run. Dipole derivatives have fixed evaluation-only counts; there is no post-hoc $L_{d\mu}$ or spectral-loss rescue. The equal-label comparison models receive no dipole supervision. See the Distilled Plan §5.1, §6.3, §6.4 and §7. Not closed as science until the untouched dipole gates pass.

5. **“Chemically precise labels” are asserted rather than demonstrated.**  
   CCSD(T)/cc-pVTZ is a defined level, but not automatically a chemical-accuracy guarantee. The plan names comparison against a higher-level reference without specifying the method, geometries, sample count, or acceptance threshold. See [Distilled_Project_Plan_and_Quality_Checks.md](Distilled_Project_Plan_and_Quality_Checks.md#L333-L335).

   **Status (2026-08-23): Addressed in spec.** Distilled Plan §5.1 now freezes an HPC-backed CCSD(T)/CBS(T,Q) audit with 19 H₂O, 13 CO₂ and 12 benzene geometries, quantitative energy/derivative/curvature gates, and a fail-closed claim ladder. “Chemically accurate” is allowed only relative to that declared reference and only for quantities whose gates pass; otherwise the claim remains “CCSD(T)/cc-pVTZ-level.” Not closed as science until the audit is completed.

6. **The calendar remains non-operational.**  
   $T_0$, deadlines, and available hours are blank. Until these are filled, the claimed 26–30-week feasibility cannot be evaluated. See [Capstone_Mapping.md](Capstone_Mapping.md#L303-L313).

   **Status (2026-08-23): Addressed in spec.** Mapping §8 now fixes $T_0$ as 2026-09-01, records the program as self-paced, and budgets 10 human hours/week separately from agent, compute and HPC queue time. The fixed-work baseline is 840 human hours, approximately 84 calendar weeks through 2028-04-11 before measured campaign and audit additions; the old 26–30-week claim is withdrawn. Estimates are re-baselined after 20 and 80 human hours and after campaign pilots. Not closed as execution until Phase 0b supplies the measured durations.

## What Passed

All four numerical probes execute successfully. They confirm the 800-row statistical design, gate-unit conversions, reference-density split, dipole calculation, and translation/rotation artifact estimates. Module 06’s geometry VAE is also explicitly allowed as “representation learning” by its rubric.

## Approval Conditions

The specification remedies for issues 1, 2, 4, 5 and 6 are accepted. I will give the full green light only after:

1. Phase 0b supplies measured H₂O and benzene timing, memory, label-consistency, and real-density results.
2. The resulting calendar proves that the selected shrink-ladder rung fits.
3. Written mentor approval closes issue 3 by confirming that the Module 04–06 datasets are rubric-eligible.

The project is intellectually serious and unusually honest about failure. Its remaining weaknesses are concentrated and fixable, but they currently affect the validity of the main conclusion, not merely presentation.
