# Professor Review — 2026-08-23, Round 3

**Verdict: conditional green light for Phase 0a and Module 02 only. No approval yet for QM campaigns, P1, or Modules 04–08.**

## Blocking Findings

1. **The central experiment does not isolate representation.**  
   The field model receives additional CCSD density supervision through $L_\rho$; MACE receives only energies and forces. Therefore, the proposed comparison tests a *density-supervised field pipeline versus MACE*, not whether the field representation itself transfers better. Either weaken the research claim or add a field-model ablation without density supervision. See [Distilled_Project_Plan_and_Quality_Checks.md](Distilled_Project_Plan_and_Quality_Checks.md#L254-L264).

2. **Energy and force labels may be mutually inconsistent.**  
   The fallback combines CCSD(T) energies with CCSD forces. A conservative model cannot generally fit forces that are not derivatives of its energy labels, especially at the proposed $1\,\mathrm{meV/Å}$ threshold. Phase 0b needs an explicit gate comparing chosen force labels against finite differences of CCSD(T) energies. See [Distilled_Project_Plan_and_Quality_Checks.md](Distilled_Project_Plan_and_Quality_Checks.md#L115-L120).

3. **Modules 04–06 have unresolved dataset eligibility risk.**  
   Module 04 explicitly lists Kaggle, UCI, Data.gov, and government portals as accepted sources. Modules 04–06 prohibit *synthetic* data, not merely AI-generated data. Publishing self-computed QM data on Zenodo does not itself prove eligibility. Obtain written mentor approval before generating expensive datasets. See [04_Applied_Machine_Learning.md](../CapstoneProjects/04_Applied_Machine_Learning.md#L438-L456), [05_Deep_Learning_Systems.md](../CapstoneProjects/05_Deep_Learning_Systems.md#L459-L469), and [06_Generative_AI_Applications.md](../CapstoneProjects/06_Generative_AI_Applications.md#L468-L478).

4. **Dipole supervision remains internally unfinished.**  
   The plan acknowledges that $L_\rho$ need not reproduce dipoles, then conditionally adds $L_\mu$ only after failure. That conflicts with the otherwise frozen four-term training specification. Define now how many QM dipoles and dipole derivatives are generated, at what theory level, and whether $L_\mu$ is pre-registered. See [Distilled_Project_Plan_and_Quality_Checks.md](Distilled_Project_Plan_and_Quality_Checks.md#L338-L343).

5. **“Chemically precise labels” are asserted rather than demonstrated.**  
   CCSD(T)/cc-pVTZ is a defined level, but not automatically a chemical-accuracy guarantee. The plan names comparison against a higher-level reference without specifying the method, geometries, sample count, or acceptance threshold. See [Distilled_Project_Plan_and_Quality_Checks.md](Distilled_Project_Plan_and_Quality_Checks.md#L333-L335).

6. **The calendar remains non-operational.**  
   $T_0$, deadlines, and available hours are blank. Until these are filled, the claimed 26–30-week feasibility cannot be evaluated. See [Capstone_Mapping.md](Capstone_Mapping.md#L303-L313).

## What Passed

All four numerical probes execute successfully. They confirm the 800-row statistical design, gate-unit conversions, reference-density split, dipole calculation, and translation/rotation artifact estimates. Module 06’s geometry VAE is also explicitly allowed as “representation learning” by its rubric.

## Approval Conditions

I will give the full green light only after:

1. The six issues above are closed in the specification.
2. Phase 0b supplies measured H₂O and benzene timing, memory, label-consistency, and real-density results.
3. The resulting calendar proves that the selected shrink-ladder rung fits.
4. Written mentor approval confirms the Module 04–06 datasets are rubric-eligible.

The project is intellectually serious and unusually honest about failure. Its remaining weaknesses are concentrated and fixable, but they currently affect the validity of the main conclusion, not merely presentation.
