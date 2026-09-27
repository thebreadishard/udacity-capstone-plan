# E7 / rung B — pairwise local force-constant terms, learned and projected (2026-09-27 20:03)

498 molecules; hold-out (a) 10 layer-A molecules, (b) scaffold cores ['fluoranthene', 'fluorene'] (39); pool 175; sizes [175]; seeds [0, 1, 2]; 60 epochs; 66 pair features; pattern pairs per molecule 414–4712. RMS in cm⁻¹; MLP mean over seeds.

| n | hold-out | model | diag CH-stretch | diag CH-oop | diag ring-ip | diag other | ring coupling RMS / zero | ratio | ring block / median | corrected ω RMS (zero) | overlap | ΔH residual |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 175 | (a) | zero rule | 43.60 | 23.75 | 19.69 | 13.21 | 3.76 / 3.76 | **1.00** | 10.99 / 2.89 | 23.29 (23.29) | 0.998 | 1.00 |
| 175 | (a) | B1 MLP | 1.36 | 5.13 | 4.54 | 6.14 | 1.62 / 3.76 | **0.43** | 0.86 / 2.89 | 4.71 (23.29) | 0.998 | 0.25 |
| 175 | (a) | B2 GBT | 5.36 | 7.99 | 6.05 | 6.58 | 1.75 / 3.76 | **0.46** | 1.64 / 2.89 | 6.17 (23.29) | 0.998 | 0.32 |
| 175 | (b) | zero rule | 44.30 | 25.32 | 19.93 | 19.18 | 3.74 / 3.74 | **1.00** | 13.23 / 1.14 | 23.09 (23.09) | 0.986 | 1.00 |
| 175 | (b) | B1 MLP | 2.81 | 6.08 | 4.85 | 6.94 | 1.76 / 3.74 | **0.47** | 1.10 / 1.14 | 5.16 (23.09) | 0.993 | 0.31 |
| 175 | (b) | B2 GBT | 6.02 | 9.07 | 6.29 | 11.90 | 1.83 / 3.74 | **0.49** | 2.14 / 1.14 | 6.66 (23.09) | 0.994 | 0.36 |

## Readings (pre-registered)

- B1 MLP ring coupling ratio vs n: (a) 175: 0.43 (slope +nan); (b) 175: 0.47 (slope +nan)
- Verdict at n = 175: ratio (a) 0.43, (b) 0.47, slope (a) +nan → **between** (win: ≤ 0.6 on both and a negative slope; lose: ≥ 0.9 on (a))

Total 212 s.
