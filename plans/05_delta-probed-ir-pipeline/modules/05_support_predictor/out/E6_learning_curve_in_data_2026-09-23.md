# E6 — learning curve in data (2026-09-23 06:28)

244 molecules (A 45, A2 199; 20 with an imaginary mode kept, as on 19 Sep). Hold-out (a): the 12 layer-A molecules of 19 Sep. Hold-out (b): scaffold cores ['fluoranthene', 'fluorene'] (41 molecules). Pool 191; sizes [45, 100, 191]; seeds [0, 1, 2]; M1 600 steps, M2 30 epochs, E5 1500 steps. Held-out RMS in cm⁻¹, mean over seeds.

## Hold-out (a): the 12 layer-A molecules

| n | model | diag CH-stretch | diag CH-oop | diag ring-ip | diag other | ring coupling RMS / zero | ratio | ring block RMS / median rule |
|---|---|---|---|---|---|---|---|---|
| 45 | zero rule | 43.76 | 23.59 | 21.89 | 14.85 | — / 5.49 | 1.00 | — / 3.90 |
| 45 | family median | 1.75 | 8.65 | 18.34 | 11.14 | | | |
| 45 | ridge probe | 4.24 | 7.56 | 17.50 | 11.46 | | | |
| 45 | M1 | 1.95 | 6.26 | 13.47 | 8.99 | | | |
| 45 | M2 | 1.88 | 6.55 | 13.92 | 10.75 | 5.50 / 5.49 | 1.00 | 4.63 / 3.90 |
| 45 | M3 | 5.18 | 5.81 | 13.66 | 11.03 | 10.52 / 5.49 | 1.91 | 3.84 / 3.90 |
| 45 | M4 | 13.47 | 7.94 | 16.82 | 11.65 | 7.85 / 5.49 | 1.43 | 3.75 / 3.90 |
| 100 | zero rule | 43.76 | 23.59 | 21.89 | 14.85 | — / 5.49 | 1.00 | — / 3.89 |
| 100 | family median | 1.73 | 8.59 | 18.37 | 11.14 | | | |
| 100 | ridge probe | 3.70 | 6.91 | 17.31 | 11.66 | | | |
| 100 | M1 | 1.70 | 5.02 | 11.59 | 26.60 | | | |
| 100 | M2 | 1.89 | 4.91 | 11.99 | 11.38 | 5.51 / 5.49 | 1.00 | 5.07 / 3.89 |
| 100 | M3 | 3.80 | 6.09 | 13.79 | 13.50 | 9.93 / 5.49 | 1.81 | 3.85 / 3.89 |
| 100 | M4 | 14.36 | 7.93 | 16.08 | 11.32 | 7.32 / 5.49 | 1.33 | 5.06 / 3.89 |
| 191 | zero rule | 43.76 | 23.59 | 21.89 | 14.85 | — / 5.49 | 1.00 | — / 3.87 |
| 191 | family median | 1.73 | 8.56 | 18.36 | 11.14 | | | |
| 191 | ridge probe | 3.85 | 6.93 | 17.34 | 11.77 | | | |
| 191 | M1 | 1.62 | 3.81 | 11.50 | 27.97 | | | |
| 191 | M2 | 2.20 | 4.55 | 11.66 | 11.44 | 5.50 / 5.49 | 1.00 | 5.63 / 3.87 |
| 191 | M3 | 4.10 | 5.72 | 13.82 | 14.56 | 10.24 / 5.49 | 1.86 | 4.03 / 3.87 |
| 191 | M4 | 10.34 | 6.95 | 15.87 | 11.69 | 7.39 / 5.49 | 1.34 | 5.31 / 3.87 |

## Hold-out (b): the scaffold cores

