# Design check — out/design_check_rungC_ck0927_2026-09-28 (2026-09-28 06:32)

body: checkpoint out/rungC_pretrained_2026-09-27.pt (sum aggregation); target: 534 molecules under `corpus/molecules`

| extreme | molecule | atoms | mean deg | max deg | max Z | feature scale | worst output |
|---|---|---|---|---|---|---|---|
| n_atoms_min | B_0112c00d02 | 8 | 6.8 | 7 | 17 | 2.3e+03 | 1.7e+16 |
| n_atoms_max | A2_02c8833bd5 | 30 | 16.5 | 25 | 6 | 0.0592 | 3.23 |
| mean_degree_min | B_0112c00d02 | 8 | 6.8 | 7 | 17 | 2.3e+03 | 1.7e+16 |
| mean_degree_max | A2_09d0b3be91 | 28 | 17.7 | 26 | 8 | 0.0599 | 3.3 |
| max_degree_max | A2_2b693cf6e7 | 29 | 17.2 | 27 | 6 | 0.0594 | 3.15 |
| max_Z_max | A2_066237c4f5 | 23 | 15.2 | 21 | 17 | 1.93 | 1.43e+06 |

verdict: **FAIL** — finite True, worst output 1.7e+16 (limit 1000), feature-scale ratio across the extremes 3.88e+04 (limit 3)

## Transfer table — source `C:\Users\thebr\Documents\CapstonePlan\plans\05_delta-probed-ir-pipeline\modules\05_support_predictor\data\hessian_qm9\hessian_qm9_DatasetDict\vacuum` (500 sampled) → target

| property | source | target | target inside source? |
|---|---|---|---|
| n_atoms | [9, 25] | [8, 30] | NO ← outside: name the test that covers it |
| mean_degree | [7.692307472229004, 21.5] | [6.75, 17.714284896850586] | NO ← outside: name the test that covers it |
| max_degree | [8, 24] | [7, 27] | NO ← outside: name the test that covers it |
| max_Z | [6, 9] | [6, 17] | NO ← outside: name the test that covers it |
| elements | [1, 6, 7, 8, 9] | [1, 6, 7, 8, 9, 16, 17] | NO ← outside: name the test that covers it |

1.4 s
