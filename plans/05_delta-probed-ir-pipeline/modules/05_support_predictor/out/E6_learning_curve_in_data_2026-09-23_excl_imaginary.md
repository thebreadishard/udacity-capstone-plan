# E6 — learning curve in data (2026-09-23 08:02)

224 molecules (A 42, A2 182; 0 with an imaginary mode kept, as on 19 Sep). Hold-out (a): the 10 layer-A molecules of 19 Sep. Hold-out (b): scaffold cores ['fluoranthene', 'fluorene'] (39 molecules). Pool 175; sizes [45, 100, 175]; seeds [0, 1, 2]; M1 600 steps, M2 30 epochs, E5 1500 steps. Held-out RMS in cm⁻¹, mean over seeds.

## Hold-out (a): the 12 layer-A molecules

| n | model | diag CH-stretch | diag CH-oop | diag ring-ip | diag other | ring coupling RMS / zero | ratio | ring block RMS / median rule |
|---|---|---|---|---|---|---|---|---|
| 45 | zero rule | 43.58 | 23.91 | 22.38 | 13.55 | — / 5.90 | 1.00 | — / 4.14 |
| 45 | family median | 1.62 | 8.77 | 18.81 | 8.42 | | | |
| 45 | ridge probe | 4.46 | 6.91 | 17.80 | 9.74 | | | |
| 45 | M1 | 1.86 | 6.04 | 13.88 | 6.05 | | | |
| 45 | M2 | 1.97 | 6.41 | 14.21 | 5.89 | 5.90 / 5.90 | 1.00 | 5.30 / 4.14 |
| 45 | M3 | 3.73 | 5.27 | 14.28 | 7.36 | 11.13 / 5.90 | 1.89 | 4.21 / 4.14 |
| 45 | M4 | 17.92 | 7.76 | 17.09 | 8.53 | 8.10 / 5.90 | 1.37 | 4.66 / 4.14 |
| 100 | zero rule | 43.58 | 23.91 | 22.38 | 13.55 | — / 5.90 | 1.00 | — / 4.12 |
| 100 | family median | 1.60 | 8.72 | 18.85 | 8.43 | | | |
| 100 | ridge probe | 4.29 | 6.93 | 17.78 | 9.65 | | | |
| 100 | M1 | 1.58 | 3.66 | 12.56 | 6.89 | | | |
| 100 | M2 | 1.74 | 4.31 | 12.81 | 5.71 | 5.91 / 5.90 | 1.00 | 5.41 / 4.12 |
| 100 | M3 | 3.90 | 6.25 | 14.52 | 7.62 | 10.63 / 5.90 | 1.80 | 4.29 / 4.12 |
| 100 | M4 | 12.59 | 7.91 | 16.88 | 14.60 | 7.62 / 5.90 | 1.29 | 5.55 / 4.12 |
| 175 | zero rule | 43.58 | 23.91 | 22.38 | 13.55 | — / 5.90 | 1.00 | — / 4.12 |
| 175 | family median | 1.60 | 8.69 | 18.83 | 8.40 | | | |
| 175 | ridge probe | 4.38 | 6.96 | 17.80 | 9.58 | | | |
| 175 | M1 | 1.50 | 3.58 | 12.23 | 5.01 | | | |
| 175 | M2 | 1.85 | 4.26 | 12.74 | 5.51 | 5.90 / 5.90 | 1.00 | 5.55 / 4.12 |
| 175 | M3 | 4.81 | 5.72 | 14.57 | 6.57 | 10.68 / 5.90 | 1.81 | 4.36 / 4.12 |
| 175 | M4 | 13.93 | 7.35 | 16.37 | 6.64 | 7.71 / 5.90 | 1.31 | 5.69 / 4.12 |

## Hold-out (b): the scaffold cores

