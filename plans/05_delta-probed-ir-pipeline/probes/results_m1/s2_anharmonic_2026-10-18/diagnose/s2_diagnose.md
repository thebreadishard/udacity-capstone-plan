# S2 diagnostics — bias or variance? (14 molecules, 9 scaffolds, route (b) has 10 coefficients)

| family | modes | (b) in-sample | (b) held out | (c) in-sample | (c) held out |
|---|---|---|---|---|---|
| CH-stretch | 0 | nan | nan | nan | nan |
| CH-oop | 74 | 5.16 | 5.67 | 5.36 | 5.92 |
| ring-ip | 257 | 3.09 | 3.15 | 8.76 | 8.77 |
| other | 101 | 18.28 | 18.85 | 19.69 | 19.76 |

| molecule | scaffold | 'other' modes | (b) held-out rms |
|---|---|---|---|
| B_410ac0fb2f | c1ccccc1 | 10 | 44.74 |
| B_0603418c5b | c1ccc2cccc-2cc1 | 7 | 41.86 |
| A_a848c04a21 | c1ccccc1 | 4 | 23.07 |
| A_72b86c2331 | c1ccc2c(c1)-c1ccccc1-2 | 8 | 8.27 |
| B_78f8233b4c | c1ccc2cccc-2cc1 | 11 | 5.64 |
| A_01f3186607 | c1ccc2ccccc2c1 | 6 | 3.77 |
| A_90df3e4aa9 | C1=Cc2ccccc2C1 | 10 | 3.48 |
| B_a41f4cff9d | c1ccc2ccccc2c1 | 8 | 3.37 |
| A_8448043181 | c1ccccc1 | 3 | 3.28 |
| B_079e66d017 | c1ccc2cnccc2c1 | 10 | 3.07 |
| A_d9139359ab | c1ccc2cccc-2cc1 | 6 | 2.88 |
| A_45187bb7c8 | C1=Cc2cccc3cccc1c23 | 9 | 2.85 |
| A_7aa232d4e9 | c1ccc2nccnc2c1 | 5 | 2.52 |
| A_d295f2fa80 | c1ccc2ncncc2c1 | 4 | 1.64 |

| molecule | ω (cm⁻¹) | family | Δ_anh | (b) predicts | h |
|---|---|---|---|---|---|
| B_410ac0fb2f | 594 | other | -129.7 | -0.3 | 0.63 |
| B_0603418c5b | 564 | other | 93.9 | -7.4 | 0.76 |
| B_410ac0fb2f | 628 | other | 52.9 | 7.7 | 0.83 |
| B_0603418c5b | 616 | other | 46.7 | 2.7 | 0.82 |
| A_a848c04a21 | 627 | other | 45.1 | 7.5 | 0.81 |
| B_410ac0fb2f | 559 | other | -28.2 | -1.0 | 0.54 |
| A_a848c04a21 | 578 | other | 26.3 | -0.4 | 0.67 |
| B_410ac0fb2f | 946 | other | 4.0 | -17.1 | 0.75 |
| A_72b86c2331 | 828 | other | -38.6 | -18.9 | 0.22 |
| A_90df3e4aa9 | 1469 | ring-ip | -40.1 | -25.7 | 0.87 |
| A_90df3e4aa9 | 1155 | ring-ip | -26.9 | -13.2 | 0.88 |
| B_0603418c5b | 680 | CH-oop | -29.8 | -17.0 | 0.32 |
| B_410ac0fb2f | 1093 | ring-ip | -27.0 | -14.3 | 0.65 |
| B_079e66d017 | 1530 | ring-ip | -38.0 | -25.4 | 0.90 |
| A_a848c04a21 | 969 | CH-oop | -2.1 | -14.1 | 0.73 |
