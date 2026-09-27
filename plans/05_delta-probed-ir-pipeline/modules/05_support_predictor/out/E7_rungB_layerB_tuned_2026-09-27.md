# E7 / rung B — pairwise local force-constant terms, learned and projected (2026-09-27 18:33)

498 molecules; hold-out (a) 42 layer-A molecules, (b) scaffold cores ['fluoranthene', 'fluorene'] (39); pool 274; sizes [274]; seeds [0, 1, 2]; 60 epochs; 66 pair features; pattern pairs per molecule 414–4712. RMS in cm⁻¹; MLP mean over seeds.

| n | hold-out | model | diag CH-stretch | diag CH-oop | diag ring-ip | diag other | ring coupling RMS / zero | ratio | ring block / median | corrected ω RMS (zero) | overlap | ΔH residual |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 274 | (a) | zero rule | 43.71 | 23.88 | 20.09 | 19.95 | 4.35 / 4.35 | **1.00** | 10.97 / 4.05 | 23.45 (23.45) | 0.997 | 1.00 |
| 274 | (a) | B1 MLP | 1.58 | 4.86 | 7.36 | 13.57 | 2.55 / 4.35 | **0.59** | 1.78 / 4.05 | 5.85 (23.45) | 0.998 | 0.39 |
| 274 | (a) | B2 GBT | 3.72 | 7.88 | 8.57 | 15.23 | 2.72 / 4.35 | **0.63** | 2.05 / 4.05 | 6.83 (23.45) | 0.998 | 0.45 |
| 274 | (b) | zero rule | 44.30 | 25.32 | 19.93 | 19.18 | 3.74 / 3.74 | **1.00** | 13.23 / 1.19 | 23.09 (23.09) | 0.986 | 1.00 |
| 274 | (b) | B1 MLP | 1.88 | 5.14 | 6.07 | 7.65 | 2.41 / 3.74 | **0.65** | 1.39 / 1.19 | 5.18 (23.09) | 0.990 | 0.43 |
| 274 | (b) | B2 GBT | 4.69 | 8.32 | 6.13 | 11.26 | 2.09 / 3.74 | **0.56** | 1.36 / 1.19 | 6.16 (23.09) | 0.993 | 0.39 |
| 274 | (c) | zero rule | 44.09 | 22.68 | 20.39 | 19.12 | 3.95 / 3.95 | **1.00** | 13.80 / 1.32 | 22.85 (22.85) | 0.989 | 1.00 |
| 274 | (c) | B1 MLP | 1.15 | 4.74 | 6.27 | 5.34 | 2.58 / 3.95 | **0.65** | 0.82 / 1.32 | 5.01 (22.85) | 0.993 | 0.45 |
| 274 | (c) | B2 GBT | 3.96 | 7.75 | 8.02 | 12.05 | 2.77 / 3.95 | **0.70** | 1.70 / 1.32 | 6.75 (22.85) | 0.993 | 0.50 |

## Readings (pre-registered)

- B1 MLP ring coupling ratio vs n: (a) 274: 0.59 (slope +nan); (b) 274: 0.65 (slope +nan)
- Verdict at n = 274: ratio (a) 0.59, (b) 0.65, slope (a) +nan → **between** (win: ≤ 0.6 on both and a negative slope; lose: ≥ 0.9 on (a))

Total 2817 s.
