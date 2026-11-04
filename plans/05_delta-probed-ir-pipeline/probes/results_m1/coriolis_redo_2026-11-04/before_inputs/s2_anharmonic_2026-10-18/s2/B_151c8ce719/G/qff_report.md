# Quartic force field from 61 displaced Hessians — /root/s2/B_151c8ce719/G/hess

Reference file `ref.json`; 30 vibrational modes; displacement 0.1 in reduced coordinates; assignment residual max 4.69e-15.
Harmonic ω (cm⁻¹): 108.0, 265.2, 337.9, 483.1, 651.5, 664.5, 687.9, 720.6, 805.7, 948.0, 979.2, 1012.9, 1081.7, 1099.6, 1139.9, 1255.2, 1301.1, 1361.3, 1445.5, 1472.2, 1507.5, 1521.1, 1542.8, 1619.0, 3047.3, 3100.9, 3124.3, 3265.6, 3287.6, 3654.1

## Noise diagnostics

Off-diagonal semi-diagonal quartic constants φ_iijj have two independent finite-difference routes (displace j and read H_ii; displace i and read H_jj). Their difference is a direct estimate of the numerical error of that constant. Exactly degenerate pairs (a, b) must give equal φ_aa,jj and φ_bb,jj for every totally symmetric j; their difference is a second estimate.

- route disagreement |φ_iijj(a) − φ_iijj(b)|: median 0.0, 90th percentile 0.3, max 5.6 cm⁻¹ (max |φ_iijj| 2048.3)
- cubic route spread (max − min of the three routes): median 0.02, max 17.7 cm⁻¹
- totally symmetric modes (|φ_iii| > 5 cm⁻¹, non-degenerate): [(5, 664.5), (9, 948.0), (10, 979.2), (11, 1012.9), (13, 1099.6), (14, 1139.9), (16, 1301.1), (17, 1361.3), (18, 1445.5), (19, 1472.2), (21, 1521.1), (22, 1542.8), (23, 1619.0), (24, 3047.3), (26, 3124.3), (27, 3265.6), (28, 3287.6), (29, 3654.1)]

| degenerate pair (ω) | j (ω) | φ_aa,jj | φ_bb,jj | difference | route disagreement a / b |
|---|---|---|---|---|---|

## VPT2 fundamentals (deperturbation window 200.0 cm⁻¹, min K 0.0; 769 resonances deperturbed; polyad diagonalisation not applied)

| mode | ω | ν raw quartics | ν − ω | ν symmetry-averaged quartics | ν − ω | pyVPT2 ν | pair |
|---|---|---|---|---|---|---|---|
| 0 | 108.0 | 93.4 | -14.6 | 93.4 | -14.6 | — |  |
| 1 | 265.2 | 263.6 | -1.6 | 263.6 | -1.6 | — |  |
| 2 | 337.9 | 338.7 | +0.8 | 338.7 | +0.8 | — |  |
| 3 | 483.1 | 488.1 | +5.0 | 488.1 | +5.0 | — |  |
| 4 | 651.5 | 637.6 | -13.8 | 637.6 | -13.8 | — |  |
| 5 | 664.5 | 655.9 | -8.6 | 655.9 | -8.6 | — |  |
| 6 | 687.9 | 676.9 | -11.0 | 676.9 | -11.0 | — |  |
| 7 | 720.6 | 712.0 | -8.6 | 712.0 | -8.6 | — |  |
| 8 | 805.7 | 793.1 | -12.6 | 793.1 | -12.6 | — |  |
| 9 | 948.0 | 935.2 | -12.8 | 935.2 | -12.8 | — |  |
| 10 | 979.2 | 962.6 | -16.6 | 962.6 | -16.6 | — |  |
| 11 | 1012.9 | 994.0 | -18.9 | 994.0 | -18.9 | — |  |
| 12 | 1081.7 | 1057.0 | -24.7 | 1057.0 | -24.7 | — |  |
| 13 | 1099.6 | 1079.5 | -20.1 | 1079.5 | -20.1 | — |  |
| 14 | 1139.9 | 1114.4 | -25.4 | 1114.4 | -25.4 | — |  |
| 15 | 1255.2 | 1230.2 | -25.0 | 1230.2 | -25.0 | — |  |
| 16 | 1301.1 | 1270.9 | -30.2 | 1270.9 | -30.2 | — |  |
| 17 | 1361.3 | 1330.2 | -31.1 | 1330.2 | -31.1 | — |  |
| 18 | 1445.5 | 1412.8 | -32.7 | 1412.8 | -32.7 | — |  |
| 19 | 1472.2 | 1428.9 | -43.3 | 1428.9 | -43.3 | — |  |
| 20 | 1507.5 | 1469.5 | -38.0 | 1469.5 | -38.0 | — |  |
| 21 | 1521.1 | 1481.7 | -39.4 | 1481.7 | -39.4 | — |  |
| 22 | 1542.8 | 1506.4 | -36.4 | 1506.4 | -36.4 | — |  |
| 23 | 1619.0 | 1580.8 | -38.2 | 1580.8 | -38.2 | — |  |
| 24 | 3047.3 | 2897.8 | -149.5 | 2897.8 | -149.5 | — |  |
| 25 | 3100.9 | 2945.6 | -155.2 | 2945.6 | -155.2 | — |  |
| 26 | 3124.3 | 2970.8 | -153.5 | 2970.8 | -153.5 | — |  |
| 27 | 3265.6 | 3127.2 | -138.5 | 3127.2 | -138.5 | — |  |
| 28 | 3287.6 | 3149.9 | -137.7 | 3149.9 | -137.7 | — |  |
| 29 | 3654.1 | 3480.3 | -173.8 | 3480.3 | -173.8 | — |  |

## Provenance

- timestamp_utc: `2026-10-16 07:16:26`
- host: `ubuntu-32gb-hel1-6`
- python: `3.12.15`
- numpy: `2.5.4`
- command: `qff.py /root/s2/B_151c8ce719/G/hess --disp 0.10 --allow-noisy --out /root/s2/B_151c8ce719/G/qff_report.md`
