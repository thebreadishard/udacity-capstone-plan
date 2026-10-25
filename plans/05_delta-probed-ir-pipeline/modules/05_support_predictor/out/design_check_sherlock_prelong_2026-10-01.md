# Design check — out/design_check_sherlock_prelong_2026-10-01 (2026-10-01 15:37)

body: checkpoint out/rungC_pretrained_mean_long_2026-10-01.pt (mean aggregation) as the fine-tune sees it: element rows reset [16, 17]; target: 847 molecules under `corpus/molecules`

| extreme | molecule | atoms | mean deg | max deg | max Z | feature scale | worst output |
|---|---|---|---|---|---|---|---|
| n_atoms_min | B_0112c00d02 | 8 | 6.8 | 7 | 17 | 0.134 | 3.62 |
| n_atoms_max | A2_02c8833bd5 | 30 | 16.5 | 25 | 6 | 0.112 | 4.36 |
| mean_degree_min | B_0112c00d02 | 8 | 6.8 | 7 | 17 | 0.134 | 3.62 |
| mean_degree_max | A2_09d0b3be91 | 28 | 17.7 | 26 | 8 | 0.113 | 4.13 |
| max_degree_max | A2_2b693cf6e7 | 29 | 17.2 | 27 | 6 | 0.111 | 4.02 |
| max_Z_max | A2_066237c4f5 | 23 | 15.2 | 21 | 17 | 0.11 | 3.68 |

verdict: **PASS** — finite True, worst output 4.36 (limit 1000), feature-scale ratio across the extremes 1.21 (limit 3)

2.7 s
