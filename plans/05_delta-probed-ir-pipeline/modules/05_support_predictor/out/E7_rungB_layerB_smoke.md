# E7 / rung B — pairwise local force-constant terms, learned and projected (2026-09-25 19:31) — SMOKE, NOT A RESULT

284 molecules; hold-out (a) 42 layer-A molecules, (b) scaffold cores ['fluoranthene', 'fluorene'] (39); pool 60; sizes [60]; seeds [0]; 2 epochs; 66 pair features; pattern pairs per molecule 414–4712. RMS in cm⁻¹; MLP mean over seeds.

| n | hold-out | model | diag CH-stretch | diag CH-oop | diag ring-ip | diag other | ring coupling RMS / zero | ratio | ring block / median | corrected ω RMS (zero) | overlap | ΔH residual |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 60 | (a) | zero rule | 43.71 | 23.88 | 20.09 | 19.95 | 4.35 / 4.35 | **1.00** | 10.97 / 3.98 | 23.45 (23.45) | 0.997 | 1.00 |
| 60 | (a) | B1 MLP | 8.47 | 16.61 | 27.48 | 16.58 | 5.86 / 4.35 | **1.35** | 22.18 / 3.98 | 18.30 (23.45) | 0.995 | 0.61 |
| 60 | (a) | B2 GBT | 8.10 | 9.20 | 9.34 | 15.47 | 2.75 / 4.35 | **0.63** | 3.14 / 3.98 | 8.09 (23.45) | 0.998 | 0.49 |
| 60 | (b) | zero rule | 44.30 | 25.32 | 19.93 | 19.18 | 3.74 / 3.74 | **1.00** | 13.23 / 1.15 | 23.09 (23.09) | 0.986 | 1.00 |
| 60 | (b) | B1 MLP | 8.51 | 16.89 | 21.81 | 16.94 | 5.03 / 3.74 | **1.35** | 16.76 / 1.15 | 15.24 (23.09) | 0.977 | 0.56 |
| 60 | (b) | B2 GBT | 8.65 | 9.80 | 7.55 | 11.82 | 2.20 / 3.74 | **0.59** | 3.55 / 1.15 | 7.67 (23.09) | 0.993 | 0.45 |
| 60 | (c) | zero rule | 44.04 | 22.48 | 20.14 | 18.94 | 3.98 / 3.98 | **1.00** | 13.58 / 1.36 | 22.77 (22.77) | 0.990 | 1.00 |
| 60 | (c) | B1 MLP | 8.06 | 14.67 | 26.56 | 14.12 | 5.61 / 3.98 | **1.41** | 20.20 / 1.36 | 16.94 (22.77) | 0.985 | 0.67 |
| 60 | (c) | B2 GBT | 8.41 | 8.28 | 8.80 | 11.89 | 2.70 / 3.98 | **0.68** | 3.40 / 1.36 | 7.87 (22.77) | 0.994 | 0.51 |

## Readings (pre-registered)

- B1 MLP ring coupling ratio vs n: (a) 60: 1.35 (slope +nan); (b) 60: 1.35 (slope +nan)
- Verdict at n = 60: ratio (a) 1.35, (b) 1.35, slope (a) +nan → **LOSE** (win: ≤ 0.6 on both and a negative slope; lose: ≥ 0.9 on (a))

Total 29 s.
