# E7 / rung B — pairwise local force-constant terms, learned and projected (2026-09-30 21:04)

799 molecules; hold-out (a) 43 layer-A molecules, (b) scaffold cores ['fluoranthene', 'fluorene'] (39); pool 574; sizes [574]; seeds [0, 1, 2]; 60 epochs; 66 pair features; pattern pairs per molecule 414–4712. RMS in cm⁻¹; MLP mean over seeds.

| n | hold-out | model | diag CH-stretch | diag CH-oop | diag ring-ip | diag other | ring coupling RMS / zero | ratio | ring block / median | corrected ω RMS (zero) | overlap | ΔH residual |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 574 | (a) | zero rule | 43.71 | 23.81 | 20.10 | 19.91 | 4.34 / 4.34 | **1.00** | 10.99 / 4.07 | 23.47 (23.47) | 0.998 | 1.00 |
| 574 | (a) | B1 MLP | 1.14 | 5.65 | 7.71 | 13.70 | 2.72 / 4.34 | **0.63** | 1.89 / 4.07 | 6.12 (23.47) | 0.998 | 0.41 |
| 574 | (a) | B2 GBT | 3.53 | 8.26 | 8.89 | 15.19 | 2.79 / 4.34 | **0.64** | 2.13 / 4.07 | 6.98 (23.47) | 0.998 | 0.46 |
| 574 | (b) | zero rule | 44.30 | 25.32 | 19.93 | 19.18 | 3.74 / 3.74 | **1.00** | 13.23 / 1.24 | 23.09 (23.09) | 0.986 | 1.00 |
| 574 | (b) | B1 MLP | 2.02 | 6.69 | 5.82 | 7.87 | 2.60 / 3.74 | **0.70** | 1.12 / 1.24 | 5.27 (23.09) | 0.989 | 0.48 |
| 574 | (b) | B2 GBT | 4.27 | 8.89 | 6.57 | 11.49 | 2.23 / 3.74 | **0.60** | 1.57 / 1.24 | 6.34 (23.09) | 0.992 | 0.42 |
| 574 | (c) | zero rule | 44.09 | 22.68 | 20.39 | 19.12 | 3.95 / 3.95 | **1.00** | 13.80 / 1.33 | 22.85 (22.85) | 0.989 | 1.00 |
| 574 | (c) | B1 MLP | 1.14 | 5.46 | 6.70 | 5.99 | 2.70 / 3.95 | **0.68** | 0.97 / 1.33 | 5.44 (22.85) | 0.992 | 0.47 |
| 574 | (c) | B2 GBT | 3.80 | 8.11 | 8.34 | 11.83 | 2.78 / 3.95 | **0.70** | 1.94 / 1.33 | 6.92 (22.85) | 0.993 | 0.51 |

## Readings (pre-registered)

- B1 MLP ring coupling ratio vs n: (a) 574: 0.63 (slope +nan); (b) 574: 0.70 (slope +nan)
- Verdict at n = 574: ratio (a) 0.63, (b) 0.70, slope (a) +nan → **between** (win: ≤ 0.6 on both and a negative slope; lose: ≥ 0.9 on (a))

Total 279 s.
