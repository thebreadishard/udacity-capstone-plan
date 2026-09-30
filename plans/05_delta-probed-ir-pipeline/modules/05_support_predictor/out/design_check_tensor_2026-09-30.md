# Design check — out/design_check_tensor_2026-09-30 (2026-09-30 22:51)

body: fresh body, sum aggregation, rank-2 tensor input, seed 0; target: 847 molecules under `corpus/molecules`

| extreme | molecule | atoms | mean deg | max deg | max Z | feature scale | worst output |
|---|---|---|---|---|---|---|---|
| n_atoms_min | B_0112c00d02 | 8 | 6.8 | 7 | 17 | 0.928 | 2.18 |
| n_atoms_max | A2_02c8833bd5 | 30 | 16.5 | 25 | 6 | 1.08 | 4.2 |
| mean_degree_min | B_0112c00d02 | 8 | 6.8 | 7 | 17 | 0.928 | 2.18 |
| mean_degree_max | A2_09d0b3be91 | 28 | 17.7 | 26 | 8 | 1.09 | 5.56 |
| max_degree_max | A2_2b693cf6e7 | 29 | 17.2 | 27 | 6 | 1.08 | 4.36 |
| max_Z_max | A2_066237c4f5 | 23 | 15.2 | 21 | 17 | 1.04 | 3.85 |

verdict: **PASS** — finite True, worst output 5.56 (limit 1000), feature-scale ratio across the extremes 1.17 (limit 3)

1.2 s
