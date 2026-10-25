# Design check — out/design_check_night4_2026-10-01 (2026-10-01 00:48)

body: fresh body, sum aggregation, seed 0; target: 847 molecules under `corpus/molecules`

| extreme | molecule | atoms | mean deg | max deg | max Z | feature scale | worst output |
|---|---|---|---|---|---|---|---|
| n_atoms_min | B_0112c00d02 | 8 | 6.8 | 7 | 17 | 0.978 | 3.76 |
| n_atoms_max | A2_02c8833bd5 | 30 | 16.5 | 25 | 6 | 1.25 | 25.3 |
| mean_degree_min | B_0112c00d02 | 8 | 6.8 | 7 | 17 | 0.978 | 3.76 |
| mean_degree_max | A2_09d0b3be91 | 28 | 17.7 | 26 | 8 | 1.27 | 22.5 |
| max_degree_max | A2_2b693cf6e7 | 29 | 17.2 | 27 | 6 | 1.26 | 25.8 |
| max_Z_max | A2_066237c4f5 | 23 | 15.2 | 21 | 17 | 1.18 | 14.9 |

verdict: **PASS** — finite True, worst output 25.8 (limit 1000), feature-scale ratio across the extremes 1.3 (limit 3)

0.8 s