| n | model | diag CH-stretch | diag CH-oop | diag ring-ip | diag other | ring coupling RMS / zero | ratio | ring block RMS / median rule |
|---|---|---|---|---|---|---|---|---|
| 45 | zero rule | 44.30 | 25.32 | 19.93 | 19.18 | — / 3.74 | 1.00 | — / 1.09 |
| 45 | family median | 3.40 | 9.06 | 15.02 | 14.39 | | | |
| 45 | ridge probe | 5.42 | 5.25 | 13.14 | 14.28 | | | |
| 45 | M1 | 3.27 | 3.40 | 6.75 | 12.41 | | | |
| 45 | M2 | 3.42 | 4.44 | 7.98 | 11.11 | 3.74 / 3.74 | 1.00 | 1.81 / 1.09 |
| 45 | M3 | 5.85 | 4.74 | 8.40 | 10.16 | 9.96 / 3.74 | 2.66 | 1.90 / 1.09 |
| 45 | M4 | 9.33 | 6.87 | 13.22 | 11.94 | 5.94 / 3.74 | 1.59 | 2.28 / 1.09 |
| 100 | zero rule | 44.30 | 25.32 | 19.93 | 19.18 | — / 3.74 | 1.00 | — / 1.16 |
| 100 | family median | 3.37 | 8.96 | 15.11 | 14.42 | | | |
| 100 | ridge probe | 5.29 | 5.36 | 13.08 | 14.23 | | | |
| 100 | M1 | 3.16 | 3.26 | 6.33 | 10.10 | | | |
| 100 | M2 | 3.37 | 4.00 | 6.19 | 10.30 | 3.74 / 3.74 | 1.00 | 1.55 / 1.16 |
| 100 | M3 | 5.32 | 5.45 | 8.81 | 9.66 | 9.42 / 3.74 | 2.52 | 2.01 / 1.16 |
| 100 | M4 | 8.83 | 7.51 | 12.19 | 11.63 | 5.84 / 3.74 | 1.56 | 2.12 / 1.16 |
| 175 | zero rule | 44.30 | 25.32 | 19.93 | 19.18 | — / 3.74 | 1.00 | — / 1.14 |
| 175 | family median | 3.38 | 8.91 | 15.08 | 14.34 | | | |
| 175 | ridge probe | 5.40 | 5.36 | 13.12 | 13.87 | | | |
| 175 | M1 | 3.02 | 3.09 | 5.82 | 6.90 | | | |
| 175 | M2 | 3.28 | 3.94 | 6.51 | 9.62 | 3.74 / 3.74 | 1.00 | 1.83 / 1.14 |
| 175 | M3 | 6.36 | 5.63 | 8.78 | 9.20 | 9.58 / 3.74 | 2.56 | 1.69 / 1.14 |
| 175 | M4 | 8.83 | 6.24 | 11.35 | 11.40 | 6.12 / 3.74 | 1.64 | 1.90 / 1.14 |

## Readings (pre-registered)

- M1 slopes of log RMS vs log n: diag CH-stretch -0.16, CH-oop -0.40, ring-ip -0.10, other -0.12
- M2 slopes of log RMS vs log n: diag CH-stretch -0.05, CH-oop -0.31, ring-ip -0.08, other -0.05; ring coupling ratio +0.00
- M3 slopes of log RMS vs log n: diag CH-stretch +0.18, CH-oop +0.07, ring-ip +0.02, other -0.08; ring coupling ratio -0.03
- M4 slopes of log RMS vs log n: diag CH-stretch -0.20, CH-oop -0.04, ring-ip -0.03, other -0.13; ring coupling ratio -0.04
- M2 crossings: ratio < 1.0 at n = None, < 0.7 at n = None, ring block beats the median rule at n = None
- M3 crossings: ratio < 1.0 at n = None, < 0.7 at n = None, ring block beats the median rule at n = None
- M4 crossings: ratio < 1.0 at n = None, < 0.7 at n = None, ring block beats the median rule at n = None
- M2 scaffold gap on the ring block, (b) − (a): n=45 -3.49, n=100 -3.86, n=175 -3.72
- M3 scaffold gap on the ring block, (b) − (a): n=45 -2.31, n=100 -2.27, n=175 -2.67
- M4 scaffold gap on the ring block, (b) − (a): n=45 -2.38, n=100 -3.43, n=175 -3.79

Total 4090 s. M1 = per-mode Transformer; M2 = ΔH block model; M3 = E5b-tok; M4 = E5b-atoms.
