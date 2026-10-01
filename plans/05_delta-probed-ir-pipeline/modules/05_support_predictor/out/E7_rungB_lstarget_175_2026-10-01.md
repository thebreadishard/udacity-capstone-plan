# E7 / rung B — pairwise local force-constant terms, learned and projected (2026-10-01 15:12)

799 molecules; hold-out (a) 10 layer-A molecules, (b) scaffold cores ['fluoranthene', 'fluorene'] (39); pool 176; sizes [175]; seeds [0, 1, 2]; 60 epochs; 66 pair features; pattern pairs per molecule 414–4712. RMS in cm⁻¹; MLP mean over seeds.

| n | hold-out | model | diag CH-stretch | diag CH-oop | diag ring-ip | diag other | ring coupling RMS / zero | ratio | ring block / median | corrected ω RMS (zero) | overlap | ΔH residual |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 175 | (a) | zero rule | 43.60 | 23.59 | 19.70 | 13.19 | 3.76 / 3.76 | **1.00** | 11.09 / 2.67 | 23.27 (23.27) | 0.998 | 1.00 |
| 175 | (a) | B1 MLP | 0.93 | 6.71 | 6.18 | 6.26 | 1.79 / 3.76 | **0.48** | 2.39 / 2.66 | 5.33 (23.27) | 0.998 | 0.26 |
| 175 | (a) | B2 GBT | 4.00 | 9.88 | 6.27 | 7.48 | 1.69 / 3.76 | **0.45** | 1.90 / 2.66 | 6.60 (23.27) | 0.998 | 0.33 |
| 175 | (b) | zero rule | 44.30 | 25.32 | 19.93 | 19.18 | 3.74 / 3.74 | **1.00** | 13.23 / 1.15 | 23.09 (23.09) | 0.986 | 1.00 |
| 175 | (b) | B1 MLP | 2.04 | 8.50 | 8.35 | 7.61 | 2.22 / 3.74 | **0.59** | 3.45 / 1.15 | 6.43 (23.09) | 0.991 | 0.36 |
| 175 | (b) | B2 GBT | 4.43 | 11.12 | 6.25 | 12.27 | 1.77 / 3.74 | **0.47** | 2.56 / 1.15 | 6.74 (23.09) | 0.993 | 0.35 |

## Readings (pre-registered)

- B1 MLP ring coupling ratio vs n: (a) 175: 0.48 (slope +nan); (b) 175: 0.59 (slope +nan)
- Verdict at n = 175: ratio (a) 0.48, (b) 0.59, slope (a) +nan → **between** (win: ≤ 0.6 on both and a negative slope; lose: ≥ 0.9 on (a))

Total 440 s.
