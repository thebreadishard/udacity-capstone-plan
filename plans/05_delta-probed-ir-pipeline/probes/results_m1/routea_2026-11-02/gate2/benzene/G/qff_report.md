# Quartic force field from 61 displaced Hessians — C:\Users\thebr\Documents\CapstonePlan\plans\05_delta-probed-ir-pipeline\probes\results_m1\routea_2026-11-02\gate2\benzene\G\hess

Reference file `ref.json`; 30 vibrational modes; displacement 0.1 in reduced coordinates; assignment residual max 4.15e-14.
Harmonic ω (cm⁻¹): 414.8, 415.5, 621.2, 621.9, 695.0, 718.3, 864.9, 865.2, 969.6, 969.8, 1011.3, 1019.1, 1020.9, 1069.0, 1069.3, 1185.3, 1207.5, 1207.5, 1356.7, 1387.8, 1531.6, 1531.8, 1655.8, 1656.2, 3176.2, 3185.9, 3186.0, 3201.9, 3201.9, 3212.6

## Noise diagnostics

Off-diagonal semi-diagonal quartic constants φ_iijj have two independent finite-difference routes (displace j and read H_ii; displace i and read H_jj). Their difference is a direct estimate of the numerical error of that constant. Exactly degenerate pairs (a, b) must give equal φ_aa,jj and φ_bb,jj for every totally symmetric j; their difference is a second estimate.

- route disagreement |φ_iijj(a) − φ_iijj(b)|: median 0.1, 90th percentile 0.6, max 6.0 cm⁻¹ (max |φ_iijj| 275.9)
- cubic route spread (max − min of the three routes): median 0.01, max 1.0 cm⁻¹
- totally symmetric modes (|φ_iii| > 5 cm⁻¹, non-degenerate): [(12, 1020.9), (29, 3212.6)]

| degenerate pair (ω) | j (ω) | φ_aa,jj | φ_bb,jj | difference | route disagreement a / b |
|---|---|---|---|---|---|
| (6,7) 865 | 12 1021 | -0.7 | -0.7 | 0.1 | 0.0 / 0.1 |
| (6,7) 865 | 29 3213 | -142.9 | -142.4 | 0.6 | 0.1 / 0.2 |
| (8,9) 970 | 12 1021 | -2.0 | -2.0 | 0.0 | 0.4 / 0.3 |
| (8,9) 970 | 29 3213 | -120.4 | -119.9 | 0.4 | 0.1 / 0.2 |
| (13,14) 1069 | 12 1021 | +5.9 | +5.8 | 0.1 | 0.4 / 0.3 |
| (13,14) 1069 | 29 3213 | -39.3 | -39.3 | 0.1 | 0.1 / 0.1 |
| (16,17) 1207 | 12 1021 | +3.4 | +3.4 | 0.0 | 0.0 / 0.0 |
| (16,17) 1207 | 29 3213 | -64.6 | -64.4 | 0.2 | 0.1 / 0.0 |
| (20,21) 1532 | 12 1021 | +4.9 | +4.6 | 0.3 | 0.1 / 0.4 |
| (20,21) 1532 | 29 3213 | -51.5 | -51.3 | 0.2 | 0.0 / 0.0 |
| (22,23) 1656 | 12 1021 | +14.0 | +14.0 | 0.1 | 0.1 / 0.1 |
| (22,23) 1656 | 29 3213 | -22.7 | -22.7 | 0.0 | 0.0 / 0.1 |
| (25,26) 3186 | 12 1021 | -0.3 | -0.3 | 0.0 | 0.0 / 0.0 |
| (25,26) 3186 | 29 3213 | +183.8 | +184.3 | 0.5 | 0.0 / 0.0 |
| (27,28) 3202 | 12 1021 | -0.1 | -0.1 | 0.1 | 0.0 / 0.1 |
| (27,28) 3202 | 29 3213 | +182.5 | +182.1 | 0.4 | 0.1 / 1.8 |

## VPT2 fundamentals (deperturbation window 200.0 cm⁻¹, min K 0.0; 561 resonances deperturbed; polyad diagonalisation not applied)

