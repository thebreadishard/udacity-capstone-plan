# Probe M1 — arms against canonical CCSD(T) — benzene cc-pvdz, arm energy = e_corr_composite, 2026-09-06 02:06, Asus18 (WSL)

Difference E_arm − E_canonical (same DF-RHF reference, frozen core) at each point; fitted per mode as a degree-4 polynomial in q. σ = residual about that fit (the arm's roughness against the truth). a2, a4 = even-part coefficients of the difference (a0 + a2 q² + a4 q⁴ fitted to ½[d(q)+d(−q)]); **2·a2 is the bias the arm puts on the CC curvature** of the mode, given also in cm⁻¹ (E = ½ ω q²). Absolute energies sealed (`canonical_truth_sealed.json`), not printed.

| mode | family | ω (cm⁻¹) | arm | n | σ about deg-4 fit (µE_h) | a2 (µE_h) | a4 (µE_h) | curvature bias 2·a2 (µE_h) | ≈ Δω (cm⁻¹) | d(±1) even (µE_h) | d(±0.5) even (µE_h) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 6 | CH-oop | 865 | A | 9 | 0.003 | +0.32 | -0.02 | +0.64 | +0.14 | +0.31 | +0.08 |
| 6 | CH-oop | 865 | B | 9 | 0.045 | -0.53 | +0.89 | -1.05 | -0.23 | +0.33 | -0.15 |
| 6 | CH-oop | 865 | C | 9 | 1.669 | +11.21 | -4.69 | +22.42 | +4.92 | +5.46 | -0.06 |
| 12 | CH-ip-bend | 1020 | A | 9 | 0.003 | +0.07 | +0.02 | +0.13 | +0.03 | +0.08 | +0.01 |
| 12 | CH-ip-bend | 1020 | B | 9 | 0.580 | +4.92 | -3.58 | +9.83 | +2.16 | +1.34 | +1.34 |
| 12 | CH-ip-bend | 1020 | C | 9 | 2.145 | +18.62 | -15.61 | +37.24 | +8.17 | +5.25 | +5.71 |
| 18 | CC-stretch | 1357 | A | 9 | 0.056 | +0.82 | -0.03 | +1.64 | +0.36 | +0.73 | +0.17 |
| 18 | CC-stretch | 1357 | B | 9 | 0.449 | +5.53 | -2.51 | +11.05 | +2.43 | +3.37 | +1.35 |
| 18 | CC-stretch | 1357 | C | 9 | 0.468 | +3.48 | -2.52 | +6.97 | +1.53 | +1.53 | +1.36 |

Reading aid: an arm with small σ is smooth; an arm with small |2·a2| is unbiased. The pipeline needs both. Arm A holds the reference frozen spaces at every q; B transports the occupied LMOs and re-selects LNOs; C is fresh. No verdict (the τ it would be judged against does not exist yet). Printed by probes/m1_canonical_truth.py.