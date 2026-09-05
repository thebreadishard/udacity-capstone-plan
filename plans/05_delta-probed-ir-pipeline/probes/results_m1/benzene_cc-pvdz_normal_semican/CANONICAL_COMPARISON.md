# Probe M1 — arms against canonical CCSD(T) — benzene cc-pvdz, arm energy = e_corr_lno_ccsd_t, 2026-09-05 21:37, Asus18 (WSL)

Difference E_arm − E_canonical (same DF-RHF reference, frozen core) at each point; fitted per mode as a degree-4 polynomial in q. σ = residual about that fit (the arm's roughness against the truth). a2, a4 = even-part coefficients of the difference (a0 + a2 q² + a4 q⁴ fitted to ½[d(q)+d(−q)]); **2·a2 is the bias the arm puts on the CC curvature** of the mode, given also in cm⁻¹ (E = ½ ω q²). Absolute energies sealed (`canonical_truth_sealed.json`), not printed.

| mode | family | ω (cm⁻¹) | arm | n | σ about deg-4 fit (µE_h) | a2 (µE_h) | a4 (µE_h) | curvature bias 2·a2 (µE_h) | ≈ Δω (cm⁻¹) | d(±1) even (µE_h) | d(±0.5) even (µE_h) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 6 | CH-oop | 865 | A | 9 | 0.002 | +62.92 | -0.67 | +125.84 | +27.62 | +62.25 | +15.69 |
| 6 | CH-oop | 865 | B | 9 | 6.638 | -23.02 | +18.40 | -46.04 | -10.10 | -0.40 | +5.63 |
| 6 | CH-oop | 865 | C | 9 | 8.944 | +13.88 | +11.46 | +27.76 | +6.09 | +21.36 | -8.18 |
| 12 | CH-ip-bend | 1020 | A | 9 | 0.005 | +12.11 | -0.01 | +24.21 | +5.31 | +12.10 | +3.03 |
| 12 | CH-ip-bend | 1020 | B | 9 | 7.442 | -50.02 | +49.68 | -100.05 | -21.96 | -7.47 | -16.67 |
| 12 | CH-ip-bend | 1020 | C | 9 | 10.741 | +63.00 | -27.60 | +126.01 | +27.66 | +46.31 | +24.81 |
| 18 | CC-stretch | 1357 | A | 9 | 0.059 | +27.57 | -0.01 | +55.14 | +12.10 | +27.50 | +6.85 |
| 18 | CC-stretch | 1357 | B | 9 | 10.546 | +63.83 | -19.81 | +127.67 | +28.02 | +35.85 | -2.52 |
| 18 | CC-stretch | 1357 | C | 9 | 11.108 | +45.59 | -11.01 | +91.17 | +20.01 | +25.24 | -7.84 |

Reading aid: an arm with small σ is smooth; an arm with small |2·a2| is unbiased. The pipeline needs both. Arm A holds the reference frozen spaces at every q; B transports the occupied LMOs and re-selects LNOs; C is fresh. No verdict (the τ it would be judged against does not exist yet). Printed by probes/m1_canonical_truth.py.