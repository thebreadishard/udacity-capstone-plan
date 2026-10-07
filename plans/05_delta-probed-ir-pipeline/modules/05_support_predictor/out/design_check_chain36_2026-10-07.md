# Design check — out/design_check_chain36_2026-10-07 (2026-10-07 07:23)

body: fresh body, sum aggregation, seed 0; target: 847 molecules under `corpus/molecules`

| extreme | molecule | atoms | mean deg | max deg | max Z | feature scale | worst output |
|---|---|---|---|---|---|---|---|
| n_atoms_min | B_0112c00d02 | 8 | 6.8 | 7 | 17 | 0.993 | 8.03 |
| n_atoms_max | A2_02c8833bd5 | 30 | 16.5 | 25 | 6 | 1.3 | 44.2 |
| mean_degree_min | B_0112c00d02 | 8 | 6.8 | 7 | 17 | 0.993 | 8.03 |
| mean_degree_max | A2_09d0b3be91 | 28 | 17.7 | 26 | 8 | 1.31 | 37.4 |
| max_degree_max | A2_2b693cf6e7 | 29 | 17.2 | 27 | 6 | 1.31 | 45.4 |
| max_Z_max | A2_066237c4f5 | 23 | 15.2 | 21 | 17 | 1.22 | 34 |

charge rows: 0 cation rows, 0 without a charge-state index, body charge input True → ok

verdict: **PASS** — finite True, worst output 45.4 (limit 1000), feature-scale ratio across the extremes 1.32 (limit 3)

2.0 s