| n | model | diag CH-stretch | diag CH-oop | diag ring-ip | diag other | ring coupling RMS / zero | ratio | ring block RMS / median rule |
|---|---|---|---|---|---|---|---|---|
| 45 | zero rule | 44.29 | 25.32 | 20.00 | 19.38 | — / 3.72 | 1.00 | — / 1.15 |
| 45 | family median | 3.38 | 9.11 | 15.05 | 14.62 | | | |
| 45 | ridge probe | 5.23 | 5.91 | 13.36 | 14.19 | | | |
| 45 | M1 | 3.28 | 3.30 | 7.08 | 12.16 | | | |
| 45 | M2 | 3.37 | 4.70 | 8.42 | 11.57 | 3.72 / 3.72 | 1.00 | 2.28 / 1.15 |
| 45 | M3 | 6.08 | 4.67 | 8.73 | 10.98 | 9.63 / 3.72 | 2.58 | 2.03 / 1.15 |
| 45 | M4 | 9.49 | 6.21 | 13.37 | 11.99 | 5.99 / 3.72 | 1.61 | 3.04 / 1.15 |
| 100 | zero rule | 44.29 | 25.32 | 20.00 | 19.38 | — / 3.72 | 1.00 | — / 1.17 |
| 100 | family median | 3.36 | 8.96 | 15.14 | 14.68 | | | |
| 100 | ridge probe | 4.90 | 5.44 | 13.11 | 14.35 | | | |
| 100 | M1 | 3.07 | 3.28 | 6.37 | 9.02 | | | |
| 100 | M2 | 3.33 | 3.63 | 6.11 | 10.46 | 3.73 / 3.72 | 1.00 | 1.43 / 1.17 |
| 100 | M3 | 5.20 | 5.61 | 8.94 | 9.60 | 8.91 / 3.72 | 2.39 | 2.26 / 1.17 |
| 100 | M4 | 12.30 | 6.91 | 12.22 | 12.11 | 5.90 / 3.72 | 1.59 | 2.64 / 1.17 |
| 191 | zero rule | 44.29 | 25.32 | 20.00 | 19.38 | — / 3.72 | 1.00 | — / 1.20 |
| 191 | family median | 3.36 | 8.90 | 15.11 | 14.57 | | | |
| 191 | ridge probe | 5.13 | 5.40 | 13.14 | 13.99 | | | |
| 191 | M1 | 3.00 | 3.33 | 6.05 | 7.65 | | | |
| 191 | M2 | 3.49 | 4.29 | 5.91 | 9.63 | 3.73 / 3.72 | 1.00 | 1.43 / 1.20 |
| 191 | M3 | 5.16 | 5.21 | 8.75 | 9.35 | 9.54 / 3.72 | 2.56 | 1.89 / 1.20 |
| 191 | M4 | 8.33 | 6.99 | 11.58 | 11.77 | 5.98 / 3.72 | 1.61 | 2.36 / 1.20 |

## Readings (pre-registered)

- M1 slopes of log RMS vs log n: diag CH-stretch -0.13, CH-oop -0.34, ring-ip -0.11, other +0.81
- M2 slopes of log RMS vs log n: diag CH-stretch +0.10, CH-oop -0.26, ring-ip -0.13, other +0.04; ring coupling ratio +0.00
- M3 slopes of log RMS vs log n: diag CH-stretch -0.17, CH-oop -0.01, ring-ip +0.01, other +0.19; ring coupling ratio -0.02
- M4 slopes of log RMS vs log n: diag CH-stretch -0.17, CH-oop -0.09, ring-ip -0.04, other +0.00; ring coupling ratio -0.04
- M2 crossings: ratio < 1.0 at n = None, < 0.7 at n = None, ring block beats the median rule at n = None
- M3 crossings: ratio < 1.0 at n = None, < 0.7 at n = None, ring block beats the median rule at n = 45
- M4 crossings: ratio < 1.0 at n = None, < 0.7 at n = None, ring block beats the median rule at n = 45
- M2 scaffold gap on the ring block, (b) − (a): n=45 -2.35, n=100 -3.64, n=191 -4.21
- M3 scaffold gap on the ring block, (b) − (a): n=45 -1.82, n=100 -1.59, n=191 -2.14
- M4 scaffold gap on the ring block, (b) − (a): n=45 -0.71, n=100 -2.42, n=191 -2.94

Total 4401 s. M1 = per-mode Transformer; M2 = ΔH block model; M3 = E5b-tok; M4 = E5b-atoms.
