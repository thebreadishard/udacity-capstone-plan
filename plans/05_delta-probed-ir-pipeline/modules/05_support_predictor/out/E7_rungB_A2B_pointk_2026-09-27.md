# E7 / rung B — pairwise local force-constant terms, learned and projected (2026-09-27 20:03)

498 molecules; hold-out (a) 10 layer-A molecules, (b) scaffold cores ['fluoranthene', 'fluorene'] (39); pool 449; sizes [449]; seeds [0, 1, 2]; 60 epochs; 66 pair features; pattern pairs per molecule 414–4712. RMS in cm⁻¹; MLP mean over seeds.

| n | hold-out | model | diag CH-stretch | diag CH-oop | diag ring-ip | diag other | ring coupling RMS / zero | ratio | ring block / median | corrected ω RMS (zero) | overlap | ΔH residual |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 449 | (a) | zero rule | 43.60 | 23.75 | 19.69 | 13.21 | 3.76 / 3.76 | **1.00** | 10.99 / 3.31 | 23.29 (23.29) | 0.998 | 1.00 |
| 449 | (a) | B1 MLP | 2.42 | 4.57 | 4.66 | 6.26 | 1.61 / 3.76 | **0.43** | 0.71 / 3.31 | 4.70 (23.29) | 0.998 | 0.26 |
| 449 | (a) | B2 GBT | 4.35 | 7.15 | 5.95 | 6.39 | 1.80 / 3.76 | **0.48** | 1.73 / 3.31 | 5.85 (23.29) | 0.998 | 0.32 |
| 449 | (b) | zero rule | 44.30 | 25.32 | 19.93 | 19.18 | 3.74 / 3.74 | **1.00** | 13.23 / 1.07 | 23.09 (23.09) | 0.986 | 1.00 |
| 449 | (b) | B1 MLP | 4.70 | 5.50 | 4.54 | 7.54 | 1.73 / 3.74 | **0.46** | 0.77 / 1.07 | 5.22 (23.09) | 0.993 | 0.31 |
| 449 | (b) | B2 GBT | 5.37 | 8.23 | 6.13 | 11.41 | 1.97 / 3.74 | **0.53** | 1.82 / 1.07 | 6.34 (23.09) | 0.993 | 0.38 |

## Readings (pre-registered)

- B1 MLP ring coupling ratio vs n: (a) 449: 0.43 (slope +nan); (b) 449: 0.46 (slope +nan)
- Verdict at n = 449: ratio (a) 0.43, (b) 0.46, slope (a) +nan → **between** (win: ≤ 0.6 on both and a negative slope; lose: ≥ 0.9 on (a))

Total 351 s.
