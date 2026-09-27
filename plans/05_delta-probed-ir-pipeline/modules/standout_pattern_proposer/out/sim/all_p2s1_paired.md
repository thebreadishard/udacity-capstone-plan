# Paired read-outs — all_p2s1 (wide pool, stage-1 recipe), 2026-09-27; `paired_readout.py`

## S2: P2 (stage 1) against P1, same run
| readout | split | seed | A | B | n paired | median A/B | A better | equal |
|---|---|---|---|---|---|---|---|---|
| K_off_0p3 | eval | 0 | P2_seed0 | P1_seed0 | 43 | 0.94 | 63 % | 7 % |
| K_off_0p3 | eval_parents | 0 | P2_seed0 | P1_seed0 | 38 | 0.89 | 66 % | 5 % |
| K_off_0p3 | eval | 1 | P2_seed1 | P1_seed1 | 43 | 0.91 | 65 % | 12 % |
| K_off_0p3 | eval_parents | 1 | P2_seed1 | P1_seed1 | 38 | 0.86 | 61 % | 8 % |
| K_off_0p3 | eval | 2 | P2_seed2 | P1_seed2 | 43 | 0.95 | 56 % | 5 % |
| K_off_0p3 | eval_parents | 2 | P2_seed2 | P1_seed2 | 38 | 0.86 | 68 % | 5 % |
| K_off_0p1 | eval | 0 | P2_seed0 | P1_seed0 | 18 | 0.96 | 67 % | 22 % |
| K_off_0p1 | eval_parents | 0 | P2_seed0 | P1_seed0 | 25 | 0.92 | 80 % | 12 % |
| K_off_0p1 | eval | 1 | P2_seed1 | P1_seed1 | 18 | 0.95 | 67 % | 17 % |
| K_off_0p1 | eval_parents | 1 | P2_seed1 | P1_seed1 | 25 | 0.97 | 64 % | 4 % |
| K_off_0p1 | eval | 2 | P2_seed2 | P1_seed2 | 18 | 0.97 | 61 % | 17 % |
| K_off_0p1 | eval_parents | 2 | P2_seed2 | P1_seed2 | 25 | 0.91 | 64 % | 12 % |

## P12 against P1, same run
| readout | split | seed | A | B | n paired | median A/B | A better | equal |
|---|---|---|---|---|---|---|---|---|
| K_off_0p3 | eval | 0 | P12_seed0 | P1_seed0 | 43 | 0.92 | 67 % | 16 % |
| K_off_0p3 | eval_parents | 0 | P12_seed0 | P1_seed0 | 38 | 0.94 | 58 % | 18 % |
| K_off_0p3 | eval | 1 | P12_seed1 | P1_seed1 | 43 | 0.89 | 72 % | 14 % |
| K_off_0p3 | eval_parents | 1 | P12_seed1 | P1_seed1 | 38 | 0.86 | 79 % | 5 % |
| K_off_0p3 | eval | 2 | P12_seed2 | P1_seed2 | 43 | 0.90 | 74 % | 5 % |
| K_off_0p3 | eval_parents | 2 | P12_seed2 | P1_seed2 | 38 | 0.94 | 66 % | 11 % |

## Stage 1 against stage 0 (all_p2s1 vs all_p2, same molecules and seeds); control P1 vs P1
| readout | split | seed | A | B | n paired | median A/B | A better | equal |
|---|---|---|---|---|---|---|---|---|
| K_off_0p3 | eval | 0 | P2_seed0 | P2_seed0 | 43 | 0.89 | 65 % | 12 % |
| K_off_0p3 | eval_parents | 0 | P2_seed0 | P2_seed0 | 38 | 0.94 | 63 % | 8 % |
| K_off_0p3 | eval | 1 | P2_seed1 | P2_seed1 | 43 | 0.94 | 63 % | 0 % |
| K_off_0p3 | eval_parents | 1 | P2_seed1 | P2_seed1 | 38 | 0.88 | 74 % | 3 % |
| K_off_0p3 | eval | 2 | P2_seed2 | P2_seed2 | 43 | 1.00 | 47 % | 7 % |
| K_off_0p3 | eval_parents | 2 | P2_seed2 | P2_seed2 | 38 | 0.98 | 50 % | 8 % |
| K_off_0p3 | eval | 0 | P1_seed0 | P1_seed0 | 43 | 1.00 | 0 % | 100 % |
| K_off_0p3 | eval_parents | 0 | P1_seed0 | P1_seed0 | 38 | 1.00 | 0 % | 100 % |
| K_off_0p3 | eval | 1 | P1_seed1 | P1_seed1 | 43 | 1.00 | 0 % | 100 % |
| K_off_0p3 | eval_parents | 1 | P1_seed1 | P1_seed1 | 38 | 1.00 | 0 % | 100 % |
| K_off_0p3 | eval | 2 | P1_seed2 | P1_seed2 | 43 | 1.00 | 0 % | 100 % |
| K_off_0p3 | eval_parents | 2 | P1_seed2 | P1_seed2 | 38 | 1.00 | 0 % | 100 % |
