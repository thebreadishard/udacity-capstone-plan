# Design check — out/design_check_rungC_ck0927_asfinetune_2026-09-28 (2026-09-28 06:37)

body: checkpoint out/rungC_pretrained_2026-09-27.pt (sum aggregation) as the fine-tune sees it: element rows reset [16, 17]; target: 534 molecules under `corpus/molecules`

| extreme | molecule | atoms | mean deg | max deg | max Z | feature scale | worst output |
|---|---|---|---|---|---|---|---|
| n_atoms_min | B_0112c00d02 | 8 | 6.8 | 7 | 17 | 0.0645 | 3.36 |
| n_atoms_max | A2_02c8833bd5 | 30 | 16.5 | 25 | 6 | 0.0592 | 3.23 |
| mean_degree_min | B_0112c00d02 | 8 | 6.8 | 7 | 17 | 0.0645 | 3.36 |
| mean_degree_max | A2_09d0b3be91 | 28 | 17.7 | 26 | 8 | 0.0599 | 3.3 |
| max_degree_max | A2_2b693cf6e7 | 29 | 17.2 | 27 | 6 | 0.0594 | 3.15 |
| max_Z_max | A2_066237c4f5 | 23 | 15.2 | 21 | 17 | 0.0586 | 2.99 |

verdict: **PASS** — finite True, worst output 3.36 (limit 1000), feature-scale ratio across the extremes 1.1 (limit 3)

0.6 s
