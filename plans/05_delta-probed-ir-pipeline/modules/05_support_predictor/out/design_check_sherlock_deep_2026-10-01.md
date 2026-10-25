# Design check — out/design_check_sherlock_deep_2026-10-01 (2026-10-01 22:56)

body: fresh body, sum aggregation, 5 blocks × width 64, seed 0; target: 847 molecules under `corpus/molecules`

| extreme | molecule | atoms | mean deg | max deg | max Z | feature scale | worst output |
|---|---|---|---|---|---|---|---|
| n_atoms_min | B_0112c00d02 | 8 | 6.8 | 7 | 17 | 1.02 | 2.06 |
| n_atoms_max | A2_02c8833bd5 | 30 | 16.5 | 25 | 6 | 1.42 | 23.4 |
| mean_degree_min | B_0112c00d02 | 8 | 6.8 | 7 | 17 | 1.02 | 2.06 |
| mean_degree_max | A2_09d0b3be91 | 28 | 17.7 | 26 | 8 | 1.45 | 30.1 |
| max_degree_max | A2_2b693cf6e7 | 29 | 17.2 | 27 | 6 | 1.44 | 26.9 |
| max_Z_max | A2_066237c4f5 | 23 | 15.2 | 21 | 17 | 1.31 | 12.1 |

verdict: **PASS** — finite True, worst output 30.1 (limit 1000), feature-scale ratio across the extremes 1.43 (limit 3)

1.5 s
