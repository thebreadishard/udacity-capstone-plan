# S2 diagnostics — bias or variance? (14 molecules, 9 scaffolds, route (b) has 10 coefficients; labels GVPT2, scope no-linear-xh)

| family | modes | (b) in-sample | (b) held out | (c) in-sample | (c) held out |
|---|---|---|---|---|---|
| CH-stretch | 0 | nan | nan | nan | nan |
| CH-oop | 74 | 5.20 | 5.78 | 5.34 | 5.89 |
| ring-ip | 257 | 3.80 | 3.90 | 9.49 | 9.50 |
| other | 96 | 13.29 | 14.00 | 13.53 | 13.61 |

| molecule | scaffold | 'other' modes | (b) held-out rms |
|---|---|---|---|
| B_410ac0fb2f | c1ccccc1 | 9 | 42.96 |
| A_72b86c2331 | c1ccc2c(c1)-c1ccccc1-2 | 8 | 9.50 |
| A_d9139359ab | c1ccc2cccc-2cc1 | 6 | 6.03 |
| B_78f8233b4c | c1ccc2cccc-2cc1 | 11 | 5.00 |
| A_45187bb7c8 | C1=Cc2cccc3cccc1c23 | 9 | 4.69 |
| B_a41f4cff9d | c1ccc2ccccc2c1 | 8 | 4.59 |
| A_01f3186607 | c1ccc2ccccc2c1 | 6 | 4.49 |
| B_079e66d017 | c1ccc2cnccc2c1 | 10 | 3.91 |
| B_0603418c5b | c1ccc2cccc-2cc1 | 5 | 3.89 |
| A_90df3e4aa9 | C1=Cc2ccccc2C1 | 10 | 3.75 |
| A_8448043181 | c1ccccc1 | 3 | 3.18 |
| A_a848c04a21 | c1ccccc1 | 2 | 3.05 |
| A_7aa232d4e9 | c1ccc2nccnc2c1 | 5 | 3.03 |
| A_d295f2fa80 | c1ccc2ncncc2c1 | 4 | 2.91 |

| molecule | ω (cm⁻¹) | family | Δ_anh | (b) predicts | h |
|---|---|---|---|---|---|
| B_410ac0fb2f | 594 | other | -132.0 | -6.9 | 0.63 |
| A_72b86c2331 | 828 | other | -38.6 | -16.2 | 0.22 |
| B_410ac0fb2f | 559 | other | -29.4 | -7.9 | 0.54 |
| B_410ac0fb2f | 946 | other | 4.0 | -16.7 | 0.75 |
| B_0603418c5b | 680 | CH-oop | -29.8 | -14.3 | 0.32 |
| A_a848c04a21 | 969 | CH-oop | -2.1 | -14.1 | 0.73 |
| A_72b86c2331 | 904 | CH-oop | -25.9 | -14.6 | 0.60 |
| A_72b86c2331 | 919 | CH-oop | -3.0 | -14.2 | 0.70 |
| A_45187bb7c8 | 582 | other | -5.8 | -16.7 | 0.22 |
| A_72b86c2331 | 924 | CH-oop | -3.5 | -14.2 | 0.69 |
| A_d9139359ab | 997 | CH-oop | -22.6 | -11.9 | 0.71 |
| B_0603418c5b | 997 | CH-oop | -22.6 | -11.9 | 0.71 |
| A_90df3e4aa9 | 1155 | ring-ip | -27.2 | -16.9 | 0.88 |
| A_01f3186607 | 964 | CH-oop | -4.1 | -14.2 | 0.71 |
| A_72b86c2331 | 587 | other | -6.5 | -16.6 | 0.20 |
