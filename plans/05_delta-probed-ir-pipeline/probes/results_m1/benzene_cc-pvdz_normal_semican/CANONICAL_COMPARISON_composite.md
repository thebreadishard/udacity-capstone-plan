# Probe M1 — arms against canonical CCSD(T) — benzene cc-pvdz, arm energy = e_corr_composite, 2026-09-05 21:37, Asus18 (WSL)

Difference E_arm − E_canonical (same DF-RHF reference, frozen core) at each point; fitted per mode as a degree-4 polynomial in q. σ = residual about that fit (the arm's roughness against the truth). a2, a4 = even-part coefficients of the difference (a0 + a2 q² + a4 q⁴ fitted to ½[d(q)+d(−q)]); **2·a2 is the bias the arm puts on the CC curvature** of the mode, given also in cm⁻¹ (E = ½ ω q²). Absolute energies sealed (`canonical_truth_sealed.json`), not printed.

| mode | family | ω (cm⁻¹) | arm | n | σ about deg-4 fit (µE_h) | a2 (µE_h) | a4 (µE_h) | curvature bias 2·a2 (µE_h) | ≈ Δω (cm⁻¹) | d(±1) even (µE_h) | d(±0.5) even (µE_h) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 6 | CH-oop | 865 | A | 9 | 0.003 | +5.82 | -0.08 | +11.63 | +2.55 | +5.74 | +1.45 |
| 6 | CH-oop | 865 | B | 9 | 1.441 | -3.67 | +4.09 | -7.35 | -1.61 | +1.33 | +1.56 |
| 6 | CH-oop | 865 | C | 9 | 8.694 | +51.86 | -16.89 | +103.72 | +22.76 | +29.81 | -1.21 |
| 12 | CH-ip-bend | 1020 | A | 9 | 0.005 | +1.12 | -0.00 | +2.24 | +0.49 | +1.12 | +0.28 |
| 12 | CH-ip-bend | 1020 | B | 9 | 1.613 | -11.74 | +11.60 | -23.48 | -5.15 | -1.69 | -3.77 |
| 12 | CH-ip-bend | 1020 | C | 9 | 10.855 | +64.13 | -40.88 | +128.26 | +28.15 | +36.31 | +27.84 |
| 18 | CC-stretch | 1357 | A | 9 | 0.059 | +4.19 | -0.03 | +8.38 | +1.84 | +4.10 | +1.00 |
| 18 | CC-stretch | 1357 | B | 9 | 3.409 | +12.59 | -0.66 | +25.18 | +5.53 | +8.60 | -2.75 |
| 18 | CC-stretch | 1357 | C | 9 | 4.424 | +2.07 | +6.53 | +4.14 | +0.91 | +3.62 | -6.60 |

Reading aid: an arm with small σ is smooth; an arm with small |2·a2| is unbiased. The pipeline needs both. Arm A holds the reference frozen spaces at every q; B transports the occupied LMOs and re-selects LNOs; C is fresh. No verdict (the τ it would be judged against does not exist yet). Printed by probes/m1_canonical_truth.py.