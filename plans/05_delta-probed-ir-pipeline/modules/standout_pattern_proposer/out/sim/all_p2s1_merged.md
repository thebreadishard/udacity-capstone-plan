# Pattern-proposer simulation — pool all, merged 5 shards

seeds [0, 1, 2], 60 checkpoints per curve, λ [1e-06, 1e-05], noise σ 0.0; 97 evaluation molecules; 61.7 CPU-hours.

## eval_parents (n 41; P0 reaches ρ_off ≤ 0.3 on 38)

| read-out | ordering | n | median ratio vs P0 | improved |
|---|---|---|---|---|
| K_off_0p3 | P3_oracle | 38 | 0.25 | 97 % |
| K_off_0p3 | P1_seed0 | 38 | 0.76 | 71 % |
| K_off_0p3 | P2_seed0 | 38 | 0.65 | 79 % |
| K_off_0p3 | P12_seed0 | 38 | 0.68 | 76 % |
| K_off_0p3 | P1_seed1 | 38 | 0.78 | 66 % |
| K_off_0p3 | P2_seed1 | 38 | 0.63 | 74 % |
| K_off_0p3 | P12_seed1 | 38 | 0.60 | 76 % |
| K_off_0p3 | P1_seed2 | 38 | 0.77 | 74 % |
| K_off_0p3 | P2_seed2 | 38 | 0.65 | 74 % |
| K_off_0p3 | P12_seed2 | 38 | 0.66 | 82 % |
| K_off_0p1 | P3_oracle | 25 | 0.46 | 88 % |
| K_off_0p1 | P1_seed0 | 25 | 0.90 | 76 % |
| K_off_0p1 | P2_seed0 | 25 | 0.72 | 80 % |
| K_off_0p1 | P12_seed0 | 25 | 0.72 | 84 % |
| K_off_0p1 | P1_seed1 | 25 | 0.86 | 80 % |
| K_off_0p1 | P2_seed1 | 25 | 0.81 | 80 % |
| K_off_0p1 | P12_seed1 | 25 | 0.76 | 80 % |
| K_off_0p1 | P1_seed2 | 25 | 0.84 | 68 % |
| K_off_0p1 | P2_seed2 | 25 | 0.78 | 88 % |
| K_off_0p1 | P12_seed2 | 25 | 0.80 | 80 % |
| n10_inband | P3_oracle | 35 | 0.80 | 63 % |
| n10_inband | P1_seed0 | 35 | 1.43 | 20 % |
| n10_inband | P2_seed0 | 35 | 1.38 | 23 % |
| n10_inband | P12_seed0 | 35 | 1.31 | 29 % |
| n10_inband | P1_seed1 | 35 | 1.52 | 17 % |
| n10_inband | P2_seed1 | 35 | 1.37 | 17 % |
| n10_inband | P12_seed1 | 35 | 1.32 | 23 % |
| n10_inband | P1_seed2 | 35 | 1.50 | 17 % |
| n10_inband | P2_seed2 | 35 | 1.40 | 23 % |
| n10_inband | P12_seed2 | 35 | 1.36 | 26 % |
| n10_all | P3_oracle | 36 | 0.43 | 97 % |
| n10_all | P1_seed0 | 36 | 0.81 | 81 % |
| n10_all | P2_seed0 | 36 | 0.71 | 89 % |
| n10_all | P12_seed0 | 36 | 0.72 | 89 % |
| n10_all | P1_seed1 | 36 | 0.82 | 78 % |
| n10_all | P2_seed1 | 36 | 0.77 | 89 % |
| n10_all | P12_seed1 | 36 | 0.73 | 86 % |
| n10_all | P1_seed2 | 36 | 0.84 | 81 % |
| n10_all | P2_seed2 | 36 | 0.78 | 94 % |
| n10_all | P12_seed2 | 36 | 0.76 | 89 % |

## eval (n 56; P0 reaches ρ_off ≤ 0.3 on 43)

| read-out | ordering | n | median ratio vs P0 | improved |
|---|---|---|---|---|
| K_off_0p3 | P3_oracle | 43 | 0.38 | 95 % |
| K_off_0p3 | P1_seed0 | 43 | 0.80 | 63 % |
| K_off_0p3 | P2_seed0 | 43 | 0.68 | 70 % |
| K_off_0p3 | P12_seed0 | 43 | 0.69 | 70 % |
| K_off_0p3 | P1_seed1 | 43 | 0.88 | 53 % |
| K_off_0p3 | P2_seed1 | 43 | 0.79 | 70 % |
| K_off_0p3 | P12_seed1 | 43 | 0.74 | 63 % |
| K_off_0p3 | P1_seed2 | 43 | 0.83 | 58 % |
| K_off_0p3 | P2_seed2 | 43 | 0.71 | 72 % |
| K_off_0p3 | P12_seed2 | 43 | 0.67 | 74 % |
| K_off_0p1 | P3_oracle | 18 | 0.52 | 100 % |
| K_off_0p1 | P1_seed0 | 18 | 0.93 | 72 % |
| K_off_0p1 | P2_seed0 | 18 | 0.87 | 89 % |
| K_off_0p1 | P12_seed0 | 18 | 0.82 | 83 % |
| K_off_0p1 | P1_seed1 | 18 | 0.90 | 61 % |
| K_off_0p1 | P2_seed1 | 18 | 0.85 | 78 % |
| K_off_0p1 | P12_seed1 | 18 | 0.84 | 78 % |
| K_off_0p1 | P1_seed2 | 18 | 0.94 | 72 % |
| K_off_0p1 | P2_seed2 | 18 | 0.88 | 83 % |
| K_off_0p1 | P12_seed2 | 18 | 0.84 | 83 % |
| n10_inband | P3_oracle | 35 | 1.08 | 40 % |
| n10_inband | P1_seed0 | 35 | 1.72 | 11 % |
| n10_inband | P2_seed0 | 35 | 1.43 | 11 % |
| n10_inband | P12_seed0 | 35 | 1.41 | 11 % |
| n10_inband | P1_seed1 | 35 | 1.69 | 9 % |
| n10_inband | P2_seed1 | 35 | 1.47 | 9 % |
| n10_inband | P12_seed1 | 35 | 1.45 | 9 % |
| n10_inband | P1_seed2 | 35 | 1.60 | 11 % |
| n10_inband | P2_seed2 | 35 | 1.43 | 9 % |
| n10_inband | P12_seed2 | 35 | 1.45 | 14 % |
| n10_all | P3_oracle | 32 | 0.57 | 100 % |
| n10_all | P1_seed0 | 32 | 0.94 | 72 % |
| n10_all | P2_seed0 | 32 | 0.88 | 88 % |
| n10_all | P12_seed0 | 32 | 0.86 | 88 % |
| n10_all | P1_seed1 | 32 | 0.94 | 75 % |
| n10_all | P2_seed1 | 32 | 0.87 | 88 % |
| n10_all | P12_seed1 | 32 | 0.85 | 91 % |
| n10_all | P1_seed2 | 32 | 0.92 | 69 % |
| n10_all | P2_seed2 | 32 | 0.88 | 94 % |
| n10_all | P12_seed2 | 32 | 0.86 | 94 % |
