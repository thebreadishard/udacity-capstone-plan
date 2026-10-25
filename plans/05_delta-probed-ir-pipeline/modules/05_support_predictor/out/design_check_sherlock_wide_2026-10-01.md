# Design check — out/design_check_sherlock_wide_2026-10-01 (2026-10-01 23:56)

body: fresh body, sum aggregation, 3 blocks × width 128, seed 0; target: 847 molecules under `corpus/molecules`

| extreme | molecule | atoms | mean deg | max deg | max Z | feature scale | worst output |
|---|---|---|---|---|---|---|---|
| n_atoms_min | B_0112c00d02 | 8 | 6.8 | 7 | 17 | 0.936 | 7.77 |
| n_atoms_max | A2_02c8833bd5 | 30 | 16.5 | 25 | 6 | 1.08 | 46.6 |
| mean_degree_min | B_0112c00d02 | 8 | 6.8 | 7 | 17 | 0.936 | 7.77 |
| mean_degree_max | A2_09d0b3be91 | 28 | 17.7 | 26 | 8 | 1.1 | 41.3 |
| max_degree_max | A2_2b693cf6e7 | 29 | 17.2 | 27 | 6 | 1.09 | 46.3 |
| max_Z_max | A2_066237c4f5 | 23 | 15.2 | 21 | 17 | 1.05 | 32 |

verdict: **PASS** — finite True, worst output 46.6 (limit 1000), feature-scale ratio across the extremes 1.17 (limit 3)

1.6 s
