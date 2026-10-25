# 'other' split into low (< 700 cm⁻¹) and mid — hold-out (a), 2026-10-04 08:27

Models: E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed0.pt, E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed1.pt, E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed2.pt (rms over models per molecule); corpus with analytic Hessians substituted for 28 molecules.

## Pooled over the hold-out (rms, cm⁻¹; n modes)

| group | n | models | zero rule | FD floor (molecules with both routes) |
|---|---|---|---|---|
| ring-ip | 231 | 1.95 | 19.22 | 35.03 |
| CH-stretch | 86 | 1.27 | 43.31 | 4.81 |
| CH-oop | 61 | 2.92 | 21.95 | 6.05 |
| other-low | 132 | 3.35 | 10.96 | 14.83 |
| other-mid | 54 | 2.90 | 15.89 | 0.99 |

Share of the pooled squared 'other' error in the low modes: **77 %** (132 low modes, 54 mid modes).

## Per molecule (rms, cm⁻¹): models / zero rule / floor

| molecule | atoms | ring-ip | CH-stretch | CH-oop | other-low | other-mid |
|---|---|---|---|---|---|---|
| A_fdc27f1bd1 | 22 | 1.38 / 19.68 | 0.62 / 43.38 | — | 3.88 / 11.08 | 2.28 / 17.38 |
| A_8448043181 | 12 | 1.74 / 17.83 / 48.56 | 0.98 / 42.91 / 6.52 | 3.58 / 22.56 / 8.32 | 1.25 / 7.80 / 25.61 | 3.42 / 16.95 / 0.31 |
| A_e72997e726 | 23 | 2.86 / 19.20 | 2.98 / 44.51 | — | 4.98 / 10.55 | 3.03 / 18.36 |
| A_541c53d1a5 | 24 | 1.87 / 17.98 | 0.61 / 43.80 | 2.06 / 23.08 | 2.05 / 8.36 | 0.85 / 9.54 |
| A_428228e5a5 | 26 | 2.57 / 19.41 | 0.66 / 43.09 | 4.19 / 21.46 | 3.65 / 8.01 | 2.16 / 9.57 |
| A_07cadc7923 | 21 | 1.42 / 18.13 | 1.02 / 42.65 | 2.78 / 21.54 | 1.52 / 15.47 | 0.71 / 19.29 |
| A_08dde334d8 | 24 | 1.83 / 20.43 | 0.85 / 43.10 | — | 4.09 / 12.32 | 5.20 / 14.32 |
| A_3100da3761 | 13 | 0.89 / 20.07 / 1.51 | 1.44 / 41.91 / 0.06 | 2.01 / 19.64 / 1.96 | 3.74 / 15.67 / 1.36 | 1.49 / 27.09 / 1.20 |
| A_bce5bae234 | 23 | 1.55 / 18.37 | 0.59 / 43.66 | 2.73 / 20.78 | 1.61 / 8.12 | 0.57 / 9.34 |
| A_72b86c2331 | 20 | 1.78 / 20.20 | 0.69 / 43.00 | 2.12 / 23.98 | 3.53 / 9.44 | 3.43 / 13.12 |