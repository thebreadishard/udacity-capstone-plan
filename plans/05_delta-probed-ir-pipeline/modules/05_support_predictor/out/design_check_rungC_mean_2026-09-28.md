# Design check — out/design_check_rungC_mean_2026-09-28 (2026-09-28 07:37)

body: fresh body, mean aggregation, seed 0; target: 534 molecules under `corpus/molecules`

| extreme | molecule | atoms | mean deg | max deg | max Z | feature scale | worst output |
|---|---|---|---|---|---|---|---|
| n_atoms_min | B_0112c00d02 | 8 | 6.8 | 7 | 17 | 0.962 | 4.21 |
| n_atoms_max | A2_02c8833bd5 | 30 | 16.5 | 25 | 6 | 1.01 | 11.1 |
| mean_degree_min | B_0112c00d02 | 8 | 6.8 | 7 | 17 | 0.962 | 4.21 |
| mean_degree_max | A2_09d0b3be91 | 28 | 17.7 | 26 | 8 | 1.01 | 10.5 |
| max_degree_max | A2_2b693cf6e7 | 29 | 17.2 | 27 | 6 | 1.01 | 11.3 |
| max_Z_max | A2_066237c4f5 | 23 | 15.2 | 21 | 17 | 0.993 | 9.09 |

verdict: **PASS** — finite True, worst output 11.3 (limit 1000), feature-scale ratio across the extremes 1.05 (limit 3)

0.6 s
