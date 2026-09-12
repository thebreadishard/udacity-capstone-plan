# Probe M1 — arms against canonical CCSD(T) — benzene cc-pvtz, arm energy = e_corr_composite, 2026-09-12 11:53, Asus18 (WSL)

Difference E_arm − E_canonical (same DF-RHF reference, frozen core) at each point; fitted per mode as a degree-4 polynomial in q. σ = residual about that fit (the arm's roughness against the truth). a2, a4 = even-part coefficients of the difference (a0 + a2 q² + a4 q⁴ fitted to ½[d(q)+d(−q)]); **2·a2 is the bias the arm puts on the CC curvature** of the mode; the frequency bias is **a2** in cm⁻¹ (E = ½ ω q²: the curvature is ω and a curvature difference is twice the frequency shift — column corrected 2026-09-10, earlier reports gave 2·a2 here). Absolute energies sealed (`canonical_truth_sealed.json`), not printed.

| mode | family | ω (cm⁻¹) | arm | n | σ about deg-4 fit (µE_h) | a2 (µE_h) | a4 (µE_h) | curvature bias 2·a2 (µE_h) | frequency bias Δω = a2 (cm⁻¹) | d(±1) even (µE_h) | d(±0.5) even (µE_h) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 6 | CH-oop | 865 | A | 9 | 0.004 | +0.52 | +0.02 | +1.04 | +0.11 | +0.54 | +0.14 |
| 12 | CH-ip-bend | 1020 | A | 9 | 0.003 | -0.06 | +0.03 | -0.12 | -0.01 | -0.03 | -0.02 |
| 18 | CC-stretch | 1357 | A | 9 | 0.044 | +1.05 | +0.06 | +2.10 | +0.23 | +1.06 | +0.23 |

Reading aid: an arm with small σ is smooth; an arm with small |2·a2| is unbiased. The pipeline needs both. Arm A holds the reference frozen spaces at every q; B transports the occupied LMOs and re-selects LNOs; C is fresh. No verdict (the τ it would be judged against does not exist yet). Printed by probes/m1_canonical_truth.py.