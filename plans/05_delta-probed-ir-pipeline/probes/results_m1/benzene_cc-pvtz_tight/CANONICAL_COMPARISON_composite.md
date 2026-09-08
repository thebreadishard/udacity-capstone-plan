# Probe M1 — arms against canonical CCSD(T) — benzene cc-pvtz, arm energy = e_corr_composite, 2026-09-08 17:31, Asus18 (WSL)

Difference E_arm − E_canonical (same DF-RHF reference, frozen core) at each point; fitted per mode as a degree-4 polynomial in q. σ = residual about that fit (the arm's roughness against the truth). a2, a4 = even-part coefficients of the difference (a0 + a2 q² + a4 q⁴ fitted to ½[d(q)+d(−q)]); **2·a2 is the bias the arm puts on the CC curvature** of the mode, given also in cm⁻¹ (E = ½ ω q²). Absolute energies sealed (`canonical_truth_sealed.json`), not printed.

| mode | family | ω (cm⁻¹) | arm | n | σ about deg-4 fit (µE_h) | a2 (µE_h) | a4 (µE_h) | curvature bias 2·a2 (µE_h) | ≈ Δω (cm⁻¹) | d(±1) even (µE_h) | d(±0.5) even (µE_h) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 6 | CH-oop | 865 | A | 9 | 0.007 | +2.13 | -0.04 | +4.26 | +0.94 | +2.09 | +0.54 |
| 6 | CH-oop | 865 | B | 9 | 0.193 | +7.25 | -0.80 | +14.51 | +3.18 | +6.50 | +1.64 |
| 6 | CH-oop | 865 | C | 9 | 1.472 | +11.82 | -4.11 | +23.63 | +5.19 | +6.77 | +0.43 |
| 12 | CH-ip-bend | 1020 | A | 9 | 0.002 | +0.14 | +0.02 | +0.27 | +0.06 | +0.15 | +0.03 |
| 12 | CH-ip-bend | 1020 | B | 9 | 0.170 | -1.58 | +1.37 | -3.15 | -0.69 | -0.20 | -0.39 |
| 12 | CH-ip-bend | 1020 | C | 9 | 3.412 | +21.63 | -18.53 | +43.25 | +9.49 | +7.19 | +8.67 |
| 18 | CC-stretch | 1357 | A | 9 | 0.021 | +3.61 | +0.10 | +7.21 | +1.58 | +3.69 | +0.88 |
| 18 | CC-stretch | 1357 | B | 9 | 0.394 | -2.39 | +10.68 | -4.78 | -1.05 | +8.50 | +0.64 |
| 18 | CC-stretch | 1357 | C | 9 | 0.677 | -1.09 | +9.51 | -2.17 | -0.48 | +8.82 | +1.35 |

Reading aid: an arm with small σ is smooth; an arm with small |2·a2| is unbiased. The pipeline needs both. Arm A holds the reference frozen spaces at every q; B transports the occupied LMOs and re-selects LNOs; C is fresh. No verdict (the τ it would be judged against does not exist yet). Printed by probes/m1_canonical_truth.py.