# 'other' split into low (< 700 cm⁻¹) and mid — hold-out (a), 2026-10-04 12:17

Models: E7_rungC_chain34c_kdfamilylow_750_2026-10-04_model_n750_seed0.pt, E7_rungC_chain34c_kdfamilylow_750_2026-10-04_model_n750_seed1.pt, E7_rungC_chain34c_kdfamilylow_750_2026-10-04_model_n750_seed2.pt (rms over models per molecule); corpus with analytic Hessians substituted for 28 molecules.

## Pooled over the hold-out (rms, cm⁻¹; n modes)

| group | n | models | zero rule | FD floor (molecules with both routes) |
|---|---|---|---|---|
| ring-ip | 231 | 2.06 | 19.22 | 35.03 |
| CH-stretch | 86 | 1.96 | 43.31 | 4.81 |
| CH-oop | 61 | 3.08 | 21.95 | 6.05 |
| other-low | 132 | 3.54 | 10.96 | 14.83 |
| other-mid | 54 | 3.02 | 15.89 | 0.99 |

Share of the pooled squared 'other' error in the low modes: **77 %** (132 low modes, 54 mid modes).

## Per molecule (rms, cm⁻¹): models / zero rule / floor

| molecule | atoms | ring-ip | CH-stretch | CH-oop | other-low | other-mid |
|---|---|---|---|---|---|---|
| A_fdc27f1bd1 | 22 | 1.43 / 19.68 | 1.43 / 43.38 | — | 4.04 / 11.08 | 2.45 / 17.38 |
| A_8448043181 | 12 | 2.10 / 17.83 / 48.56 | 1.37 / 42.91 / 6.52 | 3.46 / 22.56 / 8.32 | 1.39 / 7.80 / 25.61 | 3.61 / 16.95 / 0.31 |
| A_e72997e726 | 23 | 2.88 / 19.20 | 4.11 / 44.51 | — | 4.70 / 10.55 | 1.91 / 18.36 |
| A_541c53d1a5 | 24 | 1.65 / 17.98 | 1.85 / 43.80 | 2.37 / 23.08 | 1.90 / 8.36 | 1.03 / 9.54 |
| A_428228e5a5 | 26 | 2.41 / 19.41 | 1.11 / 43.09 | 3.59 / 21.46 | 3.88 / 8.01 | 2.78 / 9.57 |
| A_07cadc7923 | 21 | 2.06 / 18.13 | 1.26 / 42.65 | 3.29 / 21.54 | 1.79 / 15.47 | 1.22 / 19.29 |
| A_08dde334d8 | 24 | 1.97 / 20.43 | 1.51 / 43.10 | — | 4.20 / 12.32 | 6.01 / 14.32 |
| A_3100da3761 | 13 | 1.76 / 20.07 / 1.51 | 0.71 / 41.91 / 0.06 | 1.80 / 19.64 / 1.96 | 3.89 / 15.67 / 1.36 | 1.90 / 27.09 / 1.20 |
| A_bce5bae234 | 23 | 1.70 / 18.37 | 1.68 / 43.66 | 2.90 / 20.78 | 1.93 / 8.12 | 0.96 / 9.34 |
| A_72b86c2331 | 20 | 2.09 / 20.20 | 1.56 / 43.00 | 3.56 / 23.98 | 4.65 / 9.44 | 3.15 / 13.12 |