| mode | ω | ν raw quartics | ν − ω | ν symmetry-averaged quartics | ν − ω | pyVPT2 ν | pair |
|---|---|---|---|---|---|---|---|
| 0 | 414.8 | 408.1 | -6.8 | 408.1 | -6.8 | — |  |
| 1 | 415.5 | 407.7 | -7.7 | 407.7 | -7.7 | — |  |
| 2 | 621.2 | 616.0 | -5.3 | 616.0 | -5.3 | — |  |
| 3 | 621.9 | 616.4 | -5.5 | 616.4 | -5.5 | — |  |
| 4 | 695.0 | 684.5 | -10.6 | 684.5 | -10.6 | — |  |
| 5 | 718.3 | 708.4 | -9.9 | 708.4 | -9.9 | — |  |
| 6 | 864.9 | 850.8 | -14.2 | 850.3 | -14.6 | — | e |
| 7 | 865.2 | 849.7 | -15.5 | 850.1 | -15.1 | — | e |
| 8 | 969.6 | 965.7 | -3.9 | 965.2 | -4.4 | — | e |
| 9 | 969.8 | 964.7 | -5.1 | 965.2 | -4.6 | — | e |
| 10 | 1011.3 | 993.8 | -17.5 | 993.8 | -17.5 | — |  |
| 11 | 1019.1 | 1006.0 | -13.1 | 1006.0 | -13.1 | — |  |
| 12 | 1020.9 | 1003.3 | -17.5 | 1003.3 | -17.5 | — |  |
| 13 | 1069.0 | 1052.0 | -17.0 | 1051.9 | -17.2 | — | e |
| 14 | 1069.3 | 1052.0 | -17.3 | 1052.1 | -17.2 | — | e |
| 15 | 1185.3 | 1174.6 | -10.7 | 1174.6 | -10.7 | — |  |
| 16 | 1207.5 | 1192.8 | -14.7 | 1192.6 | -14.8 | — | e |
| 17 | 1207.5 | 1192.4 | -15.1 | 1192.6 | -14.9 | — | e |
| 18 | 1356.7 | 1322.1 | -34.6 | 1322.1 | -34.6 | — |  |
| 19 | 1387.8 | 1367.0 | -20.8 | 1367.0 | -20.8 | — |  |
| 20 | 1531.6 | 1501.3 | -30.3 | 1501.0 | -30.5 | — | e |
| 21 | 1531.8 | 1500.9 | -30.9 | 1501.1 | -30.6 | — | e |
| 22 | 1655.8 | 1616.1 | -39.7 | 1616.0 | -39.8 | — | e |
| 23 | 1656.2 | 1616.3 | -39.8 | 1616.5 | -39.7 | — | e |
| 24 | 3176.2 | 3035.5 | -140.7 | 3035.5 | -140.7 | — |  |
| 25 | 3185.9 | 3045.1 | -140.8 | 3045.2 | -140.8 | — | e |
| 26 | 3186.0 | 3045.0 | -141.0 | 3045.0 | -141.0 | — | e |
| 27 | 3201.9 | 3062.8 | -139.0 | 3062.6 | -139.2 | — | e |
| 28 | 3201.9 | 3062.7 | -139.3 | 3062.9 | -139.1 | — | e |
| 29 | 3212.6 | 3070.6 | -142.0 | 3070.6 | -142.0 | — |  |

## Provenance

- timestamp_utc: `2026-11-04 07:37:58`
- host: `Asus18`
- python: `3.14.6`
- numpy: `2.5.1`
- command: `qff.py C:\Users\thebr\Documents\CapstonePlan\plans\05_delta-probed-ir-pipeline\probes\results_m1\routea_2026-11-02\gate2\benzene\G\hess --disp 0.10 --out C:\Users\thebr\Documents\CapstonePlan\plans\05_delta-probed-ir-pipeline\probes\results_m1\routea_2026-11-02\gate2\benzene\G\qff_report.md`
- commit: `648a001eb6cfa32df774b73c6e2f0d91dadb87c4`
- dirty: `yes`
