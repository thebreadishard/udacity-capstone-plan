# Probe M1 — arms against canonical CCSD(T) — benzene cc-pvtz, arm energy = e_corr_lno_ccsd_t, 2026-09-08 17:31, Asus18 (WSL)

Difference E_arm − E_canonical (same DF-RHF reference, frozen core) at each point; fitted per mode as a degree-4 polynomial in q. σ = residual about that fit (the arm's roughness against the truth). a2, a4 = even-part coefficients of the difference (a0 + a2 q² + a4 q⁴ fitted to ½[d(q)+d(−q)]); **2·a2 is the bias the arm puts on the CC curvature** of the mode, given also in cm⁻¹ (E = ½ ω q²). Absolute energies sealed (`canonical_truth_sealed.json`), not printed.

| mode | family | ω (cm⁻¹) | arm | n | σ about deg-4 fit (µE_h) | a2 (µE_h) | a4 (µE_h) | curvature bias 2·a2 (µE_h) | ≈ Δω (cm⁻¹) | d(±1) even (µE_h) | d(±0.5) even (µE_h) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 6 | CH-oop | 865 | A | 9 | 0.010 | +74.23 | -2.53 | +148.45 | +32.58 | +71.70 | +18.41 |
| 6 | CH-oop | 865 | B | 9 | 0.887 | +7.43 | +5.02 | +14.86 | +3.26 | +12.49 | +1.41 |
| 6 | CH-oop | 865 | C | 9 | 0.936 | +12.76 | -4.75 | +25.52 | +5.60 | +7.40 | +1.44 |
| 12 | CH-ip-bend | 1020 | A | 9 | 0.002 | +8.10 | +0.01 | +16.20 | +3.56 | +8.11 | +2.02 |
| 12 | CH-ip-bend | 1020 | B | 9 | 0.999 | -9.73 | +11.50 | -19.45 | -4.27 | +2.00 | -1.62 |
| 12 | CH-ip-bend | 1020 | C | 9 | 3.410 | +25.98 | -17.51 | +51.96 | +11.40 | +12.40 | +9.61 |
| 18 | CC-stretch | 1357 | A | 9 | 0.021 | +23.96 | +0.01 | +47.91 | +10.52 | +23.95 | +5.96 |
| 18 | CC-stretch | 1357 | B | 9 | 2.328 | +25.71 | -18.82 | +51.43 | +11.29 | +7.20 | +3.53 |
| 18 | CC-stretch | 1357 | C | 9 | 1.320 | +42.33 | -24.40 | +84.67 | +18.58 | +19.29 | +10.04 |

Reading aid: an arm with small σ is smooth; an arm with small |2·a2| is unbiased. The pipeline needs both. Arm A holds the reference frozen spaces at every q; B transports the occupied LMOs and re-selects LNOs; C is fresh. No verdict (the τ it would be judged against does not exist yet). Printed by probes/m1_canonical_truth.py.