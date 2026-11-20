# The sample for the low-mode threshold measurement (TASKS 218)

Seed 218, 5 per band, at most 25 atoms; bands by the lowest b3lyp label mode.

| lowest b3lyp mode (cm⁻¹) | unrepaired molecules | with ≤ 25 atoms | eligible | drawn |
|---|---|---|---|---|
| 20–30 | 54 | 41 | 41 | 5 |
| 30–40 | 66 | 42 | 41 | 5 |
| 40–50 | 79 | 54 | 54 | 5 |
| 50–60 | 191 | 146 | 146 | 5 |

Eligible: no mode of either label below 20 cm⁻¹ (imaginary ones included).

| id | band | atoms | b3lyp modes below 100 | wb97x modes below 100 | noise per 1e-07 (cm⁻¹) | directions / gradients / min at --below 60 | directions / gradients / min at --below 100 |
|---|---|---|---|---|---|---|---|
| A2_3ac24b6972 | 20–30 | 23 | 20.2, 78.6 | 94.4 | 0.23 | 1 / 4 / 22 | 2 / 8 / 37 |
| B_0c6c144a7f | 20–30 | 19 | 23.7 | 67.1 | 1.09 | 1 / 4 / 12 | 1 / 4 / 12 |
| B_2326ac497c | 20–30 | 23 | 21.2, 77.2, 85.2 | 79.0, 94.0 | 0.24 | 1 / 4 / 22 | 3 / 12 / 53 |
| B_3dcbd985e3 | 20–30 | 25 | 23.7, 30.3, 86.7 | 63.4, 77.8, 89.2 | 0.24, 0.71 | 2 / 8 / 37 | 3 / 12 / 53 |
| B_55cca3aaf2 | 20–30 | 23 | 23.8, 90.6 | 54.4, 95.0 | 1.04 | 1 / 4 / 22 | 2 / 8 / 37 |
| B_15207e9ed5 | 30–40 | 18 | 35.2 | 78.8 | 0.14 | 1 / 4 / 12 | 1 / 4 / 12 |
| B_1726105aae | 30–40 | 15 | 34.3 |  | 0.14 | 1 / 4 / 9 | 1 / 4 / 9 |
| B_19c3319693 | 30–40 | 18 | 33.1, 99.7 | 80.3 | 0.15 | 1 / 4 / 12 | 2 / 8 / 21 |
| B_4f6ebdb30b | 30–40 | 25 | 31.0, 99.2 | 54.2 | 0.23 | 1 / 4 / 22 | 2 / 8 / 37 |
| B_4ff67f9ea2 | 30–40 | 23 | 33.0, 93.9 | 57.6, 98.4 | 0.73 | 1 / 4 / 22 | 2 / 8 / 37 |
| B_0af11315e3 | 40–50 | 16 | 45.7 | 84.6 | 0.11 | 1 / 4 / 9 | 1 / 4 / 9 |
| B_1139ae8d01 | 40–50 | 24 | 48.4, 63.1 | 82.1 | 0.12 | 1 / 4 / 22 | 2 / 8 / 37 |
| B_16769b963f | 40–50 | 16 | 48.1 | 71.4 | 0.07 | 1 / 4 / 9 | 1 / 4 / 9 |
| B_1b434d2cd0 | 40–50 | 16 | 48.1 | 71.3 | 0.07 | 1 / 4 / 9 | 1 / 4 / 9 |
| B_477b567fed | 40–50 | 24 | 40.7, 60.4, 83.3 | 70.7, 89.5 | 0.15 | 1 / 4 / 22 | 3 / 12 / 53 |
| A2_05e08111d2 | 50–60 | 24 | 55.5 | 72.0 | 0.09 | 1 / 4 / 22 | 1 / 4 / 22 |
| B_0d1c7f83df | 50–60 | 23 | 53.1, 85.2 | 82.1 | 0.21 | 1 / 4 / 22 | 2 / 8 / 37 |
| B_1428bc8164 | 50–60 | 17 | 50.5, 73.2, 83.1 | 95.3 | 0.07 | 1 / 4 / 12 | 3 / 12 / 30 |
| B_14cf57747b | 50–60 | 22 | 53.2, 88.3 | 77.1 | 0.06 | 1 / 4 / 22 | 2 / 8 / 37 |
| B_863cdaad7a | 50–60 | 24 | 53.8 | 77.5 | 0.28 | 1 / 4 / 22 | 1 / 4 / 22 |

Noise: the frequency noise the patch makes of 1e-07 hartree/bohr of gradient noise on each registered point (a b3lyp mode in 20–60 cm⁻¹), in the order of the modes; `low_mode_threshold_read.noise_sensitivity_cm`.

The sample at `--below 60`: 21 directions, 84 gradients and 40 reference SCFs; 6.0 h at the timings' 8 threads, so 6.0–12.0 h at 4 threads (factor 1–2, assumed, not measured; no other job beside it).
The sample at `--below 100`: 36 directions, 144 gradients and 40 reference SCFs; 9.6 h at the timings' 8 threads, so 9.6–19.1 h at 4 threads (factor 1–2, assumed, not measured; no other job beside it).
The step check at `--below 60`: 8 directions, 32 gradients and 14 reference SCFs; 2.0 h at the timings' 8 threads, so 2.0–4.1 h at 4 threads (factor 1–2, assumed, not measured; no other job beside it).
The step check at `--below 100`: 13 directions, 52 gradients and 14 reference SCFs; 3.1 h at the timings' 8 threads, so 3.1–6.2 h at 4 threads (factor 1–2, assumed, not measured; no other job beside it).

Seconds per gradient (median, 8 threads) from the timing folders, by atom count: ≤ 12 atoms b3lyp 33 s (2 points); ≤ 12 atoms wb97x 44 s (2 points); ≤ 16 atoms b3lyp 72 s (14 points); ≤ 16 atoms wb97x 112 s (14 points); ≤ 20 atoms b3lyp 115 s (24 points); ≤ 20 atoms wb97x 150 s (24 points); ≤ 25 atoms b3lyp 202 s (64 points); ≤ 25 atoms wb97x 264 s (64 points).
A molecule costs (directions + 0.4) × 2 × (the two functionals' seconds); the 0.4 is the reference SCFs and start-up measured on B_0f06474656.

Step check (the smallest molecule of each band, and every molecule with a registered point above 0.5 cm⁻¹ per 1e-07): B_0c6c144a7f (smallest of its band and a registered point above the noise line); B_3dcbd985e3 (a registered point above the noise line); B_55cca3aaf2 (a registered point above the noise line); B_1726105aae (smallest of its band); B_4ff67f9ea2 (a registered point above the noise line); B_0af11315e3 (smallest of its band); B_1428bc8164 (smallest of its band).
