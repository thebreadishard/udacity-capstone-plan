# Probe M1 — arms against canonical CCSD(T) — benzene cc-pvdz, arm energy = e_corr_lno_ccsd_t, 2026-09-06 02:06, Asus18 (WSL)

Difference E_arm − E_canonical (same DF-RHF reference, frozen core) at each point; fitted per mode as a degree-4 polynomial in q. σ = residual about that fit (the arm's roughness against the truth). a2, a4 = even-part coefficients of the difference (a0 + a2 q² + a4 q⁴ fitted to ½[d(q)+d(−q)]); **2·a2 is the bias the arm puts on the CC curvature** of the mode, given also in cm⁻¹ (E = ½ ω q²). Absolute energies sealed (`canonical_truth_sealed.json`), not printed.

| mode | family | ω (cm⁻¹) | arm | n | σ about deg-4 fit (µE_h) | a2 (µE_h) | a4 (µE_h) | curvature bias 2·a2 (µE_h) | ≈ Δω (cm⁻¹) | d(±1) even (µE_h) | d(±0.5) even (µE_h) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 6 | CH-oop | 865 | A | 9 | 0.002 | +4.41 | -0.03 | +8.83 | +1.94 | +4.39 | +1.10 |
| 6 | CH-oop | 865 | B | 9 | 0.052 | -0.28 | +1.05 | -0.57 | -0.13 | +0.72 | -0.09 |
| 6 | CH-oop | 865 | C | 9 | 2.111 | +14.28 | -5.68 | +28.56 | +6.27 | +7.26 | -0.04 |
| 12 | CH-ip-bend | 1020 | A | 9 | 0.003 | +0.79 | +0.02 | +1.58 | +0.35 | +0.81 | +0.19 |
| 12 | CH-ip-bend | 1020 | B | 9 | 1.249 | +7.87 | -6.22 | +15.75 | +3.46 | +1.80 | +2.56 |
| 12 | CH-ip-bend | 1020 | C | 9 | 2.744 | +20.78 | -15.76 | +41.57 | +9.12 | +7.66 | +6.27 |
| 18 | CC-stretch | 1357 | A | 9 | 0.056 | +2.38 | -0.02 | +4.77 | +1.05 | +2.31 | +0.56 |
| 18 | CC-stretch | 1357 | B | 9 | 0.900 | +9.55 | -4.20 | +19.09 | +4.19 | +6.14 | +2.53 |
| 18 | CC-stretch | 1357 | C | 9 | 0.943 | +6.42 | -4.74 | +12.85 | +2.82 | +2.82 | +2.59 |

Reading aid: an arm with small σ is smooth; an arm with small |2·a2| is unbiased. The pipeline needs both. Arm A holds the reference frozen spaces at every q; B transports the occupied LMOs and re-selects LNOs; C is fresh. No verdict (the τ it would be judged against does not exist yet). Printed by probes/m1_canonical_truth.py.